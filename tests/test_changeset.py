"""Tests for framework.core.changeset — Same Change Set integrity engine."""

import os
import tempfile

from framework.core.changeset import (
    ChangesetPolicy,
    ChangeSetEvaluation,
    _matches_any_pattern,
    evaluate_changeset,
)


def test_matches_code_patterns():
    policy = ChangesetPolicy()
    assert _matches_any_pattern("src/main.py", policy.code_patterns)
    assert _matches_any_pattern("lib/app.ts", policy.code_patterns)
    assert _matches_any_pattern("src/widget.dart", policy.code_patterns)
    assert not _matches_any_pattern("docs/README.md", policy.code_patterns)


def test_matches_test_patterns():
    policy = ChangesetPolicy()
    assert _matches_any_pattern("tests/test_main.py", policy.test_patterns)
    assert _matches_any_pattern("test/integration.py", policy.test_patterns)
    assert _matches_any_pattern("src/widget.spec.ts", policy.test_patterns)


def test_matches_doc_patterns():
    policy = ChangesetPolicy()
    assert _matches_any_pattern("docs/AGENTS.md", policy.doc_patterns)
    assert _matches_any_pattern("README.md", policy.doc_patterns)
    assert _matches_any_pattern("docs/architecture/design.md", policy.doc_patterns)


def test_changeset_clean_tree():
    """No changed files should pass validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = evaluate_changeset(tmpdir, changed_files=[], policy=ChangesetPolicy())
        assert result.is_valid
        assert "Clean" in result.summary or "clean" in result.summary.lower()


def test_changeset_code_only_violates():
    """Code-only changes without tests should violate when require_tests_on_code_change is True."""
    policy = ChangesetPolicy(require_tests_on_code_change=True)
    result = evaluate_changeset(".", changed_files=["src/main.py", "lib/utils.py"], policy=policy)
    assert not result.is_valid
    assert result.code_changed
    assert not result.tests_changed
    assert len(result.violations) > 0


def test_changeset_code_with_tests_passes():
    """Code changes accompanied by test changes should pass."""
    policy = ChangesetPolicy(require_tests_on_code_change=True)
    result = evaluate_changeset(
        ".", changed_files=["src/main.py", "tests/test_main.py"], policy=policy
    )
    assert result.is_valid
    assert result.code_changed
    assert result.tests_changed
    assert len(result.violations) == 0


def test_changeset_code_with_docs_required():
    """When require_docs_on_code_change is True, code without docs should violate."""
    policy = ChangesetPolicy(
        require_tests_on_code_change=False,
        require_docs_on_code_change=True,
    )
    result = evaluate_changeset(".", changed_files=["src/main.py"], policy=policy)
    assert not result.is_valid
    assert len(result.violations) == 1
    assert "documentation" in result.violations[0].lower()


def test_changeset_disabled_policy():
    """Disabled policy should always pass."""
    policy = ChangesetPolicy(enabled=False)
    result = evaluate_changeset(".", changed_files=["src/main.py"], policy=policy)
    assert result.is_valid


def test_changeset_tests_only_passes():
    """Test-only changes should always pass (no code change = no violation)."""
    policy = ChangesetPolicy(require_tests_on_code_change=True)
    result = evaluate_changeset(".", changed_files=["tests/test_new.py"], policy=policy)
    assert result.is_valid
    assert not result.code_changed
    assert result.tests_changed


def test_changeset_to_dict():
    """ChangeSetEvaluation.to_dict should serialize cleanly."""
    result = ChangeSetEvaluation(
        is_valid=True,
        code_changed=True,
        tests_changed=True,
        summary="All good",
    )
    d = result.to_dict()
    assert d["is_valid"] is True
    assert d["code_changed"] is True
    assert d["summary"] == "All good"
