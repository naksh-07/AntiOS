"""Tests for AntiOS Adapter Verification and Constitutional Invariant Protection.

Verifies that:
- Constitutional invariants (immutable zones, fail-closed) cannot be bypassed or stripped.
- Missing binaries in required runners are flagged.
- Manifest fingerprint drift is detected.
- Invalid adapter mutations are blocked.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

from framework.core.adapter import (
    ActionType,
    AdaptationProposal,
    AdaptationProposalItem,
    ChangeTarget,
    ProposalRisk,
    apply_project_adaptation,
    verify_adapter,
)
from framework.core.config import AntiOSConfig, PoliciesConfig, RunnerConfig


def test_verify_adapter_valid_configuration():
    """Valid adapter configuration with protected zones and available runners passes."""
    config = AntiOSConfig(
        version="1.0",
        name="Valid-Adapter",
        protected_zones=[".agents", "framework"],
        policies=PoliciesConfig(fail_closed=True),
        test_runners=[
            RunnerConfig(name="python-test", default_command=["python", "-m", "unittest"], required=True)
        ]
    )
    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is True
    assert len(result.issues) == 0
    assert any("Immutable core zone '.agents' protected." in p for p in result.passed_checks)
    assert any("Fail-closed policy enforced." in p for p in result.passed_checks)


def test_verify_adapter_missing_core_zone_blocks():
    """Omitting .agents or framework from protected_zones fails verification."""
    config = AntiOSConfig(
        version="1.0",
        name="Compromised-Adapter",
        protected_zones=["some_custom_zone"],  # Missing .agents and framework
        policies=PoliciesConfig(fail_closed=True),
        test_runners=[
            RunnerConfig(name="python-test", default_command=["python", "-m", "unittest"], required=True)
        ]
    )
    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION: Immutable core zone '.agents'" in i for i in result.issues)
    assert any("CONSTITUTIONAL VIOLATION: Immutable core zone 'framework'" in i for i in result.issues)


def test_verify_adapter_fail_closed_disabled_blocks():
    """Disabling fail-closed policy triggers constitutional violation."""
    config = AntiOSConfig(
        version="1.0",
        name="Insecure-Adapter",
        protected_zones=[".agents", "framework"],
        policies=PoliciesConfig(fail_closed=False),  # VIOLATION
        test_runners=[
            RunnerConfig(name="python-test", default_command=["python", "-m", "unittest"], required=True)
        ]
    )
    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("CONSTITUTIONAL VIOLATION: Fail-closed policy disabled" in i for i in result.issues)


def test_verify_adapter_missing_required_binary():
    """Required runner with unavailable binary on host PATH is flagged."""
    config = AntiOSConfig(
        version="1.0",
        name="Missing-Binary-Adapter",
        protected_zones=[".agents", "framework"],
        policies=PoliciesConfig(fail_closed=True),
        test_runners=[
            RunnerConfig(
                name="nonexistent-runner",
                default_command=["non_existent_binary_xyz_12345", "test"],
                required=True
            )
        ]
    )
    result = verify_adapter(".", config=config, check_fingerprint=False)
    assert result.is_valid is False
    assert any("is NOT available in PATH" in i for i in result.issues)


def test_verify_adapter_manifest_drift_detection():
    """Detects manifest drift when recorded manifest_fingerprint differs from current disk reality."""
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a manifest
        pkg_json = os.path.join(temp_dir, "package.json")
        with open(pkg_json, "w") as f:
            f.write(json.dumps({"name": "drift-test", "scripts": {"test": "echo 1"}}))

        config = AntiOSConfig(
            version="1.0",
            name="Drift-Adapter",
            manifest_fingerprint="old_stale_fingerprint_000000",
            protected_zones=[".agents", "framework"],
            policies=PoliciesConfig(fail_closed=True),
            test_runners=[
                RunnerConfig(name="npm-test", default_command=["npm", "test"], required=False)
            ]
        )
        result = verify_adapter(temp_dir, config=config, check_fingerprint=True)
        assert result.is_valid is False
        assert any("MANIFEST DRIFT" in i for i in result.issues)
    finally:
        shutil.rmtree(temp_dir)


def test_invalid_adapter_mutation_attempt_denied():
    """Attempts to apply an adaptation proposal modifying ANTIOS_CORE are unconditionally denied."""
    temp_dir = tempfile.mkdtemp()
    try:
        proposal = AdaptationProposal(
            repo_root=temp_dir,
            project_name="TrojanProject",
            items=[
                AdaptationProposalItem(
                    action=ActionType.CONFIGURE,
                    target=ChangeTarget.ANTIOS_CORE,
                    component="guard",
                    description="Allow arbitrary shell execution without inspection",
                    reason="Target app needs raw access",
                    risk=ProposalRisk.CRITICAL,
                    is_automated_safe=False
                )
            ]
        )
        success, msg = apply_project_adaptation(temp_dir, proposal)
        assert success is False
        assert "REFUSED" in msg
        assert "AntiOS-Core level changes" in msg
    finally:
        shutil.rmtree(temp_dir)
