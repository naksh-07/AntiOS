"""Tests for framework.core.worktree — dirty state, conflict detection, snapshots."""

import os
import tempfile

from framework.core.worktree import (
    WorktreeDisposition,
    WorktreeSnapshot,
    WorktreeAuditResult,
    capture_worktree_snapshot,
    inspect_all_conflicts,
    find_conflict_markers_in_untracked,
    audit_worktree,
)


def test_snapshot_all_dirty_files():
    snap = WorktreeSnapshot(
        timestamp=1000.0,
        commit_sha="abc123",
        staged_files=["a.py"],
        unstaged_files=["b.py"],
        untracked_files=["c.py"],
    )
    assert snap.all_dirty_files == {"a.py", "b.py", "c.py"}


def test_snapshot_empty():
    snap = WorktreeSnapshot(timestamp=0.0, commit_sha="HEAD")
    assert len(snap.all_dirty_files) == 0


def test_audit_result_to_dict():
    result = WorktreeAuditResult(
        disposition=WorktreeDisposition.CLEAN,
        is_acceptable=True,
        summary="Clean",
    )
    d = result.to_dict()
    assert d["disposition"] == "CLEAN"
    assert d["is_acceptable"] is True


def test_inspect_all_conflicts_non_git_dir():
    """Non-git directory should return empty conflict list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        conflicts = inspect_all_conflicts(tmpdir)
        assert conflicts == []


def test_find_conflict_markers_non_git():
    """Non-git directory should return empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        conflicts = find_conflict_markers_in_untracked(tmpdir)
        assert conflicts == []


def test_audit_worktree_non_git():
    """Non-git directory should audit as clean (no .git = no dirty state)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = audit_worktree(tmpdir)
        # No .git means git status returns empty, so disposition should be CLEAN
        assert result.disposition == WorktreeDisposition.CLEAN
        assert result.is_acceptable


def test_audit_forbidden_dirty_with_conflict_markers():
    """Conflict markers should produce FORBIDDEN_DIRTY disposition."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize a git repo
        os.system(f'git init "{tmpdir}" >nul 2>&1' if os.name == "nt" else f'git init "{tmpdir}" >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" config user.email "test@test.com"')
        os.system(f'git -C "{tmpdir}" config user.name "test"')
        # Create a file, add, commit
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")
        os.system(f'git -C "{tmpdir}" add -A >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" add -A >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" commit -m "init" >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" commit -m "init" >/dev/null 2>&1')

        # Now write conflict markers into the tracked file
        with open(test_file, "w") as f:
            f.write("<<<<<<< HEAD\nmine\n=======\ntheirs\n>>>>>>> branch\n")

        result = audit_worktree(tmpdir)
        assert result.disposition == WorktreeDisposition.FORBIDDEN_DIRTY
        assert not result.is_acceptable
        assert len(result.conflict_markers_found) > 0


def test_audit_expected_dirty():
    """Files modified during task (not in baseline) should be EXPECTED_DIRTY."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.system(f'git init "{tmpdir}" >nul 2>&1' if os.name == "nt" else f'git init "{tmpdir}" >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" config user.email "test@test.com"')
        os.system(f'git -C "{tmpdir}" config user.name "test"')
        test_file = os.path.join(tmpdir, "app.py")
        with open(test_file, "w") as f:
            f.write("print('initial')\n")
        os.system(f'git -C "{tmpdir}" add -A >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" add -A >/dev/null 2>&1')
        os.system(f'git -C "{tmpdir}" commit -m "init" >nul 2>&1' if os.name == "nt" else f'git -C "{tmpdir}" commit -m "init" >/dev/null 2>&1')

        # Baseline snapshot: clean
        baseline = WorktreeSnapshot(timestamp=0.0, commit_sha="abc")

        # Modify file after baseline
        with open(test_file, "w") as f:
            f.write("print('modified')\n")

        result = audit_worktree(tmpdir, baseline_snapshot=baseline)
        assert result.disposition == WorktreeDisposition.EXPECTED_DIRTY
        assert result.is_acceptable
        assert len(result.task_modified_files) > 0


def test_worktree_disposition_values():
    """All disposition values should exist."""
    assert WorktreeDisposition.CLEAN.value == "CLEAN"
    assert WorktreeDisposition.EXPECTED_DIRTY.value == "EXPECTED_DIRTY"
    assert WorktreeDisposition.PRE_EXISTING_DIRTY.value == "PRE_EXISTING_DIRTY"
    assert WorktreeDisposition.UNEXPECTED_DIRTY.value == "UNEXPECTED_DIRTY"
    assert WorktreeDisposition.FORBIDDEN_DIRTY.value == "FORBIDDEN_DIRTY"
