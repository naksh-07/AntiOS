---
name: antios-engineer
description: >-
  Standard engineering workflow policy for projects under AntiOS v1 governance.
  Use when planning, implementing, modifying, or verifying features, bug fixes,
  and refactors in the AntiOS ecosystem.
---

# AntiOS Engineering Workflow

You are working under **AntiOS v1** governance. Follow this policy for all engineering tasks.

## 1. Safety Boundaries & Immutability
- **Self-Protection**: NEVER edit `.agents/` or `framework/` directly via IDE tools.
- **Upstream Immutability**: NEVER edit domain cores protected in `antios.config.json` (e.g., `rslib/`).
- **Same Change Set**: Code modifications and documentation updates MUST be committed together.

## 2. Risk Tiering & Delegation Matrix
Assess the risk tier before implementing:
- **Low Risk** (typos, markdown documentation, formatting): Solo execution allowed. Local test check; no subagent needed.
- **Medium Risk** (isolated UI fixes, standard feature additions): Primary agent implements and self-verifies with native tests.
- **High Risk** (state machines, persistence/schema, security hooks, packaging): **MANDATORY MAKER-CHECKER**.
  - Dispatch an independent verifier via `invoke_subagent` using `TypeName='self'` (strictly NEVER `TypeName='research'`).
  - Pass task objective, modified files, and test commands.
  - Verifier uses the `antios-verifier` skill and returns a structured JSON verdict.
  - **Shallow Depth Law**: Subagent depth must never exceed 2 (Parent -> Child). Subagents must NEVER spawn children.

## 3. Systematic Debugging
If tests fail or bugs are encountered, follow `antios-debug`: reproduce with a minimal test first, isolate root cause, and apply minimal patches without touching protected cores.

## 4. The Stop Gate Ratchet
Task completion triggers the AntiOS Stop hook, which dynamically discovers and executes native test runners (`vitest:once`, `pytest`) configured in `antios.config.json`.
- The task CANNOT complete unless all physical test processes exit with code 0.
- Ensure working tree cleanliness and update `docs/ACTIVE_CONTEXT.md` (<= 60 lines) before stopping.
