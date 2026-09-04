# AntiOS v1 Task State & Memory Model (`ANTIOS_STATE_MODEL.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish a bounded, human-readable, zero-dependency task-state mechanism that maintains focus across long-running sessions, survives context resets, and strictly separates active state from permanent knowledge and historical archives.

---

## 1. Forensic Verdict on Memory in AntiOS

Phase 10 forensic findings Q14 & Q15 established:
> *AntiOS possesses no active vector database, no background memory daemon, and no magical recall mechanism. It relies entirely on documented context in version-controlled markdown files.*  
> *When an agent session resets, the conversation context window is wiped to 0 tokens. The agent survives amnesia exclusively by reading static disk files.*

However, the prototype allowed `docs/ACTIVE_CONTEXT.md` to freeze at Prototype v0.1 setup, causing **stale-state deception** where resuming agents hallucinated completed work as pending.

---

## 2. The Three-Way Information Architecture

AntiOS v1 strictly segregates repository information into three non-overlapping tiers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TIER 1: ACTIVE TASK STATE                             │
│ File: docs/ACTIVE_CONTEXT.md                                                │
│ Budget: Strictly ≤ 60 lines (~2,000 bytes)                                  │
│ Scope: Ephemeral working memory. Tracks CURRENT mission, immediate tasks,   │
│        active blockers, and next action. Overwritten every phase/task.      │
├─────────────────────────────────────────────────────────────────────────────┤
│                    TIER 2: PERMANENT PROJECT KNOWLEDGE                      │
│ Files: docs/AGENTS.md, ANTIOS_V1.md, DECISION_REGISTER.md                   │
│ Budget: Compact, authoritative reference specifications                     │
│ Scope: Canonical architecture, system invariants, security models, and      │
│        decisions. Modified only through formal architectural consensus.     │
├─────────────────────────────────────────────────────────────────────────────┤
│                       TIER 3: HISTORICAL RESEARCH                           │
│ Files: reports/PHASE_*.md, reports/archive/, experiments/                   │
│ Budget: Unconstrained historical archive                                    │
│ Scope: Empirical lab notebooks, audit reports, attack matrices, and past    │
│        experimental data. Strictly READ-ONLY. Never active task state.      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Canonical Bounded Working Set: `docs/ACTIVE_CONTEXT.md`

### Structure & Budget Rules
1. **Line Limit**: Must NEVER exceed 60 lines. Long logs belong in reports or brain artifacts.
2. **Freshness Requirement**: Must be updated whenever a major phase or task transitions.
3. **Structured Fields**:
   - `Current Phase / Objective`: The single high-level goal.
   - `Active Workstreams / Checklist`: Bounded checklist (`[x]` done, `[ ]` pending).
   - `Blockers & Active Decisions`: Current obstacles or critical constraints.
   - `Dead Ends`: Approaches attempted and empirically disproved (to avoid repeat mistakes).
   - `Verification Status`: Outcome of latest test runner execution.
   - `Next Immediate Action`: Single unambiguous instruction for the next turn.

### Canonical Template
```markdown
# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Current Mission**: Phase 11 — AntiOS v1 Architecture Freeze
**Date**: 2026-09-04
**Active Branch**: main / root workspace

## 1. Objective
Finalize the clean, evidence-backed AntiOS v1 architecture and implementation blueprint, pruning prototype bloat and establishing canonical governance.

## 2. Active Tasks
- [x] Part 1: Master Capability Disposition
- [x] Part 2: Prototype Pruning & Cleanup
- [x] Part 3 & 4: Core Architecture & Responsibility Matrix
- [x] Part 5 & 6: Skill & Constitution Architecture
- [x] Part 10: Task State & Memory Model
- [ ] Part 7 & 17: Hook Security Architecture & Security Model
- [ ] Part 8, 9 & 11: Verification Model, Ratchet & Maker-Checker
- [ ] Part 13, 14, 15, 18: MCP, Documentation, Source of Truth & Rejected Arch
- [ ] Part 19, 20, 21, 23, 24: Decision Register, Freeze Review & Master V1 Spec

## 3. Blockers & Constraints
- StudySourceCore is 100% OUT OF SCOPE.
- Production StudyLab code is untouched.
- Shell (run_command) execution is an explicit platform boundary.

## 4. Dead Ends (Do Not Repeat)
- Do NOT use TypeName='research' for verifiers (read-only; cannot run tests).
- Do NOT use verify_task.py (trivial test forgery vector).
- Do NOT put skills in framework/ (invisible to platform engine).

## 5. Next Immediate Action
Author Part 7 & 17: Hook Security Architecture and Security Model.
```

---

## 4. Context Reset & Session Resumption Protocol

When an agent wakes up in a fresh session or after a context reset:
1. **Step 1 (Constitution)**: Read `docs/AGENTS.md` to anchor boundaries.
2. **Step 2 (Active State)**: Read `docs/ACTIVE_CONTEXT.md` to identify the active mission, current checklist, and next immediate action.
3. **Step 3 (Git Reality Check)**: Run `git status` (or inspect working tree) to ensure disk reality matches `ACTIVE_CONTEXT.md`. If disk reality disagrees, disk reality is authoritative.
4. **Step 4 (Proceed)**: Execute the `Next Immediate Action`.
