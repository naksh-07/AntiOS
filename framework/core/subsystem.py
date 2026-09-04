"""AntiOS Subsystem & Component Manifest Specification.

Defines the declarative data models for project subsystems, components,
entrypoints, invariants, test mappings, and dependencies.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SubsystemDeclaration:
    """Declarative specification of a project subsystem / component."""
    subsystem_id: str
    name: str
    description: str
    area: str                                # e.g. "ui", "core", "api", "infra", "auth"
    root_paths: List[str]                   # e.g. ["src/auth", "lib/auth"]
    entrypoints: List[str]                  # e.g. ["src/auth/service.py"]
    authoritative_files: List[str]          # Core files defining interface
    covering_tests: List[str]               # e.g. ["tests/test_auth.py"]
    test_commands: List[str]                # e.g. ["pytest tests/test_auth.py"]
    applicable_skills: List[str]            # e.g. ["antios-engineer"]
    applicable_workflows: List[str]         # e.g. ["FEATURE", "BUG"]
    governing_rules: List[str]              # e.g. ["Zero token leakage"]
    protected_invariants: List[str]         # Files/paths that must not be altered
    dependencies: List[str]                 # Subsystem IDs this depends upon
    consumers: List[str]                    # Subsystem IDs depending on this
    documentation_paths: List[str]          # e.g. ["docs/subsystems/auth.md"]
    keywords: List[str]                     # Search keywords for intent matching

    def to_dict(self) -> Dict[str, Any]:
        """Converts declaration to a JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SubsystemDeclaration:
        """Constructs SubsystemDeclaration from a dictionary with validation."""
        if not isinstance(data, dict):
            raise ValueError("SubsystemDeclaration requires a dictionary")
        raw_id = data.get("subsystem_id")
        if raw_id is None or not isinstance(raw_id, str) or not raw_id.strip():
            raise ValueError("SubsystemDeclaration requires non-empty 'subsystem_id'")
        subsystem_id = raw_id.strip()
        
        return cls(
            subsystem_id=subsystem_id,
            name=str(data.get("name", subsystem_id)).strip(),
            description=str(data.get("description", "")).strip(),
            area=str(data.get("area", "core")).strip(),
            root_paths=list(data.get("root_paths", [])),
            entrypoints=list(data.get("entrypoints", [])),
            authoritative_files=list(data.get("authoritative_files", [])),
            covering_tests=list(data.get("covering_tests", [])),
            test_commands=list(data.get("test_commands", [])),
            applicable_skills=list(data.get("applicable_skills", ["antios-engineer"])),
            applicable_workflows=list(data.get("applicable_workflows", ["FEATURE", "BUG"])),
            governing_rules=list(data.get("governing_rules", [])),
            protected_invariants=list(data.get("protected_invariants", [])),
            dependencies=list(data.get("dependencies", [])),
            consumers=list(data.get("consumers", [])),
            documentation_paths=list(data.get("documentation_paths", [])),
            keywords=list(data.get("keywords", [])),
        )


def validate_subsystem_declaration(declaration: SubsystemDeclaration, workspace_root: Optional[str] = None) -> List[str]:
    """Validates structural integrity of a subsystem declaration.
    
    Returns:
        List of error strings (empty if valid).
    """
    errors: List[str] = []
    if not declaration.subsystem_id:
        errors.append("Subsystem ID must not be empty.")
    if not declaration.name:
        errors.append("Subsystem name must not be empty.")
    if not declaration.root_paths:
        errors.append("Subsystem must specify at least one root path.")

    if workspace_root:
        norm_root = os.path.normcase(os.path.abspath(workspace_root))
        # Verify root paths exist if workspace_root is provided
        for rp in declaration.root_paths:
            abs_rp = os.path.normcase(os.path.abspath(os.path.join(norm_root, rp)))
            if not os.path.exists(abs_rp):
                errors.append(f"Root path '{rp}' does not exist on disk in workspace.")

    return errors
