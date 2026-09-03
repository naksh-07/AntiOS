# Feature Implementation Workflow (`FEATURE`)

Standard end-to-end workflow for designing and delivering new functionality.

## 1. Entry Conditions
- User request or issue detailing a new functional capability.
- Acceptance criteria and expected behavior understood.

## 2. Lifecycle Progression
1. **INTAKE**: Ingest user requirements; identify problem domain.
2. **UNDERSTAND**: Clarify system architecture; confirm immutable boundaries from `antios.config.json`.
3. **INVESTIGATE**: Inspect existing codebase patterns, extension points, and test conventions.
4. **PLAN**: Draft `implementation_plan.md` in Antigravity Planning Mode. Evaluate Risk Tier (Low/Medium/High). If High Risk, include Maker-Checker verifier dispatch plan. Pause for user approval.
5. **IMPLEMENT**: Apply guarded modifications (`write_to_file`, `replace_file_content`). Adhere to **Same Change Set** (synchronize documentation and tests with code).
6. **TEST**: Primary agent executes native test suite locally via `run_command`.
7. **VERIFY**: If High Risk, dispatch an independent fresh-context Checker via `invoke_subagent(TypeName='self')` with the `antios-verifier` skill.
8. **REVIEW**: Maker inspects the structured JSON verdict (`verdict.py`). Remediate any issues before proceeding.
9. **CONSOLIDATE**: Verify working tree cleanliness (`git diff --check`). Update `docs/ACTIVE_CONTEXT.md` (<= 60 lines).
10. **COMPLETE**: Signal task completion. AntiOS Stop Gate intercepts and executes native test suites with exit code 0.

## 3. Recovery Paths
- **Test Failure**: Transition to `antios-debug`. Isolate root cause before modifying further code.
- **Verifier Rejection**: Return to IMPLEMENT stage to resolve issues identified in JSON verdict.
- **Interruption**: Save partial progress to `docs/ACTIVE_CONTEXT.md` checklist; mark status INTERRUPTED.
