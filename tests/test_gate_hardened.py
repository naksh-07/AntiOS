"""Hardened adversarial regression tests for framework.core.gate.

Tests cover:
- Stop gate fail-closed on missing/empty workspacePaths
- Stop gate fail-closed on empty dict input
- Required runner with missing binary fails closed
- Same Change Set integration with gate
"""

import json
import os
import tempfile

from framework.core.config import AntiOSConfig, PoliciesConfig, RunnerConfig
from framework.core.changeset import ChangesetPolicy
from framework.core.gate import evaluate_stop_gate, discover_test_runners


def test_gate_fail_closed_on_missing_workspace():
    """Empty workspacePaths must fail closed instead of falling back to os.getcwd()."""
    payload = {"workspacePaths": []}
    decision, reason = evaluate_stop_gate(payload)
    assert decision == "continue", f"Expected continue but got: {decision}"
    assert "Failing closed" in reason


def test_gate_fail_closed_on_empty_dict():
    """Empty dict (no workspacePaths key) must fail closed."""
    decision, reason = evaluate_stop_gate({})
    assert decision == "continue"
    assert "Failing closed" in reason


def test_gate_fail_closed_on_none_workspace():
    """None workspacePaths must fail closed."""
    decision, reason = evaluate_stop_gate({"workspacePaths": None})
    assert decision == "continue"
    assert "Failing closed" in reason


def test_gate_fail_closed_on_invalid_workspace_entry():
    """Non-string entry in workspacePaths must fail closed."""
    decision, reason = evaluate_stop_gate({"workspacePaths": [123]})
    assert decision == "continue"
    assert "Failing closed" in reason


def test_gate_fail_closed_on_empty_string_workspace():
    """Empty string workspace must fail closed."""
    decision, reason = evaluate_stop_gate({"workspacePaths": [""]})
    assert decision == "continue"
    assert "Failing closed" in reason


def test_gate_required_runner_missing_binary_fails_closed():
    """A required runner whose binary is not in PATH must fail closed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
            f.write("[project]\nname = 'test'")

        runner = RunnerConfig(
            name="nonexistent-tool",
            manifest="pyproject.toml",
            default_command=["totally_nonexistent_binary_12345", "test"],
            required=True,
        )
        config = AntiOSConfig(
            test_runners=[runner],
            policies=PoliciesConfig(
                enforce_working_tree_cleanliness=False,
                enforce_same_change_set=False,
            ),
            changeset=ChangesetPolicy(enabled=False),
        )
        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "continue", f"Expected continue but got: {decision}"
        assert "Required" in reason or "not found" in reason


def test_gate_non_required_runner_missing_binary_continues():
    """A non-required runner whose binary is missing should be skipped, not block."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = RunnerConfig(
            name="optional-tool",
            manifest="",
            default_command=["totally_nonexistent_binary_67890", "run"],
            required=False,
        )
        config = AntiOSConfig(
            test_runners=[runner],
            policies=PoliciesConfig(
                enforce_working_tree_cleanliness=False,
                enforce_same_change_set=False,
            ),
            changeset=ChangesetPolicy(enabled=False),
        )
        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "allow"


def test_gate_changeset_policy_disabled_allows():
    """When changeset policy is disabled, gate should not enforce it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(
            policies=PoliciesConfig(
                enforce_working_tree_cleanliness=False,
                enforce_same_change_set=False,
            ),
            changeset=ChangesetPolicy(enabled=False),
        )
        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "allow"


def test_gate_still_allows_with_valid_workspace():
    """A valid workspace with no runners and no issues should allow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(
            policies=PoliciesConfig(
                enforce_working_tree_cleanliness=False,
                enforce_same_change_set=False,
            ),
            changeset=ChangesetPolicy(enabled=False),
        )
        payload = {"workspacePaths": [tmpdir]}
        decision, reason = evaluate_stop_gate(payload, config=config)
        assert decision == "allow"
