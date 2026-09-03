# AntiOS Failure Taxonomy

This document establishes the comprehensive failure classification system for AntiOS, categorizing all vulnerabilities, friction points, and edge cases discovered during Phase 9 adversarial stress testing.

---

## Classification Taxonomy

- **TYPE A**: Preventable deterministically (Hard barrier via code/hook/compiler).
- **TYPE B**: Detectable deterministically (Auditable via deterministic exit code, git diff, or static analysis).
- **TYPE C**: Best handled by Skill/Subagent reasoning (Cognitive evaluation, Maker-Checker review, natural language comprehension).
- **TYPE D**: Requires human decision (Ambiguous intent, environment failure, destructive operations, credentials).
- **TYPE E**: Platform limitation (Inherent boundary of Antigravity engine, OS shell, or tool API).
- **TYPE F**: Currently UNKNOWN (Requires further empirical isolation).

---

## Detailed Failure Matrix & Architecture Guidance

| Failure ID | Description | Taxonomy Type | Mechanism & Root Cause | Architectural Guidance / Remediation |
| :--- | :--- | :---: | :--- | :--- |
| **FAIL-01** | **Direct Upstream Core Mutation** (`rslib/` write) | **TYPE A** | Agent attempts to edit upstream Anki code via `write_to_file` or `replace_file_content`. | **Prevented Deterministically**: Handled by `pre_tool_guard.py` using canonical path check. Must remain an immutable Type A hook invariant. |
| **FAIL-02** | **Windows 8.3 Short Name Traversal** (`RSLIB~1`) | **TYPE A** | `os.path.realpath()` does not expand Windows 8.3 short names without active win32 API resolution. | **Preventable Deterministically**: Fix `pre_tool_guard.py` using `GetLongPathName` or `pathlib.Path.resolve()` on Windows. |
| **FAIL-03** | **Parent Path Substring Collision** (False Positive) | **TYPE A** | `if "framework" in parts:` blocks valid edits if any parent directory in the absolute path is named `framework`. | **Preventable Deterministically**: Replace segment search with canonical prefix comparison (`os.path.commonpath([target, framework_dir]) == framework_dir`). |
| **FAIL-04** | **Fail-Open Exception Handling** in PreToolUse | **TYPE A** | Line 43 of `pre_tool_guard.py` catches all exceptions and outputs `{"decision": "allow"}`. | **Preventable Deterministically**: Replace with strict fail-closed: unhandled hook exceptions must return `{"decision": "deny"}`. |
| **FAIL-05** | **Empty Workspace Bypass** | **TYPE A** | Line 14 of `pre_tool_guard.py` and Line 12 of `stop_gate.py` return `allow` if `workspacePaths` is missing/empty. | **Preventable Deterministically**: Fail closed when workspace path context is missing. |
| **FAIL-06** | **Unprotected Hook Configuration** (`.agents/hooks.json`) | **TYPE A** | `pre_tool_guard.py` only protects `framework/` and `rslib/`; `.agents/hooks.json` can be edited or deleted. | **Preventable Deterministically**: Add `.agents` and `hooks.json` to canonical protected paths in `pre_tool_guard.py`. |
| **FAIL-07** | **Trivial Test Fabrication** (`verify_task.py`) | **TYPE A / B** | In repos without native test frameworks, agent can create dummy `verify_task.py` with `sys.exit(0)`. | **Detectable Deterministically**: Require test suites to be pre-registered or disallow creating `verify_task.py` within the same change set as code fixes. |
| **FAIL-08** | **Application Unit/Integration Test Failure** | **TYPE B** | Application code changes break test assertions. | **Detectable Deterministically**: Handled by `stop_gate.py` reading native exit codes from `vitest`, `pytest`, `cargo test`. |
| **FAIL-09** | **Untested Code Modifications Post-Verification** | **TYPE B** | Agent runs tests, modifies untested file, then declares Done. | **Detectable Deterministically**: Check `git status` / file modification timestamps against last test run timestamp before allowing stop. |
| **FAIL-10** | **Dirty Worktree Contamination** | **TYPE B** | Pre-existing dirty files in sandbox get clobbered or erroneously committed by agent. | **Detectable Deterministically**: Add pre-task git dirty-state baseline check. Enforce isolated git branches or worktrees. |
| **FAIL-11** | **Syntactic Reference Drift in Documentation** | **TYPE B** | Markdown documentation references renamed functions, deleted files, or dead anchors. | **Detectable Deterministically**: Handled by Layer-1 syntactic link/symbol checker script (Phase 6 Idea 07). |
| **FAIL-12** | **Semantic Documentation Drift** | **TYPE C** | Code functionality changes, but docs still describe old behavior; both syntax and tests pass. | **Skill / Subagent Reasoning**: Deterministic AST/NLI matching is flaky and expensive; best delegated to independent Maker-Checker subagent review. |
| **FAIL-13** | **Hallucinated Subagent Certification** | **TYPE C / B** | Verifier subagent claims tests passed without running them or due to prompt framing bias. | **Hybrid**: Handled by Maker-Checker prompt discipline (Type C) with deterministic backstop by `stop_gate.py` executing actual process (Type B). |
| **FAIL-14** | **Subagent Crash or Timeout** | **TYPE C** | Subagent runs out of tokens, crashes, or hangs. | **Skill / Subagent Reasoning**: Handled by orchestrator escalation state machine (Retry -> Reassign -> Replace -> Takeover). |
| **FAIL-15** | **Stale Active Context / Amnesia** | **TYPE C** | Interrupted session loses memory; manual `ACTIVE_CONTEXT.md` was not updated during previous tasks. | **Skill / Subagent Reasoning**: Handled by explicit task lifecycle skill protocols (RPAC Consolidate step). |
| **FAIL-16** | **Bad Domain Assumption in Non-Protected Path** | **TYPE C** | Agent assumes card flip logic is in `ts/wrong_module.ts` instead of `ts/reviewer/index.ts`. | **Skill / Subagent Reasoning**: Handled by Reconnaissance phase in skills (`studylab-task-runner`) and compiler feedback. |
| **FAIL-17** | **Missing Environment Runtime** (e.g. broken yarn/node) | **TYPE D** | Native test runner cannot execute because ambient tools (`yarn.bat`, extracted node binaries) are missing. | **Requires Human Decision / Intervention**: The agent cannot magically repair external environment prerequisites outside its sandbox permissions. Hook must classify as `ENVIRONMENT_UNAVAILABLE` and prompt user. |
| **FAIL-18** | **Destructive Git Operations on Sandbox** | **TYPE D** | Running `git reset --hard` or `git clean -fd` risking loss of uncommitted work. | **Requires Human Decision**: Must trigger human confirmation gate (e.g., accidental-data-loss-prevention skill). |
| **FAIL-19** | **Hook Bypass via Shell Redirection** (`run_command`) | **TYPE E** | Agent uses PowerShell/bash (`Set-Content`, `echo > rslib/core.rs`, `git apply`) to modify protected files. | **Platform Limitation**: Antigravity hooks intercept tool calls, not arbitrary sub-processes spawned inside shell commands. True boundary protection requires OS-level file permissions (read-only filesystem mount) or containerization. |
| **FAIL-20** | **Process Execution in Python without `python.exe` in PATH** | **TYPE E** | Windows environments where Python is accessible only via `uv run` or specific venv path, but hook calls `python`. | **Platform Limitation / Configuration**: Hook runner executes configured CLI string. Must use environment-agnostic entry points or virtualenv relative paths. |

---

## Architectural Principles Derived from Taxonomy

1. **Do not attempt to solve Type E (Platform Limitations) with Type A hooks**:
   Trying to parse arbitrary PowerShell/bash scripts inside a regex hook to catch shell bypasses is an anti-pattern. Document the platform boundary clearly: AntiOS guards IDE tool calls, while OS/container virtualization guards the filesystem.
2. **Do not attempt to solve Type C (Semantic Understanding) with Type A hooks**:
   Deterministic AST/regex checkers cannot evaluate whether documentation "accurately captures design intent." That is what the Maker-Checker subagent is for.
3. **Never let Type A hooks fail open into Type F (Unknown)**:
   Every exception in a security or verification hook must fail closed (`deny` or `continue`), preventing silent bypass.
