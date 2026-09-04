# AntiOS Forensic Findings Log (`ANTIOS_FORENSIC_FINDINGS.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Severity Scheme**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFO`  
**Total Findings**: 16

---

## Finding Summary Scorecard

```text
┌────────────────────────────────────────────────────────┐
│ TOTAL FINDINGS: 16                                     │
├──────────────────────────────────┬─────────────────────┤
│ Severity                         │ Count               │
├──────────────────────────────────┼─────────────────────┤
│ CRITICAL                         │ 3                   │
│ HIGH                             │ 3                   │
│ MEDIUM                           │ 6                   │
│ LOW                              │ 2                   │
│ INFO                             │ 2                   │
└──────────────────────────────────┴─────────────────────┘
```

---

## Detailed Forensic Findings

### FINDING-01: `pre_tool_guard.py` Fails Open on Unhandled Exceptions
- **ID**: `FND-01`
- **Severity**: **CRITICAL**
- **Component**: `framework/scripts/hooks/pre_tool_guard.py` (Lines 43–44)
- **Expected**: Security hooks must fail closed. Any unhandled Python exception, type error, or JSON parsing failure must return `{"decision": "deny"}` to maintain safety invariants.
- **Actual**: Lines 43–44 explicitly catch all exceptions and output `{"decision": "allow"}`:
  ```python
  except Exception as e:
      print(json.dumps({"decision": "allow", "reason": f"Hook error: {e}"}))
  ```
- **Evidence**: Injected payload `{"toolCall": {"args": {"TargetFile": 12345}}, "workspacePaths": ["c:/repo"]}` caused a `TypeError` in `normcase`. The hook caught the exception and output `{"decision": "allow"}`.
- **Impact**: Any agent or malicious prompt that induces an unhandled exception inside the hook gains unrestricted write access to upstream Anki core (`rslib/`) and framework files.
- **Recommendation**: Replace line 44 with `print(json.dumps({"decision": "deny", "reason": f"AntiOS Security Hook Error: {e}. Failsafe active."}))`.

---

### FINDING-02: Empty Workspace Payload Bypass in Both Hooks
- **ID**: `FND-02`
- **Severity**: **CRITICAL**
- **Component**: `framework/scripts/hooks/pre_tool_guard.py` (Line 14), `framework/scripts/hooks/stop_gate.py` (Line 12)
- **Expected**: If platform context (`workspacePaths`) is omitted or empty, hooks must deny tool execution or task completion.
- **Actual**: Both hooks explicitly check `if not workspace_paths:` and grant an unconditional `allow`:
  - `pre_tool_guard.py:14`: `if not target_file or not workspace_paths: print(json.dumps({"decision": "allow"}))`
  - `stop_gate.py:12`: `if not workspace_paths: print(json.dumps({"decision": "allow"}))`
- **Evidence**: Executed `pre_tool_guard.py` and `stop_gate.py` with payload `{"workspacePaths": []}`. Both returned `{"decision": "allow"}`. An edit to `rslib/` was permitted, and task completion was allowed with 0 tests executed.
- **Impact**: A malformed or empty context payload completely disables both the safety guard and the verification ratchet.
- **Recommendation**: Both hooks must return `deny` (`pre_tool_guard.py`) or `continue` (`stop_gate.py`) when `workspacePaths` is empty.

---

### FINDING-03: Catastrophic False Positive on Ancestor Paths Named `framework`
- **ID**: `FND-03`
- **Severity**: **CRITICAL**
- **Component**: `framework/scripts/hooks/pre_tool_guard.py` (Lines 28–33)
- **Expected**: The hook should protect files inside the AntiOS `framework/` directory without interfering with legitimate project files outside it.
- **Actual**: Line 28 uses a naive path component search: `if "framework" in parts: deny`. It inspects every ancestor directory segment of the absolute path.
- **Evidence**: If AntiOS is cloned into `C:\Users\Suraj\framework\AntiOs\...`, every file in the project has `framework` in `parts`. Tested target `C:\Users\Suraj\framework\AntiOs\sandbox\StudyLab\ts\index.ts` $\to$ returned `{"decision": "deny"}`.
- **Impact**: **System Unusable (Score 4)**. Completely freezes all agent tool edits across the entire repository if any parent directory is named `framework`.
- **Recommendation**: Replace segment search with canonical prefix comparison using `os.path.commonpath`:
  ```python
  framework_root = os.path.normcase(os.path.abspath(os.path.join(repo_root, "framework")))
  if os.path.commonpath([target_file_resolved, framework_root]) == framework_root:
      # deny
  ```

