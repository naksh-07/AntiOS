# Documentation & Specification Workflow (`DOCUMENTATION`)

Authoring, auditing, and synchronizing documentation, specifications, and architectural records.

## 1. Entry Conditions
- Request to document new architecture, update existing guides, or fix doc drift.

## 2. Lifecycle Progression
1. **INTAKE**: Identify documentation targets and audience.
2. **UNDERSTAND**: Verify code reality before writing. Never document imagined behavior.
3. **INVESTIGATE**: Audit existing documentation for drift, broken links, or stale patterns.
4. **PLAN**: Outline documentation changes adhering strictly to token budgets (e.g. skills <= 60 lines, context <= 60 lines).
5. **IMPLEMENT**: Edit markdown specifications and documentation.
6. **TEST**: Validate markdown syntax, link validity, and header hierarchies.
7. **VERIFY**: Solo verification (Low Risk). Confirm Same Change Set rules.
8. **REVIEW**: Inspect `git diff` to guarantee zero accidental modifications to application code.
9. **CONSOLIDATE**: Update `docs/ACTIVE_CONTEXT.md` with updated document map.
10. **COMPLETE**: Stop Gate validates cleanliness and passing test suite.

## 3. Recovery Paths
- **Accidental Code Edits**: Revert code changes immediately; keep documentation changes isolated.
