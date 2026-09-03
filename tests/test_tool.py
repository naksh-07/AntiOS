"""Tests for framework.core.tool — Minimal tool abstraction."""

from framework.core.tool import (
    FailureClass,
    ToolIdentity,
    ToolResult,
    ToolSelectionPolicy,
    ToolStatus,
    ToolTier,
)


def test_tool_result_success():
    r = ToolResult.success(stdout="ok", data={"count": 5})
    assert r.is_success
    assert r.status == ToolStatus.SUCCESS
    assert r.exit_code == 0
    assert r.data == {"count": 5}


def test_tool_result_failure():
    r = ToolResult.failure(
        failure_class=FailureClass.EXECUTION_FAILED,
        reason="Tests did not pass",
        exit_code=1,
        stderr="AssertionError",
    )
    assert not r.is_success
    assert r.status == ToolStatus.FAILURE
    assert r.failure_class == FailureClass.EXECUTION_FAILED
    assert "Tests did not pass" in r.failure_reason


def test_tool_result_denied():
    r = ToolResult.denied(reason="Protected zone")
    assert not r.is_success
    assert r.status == ToolStatus.DENIED
    assert r.exit_code == 126
    assert r.failure_class == FailureClass.POLICY_DENIED


def test_tool_result_timeout():
    r = ToolResult.timeout(seconds=30)
    assert not r.is_success
    assert r.status == ToolStatus.TIMEOUT
    assert r.exit_code == 124
    assert "30 seconds" in r.failure_reason


def test_tool_result_to_dict():
    r = ToolResult.success(stdout="hello")
    d = r.to_dict()
    assert d["status"] == "SUCCESS"
    assert d["exit_code"] == 0
    assert d["stdout"] == "hello"
    assert d["failure_class"] == "NONE"


def test_tool_identity():
    t = ToolIdentity(
        tool_id="inspect-repo",
        name="Repository Inspector",
        tier=ToolTier.SCRIPT,
        description="Inspects repository state",
        entrypoint="framework/scripts/tools/inspect_repo.py",
    )
    assert t.tier == ToolTier.SCRIPT
    assert t.is_deterministic
    assert not t.requires_network


def test_tool_selection_policy_native_first():
    assert ToolSelectionPolicy.select_tool_tier(True, True, True) == ToolTier.NATIVE


def test_tool_selection_policy_script_second():
    assert ToolSelectionPolicy.select_tool_tier(False, True, True) == ToolTier.SCRIPT


def test_tool_selection_policy_mcp_last():
    assert ToolSelectionPolicy.select_tool_tier(False, False, True) == ToolTier.MCP


def test_tool_selection_policy_fallback_script():
    assert ToolSelectionPolicy.select_tool_tier(False, False, False) == ToolTier.SCRIPT


def test_failure_class_values():
    """All expected failure classes should exist."""
    assert FailureClass.NONE.value == "NONE"
    assert FailureClass.SYSTEM_ERROR.value == "SYSTEM_ERROR"
    assert FailureClass.TIMEOUT.value == "TIMEOUT"
    assert FailureClass.VALIDATION_ERROR.value == "VALIDATION_ERROR"
    assert FailureClass.POLICY_DENIED.value == "POLICY_DENIED"
    assert FailureClass.ENVIRONMENT_MISSING.value == "ENVIRONMENT_MISSING"
    assert FailureClass.EXECUTION_FAILED.value == "EXECUTION_FAILED"


def test_tool_result_malformed_input():
    """Constructing ToolResult with missing fields should use defaults."""
    r = ToolResult(status=ToolStatus.FAILURE)
    assert r.exit_code == 0
    assert r.stdout == ""
    assert r.stderr == ""
    assert r.failure_class == FailureClass.NONE
    assert r.evidence == []
