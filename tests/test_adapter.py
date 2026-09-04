"""Tests for AntiOS Adapter Generation and Adaptation Proposal Model."""

import json
import os
from pathlib import Path
import tempfile
import unittest

from framework.core.adapter import (
    ActionType,
    AdaptationProposal,
    AdaptationProposalItem,
    ChangeTarget,
    ProposalRisk,
    analyze_adaptation,
    apply_project_adaptation,
    generate_adapter_config,
)
from framework.core.config import AntiOSConfig
from framework.core.discovery import discover_project

FIXTURES_DIR = Path(os.path.dirname(__file__)) / "fixtures"


def test_analyze_adaptation_proposal_creation():
    python_dir = FIXTURES_DIR / "python_project"
    profile = discover_project(str(python_dir))
    proposal = analyze_adaptation(profile)

    assert len(proposal.items) >= 1
    assert os.path.normcase(proposal.repo_root) == os.path.normcase(str(python_dir))
    assert not proposal.has_core_changes
    # All items for python_project should be PROJECT_LOCAL
    for item in proposal.items:
        assert item.target == ChangeTarget.PROJECT_LOCAL


def test_core_change_denial_invariant():
    """AntiOS Core must never be automatically mutated for project adaptation."""
    proposal = AdaptationProposal(
        repo_root="/fake/dir",
        project_name="unsafe-project",
        items=[
            AdaptationProposalItem(
                action=ActionType.DEFER,
                target=ChangeTarget.ANTIOS_CORE,
                component="core_parser",
                description="Modify framework/core/guard.py to allow custom bypass",
                reason="Project demands it",
                risk=ProposalRisk.CRITICAL,
                is_automated_safe=False,
            )
        ],
    )

    assert proposal.has_core_changes
    assert not proposal.is_safe_to_apply_automatically

    success, msg = apply_project_adaptation("/fake/dir", proposal, dry_run=False)
    assert not success
    assert "REFUSED" in msg
    assert "AntiOS-Core" in msg


def test_apply_project_adaptation_dry_run():
    python_dir = FIXTURES_DIR / "python_project"
    profile = discover_project(str(python_dir))
    proposal = analyze_adaptation(profile)

    with tempfile.TemporaryDirectory() as tmp_dir:
        success, msg = apply_project_adaptation(tmp_dir, proposal, dry_run=True)
        assert success
        assert "[DRY RUN]" in msg
        assert not os.path.exists(os.path.join(tmp_dir, "antios.config.json"))


def test_apply_project_adaptation_write():
    python_dir = FIXTURES_DIR / "python_project"
    profile = discover_project(str(python_dir))
    proposal = analyze_adaptation(profile)

    with tempfile.TemporaryDirectory() as tmp_dir:
        success, msg = apply_project_adaptation(tmp_dir, proposal, dry_run=False)
        assert success
        target_cfg = Path(tmp_dir) / "antios.config.json"
        assert target_cfg.exists()
        
        with open(target_cfg, "r") as f:
            data = json.load(f)
        assert data["name"] == f"AntiOS-{profile.identity.name}-Adapter"
        assert ".agents" in data["protected_zones"]
        assert "framework" in data["protected_zones"]
        assert len(data["test_runners"]) >= 1


if __name__ == "__main__":
    unittest.main()
