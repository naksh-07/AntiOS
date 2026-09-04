# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 55–60 Project Anatomy & Intelligence Synthesis
**Class**: FEATURE_ARCHITECTURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED
**Version**: 2.0.0-PROPOSAL | **Mode**: OPERATIONAL
**Active Subsystem**: Project Anatomy, Component Intelligence & Verification

## 1. Active Checklist
- [x] Phase 55: Project Anatomy Compiler (`anatomy.py`, `.antios/project_anatomy.json`)
- [x] Phase 56: Component Intelligence (`component_intelligence.py`, card <= 25 lines)
- [x] Phase 57: Project Skill Generation (`skill_generator.py`, main skill <= 80 lines)
- [x] Phase 58: Project Specialist Generation (`specialist_generator.py`, depth <= 2)
- [x] Phase 59: Workflow Retirement Enforced (0 `.agents/workflows/` generated)
- [x] Phase 60: Generated Intelligence Verification (`intelligence_verifier.py`, CLI)
- [x] 10-Fixture Proving Ground Matrix Certified (`test_phase55_60_fixtures.py`)
- [x] Authoritative Full Regression Run (534/534 tests pass in 30.18s) & Audit

## 2. Blockers & Invariants
- Invariant: 4-Boundary Demarcation (`SOURCE ≠ INSTANCE ≠ PROJECT ≠ ANTIGRAVITY`)
- Invariant: Target project never receives AntiOS core framework code or tests
- Invariant: Shallow Depth Law (max delegation depth <= 2, specialists can_delegate=False)
- Invariant: Epistemic segregation (`OBSERVED`, `INFERRED`, `UNKNOWN`)
- Invariant: Active Context strictly bounded <= 60 lines (currently 42 lines)

## 3. Changed Files & Verification State
- Core: `anatomy.py`, `component_intelligence.py`, `skill_generator.py`, `specialist_generator.py`, `intelligence_verifier.py`, `compiler.py`
- CLI: `framework/scripts/tools/verify_intelligence.py`
- Tests: 7 new test modules (534/534 tests passing 100% with 0 regressions)
- Fixtures: 5 new test fixtures covering web, legacy, drift, and custom agents
- Docs: `DECISION_REGISTER.md` (ADR 49, 50), `docs/INDEX.md`, `ANTIOS_V1.md`

## 4. Dead-End Memory & Validated Lessons
- `SubsystemDeclaration` has 15 positional fields; construct via `from_dict` in tests
- Subsystem objects in `SpecialistGenerator` must be safely coerced from dict/str/obj
- Discovery of important directories must check both root and `src/`/`lib/`/`app/`
- Zero workflows invariant: routing flows exclusively via `/antios` and native skills

## 5. Next Immediate Action
Phase 55–60 implementation complete. Final verifier audit and sign-off.
