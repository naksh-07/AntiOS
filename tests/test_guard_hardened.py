"""Hardened adversarial regression tests for framework.core.guard.

Tests cover:
- Immutable Core self-protection (antios.config.json, .git)
- Relative path anchoring to workspace root
- Out-of-workspace boundary confinement
- Multi-segment domain path enforcement
- Windows 8.3 alias bypass prevention on self-protection zones
- Invalid workspacePaths entries
"""

import os
import tempfile

from framework.core.config import AntiOSConfig
from framework.core.guard import evaluate_tool_call, IMMUTABLE_CORE_ZONES


def _payload(target, workspace):
    return {
        "toolCall": {"args": {"TargetFile": target}},
        "workspacePaths": [workspace],
    }


def test_guard_immutable_antios_config_json():
    """antios.config.json must be protected even if adapter clears protected_zones."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_zones=[])  # attacker cleared zones
        target = os.path.join(tmpdir, "antios.config.json")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny", f"antios.config.json should be denied but got: {decision}"
        assert "Self-Protection" in reason


def test_guard_immutable_git_directory():
    """.git must always be protected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_zones=[])
        target = os.path.join(tmpdir, ".git", "config")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"
        assert "Self-Protection" in reason


def test_guard_immutable_agents_even_when_cleared():
    """.agents must remain protected even with empty protected_zones in adapter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_zones=[])
        target = os.path.join(tmpdir, ".agents", "hooks.json")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"
        assert "Self-Protection" in reason


def test_guard_immutable_framework_even_when_cleared():
    """framework must remain protected even with empty protected_zones in adapter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_zones=[])
        target = os.path.join(tmpdir, "framework", "core", "guard.py")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"
        assert "Self-Protection" in reason


def test_guard_out_of_workspace_denied():
    """Writes outside the workspace repository boundary must fail closed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with tempfile.TemporaryDirectory() as outside:
            config = AntiOSConfig()
            target = os.path.join(outside, "evil.py")
            decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
            assert decision == "deny"
            assert "Boundary Policy" in reason or "outside" in reason.lower()


def test_guard_multi_segment_domain_path():
    """Multi-segment domain paths like 'src/core' must be enforced."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_domain_paths=["src/core"])
        target = os.path.join(tmpdir, "src", "core", "index.ts")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"
        assert "Boundary Policy" in reason


def test_guard_multi_segment_domain_allows_partial():
    """A file in src/ but NOT in src/core should be allowed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig(protected_domain_paths=["src/core"])
        target = os.path.join(tmpdir, "src", "app", "widget.ts")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "allow"


def test_guard_83_alias_bypass_on_framework():
    """8.3 alias like FRAMEW~1 targeting framework must be denied."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig()
        target = os.path.join(tmpdir, "framew~1", "core", "guard.py")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"


def test_guard_83_alias_bypass_on_agents():
    """8.3 alias like AGENTS~1 targeting .agents must be denied."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = AntiOSConfig()
        target = os.path.join(tmpdir, "agents~1", "hooks.json")
        decision, reason = evaluate_tool_call(_payload(target, tmpdir), config=config)
        assert decision == "deny"


def test_guard_invalid_workspace_path_string():
    """Empty string in workspacePaths should fail closed."""
    decision, reason = evaluate_tool_call({
        "toolCall": {"args": {"TargetFile": "some/file.py"}},
        "workspacePaths": [""],
    })
    assert decision == "deny"
    assert "Failing closed" in reason


def test_guard_workspace_path_non_string():
    """Non-string entry in workspacePaths should fail closed."""
    decision, reason = evaluate_tool_call({
        "toolCall": {"args": {"TargetFile": "some/file.py"}},
        "workspacePaths": [12345],
    })
    assert decision == "deny"


def test_guard_numeric_target_file():
    """Numeric TargetFile should fail closed."""
    decision, reason = evaluate_tool_call({
        "toolCall": {"args": {"TargetFile": 42}},
        "workspacePaths": ["C:\\tmp"],
    })
    assert decision == "deny"


def test_guard_immutable_core_zones_constant():
    """IMMUTABLE_CORE_ZONES must contain the 4 essential zones."""
    assert ".agents" in IMMUTABLE_CORE_ZONES
    assert "framework" in IMMUTABLE_CORE_ZONES
    assert "antios.config.json" in IMMUTABLE_CORE_ZONES
    assert ".git" in IMMUTABLE_CORE_ZONES
