# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 90–92 Evidence Architecture, Evaluation & Benchmarking
**Class**: EVALUATION_AND_MEASUREMENT | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED_AND_VERIFIED
**Version**: 2.0.0-EVIDENCE-GRADE | **Mode**: OPERATIONAL
**Active Subsystem**: Evidence Architecture, Mission Evaluation Engine, Mission Benchmark

## 1. Active Checklist
- [x] Phase 90: Evidence Architecture (`evidence.py`, epistemic separation, 6 states, bounded packages)
- [x] Phase 91: Mission Evaluation Engine (`mission_evaluation.py`, 11 dimensions, 4 statuses, Maker-Checker)
- [x] Phase 92: Agent-Native Mission Benchmark (`mission_benchmark.py`, proxy metrics, baseline vs AntiOS, A–J)
- [x] Core Integration: Stage 9 & 10 pipeline integration (`dispatch.py`), `__init__.py`, `mission_state.py`
- [x] Comprehensive Test Suites: 4 test modules, 41 new tests, 12 adversarial vectors (807/807 passing)
- [x] Architecture Docs & ADRs 74–76 Synchronized (`DECISION_REGISTER.md`, `EVIDENCE_ARCHITECTURE.md`, etc.)
- [x] Skills & Templates Synchronized (`.agents/skills/antios/SKILL.md`, `framework/templates/skills/antios/SKILL.md`)
- [x] Maker-Checker Audit: Independent verification via `antios-verifier`

## 2. Blockers & Invariants
- Invariant: `AntiOS orchestrates Antigravity, not AntiOS rebuilds Antigravity`.
- Invariant: Epistemic Law: `OBSERVATION ≠ EVIDENCE ≠ VERDICT ≠ INFERENCE ≠ DECISION`.
- Invariant: Constitutional Limits: Max 10 active/wave, Max 20 lifetime launches, Shallow Depth $\le 2$.
- Invariant: Mandatory Wave Collapse: `NEXT_WAVE` blocked while active total $\ne 0$.
- Invariant: Active Context strictly bounded $\le 60$ lines.

## 3. Changed Files & Verification State
- Core: `evidence.py`, `mission_evaluation.py`, `mission_benchmark.py`, `dispatch.py`, `mission_state.py`, `__init__.py`
- Skills: `.agents/skills/antios/SKILL.md`, `framework/templates/skills/antios/SKILL.md`
- Tests: `test_evidence_architecture.py`, `test_mission_evaluation.py`, `test_mission_benchmark.py`, `test_evidence_evaluation_adversarial.py`, `run_all.py`
- Docs: `EVIDENCE_ARCHITECTURE.md`, `MISSION_EVALUATION.md`, `MISSION_BENCHMARK.md`, `DECISION_REGISTER.md`, `ANTIOS_SOURCE_OF_TRUTH.md`, `INDEX.md`, `README.md`
- Verdict: PASS (All 807 tests pass cleanly with 0 failures)

## 4. Dead-End Memory & Validated Lessons
- Agent assertions must never be registered as `EVIDENCE` without physical command/test artifacts.
- `ToolOutputClassifier.process_output` (aliased to `classify`) bounds oversized stdout $>2000$ chars with SHA-256.
- Comparison metrics must use conservative categories (`OBSERVED_IMPROVEMENT`, `MEASURED_DIFFERENCE`, `INSUFFICIENT_DATA`).
- `summary_notes` formatting in BenchmarkReportCard requires up to 160 characters to avoid trailing string cutoff.

## 5. Next Immediate Action
Phases 90–92 complete, verified, and certified. Ready for independent Maker-Checker audit.
