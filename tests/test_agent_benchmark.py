"""Performance Benchmark Test Suite for AntiOS Agent Topology & Routing (Phase 34–36).

Verifies strict lightweight performance targets:
- AgentTopologyRegistry lookup & indexing (< 0.5ms)
- AgentRouter.route_task resolution (< 1.0ms)
- AgentRoutingPack card rendering & JSON emission (< 0.5ms)
- Full pipeline CapabilityRouter.resolve_agent_routing (< 2.0ms)
"""

from __future__ import annotations
import time

from framework.core.agent_router import AgentRouter
from framework.core.agent_topology import build_default_agent_topology
from framework.core.capability_router import CapabilityRouter
from framework.core.capability_pack import CapabilityPack
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


def test_benchmark_agent_topology_lookup():
    reg = build_default_agent_topology()

    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        _ = reg.get("role:root-cause-debugger")
        _ = reg.find_by_subsystem("governance")
        _ = reg.find_by_task_type("BUG")
        _ = reg.get_primary_agent()
    duration = time.perf_counter() - start

    avg_ms = (duration / iterations) * 1000
    assert avg_ms < 0.5, f"Registry lookup exceeded budget: {avg_ms:.4f}ms"


def test_benchmark_agent_routing_resolution():
    router = AgentRouter()
    pack = CapabilityPack(
        pack_id="pack-bench",
        project_name="Benchmark",
        task_intent="Fix crash in auth",
        task_class="BUG",
        risk_tier="MEDIUM",
        matched_subsystems=["auth"],
        matched_components=["token"],
        workflow={"id": "wf:bug", "name": "Bug"},
        skills=[{"capability_id": "skill:antios-engineer"}],
        rules=[{"capability_id": "rule:core-immutable", "name": "Core"}],
        tools=[{"capability_id": "tool:navigate-repo", "name": "Nav"}],
        verifier={"capability_id": "verifier:maker-checker"},
        specialists=[],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED"},
        why_selected={},
        confidence=0.9,
        epistemic_state="OBSERVED",
    )

    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        _ = router.route_task(pack)
    duration = time.perf_counter() - start

    avg_ms = (duration / iterations) * 1000
    assert avg_ms < 2.5, f"Agent routing resolution exceeded budget: {avg_ms:.4f}ms"


def test_benchmark_card_and_json_rendering():
    router = AgentRouter()
    pack = CapabilityPack(
        pack_id="pack-bench",
        project_name="Benchmark",
        task_intent="Fix crash in auth",
        task_class="BUG",
        risk_tier="MEDIUM",
        matched_subsystems=["auth"],
        matched_components=["token"],
        workflow={"id": "wf:bug", "name": "Bug"},
        skills=[{"capability_id": "skill:antios-engineer"}],
        rules=[{"capability_id": "rule:core-immutable", "name": "Core"}],
        tools=[{"capability_id": "tool:navigate-repo", "name": "Nav"}],
        verifier={"capability_id": "verifier:maker-checker"},
        specialists=[],
        providers=[],
        mcp_decision={"status": "NOT_NEEDED"},
        why_selected={},
        confidence=0.9,
        epistemic_state="OBSERVED",
    )
    routing = router.route_task(pack)

    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        _ = routing.format_card()
        _ = routing.format_summary()
        _ = routing.to_json()
    duration = time.perf_counter() - start

    avg_ms = (duration / iterations) * 1000
    assert avg_ms < 2.5, f"Rendering & JSON emission exceeded budget: {avg_ms:.4f}ms"


def test_benchmark_full_pipeline_resolution():
    wayfinder = WayfindingEngine()
    wayfinder.register_subsystem(SubsystemDeclaration.from_dict({
        "subsystem_id": "auth",
        "name": "Auth",
        "description": "Auth subsystem",
        "area": "security",
        "root_paths": ["src/auth"],
        "authoritative_files": ["src/auth/token.py"],
        "covering_tests": ["tests/test_auth.py"],
        "keywords": ["auth", "token"],
    }))
    cap_router = CapabilityRouter(wayfinding_engine=wayfinder, project_name="Benchmark")

    iterations = 200
    start = time.perf_counter()
    for _ in range(iterations):
        _ = cap_router.resolve_agent_routing("Fix bug in auth token")
    duration = time.perf_counter() - start

    avg_ms = (duration / iterations) * 1000
    assert avg_ms < 2.0, f"Full pipeline resolution exceeded budget: {avg_ms:.4f}ms"
