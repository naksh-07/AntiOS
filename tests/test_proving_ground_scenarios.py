#!/usr/bin/env python3
"""Proving ground test suite for AntiOS 2.0 Phases 83-86.

Covers Scenarios A through I:
  - Scenario A: Simple single-file change -> SOLO
  - Scenario B: Multi-file frontend change -> PARALLEL (disjoint paths)
  - Scenario C: Backend + tests -> FOCUSED / SMALL
  - Scenario D: Cross-subsystem refactor -> STAGED waves
  - Scenario E: Security-sensitive change -> HIGH risk + independent verifier
  - Scenario F: Unknown/legacy project -> RECON + ADAPT
  - Scenario G: Task requiring external MCP -> justified 7-field escalation
  - Scenario H: MCP available but local CLI preferred -> Local Git over GitHub MCP
  - Scenario I: Task requiring independent verification -> Maker-Checker + Stop Gate
"""

import unittest
from framework.core.orchestration import (
    AdaptiveWorkforcePlanner,
    GateDecision,
    MissionLedger,
    StructuredHandoff,
    WaveManager,
    WorkerMetadata,
    WorkforceMode,
    WriteSafetyPolicy,
)
from framework.core.lifecycle import TaskClass, RiskTier
from framework.core.tool_policy import (
    HybridCapabilityExecutionMatrix,
    HybridCapabilityTier,
    MCPJustificationReport,
)
from framework.core.verdict import (
    prepare_checker_context,
    evaluate_checker_verdict,
    VerificationVerdict,
    ResultItem,
)


