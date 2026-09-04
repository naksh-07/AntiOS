# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 49–54 Main Skill, Orchestration & Capability Dispatch
**Class**: FEATURE_ARCHITECTURE | **Risk**: HIGH
**Stage**: VERIFY | **Status**: ACTIVE
**Version**: 2.0.0-PROPOSAL | **Mode**: VERIFYING
**Active Subsystem**: Adaptive Orchestration, Capability Dispatch & Main Skill

## 1. Active Checklist
- [x] Phase 49: Authoritative Mission Orchestrator & Ledger (`framework/core/orchestration.py`)
- [x] Phase 50: Canonical Task Dispatch Pipeline (`framework/core/dispatch.py`, `dispatch_task.py`)
- [x] Phase 51: Universal Main Operating Skill (`.agents/skills/antios/SKILL.md`)
- [x] Phase 52: Boundary Compiler & Installation Sync (`framework/core/compiler.py`)
- [x] Phase 53: Legacy Workflow Retirement & Migration (`reports/archive/legacy_workflows/`)
- [x] Phase 54: Architecture Specs & Decision Register (Decisions 43–48, ORCHESTRATION_MODEL.md)
- [x] Comprehensive Test Matrix (Skill discovery, sizing, budget, waves, hierarchy, adversarial)
- [x] Authoritative Full Regression Run (503/503 tests pass in 27.18s) & Audit

## 2. Blockers & Invariants
- Invariant: 4-Boundary Demarcation (`SOURCE ≠ INSTANCE ≠ PROJECT ≠ ANTIGRAVITY`)
- Invariant: Max active subagents <= 10 per wave; total launches <= 20 per mission; depth <= 2
- Invariant: Mandatory wave collapse (`NEXT_WAVE_ALLOWED` only when active total == 0)
- Invariant: Read-parallel, write-controlled (no overlapping concurrent writers)
- Invariant: Active Context strictly bounded <= 60 lines (currently 42 lines)

## 3. Changed Files & Verification State
- Core: `framework/core/orchestration.py`, `dispatch.py`, `worktree.py`, `governance.py`
- Skill: `.agents/skills/antios/SKILL.md`, `framework/templates/skills/antios/SKILL.md`
- CLI: `framework/scripts/tools/dispatch_task.py`
- Docs: `ORCHESTRATION_MODEL.md`, `ANTIOS_SKILL_MODEL.md`, `ORCHESTRATION_POLICY.md`, `AGENT_DISPATCH.md`
- Tests: `test_main_antios_skill.py`, `test_orchestration_adaptive.py`, `test_dispatch_pipeline.py`, `test_orchestration_adversarial.py`
- Regressions: 503 tests pass (`python tests/run_all.py`), 0 broken doc links (`audit_docs.py --all`)

## 4. Dead-End Memory & Validated Lessons
- `write_to_file` on codebase files must NOT include `ArtifactMetadata` (reserved for brain artifacts)
- `RiskTier` in `lifecycle.py` uses `HIGH`, `MEDIUM`, `LOW` (no `CRITICAL` enum value)
- `find_conflict_markers_in_untracked` must check conflict separator lines to prevent banner collisions
- Retiring `.agents/workflows/` eliminates dual authority while preserving archive evidence

## 5. Next Immediate Action
Emit authoritative final acceptance report and conclude Phase 49–54 implementation.
