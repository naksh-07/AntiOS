# Read-Only Investigation Workflow (`INVESTIGATION`)

Architectural spikes, feasibility research, and forensic codebase analysis without production code modification.

## 1. Entry Conditions
- Technical spike question, performance analysis, or architectural trade-off evaluation.

## 2. Lifecycle Progression
1. **INTAKE**: Clarify research question and acceptance criteria.
2. **UNDERSTAND**: Define investigation boundaries. Confirm strictly read-only execution.
3. **INVESTIGATE**: Use search tools, static analysis, log examination, or read-only test runs. If scratch scripts are needed, store strictly in brain scratch directory.
4. **PLAN**: Structure hypotheses and decompose into orthogonal search queries.
5. **IMPLEMENT**: None. Production code is NOT modified.
6. **TEST**: Validate hypotheses against actual code execution or test outputs.
7. **VERIFY**: Audit claims against physical citations and command outputs.
8. **REVIEW**: Reconcile contradictory evidence; evaluate caveats and edge cases.
9. **CONSOLIDATE**: Author structured report artifact. Update `docs/ACTIVE_CONTEXT.md`.
10. **COMPLETE**: Deliver findings to user or parent orchestrator.

## 3. Recovery Paths
- **Inconclusive Findings**: Document tested hypotheses in `dead_ends` and report bounded uncertainty.
