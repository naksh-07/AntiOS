"""AntiOS 3.0 Tests: Epistemic Engineering Memory & Cryptographic Code Binding.

Constitutional Invariants:
- INV-09: Exact cryptographic state only (zero vector databases).
- INV-11: Zero third-party dependencies (unittest + stdlib).
- INV-13: System A / System B strict decoupling.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import unittest

from framework.intelligence.memory import (
    EpistemicGrade,
    MemoryCategory,
    MemoryRecord,
    MemoryStore,
)


class TestEpistemicMemory(unittest.TestCase):
    """Verifies epistemic memory categories, cryptographic binding, and context budgets."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_test_memory_")
        self.store = MemoryStore(self.test_dir)
        self.store.initialize_store()

        # Create target sample code file
        self.sample_file = os.path.join(self.test_dir, "framework", "sample.py")
        os.makedirs(os.path.dirname(self.sample_file), exist_ok=True)
        with open(self.sample_file, "w", encoding="utf-8") as f:
            f.write("def sample_function(): return 'v1'\n")

        with open(self.sample_file, "rb") as fp:
            self.sample_hash = hashlib.sha256(fp.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_initialization(self):
        """Verifies that all standard memory files and directories are created."""
        mem_dir = os.path.join(self.test_dir, "docs", "memory")
        self.assertTrue(os.path.isdir(os.path.join(mem_dir, "adr")))
        self.assertTrue(os.path.isdir(os.path.join(mem_dir, "rca")))
        for fname in ["dead_ends.md", "environment.md", "hazards.md", "runbooks.md", "baselines.md", "preferences.md"]:
            self.assertTrue(os.path.isfile(os.path.join(mem_dir, fname)))

    def test_target_code_binding_and_stale_evidence(self):
        """Records with mismatched SHA-256 hashes are flagged STALE_EVIDENCE and suppressed."""
        record = MemoryRecord(
            record_id="DE-099",
            category=MemoryCategory.DEAD_ENDS.value,
            title="Sample Function Modification Dead End",
            epistemic_status=EpistemicGrade.TESTED_NEGATIVE.value,
            timestamp="2026-09-08T00:00:00Z",
            target_subsystem="framework/sample",
            target_file="framework/sample.py",
            target_content_hash=self.sample_hash,
            content="Attempted to return v2, failed.",
            tags=["sample", "dead_end"],
        )

        # 1. Fresh state: hash matches
        self.assertFalse(record.is_stale(self.test_dir))
        self.assertEqual(record.get_effective_status(self.test_dir), EpistemicGrade.TESTED_NEGATIVE.value)

        # 2. Code modification: SHA-256 drifts
        with open(self.sample_file, "w", encoding="utf-8") as f:
            f.write("def sample_function(): return 'v2_drifted'\n")

        self.assertTrue(record.is_stale(self.test_dir))
        self.assertEqual(record.get_effective_status(self.test_dir), EpistemicGrade.STALE_EVIDENCE.value)

        # 3. Code deletion: target file deleted
        os.remove(self.sample_file)
        self.assertTrue(record.is_stale(self.test_dir))
        self.assertEqual(record.get_effective_status(self.test_dir), EpistemicGrade.STALE_EVIDENCE.value)

    def test_epistemic_hygiene_suppresses_hypotheses(self):
        """Working hypotheses are strictly quarantined and never returned in context queries."""
        dead_ends_path = os.path.join(self.test_dir, "docs", "memory", "dead_ends.md")
        with open(dead_ends_path, "a", encoding="utf-8") as fp:
            fp.write("""
### HYP-001: Unverified Hypothesis on Compiler
- **Status**: [WORKING_HYPOTHESIS]
- **Timestamp**: 2026-09-08T01:00:00Z
- **Target Subsystem**: `compiler`
- **Tags**: hypothesis, compiler
Some unverified conjecture that should never be injected as fact.
""")

        results = self.store.query("compiler")
        self.assertEqual(len(results), 0, "WORKING_HYPOTHESIS must be suppressed from query results")

    def test_gated_retrieval_context_budget(self):
        """Retrieval caps results to max_records <= 2 and max_tokens <= 300."""
        hazards_path = os.path.join(self.test_dir, "docs", "memory", "hazards.md")
        with open(hazards_path, "a", encoding="utf-8") as fp:
            for i in range(1, 6):
                fp.write(f"""
### HAZ-{i:03d}: Hazard {i} for Subsystem
- **Status**: [VERIFIED_FACT]
- **Timestamp**: 2026-09-08T02:00:00Z
- **Target Subsystem**: `subsystem`
- **Tags**: hazard, subsystem
Detailed hazard description number {i} with extensive text to verify budgeting constraints.
""")

        results = self.store.query("subsystem", max_records=2, max_tokens=300)
        self.assertLessEqual(len(results), 2, "Must not exceed max_records ceiling")

        total_chars = sum(len(md) for _, md in results)
        self.assertLessEqual(total_chars, 300 * 4, "Must not exceed max token character budget")

    def test_query_suppresses_stale_records(self):
        """Queries automatically omit records whose target code has drifted."""
        dead_ends_path = os.path.join(self.test_dir, "docs", "memory", "dead_ends.md")
        with open(dead_ends_path, "a", encoding="utf-8") as fp:
            fp.write(f"""
### DE-101: Stale Bound Dead End
- **Status**: [TESTED_NEGATIVE]
- **Timestamp**: 2026-09-08T03:00:00Z
- **Target Subsystem**: `framework`
- **Target File**: `framework/sample.py`
- **Target SHA-256**: `0000000000000000000000000000000000000000000000000000000000000000`
- **Tags**: stale, sample
Stale dead end referencing old code.
""")

        results = self.store.query("sample")
        self.assertEqual(len(results), 0, "Stale record must be suppressed from agent context")


if __name__ == "__main__":
    unittest.main()
