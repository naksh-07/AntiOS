"""Performance Benchmarking Suite for AntiOS Phase 28-30 Knowledge & Wayfinding Engine."""

import time
import unittest

from framework.core.subsystem import SubsystemDeclaration
from framework.core.knowledge import (
    KnowledgeGraph,
    ProgressiveDisclosureLevel,
    ProgressiveDisclosureEngine,
)
from framework.core.wayfinding import WayfindingEngine


def test_perf_synthetic_graph_construction_50_nodes():
    """Constructing a 50-node knowledge graph with multi-edge indices must complete < 50ms."""
    graph = KnowledgeGraph()
    start = time.perf_counter()

    for i in range(50):
        deps = [f"sub_{i-1}"] if i > 0 else []
        cons = [f"sub_{i+1}"] if i < 49 else []
        decl = SubsystemDeclaration(
            subsystem_id=f"sub_{i}",
            name=f"Subsystem {i}",
            description=f"Synthetic test component {i}",
            area="core" if i % 2 == 0 else "infra",
            root_paths=[f"src/sub_{i}"],
            entrypoints=[f"src/sub_{i}/main.py"],
            authoritative_files=[f"src/sub_{i}/main.py", f"src/sub_{i}/api.py"],
            covering_tests=[f"tests/test_sub_{i}.py"],
            test_commands=[f"pytest tests/test_sub_{i}.py"],
            applicable_skills=["antios-engineer"],
            applicable_workflows=["FEATURE"],
            governing_rules=[f"Rule for subsystem {i}"],
            protected_invariants=[],
            dependencies=deps,
            consumers=cons,
            documentation_paths=[f"docs/sub_{i}.md"],
            keywords=[f"keyword_{i}", "synthetic", "test"],
        )
        graph.add_component(decl)

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert len(graph.list_components()) == 50
    assert elapsed_ms < 50.0, f"Graph construction took {elapsed_ms:.2f}ms (target < 50ms)"


def test_perf_transitive_blast_radius_resolution():
    """Transitive blast radius traversal across 50 nodes must complete < 10ms."""
    graph = KnowledgeGraph()
    for i in range(50):
        deps = [f"sub_{i+1}"] if i < 49 else []
        cons = [f"sub_{i-1}"] if i > 0 else []
        decl = SubsystemDeclaration(
            subsystem_id=f"sub_{i}",
            name=f"Subsystem {i}",
            description=f"Synthetic test component {i}",
            area="core",
            root_paths=[f"src/sub_{i}"],
            entrypoints=[], authoritative_files=[], covering_tests=[f"tests/test_{i}.py"],
            test_commands=[f"pytest tests/test_{i}.py"], applicable_skills=[],
            applicable_workflows=[], governing_rules=[], protected_invariants=[],
            dependencies=deps, consumers=cons, documentation_paths=[], keywords=[],
        )
        graph.add_component(decl)

    start = time.perf_counter()
    blast = graph.calculate_blast_radius("sub_49")
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert len(blast["transitive_consumers"]) == 49
    assert elapsed_ms < 10.0, f"Blast radius resolution took {elapsed_ms:.2f}ms (target < 10ms)"


def test_perf_wayfinding_query_and_change_intent():
    """Wayfinding query and change intent impact analysis must complete < 10ms."""
    engine = WayfindingEngine(workspace_root="/perf_repo")
    for i in range(30):
        decl = SubsystemDeclaration(
            subsystem_id=f"component_{i}",
            name=f"Component {i}",
            description=f"Handles feature {i}",
            area="services",
            root_paths=[f"src/component_{i}"],
            entrypoints=[f"src/component_{i}/service.py"],
            authoritative_files=[f"src/component_{i}/service.py"],
            covering_tests=[f"tests/test_{i}.py"],
            test_commands=[f"pytest tests/test_{i}.py"],
            applicable_skills=["antios-engineer"],
            applicable_workflows=["FEATURE"],
            governing_rules=[], protected_invariants=[],
            dependencies=[], consumers=[], documentation_paths=[],
            keywords=[f"feat_{i}", "service"],
        )
        engine.register_subsystem(decl)

    # 1. Query benchmark
    start_q = time.perf_counter()
    res = engine.locate("feat_15")
    q_ms = (time.perf_counter() - start_q) * 1000.0
    assert res is not None
    assert res.matched_subsystem_id == "component_15"
    assert q_ms < 5.0, f"Query took {q_ms:.2f}ms (target < 5ms)"

    # 2. Change intent benchmark
    start_ci = time.perf_counter()
    intent = engine.analyze_change([
        "src/component_5/service.py",
        "src/component_12/service.py",
        "src/component_20/service.py",
    ])
    ci_ms = (time.perf_counter() - start_ci) * 1000.0
    assert len(intent.affected_subsystems) == 3
    assert ci_ms < 10.0, f"Change intent took {ci_ms:.2f}ms (target < 10ms)"


def test_perf_progressive_disclosure_rendering():
    """Rendering progressive disclosure cards (L0-L4) must complete < 2ms."""
    engine = WayfindingEngine(workspace_root="/perf_repo")
    decl = SubsystemDeclaration(
        subsystem_id="core_engine",
        name="Core Engine",
        description="The central processing engine",
        area="core",
        root_paths=["src/core"],
        entrypoints=["src/core/main.py"],
        authoritative_files=["src/core/main.py"],
        covering_tests=["tests/test_core.py"],
        test_commands=["pytest tests/test_core.py"],
        applicable_skills=["antios-engineer"],
        applicable_workflows=["FEATURE"],
        governing_rules=["Rule 1"],
        protected_invariants=[],
        dependencies=[],
        consumers=["api"],
        documentation_paths=["docs/core.md"],
        keywords=["core", "engine"],
    )
    engine.register_subsystem(decl)
    res = engine.resolve_component("core_engine")
    assert res is not None

    start = time.perf_counter()
    for lvl in [ProgressiveDisclosureLevel.L1, ProgressiveDisclosureLevel.L2, ProgressiveDisclosureLevel.L3, ProgressiveDisclosureLevel.L4]:
        card = engine.format_progressive_card(res, level=lvl)
        assert len(card) > 0
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    assert elapsed_ms < 5.0, f"Progressive rendering took {elapsed_ms:.2f}ms (target < 5ms)"
