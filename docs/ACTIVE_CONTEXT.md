# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS Phase 34–36: Agent Topology & Project-Specific Specialist Layer
**Class**: FEATURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: COMPLETED
**Active Subsystem**: core

## 1. Active Checklist
- [x] Canonical AgentRole domain model & AgentCapabilityBoundary implemented (`agent_role.py`)
- [x] AgentTopologyRegistry & SpecialistDiscoveryEngine implemented (`agent_topology.py`)
- [x] Deterministic AgentRouter with NO_DELEGATION default implemented (`agent_router.py`)
- [x] AgentRoutingPack data model & strict <= 25-line card formatter implemented (`agent_routing_pack.py`)
- [x] Shallow Depth Law (depth <= 2; no child spawning by specialists) strictly enforced
- [x] Project adapter topology schema & constitutional verification implemented (`adapter.py`, `config.py`)
- [x] CLI repository navigation extended with `--agent-routing` (`navigate_repo.py`)
- [x] 48 new tests implemented across unit, golden, negative, adversarial, & benchmark suites
- [x] 402/402 tests passing in 21.4s (100% pass rate, 0 regressions)
- [x] Formal Phase 34–36 architecture, agent model, routing, decision register, matrix & report docs authored

## 2. Blockers & Invariants
- Invariant: Locked architecture: Platform -> Core -> Adapter -> Target
- Invariant: Shallow depth law (depth <= 2; specialists/checkers never spawn children)
- Invariant: Active Context strictly bounded <= 60 lines (currently 46 lines)
- Invariant: Universal Core is project-agnostic; no foreign domain hardcoding
- Invariant: Zero third-party dependencies (Python 3.11 stdlib only)

## 3. Changed Files & Verification State
- Verification State: VERIFIED
- Active Subsystem: core
- Key Modules Added/Updated:
  - framework/core/agent_role.py, agent_topology.py, agent_router.py, agent_routing_pack.py
  - framework/core/config.py, adapter.py, capability_router.py, __init__.py
  - framework/scripts/tools/navigate_repo.py
  - tests/test_agent_*.py, tests/test_golden_agent_routing.py, tests/run_all.py
  - docs/architecture/PHASE34_36_*.md
- Verdict: PASS (402/402 tests passing in 21.4s)

## 4. Dead-End Memory & Validated Lessons
- Authority must never be inferred from role name; explicit capability boundary is required
- Default must remain NO_DELEGATION; delegation only when specialization provides measurable value
- Cross-subsystem features must be owned by Primary Agent to prevent multi-agent swarms
- Sub-millisecond routing (< 1ms) achieves 100% precision without agent daemons or schedulers

## 5. Next Immediate Action
AntiOS Phase 34–36 Agent Topology Layer certified and complete. Ready for Phase 37–39.
