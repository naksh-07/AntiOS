# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS Phase 31–33: Project Capability Layer
**Class**: FEATURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: COMPLETED
**Active Subsystem**: core

## 1. Active Checklist
- [x] Canonical capability domain models across 8 types implemented (`capability.py`)
- [x] In-memory deterministic registry indexing capabilities implemented (`capability_registry.py`)
- [x] Task-to-capability router with intent classifier & why_selected implemented (`capability_router.py`)
- [x] CapabilityPack data model & strict <= 25-line card formatter implemented (`capability_pack.py`)
- [x] Multi-tier progressive capability disclosure (L0-L5) integrated (`knowledge.py`)
- [x] Project adapter capability policy & core invariant defense implemented (`adapter.py`, `config.py`)
- [x] CLI repository navigation extended with `--task` and `--json` (`navigate_repo.py`)
- [x] 46 new tests implemented across unit, golden tasks, adversarial, & benchmark suites
- [x] 354/354 tests passing in 21.3s (100% pass rate, 0 regressions)
- [x] Formal Phase 31–33 architecture, routing, decision, matrix & report docs authored

## 2. Blockers & Invariants
- Invariant: Locked architecture: Platform -> Core -> Adapter -> Target
- Invariant: Shallow depth law (depth <= 2; verifier never spawns children)
- Invariant: Active Context strictly bounded <= 60 lines (currently 48 lines)
- Invariant: Universal Core is project-agnostic; no foreign domain hardcoding
- Invariant: Zero third-party dependencies (Python 3.11 stdlib only)

## 3. Changed Files & Verification State
- Verification State: VERIFIED
- Active Subsystem: core
- Key Modules Added/Updated:
  - framework/core/capability.py, capability_registry.py, capability_router.py, capability_pack.py
  - framework/core/knowledge.py, wayfinding.py, config.py, adapter.py
  - framework/scripts/tools/navigate_repo.py
  - tests/test_capability_*.py, tests/test_golden_tasks.py, tests/run_all.py
- Verdict: PASS (354/354 tests passing in 21.3s)

## 4. Dead-End Memory & Validated Lessons
- Capability routing must evaluate negative applicability (e.g. debug on doc tasks)
- Core invariant rules must carry higher precedence (Rank 2) than project guidance (Rank 5)
- Tool mechanism must be decoupled from skill procedural policy
- Sub-millisecond routing (<1ms) achieves 100% precision without vector databases

## 5. Next Immediate Action
AntiOS Phase 31–33 Project Capability Layer certified and complete. Ready for Phase 34+.
