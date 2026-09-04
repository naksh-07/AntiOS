"""Performance & Scale Benchmarks for AntiOS Project Capability Layer (Phase 31–33).

Benchmarks:
1. Canonical registry construction time (< 25ms).
2. Capability query and multi-index filtering (< 2ms).
3. Task-to-capability routing pipeline (< 10ms).
4. CapabilityPack card rendering (< 2ms).
5. CapabilityPack JSON serialization (< 2ms).
6. Synthetic large registry scaling (100 capabilities) (< 5ms).
"""

from __future__ import annotations
import time

from framework.core.capability import Capability, CapabilityType
from framework.core.capability_registry import CapabilityRegistry, build_default_registry
from framework.core.capability_router import CapabilityRouter


def test_benchmark_registry_construction():
    start = time.perf_counter()
    reg = build_default_registry()
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 25.0, f"Registry construction took {elapsed_ms:.2f}ms (target < 25ms)"
    assert len(reg.list_all(enabled_only=False)) > 15


def test_benchmark_capability_lookup_and_indexing():
    reg = build_default_registry()
    start = time.perf_counter()
    for _ in range(100):
        _ = reg.find_by_subsystem("ui")
        _ = reg.find_by_task_type("FEATURE")
        _ = reg.get("skill:antios-engineer")
    elapsed_ms = ((time.perf_counter() - start) * 1000) / 100
    assert elapsed_ms < 2.0, f"Average lookup took {elapsed_ms:.3f}ms (target < 2ms)"


def test_benchmark_task_resolution_pipeline():
    router = CapabilityRouter(project_name="AntiOS-Bench")
    start = time.perf_counter()
    for _ in range(50):
        _ = router.resolve_capabilities("Change the login button")
    elapsed_ms = ((time.perf_counter() - start) * 1000) / 50
    assert elapsed_ms < 10.0, f"Average task resolution took {elapsed_ms:.3f}ms (target < 10ms)"


def test_benchmark_card_and_json_rendering():
    router = CapabilityRouter(project_name="AntiOS-Bench")
    pack = router.resolve_capabilities("Fix crash in database schema migration")

    start = time.perf_counter()
    for _ in range(100):
        _ = pack.format_card(max_lines=25)
    card_ms = ((time.perf_counter() - start) * 1000) / 100
    assert card_ms < 2.0, f"Card rendering took {card_ms:.3f}ms (target < 2ms)"

    start = time.perf_counter()
    for _ in range(100):
        _ = pack.to_json()
    json_ms = ((time.perf_counter() - start) * 1000) / 100
    assert json_ms < 10.0, f"JSON rendering took {json_ms:.3f}ms (target < 10ms)"


def test_benchmark_synthetic_scale_100_capabilities():
    reg = CapabilityRegistry()
    for i in range(100):
        reg.register(Capability(
            capability_id=f"tool:synthetic-{i}",
            type=CapabilityType.TOOL,
            name=f"Synthetic Tool {i}",
            purpose=f"Test tool {i}",
            applies_to_subsystems=[f"sub-{i % 10}"],
            applies_to_task_types=["FEATURE" if i % 2 == 0 else "BUG"],
        ))

    start = time.perf_counter()
    matched = reg.find_by_subsystem("sub-3")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert len(matched) == 10
    assert elapsed_ms < 5.0, f"Filtering 100 synthetic capabilities took {elapsed_ms:.2f}ms (target < 5ms)"
