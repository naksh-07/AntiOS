"""AntiOS 3.0 Tests: Cryptographic Freshness & Combined Git Token Engine.

Constitutional Invariants:
- INV-09: Exact cryptographic state only.
- INV-11: Zero third-party dependencies (unittest + stdlib).
- INV-15: Zero background daemons (synchronous execution).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
import time
import unittest

from framework.intelligence.freshness import (
    compute_git_token,
    get_cache_token_path,
    read_cached_token,
    write_cached_token,
    check_freshness,
)


class TestCombinedGitToken(unittest.TestCase):
    """Verifies the Combined Git Token protocol and zero-daemon freshness detection."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="antios_test_freshness_")
        # Initialize a temporary git repository
        subprocess.run(["git", "init"], cwd=self.test_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test Agent"], cwd=self.test_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "agent@antios.dev"], cwd=self.test_dir, capture_output=True, check=True)

        # Initial commit
        self.readme_path = os.path.join(self.test_dir, "README.md")
        with open(self.readme_path, "w", encoding="utf-8") as f:
            f.write("# Test Repo\n")
        subprocess.run(["git", "add", "README.md"], cwd=self.test_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.test_dir, capture_output=True, check=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_token_computation_clean_repo(self):
        """Token computes deterministically on clean repo."""
        token, dirty_files, head_sha, dt_ms = compute_git_token(self.test_dir)
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 16)
        self.assertEqual(len(dirty_files), 0)
        self.assertNotEqual(head_sha, "NO_HEAD")
        self.assertNotEqual(head_sha, "GIT_UNAVAILABLE")

    def test_token_sensitivity_uncommitted_edit(self):
        """Combined Git Token immediately changes upon working tree file edit."""
        token1, dirty1, _, _ = compute_git_token(self.test_dir)
        self.assertEqual(len(dirty1), 0)

        # Uncommitted edit
        with open(self.readme_path, "a", encoding="utf-8") as f:
            f.write("Uncommitted change.\n")

        token2, dirty2, _, _ = compute_git_token(self.test_dir)
        self.assertNotEqual(token1, token2, "Token must change on uncommitted working tree edit")
        self.assertIn("README.md", dirty2)

    def test_token_sensitivity_untracked_file(self):
        """Combined Git Token changes upon creating an untracked file."""
        token1, dirty1, _, _ = compute_git_token(self.test_dir)

        new_file = os.path.join(self.test_dir, "new_file.py")
        with open(new_file, "w", encoding="utf-8") as f:
            f.write("print('hello')\n")

        token2, dirty2, _, _ = compute_git_token(self.test_dir)
        self.assertNotEqual(token1, token2, "Token must change on untracked file addition")
        self.assertIn("new_file.py", dirty2)

    def test_token_sensitivity_file_deletion(self):
        """Combined Git Token changes upon deleting a tracked file."""
        token1, _, _, _ = compute_git_token(self.test_dir)

        os.remove(self.readme_path)

        token2, dirty2, _, _ = compute_git_token(self.test_dir)
        self.assertNotEqual(token1, token2, "Token must change on tracked file deletion")
        self.assertIn("README.md", dirty2)

    def test_token_sensitivity_commit(self):
        """Combined Git Token changes upon git commit even if working tree is clean."""
        token1, _, head1, _ = compute_git_token(self.test_dir)

        with open(self.readme_path, "a", encoding="utf-8") as f:
            f.write("Another commit.\n")
        subprocess.run(["git", "commit", "-am", "Second commit"], cwd=self.test_dir, capture_output=True, check=True)

        token2, dirty2, head2, _ = compute_git_token(self.test_dir)
        self.assertNotEqual(token1, token2, "Token must change when HEAD advances")
        self.assertNotEqual(head1, head2)
        self.assertEqual(len(dirty2), 0)

    def test_cache_persistence_and_freshness(self):
        """Tests read/write of git token and synchronous freshness detection."""
        # First check: no cache, should be not fresh
        is_fresh, token, dirty, _ = check_freshness(self.test_dir)
        self.assertFalse(is_fresh)

        # Write cache
        success = write_cached_token(self.test_dir, token)
        self.assertTrue(success)
        self.assertEqual(read_cached_token(self.test_dir), token)

        # Second check: cache matches, state is fresh
        is_fresh2, token2, dirty2, _ = check_freshness(self.test_dir)
        self.assertTrue(is_fresh2)
        self.assertEqual(token, token2)

        # Edit file: state becomes not fresh
        with open(self.readme_path, "a", encoding="utf-8") as f:
            f.write("Drift!\n")

        is_fresh3, token3, dirty3, _ = check_freshness(self.test_dir)
        self.assertFalse(is_fresh3)
        self.assertNotEqual(token, token3)

    def test_non_git_directory_fallback(self):
        """Gracefully falls back in non-git directory without throwing exceptions."""
        non_git_dir = tempfile.mkdtemp(prefix="antios_test_nongit_")
        try:
            token, dirty, head, dt_ms = compute_git_token(non_git_dir)
            self.assertIsInstance(token, str)
            self.assertEqual(len(token), 16)
            self.assertIn(head, ("NO_HEAD", "GIT_UNAVAILABLE"))
        finally:
            shutil.rmtree(non_git_dir, ignore_errors=True)

    def test_zero_daemons_guarantee(self):
        """Verifies no persistent threads or child daemons remain active (INV-15)."""
        import threading
        threads_before = threading.active_count()
        check_freshness(self.test_dir)
        threads_after = threading.active_count()
        self.assertEqual(threads_before, threads_after, "Freshness check must not spawn threads (INV-15)")


if __name__ == "__main__":
    unittest.main()
