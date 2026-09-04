"""AntiOS 2.0 Project Boundary Compiler.

Compiles AntiOS Source into a target Project Agent OS Instance (.antios/).
Does NOT blindly copy the AntiOS repository into the target project.
Distinguishes:
- UNIVERSAL CORE: Reference policies and immutable governance contracts
- PROJECT ADAPTER: antios.config.json
- GENERATED PROJECT INTELLIGENCE: .antios/ (profile, knowledge, topology, tool policy)
- ANTIGRAVITY-FACING ASSETS: .agents/skills/antios/SKILL.md, .agents/hooks.json
- HISTORICAL / DEVELOPMENT MATERIAL: Strictly excluded from installation

Preserves the universal-core boundary; target instance never becomes a
forked copy of AntiOS internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from framework.core.adapter import generate_adapter_config
from framework.core.config import AntiOSConfig, load_config
from framework.core.discovery import discover_project
from framework.core.manifest import (
    AdaptationState,
    ArtifactOwnership,
    ArtifactRecord,
    CURRENT_ANTIOS_VERSION,
    CURRENT_SCHEMA_VERSION,
    InstallationState,
    ProjectManifest,
)
from framework.core.profile import ProjectProfile
from framework.core.provenance import can_safely_overwrite, compute_file_sha256


@dataclass
class CompilationResult:
    """Outcome of the Project Boundary Compilation."""
    manifest: ProjectManifest
    compiled_files: Dict[str, str] = field(default_factory=dict)  # rel_path -> file content
    skipped_files: Dict[str, str] = field(default_factory=dict)   # rel_path -> reason
    conflicts: List[str] = field(default_factory=list)
    success: bool = True
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "summary": self.summary,
            "manifest": self.manifest.to_dict(),
            "compiled_files": list(self.compiled_files.keys()),
            "skipped_files": self.skipped_files,
            "conflicts": self.conflicts,
        }


class ProjectBoundaryCompiler:
    """Compiles AntiOS Source intelligence into a target Project Agent OS Instance."""

    def __init__(
        self,
        source_root: Union[str, Path],
        target_root: Union[str, Path],
        source_revision: str = "v2.0.0",
    ):
        self.source_root = Path(source_root).resolve()
        self.target_root = Path(target_root).resolve()
        self.source_revision = source_revision

    def compile(
        self,
        existing_manifest: Optional[ProjectManifest] = None,
        profile_override: Optional[ProjectProfile] = None,
        config_override: Optional[AntiOSConfig] = None,
    ) -> CompilationResult:
        """Executes boundary compilation, generating files and manifest in memory."""
        conflicts: List[str] = []
        skipped_files: Dict[str, str] = {}
        compiled_files: Dict[str, str] = {}

        # 1. Discover target project traits
        profile = profile_override or discover_project(str(self.target_root))
        project_fingerprint = profile.manifest_fingerprint
        if not project_fingerprint:
            # Deterministic fallback for repos with no package manifests
            project_fingerprint = hashlib.sha256(f"manifestless:{self.target_root.name}".encode("utf-8")).hexdigest()

        # 2. Derive adapter configuration
        config_path = self.target_root / "antios.config.json"
        if config_override:
            adapter_config = config_override
        elif config_path.is_file():
            adapter_config = load_config(str(self.target_root))
        else:
            from framework.core.adapter import analyze_adaptation, generate_adapter_config
            proposal = analyze_adaptation(profile)
            adapter_config = generate_adapter_config(profile, proposal)

        # Ensure core protected zones exist in config
        for zone in [".agents", "framework"]:
            if zone not in adapter_config.protected_zones:
                adapter_config.protected_zones.append(zone)

        # 3. Compile Project Profile (.antios/project_profile.json)
        profile_content = json.dumps(profile.to_dict(), indent=2)
        compiled_files[".antios/project_profile.json"] = profile_content

        # 4. Compile Knowledge Graph (.antios/knowledge.json)
        top = getattr(profile, "topology", None) or getattr(profile, "workspace_topology", None)
        top_str = top.value if hasattr(top, "value") else (str(top) if top else "STANDALONE")
        knowledge_data = {
            "project_identity": profile.identity.to_dict(),
            "workspace_topology": top_str,
            "subsystems": [s.to_dict() if hasattr(s, "to_dict") else s for s in profile.subsystems],
            "workspace_members": [m.to_dict() if hasattr(m, "to_dict") else m for m in profile.workspace_members],
            "risk_zones": list(profile.risk_zones),
            "protected_paths": list(profile.protected_paths),
            "protected_domain_paths": list(adapter_config.protected_domain_paths),
            "manifest_fingerprint": project_fingerprint,
        }
        compiled_files[".antios/knowledge.json"] = json.dumps(knowledge_data, indent=2)

        # 5. Compile Agent Topology (.antios/agent_topology.json)
        topology_data = {
            "project_name": profile.identity.name or "Target-Project",
            "primary_role": "role:primary-engineer",
            "allow_delegation": True,
            "max_depth": 2,
            "canonical_roles": [
                "role:primary-engineer",
                "role:root-cause-debugger",
                "role:independent-verifier",
                "role:investigation-specialist",
                "role:security-reviewer",
            ],
            "subsystem_specialists": [
                {
                    "subsystem": s.name if hasattr(s, "name") else s.get("name", "unknown"),
                    "owner": s.owner if hasattr(s, "owner") else s.get("owner", "unassigned"),
                }
                for s in profile.subsystems
            ],
        }
        compiled_files[".antios/agent_topology.json"] = json.dumps(topology_data, indent=2)

        # 6. Compile Tool Policy (.antios/tool_policy.json)
        from dataclasses import asdict
        runners_list = []
        for r in adapter_config.test_runners:
            if hasattr(r, "to_dict"):
                runners_list.append(r.to_dict())
            elif hasattr(r, "__dataclass_fields__"):
                runners_list.append(asdict(r))
            else:
                runners_list.append(r)

        tool_data = {
            "tier_preference": ["NATIVE", "SCRIPT", "PROJECT", "EXTERNAL", "SERVICE", "MCP"],
            "configured_runners": runners_list,
            "linters": getattr(adapter_config, "linters", []),
            "policies": asdict(adapter_config.policies) if hasattr(adapter_config.policies, "__dataclass_fields__") else {},
        }
        compiled_files[".antios/tool_policy.json"] = json.dumps(tool_data, indent=2)

        # 7. Compile antios.config.json
        config_dict = asdict(adapter_config) if hasattr(adapter_config, "__dataclass_fields__") else adapter_config.to_dict()
        config_content = json.dumps(config_dict, indent=2)
        compiled_files["antios.config.json"] = config_content

        # 8. Compile .agents/skills/antios/SKILL.md from template
        template_skill_path = self.source_root / "framework/templates/skills/antios/SKILL.md"
        if template_skill_path.is_file():
            skill_content = template_skill_path.read_text(encoding="utf-8")
        else:
            # Fallback embedded skill content
            skill_content = (
                "---\nname: antios\ndescription: Universal project operating interface under AntiOS 2.0 governance.\n---\n"
                "# AntiOS Project Operating Interface\n\nGoverns repository workflow under AntiOS 2.0.\n"
            )
        compiled_files[".agents/skills/antios/SKILL.md"] = skill_content

        # 9. Compile .agents/hooks.json
        hooks_data = {
            "antios-guard": {
                "PreToolUse": [
                    {
                        "matcher": "write_to_file|replace_file_content",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python framework/scripts/hooks/pre_tool_guard.py"
                            }
                        ]
                    }
                ],
                "Stop": [
                    {
                        "type": "command",
                        "command": "python framework/scripts/hooks/stop_gate.py"
                    }
                ]
            }
        }
        compiled_files[".agents/hooks.json"] = json.dumps(hooks_data, indent=2)

        # 10. Build Artifact Records & Project Manifest
        now_ts = datetime.now(timezone.utc).isoformat()
        managed_paths: Dict[str, ArtifactRecord] = {}
        generated_paths: Dict[str, ArtifactRecord] = {}

        # Managed paths (adapter configuration & hooks)
        managed_keys = {"antios.config.json", ".agents/hooks.json"}
        for k in managed_keys:
            if k in compiled_files:
                content = compiled_files[k]
                sha = hashlib.sha256(content.replace("\r\n", "\n").encode("utf-8")).hexdigest()
                managed_paths[k] = ArtifactRecord(
                    path=k,
                    ownership=ArtifactOwnership.MANAGED,
                    sha256=sha,
                    source_revision=self.source_revision,
                    generated_at=now_ts,
                    source_template=k,
                )

        # Generated paths (intelligence & operating skill)
        generated_keys = {
            ".antios/project_profile.json",
            ".antios/knowledge.json",
            ".antios/agent_topology.json",
            ".antios/tool_policy.json",
            ".agents/skills/antios/SKILL.md",
        }
        for k in generated_keys:
            if k in compiled_files:
                content = compiled_files[k]
                sha = hashlib.sha256(content.replace("\r\n", "\n").encode("utf-8")).hexdigest()
                generated_paths[k] = ArtifactRecord(
                    path=k,
                    ownership=ArtifactOwnership.GENERATED,
                    sha256=sha,
                    source_revision=self.source_revision,
                    generated_at=now_ts,
                )

        # Protected paths from adapter config
        protected_paths = list(adapter_config.protected_zones) + list(adapter_config.protected_domain_paths)
        if ".antios" not in protected_paths:
            protected_paths.append(".antios")

        # Preserve user owned paths from existing manifest if present
        user_owned: List[str] = []
        if existing_manifest:
            user_owned = list(existing_manifest.user_owned_paths)

        manifest = ProjectManifest(
            antios_version=CURRENT_ANTIOS_VERSION,
            schema_version=CURRENT_SCHEMA_VERSION,
            project_fingerprint=project_fingerprint,
            source_revision=self.source_revision,
            generated_at=now_ts,
            adaptation_state=AdaptationState.ADAPTED,
            installation_state=InstallationState.INSTALLED,
            managed_paths=managed_paths,
            generated_paths=generated_paths,
            user_owned_paths=user_owned,
            protected_paths=protected_paths,
            stale_paths=[],
            project_profile_reference=".antios/project_profile.json",
        )

        # Add manifest itself to compiled files
        compiled_files[".antios/manifest.json"] = manifest.to_json(indent=2)

        return CompilationResult(
            manifest=manifest,
            compiled_files=compiled_files,
            skipped_files=skipped_files,
            conflicts=conflicts,
            success=len(conflicts) == 0,
            summary=f"Compiled AntiOS 2.0 instance ({len(compiled_files)} artifacts prepared).",
        )

    def emit(
        self,
        result: CompilationResult,
        existing_manifest: Optional[ProjectManifest] = None,
        dry_run: bool = False,
    ) -> Tuple[bool, List[str], List[str]]:
        """Emits compiled files to target root respecting artifact ownership.

        Returns:
            (success, written_paths, conflict_errors)
        """
        written_paths: List[str] = []
        conflict_errors: List[str] = []

        for rel_path, content in result.compiled_files.items():
            content_sha = hashlib.sha256(content.replace("\r\n", "\n").encode("utf-8")).hexdigest()
            can_overwrite, reason = can_safely_overwrite(
                rel_path=rel_path,
                manifest=existing_manifest,
                target_root=self.target_root,
                proposed_content_sha=content_sha,
            )

            if not can_overwrite:
                conflict_errors.append(f"Refused to write '{rel_path}': {reason}")
                continue

            if not dry_run:
                target_file = self.target_root / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(content, encoding="utf-8", newline="\n")
            written_paths.append(rel_path)

        success = len(conflict_errors) == 0
        return success, written_paths, conflict_errors
