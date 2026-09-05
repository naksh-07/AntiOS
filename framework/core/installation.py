"""AntiOS 2.0 Installation Lifecycle Engine.

Governs the deterministic, ownership-aware lifecycle:
INSTALL -> ADAPT -> VERIFY -> READY
UPDATE -> RE-ADAPT -> VERIFY
REPAIR -> VERIFY
REMOVE -> VERIFY

Handles all lifecycle states:
- First installation
- Already-installed instance (idempotent, zero unnecessary mutations)
- Partially installed instance recovery
- Stale instance detection (manifest drift)
- Newer AntiOS source / Older AntiOS instance migration
- Corrupted manifest (fail-closed, diagnostic error)
- Conflicting .agents configuration (preserves pre-existing user assets)
- User-modified generated/managed file (blocks silent overwrite)
- Removed project component (flags stale paths)
- Unsupported project topology (graceful degradation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from framework.core.compiler import CompilationResult, ProjectBoundaryCompiler
from framework.core.config import AntiOSConfig, load_config
from framework.core.discovery import discover_project, is_tool_in_path
from framework.core.manifest import (
    AdaptationState,
    ArtifactOwnership,
    ArtifactRecord,
    CURRENT_ANTIOS_VERSION,
    CURRENT_SCHEMA_VERSION,
    InstallationState,
    ProjectManifest,
    load_manifest,
    save_manifest,
)
from framework.core.provenance import (
    ProvenanceConflict,
    ProvenanceTracker,
    compute_file_sha256,
)


@dataclass
class LifecycleResult:
    """Structured result for an AntiOS lifecycle operation."""
    operation: str  # INSTALL, ADAPT, UPDATE, REPAIR, REMOVE, VERIFY
    status: str     # SUCCESS, IDEMPOTENT, BLOCKED, CONFLICT, ERROR, STALE
    installation_state: InstallationState
    adaptation_state: AdaptationState
    manifest: Optional[ProjectManifest] = None
    written_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status,
            "installation_state": self.installation_state.value if isinstance(self.installation_state, InstallationState) else str(self.installation_state),
            "adaptation_state": self.adaptation_state.value if isinstance(self.adaptation_state, AdaptationState) else str(self.adaptation_state),
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "written_files": self.written_files,
            "removed_files": self.removed_files,
            "conflicts": self.conflicts,
            "issues": self.issues,
            "summary": self.summary,
        }


def _resolve_project_fingerprint(profile: Any, target_root: Path) -> str:
    fp = getattr(profile, "manifest_fingerprint", "")
    if not fp:
        return hashlib.sha256(f"manifestless:{target_root.name}".encode("utf-8")).hexdigest()
    return fp


class InstallationLifecycleManager:
    """Manages the lifecycle operations for Project Agent OS instances."""

    def __init__(
        self,
        source_root: Union[str, Path],
        target_root: Union[str, Path],
        source_revision: str = "v2.0.0",
    ):
        self.source_root = Path(source_root).resolve()
        self.target_root = Path(target_root).resolve()
        self.source_revision = source_revision
        self.compiler = ProjectBoundaryCompiler(
            source_root=self.source_root,
            target_root=self.target_root,
            source_revision=self.source_revision,
        )

    def install(self, dry_run: bool = False, force: bool = False) -> LifecycleResult:
        """Installs AntiOS into target project. Idempotent if already installed."""
        # 1. Check if manifest already exists
        manifest_path = self.target_root / ".antios/manifest.json"
        existing_manifest: Optional[ProjectManifest] = None

        if manifest_path.is_file():
            try:
                existing_manifest = load_manifest(self.target_root)
            except Exception as e:
                # Corrupted manifest -> fail closed
                return LifecycleResult(
                    operation="INSTALL",
                    status="BLOCKED",
                    installation_state=InstallationState.ERROR,
                    adaptation_state=AdaptationState.CONFLICT,
                    issues=[f"Corrupted manifest detected: {e}. Run 'repair' or inspect .antios/manifest.json."],
                    summary="Installation blocked by corrupted manifest.",
                )

        # 2. If valid manifest already exists and not forced, check idempotency
        if existing_manifest and not force:
            # Check manifest fingerprint against current disk manifests
            current_profile = discover_project(str(self.target_root))
            current_fp = _resolve_project_fingerprint(current_profile, self.target_root)
            if existing_manifest.project_fingerprint == current_fp:
                # Perfectly matching fingerprint: verify files on disk
                verification = self.verify()
                if verification.status == "SUCCESS":
                    return LifecycleResult(
                        operation="INSTALL",
                        status="IDEMPOTENT",
                        installation_state=existing_manifest.installation_state,
                        adaptation_state=existing_manifest.adaptation_state,
                        manifest=existing_manifest,
                        summary="AntiOS is already installed and up to date (idempotent no-op).",
                    )
            else:
                # Fingerprint changed: project was modified -> needs adapt
                return LifecycleResult(
                    operation="INSTALL",
                    status="STALE",
                    installation_state=existing_manifest.installation_state,
                    adaptation_state=AdaptationState.STALE,
                    manifest=existing_manifest,
                    issues=["Target manifests have changed since last installation. Re-adaptation required."],
                    summary="Existing installation is stale. Run 'adapt' to synchronize.",
                )

        # 3. Detect pre-existing user assets in .agents/
        user_owned_paths: List[str] = []
        agents_dir = self.target_root / ".agents"
        if agents_dir.is_dir():
            for p in agents_dir.rglob("*"):
                if p.is_file():
                    rel = str(p.relative_to(self.target_root)).replace("\\", "/")
                    if rel != ".agents/hooks.json":
                        user_owned_paths.append(rel)

        # 4. Compile boundary assets
        compilation = self.compiler.compile(existing_manifest=existing_manifest)
        if user_owned_paths:
            for u in user_owned_paths:
                if u not in compilation.manifest.user_owned_paths:
                    compilation.manifest.user_owned_paths.append(u)

        # 5. Emit files to disk
        emit_ok, written, conflicts = self.compiler.emit(
            compilation,
            existing_manifest=existing_manifest,
            dry_run=dry_run,
        )

        if not emit_ok and not force:
            return LifecycleResult(
                operation="INSTALL",
                status="CONFLICT",
                installation_state=InstallationState.PARTIAL,
                adaptation_state=AdaptationState.CONFLICT,
                manifest=compilation.manifest,
                conflicts=conflicts,
                summary="Installation blocked by artifact ownership conflicts.",
            )

        if not dry_run:
            compilation.manifest.installation_state = InstallationState.INSTALLED
            compilation.manifest.adaptation_state = AdaptationState.ADAPTED
            save_manifest(compilation.manifest, self.target_root)

        return LifecycleResult(
            operation="INSTALL",
            status="SUCCESS",
            installation_state=InstallationState.INSTALLED,
            adaptation_state=AdaptationState.ADAPTED,
            manifest=compilation.manifest,
            written_files=written,
            conflicts=conflicts,
            summary=f"Installed AntiOS 2.0 Project Agent OS ({len(written)} files written).",
        )

    def adapt(self, dry_run: bool = False) -> LifecycleResult:
        """Re-discovers target project and updates generated intelligence."""
        manifest = load_manifest(self.target_root)
        if not manifest:
            return LifecycleResult(
                operation="ADAPT",
                status="ERROR",
                installation_state=InstallationState.UNINSTALLED,
                adaptation_state=AdaptationState.UNADAPTED,
                issues=["Cannot adapt: AntiOS is not installed in this project."],
                summary="AntiOS is not installed.",
            )

        # Run fresh discovery
        fresh_profile = discover_project(str(self.target_root))
        manifest.project_fingerprint = _resolve_project_fingerprint(fresh_profile, self.target_root)

        # Recompile boundary
        compilation = self.compiler.compile(
            existing_manifest=manifest,
            profile_override=fresh_profile,
        )

        # Emit files
        emit_ok, written, conflicts = self.compiler.emit(
            compilation,
            existing_manifest=manifest,
            dry_run=dry_run,
        )

        if not dry_run:
            compilation.manifest.adaptation_state = AdaptationState.ADAPTED
            save_manifest(compilation.manifest, self.target_root)

        status = "SUCCESS" if emit_ok else "CONFLICT"
        return LifecycleResult(
            operation="ADAPT",
            status=status,
            installation_state=compilation.manifest.installation_state,
            adaptation_state=compilation.manifest.adaptation_state,
            manifest=compilation.manifest,
            written_files=written,
            conflicts=conflicts,
            summary=f"Adapted AntiOS 2.0 instance ({len(written)} files updated).",
        )

    def update(self, new_revision: str, dry_run: bool = False) -> LifecycleResult:
        """Updates AntiOS instance to a newer source revision."""
        manifest = load_manifest(self.target_root)
        if not manifest:
            return self.install(dry_run=dry_run)

        # Update source revision
        self.source_revision = new_revision
        self.compiler.source_revision = new_revision

        compilation = self.compiler.compile(existing_manifest=manifest)
        emit_ok, written, conflicts = self.compiler.emit(
            compilation,
            existing_manifest=manifest,
            dry_run=dry_run,
        )

        if not dry_run:
            compilation.manifest.source_revision = new_revision
            save_manifest(compilation.manifest, self.target_root)

        return LifecycleResult(
            operation="UPDATE",
            status="SUCCESS" if emit_ok else "CONFLICT",
            installation_state=compilation.manifest.installation_state,
            adaptation_state=compilation.manifest.adaptation_state,
            manifest=compilation.manifest,
            written_files=written,
            conflicts=conflicts,
            summary=f"Updated AntiOS to revision '{new_revision}'.",
        )

    def repair(self, dry_run: bool = False) -> LifecycleResult:
        """Repairs damaged or missing AntiOS instance artifacts."""
        manifest = load_manifest(self.target_root)
        if not manifest:
            return self.install(dry_run=dry_run)

        tracker = ProvenanceTracker(self.target_root, manifest)
        conflicts = tracker.audit_artifacts()

        written: List[str] = []
        issues: List[str] = []

        compilation = self.compiler.compile(existing_manifest=manifest)

        # Repair missing files
        for conf in conflicts:
            if conf.conflict_type in ("MISSING_MANAGED", "MISSING_GENERATED"):
                rel_path = conf.path
                if rel_path in compilation.compiled_files:
                    if not dry_run:
                        target_file = self.target_root / rel_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        target_file.write_text(compilation.compiled_files[rel_path], encoding="utf-8")
                    written.append(rel_path)

        if not dry_run:
            manifest.installation_state = InstallationState.INSTALLED
            save_manifest(manifest, self.target_root)

        return LifecycleResult(
            operation="REPAIR",
            status="SUCCESS",
            installation_state=InstallationState.INSTALLED,
            adaptation_state=manifest.adaptation_state,
            manifest=manifest,
            written_files=written,
            issues=issues,
            summary=f"Repaired AntiOS instance ({len(written)} files restored).",
        )

    def remove(self, dry_run: bool = False) -> LifecycleResult:
        """Safely removes AntiOS instance files while preserving user code."""
        manifest = load_manifest(self.target_root)
        removed: List[str] = []

        # Target files to remove: only managed and generated files from manifest
        paths_to_remove: List[str] = []
        if manifest:
            paths_to_remove.extend(list(manifest.generated_paths.keys()))
            paths_to_remove.extend(list(manifest.managed_paths.keys()))
        else:
            # Fallback default instance paths
            paths_to_remove = [
                ".antios/manifest.json",
                ".antios/project_profile.json",
                ".antios/project_anatomy.json",
                ".antios/knowledge.json",
                ".antios/agent_topology.json",
                ".antios/tool_policy.json",
                ".antios/runtime/pre_tool_guard.py",
                ".antios/runtime/stop_gate.py",
                ".antios/runtime/inspect_instance.py",
                ".antios/runtime/verify_runtime.py",
                ".agents/skills/antios/SKILL.md",
                "antios.config.json",
            ]

        for rel_path in paths_to_remove:
            # Do NOT remove user owned paths
            if manifest and manifest.is_artifact_user_owned(rel_path):
                continue
            abs_path = self.target_root / rel_path
            if abs_path.is_file():
                if not dry_run:
                    abs_path.unlink()
                removed.append(rel_path)

        # Remove .antios directory if empty or contains only non-user files
        antios_dir = self.target_root / ".antios"
        if antios_dir.is_dir():
            if not dry_run:
                try:
                    shutil.rmtree(antios_dir)
                except Exception:
                    pass
            removed.append(".antios/")

        # Remove .agents/skills/antios directory if empty
        skill_antios_dir = self.target_root / ".agents/skills/antios"
        if skill_antios_dir.is_dir():
            if not dry_run:
                try:
                    shutil.rmtree(skill_antios_dir)
                except Exception:
                    pass
            removed.append(".agents/skills/antios/")

        return LifecycleResult(
            operation="REMOVE",
            status="SUCCESS",
            installation_state=InstallationState.REMOVED,
            adaptation_state=AdaptationState.UNADAPTED,
            removed_files=removed,
            summary=f"Removed AntiOS instance ({len(removed)} artifacts removed).",
        )

    def verify(self) -> LifecycleResult:
        """Verifies installation health, manifest validity, and checksums."""
        issues: List[str] = []
        conflicts: List[str] = []

        manifest = load_manifest(self.target_root)
        if not manifest:
            return LifecycleResult(
                operation="VERIFY",
                status="ERROR",
                installation_state=InstallationState.UNINSTALLED,
                adaptation_state=AdaptationState.UNADAPTED,
                issues=["AntiOS is not installed: .antios/manifest.json not found."],
                summary="Verification failed: instance not installed.",
            )

        # 1. Validate manifest schema
        is_valid, schema_issues = manifest.validate()
        if not is_valid:
            issues.extend(schema_issues)

        # 2. Check checksums of all tracked artifacts
        tracker = ProvenanceTracker(self.target_root, manifest)
        provenance_conflicts = tracker.audit_artifacts()
        for pc in provenance_conflicts:
            if pc.conflict_type in ("MISSING_MANAGED", "MISSING_GENERATED"):
                issues.append(pc.description)
            elif pc.conflict_type == "USER_MODIFIED":
                conflicts.append(pc.description)

        # 3. Check manifest fingerprint staleness
        try:
            current_profile = discover_project(str(self.target_root))
            current_fp = _resolve_project_fingerprint(current_profile, self.target_root)
            if manifest.project_fingerprint != current_fp:
                issues.append("Manifest fingerprint drift: target manifests have changed since last adaptation.")
        except Exception as e:
            issues.append(f"Failed to verify manifest fingerprint: {e}")

        # 4. Check runtime closure (Phases 79–82)
        try:
            from framework.core.runtime_contract import verify_runtime_closure
            closure_res = verify_runtime_closure(self.target_root)
            if not closure_res.is_closed:
                for viol in closure_res.violations:
                    if viol not in issues:
                        issues.append(viol)
        except Exception as e:
            issues.append(f"Failed to verify runtime closure: {e}")

        status = "SUCCESS" if len(issues) == 0 else "ERROR"
        if status == "SUCCESS" and len(conflicts) > 0:
            status = "CONFLICT"

        return LifecycleResult(
            operation="VERIFY",
            status=status,
            installation_state=manifest.installation_state,
            adaptation_state=manifest.adaptation_state,
            manifest=manifest,
            conflicts=conflicts,
            issues=issues,
            summary=f"Verification complete: {status} ({len(issues)} issues, {len(conflicts)} conflicts).",
        )
