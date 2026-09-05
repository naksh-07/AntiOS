"""Tests for Phase 73 Agent-Native Score Engine."""

import os
from pathlib import Path
import tempfile
import unittest

from framework.core.agent_native_score import (
    AgentNativeScoreCard,
    AgentNativeScoreEngine,
    ConfidenceLevel,
    EpistemicDimensionState,
    ScoreDimension,
)


class TestAgentNativeScore(unittest.TestCase):
    """Test suite for AgentNativeScoreEngine."""

    def test_deterministic_scoring_reproducibility(self):
        """Evaluating the same repository twice produces identical scores."""
        score1 = AgentNativeScoreEngine.evaluate_repository(".")
        score2 = AgentNativeScoreEngine.evaluate_repository(".")

        self.assertEqual(score1.overall_score, score2.overall_score)
        self.assertEqual(score1.confidence, score2.confidence)
        for dim, ds1 in score1.dimension_scores.items():
            ds2 = score2.dimension_scores[dim]
            self.assertEqual(ds1.score, ds2.score)
            self.assertEqual(ds1.epistemic_state, ds2.epistemic_state)

    def test_ten_dimensions_evaluated(self):
        """All 10 canonical dimensions must be evaluated."""
        score = AgentNativeScoreEngine.evaluate_repository(".")
        self.assertEqual(len(score.dimension_scores), 10)
        expected_dims = {d.value for d in ScoreDimension}
        self.assertEqual(set(score.dimension_scores.keys()), expected_dims)

    def test_evidence_backed_scores(self):
        """Every dimension score must contain observable evidence or explicit unknowns."""
        score = AgentNativeScoreEngine.evaluate_repository(".")
        for dim_name, ds in score.dimension_scores.items():
            has_evidence = len(ds.evidence) > 0
            has_unknowns = len(ds.unknowns) > 0
            self.assertTrue(
                has_evidence or has_unknowns,
                f"Dimension {dim_name} has neither evidence nor unknowns.",
            )

    def test_unknown_handling_does_not_zero_out(self):
        """Empty temporary repository assigns UNKNOWN status with baseline neutral scores, never 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            score = AgentNativeScoreEngine.evaluate_repository(tmpdir)
            self.assertGreater(score.overall_score, 0.0)
            for dim_name, ds in score.dimension_scores.items():
                self.assertGreaterEqual(ds.score, 30.0)
                if ds.epistemic_state == EpistemicDimensionState.UNKNOWN:
                    self.assertTrue(len(ds.unknowns) > 0)

    def test_summary_card_formatting(self):
        """Card summary renders required human-readable breakdown."""
        score = AgentNativeScoreEngine.evaluate_repository(".")
        card = score.to_summary_card()
        self.assertIn("AGENT-NATIVE REPOSITORY SCORE CARD", card)
        self.assertIn("DIMENSION BREAKDOWN:", card)
        self.assertIn("WAYFINDING", card)
        self.assertIn("VERIFICATION", card)


if __name__ == "__main__":
    unittest.main()
