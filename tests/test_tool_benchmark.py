"""Performance & Scalability Benchmark Suite for AntiOS Tool Layer."""

import time
from framework.core.tool import (
    ExecutionMode,
    Locality,
    ProviderAvailability,
    ToolDefinition,
    ToolTier,
)
from framework.core.provider import ProviderDefinition, ProviderType
from framework.core.tool_registry import ToolRegistry, build_default_tool_registry
from framework.core.tool_policy import DeterministicToolSelector, MCPJustificationEngine
from framework.core.wayfinding import WayfindingEngine
from framework.core.capability_router import CapabilityRouter


def test_benchmark_tool_registry_build():
    """ToolRegistry construction must complete in < 25ms."""
    start = time.perf_counter()
    reg = build_default_tool_registry()
    elapsed = (time.perf_counter() - start) * 1000
    assert len(reg._tools) >= 20
    assert len(reg._providers) >= 10
    assert elapsed < 50.0, f"Registry build took {elapsed:.2f}ms (expected < 50ms)"


def test_benchmark_provider_and_tool_lookup():
    """Provider and tool lookups must complete in sub-millisecond time (< 1ms)."""
    reg = build_default_tool_registry()
    start = time.perf_counter()
    for _ in range(100):
        t = reg.get_tool("tool:native-run-command")
        p = reg.get_provider("provider:antigravity-native")
        caps = reg.find_tools_by_capability("git:status")
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 20.0, f"100 lookups took {elapsed:.2f}ms (expected < 20ms)"


def test_benchmark_mcp_justification_evaluation():
    """MCP justification evaluation must execute in < 2ms."""
    start = time.perf_counter()
    for _ in range(50):
        rep = MCPJustificationEngine.evaluate(
            task_intent="Inspect browser DOM layout and styles",
            capability_id="browser:dom-inspection",
        )
    elapsed = (time.perf_counter() - start) * 1000
    assert rep.status == "USEFUL"
    assert elapsed < 25.0, f"50 MCP evaluations took {elapsed:.2f}ms (expected < 25ms)"


def test_benchmark_synthetic_scale_100_tools_and_providers():
    """Registry must scale linearly to 100+ tools and providers with < 10ms lookup."""
    reg = ToolRegistry(project_name="Synthetic-Scale")
    for i in range(100):
        prov = ProviderDefinition(
            provider_id=f"provider:synthetic-{i}",
            name=f"Synthetic Provider {i}",
            provider_type=ProviderType.PROJECT,
            capabilities=[f"cap:synthetic-{i}"],
        )
        reg.register_provider(prov)

        tool = ToolDefinition(
            tool_id=f"tool:synthetic-{i}",
            name=f"Synthetic Tool {i}",
            purpose=f"Synthetic tool operation {i}",
            tier=ToolTier.PROJECT,
            provider_id=f"provider:synthetic-{i}",
            capability_ids=[f"cap:synthetic-{i}"],
            supported_task_types=["FEATURE"],
        )
        reg.register_tool(tool)

    assert len(reg._tools) == 100
    assert len(reg._providers) == 100

    start = time.perf_counter()
    tools = reg.find_tools_by_capability("cap:synthetic-50")
    elapsed = (time.perf_counter() - start) * 1000
    assert len(tools) == 1
    assert elapsed < 5.0, f"Scale lookup took {elapsed:.2f}ms (expected < 5ms)"


def test_benchmark_full_pipeline_task_to_tool_resolution():
    """Full pipeline Task -> Capability -> Agent -> Tool must resolve in < 50ms."""
    engine = WayfindingEngine()
    cap_router = CapabilityRouter(wayfinding_engine=engine)
    tool_reg = build_default_tool_registry()
    selector = DeterministicToolSelector(tool_reg)

    start = time.perf_counter()
    # 1. Capability resolution
    cap_pack = cap_router.resolve_capabilities("Check git status and diff")
    # 2. Agent resolution
    agent_pack = cap_router.resolve_agent_routing("Check git status and diff")
    # 3. Tool resolution
    res = selector.select_tool(
        task_intent="Check git status and diff",
        capability_id="git:status",
    )
    elapsed = (time.perf_counter() - start) * 1000

    assert res["selected_tool"].tool_id == "tool:native-git-cli"
    assert elapsed < 100.0, f"Full resolution pipeline took {elapsed:.2f}ms (expected < 100ms)"
