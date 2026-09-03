"""Tests for framework.core.guard."""

import os
import tempfile

from framework.core.config import AntiOSConfig
from framework.core.guard import evaluate_tool_call


def test_guard_fail_closed_on_invalid_types():
    # None or non-dict
    decision, reason = evaluate_tool_call(None)
    assert decision == "deny"

    decision, reason = evaluate_tool_call("not a dict")
    assert decision == "deny"

    # Missing toolCall
    decision, reason = evaluate_tool_call({})
    assert decision == "deny"

    # Missing args
    decision, reason = evaluate_tool_call({"toolCall": {}})
    assert decision == "deny"

    # Missing TargetFile
    decision, reason = evaluate_tool_call({"toolCall": {"args": {}}})
    assert decision == "deny"

    # Empty TargetFile
    decision, reason = evaluate_tool_call({"toolCall": {"args": {"TargetFile": ""}}})
    assert decision == "deny"

    # Missing workspacePaths
    decision, reason = evaluate_tool_call({
        "toolCall": {"args": {"TargetFile": "some/file.txt"}},
        "workspacePaths": []
    })
    assert decision == "deny"


def test_guard_self_protection():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig()
        agents_dir = os.path.join(tmpdir, ".agents")
        framework_dir = os.path.join(tmpdir, "framework")
        os.makedirs(agents_dir, exist_ok=True)
        os.makedirs(framework_dir, exist_ok=True)

        # Target in .agents
        target_agents = os.path.join(agents_dir, "hooks.json")
        payload = {
            "toolCall": {"args": {"TargetFile": target_agents}},
            "workspacePaths": [tmpdir]
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "deny"
        assert "Self-Protection" in reason

        # Target in framework
        target_framework = os.path.join(framework_dir, "scripts", "hook.py")
        payload = {
            "toolCall": {"args": {"TargetFile": target_framework}},
            "workspacePaths": [tmpdir]
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "deny"
        assert "Self-Protection" in reason


def test_guard_domain_boundary_protection():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_domain_paths=["rslib"], forbidden_patterns=["rslib~*"])

        # Target in rslib
        target = os.path.join(tmpdir, "src", "rslib", "lib.rs")
        payload = {
            "toolCall": {"args": {"TargetFile": target}},
            "workspacePaths": [tmpdir]
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "deny"
        assert "Boundary Policy" in reason

        # Target with 8.3 short name alias
        target_83 = os.path.join(tmpdir, "src", "rslib~1", "lib.rs")
        payload = {
            "toolCall": {"args": {"TargetFile": target_83}},
            "workspacePaths": [tmpdir]
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "deny"
        assert "Boundary Policy" in reason


def test_guard_allows_application_targets():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig()
        target = os.path.join(tmpdir, "src", "ts", "app.ts")
        payload = {
            "toolCall": {"args": {"TargetFile": target}},
            "workspacePaths": [tmpdir]
        }
        decision, reason = evaluate_tool_call(payload, config=config)
        assert decision == "allow"
        assert reason is None
