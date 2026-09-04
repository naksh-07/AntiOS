"""Unit tests for AntiOS 2.0 Constitutional Orchestration Engine."""

import unittest

from framework.core.orchestration import (
    OrchestrationBudget,
    OrchestrationBudgetExceeded,
    StructuredHandoff,
    WaveManager,
    WaveState,
)


class TestOrchestrationConstitution(unittest.TestCase):
    def test_max_active_agents_per_wave_limit_ten(self):
        budget = OrchestrationBudget(max_active_per_wave=10, max_total_spawned=20)

        # Spawn 10 active agents successfully
        for i in range(10):
            budget.record_spawn(
                agent_id=f"worker-{i}",
                role="specialist",
                depth=1,
                wave_number=1,
            )

        self.assertEqual(budget.active_total, 10)
        self.assertEqual(budget.spawned_total, 10)
        self.assertEqual(budget.remaining_budget, 10)

        # Attempting to spawn 11th active agent MUST be blocked
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            budget.record_spawn(
                agent_id="worker-overflow",
                role="specialist",
                depth=1,
                wave_number=1,
            )
        self.assertIn("Wave concurrency limit reached", str(ctx.exception))

    def test_max_total_spawned_agents_limit_twenty(self):
        budget = OrchestrationBudget(max_active_per_wave=10, max_total_spawned=20)

        # Run 2 waves of 10 workers each, terminating them between waves
        for wave_idx in (1, 2):
            for i in range(10):
                aid = f"w{wave_idx}-{i}"
                budget.record_spawn(aid, role="worker", depth=1, wave_number=wave_idx)
            # Terminate all 10 workers in this wave
            for i in range(10):
                aid = f"w{wave_idx}-{i}"
                budget.record_termination(aid)
            self.assertEqual(budget.active_total, 0)

        self.assertEqual(budget.spawned_total, 20)
        self.assertEqual(budget.remaining_budget, 0)

        # Attempting 21st launch anywhere in the mission MUST be blocked
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            budget.record_spawn("worker-21", role="worker", depth=1, wave_number=3)
        self.assertIn("Constitutional ceiling reached", str(ctx.exception))

    def test_shallow_depth_law_enforced(self):
        budget = OrchestrationBudget()

        # Depth 1: OK (Root -> Direct Child)
        r1 = budget.record_spawn("child-1", role="specialist", depth=1, wave_number=1)
        self.assertEqual(r1.depth, 1)

        # Depth 2: OK (Child -> Grandchild)
        r2 = budget.record_spawn("grandchild-1", role="verifier", depth=2, wave_number=1)
        self.assertEqual(r2.depth, 2)

        # Depth 3: BLOCKED!
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            budget.record_spawn("great-grandchild", role="rogue", depth=3, wave_number=1)
        self.assertIn("Shallow Depth Law violation", str(ctx.exception))

    def test_wave_manager_enforces_mandatory_collapse_before_next_wave(self):
        manager = WaveManager()

        # Start Wave 1 (Recon)
        w1 = manager.start_wave("DISCOVER")
        manager.spawn_worker("explorer-1", role="explorer", depth=1)
        manager.spawn_worker("explorer-2", role="explorer", depth=1)

        self.assertEqual(manager.budget.active_total, 2)

        # Attempting to start Wave 2 without collapsing Wave 1 workers MUST raise error
        with self.assertRaises(RuntimeError) as ctx:
            manager.start_wave("IMPLEMENT")
        self.assertIn("uncollapsed active workers", str(ctx.exception))

        # Collapse Wave 1
        collapsed = manager.collapse_wave()
        self.assertEqual(collapsed, 2)
        self.assertEqual(manager.budget.active_total, 0)
        self.assertEqual(w1.state, WaveState.COLLAPSED)

        # Now Wave 2 can proceed cleanly!
        w2 = manager.start_wave("IMPLEMENT")
        self.assertEqual(w2.wave_number, 2)
        self.assertEqual(w2.state, WaveState.ACTIVE)

    def test_structured_handoff_recording_and_termination(self):
        manager = WaveManager()
        manager.start_wave("INVESTIGATION")
        manager.spawn_worker("inv-1", role="investigation-specialist", depth=1)

        handoff = StructuredHandoff(
            objective="Inspect memory leaks",
            observations=["Found unclosed connection in db.py:45"],
            logic_chain="Connection pool was missing close() call in finally block",
            evidence=["diff --git a/db.py b/db.py"],
            caveats=["Requires postgres runtime running"],
            conclusion="Fix applied and verified",
            verification_method="pytest tests/test_db.py",
            next_owner="primary-engineer",
        )

        manager.record_handoff("inv-1", handoff)

        # Worker should now be terminated
        self.assertEqual(manager.budget.active_total, 0)
        self.assertFalse(manager.budget.records["inv-1"].is_active)
        self.assertEqual(manager.current_wave.handoffs[0].conclusion, "Fix applied and verified")


if __name__ == "__main__":
    unittest.main()
