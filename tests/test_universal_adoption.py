"""Unit & Integration Tests for AntiOS 2.0 Fresh Project Universal Adoption (Phase 100)."""

import os
from pathlib import Path
import tempfile
import unittest

from framework.core.universal_adoption import (
    ExecutionLabel,
    TwoWayAdaptationAudit,
    UniversalAdoptionCard,
    UniversalAdoptionProvingGround,
    UniversalAdoptionReport,
)


class TestUniversalAdoption(unittest.TestCase):
    """Tests for Phase 100 Fresh Project Universal Adoption Proving Ground."""

    def setUp(self):
        self.temp_sandbox = tempfile.mkdtemp(prefix="test_adopt_pg_")
        self.proving_ground = UniversalAdoptionProvingGround(sandbox_dir=self.temp_sandbox)

    def tearDown(self):
        self.proving_ground.cleanup()
        if os.path.exists(self.temp_sandbox):
            import shutil
            shutil.rmtree(self.temp_sandbox, ignore_errors=True)

    def test_run_full_adoption_campaign_19_steps(self):
        report = self.proving_ground.run_full_adoption_campaign()
        self.assertIsInstance(report, UniversalAdoptionReport)
        self.assertEqual(report.overall_status, "ADOPTABLE")
        self.assertEqual(len(report.step_results), 19)

        # Ensure all 19 steps succeeded
        for step in report.step_results:
            self.assertIn(step.status, ("SUCCESS", "VERIFIED"), f"Step {step.step_number} failed: {step.details}")
            self.assertIsInstance(step.execution_label, ExecutionLabel)
            self.assertGreater(len(step.artifacts_verified), 0)

    def test_two_way_adaptation_contract_and_zero_core_mutations(self):
        report = self.proving_ground.run_full_adoption_campaign()
        audit = report.two_way_audit
        self.assertIsNotNone(audit)
        self.assertTrue(audit.antios_to_project_verified)
        self.assertTrue(audit.project_to_antios_verified)
        self.assertEqual(audit.core_mutations_count, 0)

        # Assert all 6 categorization lists are populated
        self.assertGreaterEqual(len(audit.automatically_generated), 4)
        self.assertGreaterEqual(len(audit.explicit_project_config), 2)
        self.assertGreaterEqual(len(audit.required_human_approval), 2)
        self.assertGreaterEqual(len(audit.could_not_be_automated), 2)
        self.assertGreaterEqual(len(audit.remained_project_specific), 3)
        self.assertGreaterEqual(len(audit.refused_to_assume), 2)

    def test_universal_adoption_summary_card_bounded(self):
        report = self.proving_ground.run_full_adoption_campaign()
        self.assertIsNotNone(report.summary_card)
        card_md = report.summary_card.render_markdown()
        lines = card_md.strip().split("\n")
        self.assertLessEqual(len(lines), 25)
        self.assertIn("AntiOS 2.0 Universal Adoption Proving Ground Card", lines[0])
        self.assertIn("19/19", card_md)

    def test_target_business_logic_preserved_and_uncontaminated(self):
        report = self.proving_ground.run_full_adoption_campaign()
        target_root = self.proving_ground.project_root
        processor_file = target_root / "src" / "orders" / "processor.py"
        self.assertTrue(processor_file.exists())
        content = processor_file.read_text(encoding="utf-8")
        self.assertIn("def process_order", content)
        # AntiOS core internals must not be leaked into business logic
        self.assertNotIn("AntiOSConfig", content)
        self.assertNotIn("TaskDispatchPipeline", content)

    def test_clean_uninstallation_and_idempotence(self):
        pg = self.proving_ground
        pg.scaffold_target_project()
        from framework.core.installation import InstallationLifecycleManager
        mgr = InstallationLifecycleManager(source_root=pg.source_root, target_root=pg.project_root)

        # First install
        r1 = mgr.install()
        self.assertEqual(r1.status, "SUCCESS")

        # Idempotent re-install
        r2 = mgr.install()
        self.assertEqual(r2.status, "IDEMPOTENT")

        # Clean removal
        r3 = mgr.remove()
        self.assertEqual(r3.status, "SUCCESS")
        self.assertFalse((pg.project_root / ".antios").exists())


if __name__ == "__main__":
    unittest.main()
