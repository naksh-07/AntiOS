# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 79–82 Project Instance Runtime Closure
**Class**: ARCHITECTURE_CLOSURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED_AND_VERIFIED
**Version**: 2.0.0-RUNTIME-CLOSED | **Mode**: OPERATIONAL
**Active Subsystem**: Runtime Closure Contract, Standalone Hooks, Instance Verifier, Compiler Closure

## 1. Active Checklist
- [x] Phase 79: Runtime Closure Contract (`runtime_contract.py`, AST check, forbidden leak scan)
- [x] Phase 80: Standalone Instance Runtime Templates (`pre_tool_guard.py`, `stop_gate.py`, `inspect_instance.py`, `verify_runtime.py`)
- [x] Phase 81: Compiler & Adapter Runtime Asset Emission (`compiler.py`, `adapter.py`, `manifest.py`, `installation.py`)
- [x] Phase 82: Single Primary Skill (`/antios`) Runtime Closure (removed source references, synchronized template)
- [x] Comprehensive Test Suite: `tests/test_runtime_closure.py` (13/13 passing in 3.6s)
- [x] Full Regression Suite Pass (684/684 tests pass in 33.3s on `tests/run_all.py`, 0 failures)
- [x] Architecture Docs & ADR 65 Synchronized (`DECISION_REGISTER.md`, `PROJECT_AGENT_OS.md`, `ANTIOS_SOURCE_OF_TRUTH.md`)
- [x] Wave 4: Independent Maker-Checker Audit (`antios-verifier` PASS)

## 2. Blockers & Invariants
- Invariant: `SOURCE ≠ INSTANCE` — Target instances are 100% self-contained; zero framework imports.
- Invariant: Zero Legacy Workflows — no `.agents/workflows/`, zero copying `framework/` wholesale.
- Invariant: Fail-closed PreToolUse and Stop Gate hooks across both source and target environments.
- Invariant: Active Context strictly bounded <= 60 lines.

## 3. Changed Files & Verification State
- Core: `runtime_contract.py`, `compiler.py`, `adapter.py`, `manifest.py`, `installation.py`, `skill_generator.py`, `__init__.py`
- Templates: `pre_tool_guard.py`, `stop_gate.py`, `inspect_instance.py`, `verify_runtime.py`, `SKILL.md`
- Skills & Hooks: `.agents/skills/antios/SKILL.md`, `.agents/hooks.json`
- Tests: `tests/test_runtime_closure.py`, `tests/run_all.py` (684/684 tests passing)
- Docs: `DECISION_REGISTER.md` (ADR 65), `PROJECT_AGENT_OS.md`, `ANTIOS_SKILL_MODEL.md`, `ANTIOS_SOURCE_OF_TRUTH.md`
- Verdict: PASS (Independent Maker-Checker verified runtime closure)

## 4. Dead-End Memory & Validated Lessons
- In-memory PreToolUse hooks run with cwd = `.agents`, requiring clean workspace resolution.
- `verify_runtime.py` leak check excludes itself to prevent false-positive self-detection.
- Target protected zones protect `.agents`, `.antios`, `antios.config.json`; `framework` only in source.

## 5. Next Immediate Action
Mission complete. Certified under AntiOS 2.0 governance with independent Maker-Checker verification.
