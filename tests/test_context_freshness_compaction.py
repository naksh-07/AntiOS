"""Unit and integration tests for AntiOS 2.0 Context Freshness & Safe Compaction (Phase 88)."""

import os
from pathlib import Path
import shutil
import tempfile
import unittest

from framework.core.context_freshness import (
    ContextFreshnessState,
    FreshnessEvaluation,
    FreshnessEvaluator,
    SafeContextCompactor,
)
from framework.core.learning import EpistemicSource


class TestContextFreshnessAndCompaction(unittest.TestCase):
    """Test suite verifying freshness auditing and non-destructive compaction."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "sample_module.py"
        self.test_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_source_freshness_clean(self):
        """Unmodified physical file matches SHA-256 and evaluates to FRESH."""
        sha = FreshnessEvaluator.compute_sha256(self.test_file)
        eval_res = FreshnessEvaluator.evaluate_file_source(
            source_id="sample-mod",
            file_path="sample_module.py",
            recorded_sha256=sha,
            workspace_root=self.temp_dir,
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.FRESH)
        self.assertTrue(eval_res.is_trustworthy)

    def test_file_source_freshness_stale(self):
        """Modified file exhibits hash drift and evaluates to STALE."""
        initial_sha = FreshnessEvaluator.compute_sha256(self.test_file)
        # Mutate file
        self.test_file.write_text("def hello():\n    return 'mutated'\n", encoding="utf-8")

        eval_res = FreshnessEvaluator.evaluate_file_source(
            source_id="sample-mod",
            file_path="sample_module.py",
            recorded_sha256=initial_sha,
            workspace_root=self.temp_dir,
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.STALE)
        self.assertFalse(eval_res.is_trustworthy)
        self.assertIn("File modified since context capture", eval_res.reasons[0])

    def test_missing_file_source_evaluates_to_invalid(self):
        """Non-existent file evaluates to INVALID with zero confidence."""
        eval_res = FreshnessEvaluator.evaluate_file_source(
            source_id="ghost-file",
            file_path="does_not_exist.py",
            recorded_sha256="fakehash",
            workspace_root=self.temp_dir,
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.INVALID)
        self.assertEqual(eval_res.confidence, 0.0)

    def test_project_manifest_drift_triggers_stale(self):
        """Manifest fingerprint mismatch evaluates to STALE."""
        eval_res = FreshnessEvaluator.evaluate_project_context(
            recorded_manifest_fingerprint="sha256:old_fingerprint",
            current_manifest_fingerprint="sha256:new_fingerprint",
            recorded_git_head="commit_a",
            current_git_head="commit_a",
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.STALE)
        self.assertIn("manifest fingerprint mismatch", eval_res.reasons[0])

    def test_git_head_advance_triggers_aging(self):
        """Git HEAD advancement evaluates to AGING context."""
        eval_res = FreshnessEvaluator.evaluate_project_context(
            recorded_manifest_fingerprint="sha256:same",
            current_manifest_fingerprint="sha256:same",
            recorded_git_head="commit_a",
            current_git_head="commit_b",
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.AGING)
        self.assertTrue(eval_res.is_trustworthy)

    def test_substantive_dirty_files_triggers_stale(self):
        """Uncommitted working tree mutations evaluate to STALE."""
        eval_res = FreshnessEvaluator.evaluate_project_context(
            recorded_manifest_fingerprint="sha256:same",
            current_manifest_fingerprint="sha256:same",
            recorded_git_head="commit_a",
            current_git_head="commit_a",
            substantive_dirty_files=["src/core.py"],
        )
        self.assertEqual(eval_res.state, ContextFreshnessState.STALE)

    def test_safe_compaction_preserves_facts_and_invariants(self):
        """Compactor preserves hard facts and invariants while discarding greeting fluff."""
        raw_text = """
        Hello! As an AI assistant, I am happy to help you with this task.
        Here is what you need to know about the architecture:
        # Architecture Rules
        - All tests must pass with exit code 0.
        - Immutable core zones: framework/, .agents/hooks.json.
        - Shallow depth <= 2 strictly enforced.
        - The database uses SQLite3 connection pooling.
        Certainly! Let me know if you need anything else!
        """
        compacted = SafeContextCompactor.compact(
            raw_text=raw_text,
            provenance="docs/rules.md",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
        )

        self.assertIn("# Architecture Rules", compacted)
        self.assertIn("exit code 0", compacted)
        self.assertIn("Immutable core zones:", compacted)
        self.assertIn("Shallow depth <= 2", compacted)
        self.assertIn("SQLite3 connection pooling", compacted)
        self.assertIn("docs/rules.md", compacted)

        # Fluff removed
        self.assertNotIn("Hello! As an AI assistant", compacted)
        self.assertNotIn("Certainly! Let me know", compacted)

    def test_safe_compaction_never_converts_inference_into_fact(self):
        """Inferences compacted by SafeContextCompactor retain their explicit epistemic source."""
        raw_inference = "- Agent hypothesis: The memory leak is caused by unclosed socket."
        compacted = SafeContextCompactor.compact(
            raw_text=raw_inference,
            provenance="agent-notes.md",
            epistemic_source=EpistemicSource.AGENT_INTERPRETATION,
        )

        self.assertIn("Epistemic Source: AGENT_INTERPRETATION", compacted)
        self.assertNotIn("Epistemic Source: OBSERVED_FACT", compacted)

    def test_safe_compaction_preserves_provenance(self):
        """Compaction output always includes provenance metadata."""
        compacted = SafeContextCompactor.compact(
            raw_text="- Fact: Module A depends on Module B.",
            provenance="framework/core/anatomy.py",
            epistemic_source=EpistemicSource.OBSERVED_FACT,
        )
        self.assertIn("framework/core/anatomy.py", compacted)


if __name__ == "__main__":
    unittest.main()
