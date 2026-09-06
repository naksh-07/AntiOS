# AntiOS 2.0 Failure Injection & Recovery Architecture (Phase 97)

## 1. Architectural Purpose

The Failure Injection & Recovery Certification framework (`framework/core/failure_injection.py`) provides systematic adversarial stress testing of AntiOS recovery mechanisms across 16 canonical failure modes.

## 2. The 16 Canonical Failure Modes

1. `TOOL_TIMEOUT`: Tool execution exceeded hard timeout budget.
2. `TOOL_EXIT_NONZERO`: Tool process returned unexpected non-zero exit code.
3. `FILE_NOT_FOUND`: Target source file missing from filesystem.
4. `PERMISSION_DENIED`: Filesystem permission error during tool invocation.
5. `SYNTAX_ERROR_IN_EDIT`: Modification produced parse error or invalid syntax.
6. `LINTER_REGRESSION`: Linter reported new violations after modification.
7. `TEST_REGRESSION`: Previously green unit tests failed on modification.
8. `TRANSIENT_TEST_FLAKE`: Intermittent non-deterministic test failure.
9. `CONTEXT_WINDOW_EXHAUSTION`: Context token budget exceeded ceiling.
10. `STALE_CONTEXT_DRIFT`: Working memory out of sync with disk reality.
11. `WORKER_CRASH`: Subagent process terminated abruptly or unresponsively.
12. `UNAUTHORIZED_DELEGATION`: Worker attempted forbidden subagent delegation.
13. `STATE_FILE_CORRUPTION`: Mission continuity JSON state unparseable or corrupted.
14. `UNCOMMITTED_DIRTY_TREE`: Working tree has uncommitted edits before critical step.
15. `EXTERNAL_INTERRUPT`: Execution interrupted by user or external signal.
16. `CRITICAL_PROJECT_DRIFT`: Incompatible changes detected in project configuration.

## 3. Deterministic Recovery Action Matrix

AntiOS forbids ad-hoc retry loops. Every failure maps deterministically to a canonical recovery action:

| Failure Mode | Default Recovery Action | Secondary Action |
| :--- | :---: | :---: |
| `TOOL_TIMEOUT` | `REPLAN` | `ABORT` |
| `TOOL_EXIT_NONZERO` | `REPLAN` | `ABORT` |
| `FILE_NOT_FOUND` | `REFRESH` | `REPLAN` |
| `PERMISSION_DENIED` | `BLOCK` | `REQUIRE_HUMAN_APPROVAL` |
| `SYNTAX_ERROR_IN_EDIT` | `ROLLBACK` | `REPLAN` |
| `LINTER_REGRESSION` | `REPLAN` | `ROLLBACK` |
| `TEST_REGRESSION` | `ROLLBACK` | `REPLAN` |
| `TRANSIENT_TEST_FLAKE` | `RESUME` | `REPLAN` |
| `CONTEXT_WINDOW_EXHAUSTION` | `REFRESH` | `REPLAN` |
| `STALE_CONTEXT_DRIFT` | `REFRESH` | `REPLAN` |
| `WORKER_CRASH` | `RESUME` | `REPLAN` |
| `UNAUTHORIZED_DELEGATION` | `BLOCK` | `ABORT` |
| `STATE_FILE_CORRUPTION` | `ROLLBACK` | `ABORT` |
| `UNCOMMITTED_DIRTY_TREE` | `ROLLBACK` | `BLOCK` |
| `EXTERNAL_INTERRUPT` | `REQUIRE_HUMAN_APPROVAL` | `ABORT` |
| `CRITICAL_PROJECT_DRIFT` | `BLOCK` | `REQUIRE_HUMAN_APPROVAL` |

## 4. Partial Write Safety & Invariant Protections

Whenever uncommitted modifications are detected after tool or test failures, the harness guarantees either an atomic rollback to the last verified checkpoint or an explicit safe block. Dirty state is never left unaddressed.
Emits a token-bounded `FailureRecoveryCard` ($\le 25$ lines).
