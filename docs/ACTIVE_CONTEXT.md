# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Current Mission**: Phases 12–15 — AntiOS Capability Foundation  
**Date**: 2026-09-04  
**Active State**: Framework core, skills, workflows, and test harness implemented  

## 1. Objective
Transform the frozen AntiOS v1 foundation into an active, verified capability layer:
- Phase 12: Capability Architecture & Configurable Adapter
- Phase 13: Core Skills (antios-engineer, verifier, debug)
- Phase 14: Composed Workflows & Ratchets
- Phase 15: Agent Roles & Maker-Checker Protocol

## 2. Active Tasks
- [x] Phase 12: Declarative domain adapter config (`antios.config.json`)
- [x] Phase 12: Modular framework core (`framework/core/`)
- [x] Phase 12: Fail-closed hook refactoring (`pre_tool_guard.py`, `stop_gate.py`)
- [x] Phase 12: Prune legacy undiscoverable `framework/.agents/`
- [x] Phase 13: Canonical skill baseline (`antios-engineer`, `antios-verifier`, `antios-debug`)
- [x] Phase 14: Capability architecture & workflows specification (`docs/CAPABILITY_ARCHITECTURE.md`)
- [x] Phase 15: Maker-Checker role model & structured verdict protocol (`verdict.py`)
- [ ] Step 4: Author and execute deterministic pytest test suite in `tests/`
- [ ] Step 5: Verification audit & final report (`PHASE_12_15_IMPLEMENTATION_REPORT.md`)

## 3. Blockers & Constraints
- StudySourceCore is 100% OUT OF SCOPE.
- Production StudyLab code is untouched.
- Subagent Shallow Depth Law: Depth <= 2 strictly enforced.

## 4. Dead Ends (Do Not Repeat)
- Do NOT use `TypeName='research'` for verifiers (read-only; cannot run tests).
- Do NOT place skills inside `framework/.agents` (causes discoverability black hole).
- Do NOT fracture skills into 7 micro-skills (causes prompt clutter and coordination latency).
- Do NOT assume non-git folders support `git diff --check`.

## 5. Next Immediate Action
Author comprehensive unit test suite in `tests/` and run `pytest`.
