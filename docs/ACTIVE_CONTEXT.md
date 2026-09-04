# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS Phase 37–39: Tool, Provider & MCP Architecture
**Class**: FEATURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: COMPLETED
**Active Subsystem**: core

## 1. Active Checklist
- [x] Extended ToolTier and Canonical ToolDefinition model implemented (`tool.py`)
- [x] Canonical ProviderDefinition and ProviderType abstraction implemented (`provider.py`)
- [x] Deterministic Tool & Provider Registry with 6 secondary indices implemented (`tool_registry.py`)
- [x] Unified MCPJustificationEngine answering 8 canonical questions implemented (`tool_policy.py`)
- [x] Strict 6-Tier Tool Preference (NATIVE > SCRIPT > PROJECT > EXTERNAL > SERVICE > MCP) implemented
- [x] Tool Authorization Enforcement against AgentCapabilityBoundary implemented (`tool_policy.py`)
- [x] Bounded ToolRoutingPack data model (<= 25 lines) implemented (`tool_pack.py`)
- [x] CLI repository navigation extended with `--tools`, `--providers`, `--tool-selection` (`navigate_repo.py`)
- [x] 45 new tests implemented across unit, golden (12 tasks), negative, failure, & benchmark suites
- [x] 447/447 tests passing in ~18.6s (100% pass rate, 0 regressions)
- [x] Phase 37–39 architecture, tool model, provider model, ADR, matrix & report docs authored

## 2. Blockers & Invariants
- Invariant: Locked architecture: Platform -> Core -> Adapter -> Target
- Invariant: Shallow depth law (depth <= 2; specialists/checkers never spawn children)
- Invariant: Local Git CLI authoritative for local repo; GitHub MCP restricted to remote PRs
- Invariant: No custom AntiOS MCP server; core scripts remain local deterministic tools
- Invariant: Tool selection does NOT grant authority; governed by agent boundary & protected zones
- Invariant: Active Context strictly bounded <= 60 lines (currently 47 lines)
- Invariant: Zero third-party dependencies (Python 3.11 stdlib only)

## 3. Changed Files & Verification State
- Verification State: VERIFIED
- Active Subsystem: core
- Key Modules Added/Updated:
  - framework/core/tool.py, provider.py, tool_registry.py, tool_policy.py, tool_pack.py, __init__.py
  - framework/scripts/tools/navigate_repo.py
  - tests/test_provider_model.py, test_tool_registry.py, test_tool_policy.py, test_tool_pack.py
  - tests/test_golden_tool_routing.py, test_tool_negative.py, test_tool_failure.py, test_tool_benchmark.py
  - tests/run_all.py, docs/architecture/PHASE37_39_*.md
- Verdict: PASS (447/447 tests passing in ~18.6s)

## 4. Dead-End Memory & Validated Lessons
- Wildcard capability matching must check `endswith("*")` to prevent prefix false-positives
- Available candidates must be sorted before unavailable candidates regardless of tier preference
- Provider declaration does not grant authority; agent role boundary must be checked at selection time
- Sub-millisecond lookup (<0.1ms) achieved in-memory with zero external database or runtime daemons

## 5. Next Immediate Action
AntiOS Phase 37–39 certified and complete. Stop at Phase 37–39 boundary. Ready for Phase 40–42.