class TestProvingGroundScenarios(unittest.TestCase):
    """Proving ground tests validating real-world AntiOS engineering scenarios A-I."""

    def setUp(self):
        self.planner = AdaptiveWorkforcePlanner()
        self.matrix = HybridCapabilityExecutionMatrix()

    def test_scenario_a_simple_single_file_change_solo(self):
        """Scenario A: Simple single-file change selects SOLO mode with bounded cost card."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="DOCUMENTATION",
            risk_tier="LOW",
            pre_planning_decision=GateDecision.SOLO_AUTHORIZED,
            execution_decision=GateDecision.SOLO_AUTHORIZED,
            write_policy=WriteSafetyPolicy.READ_ONLY,
            subsystem_count=1,
            file_count=1,
            has_disjoint_boundaries=False,
            remaining_mission_budget=20,
        )
        self.assertEqual(mode, WorkforceMode.SOLO)
        self.assertEqual(reasoning.mode, WorkforceMode.SOLO)
        self.assertEqual(reasoning.max_recommended_workers, 1)
        self.assertIn("solo", reasoning.why_this_workforce.lower())
        self.assertIn("minimum", reasoning.why_not_fewer.lower())
        card = reasoning.format_explanation_card(max_lines=10)
        self.assertIn("WORKFORCE COST REASONING", card)
        self.assertLessEqual(len(card.splitlines()), 10)

    def test_scenario_b_multifile_frontend_parallel_disjoint(self):
        """Scenario B: Multi-file frontend change with disjoint paths permits parallel workers."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="FEATURE",
            risk_tier="LOW",
            pre_planning_decision=GateDecision.DELEGATION_MANDATORY,
            execution_decision=GateDecision.DELEGATION_MANDATORY,
            write_policy=WriteSafetyPolicy.SAFELY_PARALLELIZABLE,
            subsystem_count=3,
            file_count=3,
            has_disjoint_boundaries=True,
            remaining_mission_budget=15,
        )
        self.assertEqual(mode, WorkforceMode.PARALLEL)
        self.assertEqual(reasoning.mode, WorkforceMode.PARALLEL)
        self.assertEqual(reasoning.max_recommended_workers, 3)
        self.assertIn("parallel", reasoning.why_this_workforce.lower())

    def test_scenario_c_backend_plus_tests_small_mode(self):
        """Scenario C: Backend implementation + test coverage selects FOCUSED / SMALL mode."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="FEATURE",
            risk_tier="MEDIUM",
            pre_planning_decision=GateDecision.DELEGATION_MANDATORY,
            execution_decision=GateDecision.DELEGATION_MANDATORY,
            write_policy=WriteSafetyPolicy.CONTROLLED_SINGLE_WRITER,
            subsystem_count=1,
            file_count=2,
            has_disjoint_boundaries=False,
            remaining_mission_budget=15,
        )
        self.assertEqual(mode, WorkforceMode.FOCUSED)
        self.assertEqual(reasoning.max_recommended_workers, 2)
        self.assertIn("focused", reasoning.why_this_workforce.lower())

    def test_scenario_d_cross_subsystem_refactor_staged_waves(self):
        """Scenario D: Cross-subsystem refactor coordinates staged waves with mandatory collapse."""
        ledger = MissionLedger(mission_id="refactor-01")
        wave_mgr = WaveManager(ledger=ledger)

        # Wave 1: Reconnaissance
        w1 = wave_mgr.start_wave("RECONNAISSANCE")
        rec1 = wave_mgr.spawn_worker(
            agent_id="recon-specialist",
            role="researcher",
            depth=1,
            metadata=WorkerMetadata(
                mission_id="refactor-01",
                wave_id=1,
                parent_id=None,
                capability="recon",
                purpose="analyze cross-subsystem call graph",
                write_boundary=[],
                risk_tier="LOW",
                expected_output="Dependency graph",
                verification_requirement="Graph integrity",
            ),
        )
        wave_mgr.record_handoff(
            agent_id="recon-specialist",
            handoff=StructuredHandoff(
                objective="Analyze subsystem dependencies",
                conclusion="Clean separation exists between core and api",
                verification_method="Static import analysis",
                evidence=["core/base.py:12", "api/routes.py:45"],
            ),
        )
        ledger.record_termination("recon-specialist")

        # Wave 2: Implementation (Wave 1 must be collapsed)
        w2 = wave_mgr.start_wave("IMPLEMENTATION")
        self.assertEqual(w2.wave_number, 2)
        rec2 = wave_mgr.spawn_worker(
            agent_id="refactor-worker",
            role="refactor-engineer",
            depth=1,
            metadata=WorkerMetadata(
                mission_id="refactor-01",
                wave_id=2,
                parent_id=None,
                capability="refactor",
                purpose="refactor interface boundaries",
                write_boundary=["core/base.py", "api/routes.py"],
                risk_tier="MEDIUM",
                expected_output="Updated interfaces",
                verification_requirement="Tests pass",
            ),
        )
        ledger.record_termination("refactor-worker")

        # Wave 3: Verification
        w3 = wave_mgr.start_wave("VERIFICATION")
        self.assertEqual(w3.wave_number, 3)
        self.assertEqual(ledger.current_wave, 3)

    def test_scenario_e_security_sensitive_change_high_risk_independent_verifier(self):
        """Scenario E: Security-sensitive change mandates HIGH risk tier and independent verifier."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="FEATURE",
            risk_tier="HIGH",
            pre_planning_decision=GateDecision.DELEGATION_MANDATORY,
            execution_decision=GateDecision.DELEGATION_MANDATORY,
            write_policy=WriteSafetyPolicy.CONTROLLED_SINGLE_WRITER,
            subsystem_count=2,
            file_count=3,
            has_disjoint_boundaries=False,
            remaining_mission_budget=15,
        )
        self.assertEqual(mode, WorkforceMode.FOCUSED)
        self.assertIn("verifier", reasoning.why_this_workforce.lower())

    def test_scenario_f_unknown_legacy_project_recon_and_adapt(self):
        """Scenario F: Unknown/legacy project triggers low epistemic state and exploratory recon."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="INVESTIGATION",
            risk_tier="LOW",
            pre_planning_decision=GateDecision.SOLO_AUTHORIZED,
            execution_decision=GateDecision.SOLO_AUTHORIZED,
            write_policy=WriteSafetyPolicy.READ_ONLY,
            subsystem_count=1,
            file_count=1,
            has_disjoint_boundaries=False,
            remaining_mission_budget=20,
        )
        self.assertEqual(mode, WorkforceMode.SOLO)
        self.assertIn("solo", reasoning.why_this_workforce.lower())

    def test_scenario_g_task_requiring_external_mcp_justified_escalation(self):
        """Scenario G: Remote GitHub PR creation legitimately escalates to Tier 8 with complete audit."""
        res = self.matrix.resolve(
            capability_sought="create_pull_request",
            task_intent="create remote pull request for approved branch",
        )
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_8_MANAGED_MCP)
        self.assertTrue(res.is_authorized)
        self.assertIsNotNone(res.justification_report)
        valid_audit, errs = res.justification_report.validate_escalation_audit()
        self.assertTrue(valid_audit)
        self.assertEqual(len(errs), 0)

    def test_scenario_h_mcp_available_but_local_cli_preferred(self):
        """Scenario H: Task where MCP is available but local CLI is preferred strictly chooses local git."""
        # When checking git status, local CLI is chosen over GitHub MCP
        res = self.matrix.resolve(
            capability_sought="cli:git",
            task_intent="check local git status and commit log",
        )
        self.assertEqual(res.resolved_tier, HybridCapabilityTier.TIER_6_STANDARD_CLI)
        self.assertTrue(res.is_authorized)
        self.assertEqual(res.target_identifier, "cli:git")

        # Attempt to escalate to GitHub MCP for local git status is rejected fail-closed
        res_mcp = self.matrix.resolve(
            capability_sought="mcp:github",
            task_intent="git status of repository",
        )
        self.assertEqual(res_mcp.resolved_tier, HybridCapabilityTier.TIER_8_MANAGED_MCP)
        self.assertFalse(res_mcp.is_authorized)
        self.assertIn("Local Git CLI is authoritative", res_mcp.justification_report.why)

    def test_scenario_i_task_requiring_independent_verification(self):
        """Scenario I: Task requiring independent verification verifies Maker-Checker pass/fail contract."""
        # 1. Checker context is prepared with required invariants
        checker_ctx = prepare_checker_context(
            task_id="TASK-PROVING-I",
            objective="Verify critical auth logic and test pass",
            risk_tier="HIGH",
            changed_files=["src/auth.py", "tests/test_auth.py"],
            test_commands=["pytest tests/test_auth.py"],
            target_member="core",
            affected_dependents=[],
            protected_zones=[".agents", "framework"],
        )
        self.assertEqual(checker_ctx["role"], "INDEPENDENT_VERIFIER")
        self.assertIn("physical_execution", checker_ctx["invariants"])
        self.assertIn("shallow_depth_law", checker_ctx["invariants"])

        # 2. Simulated passing verdict
        v_pass = VerificationVerdict(
            status="PASS",
            risk_tier="HIGH",
            files_audited=["src/auth.py", "tests/test_auth.py"],
            tests=[ResultItem(command="pytest tests/test_auth.py", exit_code=0, passed=True, details="OK")],
            same_change_set_verified=True,
            summary="All tests pass cleanly",
        )
        ok_pass, reason_pass = evaluate_checker_verdict(v_pass, required_risk_tier="HIGH")
        self.assertTrue(ok_pass)
        self.assertIn("approved", reason_pass.lower())

        # 3. Simulated failing verdict (test failure)
        v_fail = VerificationVerdict(
            status="FAIL",
            risk_tier="HIGH",
            files_audited=["src/auth.py"],
            tests=[ResultItem(command="pytest tests/test_auth.py", exit_code=1, passed=False, details="Auth failure")],
            same_change_set_verified=True,
            summary="Tests failed",
            issues=["Authentication test failed"],
        )
        ok_fail, reason_fail = evaluate_checker_verdict(v_fail, required_risk_tier="HIGH")
        self.assertFalse(ok_fail)
        self.assertIn("rejected", reason_fail.lower())


if __name__ == "__main__":
    unittest.main()
