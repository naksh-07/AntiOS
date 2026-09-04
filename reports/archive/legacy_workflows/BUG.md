# Systematic Bug-Fix Workflow (`BUG`)

Deterministic debugging and surgical patch workflow using the 5-step root-cause protocol.

## 1. Entry Conditions
- Bug report, failing automated test, runtime error, or Stop Gate rejection.

## 2. Lifecycle Progression
1. **INTAKE**: Ingest failure symptoms, error logs, and stack traces.
2. **UNDERSTAND**: Identify affected components and ensure protected domain cores are isolated.
3. **INVESTIGATE**: Follow `antios-debug` Step 1:
   - Execute test suite via `run_command` to observe failure directly.
   - Author a minimal reproducing test case before altering any production code.
4. **PLAN**: Follow `antios-debug` Step 2 & 3:
   - Formulate an explicit root-cause hypothesis in chat/plan.
   - Isolate minimal cause; distinguish environment issues from code regressions.
5. **IMPLEMENT**: Follow `antios-debug` Step 4:
   - Apply the smallest possible surgical patch to application layers.
6. **TEST**: Follow `antios-debug` Step 5:
   - Run reproducing test to confirm resolution.
   - Run full project test runner to verify zero regressions.
7. **VERIFY**: For High-Risk modules, dispatch fresh-context Checker via `invoke_subagent(TypeName='self')`.
8. **REVIEW**: Inspect test outputs and verifier JSON verdict.
9. **CONSOLIDATE**: Record root cause and resolution in `docs/ACTIVE_CONTEXT.md`. Verify clean diff.
10. **COMPLETE**: Stop Gate runs full project test suite; exit code 0 confirms completion.

## 3. Recovery Paths
- **Falsified Hypothesis**: Revert code edits via git, record falsified hypothesis in `dead_ends` in `docs/ACTIVE_CONTEXT.md`, and formulate a new hypothesis.
- **Regression Detected**: Roll back patch immediately. Do not stack speculative fixes.
