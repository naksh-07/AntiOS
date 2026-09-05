"""Tests for Phase 91: Mission Evaluation Engine.

Verifies:
1. Deterministic evaluation across 11 canonical dimensions.
2. 4 Evaluation statuses: PASS, FAIL, BLOCKED, INCONCLUSIVE.
3. Fail-closed on missing physical test verification for MEDIUM/HIGH risk.
4. Fail-closed on test failures or non-zero exit codes.
5. Fail-closed on broken invariants.
6. Conflicting evidence resolution to INCONCLUSIVE.
7. Maker-Checker enforcement rejecting worker self-certification on HIGH risk.
8. Strictly bounded MissionEvaluationCard (<= 25 lines).
9. All 11 evaluation dimensions presence.
10. Stale context evaluation rejection.
"""

import unittest

from framework.core.evidence import (
    ArtifactFingerprint,
    EpistemicCategory,
    EvidenceBuilder,
    EvidenceItem,
    EvidencePackage,
    EvidenceState,
)
from framework.core.mission_evaluation import (
    EvaluationStatus,
    IndependentVerifierContract,
    MissionEvaluationCard,
    MissionEvaluationDimension,
    MissionEvaluationEngine,
    MissionEvaluationResult,
)


class TestMissionEvaluation(unittest.TestCase):
    """Test suite for Phase 91 Mission Evaluation Engine."""

    def test_four_evaluation_statuses(self):
        """Rule: EvaluationStatus covers PASS, FAIL, BLOCKED, INCONCLUSIVE."""
        statuses = {s.value for s in EvaluationStatus}
        self.assertEqual(statuses, {"PASS", "FAIL", "BLOCKED", "INCONCLUSIVE"})

    def test_all_eleven_dimensions_defined(self):
        """Rule: Exactly 11 canonical evaluation dimensions exist."""
        self.assertEqual(len(MissionEvaluationDimension), 11)

    def test_deterministic_pass_with_authoritative_evidence(self):
        """Rule: Mission with valid criteria, passing tests, clean invariants, and verifier passes."""
        builder = EvidenceBuilder(
            mission_id="m-pass-1",
            intent="Add verified feature",
            acceptance_criteria=["Feature works", "Tests pass"],
        )
        builder.track_file_change("core/feat.py", "old", "new")
        builder.add_command_evidence("pytest tests/test_feat.py", 0, "1 passed in 0.05s", criteria_keys=["crit-1", "crit-2"])
        builder.package.record_invariant("Constitutional caps respected", True)
        builder.package.workforce_summary = {
            "active_workers_per_wave_peak": 1,
            "total_launches": 1,
            "delegation_depth": 1,
            "all_waves_collapsed": True,
        }
        builder.package.context_summary = {
            "budget_respected": True,
            "safety_invariants_loaded": True,
        }
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
            maker_identity="primary-engineer",
            checker_identity="checker-agent",
            is_independent_checker=True,
        )
        self.assertEqual(res.overall_status, EvaluationStatus.PASS)
        self.assertTrue(res.is_passed())
        self.assertEqual(len(res.dimension_evaluations), 11)

    def test_fail_closed_on_missing_physical_tests_medium_high_risk(self):
        """Rule: MEDIUM/HIGH risk tasks without physical test verification FAIL closed."""
        builder = EvidenceBuilder(
            mission_id="m-no-tests",
            intent="Refactor core security",
            acceptance_criteria=["Security refactored"],
        )
        builder.track_file_change("core/auth.py", "old_auth", "new_auth")
        # No tests or commands added!
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="HIGH",
            maker_identity="primary-engineer",
            checker_identity="checker-agent",
            is_independent_checker=True,
        )
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertEqual(
            res.dimension_evaluations[MissionEvaluationDimension.TEST_VERIFICATION.value].status,
            EvaluationStatus.FAIL,
        )

    def test_fail_closed_on_test_failure(self):
        """Rule: Test failures lead to deterministic evaluation FAIL."""
        builder = EvidenceBuilder(
            mission_id="m-failed-test",
            intent="Fix bug",
            acceptance_criteria=["Bug fixed"],
        )
        builder.add_command_evidence("pytest tests/test_bug.py", 1, "1 FAILED in 0.05s")
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
        )
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)

    def test_fail_closed_on_broken_invariant(self):
        """Rule: Broken invariant leads to deterministic evaluation FAIL."""
        builder = EvidenceBuilder(
            mission_id="m-inv-fail",
            intent="Routine task",
            acceptance_criteria=["Clean build"],
        )
        builder.add_command_evidence("pytest", 0, "OK")
        builder.package.record_invariant("Single writer policy", False, "Two workers wrote to same file")
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
        )
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertEqual(
            res.dimension_evaluations[MissionEvaluationDimension.INVARIANT_COMPLIANCE.value].status,
            EvaluationStatus.FAIL,
        )

    def test_conflicting_evidence_resolves_to_inconclusive(self):
        """Rule: Conflicting evidence resolves to INCONCLUSIVE."""
        builder = EvidenceBuilder(
            mission_id="m-conflict",
            intent="Investigation with conflicting findings",
            acceptance_criteria=["Determine root cause"],
        )
        item1 = EvidenceItem(
            evidence_id="ev-pass",
            mission_id="m-conflict",
            intent="Run unit test",
            provenance="runner A",
            state=EvidenceState.VERIFIED,
            commands_executed=["pytest"],
            command_exit_codes={"pytest": 0},
        )
        item2 = EvidenceItem(
            evidence_id="ev-fail",
            mission_id="m-conflict",
            intent="Run linter",
            provenance="runner B",
            state=EvidenceState.CONFLICTING,
            commands_executed=["flake8"],
            command_exit_codes={"flake8": 1},
        )
        builder.package.add_evidence_item(item1)
        builder.package.add_evidence_item(item2)
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
        )
        self.assertEqual(res.overall_status, EvaluationStatus.INCONCLUSIVE)

    def test_maker_checker_self_certification_rejected_on_high_risk(self):
        """Rule: Maker cannot self-certify HIGH-risk task without independent checker."""
        builder = EvidenceBuilder(
            mission_id="m-high-risk",
            intent="Database schema migration",
            acceptance_criteria=["Migration applied", "Tests pass"],
        )
        builder.add_command_evidence("alembic upgrade head", 0, "Success")
        pkg = builder.build()

        # Maker is primary-engineer, checker is same primary-engineer!
        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="HIGH",
            maker_identity="primary-engineer",
            checker_identity="primary-engineer",
            is_independent_checker=False,
            enforce_maker_checker=True,
        )
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertIn("Maker-Checker Violation", " ".join(res.metadata.get("failure_reasons", [])))

    def test_evaluation_card_bounded_lines(self):
        """Rule: Formatted MissionEvaluationCard strictly satisfies <= 25 lines."""
        builder = EvidenceBuilder(
            mission_id="m-card-test",
            intent="Verify card formatting",
            acceptance_criteria=["Card bounded"],
        )
        builder.add_command_evidence("python tests/run_all.py", 0, "OK")
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
            maker_identity="primary-engineer",
            checker_identity="independent-verifier",
            is_independent_checker=True,
        )
        card_text = res.card.format_card(max_lines=25)
        lines = card_text.splitlines()
        self.assertLessEqual(len(lines), 25)
        self.assertIn("=== ANTIOS MISSION EVALUATION ===", card_text)
        self.assertIn("Verdict:", card_text)

    def test_stale_context_without_refresh_fails_freshness_dimension(self):
        """Rule: Stale context without refresh fails FRESHNESS_REALITY_ALIGNMENT."""
        builder = EvidenceBuilder(
            mission_id="m-stale",
            intent="Edit on stale state",
            acceptance_criteria=["Modify logic"],
        )
        builder.add_command_evidence("pytest", 0, "OK")
        # Add item marked as STALE
        stale_item = EvidenceItem(
            evidence_id="ev-stale",
            mission_id="m-stale",
            intent="Read stale file",
            provenance="disk cache",
            freshness_state="STALE",
            commands_executed=["cat"],
            command_exit_codes={"cat": 0},
        )
        builder.package.add_evidence_item(stale_item)
        pkg = builder.build()

        res = MissionEvaluationEngine.evaluate(
            evidence_package=pkg,
            risk_tier="LOW",
        )
        self.assertEqual(res.overall_status, EvaluationStatus.FAIL)
        self.assertEqual(
            res.dimension_evaluations[MissionEvaluationDimension.FRESHNESS_REALITY_ALIGNMENT.value].status,
            EvaluationStatus.FAIL,
        )


if __name__ == "__main__":
    unittest.main()
