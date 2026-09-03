# AntiOS Hook Forensic Audit (`HOOK_FORENSIC_AUDIT.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Scope**: All AntiOS platform hooks (`PreToolUse`, `Stop`) registered in `framework/.agents/hooks.json` and implemented in `framework/scripts/hooks/`.  
**Empirical Basis**: Runtime testing via Python test harnesses (`test_pre_tool_guard_forensics.py`, `test_stop_gate_forensics.py`).

---

## 1. Architectural Model of AntiOS Hooks

AntiOS implements hook-based policy enforcement by leveraging Antigravity's `.agents/hooks.json` configuration.

```text
Antigravity Platform Engine
       │
       ├── [Tool Call: write_to_file / replace_file_content]
       │       │
       │       ▼ (PreToolUse Hook)
       │   python ./scripts/hooks/pre_tool_guard.py
       │       ├── Stdin: JSON Payload (toolCall, workspacePaths)
       │       └── Stdout: JSON Decision (allow / deny)
       │
       └── [Agent Task Completion Attempt]
               │
               ▼ (Stop Hook)
           python ./scripts/hooks/stop_gate.py
               ├── Stdin: JSON Payload (workspacePaths)
               └── Stdout: JSON Decision (allow / continue)
```

---

## 2. Comprehensive Hook-by-Hook Audit

### A. PreToolUse Hook: `pre_tool_guard.py`

#### 1. Registration & Triggers
- **File**: `framework/scripts/hooks/pre_tool_guard.py` (Mirror: `sandbox/StudyLab_Treatment/scripts/hooks/pre_tool_guard.py`)
- **Hook Event**: `PreToolUse`
- **Tool Matcher**: `write_to_file|replace_file_content`
- **Invocation Command**: `python ./scripts/hooks/pre_tool_guard.py`
- **Unintercepted Tools**: `run_command` (PowerShell/cmd), file creation/deletion via bash scripts, git operations, browser tools.

#### 2. Input & Output Schemas
- **Input Schema (via `sys.stdin`)**:
  ```json
  {
    "toolCall": {
      "name": "write_to_file",
      "args": {
        "TargetFile": "string",
        "CodeContent": "string"
      }
    },
    "workspacePaths": ["string"]
  }
  ```
- **Output Schema (via `sys.stdout`)**:
  ```json
  {
    "decision": "allow" | "deny",
    "reason": "string (optional on allow, mandatory on deny)"
  }
  ```

#### 3. Decision Logic
1. Parses JSON from `sys.stdin`.
2. Extracts `target_file = args.get("TargetFile", "")` and `workspace_paths = input_data.get("workspacePaths", [])`.
3. If either `target_file` or `workspace_paths` is falsy, immediately outputs `{"decision": "allow"}`.
4. Normalizes path: `os.path.normcase(os.path.abspath(os.path.realpath(target_file)))`.
5. Splits path by `os.sep` into `parts`.
6. Checks:
   - `if "framework" in parts: deny` (Intended: Hook Self-Protection).
   - `if "rslib" in parts: deny` (Intended: Upstream Immutability).
7. Defaults to `{"decision": "allow"}`.

#### 4. Empirical Vulnerability & Edge Case Matrix

| Attack / Edge Case | Injected Payload | Observed Hook Output | Forensic Classification | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Direct Core Mutation** | `TargetFile: "rslib/dummy.rs"` | `{"decision": "deny", "reason": "...Modifying rslib/ is strictly forbidden..."}` | Intended Protection | **PASS** |
| **Path Traversal `../`** | `TargetFile: "ts/../rslib/dummy.rs"` | `{"decision": "deny"}` | Canonicalized via `realpath` | **PASS** |
| **Case Variation** | `TargetFile: "RSLIB/dummy.rs"` | `{"decision": "deny"}` | Canonicalized via `normcase` | **PASS** |
| **Mixed Separators** | `TargetFile: "rslib\\foo\\bar.rs"` | `{"decision": "deny"}` | Canonicalized via `normcase` | **PASS** |
| **Nonexistent Core Path** | `TargetFile: "rslib/nonexistent.rs"` | `{"decision": "deny"}` | Lexical path includes `rslib` | **PASS** |
| **Direct Framework Edit** | `TargetFile: "framework/scripts/hooks/pre_tool_guard.py"` | `{"decision": "deny"}` | `framework` in parts | **PASS** |
| **Windows 8.3 Short Name** | `TargetFile: "RSLIB~1/dummy.rs"` | `{"decision": "allow"}` | `realpath` fails to expand 8.3 name without active Win32 lookup | **CRITICAL FAIL** |
| **Parent Folder Collision** | `TargetFile: "C:\Users\Suraj\framework\AntiOs\ts\app.ts"` | `{"decision": "deny"}` | Any ancestor path segment named `framework` blocks ALL edits | **CATASTROPHIC FALSE POSITIVE** |
| **Config Tampering** | `TargetFile: ".agents/hooks.json"` | `{"decision": "allow"}` | `.agents` is not in protected list; hook can be deleted | **CRITICAL FAIL** |
| **Empty Payload** | `{}` | `{"decision": "allow"}` | Line 14 allows when `not target_file` | **CRITICAL FAIL-OPEN** |
| **Empty Workspace Path** | `workspacePaths: []` | `{"decision": "allow"}` | Line 14 allows when `not workspace_paths` | **CRITICAL FAIL-OPEN** |
| **Malformed Type Exception** | `TargetFile: 12345` (int) | `{"decision": "allow", "reason": "Hook error: expected str..."}` | Line 43 catches `TypeError` and allows | **CRITICAL FAIL-OPEN** |
| **Timeout Handling** | N/A | No timeout configured | Pure CPU calculation (no subprocess) | **PASS** |

