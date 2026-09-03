# Project Lessons & Improvements (`docs/LESSONS.md`)

**Status**: Active Failure Prevention & Validated Patterns  
**Format**: Candidate hypotheses remain provisional until validated across multiple runs.  

## 1. Candidate Improvements

- None currently recorded.

## 2. Durable Lessons

### [L-01] Universal Core Boundary Protection
- **Trigger/Failure**: Subagent or tool attempt to mutate .agents/ or framework/ directly
- **Rule/Action**: PreToolUse hook intercepts and unconditionally denies write actions with PERMISSION_DENIED
- **Authority**: DURABLE
- **Evidence**: Enforced across all phases with 100% pass rate in test_guard.py and test_guard_hardened.py
- **Date**: 2026-09-04
- **Category**: Security & Boundaries
- **Problem Pattern**: Unauthorized write to core governance framework
- **Verified Resolution**: Enforced via deterministic evaluate_tool_call in framework/core/guard.py
- **Scope**: Universal AntiOS Framework
- **When Applies**: All file edits, creations, deletions, and commands modifying core paths
- **When Not Applies**: When modifying project-specific code in target project
- **Recurrence Count**: 5
- **Task IDs**: TASK-PHASE12, TASK-PHASE16, TASK-PHASE18, TASK-PHASE21, TASK-PHASE23

### [L-02] Host Toolchain Environment Mismatch
- **Trigger/Failure**: Configured runner binary missing from global host PATH (e.g. pytest vs uv run pytest)
- **Rule/Action**: Discovery engine checks shutil.which and flags TOOLING_ENVIRONMENT_MISMATCH; adapter configures exact runner invocation
- **Authority**: VALIDATED
- **Evidence**: Validated during pallets/click and StudyLab discovery in Phase 23-24
- **Date**: 2026-09-04
- **Category**: Tooling & Environment
- **Problem Pattern**: Global binary invocation fails in isolated or virtualized environments
- **Verified Resolution**: Discovery engine validates executable PATH; adapter configures explicit command
- **Scope**: Python / Node.js Tooling Execution
- **When Applies**: When discovering test runners and linters in repositories using uv, poetry, or pnpm
- **When Not Applies**: When standard binaries are globally linked in system PATH
- **Recurrence Count**: 2
- **Task IDs**: TASK-CLICK-DISCOVERY, TASK-STUDYLAB-DISCOVERY

### [L-03] Same Change Set Documentation Drift
- **Trigger/Failure**: Task completes functional code changes but neglects updating docs/ACTIVE_CONTEXT.md
- **Rule/Action**: Stop Gate inspects git diff and requires documentation touchpoints alongside code modifications
- **Authority**: DURABLE
- **Evidence**: Enforced by evaluate_changeset and verified across 193 test suite runs
- **Date**: 2026-09-04
- **Category**: Governance & Audit
- **Problem Pattern**: Code changes committed without contemporaneous operational ledger update
- **Verified Resolution**: evaluate_changeset enforces atomic code + docs sync
- **Scope**: Universal AntiOS Engineering Lifecycle
- **When Applies**: In all FEATURE, BUG, REFACTOR, and RELEASE workflows
- **When Not Applies**: In read-only INVESTIGATION workflows
- **Recurrence Count**: 4
- **Task IDs**: TASK-PHASE16, TASK-PHASE19, TASK-PHASE21, TASK-PHASE23