---

### FINDING-04: Hook Self-Protection Gap (`.agents/hooks.json` Unprotected)
- **ID**: `FND-04`
- **Severity**: **HIGH**
- **Component**: `framework/scripts/hooks/pre_tool_guard.py` (Lines 28–40)
- **Expected**: An agent must not be permitted to tamper with, disable, or delete hook configuration files.
- **Actual**: `pre_tool_guard.py` only checks for `framework` and `rslib` in path segments. `.agents` and `hooks.json` are not protected.
- **Evidence**: Injected payload `TargetFile: "sandbox/StudyLab/.agents/hooks.json"` $\to$ returned `{"decision": "allow"}`.
- **Impact**: An agent can use `write_to_file` or `replace_file_content` to empty `hooks.json`, removing all `PreToolUse` and `Stop` hooks for the remainder of the session.
- **Recommendation**: Add `.agents` and `hooks.json` to the protected path checks in `pre_tool_guard.py`.

---

### FINDING-05: Trivial Test Fabrication via Dummy `verify_task.py`
- **ID**: `FND-05`
- **Severity**: **HIGH**
- **Component**: `framework/scripts/hooks/stop_gate.py` (Lines 58–69)
- **Expected**: Stop gate must enforce real, pre-existing project test suites and reject trivial agent-authored passes.
- **Actual**: Lines 58–69 contain a fallback that executes any `verify_task.py` found in the root directory:
  ```python
  verify_script = os.path.join(repo_root, "verify_task.py")
  if os.path.exists(verify_script):
      has_tests = True
      result = subprocess.run([sys.executable, verify_script], ...)
  ```
- **Evidence**: Created dummy `verify_task.py` containing `sys.exit(0)` in a repository without `package.json`. `stop_gate.py` executed it, observed returncode 0, and allowed task completion without executing any application tests.
- **Impact**: Trivial subversion of the verification ratchet. Agents can forge successful task completion on untested or broken code.
- **Recommendation**: Prune lines 58–69 from `stop_gate.py`. Require test runners to be registered in `package.json`, `pyproject.toml`, or an immutable configuration.

---

