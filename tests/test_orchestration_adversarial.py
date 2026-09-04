"""Adversarial and boundary stress tests for AntiOS 2.0 Orchestration Engine."""

import unittest

from framework.core.orchestration import (
    MissionLedger,
    OrchestrationBudgetExceeded,
    StructuredHandoff,
    WaveManager,
    WaveState,
    WriteSafetyEvaluator,
    WriteSafetyPolicy,
)


class TestOrchestrationAdversarial(unittest.TestCase):
    def setUp(self):
        self.ledger = MissionLedger(max_active_per_wave=10, max_total_spawned=20, max_depth=2)

    def test_adversarial_11_active_workers_strictly_blocked(self):
        """Vector 1: Attempting to spawn 11 active workers concurrently in a single wave."""
        for i in range(10):
            self.ledger.record_spawn(f"worker-{i}", role="worker", depth=1, wave_number=1)
        self.assertEqual(self.ledger.active_total, 10)

        # 11th concurrent worker MUST raise OrchestrationBudgetExceeded
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            self.ledger.record_spawn("worker-overflow", role="worker", depth=1, wave_number=1)
        self.assertIn("Wave concurrency limit reached", str(ctx.exception))
        self.assertEqual(self.ledger.active_total, 10)

    def test_adversarial_21_total_launches_strictly_blocked(self):
        """Vector 2: Attempting 21 lifetime launches across multiple collapsed waves."""
        # 2 waves of 10 workers, properly terminated
        for w in (1, 2):
            for i in range(10):
                aid = f"w{w}-{i}"
                self.ledger.record_spawn(aid, role="worker", depth=1, wave_number=w)
            for i in range(10):
                aid = f"w{w}-{i}"
                self.ledger.record_termination(aid)

        self.assertEqual(self.ledger.spawned_total, 20)
        self.assertEqual(self.ledger.active_total, 0)
        self.assertEqual(self.ledger.remaining_budget, 0)

        # 21st launch anywhere in mission MUST raise OrchestrationBudgetExceeded
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            self.ledger.record_spawn("worker-21", role="worker", depth=1, wave_number=3)
        self.assertIn("Constitutional ceiling reached", str(ctx.exception))

    def test_adversarial_depth_greater_than_2_strictly_blocked(self):
        """Vector 3: Attempting deep delegation hierarchy exceeding Shallow Depth Law (depth <= 2)."""
        # Depth 1: OK
        self.ledger.record_spawn("c1", role="coordinator", depth=1, wave_number=1, is_coordinator=True)
        self.ledger.reserve_capacity("c1", quota=2)
        # Depth 2: OK
        self.ledger.record_spawn("c2", role="specialist", depth=2, wave_number=1, parent_id="c1")

        # Depth 3: BLOCKED!
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            self.ledger.record_spawn("rogue-depth-3", role="rogue", depth=3, wave_number=1, parent_id="c2")
        self.assertIn("Shallow Depth Law violation", str(ctx.exception))

        # Depth 4: BLOCKED!
        with self.assertRaises(OrchestrationBudgetExceeded) as ctx:
            self.ledger.record_spawn("rogue-depth-4", role="rogue", depth=4, wave_number=1)
        self.assertIn("Shallow Depth Law violation", str(ctx.exception))

    def test_adversarial_uncollapsed_workers_block_next_wave(self):
        """Vector 4: Attempting to advance wave while uncollapsed active workers remain."""
        wm = WaveManager(ledger=self.ledger)
        wm.start_wave("WAVE_1")
        wm.spawn_worker("w1", role="explorer", depth=1)

        # Worker w1 is still active
        self.assertEqual(self.ledger.active_total, 1)

        # Advancing to WAVE_2 without collapse MUST fail
        with self.assertRaises(RuntimeError) as ctx:
            wm.start_wave("WAVE_2")
        self.assertIn("uncollapsed active workers", str(ctx.exception))

        # Also direct ledger check
        can_advance, reason = self.ledger.can_enter_next_wave(previous_wave_collapsed=False)
        self.assertFalse(can_advance)
        self.assertIn("Previous wave has not been collapsed", reason)

    def test_adversarial_ungrounded_handoffs_strictly_rejected(self):
        """Vector 5: Attempting to submit empty, ungrounded, or fake handoffs."""
        # Missing objective
        h_no_obj = StructuredHandoff(
            objective="",
            conclusion="Done",
            verification_method="pytest",
            evidence=["file.py:10"],
        )
        valid, errs = h_no_obj.validate()
        self.assertFalse(valid)
        self.assertIn("missing required objective", errs[0].lower())

        # Missing evidence
        h_no_ev = StructuredHandoff(
            objective="Inspect bug",
            conclusion="Fixed it in my head",
            verification_method="none",
            evidence=[],
        )
        valid, errs = h_no_ev.validate()
        self.assertFalse(valid)
        self.assertTrue(any("evidence" in e.lower() for e in errs))

        # Ungrounded evidence (no file paths, line numbers, diffs, or commands)
        h_hallucinated = StructuredHandoff(
            objective="Inspect bug",
            conclusion="Code is definitely working now",
            verification_method="tested manually",
            evidence=["it works because I checked the algorithm thoroughly"],
        )
        valid, errs = h_hallucinated.validate()
        self.assertFalse(valid)
        self.assertTrue(any("lacks grounding" in e.lower() for e in errs))

        # Valid grounded evidence
        h_grounded = StructuredHandoff(
            objective="Inspect bug",
            conclusion="Fixed null pointer exception",
            verification_method="python -m unittest tests/test_parser.py",
            evidence=["framework/core/dispatch.py:45", "exit code 0"],
        )
        valid, errs = h_grounded.validate()
        self.assertTrue(valid)
        self.assertEqual(len(errs), 0)

    def test_adversarial_overlapping_writes_rejected(self):
        """Vector 6: Attempting to parallelize writes on overlapping file paths."""
        policy, reason = WriteSafetyEvaluator.evaluate(
            target_files=["src/core.py", "src/auth.py", "src/utils.py"],
            worker_file_assignments={
                "worker-alpha": ["src/core.py", "src/utils.py"],
                "worker-beta": ["src/auth.py", "src/utils.py"],  # Overlap on src/utils.py!
            },
        )
        self.assertEqual(policy, WriteSafetyPolicy.UNSAFE_TO_PARALLELIZE)
        self.assertIn("Overlapping writers detected", reason)
        self.assertIn("src/utils.py", reason)

    def test_adversarial_coordinator_quota_spoofing_and_limits(self):
        """Vector 7: Coordinator attempts to reserve excessive quota or bypass reservation."""
        # 1. Quota > 4 blocked
        ok, msg = self.ledger.reserve_capacity("coord-bad", quota=5)
        self.assertFalse(ok)
        self.assertIn("cannot exceed 4", msg)

        # 2. Quota <= 0 blocked
        ok, msg = self.ledger.reserve_capacity("coord-bad", quota=0)
        self.assertFalse(ok)
        self.assertIn("greater than zero", msg)

        # 3. Reserve valid quota of 3
        ok, msg = self.ledger.reserve_capacity("coord-1", quota=3)
        self.assertTrue(ok)

        # 4. Another coordinator attempts to reserve more than unreserved budget
        # remaining is 20 - 3 (reserved) = 17, but quota limit is 4
        ok, msg = self.ledger.reserve_capacity("coord-2", quota=4)
        self.assertTrue(ok)
        # Total reserved = 7. Unreserved = 20 - 7 = 13.
        # Coordinator attempts to spawn without reservation
        can_del, reason = self.ledger.can_delegate("unregistered-coordinator")
        self.assertFalse(can_del)
        self.assertIn("Unknown coordinator", reason)


if __name__ == "__main__":
    unittest.main()
