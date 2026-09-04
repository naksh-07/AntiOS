# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS Phase 28–30: Agent-Native Project Knowledge & Wayfinding
**Class**: FEATURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: COMPLETED
**Active Subsystem**: core

## 1. Active Checklist
- [x] Knowledge Graph with 8 typed edge relations implemented (`knowledge.py`)
- [x] Ownership deriver with CODEOWNERS fnmatch & confidence implemented
- [x] Functional doc taxonomy & broken/stale reference detection implemented
- [x] Transitive blast radius & change intent analysis implemented
- [x] Progressive disclosure engine (L0–L5) with line budgets implemented
- [x] WayfindingEngine & navigate_repo.py integrated with Knowledge Graph
- [x] 42 new tests implemented across unit, adversarial, perf, & e2e suites
- [x] 308/308 tests passing in 18.9s (100% pass rate, 0 regressions)
- [x] Formal Phase 28–30 architecture & completion reports published

## 2. Blockers & Invariants
- Invariant: Locked architecture: Platform -> Core -> Adapter -> Target
- Invariant: Shallow depth law (depth <= 2; verifier never spawns children)
- Invariant: Active Context strictly bounded <= 60 lines
- Invariant: Production StudyLab & StudySourceCore untouched (out of scope)
- Invariant: Zero third-party dependencies (Python 3.11 stdlib only)

## 3. Changed Files & Verification State
- Verification State: VERIFIED
- Active Subsystem: core
- Key Modules Added/Updated:
  - framework/core/knowledge.py, subsystem.py, wayfinding.py, discovery.py
  - framework/scripts/tools/navigate_repo.py
  - tests/test_project_knowledge.py, test_change_intent.py
  - tests/test_progressive_disclosure.py, test_ownership_derivation.py
  - tests/test_doc_infrastructure.py, test_knowledge_wayfinding.py
  - tests/test_knowledge_adversarial.py, test_performance_phase28_30.py
  - tests/test_phase28_30_integration.py, tests/run_all.py
- Verdict: PASS (308/308 tests passing in 18.9s)

## 4. Dead-End Memory & Validated Lessons
- CODEOWNERS glob matching must strip trailing /* to match directories
- ProgressiveDisclosureLevel requires explicit range check to fail closed
- Reverse consumer BFS prevents silent regression in downstream dependents
- In-memory graph indices execute in <5ms without external databases

## 5. Next Immediate Action
AntiOS Phase 28–30 completed and certified. Ready for Phase 31+.
