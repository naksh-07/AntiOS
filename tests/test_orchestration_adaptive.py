"""Unit tests for AntiOS 2.0 Adaptive Native Orchestration Engine."""

import unittest

from framework.core.orchestration import (
    AgentRecord,
    CoordinationLevel,
    DispatchGateResult,
    DispatchGateType,
    DualDispatchGates,
    GateDecision,
    MissionLedger,
    OrchestrationBudget,
    OrchestrationBudgetExceeded,
    StructuredHandoff,
    Wave,
    WaveManager,
    WaveState,
    WorkforceMode,
    WorkforceSizer,
    WriteSafetyEvaluator,
    WriteSafetyPolicy,
    determine_coordination_level,
)


class TestAdaptiveOrchestration(unittest.TestCase):
    def test_pre_planning_gate_solo_vs_delegation(self):
        # Case 1: Simple narrow task -> SOLO
        gate_solo = DualDispatchGates.evaluate_pre_planning(
            domain_count=1,
            independent_lanes=1,
            file_count=1,
            module_count=1,
        )
        self.assertEqual(gate_solo.decision, GateDecision.SOLO_AUTHORIZED)
        self.assertEqual(gate_solo.mode, WorkforceMode.SOLO)
        self.assertEqual(gate_solo.recommended_workers, 0)

        # Case 2: 3 distinct problem domains -> PARALLEL
        gate_multi_domain = DualDispatchGates.evaluate_pre_planning(
            domain_count=3,
            independent_lanes=1,
        )
        self.assertEqual(gate_multi_domain.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_multi_domain.mode, WorkforceMode.PARALLEL)
        self.assertGreaterEqual(gate_multi_domain.recommended_workers, 2)

        # Case 3: 2 independent lanes -> SMALL
        gate_lanes = DualDispatchGates.evaluate_pre_planning(
            domain_count=1,
            independent_lanes=2,
        )
        self.assertEqual(gate_lanes.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_lanes.mode, WorkforceMode.SMALL)
        self.assertEqual(gate_lanes.recommended_workers, 2)

        # Case 4: 5+ files across 2+ modules -> FOCUSED or SMALL
        gate_files = DualDispatchGates.evaluate_pre_planning(
            file_count=6,
            module_count=2,
            independent_lanes=1,
        )
        self.assertEqual(gate_files.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_files.mode, WorkforceMode.FOCUSED)

        # Case 5: Explicit user delegation request
        gate_explicit = DualDispatchGates.evaluate_pre_planning(
            explicit_delegation_request=True,
        )
        self.assertEqual(gate_explicit.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_explicit.mode, WorkforceMode.PARALLEL)

    def test_execution_dispatch_gate_policies(self):
        # Case 1: Tightly coupled changes -> Single Writer
        gate_coupled = DualDispatchGates.evaluate_execution_dispatch(
            workstream_count=2,
            independent_streams=2,
            is_tightly_coupled=True,
        )
        self.assertEqual(gate_coupled.decision, GateDecision.SOLO_AUTHORIZED)
        self.assertEqual(gate_coupled.mode, WorkforceMode.FOCUSED)
        self.assertEqual(gate_coupled.recommended_workers, 1)

        # Case 2: 2 independent implementation streams -> SMALL mandatory
        gate_small = DualDispatchGates.evaluate_execution_dispatch(
            independent_streams=2,
            is_tightly_coupled=False,
        )
        self.assertEqual(gate_small.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_small.mode, WorkforceMode.SMALL)
        self.assertEqual(gate_small.recommended_workers, 2)

        # Case 3: 4 independent streams -> PARALLEL up to 4
        gate_parallel = DualDispatchGates.evaluate_execution_dispatch(
            independent_streams=4,
            is_tightly_coupled=False,
        )
        self.assertEqual(gate_parallel.decision, GateDecision.DELEGATION_MANDATORY)
        self.assertEqual(gate_parallel.mode, WorkforceMode.PARALLEL)
        self.assertEqual(gate_parallel.recommended_workers, 4)

        # Case 4: Budget exhausted -> BLOCKED
        gate_blocked = DualDispatchGates.evaluate_execution_dispatch(
            remaining_budget=0,
        )
        self.assertEqual(gate_blocked.decision, GateDecision.BLOCKED)
        self.assertEqual(gate_blocked.recommended_workers, 0)

    def test_workforce_sizer_and_coordination_levels(self):
        # Documentation + Low Risk -> SOLO
        gate_pre = DualDispatchGates.evaluate_pre_planning()
        mode = WorkforceSizer.select_mode("DOCUMENTATION", "LOW", gate_pre)
        self.assertEqual(mode, WorkforceMode.SOLO)
        self.assertEqual(determine_coordination_level(mode, wave_count=1), CoordinationLevel.L0)

        # Focused / Small -> L1
        self.assertEqual(determine_coordination_level(WorkforceMode.FOCUSED, wave_count=1), CoordinationLevel.L1)
        self.assertEqual(determine_coordination_level(WorkforceMode.SMALL, wave_count=2), CoordinationLevel.L1)

        # Parallel / Staged -> L2
        self.assertEqual(determine_coordination_level(WorkforceMode.PARALLEL, wave_count=1), CoordinationLevel.L2)
        self.assertEqual(determine_coordination_level(WorkforceMode.STAGED, wave_count=3), CoordinationLevel.L2)

        # Hierarchical / Max -> L3
        self.assertEqual(determine_coordination_level(WorkforceMode.HIERARCHICAL, wave_count=1), CoordinationLevel.L3)
        self.assertEqual(determine_coordination_level(WorkforceMode.MAX, wave_count=1), CoordinationLevel.L3)

    def test_coordinator_quota_reservation_and_reversion(self):
        ledger = MissionLedger(max_total_spawned=20, max_active_per_wave=10)

        # Spawn coordinator agent at depth 1
        coord_rec = ledger.record_spawn("coord-1", role="coordinator", depth=1, wave_number=1, is_coordinator=True)
        self.assertTrue(coord_rec.is_coordinator)
        self.assertEqual(ledger.remaining_budget, 19)

        # Attempt to reserve invalid quota (> 4)
        ok, msg = ledger.reserve_capacity("coord-1", quota=5)
        self.assertFalse(ok)
        self.assertIn("cannot exceed 4", msg)

        # Reserve valid quota of 2
        ok, msg = ledger.reserve_capacity("coord-1", quota=2)
        self.assertTrue(ok)
        self.assertEqual(ledger.reserved_capacity["coord-1"], 2)

        # Coordinator spawns child 1
        c1 = ledger.record_spawn("child-1", role="specialist", depth=2, wave_number=1, parent_id="coord-1")
        self.assertEqual(coord_rec.actually_spawned, 1)

        # Coordinator spawns child 2
        c2 = ledger.record_spawn("child-2", role="specialist", depth=2, wave_number=1, parent_id="coord-1")
        self.assertEqual(coord_rec.actually_spawned, 2)

        # Coordinator attempts to spawn child 3 -> Exceeds reserved quota!
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            ledger.record_spawn("child-3", role="specialist", depth=2, wave_number=1, parent_id="coord-1")
        self.assertIn("exceeded reserved child quota", str(ctx.exception))

        # Terminate child 1 & child 2
        ledger.record_termination("child-1")
        ledger.record_termination("child-2")
        self.assertEqual(ledger.active_total, 1)  # Only coord-1 active

        # Releasing capacity should return 0 unused since 2 of 2 were used
        unused = ledger.release_capacity("coord-1")
        self.assertEqual(unused, 0)
        self.assertNotIn("coord-1", ledger.reserved_capacity)

    def test_write_safety_evaluator_disjoint_and_conflicts(self):
        # Case 1: Read only
        policy, reason = WriteSafetyEvaluator.evaluate([], is_read_only=True)
        self.assertEqual(policy, WriteSafetyPolicy.READ_ONLY)

        # Case 2: Single writer
        policy, reason = WriteSafetyEvaluator.evaluate(
            ["src/a.py", "src/b.py"],
            worker_file_assignments={"worker-1": ["src/a.py", "src/b.py"]},
        )
        self.assertEqual(policy, WriteSafetyPolicy.CONTROLLED_SINGLE_WRITER)

        # Case 3: Disjoint writes -> SAFELY_PARALLELIZABLE
        policy, reason = WriteSafetyEvaluator.evaluate(
            ["src/a.py", "src/b.py"],
            worker_file_assignments={
                "worker-1": ["src/a.py"],
                "worker-2": ["src/b.py"],
            },
        )
        self.assertEqual(policy, WriteSafetyPolicy.SAFELY_PARALLELIZABLE)

        # Case 4: Overlapping writes -> UNSAFE_TO_PARALLELIZE
        policy, reason = WriteSafetyEvaluator.evaluate(
            ["src/a.py", "src/shared.py"],
            worker_file_assignments={
                "worker-1": ["src/a.py", "src/shared.py"],
                "worker-2": ["src/shared.py"],
            },
        )
        self.assertEqual(policy, WriteSafetyPolicy.UNSAFE_TO_PARALLELIZE)
        self.assertIn("Overlapping writers detected", reason)

    def test_wave_progression_and_collapse_lifecycle(self):
        wm = WaveManager()
        
        # Wave 1: Discovery
        w1 = wm.start_wave("RECONNAISSANCE")
        self.assertEqual(w1.wave_number, 1)
        self.assertEqual(w1.state, WaveState.ACTIVE)

        wm.spawn_worker("w1-a", role="explorer", depth=1)
        wm.spawn_worker("w1-b", role="explorer", depth=1)
        self.assertEqual(wm.ledger.active_total, 2)

        # Advancing to Wave 2 while Wave 1 workers active must fail
        with self.assertRaises(RuntimeError):
            wm.start_wave("IMPLEMENTATION")

        # Collapse Wave 1
        collapsed = wm.collapse_wave()
        self.assertEqual(collapsed, 2)
        self.assertEqual(wm.ledger.active_total, 0)
        self.assertEqual(w1.state, WaveState.COLLAPSED)

        # Wave 2: Implementation can now start
        w2 = wm.start_wave("IMPLEMENTATION")
        self.assertEqual(w2.wave_number, 2)
        self.assertEqual(w2.state, WaveState.ACTIVE)


if __name__ == "__main__":
    unittest.main()
