# Behavior-Preserving Refactor Workflow (`REFACTOR`)

Structural code improvements and architectural reorganization with zero external behavior change.

## 1. Entry Conditions
- Identified architectural debt, modularization need, or performance refactor.
- Full project test suite must pass cleanly before starting.

## 2. Lifecycle Progression
1. **INTAKE**: Define refactoring target, scope, and non-negotiable external invariants.
2. **UNDERSTAND**: Map public interface contracts and consumers. Confirm immutable boundaries.
3. **INVESTIGATE**: Run full baseline test suite via `run_command`. Baseline MUST pass (Exit Code 0).
4. **PLAN**: Draft `implementation_plan.md` scoping incremental modifications. Default risk: HIGH.
5. **IMPLEMENT**: Execute refactor in small, atomic steps. Keep public APIs identical.
6. **TEST**: Execute tests after each atomic step to catch unintended breakage immediately.
7. **VERIFY**: Mandatory Maker-Checker dispatch via `invoke_subagent(TypeName='self')` with `antios-verifier`.
8. **REVIEW**: Verify that `git diff` shows only architectural improvements, zero semantic changes.
9. **CONSOLIDATE**: Update architectural documentation in Same Change Set; sync `docs/ACTIVE_CONTEXT.md`.
10. **COMPLETE**: Stop Gate executes full test suite.

## 3. Recovery Paths
- **Behavioral Drift / Test Failure**: Git revert to last clean atomic state. Do not debug refactors by mutating public contracts.
