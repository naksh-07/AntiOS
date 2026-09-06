"""Unit & Integration Tests for AntiOS 2.0 Production Readiness & Architecture Freeze (Phase 101)."""

from pathlib import Path
import unittest

from framework.core.architecture_freeze import (
    ArchitectureFreezeValidator,
    CriticalInvariant,
    DimensionEvaluation,
    InvariantRegistry,
    InvariantStatus,
    ProductionReadinessCard,
    ProductionReadinessEngine,
    ProductionReadinessReport,
    ReadinessDimension,
    ReadinessStatus,
)


class TestProductionReadinessAndFreeze(unittest.TestCase):
    """Tests for Phase 101 Production Readiness, Architecture Freeze & Invariant Registry."""

    def setUp(self):
        self.engine = ProductionReadinessEngine()

    def test_all_15_readiness_dimensions_production_ready(self):
        report = self.engine.evaluate_all()
        self.assertIsInstance(report, ProductionReadinessReport)
        self.assertEqual(report.overall_status, ReadinessStatus.PRODUCTION_READY)
        self.assertEqual(len(report.dimensions), 15)

        for dim in ReadinessDimension:
            self.assertIn(dim.value, report.dimensions)
            eval_res = report.dimensions[dim.value]
            self.assertEqual(eval_res.status, ReadinessStatus.PRODUCTION_READY)
            self.assertEqual(eval_res.score, 1.0)
            self.assertTrue(len(eval_res.rationale) > 0)
            self.assertGreaterEqual(len(eval_res.supporting_evidence), 1)

    def test_production_readiness_card_bounded(self):
        report = self.engine.evaluate_all()
        self.assertIsNotNone(report.summary_card)
        card_md = report.summary_card.render_markdown()
        lines = card_md.strip().split("\n")
        self.assertLessEqual(len(lines), 25)
        self.assertIn("AntiOS 2.0 Production Readiness & Architecture Freeze Card", lines[0])
        self.assertIn("15/15", card_md)
        self.assertIn("FROZEN", card_md)

    def test_invariant_registry_completeness_and_status(self):
        invariants = InvariantRegistry.get_canonical_invariants()
        self.assertEqual(len(invariants), 20)

        for inv in invariants:
            self.assertEqual(inv.current_status, InvariantStatus.VERIFIED)
            self.assertTrue(inv.invariant_id.startswith("INV-"))
            self.assertTrue(len(inv.statement) > 0)
            self.assertTrue(len(inv.enforcement_location) > 0)
            self.assertTrue(len(inv.verification_method) > 0)
            self.assertTrue(len(inv.supporting_evidence) > 0)
            self.assertTrue(len(inv.failure_consequence) > 0)

    def test_invariant_supporting_evidence_files_exist(self):
        repo_root = self.engine.repo_root
        invariants = InvariantRegistry.get_canonical_invariants()
        for inv in invariants:
            # Evidence string may have multiple comma-separated files or functions
            evidence_items = [e.strip() for e in inv.supporting_evidence.split(",")]
            for item in evidence_items:
                file_rel = item.split(":")[0].strip()
                if file_rel.endswith(".py") or file_rel.endswith(".md"):
                    target_path = repo_root / file_rel
                    self.assertTrue(
                        target_path.exists(),
                        f"Supporting evidence path '{file_rel}' for {inv.invariant_id} must physically exist!",
                    )

    def test_invariant_registry_markdown_rendering(self):
        md = InvariantRegistry.render_markdown()
        self.assertIn("# AntiOS 2.0 Canonical Invariant Registry", md)
        self.assertIn("INV-01", md)
        self.assertIn("INV-20", md)

    def test_architecture_freeze_compliance_on_repo(self):
        compliant, issues = ArchitectureFreezeValidator.validate_freeze_compliance(self.engine.repo_root)
        self.assertTrue(compliant, f"Freeze compliance failed with issues: {issues}")
        self.assertEqual(len(issues), 0)

    def test_architecture_freeze_adversarial_rejection(self):
        # Validate that prohibited subsystem list contains expected banned patterns
        self.assertIn("background_daemon", ArchitectureFreezeValidator.PROHIBITED_SUBSYSTEMS)
        self.assertIn("vector_database", ArchitectureFreezeValidator.PROHIBITED_SUBSYSTEMS)
        self.assertIn("custom_scheduler", ArchitectureFreezeValidator.PROHIBITED_SUBSYSTEMS)
        self.assertIn("agent_swarm_consensus", ArchitectureFreezeValidator.PROHIBITED_SUBSYSTEMS)


if __name__ == "__main__":
    unittest.main()
