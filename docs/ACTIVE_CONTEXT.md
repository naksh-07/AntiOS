# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.1 — Phase 106 Experience Intelligence Engine
**Class**: ARCHITECTURE_AND_INTELLIGENCE | **Risk**: MEDIUM
**Stage**: COMPLETE | **Status**: CERTIFIED_PHASE_106
**Version**: 2.0.0-beta.1 (2.1 Storage Foundation) | **Mode**: OPERATIONAL
**Active Subsystem**: Experience Analytics Engine, Metrics & Non-Mutation Boundary

## 1. Active Checklist
- [x] Epistemic Separation: Strict firewall between System A (Project Learning) and System B (Experience Intelligence)
- [x] Analytics Core: `experience_analytics.py` deterministic metrics, failure, friction, strategy mining
- [x] Unified CLI: `antios experience {analyze,report,export}` with JSON and Markdown outputs
- [x] Non-Mutation Tests: `test_experience_learning_separation.py` verifies byte-for-byte immutability
- [x] Engine Tests: `test_experience_intelligence.py` 17 dimensions (empty store, recovery, retries, etc.)
- [x] Core Exports: Package exports in `framework/core/__init__.py`
- [x] Architecture Spec: `docs/architecture/EXPERIENCE_INTELLIGENCE.md` ratified
- [x] Global Test Suite: Integrated in `tests/run_all.py` (20 new tests, 100% passing)

## 2. Blockers & Invariants
- Invariant: Experience is raw telemetry; Learning is evidence accumulation; Proofs are physical disk byte hashes.
- Invariant: Experience Intelligence NEVER automatically feeds into learning, memory, lessons, or rules.
- Invariant: Zero background daemons, zero vector DBs, zero embeddings, zero custom agent runtimes.
- Invariant: INV-10 (Zero database files in project repositories).
- Invariant: Module size $\le 2000$ lines; Active Context $\le 60$ lines; cards $\le 25$ lines.

## 3. Changed Files & Verification State
- Core: `experience_analytics.py` (NEW), `experience.py`, `__init__.py`, `cli.py`
- Tests: `test_experience_intelligence.py` (NEW), `test_experience_learning_separation.py` (NEW), `run_all.py`
- Docs: `docs/architecture/EXPERIENCE_INTELLIGENCE.md` (NEW), `docs/ACTIVE_CONTEXT.md`
- Verdict: PASS (20/20 Phase 106 tests passing, zero project mutation verified)

## 4. Dead-End Memory & Validated Lessons
- `AntiOSDataResolver.resolve_context()` encapsulates data directory, database path, and project identity cleanly.
- Epistemic classification requires explicit `UNKNOWN` when denominators are zero; avoid heuristic guessing.
- Target project immutability is validated cryptographically via full working tree SHA-256 snapshots.

## 5. Next Immediate Action
Phase 106 complete. Recommended next step: Phase 107.
