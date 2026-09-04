"""Unit tests for AntiOS Subsystem & Component Manifest Specification."""

import os
import unittest

from framework.core.subsystem import (
    SubsystemDeclaration,
    validate_subsystem_declaration,
)


def _get_sample_decl():
    return SubsystemDeclaration(
        subsystem_id="auth",
        name="Authentication Engine",
        description="Handles user identity, JWT tokens, and session persistence.",
        area="security",
        root_paths=["src/auth"],
        entrypoints=["src/auth/service.py"],
        authoritative_files=["src/auth/service.py", "src/auth/types.py"],
        covering_tests=["tests/test_auth.py"],
        test_commands=["pytest tests/test_auth.py"],
        applicable_skills=["antios-engineer", "antios-debug"],
        applicable_workflows=["FEATURE", "BUG"],
        governing_rules=["Token expiration must be verified"],
        protected_invariants=["src/auth/crypto.py"],
        dependencies=["database"],
        consumers=["api-gateway", "billing"],
        documentation_paths=["docs/subsystems/auth.md"],
        keywords=["auth", "login", "jwt", "session", "token"],
    )


def test_subsystem_declaration_initialization():
    decl = _get_sample_decl()
    assert decl.subsystem_id == "auth"
    assert decl.area == "security"
    assert len(decl.root_paths) == 1
    assert len(decl.keywords) == 5
    assert len(decl.consumers) == 2


def test_subsystem_declaration_to_and_from_dict():
    decl = _get_sample_decl()
    data = decl.to_dict()
    assert isinstance(data, dict)
    assert data["subsystem_id"] == "auth"
    assert data["test_commands"] == ["pytest tests/test_auth.py"]

    rebuilt = SubsystemDeclaration.from_dict(data)
    assert rebuilt == decl
    assert rebuilt.subsystem_id == "auth"
    assert rebuilt.name == "Authentication Engine"


def test_subsystem_declaration_from_dict_defaults():
    minimal = {"subsystem_id": "minimal-core"}
    decl = SubsystemDeclaration.from_dict(minimal)
    assert decl.subsystem_id == "minimal-core"
    assert decl.name == "minimal-core"
    assert decl.area == "core"
    assert decl.applicable_skills == ["antios-engineer"]
    assert decl.applicable_workflows == ["FEATURE", "BUG"]
    assert decl.root_paths == []


def test_subsystem_declaration_from_dict_missing_id():
    try:
        SubsystemDeclaration.from_dict({})
        assert False, "Should raise ValueError for missing subsystem_id"
    except ValueError:
        pass

    try:
        SubsystemDeclaration.from_dict({"subsystem_id": "   "})
        assert False, "Should raise ValueError for whitespace subsystem_id"
    except ValueError:
        pass


def test_validate_subsystem_declaration_structure():
    decl = _get_sample_decl()
    errors = validate_subsystem_declaration(decl)
    assert errors == []

    invalid_decl = SubsystemDeclaration(
        subsystem_id="invalid",
        name="Invalid Subsystem",
        description="",
        area="core",
        root_paths=[],
        entrypoints=[],
        authoritative_files=[],
        covering_tests=[],
        test_commands=[],
        applicable_skills=[],
        applicable_workflows=[],
        governing_rules=[],
        protected_invariants=[],
        dependencies=[],
        consumers=[],
        documentation_paths=[],
        keywords=[],
    )
    errors = validate_subsystem_declaration(invalid_decl)
    assert any("root path" in e for e in errors)
