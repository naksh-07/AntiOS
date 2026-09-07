# Antigravity Tool Interception: PreToolUse Mechanics & The Shell Bypass Problem

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity Customization Docs (`hooks.md:L168-212`), `[OBSERVED]` Empirical Windows Runtime Harness (`test_lifecycle_primitives.py`), `[EXTERNAL_REPORT]` Upstream Issue Tracker (#5358, #528)

---

## 1. Executive Summary

A core promise of agentic governance frameworks is deterministic enforcement: preventing unauthorized modifications, protecting critical paths, and intercepting hazardous operations before execution. Antigravity provides the `PreToolUse` hook as its physical pre-execution interceptor.

This monograph provides an exhaustive technical analysis of `PreToolUse`. It details matcher semantics, the decision protocol, argument rewriting via `overwrite`, and presents an empirical investigation into **The Shell Redirection Problem**—demonstrating why string-matching `write_to_file` and `replace_file_content` provides an illusion of safety when `run_command` is available, and defining how true deterministic enforcement can be achieved.

---

## 2. The `PreToolUse` Protocol & Interception Mechanics

When the LLM proposes one or more tool calls, Antigravity evaluates each call sequentially against the `matcher` regex in `.agents/hooks.json`.

```
Model Emits Tool Call
         │
         ▼
Regex Matcher Check ─── No Match ───> Execute Tool Directly
         │
      Matches
         │
         ▼
Spawn PreToolUse Hook Subprocess
  - stdin: toolCall { name, args }, stepIdx, metadata
  - stdout: decision, reason, overwrite, permissionOverrides
         │
         ├── decision == "deny" ────────> Abort Tool Call; return reason to model
         ├── decision == "ask" ─────────> Prompt user in UI (honors cache)
         ├── decision == "force_ask" ───> Prompt user unconditionally
         ├── decision == "allow" ───────> Execute Tool (with overwritten args if present)
         └── Malformed / Empty Output ──> FAIL-CLOSED: Denies all (invalid_args)
```

### 2.1 Decision Outcomes `[OFFICIAL]` `[OBSERVED]`
1. **`"allow"`**: Approves immediate execution.
2. **`"deny"`**: Aborts tool execution. The string provided in `reason` is returned directly to the model as an error response. The physical tool process is never spawned.
3. **`"ask"`**: Suspends tool execution and displays an interactive modal in the Antigravity UI for human confirmation. If the user previously selected "Always allow for this session", the modal is bypassed.
4. **`"force_ask"`**: Suspends tool execution and prompts the user unconditionally, ignoring any cached approvals.

### 2.2 Argument Overwrite (`overwrite`) Mechanics `[OFFICIAL]` `[OBSERVED]`
`PreToolUse` can rewrite tool arguments before physical execution via the `overwrite` field:

```json
{
  "decision": "allow",
  "overwrite": {
    "CommandLine": "pytest tests/unit/ -q --maxfail=1"
  }
}
```

#### The Shallow Merge Trap `[OFFICIAL]` `[OBSERVED]`
Upstream Antigravity documentation explicitly specifies:
> *"The overwrite dictionary performs a shallow, top-level merge into toolCall.args."*

- **Top-level keys**: Safely overwritten or added.
- **Nested dictionaries / arrays**: Entire nested objects are **replaced wholesale**, not deep-merged.
  - *Example*: If `toolCall.args` has `{"options": {"verbose": true, "timeout": 10}}`, returning `{"overwrite": {"options": {"timeout": 20}}}` **deletes** `verbose`!

---

## 3. The Shell Redirection Problem: Regex Bypasses & The Illusion of Safety

### 3.1 The Flawed Assumption
A common design pattern in AI governance is to register a `PreToolUse` hook matching:
```json
"matcher": "write_to_file|replace_file_content"
```
The assumption is that by intercepting these two tools, the framework can prevent any unauthorized modification to protected files (such as production configurations, credentials, or core architectural components).

### 3.2 Empirical Proof of Shell Bypass `[OBSERVED]`
If the agent is equipped with `run_command`, restricting `write_to_file` and `replace_file_content` provides **zero physical protection**. In Windows PowerShell, bash, or CMD, there are dozens of native primitives capable of creating, modifying, or truncating files without triggering file-tool hooks.

In our empirical runtime test harness (`test_lifecycle_primitives.py`), we evaluated 14 common file-write commands executed via `run_command`. All of them execute arbitrary file writes while completely bypassing file-tool hooks:

| Shell Environment | Command Syntax Pattern | Bypass Vector |
|---|---|---|
| **PowerShell** | `Set-Content -Path secret.py -Value "data"` | Cmdlet file creation |
| **PowerShell** | `Out-File -FilePath secret.py -InputObject "data"` | Cmdlet file stream write |
| **PowerShell / CMD** | `echo payload > secret.py` | Shell stdout redirection |
| **PowerShell / CMD** | `echo payload >> secret.py` | Shell stdout append redirection |
| **PowerShell .NET** | `[System.IO.File]::WriteAllText('secret.py', 'data')` | Direct CLR memory write |
| **PowerShell .NET** | `[System.IO.File]::AppendAllText('secret.py', 'data')` | Direct CLR append |
| **Any Shell** | `python -c "open('secret.py', 'w').write('data')"` | Scripting language file write |
| **Any Shell** | `node -e "fs.writeFileSync('secret.py', 'data')"` | Node.js file system write |
| **PowerShell** | `Invoke-WebRequest -Uri ... -OutFile secret.py` | Remote payload file download |
| **PowerShell** | `curl.exe -o secret.py http://...` | Native binary output write |
| **PowerShell / CMD** | `type source.txt > secret.py` | Pipeline copy redirection |
| **PowerShell / CMD** | `copy /y source.txt secret.py` | Shell copy overwrite |
| **PowerShell** | `[IO.File]::WriteAllBytes('bin', [Convert]::FromBase64String('...'))` | Binary base64 decoding |
| **PowerShell** | `& (Get-Command Set-Content) -Path secret.py ...` | Dynamic cmdlet invocation |

### 3.3 Why Regex Filtering on `run_command` Fails `[OBSERVED]` `[INFERRED]`
Attempting to solve this by adding `run_command` to the hook matcher and running regex checks over `CommandLine` creates an unsolvable cat-and-mouse game:
1. **Obfuscation & Aliases**: In PowerShell, `sc` is an alias for `Set-Content`, `>` is syntactic sugar for `Out-File`, and commands can be invoked dynamically via `& ("Set" + "-Content")`.
2. **String Interpolation & Variables**: `$p = "secret.py"; $c = "data"; [IO.File]::WriteAllText($p, $c)`.
3. **Severe False Positives**: Regexes that block `>` or `Set-Content` will break legitimate engineering workflows (such as running test commands with stdout redirected to log files).

---

## 4. Deterministic Enforcement Alternatives

If string regex matching cannot guarantee file protection against shell commands, how can an engineering framework achieve deterministic boundary governance?

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DETERMINISTIC ENFORCEMENT HIERARCHY                  │
├──────────────────────────────┬─────────────────────────────────────────┤
│ Tier 1: Strict Tool Pruning  │ Remove run_command from read-only       │
│                              │ checker subagents. (100% Deterministic) │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Tier 2: Physical Stop Gate   │ Stop hook checks git diff against       │
│                              │ protected paths. (100% Deterministic)   │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Tier 3: OS Sandbox Isolation │ enableTerminalSandbox: true (Cgroups,   │
│                              │ Windows AppContainer). (High Assurance) │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Tier 4: Interactive Review   │ PreToolUse decision: "ask" for any      │
│                              │ shell execution. (Human Governance)     │
├──────────────────────────────┼─────────────────────────────────────────┤
│ Tier 5: Regex String Guards  │ PreToolUse regex on CommandLine.        │
│                              │ (Heuristic only - Low Assurance)        │
└──────────────────────────────┴─────────────────────────────────────────┘
```

### 4.1 Architectural Strategy for AntiOS
1. **Interception at `PreToolUse` as an Early Warning System**:
   - `pre_tool_guard.py` intercepts `write_to_file` and `replace_file_content` to block obvious, accidental modifications to protected files.
   - For `run_command`, it warns on explicit dangerous tokens (`git push --force`, `rm -rf /`, `Drop-Database`), but acknowledges that shell commands cannot be deterministically validated via regex.
2. **Enforcement at the Physical Stop Gate (`Stop`)**:
   - The true, unbypassable boundary is the `Stop` hook (`stop_gate.py`).
   - When the agent finishes its work and attempts to complete the session, `stop_gate.py` runs `git status --porcelain` and `git diff --name-only`.
   - Regardless of whether changes were written via `write_to_file`, `Set-Content`, Python, or a compiled binary, `git` physically detects all modified files.
   - If any protected path was modified or uncommitted changes remain, `stop_gate.py` emits `{"decision": "continue", "reason": "Protected file modified"}` and completely blocks completion.
3. **Checker Subagent Hardening**:
   - When AntiOS dispatches verification subagents (`antios-verifier`), it explicitly omits `enable_write_tools: true`.
   - A subagent without `run_command` or file write tools physically cannot bypass boundaries.