### FINDING-06: Skill Discoverability Failure in Workspace Root
- **ID**: `FND-06`
- **Severity**: **HIGH**
- **Component**: `framework/.agents/skills/studylab-task-runner/SKILL.md`
- **Expected**: AntiOS skills should be discoverable and automatically indexed by Antigravity upon workspace initialization.
- **Actual**: The custom skill is stored in `framework/.agents/skills/`. Antigravity only indexes `<workspace_root>/.agents/skills/`. The root workspace `AntiOs/` has no `.agents/skills/`.
- **Evidence**: Inspected platform system prompt `<skills>` block containing 67 loaded skills. `studylab-task-runner` is completely absent.
- **Impact**: The RPAC task lifecycle skill is **never loaded or activated** when operating in the root workspace. Agents receive zero progressive disclosure from the skill.
- **Recommendation**: Symlink or relocate `.agents/` to the root workspace directory: `c:\Users\Suraj\Documents\Antigravity\AntiOs\.agents\skills\`.

---

### FINDING-07: Stale Active Context & Task State Decay
- **ID**: `FND-07`
- **Severity**: **MEDIUM**
- **Component**: `docs/ACTIVE_CONTEXT.md`
- **Expected**: Working set memory must reflect the active phase, current workstreams, and recent decisions.
- **Actual**: `docs/ACTIVE_CONTEXT.md` was authored during Phase 6 and never updated. It lists `Phase: Framework Setup` and shows safety hooks as uncompleted tasks.
- **Evidence**: `docs/ACTIVE_CONTEXT.md:L6,11-13` contains `- [ ] Implement safety hooks (pre_tool_guard.py, stop_gate.py)`.
- **Impact**: **Stale-State Deception**. Resuming agents trust this document, suffer amnesia, and waste tokens attempting to re-implement already-existing hooks.
- **Recommendation**: Re-anchor `docs/ACTIVE_CONTEXT.md` with active Phase 10 state and establish an automated update protocol during the RPAC Consolidate step.

---

### FINDING-08: Lexical Windows 8.3 Short Name Traversal Bypass
- **ID**: `FND-08`
- **Severity**: **MEDIUM**
- **Component**: `framework/scripts/hooks/pre_tool_guard.py` (Line 23)
- **Expected**: Path canonicalization must resolve all Windows 8.3 short names (`RSLIB~1`) to their long-form directory equivalents (`rslib`).
- **Actual**: `os.path.realpath()` resolves lexically on Windows when targets do not physically exist on disk, failing to expand 8.3 short names.
- **Evidence**: Test harness executed payload `{"TargetFile": "RSLIB~1/dummy.rs"}` $\to$ returned `{"decision": "allow"}`.
- **Impact**: An agent targeting non-existent or newly created files in upstream core via 8.3 aliases can bypass `pre_tool_guard.py`.
- **Recommendation**: Use `pathlib.Path(target_file).resolve()` or invoke Win32 `GetLongPathName` before splitting path components.

---

### FINDING-09: Environment Failure Misdiagnosis & Agent Lockup
- **ID**: `FND-09`
- **Severity**: **MEDIUM**
- **Component**: `framework/scripts/hooks/stop_gate.py` (Lines 36–42)
- **Expected**: Stop gate should distinguish between application test assertion failures and missing ambient runtime executables.
- **Actual**: Any non-zero exit code from `npm` or `yarn` is reported as `"TypeScript tests did not pass"`. When `yarn.cmd` fails because `node.exe` is missing from PATH, the hook returns `continue` with compiler error text.
- **Evidence**: In `sandbox/StudyLab`, missing ambient node wrapper produces exit code 1 with message `The system cannot find the path specified`. `stop_gate.py` outputs `TypeScript tests did not pass`, causing the agent to repeatedly edit TypeScript code in an attempt to fix a missing binary.
- **Impact**: **Environment Trap (Score 3)**. Traps the agent in an infinite retry loop until human intervention occurs.
- **Recommendation**: Inspect process output for `FileNotFoundError` or standard OS missing executable strings, outputting `ENVIRONMENT_ERROR` with guidance to seek human intervention.

---

### FINDING-10: Ratchet Expiry & Post-Verification Mutation Blind Spot
- **ID**: `FND-10`
- **Severity**: **MEDIUM**
- **Component**: `framework/scripts/hooks/stop_gate.py`
- **Expected**: Stop gate should verify that the final working tree contains no unverified modifications (`CHANGE -> TEST -> CHANGE AGAIN -> DONE`).
- **Actual**: `stop_gate.py` re-runs `vitest:once` at the moment of Stop, but `vitest:once` only tests files matched by test globs. Modifications to untracked scripts, standalone modules, or documentation made after testing pass unverified.
- **Evidence**: Modified `scripts/deploy.py` after test execution $\to$ `stop_gate.py` ran `vitest:once`, observed exit code 0, and allowed task completion.
- **Impact**: Unverified code can escape into completed change sets.
- **Recommendation**: Add a `git diff --name-only` check against the test runner's coverage manifest.

---

### FINDING-11: Missing Change Set Synchronization (Documentation Drift)
- **ID**: `FND-11`
- **Severity**: **MEDIUM**
- **Component**: `framework/scripts/hooks/stop_gate.py`, `docs/AGENTS.md` (Directive 3)
- **Expected**: Code modifications must be bundled with documentation updates in the same change set.
- **Actual**: Zero code exists in AntiOS to check git diffs or verify documentation synchronization.
- **Evidence**: Edited TypeScript reviewer code in `sandbox/StudyLab` without modifying docs $\to$ `stop_gate.py` returned `allow`.
- **Impact**: Documentation drifts silently from code despite the constitutional rule in `AGENTS.md`.
- **Recommendation**: Implement a Layer-1 git pre-stop check verifying that if files in `ts/` or `rslib/` are modified, corresponding docs in `docs/` have staged changes.

---

### FINDING-12: Duplicate Report Corpus & Documentation Fragmentation
- **ID**: `FND-12`
- **Severity**: **MEDIUM**
- **Component**: Repository Root vs `reports/`
- **Expected**: A single canonical directory structure for historical phase reports.
- **Actual**: Seven exact duplicate report files (54,582 bytes) exist in both the root directory and `reports/`. An additional archive `PHASE_9_REPORTS.zip` is committed to the root.
- **Evidence**: SHA-256 hash comparison confirmed 100% identical file digests across all 7 pairs.
- **Impact**: Double-matching in grep searches, context window token waste, and confusion over which file is authoritative.
- **Recommendation**: Prune the 7 duplicate report files and the zip archive from the root directory.

---

### FINDING-13: Cross-Project Path Contamination in Sandbox
- **ID**: `FND-13`
- **Severity**: **LOW**
- **Component**: `sandbox/StudyLab_Treatment/.agents/sentinel/`
- **Expected**: Sandboxes should only contain artifacts and paths relevant to StudyLab.
- **Actual**: `BRIEFING.md` and `handoff.md` contain references to an external repository: `c:\Users\Suraj\Documents\Antigravity\Anki-maths\...`.
- **Evidence**: Inspected `sandbox/StudyLab_Treatment/.agents/sentinel/BRIEFING.md:L8,32-38`.
- **Impact**: Misleads agents into searching for nonexistent external directory trees.
- **Recommendation**: Delete the stale `sandbox/StudyLab_Treatment/.agents/sentinel/` directory.

---

### FINDING-14: Subagent Tool Mismatch in `studylab-task-runner/SKILL.md`
- **ID**: `FND-14`
- **Severity**: **LOW**
- **Component**: `framework/.agents/skills/studylab-task-runner/SKILL.md` (Line 29)
- **Expected**: Skill instructions must recommend subagent types equipped with the tools required to fulfill the instruction.
- **Actual**: Line 29 advises spawning a verifier subagent with `TypeName='research'` to run tests. The `research` subagent type is strictly read-only and does NOT have `run_command`!
- **Evidence**: System prompt `<subagents>` definition: `research` subagent has only `view_file`, `grep_search`, `find_by_name`, `list_dir`.
- **Impact**: A subagent spawned with `TypeName='research'` cannot run test suites and fails its verification mandate.
- **Recommendation**: Update line 29 of `SKILL.md` to specify `TypeName='self'`.

---

### FINDING-15: Root Workspace Is Unversioned (Not a Git Repository)
- **ID**: `FND-15`
- **Severity**: **INFO**
- **Component**: `c:\Users\Suraj\Documents\Antigravity\AntiOs`
- **Expected**: AntiOS framework repository should be tracked under version control.
- **Actual**: The root directory is not an initialized Git repository (`fatal: not a git repository`).
- **Evidence**: Executed `git status` in root $\to$ exit code 1.
- **Impact**: Changes made to the framework, reports, or documentation cannot be tracked, diffed, or reverted using standard git tooling.
- **Recommendation**: Initialize a Git repository at the AntiOS root (`git init`), author a `.gitignore`, and commit the baseline state.

---

### FINDING-16: Unhooked Shell Commands (`run_command`) Represent a Platform Boundary Limitation
- **ID**: `FND-16`
- **Severity**: **INFO**
- **Component**: Antigravity Platform Engine / Tool Boundary
- **Expected**: System should understand what AntiOS can intercept vs what the platform permits.
- **Actual**: Antigravity hooks intercept IDE tool calls (`write_to_file`, `replace_file_content`), but do not intercept raw strings passed to `run_command`.
- **Evidence**: `run_command` executing PowerShell `Set-Content` modified protected paths without invoking `pre_tool_guard.py`.
- **Impact**: IDE hooks provide route protection, not kernel filesystem boundary protection.
- **Recommendation**: Classify shell command mutation as an inherent **PLATFORM LIMITATION**. Enforce filesystem boundaries via OS-level permissions (e.g. read-only ACLs) or containerization.
