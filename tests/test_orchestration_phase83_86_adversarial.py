#!/usr/bin/env python3
"""Adversarial security and constitutional boundary tests for AntiOS Phases 83-86.

Covers 10 critical attack vectors:
  1. Recursive spawning attack (depth > 2 or leaf delegation)
  2. Budget exhaustion attack (> 20 lifetime launches)
  3. Wave concurrency limit attack (> 10 active agents in wave)
  4. Duplicate specialist attack (same role & goal in same wave)
  5. Runaway failure retry loop attack (>= 2 failures)
  6. Overlapping write boundary collision attack
  7. Anonymous worker spawn attack (invalid WorkerMetadata)
  8. AntiOS usurping native Antigravity primitives attack
  9. Unjustified or incomplete MCP escalation report attack
 10. Wave advance without collapsing active workers attack
"""

import unittest
from framework.core.orchestration import (
    MissionLedger,
    WaveManager,
    WorkerMetadata,
    OrchestrationBudgetExceeded,
)
from framework.core.workforce_contract import (
    WorkforceContract,
    ResponsibilityAllocation,
    ResponsibilityDomain,
)
from framework.core.tool_policy import (
    HybridCapabilityExecutionMatrix,
    MCPJustificationReport,
)


class TestOrchestrationPhase83To86Adversarial(unittest.TestCase):
    """Adversarial test suite enforcing strict constitutional limits and safety boundaries."""

    def setUp(self):
        self.ledger = MissionLedger(mission_id="adv-mission-01")
        self.wave_mgr = WaveManager(ledger=self.ledger)

    def _make_meta(self, suffix: str, write_boundary=None, goal="execute task") -> WorkerMetadata:
        return WorkerMetadata(
            mission_id="adv-mission-01",
            wave_id=1,
            parent_id=None,
            capability=f"cap-{suffix}",
            purpose=goal,
            goal=goal,
            write_boundary=write_boundary or [f"src/{suffix}.py"],
            risk_tier="LOW",
            expected_output=f"Output for {suffix}",
            verification_requirement=f"Verify {suffix}",
        )

    def test_vector_1_recursive_spawning_attack(self):
        """Attack Vector 1: Attempt to spawn beyond depth 2 or delegate from leaf worker."""
        # 1a. Attempt to spawn at depth 3 directly
        can_spawn, reason = self.ledger.can_spawn(depth=3)
        self.assertFalse(can_spawn)
        self.assertIn("Shallow Depth Law violation", reason)

        # 1b. Spawn root at depth 1, child at depth 2
        self.ledger.record_spawn(
            agent_id="root-1",
            role="coordinator",
            depth=1,
            wave_number=1,
            metadata=self._make_meta("root"),
        )
        self.ledger.record_spawn(
            agent_id="child-1",
            role="leaf-worker",
            depth=2,
            wave_number=1,
            parent_id="root-1",
            metadata=self._make_meta("child"),
        )

        # 1c. Leaf worker at depth 2 attempts to delegate (even if requesting depth 2)
        can_leaf_spawn, leaf_reason = self.ledger.can_spawn(
            depth=2,
            parent_id="child-1",
            metadata=self._make_meta("leaf-child"),
        )
        self.assertFalse(can_leaf_spawn)
        self.assertIn("leaf worker 'child-1' at depth 2 cannot delegate", leaf_reason)

    def test_vector_2_budget_exhaustion_attack(self):
        """Attack Vector 2: Attempt to exceed constitutional lifetime launch ceiling of 20."""
        # Spawn up to max 20 agents (terminating them to avoid wave concurrency limit)
        for i in range(20):
            aid = f"agent-{i+1}"
            meta = self._make_meta(f"worker-{i+1}", write_boundary=[f"src/file_{i}.py"], goal=f"subtask {i+1}")
            self.ledger.record_spawn(agent_id=aid, role=f"worker-{i+1}", depth=1, wave_number=1, metadata=meta)
            self.ledger.record_termination(aid)

        self.assertEqual(self.ledger.spawned_total, 20)
        self.assertEqual(self.ledger.remaining_budget, 0)

        # Attempt 21st launch
        meta_21 = self._make_meta("worker-21", goal="subtask 21")
        can_spawn, reason = self.ledger.can_spawn(depth=1, metadata=meta_21)
        self.assertFalse(can_spawn)
        self.assertIn("Constitutional ceiling reached", reason)

        with self.assertRaises(OrchestrationBudgetExceeded):
            self.ledger.record_spawn(agent_id="agent-21", role="worker-21", depth=1, wave_number=1, metadata=meta_21)

    def test_vector_3_wave_concurrency_limit_attack(self):
        """Attack Vector 3: Attempt to exceed wave concurrency limit of 10 active agents."""
        for i in range(10):
            aid = f"active-agent-{i+1}"
            meta = self._make_meta(f"worker-{i+1}", write_boundary=[f"src/unique_{i}.py"], goal=f"task {i+1}")
            self.ledger.record_spawn(agent_id=aid, role=f"worker-{i+1}", depth=1, wave_number=1, metadata=meta)

        self.assertEqual(self.ledger.active_total, 10)
        self.assertEqual(self.ledger.available_active_slots, 0)

        # Attempt 11th active launch
        meta_11 = self._make_meta("worker-11", write_boundary=["src/unique_11.py"], goal="task 11")
        can_spawn, reason = self.ledger.can_spawn(depth=1, metadata=meta_11)
        self.assertFalse(can_spawn)
        self.assertIn("Wave concurrency limit reached", reason)

        with self.assertRaises(OrchestrationBudgetExceeded):
            self.ledger.record_spawn(agent_id="active-agent-11", role="worker-11", depth=1, wave_number=1, metadata=meta_11)

    def test_vector_4_duplicate_specialist_same_wave_attack(self):
        """Attack Vector 4: Attempt to spawn duplicate active specialist with identical goal in wave."""
        meta_spec_1 = self._make_meta("spec-1", goal="research auth architecture")
        self.ledger.record_spawn(
            agent_id="researcher-1",
            role="researcher",
            depth=1,
            wave_number=1,
            metadata=meta_spec_1,
        )

        # Duplicate researcher with identical goal in wave 1
        meta_spec_2 = self._make_meta("spec-2", goal="research auth architecture")
        can_spawn, reason = self.ledger.can_spawn(
            role="researcher",
            wave_number=1,
            metadata=meta_spec_2,
        )
        self.assertFalse(can_spawn)
        self.assertIn("Duplicate active specialist 'researcher' with identical goal", reason)

    def test_vector_5_runaway_failure_retry_loop_attack(self):
        """Attack Vector 5: Attempt runaway retry loop after 2 consecutive failures for same role."""
        # 1st failure
        self.ledger.record_spawn(
            agent_id="failing-1",
            role="flaky-worker",
            depth=1,
            wave_number=1,
            metadata=self._make_meta("flaky-1"),
        )
        self.ledger.record_failure("failing-1", reason="SyntaxError")

        # 2nd failure
        self.ledger.record_spawn(
            agent_id="failing-2",
            role="flaky-worker",
            depth=1,
            wave_number=1,
            metadata=self._make_meta("flaky-2"),
        )
        self.ledger.record_failure("failing-2", reason="ImportError")

        # 3rd spawn attempt for flaky-worker should be blocked (ceiling is 2 retries)
        can_spawn, reason = self.ledger.can_spawn(
            role="flaky-worker",
            wave_number=1,
            metadata=self._make_meta("flaky-3"),
        )
        self.assertFalse(can_spawn)
        self.assertIn("Retry limit reached for role 'flaky-worker'", reason)
        self.assertIn("Runaway retry loop prevented", reason)

    def test_vector_6_overlapping_write_boundary_collision_attack(self):
        """Attack Vector 6: Attempt to spawn two concurrent workers with conflicting write targets."""
        meta_w1 = self._make_meta("writer-1", write_boundary=["src/core/auth.py", "src/shared.py"])
        self.ledger.record_spawn(
            agent_id="writer-1",
            role="coder",
            depth=1,
            wave_number=1,
            metadata=meta_w1,
        )

        # Second worker targeting overlapping src/shared.py
        meta_w2 = self._make_meta("writer-2", write_boundary=["src/shared.py", "src/views.py"])
        can_spawn, reason = self.ledger.can_spawn(
            role="tester",
            write_boundary=meta_w2.write_boundary,
            metadata=meta_w2,
        )
        self.assertFalse(can_spawn)
        self.assertIn("Write collision with active worker 'writer-1'", reason)

    def test_vector_7_anonymous_worker_spawn_attack(self):
        """Attack Vector 7: Attempt to spawn worker with missing or invalid WorkerMetadata."""
        invalid_meta = WorkerMetadata(
            mission_id="",  # Missing mission_id
            wave_id=1,
            parent_id=None,
            capability="",  # Missing capability
            purpose="",  # Missing purpose
            expected_output="",  # Missing expected output
            verification_requirement="",  # Missing verification
        )
        is_valid, errs = invalid_meta.validate()
        self.assertFalse(is_valid)
        self.assertGreaterEqual(len(errs), 4)

        with self.assertRaises(ValueError) as ctx:
            self.ledger.record_spawn(
                agent_id="anon-agent",
                role="anonymous",
                depth=1,
                wave_number=1,
                metadata=invalid_meta,
            )
        self.assertIn("Anti-Hydra Protection: Invalid worker metadata", str(ctx.exception))

    def test_vector_8_antios_usurping_native_antigravity_primitives_attack(self):
        """Attack Vector 8: Reject attempt by AntiOS to claim native Antigravity responsibilities."""
        # 1. Attempting to assign native Antigravity primitives to AntiOS in contract
        usurp_allocations = [
            ResponsibilityAllocation(
                responsibility="agent_execution_runtime",
                owner=ResponsibilityDomain.ANTIOS,  # Violation! Native must own
                rationale="AntiOS tries to manage agent process execution",
                anti_patterns=["AntiOS managing LLM loop"],
            )
        ]
        contract = WorkforceContract(allocations=usurp_allocations)
        is_valid, errs = contract.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any("Usurpation violation" in e for e in errs))

        # 2. Check emulation violation detection on proposed action triggers
        for trigger in ["custom_daemon", "workflow_engine", "agent_runtime", "mcp_broker", "polling_loop", "subagent_spawner"]:
            is_violation, details = contract.check_emulation_violation(f"launch {trigger} to coordinate work")
            self.assertTrue(is_violation)
            self.assertIn("Contract Violation", details)

    def test_vector_9_unjustified_or_incomplete_mcp_escalation_report_attack(self):
        """Attack Vector 9: Reject incomplete or fraudulent MCP escalation reports."""
        matrix = HybridCapabilityExecutionMatrix()

        # Incomplete report missing rollback_plan, risk_assessment, etc.
        incomplete_report = MCPJustificationReport(
            provider_id="provider:github",
            status="USEFUL",
            is_needed=True,
            is_permitted=True,
            why="Escalating without audit fields",
            local_alternatives=[],
            why_insufficient="",
            fallback="NONE",
            on_unavailable="FAIL_CLOSED",
            capability_sought="",  # Missing field 1
            why_native_failed="",  # Missing field 2
            least_privilege_scope=[],  # Missing field 3
            risk_assessment="",  # Missing field 4
            rollback_plan="",  # Missing field 5
            user_approval_required=False,
            audit_trail_entry={},  # Missing field 7
        )
        is_valid, audit_errs = incomplete_report.validate_escalation_audit()
        self.assertFalse(is_valid)
        self.assertTrue(any("capability_sought" in e for e in audit_errs))
        self.assertTrue(any("rollback_plan" in e for e in audit_errs))

    def test_vector_10_wave_advance_without_collapsing_active_workers_attack(self):
        """Attack Vector 10: Advancing wave without collapsing active workers is strictly blocked."""
        self.wave_mgr.start_wave("WAVE_1")
        self.wave_mgr.spawn_worker(
            agent_id="w1-worker",
            role="coder",
            depth=1,
            metadata=self._make_meta("w1-worker"),
        )
        self.assertEqual(self.ledger.active_total, 1)

        # Attempt to enter next wave while active_total == 1
        can_advance, reason = self.ledger.can_enter_next_wave(previous_wave_collapsed=False)
        self.assertFalse(can_advance)

        # Attempting start_wave without collapsing must raise RuntimeError
        with self.assertRaises(RuntimeError) as ctx:
            self.wave_mgr.start_wave("WAVE_2")
        self.assertIn("uncollapsed active workers", str(ctx.exception))

        # Collapse workers and verify wave advance is now allowed
        collapsed = self.ledger.collapse_all_active()
        self.assertEqual(collapsed, 1)
        self.assertEqual(self.ledger.active_total, 0)

        # Now start_wave succeeds
        wave_2 = self.wave_mgr.start_wave("WAVE_2")
        self.assertEqual(wave_2.wave_number, 2)


if __name__ == "__main__":
    unittest.main()
