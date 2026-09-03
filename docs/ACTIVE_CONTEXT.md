# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Current Mission**: Phase 14–15: Core Skills & Engineering Workflow Layer
**Date**: 2026-09-04
**Active State**: Universal Core, Workflows, Lifecycle Engine & Skills Complete

## 1. Objective
Establish AntiOS as a universal, reusable Agent-Native Engineering OS for Antigravity:
- Decouple AntiOS Core from StudyLab proving ground domain assumptions.
- Generalize 3 canonical skills (`antios-engineer`, `antios-verifier`, `antios-debug`) to <= 60 lines.
- Implement 6 canonical engineering workflows (`FEATURE`, `BUG`, `REFACTOR`, `INVESTIGATION`, `DOCUMENTATION`, `RELEASE_MAINTENANCE`).
- Implement 10-step lifecycle state engine and test runner dynamic manifest auto-discovery.

## 2. Active Tasks
- [x] Phase 14: Core Decoupling (`framework/core/config.py` defaults to empty domain lists)
- [x] Phase 14: Dynamic Manifest Discovery (`framework/core/gate.py` auto-detects runners)
- [x] Phase 14: Lifecycle State Engine (`framework/core/lifecycle.py` 10-step progression)
- [x] Phase 14: Universal Workflow Registry (`framework/core/workflow.py` 6 task classes)
- [x] Phase 15: Universal Core Skills (`.agents/skills/` <= 60 lines, parameterized)
- [x] Phase 15: Workflow Specifications (`.agents/workflows/*.md` 6 workflow files)
- [x] Phase 15: Universal Project Constitution (`docs/AGENTS.md`)
- [x] Phase 15: Comprehensive Test Suite (31/31 tests passing in 0.77s)
- [x] Phase 15: Author Milestone Report (`ANTIOS_PHASE14_15_REPORT.md`)
- [x] Phase 15: Independent Verification Audit Wave (Status: PASS)

## 3. Blockers & Invariants
- StudySourceCore is 100% OUT OF SCOPE.
- Production StudyLab code remains completely untouched.
- Subagent Shallow Depth Law: Depth <= 2 strictly enforced.
- Token Budget: Skills <= 60 lines, ACTIVE_CONTEXT <= 60 lines.

## 4. Dead Ends (Do Not Repeat)
- Do NOT hardcode domain paths (e.g. rslib) into Core fallback dataclasses.
- Do NOT create micro-skills for every verb (caused prompt thrashing and discovery clutter).
- Do NOT duplicate platform Planning Mode mechanisms in skill files.

## 5. Next Immediate Action
Phase 16: Project Adapter Ecosystem & Proving Ground Certification.
