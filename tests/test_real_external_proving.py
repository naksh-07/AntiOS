"""AntiOS 3.x Real External Project Lifecycle & System B Certification.

Full end-to-end integration test proving:
1. Real Multi-module Project Setup: Python library with data models, business logic, and unittest suite.
2. AntiOS Installation: antios install with external data directory outside target repo.
3. Realistic Agent Usage: Tool calls, code modification, testing, stop gate validation.
4. Experience System Intelligence: Telemetry ingestion, event sanitization, session aggregation, report generation.
5. Instance Upgrade: Simulated upgrade, reconciliation engine, user modification preservation, re-compilation.
6. Upgrade Idempotency: Second consecutive upgrade is verified strictly no-op / IDEMPOTENT.
7. Sovereign Uninstallation: Clean removal leaving project completely intact, runnable, and independent.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from framework.core.experience import (
    AntiOSDataResolver,
    ExperienceRepository,
    init_data_directory,
    init_experience_db,
)
from framework.core.experience_analytics import (
    ExperienceAnalyticsEngine,
    ExperienceReport,
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
from framework.core.telemetry_bridge import (
    AntigravityEventBridge,
    TelemetryCollectionMode,
    TelemetryConfig,
)
from framework.core.version import ANTIOS_VERSION


class TestRealExternalProving(unittest.TestCase):
    """Rigorous end-to-end certification on a realistic disposable external codebase."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp(prefix="antios_proving_e2e_")
        self.base = Path(self.test_root).resolve()
        self.repo_source = Path(__file__).resolve().parent.parent

        # 1. Project Directory & External System B Data Directory
        self.project_dir = self.base / "orders_engine"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = self.base / "external_system_b_store"

        # 2. Build Realistic Multi-Module Project
        (self.project_dir / "pyproject.toml").write_text(
            '[project]\nname = "orders-engine"\nversion = "1.2.0"\nauthors = [{name="Ops Team"}]\n',
            encoding="utf-8",
        )
        (self.project_dir / "README.md").write_text(
            "# Orders Engine\nHigh throughput order pricing and taxation pipeline.\n",
            encoding="utf-8",
        )

        src_dir = self.project_dir / "src" / "orders"
        src_dir.mkdir(parents=True, exist_ok=True)

        (src_dir / "__init__.py").write_text('__version__ = "1.2.0"\n', encoding="utf-8")

        (src_dir / "models.py").write_text(
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class Item:\n"
            "    sku: str\n"
            "    price: float\n"
            "    quantity: int\n\n"
            "    @property\n"
            "    def subtotal(self) -> float:\n"
            "        return round(self.price * self.quantity, 2)\n",
            encoding="utf-8",
        )

        (src_dir / "pricing.py").write_text(
            "from typing import List\n"
            "from .models import Item\n\n"
            "def calculate_total(items: List[Item], discount_rate: float = 0.0) -> float:\n"
            "    raw = sum(i.subtotal for i in items)\n"
            "    discounted = raw * (1.0 - discount_rate)\n"
            "    return round(discounted, 2)\n",
            encoding="utf-8",
        )

        tests_dir = self.project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "test_pricing.py").write_text(
            "import unittest\n"
            "from src.orders.models import Item\n"
            "from src.orders.pricing import calculate_total\n\n"
            "class TestPricing(unittest.TestCase):\n"
            "    def test_basic_subtotal(self):\n"
            "        item = Item(sku='SKU1', price=10.0, quantity=3)\n"
            "        self.assertEqual(item.subtotal, 30.0)\n\n"
            "    def test_discount(self):\n"
            "        items = [Item('A', 50.0, 1), Item('B', 25.0, 2)]\n"
            "        self.assertEqual(calculate_total(items, 0.1), 90.0)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

        # Baseline native test execution check
        proc = subprocess.run(
            ["python", "-m", "unittest", "discover", "tests"],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Baseline tests failed: {proc.stderr}")

    def tearDown(self):
        if "ANTIOS_DATA_DIR" in os.environ:
            del os.environ["ANTIOS_DATA_DIR"]
        if "ANTIOS_TELEMETRY_MODE" in os.environ:
            del os.environ["ANTIOS_TELEMETRY_MODE"]
        shutil.rmtree(self.test_root, ignore_errors=True)

    def test_full_external_proving_lifecycle(self):
        """End-to-end certification of the complete AntiOS 3.x instance lifecycle."""
        # -------------------------------------------------------------
        # STEP 1: INSTALL with external data directory
        # -------------------------------------------------------------
        mgr = InstallationLifecycleManager(
            source_root=self.repo_source,
            target_root=self.project_dir,
        )
        install_res = mgr.install(data_dir=self.data_dir)
        self.assertEqual(install_res.status, "SUCCESS")
        self.assertEqual(install_res.installation_state, InstallationState.INSTALLED)
        self.assertTrue((self.project_dir / ".antios/manifest.json").is_file())
        self.assertTrue((self.project_dir / "antios.config.json").is_file())
        self.assertTrue((self.project_dir / ".agents/skills/antios/SKILL.md").is_file())
        self.assertTrue((self.project_dir / "AGENTS.md").is_file())
        self.assertTrue((self.project_dir / ".agents/routes.json").is_file())

        # Verify manifest records
        manifest = load_manifest(self.project_dir)
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.antios_version, ANTIOS_VERSION)
        self.assertEqual(manifest.metadata.get("data_dir"), str(self.data_dir))
        self.assertIn(".antios/tool_policy.json", manifest.generated_paths)
        self.assertIn("antios.config.json", manifest.managed_paths)

        # Verify external System B database initialized outside repo
        db_path = self.data_dir / "experience.db"
        self.assertTrue(db_path.is_file())

        # -------------------------------------------------------------
        # STEP 2: REALISTIC AGENT USE & TELEMETRY COLLECTION
        # -------------------------------------------------------------
        os.environ["ANTIOS_DATA_DIR"] = str(self.data_dir)
        os.environ["ANTIOS_TELEMETRY_MODE"] = "ON"

        bridge = AntigravityEventBridge(
            project_root=self.project_dir,
            data_dir=self.data_dir,
            mode=TelemetryCollectionMode.ON,
        )
        self.assertTrue(bridge.is_enabled())

        # Simulate agent modifying native project code (adding tax logic)
        pricing_file = self.project_dir / "src/orders/pricing.py"
        pricing_content = pricing_file.read_text(encoding="utf-8")
        pricing_content += (
            "\ndef calculate_tax(amount: float, tax_rate: float = 0.08) -> float:\n"
            "    return round(amount * tax_rate, 2)\n"
        )
        pricing_file.write_text(pricing_content, encoding="utf-8")

        test_pricing_file = self.project_dir / "tests/test_pricing.py"
        test_content = test_pricing_file.read_text(encoding="utf-8")
        test_content = test_content.replace(
            "from src.orders.pricing import calculate_total",
            "from src.orders.pricing import calculate_total, calculate_tax",
        )
        test_content = test_content.replace(
            "    def test_discount(self):",
            "    def test_tax(self):\n        self.assertEqual(calculate_tax(100.0, 0.05), 5.0)\n\n    def test_discount(self):",
        )
        test_pricing_file.write_text(test_content, encoding="utf-8")

        # Run native tests to verify agent changes pass
        proc_mid = subprocess.run(
            ["python", "-m", "unittest", "discover", "tests"],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_mid.returncode, 0)

        # Simulate Antigravity runtime telemetry output (.agents/telemetry.ndjson)
        telemetry_file = self.project_dir / ".agents/telemetry.ndjson"
        telemetry_file.parent.mkdir(parents=True, exist_ok=True)

        now_ts = datetime.now(timezone.utc).isoformat()
        with open(telemetry_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "schema_version": 1,
                "event": "tool_call",
                "tool": "replace_file_content",
                "timestamp": now_ts,
                "project_id": bridge.project_id,
                "metadata": {"path": "src/orders/pricing.py", "lines_changed": 3},
            }) + "\n")
            f.write(json.dumps({
                "schema_version": 1,
                "event": "stop",
                "decision": "approve",
                "timestamp": now_ts,
                "project_id": bridge.project_id,
                "metadata": {"reason": "Verification suite passed with exit code 0."},
            }) + "\n")

        # Ingest telemetry through non-blocking bridge
        ingest_res = bridge.ingest_ndjson_telemetry()
        self.assertTrue(ingest_res.success)
        self.assertEqual(ingest_res.events_ingested, 2)

        # -------------------------------------------------------------
        # STEP 3: VERIFY EXPERIENCE INTELLIGENCE (System B)
        # -------------------------------------------------------------
        repo = ExperienceRepository(db_path)
        events = repo.query_events(project_id=bridge.project_id)
        self.assertGreaterEqual(len(events), 2)

        # Verify event sanitation and fields
        tool_ev = next((e for e in events if e.get("event_type") == "TOOL_CALL"), None)
        self.assertIsNotNone(tool_ev)
        self.assertEqual(tool_ev.get("epistemic_grade"), "FACT")

        stop_ev = next((e for e in events if e.get("event_type") == "STOP_GATE_RESULT"), None)
        self.assertIsNotNone(stop_ev)
        self.assertEqual(stop_ev.get("epistemic_grade"), "FACT")
        payload = json.loads(stop_ev.get("payload_json", "{}"))
        self.assertIn("reason", payload)

        # Generate Experience Intelligence Report via Analytics Engine
        analytics_engine = ExperienceAnalyticsEngine(db_path)
        report = analytics_engine.analyze_project(bridge.project_id)
        self.assertEqual(report.scope, "PROJECT")
        self.assertEqual(report.project_id, bridge.project_id)
        self.assertGreaterEqual(report.data_coverage.get("engineering_events", 0), 2)
        md_text = report.to_markdown()
        self.assertIn("# AntiOS Experience Intelligence Report", md_text)

        # -------------------------------------------------------------
        # STEP 4: USER CUSTOMIZATIONS & SIMULATED UPGRADE
        # -------------------------------------------------------------
        # User customizes an AntiOS file (.antios/tool_policy.json)
        policy_path = self.project_dir / ".antios/tool_policy.json"
        policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_data["user_custom_rule"] = "ALLOW_INLINE_PROBES"
        policy_path.write_text(json.dumps(policy_data, indent=2), encoding="utf-8")

        # User authors a custom skill (.agents/skills/deploy/SKILL.md)
        custom_skill = self.project_dir / ".agents/skills/deploy/SKILL.md"
        custom_skill.parent.mkdir(parents=True, exist_ok=True)
        custom_skill.write_text("---\nname: deploy\ndescription: Custom deployment skill\n---\n# Deploy\n", encoding="utf-8")

        # Simulate instance running on previous version
        manifest = load_manifest(self.project_dir)
        manifest.antios_version = "2.9.0"
        manifest.source_revision = "v2.9.0"
        save_manifest(manifest, self.project_dir)

        # Execute Upgrade Plan
        plan_res = mgr.upgrade(plan_only=True)
        self.assertEqual(plan_res.status, "SUCCESS")
        self.assertTrue(plan_res.summary.startswith("Reconciliation Plan:"))

        # Apply Upgrade
        upg_res = mgr.upgrade()
        self.assertIn(upg_res.status, ("SUCCESS", "IDEMPOTENT"))
        self.assertEqual(upg_res.installation_state, InstallationState.INSTALLED)

        # Verify user modifications were strictly preserved
        updated_policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(updated_policy.get("user_custom_rule"), "ALLOW_INLINE_PROBES")
        self.assertTrue(custom_skill.is_file())

        upgraded_manifest = load_manifest(self.project_dir)
        self.assertEqual(upgraded_manifest.antios_version, ANTIOS_VERSION)
        self.assertIn(".antios/tool_policy.json", upgraded_manifest.user_owned_paths)

        # -------------------------------------------------------------
        # STEP 5: VERIFY UPGRADE IDEMPOTENCY
        # -------------------------------------------------------------
        idemp_res = mgr.upgrade()
        self.assertEqual(idemp_res.status, "IDEMPOTENT")
        self.assertEqual(len(idemp_res.written_files), 0)
        self.assertEqual(len(idemp_res.removed_files), 0)

        # -------------------------------------------------------------
        # STEP 6: SOVEREIGN UNINSTALLATION
        # -------------------------------------------------------------
        rem_res = mgr.remove()
        self.assertEqual(rem_res.status, "SUCCESS")

        # AntiOS core generated runtime files removed
        self.assertFalse((self.project_dir / ".antios/manifest.json").exists())
        self.assertFalse((self.project_dir / ".antios/project_profile.json").exists())
        self.assertFalse((self.project_dir / ".antios/runtime").exists())
        self.assertFalse((self.project_dir / "antios.config.json").exists())

        # User-modified and user-authored files preserved
        self.assertTrue(policy_path.is_file())  # user-modified tool policy preserved!
        self.assertTrue(custom_skill.is_file())  # custom skill preserved!

        # Project files completely intact
        self.assertTrue((self.project_dir / "pyproject.toml").exists())
        self.assertTrue((self.project_dir / "src/orders/pricing.py").exists())
        self.assertTrue((self.project_dir / "tests/test_pricing.py").exists())

        # External System B experience database still exists and is untouched
        self.assertTrue(db_path.is_file())
        repo_after = ExperienceRepository(db_path)
        events_after = repo_after.query_events(project_id=bridge.project_id)
        self.assertGreaterEqual(len(events_after), 2)

        # Project unit tests pass 100% natively without AntiOS
        final_proc = subprocess.run(
            ["python", "-m", "unittest", "discover", "tests"],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
        )
        self.assertEqual(final_proc.returncode, 0, f"Final project tests failed: {final_proc.stderr}")


if __name__ == "__main__":
    unittest.main()
