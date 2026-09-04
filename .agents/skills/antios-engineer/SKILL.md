---
name: antios-engineer
description: >-
  Universal engineering workflow policy for projects under AntiOS governance.
  Use when planning, implementing, modifying, or verifying features, bug fixes,
  refactors, and maintenance tasks across any software stack.
---

# AntiOS Universal Engineering Policy

You operate under **AntiOS Core** governance. Follow this policy for all engineering tasks.

## 1. Safety Boundaries & Immutability
- **Self-Protection**: NEVER edit `.agents/` or `framework/` directly via IDE tools.
- **Upstream Immutability**: NEVER edit domain cores declared in `protected_domain_paths` in `antios.config.json`.
- **Same Change Set**: Code modifications and documentation updates MUST be committed together.

## 2. Risk Tiering & Delegation Matrix
Assess the risk tier before implementing:
- **Low Risk** (typos, markdown documentation, formatting): Solo execution allowed. Local test check; no subagent needed.
- **Medium Risk** (isolated UI fixes, standard feature additions): Primary agent implements and self-verifies with native tests.
- **High Risk** (state machines, persistence/schema, security hooks, packaging): **MANDATORY MAKER-CHECKER**.
  - Dispatch an independent verifier via `invoke_subagent` using `TypeName='self'` (strictly NEVER `TypeName='research'`).
  - Pass minimal context: objective, modified files, test commands, target member (via `prepare_checker_context`).
  - Verifier uses the `antios-verifier` skill and returns a structured JSON verdict.
  - **Shallow Depth Law**: Subagent depth must never exceed 2 (Parent -> Child). Subagents must NEVER spawn children.

## 3. The 8-Stage Engineering Lifecycle
Always proceed through:
`UNDERSTAND -> LOCATE -> PLAN -> ACT -> TEST -> VERIFY -> REMEMBER -> RECOVER`.
- **LOCATE FIRST**: Before exploring files or writing plans, run `python framework/scripts/tools/navigate_repo.py --query "<intent>"` to resolve the owning subsystem, entrypoints, invariants, and covering tests.
- Standard workflows (`FEATURE`, `BUG`, `REFACTOR`, `INVESTIGATION`, `DOCUMENTATION`, `RELEASE`) govern the operational sequence. Never guess file locations.

## 4. The Stop Gate Ratchet
Task completion triggers the AntiOS Stop hook, which dynamically discovers and executes configured or manifest-detected test runners.
- Member-scoped filtering applies for monorepos (executes member runners unless broader blast radius or RELEASE/REFACTOR).
- The task CANNOT complete unless all physical test processes exit with code 0.
- Ensure working tree cleanliness and update `docs/ACTIVE_CONTEXT.md` (<= 60 lines) before stopping.
