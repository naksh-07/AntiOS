# AntiOS Testing & Quality Assurance (`docs/operations/TESTING.md`)

AntiOS enforces a rigorous, multi-layered, zero-dependency testing architecture. All tests execute hermetically against the local physical filesystem using standard library `unittest`.

---

## 1. Test Suite Organization

The testing framework is centralized under `tests/` and orchestrated by `tests/run_all.py`:

```
tests/
├── run_all.py                     # Master test suite runner & benchmark timer
├── test_guard.py                  # PreToolUse security interception tests
├── test_guard_hardened.py         # Boundary & path-traversal adversarial tests
├── test_gate.py                   # Stop Gate ratchet & test discovery tests
├── test_gate_hardened.py          # Dynamic runner execution & timeout tests
├── test_memory.py                 # Active context & decision register tests
├── test_memory_distillation.py    # Cross-session lesson promotion tests
├── test_knowledge.py              # Semantic documentation classification tests
├── test_budget.py                 # Context token budget estimator tests
├── test_lifecycle.py              # Task lifecycle state machine tests
├── test_changeset.py              # Same Change Set integrity tests
├── test_worktree.py               # Working tree snapshot & conflict tests
├── test_path_normalizer.py        # Unicode, symlink, and path normalization tests
├── test_security.py               # Shell command tokenization & safety tests
├── test_discovery.py              # Manifest & language detection tests
├── test_discovery_rules.py        # Multi-stack heuristic rule tests
├── test_adapter.py                # Project profile & adaptation generator tests
├── test_inspection.py             # Repository health inspection tests
├── test_topology.py               # Workspace topology detection tests
├── test_governance.py             # Rule evaluation & boundary tests
├── test_policy.py                 # Tool policy & execution rules tests
├── test_certification.py          # Canonical certification rules (C-01 to C-50)
├── test_capability_registry.py    # Capability registration & taxonomy tests
├── test_tool_model.py             # Canonical ToolDefinition data model tests
├── test_provider_model.py         # ProviderDefinition & abstraction tests
├── test_tool_registry.py          # Tool registry & secondary index tests
├── test_tool_policy.py            # MCP justification & authorization tests
├── test_tool_pack.py              # Bounded ToolRoutingPack serializer tests
├── test_golden_tool_routing.py    # Golden scenario tool resolution tests
├── test_tool_negative.py          # Security, boundary, and error tests
├── test_tool_failure.py           # Provider failure & fallback routing tests
├── test_tool_benchmark.py         # Performance benchmark tests (<0.1ms lookup)
├── test_orchestration.py          # Multi-agent workflow coordination tests
├── test_workflow.py               # Engineering workflow lifecycle tests
├── test_delegation.py             # Risk-based delegation & depth limit tests
├── test_docaudit.py               # Syntactic documentation reference tests
└── test_recovery.py               # Session recovery & state reconstruction tests
```

---

## 2. Executing Tests

### Run Full Test Suite
Execute all 447 tests with the master runner:
```bash
python tests/run_all.py
```

### Run Individual Test Module
Run a specific test suite using Python's standard `unittest`:
```bash
python -m unittest tests/test_guard.py
python -m unittest tests/test_tool_registry.py
```

---

## 3. Performance & Pass-Rate Invariants

1. **100% Pass Rate**: Zero failures, zero errors. Any failure blocks Stop Gate from completing.
2. **Sub-20s Execution**: The entire 447-test suite runs in under 20 seconds on standard developer hardware.
3. **Sub-Millisecond Routing**: Tool lookup, justification, and routing execute in <0.1ms per query with zero database dependencies.