---

### B. Stop Gate Hook: `stop_gate.py`

#### 1. Registration & Triggers
- **File**: `framework/scripts/hooks/stop_gate.py` (Mirror: `sandbox/StudyLab_Treatment/scripts/hooks/stop_gate.py`)
- **Hook Event**: `Stop`
- **Invocation Command**: `python ./scripts/hooks/stop_gate.py`
- **Trigger**: Called automatically by Antigravity whenever an agent attempts to finish its turn or conclude task execution without issuing further tool calls.

#### 2. Input & Output Schemas
- **Input Schema (via `sys.stdin`)**:
  ```json
  {
    "workspacePaths": ["string"]
  }
  ```
- **Output Schema (via `sys.stdout`)**:
  ```json
  {
    "decision": "allow" | "continue",
    "reason": "string (optional on allow, mandatory on continue)"
  }
  ```

#### 3. Decision Logic
1. Parses JSON from `sys.stdin`.
2. Extracts `workspace_paths = input_data.get("workspacePaths", [])`.
3. If `not workspace_paths`, outputs `{"decision": "allow"}` (Premature pass).
4. Inspects `repo_root = workspace_paths[0]`:
   - Checks for `package.json`: If `"vitest:once"` in `scripts`, executes `npm run vitest:once` (or `yarn` if `yarn.lock` exists).
   - Checks for `pyproject.toml`: Executes `uv run pytest`.
   - Fallback check: If `verify_task.py` exists, executes `python verify_task.py`.
5. If no test configuration is found: outputs `{"decision": "continue", "reason": "No tests were found!..."}`.
6. Evaluates process returncode:
   - If returncode $\neq 0$: outputs `{"decision": "continue", "reason": "Verification failed!..."}` with stdout/stderr.
   - If returncode $== 0$: outputs `{"decision": "allow"}`.
7. Exception block: Outputs `{"decision": "continue", "reason": "Internal error during verification!..."}` (Fail-Closed).

#### 4. Empirical Vulnerability & Edge Case Matrix

| Attack / Edge Case | Injected Workspace Condition | Observed Hook Output | Forensic Classification | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Broken Test Assertions** | Real test exits code `1` | `{"decision": "continue", "reason": "Verification failed!..."}` | Test failure detected | **PASS** |
| **Conversational LLM Claim** | Agent outputs "All tests passed" | Hook executes actual OS subprocess, ignores chat text | Immune to text claims | **PASS** |
| **Script Crash / Exception** | Malformed JSON input | `{"decision": "continue", "reason": "Internal error..."}` | Fails closed on exception | **PASS** |
| **No Tests in Workspace** | Empty repository | `{"decision": "continue", "reason": "No tests were found!..."}` | Blocks unverified stop | **PASS** |
| **Empty Workspace Path** | `workspacePaths: []` | `{"decision": "allow"}` | Line 12 allows stop immediately | **CRITICAL FAIL-OPEN** |
| **Forged `verify_task.py`** | Script with `sys.exit(0)` | `{"decision": "allow"}` | Executes arbitrary script; trivial pass forgery | **CRITICAL SUBVERSION** |
| **Tampered `package.json`** | `"vitest:once": "exit 0"` | `{"decision": "allow"}` | Subprocess returns 0; allowed without running tests | **CRITICAL SUBVERSION** |
| **Missing Executable Runtime** | `yarn` or node wrapper broken | `{"decision": "continue", "reason": "TypeScript tests did not pass. Output: The system cannot find..."}` | Misclassifies environment crash as broken code | **ENVIRONMENT TRAP (Score 3)** |
| **Timeout Handling** | Test runner deadlocks | Hangs indefinitely | `subprocess.run()` has NO `timeout` parameter | **HANG VULNERABILITY** |
| **Post-Verification Mutation** | Change file outside test glob | `{"decision": "allow"}` | Does not check `git status` or file diffs | **RATCHET EXPIRY** |

---

## 3. Comparative Summary: Fail-Open vs Fail-Closed

```text
┌──────────────────────────────────────┬──────────────────────────────────────┐
│        pre_tool_guard.py             │            stop_gate.py              │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Missing workspacePaths: ALLOW        │ Missing workspacePaths: ALLOW        │
│ Missing TargetFile:     ALLOW        │ No tests found:         CONTINUE     │
│ Python Exception:       ALLOW        │ Python Exception:       CONTINUE     │
│                                      │                                      │
│ VERDICT: CATASTROPHIC FAIL-OPEN      │ VERDICT: MIXED (FAIL-CLOSED EXCEPT   │
│                                      │          ON MISSING WORKSPACE)       │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 4. Subprocess & Platform Runtime Gap

1. **Subprocess Spawning**:
   - `stop_gate.py` uses `subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, shell=(os.name == 'nt'))`.
   - The use of `shell=True` on Windows is required for batch files (`npm.cmd`, `yarn.cmd`), but introduces shell injection risks if arguments contain untrusted characters.
   - **No Timeout Bound**: No `timeout=N` is specified. If a test runner opens an interactive prompt (e.g. Vitest watch mode instead of run mode), the hook process hangs forever.
2. **Interpreter Invocation**:
   - `hooks.json` registers `"command": "python ./scripts/hooks/..."`.
   - On standard developer machines where `python` is not in system PATH (only `python3.11` or `uv`), Antigravity cannot spawn the hook script. Hook commands must use cross-platform launcher idioms or environment variables.
