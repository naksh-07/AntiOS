# AntiOS v1 Skill Architecture (`ANTIOS_SKILL_ARCHITECTURE.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Define a discoverable, progressive, non-redundant skill system that injects genuine project governance without duplicating Antigravity platform mechanisms.

---

## 1. Forensic Audit of Prototype Skills

Phase 10 exposed three fatal flaws in the prototype skill (`studylab-task-runner`):
1. **Discoverability Black Hole**: It was placed in `framework/.agents/skills/`. Antigravity only indexes `<workspace_root>/.agents/skills/` and `<workspace_root>/.gemini/skills/`. As a result, the skill was **100% invisible to the platform engine** in the root workspace.
2. **Platform Redundancy**: It attempted to teach the RPAC lifecycle (Refine, Plan, Act, Consolidate), which is virtually identical to Antigravity's native Planning Mode (`<planning_mode>`: Research $\to$ Plan $\to$ User Approval $\to$ Execute $\to$ Verify).
3. **Execution Tooling Bug**: Line 29 advised spawning a verifier subagent with `TypeName='research'`. The `research` subagent is strictly read-only and possesses no `run_command` tool, making it incapable of running test suites.

---

## 2. Core Architectural Principles for v1 Skills

1. **Root Discoverability**: All active skills reside in `<workspace_root>/.agents/skills/<skill-name>/SKILL.md`.
2. **Lean & Non-Redundant**: Skills must NEVER duplicate platform behaviors (e.g. telling an agent how to make an implementation plan). They must exclusively teach **non-native project policies**:
   - Risk classification (when to dispatch a verifier).
   - Verifier dispatch idioms (`TypeName='self'`, test commands).
   - Invariant boundaries (`rslib/` immutability, Same Change Set).
   - Stop gate awareness (how the physical test ratchet works).
3. **Token Efficiency Budget**: A skill's `SKILL.md` must be $\le 60$ lines (~2,500 bytes) to minimize context saturation upon activation.
4. **Single Core Skill over Monolithic Bloat**: For AntiOS v1, a single focused skill (`antios-engineer`) satisfies all operational requirements. We deliberately reject fracturing into 5 micro-skills or building a 2,000-line monolithic framework skill.

---

## 3. The Canonical AntiOS v1 Skill: `antios-engineer`

### Path
`.agents/skills/antios-engineer/SKILL.md`

### Frontmatter Specification
```yaml
---
name: antios-engineer
description: >-
  Standard engineering workflow policy for StudyLab under AntiOS v1 governance.
  Use when planning, implementing, modifying, or verifying features, bug fixes,
  and refactors in the StudyLab codebase.
---
```

### Content Specification & Responsibilities

The skill provides the agent with three critical non-native capabilities:

#### A. Risk Tiering & Maker-Checker Dispatch
- **Low Risk** (typos, markdown documentation, formatting): Solo execution allowed. No fresh subagent required.
- **Medium Risk** (multi-file bug fixes, non-critical features): Parent agent self-verifies via test suite.
- **High Risk** (Reviewer FSM, double SQLite persistence, APKG packaging, security hooks): **MANDATORY MAKER-CHECKER**.
  - Must spawn an independent subagent via `invoke_subagent` using **`TypeName='self'`** (providing shell & test execution).
  - Verifier prompt must specify: clean working tree inspection, explicit test execution, and acceptance criteria verification.

#### B. Boundary Discipline
- Reminds the agent that `rslib/` (Anki core) and `.agents/` (AntiOS hooks) are immutable.
- Requires changes to be delivered in the **Same Change Set** (code and corresponding docs together).

#### C. Stop Gate Mechanics
- Informs the agent that attempting to conclude the task will trigger `stop_gate.py`.
- Explains that the Stop gate executes the project's native test runner (`vitest:once` or `pytest`) via an OS subprocess.
- Advises that if tests fail or the environment is broken, the agent must inspect the returned stderr and resolve the root cause rather than attempting to bypass the gate.

---

## 4. Skill vs Platform Boundary Matrix

| Capability / Instruction | Owned by Platform Planning Mode | Owned by AntiOS `antios-engineer` Skill |
| :--- | :---: | :---: |
| Codebase reconnaissance before editing | **YES** (`## Research`) | NO |
| Drafting `implementation_plan.md` | **YES** (Native Artifact) | NO |
| Halting for user approval | **YES** (Native UI Gate) | NO |
| Authoring `walkthrough.md` | **YES** (Native Artifact) | NO |
| Identifying Task Risk Tier (Low/Med/High) | NO | **YES** |
| Mandating Maker-Checker Subagent | NO | **YES** |
| Ensuring `TypeName='self'` for verifier | NO | **YES** |
| Protecting `rslib/` from blast radius | NO | **YES** |
| Same Change Set documentation rule | NO | **YES** |
| Physical OS Stop gate compliance | NO | **YES** |

---

## 5. Lifecycle Interaction Diagram

```text
User Request
     │
     ▼
[Antigravity Planning Mode] ──► Reads antios-engineer Skill (Assesses Risk Tier)
     │
     ▼
implementation_plan.md authored with Maker-Checker plan (if High Risk)
     │
     ▼
[User Approves Plan]
     │
     ▼
[Execution Phase]
     │  - Agent applies edits
     │  - PreToolUse Hook enforces rslib/ and .agents/ protection
     │
     ▼
[Verification Phase]
     │  - If High Risk: invoke_subagent(TypeName='self', ...) performs fresh review
     │
     ▼
[Task Completion]
     │  - Agent stops
     │  - Stop Hook executes native tests (vitest / pytest)
     ▼
Done
```
