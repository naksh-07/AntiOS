"""AntiOS 3.0 Tests: Hierarchical Merkle Tree Engine & Bubble-Up Performance.

Constitutional Invariants:
- INV-09: Exact cryptographic Merkle state only (zero vector embeddings).
- INV-11: Zero third-party dependencies (unittest + stdlib).
- INV-15: Zero background daemons; purely synchronous recalculation.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import unittest

from framework.intelligence.merkle import MerkleNode, MerkleTree


class TestMerklePerformance(unittest.TestCase):
    """Verifies sub-millisecond bubble-up recalculation and cryptographic correctness."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_test_merkle_")
        # Build directory hierarchy:
        # a/b/file1.py
        # a/b/file2.py
        # a/c/file3.py
        # d/file4.py
        os.makedirs(os.path.join(self.test_dir, "a", "b"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "a", "c"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "d"), exist_ok=True)

        with open(os.path.join(self.test_dir, "a", "b", "file1.py"), "w") as f:
            f.write("def foo(): return 1\n")
        with open(os.path.join(self.test_dir, "a", "b", "file2.py"), "w") as f:
            f.write("def bar(): return 2\n")
        with open(os.path.join(self.test_dir, "a", "c", "file3.py"), "w") as f:
            f.write("def baz(): return 3\n")
        with open(os.path.join(self.test_dir, "d", "file4.py"), "w") as f:
            f.write("def qux(): return 4\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_tree_build(self):
        """Full build computes deterministic SHA-256 root hash."""
        tree = MerkleTree(self.test_dir)
        root_hash, build_ms = tree.build()
        self.assertIsInstance(root_hash, str)
        self.assertEqual(len(root_hash), 64)
        self.assertGreater(len(tree.root_node.children), 0)

        # Idempotency
        tree2 = MerkleTree(self.test_dir)
        root_hash2, _ = tree2.build()
        self.assertEqual(root_hash, root_hash2)

    def test_sub_millisecond_bubble_up_performance(self):
        """Single-file incremental bubble-up update executes in < 0.1 ms (100 µs)."""
        tree = MerkleTree(self.test_dir)
        tree.build()

        # Warm-up call
        tree.update_file("a/b/file1.py", content=b"def foo(): return 10\n")

        # Measure 100 iterations of in-memory update
        durations = []
        for i in range(100):
            new_content = f"def foo(): return {i}\n".encode("utf-8")
            _, dt_ms = tree.update_file("a/b/file1.py", content=new_content)
            durations.append(dt_ms)

        avg_duration_ms = sum(durations) / len(durations)
        # Average must be well under 0.1 ms (100 microseconds)
        self.assertLess(avg_duration_ms, 0.10, f"Expected < 0.1ms bubble up, got {avg_duration_ms:.4f}ms")

    def test_bubble_up_hash_propagation(self):
        """Verifies that updating a leaf changes root and ancestors, but leaves siblings intact."""
        tree = MerkleTree(self.test_dir)
        initial_root_hash, _ = tree.build()

        node_d_hash_before = tree.root_node.children["d"].node_hash
        node_ac_hash_before = tree.root_node.children["a"].children["c"].node_hash

        # Update a file in a/b
        new_root_hash, _ = tree.update_file("a/b/file1.py", content=b"modified content")

        self.assertNotEqual(initial_root_hash, new_root_hash)
        # Sibling subtree 'd' must NOT change
        self.assertEqual(tree.root_node.children["d"].node_hash, node_d_hash_before)
        # Sibling branch 'a/c' must NOT change
        self.assertEqual(tree.root_node.children["a"].children["c"].node_hash, node_ac_hash_before)

    def test_file_deletion(self):
        """Deleting a file incrementally removes it from the tree and updates root."""
        tree = MerkleTree(self.test_dir)
        initial_hash, _ = tree.build()

        new_hash, _ = tree.update_file("d/file4.py", is_deleted=True)
        self.assertNotEqual(initial_hash, new_hash)
        self.assertNotIn("file4.py", tree.root_node.children["d"].file_hashes)

    def test_batch_update(self):
        """Batch update successfully recalculates multiple dirty files."""
        tree = MerkleTree(self.test_dir)
        initial_hash, _ = tree.build()

        # Update files on disk
        with open(os.path.join(self.test_dir, "a", "b", "file1.py"), "w") as f:
            f.write("batch edit 1\n")
        with open(os.path.join(self.test_dir, "d", "file4.py"), "w") as f:
            f.write("batch edit 2\n")

        new_hash, dt_ms = tree.update_batch(["a/b/file1.py", "d/file4.py"])
        self.assertNotEqual(initial_hash, new_hash)

    def test_serialization_and_recovery(self):
        """Tests JSON save, load, and safe recovery from corruption."""
        tree = MerkleTree(self.test_dir)
        orig_hash, _ = tree.build()

        cache_file = os.path.join(self.test_dir, ".agents", "cache", "merkle_tree.json")
        saved = tree.save(cache_file)
        self.assertTrue(saved)
        self.assertTrue(os.path.isfile(cache_file))

        # Load from disk
        loaded_tree = MerkleTree.load(self.test_dir, cache_file_path=cache_file)
        self.assertIsNotNone(loaded_tree)
        self.assertEqual(loaded_tree.root_hash, orig_hash)

        # Corrupt cache file
        with open(cache_file, "w") as f:
            f.write("INVALID JSON TRUNCATED {")

        reloaded = MerkleTree.load(self.test_dir, cache_file_path=cache_file)
        self.assertIsNone(reloaded, "Corrupted cache must return None to trigger clean rebuild")


if __name__ == "__main__":
    unittest.main()
