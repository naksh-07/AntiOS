# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 61–66 Project Learning & Safe Intelligence Evolution
**Class**: FEATURE_ARCHITECTURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED
**Version**: 2.0.0-PROPOSAL | **Mode**: OPERATIONAL
**Active Subsystem**: Project Learning Engine, Epistemic Segregation & Safety Gate

## 1. Active Checklist
- [x] Phase 61: Deterministic Project-Local Observation Capture (`ObservationStore`, bounds <=100/200KB)
- [x] Phase 62: Deterministic Lesson Distillation & Signature Deduplication (`LessonDistiller`)
- [x] Phase 63: Evidence Promotion Lifecycle (`OBSERVED` -> `CANDIDATE` -> `VALIDATED` -> `DURABLE`)
- [x] Phase 64: Safe Skill & Knowledge Evolution (`EvolutionProposalEngine`, proposals only, no silent mutation)
- [x] Phase 65: Knowledge Decay & Staleness Detection (`KnowledgeDecayEngine`, preserves provenance)
- [x] Phase 66: Learning Safety Gate & Certification Boundary (10 safety invariants, prompt injection defense)
- [x] Full Regression Suite Pass (571/571 tests pass in 25.10s, 0 failures, 0 regressions)
- [x] CLI & Distillation Tooling Verified (`distill_memory.py`, `verify_intelligence.py`)

## 2. Blockers & Invariants
- Invariant: "Learning is evidence accumulation, not memory mutation."
- Invariant: Zero silent mutation of codebase or skills; evolution via reviewable proposals only.
- Invariant: Core framework (`framework/`, `ANTIOS_CONSTITUTION.md`) is strictly immutable.
- Invariant: Shallow Depth Law (depth <= 2; specialist self-promotion strictly blocked).
- Invariant: Storage ceilings (<=100 observations, <=200KB store, <=120 char titles, <=1000 char content).
- Invariant: Active Context strictly bounded <= 60 lines (currently 42 lines).

## 3. Changed Files & Verification State
- Core: `framework/core/learning.py`, `__init__.py`, `compiler.py`, `intelligence_verifier.py`
- Tools & Skills: `distill_memory.py`, `.agents/skills/antios/SKILL.md`, `framework/templates/skills/antios/SKILL.md`
- Tests: 5 new test modules (37 new tests, 571/571 tests passing on `run_all.py` and `pytest`)
- Docs: `docs/ACTIVE_CONTEXT.md`, `docs/INDEX.md`, `DECISION_REGISTER.md` (ADR 51, 52)

## 4. Dead-End Memory & Validated Lessons
- Epistemic segregation: Agent inferences (weight 0.3) alone can never promote lessons to `VALIDATED`.
- Test runner invariant: Windows CP-1252 byte encodings in docs/comments must be strict ASCII/UTF-8.
- Learning state lives in `.antios/learning_observations.json` and `.antios/learning_proposals.json`.
- Missing files or removed subsystems trigger staleness decay without deleting provenance audit trails.

## 5. Next Immediate Action
Wave 4 Independent Maker-Checker verification and final sign-off.
