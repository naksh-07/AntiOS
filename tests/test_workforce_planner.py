"""Unit tests for Phase 84 Adaptive Workforce Planner and Cost Reasoning."""

import unittest

from framework.core.orchestration import (
    AdaptiveWorkforcePlanner,
    DispatchGateType,
    DualDispatchGates,
    GateDecision,
    WorkforceCostReasoning,
    WorkforceMode,
    WriteSafetyPolicy,
)


class TestWorkforcePlanner(unittest.TestCase):
    """Verifies Phase 84 Adaptive Workforce Planner with 12-input evaluation and cost reasoning."""

    def test_plan_solo_for_low_risk_documentation(self):
        """Low risk documentation task evaluates to SOLO with cost reasoning."""
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
        self.assertIn("single", reasoning.why_not_more.lower())

    def test_plan_parallel_for_disjoint_files(self):
        """Independent streams across disjoint files evaluate to PARALLEL."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="FEATURE",
            risk_tier="MEDIUM",
            pre_planning_decision=GateDecision.DELEGATION_MANDATORY,
            execution_decision=GateDecision.DELEGATION_MANDATORY,
            write_policy=WriteSafetyPolicy.SAFELY_PARALLELIZABLE,
            subsystem_count=3,
            file_count=4,
            has_disjoint_boundaries=True,
            remaining_mission_budget=15,
        )
        self.assertEqual(mode, WorkforceMode.PARALLEL)
        self.assertEqual(reasoning.mode, WorkforceMode.PARALLEL)
        self.assertGreaterEqual(reasoning.max_recommended_workers, 3)
        self.assertIn("parallel", reasoning.why_this_workforce.lower())
        self.assertIn("serializing", reasoning.why_not_fewer.lower())

    def test_plan_focused_for_high_risk_cross_subsystem(self):
        """High risk cross-subsystem tasks evaluate to FOCUSED with independent verifier."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="REFACTOR",
            risk_tier="HIGH",
            pre_planning_decision=GateDecision.SOLO_AUTHORIZED,
            execution_decision=GateDecision.SOLO_AUTHORIZED,
            write_policy=WriteSafetyPolicy.CONTROLLED_SINGLE_WRITER,
            subsystem_count=2,
            file_count=5,
            has_disjoint_boundaries=False,
            remaining_mission_budget=18,
        )
        self.assertEqual(mode, WorkforceMode.FOCUSED)
        self.assertEqual(reasoning.mode, WorkforceMode.FOCUSED)
        self.assertIn("high risk", reasoning.why_this_workforce.lower())
        self.assertIn("maker-checker", reasoning.why_not_fewer.lower())

    def test_plan_exhausted_budget_forces_solo_fallback(self):
        """Remaining budget <= 2 forces SOLO to prevent mission abort."""
        mode, reasoning = AdaptiveWorkforcePlanner.plan(
            task_class="FEATURE",
            risk_tier="HIGH",
            pre_planning_decision=GateDecision.DELEGATION_MANDATORY,
            execution_decision=GateDecision.DELEGATION_MANDATORY,
            write_policy=WriteSafetyPolicy.SAFELY_PARALLELIZABLE,
            subsystem_count=4,
            file_count=8,
            has_disjoint_boundaries=True,
            remaining_mission_budget=2,  # Constrained!
        )
        self.assertEqual(mode, WorkforceMode.SOLO)
        self.assertEqual(reasoning.max_recommended_workers, 1)
        self.assertIn("budget", reasoning.why_this_workforce.lower())
        self.assertIn("forbids", reasoning.why_not_more.lower())

    def test_cost_reasoning_format_token_bounded(self):
        """Token-bounded formatting strictly respects line limit <= 12 lines."""
        reasoning = WorkforceCostReasoning(
            why_this_workforce="Disjoint worker boundaries allow concurrent execution.",
            why_not_fewer="Serializing independent streams causes unnecessary delay.",
            why_not_more="Concurrency capped at 4 to control coordination overhead.",
            max_recommended_workers=4,
            mode=WorkforceMode.PARALLEL,
            coordination_cost_tokens=2000,
            write_collision_risk="LOW",
        )
        card = reasoning.format_token_bounded(max_lines=12)
        lines = card.splitlines()
        self.assertLessEqual(len(lines), 12)
        self.assertIn("WORKFORCE COST REASONING", card)
        self.assertIn("PARALLEL", card)
        self.assertIn("Why This:", card)
        self.assertIn("Why Not Fewer:", card)
        self.assertIn("Why Not More:", card)

    def test_dual_dispatch_gates_contain_cost_reasoning(self):
        """Pre-planning and execution gates both attach WorkforceCostReasoning."""
        pre_gate = DualDispatchGates.evaluate_pre_planning(
            domain_count=3,
            independent_lanes=3,
            file_count=3,
        )
        self.assertIsNotNone(pre_gate.cost_reasoning)
        self.assertGreaterEqual(pre_gate.cost_reasoning.recommended_workers, 2)
        self.assertIn("domain", pre_gate.cost_reasoning.why_this_workforce)

        exec_gate = DualDispatchGates.evaluate_execution_dispatch(
            workstream_count=3,
            independent_streams=3,
            file_ownership_disjoint=True,
        )
        self.assertIsNotNone(exec_gate.cost_reasoning)
        self.assertEqual(exec_gate.cost_reasoning.selected_mode, WorkforceMode.PARALLEL)
        self.assertIn("independent", exec_gate.cost_reasoning.why_this_workforce)


if __name__ == "__main__":
    unittest.main()
