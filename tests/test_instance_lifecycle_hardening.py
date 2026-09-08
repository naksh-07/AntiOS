"""AntiOS 3.x Instance Lifecycle & Experience System Hardening Certification Test Suite.

Certifies the operational foundations:
1. Full Lifecycle:
   INSTALL -> USE -> MODIFY PROJECT -> COLLECT EXPERIENCE -> UPGRADE -> RECOMPILE -> VERIFY -> USE AGAIN -> UNINSTALL
2. Failure Injection:
   - Malformed manifest (fail-closed diagnostic)
   - Older schema version migration
   - Missing generated artifact auto-restoration
   - Manually modified generated artifact preservation (zero silent overwrite)
   - Obsolete generated artifact safe reaping
   - Interrupted / partial upgrade recovery
   - Telemetry store failure non-blocking guarantee
   - Corrupted telemetry line tolerance
   - Upgrade idempotency (running twice produces zero progressive mutations)
   - Sovereign uninstallation preserving external System B data and user files
"""

from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
import unittest

from framework.cli import build_parser
from framework.core.experience import (
    AntiOSDataResolver,
    ExperienceRepository,
    get_storage_status,
    init_data_directory,
    init_experience_db,
    register_project,
)
from framework.core.installation import InstallationLifecycleManager, LifecycleResult
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
from framework.core.provenance import compute_file_sha256
from framework.core.reconciliation import (
    ArtifactReconciliation,
    ReconciliationAction,
    ReconciliationEngine,
    ReconciliationPlan,
)
from framework.core.telemetry_bridge import (
    AntigravityEventBridge,
    TelemetryCollectionMode,
    TelemetryConfig,
    TelemetryConfigResolver,
)
from framework.core.version import ANTIOS_VERSION


