"""Adversarial and Edge-Case Test Suite for AntiOS Phase 28-30 Knowledge System."""

import os
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import (
    KnowledgeGraph,
    OwnershipDeriver,
    ProgressiveDisclosureLevel,
)
from framework.core.wayfinding import WayfindingEngine


def test_adversarial_circular_dependency_cycles():
    """Circular dependencies (A -> B -> C -> A) must not cause infinite recursion."""
    graph = KnowledgeGraph()
    sub_a = SubsystemDeclaration(
        subsystem_id="sub_a", name="A", description="", area="core",
        root_paths=["src/a"], entrypoints=[], authoritative_files=[],
        covering_tests=[], test_commands=[], applicable_skills=[],
        applicable_workflows=[], governing_rules=[], protected_invariants=[],
        dependencies=["sub_b"], consumers=["sub_c"], documentation_paths=[], keywords=[],
    )
    sub_b = SubsystemDeclaration(
        subsystem_id="sub_b", name="B", description="", area="core",
        root_paths=["src/b"], entrypoints=[], authoritative_files=[],
        covering_tests=[], test_commands=[], applicable_skills=[],
        applicable_workflows=[], governing_rules=[], protected_invariants=[],
        dependencies=["sub_c"], consumers=["sub_a"], documentation_paths=[], keywords=[],
    )
    sub_c = SubsystemDeclaration(
        subsystem_id="sub_c", name="C", description="", area="core",
        root_paths=["src/c"], entrypoints=[], authoritative_files=[],
        covering_tests=[], test_commands=[], applicable_skills=[],
        applicable_workflows=[], governing_rules=[], protected_invariants=[],
        dependencies=["sub_a"], consumers=["sub_b"], documentation_paths=[], keywords=[],
    )
    graph.add_component(sub_a)
    graph.add_component(sub_b)
    graph.add_component(sub_c)

    # Transitive dependencies must terminate without recursion error
    deps = graph.get_dependencies("sub_a", transitive=True)
    assert set(deps) == {"sub_b", "sub_c"}

    # Transitive consumers must terminate without recursion error
    cons = graph.get_consumers("sub_a", transitive=True)
    assert set(cons) == {"sub_b", "sub_c"}

    blast = graph.calculate_blast_radius("sub_a")
    assert "sub_b" in blast["transitive_consumers"]
    assert "sub_c" in blast["transitive_consumers"]


def test_adversarial_deep_dependency_chain():
    """Deep dependency chains (depth = 25) must resolve cleanly."""
    graph = KnowledgeGraph()
    for i in range(25):
        sub_id = f"node_{i}"
        next_id = f"node_{i+1}" if i < 24 else None
        deps = [next_id] if next_id else []
        sub = SubsystemDeclaration(
            subsystem_id=sub_id, name=f"Node {i}", description="", area="chain",
            root_paths=[f"src/{sub_id}"], entrypoints=[], authoritative_files=[],
            covering_tests=[], test_commands=[], applicable_skills=[],
            applicable_workflows=[], governing_rules=[], protected_invariants=[],
            dependencies=deps, consumers=[], documentation_paths=[], keywords=[],
        )
        graph.add_component(sub)

    trans_deps = graph.get_dependencies("node_0", transitive=True)
    assert len(trans_deps) == 24
    assert "node_24" in trans_deps

    trans_cons = graph.get_consumers("node_24", transitive=True)
    assert len(trans_cons) == 24
    assert "node_0" in trans_cons


def test_adversarial_nonexistent_component_resolution():
    engine = WayfindingEngine(workspace_root="/repo")
    res = engine.resolve_component("nonexistent_ghost_subsystem")
    assert res is None

    caps = engine.get_capabilities("ghost_subsystem")
    assert caps["skills"] == ["antios-engineer"]
    assert caps["rules"] == []


def test_adversarial_change_intent_injection_payload():
    engine = WayfindingEngine(workspace_root="/repo")
    attack_payloads = [
        "../../../etc/passwd",
        "'; DROP TABLE subsystems; --",
        "<script>alert('xss')</script>",
        "A" * 5000,
    ]
    intent = engine.analyze_change(attack_payloads)
    assert intent is not None
    assert intent.affected_subsystems == ["UNKNOWN"]
    assert "outside registered subsystems" in intent.blast_radius_summary


def test_adversarial_fake_ownership_no_hallucination():
    deriver = OwnershipDeriver(workspace_root="/empty_workspace")
    res = deriver.resolve_path("src/secret/core.py")
    assert res.owner is None
    assert res.source == "UNKNOWN"
    assert res.confidence == 0.0


def test_adversarial_progressive_disclosure_out_of_range():
    engine = WayfindingEngine(workspace_root="/repo")
    decl = SubsystemDeclaration(
        subsystem_id="simple", name="Simple", description="", area="core",
        root_paths=["src/simple"], entrypoints=[], authoritative_files=[],
        covering_tests=[], test_commands=[], applicable_skills=[],
        applicable_workflows=[], governing_rules=[], protected_invariants=[],
        dependencies=[], consumers=[], documentation_paths=[], keywords=[],
    )
    engine.register_subsystem(decl)
    res = engine.resolve_component("simple")

    # Asking for unknown integer level must not crash
    try:
        engine.locate_progressive("simple", level=99)
        assert False, "Should raise ValueError for invalid disclosure level"
    except ValueError:
        pass
