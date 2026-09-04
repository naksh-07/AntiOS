# AntiOS Implementation vs Documentation Matrix (`IMPLEMENTATION_REALITY_MATRIX.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Scope**: All documented architectural capabilities across Phase 6–9 compared against actual code and runtime execution evidence.  
**Classification Values**: `MATCH` | `PARTIAL` | `CONTRADICTION` | `MISSING` | `UNKNOWN`

---

## 1. Master Implementation Reality Matrix

| # | Capability | Documentation Says | Implementation Does | Runtime Evidence | Status |
| :-: | :--- | :--- | :--- | :--- | :---: |
| **1** | **Upstream Blast Radius Containment** *(IDE Tools)* | Modifying upstream Anki core (`rslib/`) is strictly forbidden and deterministically blocked (`AGENTS.md:L5-7`, `ARCHITECTURE_PROPOSAL.md:L41-43`). | `pre_tool_guard.py:35-40` normalizes path with `realpath` and `normcase`, checks `if "rslib" in parts`, and returns `decision: deny`. | Injected payload `{"TargetFile": "rslib/dummy.rs"}` returned `{"decision": "deny"}`. | **MATCH** |
| **2** | **Upstream Protection via Shell** | *"If an agent tries to execute a dangerous shell command, the hook exits with non-zero status..."* (`DECISION_REGISTER.md:L41`). | `hooks.json:L5` matcher only targets `write_to_file\|replace_file_content`. `run_command` is never intercepted. | Shell command `powershell -Command "Set-Content -Path rslib/dummy.rs -Value 'test'"` mutates `rslib/` with zero resistance. | **CONTRADICTION** |
| **3** | **Hook Script Self-Protection** | Modifying framework code is strictly forbidden; hooks protect themselves (`PHASE_8_REPORT.md:L14`, `ARCHITECTURE_PROPOSAL.md:L43`). | `pre_tool_guard.py:28-33` checks `if "framework" in parts: deny`. Blocks direct IDE edits to files inside `framework/`. | Tool edit to `framework/scripts/hooks/pre_tool_guard.py` returned `{"decision": "deny"}`. | **MATCH** |
| **4** | **Hook Configuration Protection** | System prevents tampering with hook definitions (`SECURITY_HARDENING_REPORT.md`). | `pre_tool_guard.py` only protects `framework` and `rslib`. `.agents/hooks.json` is not in the protected list. | Tool edit targeting `.agents/hooks.json` returned `{"decision": "allow"}`. Hook can be deleted or detached. | **CONTRADICTION** |
| **5** | **Path Canonicalization: Directory Traversal** | System prevents directory traversal (`../rslib`) and casing bypasses (`RSLIB/`) (`PHASE_8_REPORT.md:L13`). | `os.path.realpath` and `os.path.normcase` successfully canonicalize relative traversal and case variations. | Test harness: `ts/../rslib/dummy.rs` $\to$ `deny`; `RSLIB/dummy.rs` $\to$ `deny`; `rslib\\bar.rs` $\to$ `deny`. | **MATCH** |
| **6** | **Path Canonicalization: Windows 8.3 Names** | Path resolution expands all Windows aliases and short names (`PHASE_8_REPORT.md:L13`). | `os.path.realpath` resolves lexically for non-existent paths on Windows without calling Win32 API `GetLongPathName`. | Test harness: `TargetFile: "RSLIB~1/dummy.rs"` returned `{"decision": "allow"}`. | **CONTRADICTION** |
| **7** | **Ancestor Directory Isolation** | Hook protects AntiOS framework directory without false positives on legitimate project code (`PHASE_8_REPORT.md:L14`). | Line 28 uses `if "framework" in parts: deny`. Tests every path segment in absolute path. | Test harness: Path `C:\Users\Suraj\framework\AntiOs\ts\card.ts` returned `{"decision": "deny"}`. 100% false positive. | **CONTRADICTION** |
| **8** | **Hook Exception Handling (PreToolUse)** | Security hooks fail closed to guarantee safety boundaries (`FRAMEWORK_REQUIREMENTS.md:SR1`). | `pre_tool_guard.py:43-44` catches all Python exceptions and outputs `{"decision": "allow"}`. | Injected integer `TargetFile: 12345` $\to$ caught by `except Exception` $\to$ returned `{"decision": "allow"}`. | **CONTRADICTION** |
| **9** | **Missing Workspace Payload Handling** | Hooks gracefully handle missing payload context (`PHASE_8_REPORT.md`). | Line 14 of `pre_tool_guard.py` and Line 12 of `stop_gate.py` return `{"decision": "allow"}` if `workspacePaths` is empty. | Test harness: Payload `{"workspacePaths": []}` caused both hooks to return `allow` without inspection. | **CONTRADICTION** |
| **10** | **Test Ratchet (Process Execution)** | Task cannot be marked completed if tests fail; executes OS process (`AGENTS.md:L21-23`, `stop_gate.py`). | `stop_gate.py` runs `npm run vitest:once` or `uv run pytest`, observes returncode, and blocks stop on non-zero. | Test harness: Exit code 1 returned `{"decision": "continue", "reason": "Verification failed!..."}`. | **MATCH** |
| **11** | **Dynamic Test Discovery** | Stop gate dynamically discovers native project test runners (`package.json`, `pyproject.toml`) (`PHASE_8_REPORT.md:L15`). | Checks `package.json` for `vitest:once` and `pyproject.toml` for `pytest` in `repo_root`. | Successfully executed `npm run vitest:once` when `package.json` present. | **MATCH** |
| **12** | **Test Script Forgery Resistance** | Prevents agent from subverting test verification (`VERIFICATION_HARDENING_REPORT.md`). | Lines 58–69 in `stop_gate.py` execute any `verify_task.py` found in the root directory and accept returncode 0. | Test harness: Created `verify_task.py` with `sys.exit(0)` $\to$ `stop_gate.py` allowed stop with 0 unit tests run. | **CONTRADICTION** |
| **13** | **Environment Failure Diagnosis** | System clearly diagnoses why verification failed (`RECOVERY_TEST_REPORT.md`). | Any non-zero exit code (including missing `yarn.cmd` or broken node binary) is reported as `"TypeScript tests did not pass"`. | Broken runtime binary returned `continue`, outputting `"TypeScript tests did not pass"`, trapping agent in loop. | **PARTIAL** |
| **14** | **Same Change Set Synchronization** | Code changes and corresponding documentation updates must be committed together (`AGENTS.md:L13-14`, `FR4`). | `stop_gate.py` only checks test runner return code; does not inspect `git diff`, `git status`, or documentation files. | Modified TypeScript code without touching docs $\to$ `stop_gate.py` allowed completion without warning. | **MISSING** |
| **15** | **Dirty Worktree Protection** | Experimental execution is isolated; prevents clobbering pre-existing work (`AGENTS.md:L9-11`). | Zero git status tracking, zero pre-flight dirty checking, zero automated worktree isolation. | Pre-existing modified files in `sandbox/StudyLab` were unmonitored; agent git commands clobbered work. | **MISSING** |
| **16** | **Progressive Skill Disclosure** | Domain procedures are codified as lazy-loaded Antigravity skills (`FRAMEWORK_REQUIREMENTS.md:FR2`). | Skill is placed in `framework/.agents/skills/`. Antigravity only discovers `<workspace_root>/.agents/skills`. | Platform `<skills>` block does not list `studylab-task-runner`. In root workspace, the skill is undiscoverable. | **CONTRADICTION** |
| **17** | **Bounded Memory Bank** | Durable, file-backed project state externalized on disk prevents amnesia (`ARCHITECTURE_PROPOSAL.md:L36-39`). | `docs/ACTIVE_CONTEXT.md` was created, but was never updated after Phase 6. Frozen at Prototype v0.1 setup. | `docs/ACTIVE_CONTEXT.md` shows `- [ ] Implement safety hooks`. Resuming agents suffer stale-state amnesia. | **PARTIAL** |
| **18** | **Maker-Checker Subagent Verification** | Fresh-context verifier subagent audits primary agent's changes (`AGENTS.md:L16-19`, `VR1`). | Uses `invoke_subagent`. However, `SKILL.md` recommends `TypeName='research'`, which has no `run_command` tool! | Subagent with `research` cannot execute tests. Subagent with `self` can, but dialogue claims require Stop gate backstop. | **PARTIAL** |
| **19** | **StudySourceCore Domain MCP** | Connects agents to `studysource-core` MCP for deterministic validation (`FRAMEWORK_REQUIREMENTS.md:FR3`). | Disproved and rejected in Phase 8 (`DECISION_REGISTER.md:L60`). User directive strictly forbids touching it. | Tool is out of scope and unused by AntiOS. | **CONTRADICTION** |
| **20** | **Layer-1 Syntactic Doc Drift Checker** | Deterministic script verifies file and symbol references physically exist (`DECISION_REGISTER.md:L45-52`). | Proposed in Phase 6. Never authored, committed, or integrated into `stop_gate.py`. | Zero drift checking code exists in `framework/` or `sandbox/`. | **MISSING** |
| **21** | **Dead-End Logging** | Failed hypotheses logged to prevent repeating failed approaches (`FRAMEWORK_REQUIREMENTS.md:RR1`). | `evidence/` directory is empty. No automated dead-end logging mechanism exists. | `AntiOs/evidence/` contains 0 bytes. Completely reliant on manual agent memory. | **MISSING** |
| **22** | **Cross-Platform Hook Command Runner** | Unified Python hook runner across OS environments (`FRAMEWORK_REQUIREMENTS.md:MR1`). | `hooks.json` uses raw string `"command": "python ..."`. Fails on Windows systems without `python` alias. | PowerShell check: `python` not found; only `python3.11.exe` exists in `~/.local/bin`. | **PARTIAL** |

---

## 2. Summary Scorecard

```text
┌────────────────────────────────────────────────────────┐
│ TOTAL CAPABILITIES AUDITED: 22                         │
├──────────────────────────────────┬─────────────────────┤
│ Status                           │ Count               │
├──────────────────────────────────┼─────────────────────┤
│ MATCH (Verified Ground Truth)    │ 5 (22.7%)           │
│ PARTIAL (Partially Implemented)  │ 4 (18.2%)           │
│ CONTRADICTION (Spec vs Reality)  │ 8 (36.4%)           │
│ MISSING (Unimplemented Claim)    │ 5 (22.7%)           │
│ UNKNOWN                          │ 0 (0.0%)            │
└──────────────────────────────────┴─────────────────────┘
```

**Key Takeaway**: Only **22.7%** of documented capabilities match reality. **59.1%** of documented capabilities are either in direct contradiction with the code (36.4%) or completely missing from the implementation (22.7%).
