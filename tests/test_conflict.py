"""Tests for AntiOS Conflict Detection Taxonomy and Precedence Resolution."""

import os
from pathlib import Path
import unittest

from framework.core.discovery import discover_project
from framework.core.profile import ConflictFact, ConflictType

FIXTURES_DIR = Path(os.path.dirname(__file__)) / "fixtures"


def test_conflict_project_detections():
    conflict_dir = FIXTURES_DIR / "conflict_project"
    profile = discover_project(str(conflict_dir))

    assert len(profile.conflicts) >= 2

    # Check for Guidance vs Manifest drift
    drift_conflict = next(
        (c for c in profile.conflicts if c.conflict_type == ConflictType.GUIDANCE_MANIFEST_DRIFT),
        None,
    )
    assert drift_conflict is not None
    assert drift_conflict.winning_source == "MANIFEST"
    assert "test:legacy" in drift_conflict.prose_claim

    # Check for Constitutional Boundary Violation
    const_conflict = next(
        (c for c in profile.conflicts if c.conflict_type == ConflictType.CONSTITUTIONAL_VIOLATION),
        None,
    )
    assert const_conflict is not None
    assert const_conflict.winning_source == "ANTIOS_CORE_CONSTITUTION"
    assert ".agents" in const_conflict.description

    # Check for Ambiguous Dual Tooling
    dual_conflict = next(
        (c for c in profile.conflicts if c.conflict_type == ConflictType.AMBIGUOUS_DUAL_TOOLING),
        None,
    )
    assert dual_conflict is not None
    assert "pnpm-lock.yaml" in dual_conflict.description


def test_tooling_environment_mismatch_detection():
    # Construct synthetic conflict
    conflict = ConflictFact(
        conflict_type=ConflictType.TOOLING_ENVIRONMENT_MISMATCH,
        description="Cargo binary not found in PATH",
        prose_claim="cargo test",
        physical_reality="Binary missing in host environment",
        resolution_recommendation="Fail-closed Stop Gate with ENVIRONMENT_UNAVAILABLE",
        winning_source="PHYSICAL_ENVIRONMENT",
    )
    assert conflict.conflict_type == ConflictType.TOOLING_ENVIRONMENT_MISMATCH
    assert "ENVIRONMENT_UNAVAILABLE" in conflict.resolution_recommendation


if __name__ == "__main__":
    unittest.main()
