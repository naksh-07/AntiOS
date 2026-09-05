# AntiOS Testing & Quality Assurance (`docs/operations/TESTING.md`)

# AntiOS Testing & Quality Assurance (`docs/operations/TESTING.md`)

AntiOS enforces a rigorous, multi-layered, zero-dependency testing architecture. All tests execute hermetically against the local physical filesystem using standard library `unittest`.

---

## 1. Test Suite Organization

The testing framework is centralized under `tests/` and executed by `tests/run_all.py` (115 test modules, 766 tests):

### A. Core Governance & Boundary Defense
- `test_guard.py` & `test_guard_hardened.py` — PreToolUse hook evaluation, path traversal defenses, protected zone immutability.
- `test_governance.py` — Governance rule evaluation and immutable core boundary checks.
- `test_security_adversarial.py` — Penetration testing, symlink escapes, and privilege escalation mitigations.

### B. Dynamic Ratchet & Verification
- `test_gate.py` & `test_gate_hardened.py` — Stop Gate verification ratchet, test runner discovery, timeout handling.
- `test_verdict.py` — Verifier JSON contract schema validation and tamper resistance.
- `test_maker_checker_dispatch.py` — Independent Maker-Checker auditor workflow dispatch.
- `test_verification_adversarial.py` & `test_adversarial_verification.py` — Verification bypass and suppressed failure attacks.

### C. Capability & Tool Policy Routing
- `test_capability_registry.py` & `test_capability_router.py` — Capability taxonomy, multi-index lookup, and task resolution.
- `test_capability_model.py`, `test_capability_pack.py` & `test_capability_benchmark.py` — Capability pack formatting and performance.
- `test_tool.py`, `test_tool_policy.py` & `test_tool_registry.py` — 8-tier hybrid capability matrix and MCP escalation protocol.
- `test_provider_model.py` & `test_golden_tool_routing.py` — Provider lifecycle and golden scenario resolution.
- `test_tool_negative.py`, `test_tool_failure.py` & `test_tool_benchmark.py` — Offline mode, fallback, and sub-millisecond benchmarks.

### D. Agent Routing & Delegation Topology
- `test_agent_router.py` & `test_agent_role_model.py` — Intent-to-specialist and verifier routing.
- `test_agent_topology.py` & `test_golden_agent_routing.py` — Hierarchical topology graphs and delegation depth laws (depth <= 2).
- `test_agent_negative.py`, `test_agent_adversarial.py` & `test_agent_benchmark.py` — Boundary authorization and rogue specialist blocks.

### E. Repository Intelligence & Topology
- `test_discovery.py`, `test_adapter.py` & `test_adapter_verification.py` — Multi-lingual repo discovery and adapter generation.
- `test_topology.py` & `test_subsystem.py` — Workspace topology detection (monorepos, polyglot) and subsystem boundaries.
- `test_wayfinding.py` & `test_project_knowledge.py` — Subsystem wayfinding and semantic keyword ranking.
- `test_fixtures.py` & `test_conflict.py` — 9 project archetypes in `tests/fixtures/`.

### F. Lifecycle, Memory & Recovery
- `test_lifecycle.py` — 10-stage task lifecycle state machine and active context line budget (<= 60 lines).
- `test_memory.py` & `test_lesson_distillation.py` — 3-tier memory model (Working, Episodic, Procedural).
- `test_recovery.py` — Crash recovery, state rollback, and session repair.
- `test_changeset.py` & `test_worktree.py` — Same Change Set policy and dirty worktree isolation.
- `test_skills.py` & `test_workflows.py` — Agent skill line budgets (<= 60 lines) and workflow contracts.
- `test_docaudit.py` & `test_doc_infrastructure.py` — Syntactic link validation and reference integrity.

### G. Native Antigravity Orchestration & Workforce Architecture
- `test_workforce_contract.py` — Native workforce contract, 11-step pipeline, anti-emulation constraints.
- `test_workforce_planner.py` — Adaptive workforce planner, 12-factor inputs, token-bounded cost card.
- `test_teamwork_wave_orchestration.py` — Wave manager, wave collapse rules, failure recovery engine.
- `test_hybrid_capability_matrix.py` — 8-tier hybrid capability execution matrix and escalation protocol.
- `test_orchestration_phase83_86_adversarial.py` — 10 adversarial vectors targeting orchestration constraints.
- `test_proving_ground_scenarios.py` — 9 external proving ground real-world scenarios.

### H. Context Engineering, Freshness & Mission Continuity
- `test_context_budget_governor.py` — 6-action context budget governor, token-bounded reasoning card.
- `test_context_freshness_compaction.py` — Context freshness evaluation, git drift detection, safe compaction.
- `test_mission_state_continuity.py` — Dual-mode persistence, 4-file format, crash recovery engine.
- `test_context_mission_adversarial.py` — 9 adversarial vectors targeting context injection, tampering, and state forgery.

### I. Full Integration & Red-Team Campaigns
- `test_e2e_scenarios.py` & `test_golden_tasks.py` — End-to-end task execution flows.
- `test_false_done_campaign.py` — 10-vector false-done adversarial attack matrix.
- `test_failure_injection_campaign.py` — Systemic fault injection across 15 failure modes.
- `test_performance_benchmarks.py` — Cross-subsystem sub-second performance validations.

---

## 2. Executing Tests

### Run Complete Test Suite
Execute all 766 tests with the zero-dependency runner:
```bash
python tests/run_all.py
```

### Run Module or Directory
Run any test module directly with Python standard library:
```bash
python -m unittest tests/test_guard.py
python -m unittest tests/test_context_budget_governor.py
```

---

## 3. Performance & Quality Invariants

1. **100% Deterministic Pass Rate**: Zero skipped tests, zero suppressed failures, zero errors.
2. **Sub-35s Full Execution**: Complete 766-test suite executes in ~30 seconds on standard hardware.
3. **Sub-Millisecond Routing**: In-memory capability, agent, and tool routing executes in <1ms per query.