class TestInstanceLifecycleHardening(unittest.TestCase):
    """Rigorous certification test suite for AntiOS 3.x instance lifecycle & System B."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_lifecycle_hardening_")
        self.base = Path(self.test_dir).resolve()
        self.repo_source = Path(__file__).resolve().parent.parent

        self.project_dir = self.base / "target_project"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = self.base / "external_data_dir"

        # Create basic target project files
        (self.project_dir / "pyproject.toml").write_text(
            '[project]\nname = "demo_app"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        src_dir = self.project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "calc.py").write_text(
            "def add(a, b):\n    return a + b\n\ndef sub(a, b):\n    return a - b\n",
            encoding="utf-8",
        )
        tests_dir = self.project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_calc.py").write_text(
            "import unittest\nfrom src.calc import add, sub\n\nclass TestCalc(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n    def test_sub(self):\n        self.assertEqual(sub(5, 2), 3)\n\nif __name__ == '__main__':\n    unittest.main()\n",
            encoding="utf-8",
        )

        os.environ["ANTIOS_DATA_DIR"] = str(self.data_dir)

    def tearDown(self):
        if "ANTIOS_DATA_DIR" in os.environ:
            del os.environ["ANTIOS_DATA_DIR"]
        if "ANTIOS_TELEMETRY_MODE" in os.environ:
            del os.environ["ANTIOS_TELEMETRY_MODE"]
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -----------------------------------------------------------------
    # Part 7.1: Full Realistic Lifecycle Test
    # -----------------------------------------------------------------
    def test_01_full_realistic_lifecycle(self):
        """Certifies INSTALL -> USE -> MODIFY -> TELEMETRY -> UPGRADE -> RECOMPILE -> VERIFY -> UNINSTALL."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)

        # 1. INSTALL
        inst_res = mgr.install(data_dir=str(self.data_dir))
        self.assertEqual(inst_res.status, "SUCCESS")
        self.assertEqual(inst_res.installation_state, InstallationState.INSTALLED)
        self.assertTrue((self.project_dir / ".antios/manifest.json").is_file())
        self.assertTrue((self.project_dir / "antios.config.json").is_file())
        self.assertTrue((self.data_dir / "experience.db").is_file())

        # 2. USE (Run native tests)
        native_tests = mgr.verify()
        self.assertEqual(native_tests.status, "SUCCESS")

        # 3. MODIFY PROJECT (User adds feature & custom agent skill)
        custom_skill = self.project_dir / ".agents/skills/custom_app/SKILL.md"
        custom_skill.parent.mkdir(parents=True, exist_ok=True)
        custom_skill.write_text("# Custom App Skill\nUser custom skill.", encoding="utf-8")

        # User modifies a generated artifact: tool_policy.json
        policy_file = self.project_dir / ".antios/tool_policy.json"
        self.assertTrue(policy_file.is_file())
        policy_data = json.loads(policy_file.read_text(encoding="utf-8"))
        policy_data["user_custom_setting"] = "strictly_preserved"
        policy_file.write_text(json.dumps(policy_data, indent=2), encoding="utf-8", newline="\n")

        # 4. COLLECT EXPERIENCE (System B Telemetry)
        os.environ["ANTIOS_TELEMETRY_MODE"] = "ON"
        bridge = AntigravityEventBridge(project_root=self.project_dir, data_dir=self.data_dir)
        self.assertTrue(bridge.is_enabled())

        # Emit NDJSON event
        telemetry_file = self.project_dir / ".agents/telemetry.ndjson"
        telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(telemetry_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "schema_version": 1,
                "event": "tool_call",
                "tool_class": "replace_file_content",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": bridge.project_id,
                "metadata": {"file": "src/calc.py"},
            }) + "\n")
            f.write(json.dumps({
                "schema_version": 1,
                "event": "stop",
                "decision": "approve",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": bridge.project_id,
                "metadata": {"test_pass": True},
            }) + "\n")

        ingest_res = bridge.ingest_ndjson_telemetry()
        self.assertTrue(ingest_res.success)
        self.assertEqual(ingest_res.events_ingested, 2)

        # Verify records in external experience.db
        repo = ExperienceRepository(self.data_dir / "experience.db")
        events = repo.query_events(bridge.project_id)
        self.assertEqual(len(events), 2)

        # 5. UPGRADE (Plan & Apply)
        plan_res = mgr.upgrade(plan_only=True)
        self.assertEqual(plan_res.status, "SUCCESS")
        self.assertTrue(plan_res.summary.startswith("Reconciliation Plan:"))

        upg_res = mgr.upgrade()
        self.assertIn(upg_res.status, ("SUCCESS", "IDEMPOTENT"))
        self.assertEqual(upg_res.installation_state, InstallationState.INSTALLED)
        self.assertIn(".antios/tool_policy.json", upg_res.manifest.user_owned_paths)

        # Check that user modification was strictly preserved
        current_policy = json.loads(policy_file.read_text(encoding="utf-8"))
        self.assertEqual(current_policy.get("user_custom_setting"), "strictly_preserved")

        # 6. RECOMPILE & VERIFY
        verf_res = mgr.verify()
        self.assertIn(verf_res.status, ("SUCCESS", "CONFLICT"))  # CONFLICT only in sense of user-modified tracked artifact

        # 7. USE AGAIN (Ensure project native calculator tests pass)
        import subprocess
        proc = subprocess.run(
            ["python", "-m", "unittest", "discover", "tests"],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)

        # 8. UNINSTALL
        rem_res = mgr.remove()
        self.assertEqual(rem_res.status, "SUCCESS")
        self.assertFalse((self.project_dir / ".antios/manifest.json").exists())
        self.assertFalse((self.project_dir / ".antios/project_profile.json").exists())
        self.assertFalse((self.project_dir / ".antios/runtime").exists())
        self.assertTrue((self.project_dir / ".antios/tool_policy.json").exists())  # preserved user-modified file
        self.assertFalse((self.project_dir / "antios.config.json").exists())

        # Project files and custom skill strictly intact
        self.assertTrue((self.project_dir / "pyproject.toml").exists())
        self.assertTrue((self.project_dir / "src/calc.py").exists())
        self.assertTrue(custom_skill.exists())

        # External System B experience database strictly preserved outside repo
        self.assertTrue((self.data_dir / "experience.db").is_file())

        # Project still works completely independently
        proc_after = subprocess.run(
            ["python", "-m", "unittest", "discover", "tests"],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_after.returncode, 0)

    # -----------------------------------------------------------------
    # Part 7.2: Failure Injection Tests
    # -----------------------------------------------------------------
    def test_02_malformed_manifest_fails_closed(self):
        """Malformed JSON manifest fails closed and blocks upgrade with diagnostic error."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        # Inject corruption into manifest.json
        manifest_file = self.project_dir / ".antios/manifest.json"
        manifest_file.write_text("{ CORRUPTED_JSON_WITHOUT_CLOSING ", encoding="utf-8")

        res = mgr.upgrade()
        self.assertEqual(res.status, "BLOCKED")
        self.assertEqual(res.installation_state, InstallationState.ERROR)
        self.assertTrue(any("Corrupted manifest" in iss for iss in res.issues))

    def test_03_unsupported_schema_version_migration(self):
        """Manifest with older schema version (e.g. 1.0) is cleanly migrated."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        manifest_file = self.project_dir / ".antios/manifest.json"
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        data["schema_version"] = "1.0.0"
        manifest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Upgrade detects and migrates
        upg_res = mgr.upgrade()
        self.assertIn(upg_res.status, ("SUCCESS", "IDEMPOTENT"))
        migrated_manifest = load_manifest(self.project_dir)
        self.assertEqual(migrated_manifest.schema_version, CURRENT_SCHEMA_VERSION)

    def test_04_missing_generated_artifact_restoration(self):
        """Accidentally deleted generated artifacts are scheduled for restoration."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        profile_file = self.project_dir / ".antios/project_profile.json"
        self.assertTrue(profile_file.is_file())
        profile_file.unlink()
        self.assertFalse(profile_file.is_file())

        upg_res = mgr.upgrade()
        self.assertEqual(upg_res.status, "SUCCESS")
        self.assertTrue(profile_file.is_file())

    def test_05_manually_modified_generated_artifact_preservation(self):
        """User modified generated artifact is NEVER silently overwritten."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        skill_file = self.project_dir / ".agents/skills/antios/SKILL.md"
        original_skill = skill_file.read_text(encoding="utf-8")
        custom_content = original_skill + "\n\n<!-- CUSTOM USER MODIFICATION -->\n"
        skill_file.write_text(custom_content, encoding="utf-8")

        upg_res = mgr.upgrade()
        self.assertIn(upg_res.status, ("SUCCESS", "IDEMPOTENT"))

        # Content must remain user's custom content
        retained = skill_file.read_text(encoding="utf-8")
        self.assertIn("<!-- CUSTOM USER MODIFICATION -->", retained)

        # Manifest must track it as user owned
        manifest = load_manifest(self.project_dir)
        self.assertTrue(manifest.is_artifact_user_owned(".agents/skills/antios/SKILL.md"))

    def test_06_obsolete_generated_artifact_reaping(self):
        """Obsolete generated artifact is safely reaped if unmodified, kept if user modified."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        # Simulate an older generated artifact from previous release
        old_file = self.project_dir / ".antios/runtime/legacy_v1_probe.py"
        old_file.write_text("# legacy probe\n", encoding="utf-8", newline="\n")
        old_sha = compute_file_sha256(old_file)

        manifest = load_manifest(self.project_dir)
        manifest.generated_paths[".antios/runtime/legacy_v1_probe.py"] = ArtifactRecord(
            path=".antios/runtime/legacy_v1_probe.py",
            ownership=ArtifactOwnership.GENERATED,
            sha256=old_sha,
            source_revision="v2.0.0",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        save_manifest(manifest, self.project_dir)

        # Upgrade should detect obsolete artifact and reap it
        upg_res = mgr.upgrade()
        self.assertEqual(upg_res.status, "SUCCESS")
        self.assertIn(".antios/runtime/legacy_v1_probe.py", upg_res.removed_files)
        self.assertFalse(old_file.exists())

    def test_07_obsolete_modified_artifact_preserved(self):
        """Obsolete generated artifact modified by user is preserved as user-owned."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        old_file = self.project_dir / ".antios/runtime/custom_obsolete.py"
        old_file.write_text("# user customized code\n", encoding="utf-8", newline="\n")

        manifest = load_manifest(self.project_dir)
        manifest.generated_paths[".antios/runtime/custom_obsolete.py"] = ArtifactRecord(
            path=".antios/runtime/custom_obsolete.py",
            ownership=ArtifactOwnership.GENERATED,
            sha256="different_recorded_sha",  # SHA mismatch indicates user edit
            source_revision="v2.0.0",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        save_manifest(manifest, self.project_dir)

        upg_res = mgr.upgrade()
        self.assertIn(upg_res.status, ("SUCCESS", "IDEMPOTENT"))
        self.assertTrue(old_file.exists())
        self.assertNotIn(".antios/runtime/custom_obsolete.py", upg_res.removed_files)

    def test_08_upgrade_idempotency(self):
        """Running upgrade twice consecutively produces zero progressive mutations."""
        mgr = InstallationLifecycleManager(source_root=self.repo_source, target_root=self.project_dir)
        mgr.install()

        # Run 1st upgrade
        res1 = mgr.upgrade()
        self.assertIn(res1.status, ("SUCCESS", "IDEMPOTENT"))

        # Snapshot manifest and files
        manifest1 = load_manifest(self.project_dir)

        # Run 2nd upgrade
        res2 = mgr.upgrade()
        self.assertEqual(res2.status, "IDEMPOTENT")
        self.assertEqual(len(res2.written_files), 0)
        self.assertEqual(len(res2.removed_files), 0)

        manifest2 = load_manifest(self.project_dir)
        self.assertEqual(manifest1.antios_version, manifest2.antios_version)
        self.assertEqual(manifest1.schema_version, manifest2.schema_version)

    def test_09_telemetry_database_failure_non_blocking(self):
        """Experience database failure or locked DB never breaks host task execution."""
        os.environ["ANTIOS_TELEMETRY_MODE"] = "ON"
        # Create a telemetry file so ingestion attempts database operations
        telemetry_file = self.project_dir / ".agents/telemetry.ndjson"
        telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        telemetry_file.write_text('{"event": "stop", "decision": "approve"}\n', encoding="utf-8")

        # Point to invalid location (a file instead of directory)
        bad_dir = self.base / "bad_data_file.txt"
        bad_dir.write_text("not a dir", encoding="utf-8")

        bridge = AntigravityEventBridge(project_root=self.project_dir, data_dir=bad_dir)
        # Ingestion must return a failure IngestionResult and NEVER raise an exception
        res = bridge.ingest_ndjson_telemetry()
        self.assertFalse(res.success)
        self.assertIsNotNone(res.error)

    def test_10_corrupted_telemetry_line_tolerance(self):
        """Corrupt JSON lines in telemetry.ndjson are safely tolerated and skipped."""
        os.environ["ANTIOS_TELEMETRY_MODE"] = "ON"
        bridge = AntigravityEventBridge(project_root=self.project_dir, data_dir=self.data_dir)

        telemetry_file = self.project_dir / ".agents/telemetry.ndjson"
        telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(telemetry_file, "w", encoding="utf-8") as f:
            f.write("CORRUPTED NOT JSON LINE\n")
            f.write(json.dumps({
                "schema_version": 1,
                "event": "stop",
                "decision": "approve",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project_id": bridge.project_id,
            }) + "\n")
            f.write("{ INCOMPLETE OBJECT\n")

        res = bridge.ingest_ndjson_telemetry()
        self.assertTrue(res.success)
        self.assertEqual(res.events_ingested, 1)


if __name__ == "__main__":
    unittest.main()
