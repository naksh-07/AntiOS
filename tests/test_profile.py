"""Tests for AntiOS Project Profile Model."""

import json
import unittest

from framework.core.profile import (
    ConfidenceLevel,
    ConflictFact,
    ConflictType,
    EvidenceFact,
    EvidenceTier,
    GuidanceFact,
    InferredFact,
    ProjectIdentity,
    ProjectProfile,
    ToolCategory,
    ToolFact,
    UnknownFact,
)


def test_profile_identity_and_facts():
    identity = ProjectIdentity(
        name="test-repo",
        root_path="/tmp/test-repo",
        is_git_repo=True,
        head_commit="abc1234",
        languages=["Python"],
        frameworks=["FastAPI"],
        package_managers=["uv"],
        build_systems=[],
    )
    profile = ProjectProfile(identity=identity)

    profile.add_observed("pyproject.toml", "[tool.pytest]", "configured", "FILE_CONTENT", "Pytest configured")
    profile.add_inferred("Uses pytest", 0.95, "Found [tool.pytest]", ["pyproject.toml"])
    profile.add_unknown("docs_location", "No docs found", "Add docs/", False)

    assert len(profile.observed_facts) == 1
    assert profile.observed_facts[0].path == "pyproject.toml"
    assert profile.observed_facts[0].to_dict()["tier"] == EvidenceTier.OBSERVED.value

    assert len(profile.inferred_facts) == 1
    assert profile.inferred_facts[0].confidence == 0.95
    assert profile.inferred_facts[0].confidence_level == ConfidenceLevel.HIGH

    assert len(profile.unknown_fields) == 1
    assert profile.unknown_fields[0].field_name == "docs_location"
    assert not profile.unknown_fields[0].is_blocking


def test_confidence_level_thresholds():
    high_fact = InferredFact("hypothesis", 0.90, "rationale")
    med_fact = InferredFact("hypothesis", 0.70, "rationale")
    low_fact = InferredFact("hypothesis", 0.45, "rationale")

    assert high_fact.confidence_level == ConfidenceLevel.HIGH
    assert med_fact.confidence_level == ConfidenceLevel.MEDIUM
    assert low_fact.confidence_level == ConfidenceLevel.LOW


def test_tool_fact_filtering():
    identity = ProjectIdentity(name="tool-test", root_path="/tmp")
    profile = ProjectProfile(identity=identity)

    runner = ToolFact(
        name="pytest",
        category=ToolCategory.TEST_RUNNER,
        manifest_path="pyproject.toml",
        command=["pytest"],
    )
    linter = ToolFact(
        name="ruff",
        category=ToolCategory.LINTER,
        manifest_path="pyproject.toml",
        command=["ruff", "check", "."],
    )

    profile.add_tool(runner)
    profile.add_tool(linter)

    assert len(profile.get_test_runners()) == 1
    assert profile.get_test_runners()[0].name == "pytest"
    assert len(profile.get_linters()) == 1
    assert profile.get_linters()[0].name == "ruff"


def test_profile_json_serialization():
    identity = ProjectIdentity(name="json-test", root_path="/tmp")
    profile = ProjectProfile(identity=identity)
    profile.add_observed("package.json", "file", "present")
    
    json_str = profile.to_json()
    parsed = json.loads(json_str)

    assert parsed["identity"]["name"] == "json-test"
    assert len(parsed["observed_facts"]) == 1
    assert parsed["observed_facts"][0]["path"] == "package.json"


if __name__ == "__main__":
    unittest.main()
