# Antigravity Hook Architecture & Execution Model

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity SDK & Customization Specs (`hooks.md`), `[OBSERVED]` Empirical AntiOS Test Harness (`test_lifecycle_primitives.py`), `[EXTERNAL_REPORT]` Upstream Issue Tracker (#5358, #528, #301)

---

## 1. Executive Summary

Hooks represent Antigravity's primary mechanism for deterministic, out-of-band runtime interception. Configured declaratively via `.agents/hooks.json`, hooks allow external tools and governance frameworks to execute arbitrary binaries or scripts in response to internal execution loop transitions.

This monograph documents the exact protocol, schema specifications, serialization contracts, and execution mechanics of the five primary Antigravity lifecycle hooks: `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, and `Stop`.

---

## 2. Configuration & Execution Mechanics

### 2.1 Declaration Hierarchy & Discovery
Antigravity discovers hooks across three scoping tiers:
1. **Global Tier**: `~/.gemini/config/hooks.json` (or `~/.gemini/antigravity/hooks.json`) — applies to all sessions across the machine.
2. **Plugin Tier**: `<plugin_dir>/hooks.json` — loaded when a plugin is explicitly enabled.
3. **Workspace Tier**: `<workspace_root>/.agents/hooks.json` (or `.gemini/hooks.json`) — applies to any session rooted within the repository.

```json
{
  "version": 1,
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "command": "python ../scripts/pre_tool_guard.py",
        "timeout": 30
      }
    ],
    "Stop": [
      {
        "command": "python ../scripts/stop_gate.py",
        "timeout": 60
      }
    ]
  }
}
```

### 2.2 Transport, Serialization, and Process Wrapping `[OFFICIAL]` `[OBSERVED]`
- **Transport**: Standard I/O (`stdin` / `stdout`). Diagnostic errors should be written to `stderr`.
- **Serialization**: JSON (protojson camelCase).
- **Execution Wrapper**:
  - **Linux / macOS**: Executed via `/bin/sh -c "<command>"`.
  - **Windows**: Executed via `cmd /c "<command>"`.
- **Working Directory (`cwd`) Trap**:
  - `[OFFICIAL]` The working directory of hook subprocesses is set to the **directory containing `hooks.json`** (`.agents/`), **NOT** the workspace root!
  - Commands invoking scripts must use relative paths from `.agents/` (e.g., `python ../scripts/pre_tool_guard.py`) or absolute paths.
- **Timeout**: Defaults to **30 seconds** if unspecified. A hanging script is killed via `SIGKILL` after the timeout expires.

---

## 3. Detailed Hook Schema Specifications

All hook inputs share a common set of session metadata fields:

```json
{
  "conversationId": "c685f696-3cc6-44dd-bb13-84d1877ad2f8",
  "workspacePaths": ["c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs"],
  "transcriptPath": "C:\\Users\\Suraj\\.gemini\\antigravity\\brain\\c685f696-3cc6-44dd-bb13-84d1877ad2f8\\.system_generated\\logs\\transcript.jsonl",
  "artifactDirectoryPath": "C:\\Users\\Suraj\\.gemini\\antigravity\\brain\\c685f696-3cc6-44dd-bb13-84d1877ad2f8",
  "modelName": "gemini-2.5-pro"
}
```

---

### 3.1 `PreInvocation` Hook `[OFFICIAL]` `[OBSERVED]`

Fires immediately before dispatching an inference call to the LLM.

#### Input Schema (`stdin`)
```json
{
  "conversationId": "string",
  "workspacePaths": ["string"],
  "transcriptPath": "string",
  "artifactDirectoryPath": "string",
  "modelName": "string",
  "invocationNum": 2,
  "initialNumSteps": 8
}
```

#### Output Schema (`stdout`)
```json
{
  "injectSteps": [
    {
      "ephemeralMessage": "CRITICAL: Do not modify files in tests/ until plan approval."
    },
    {
      "userMessage": "System update: deployment window closed."
    },
    {
      "toolCall": {
        "name": "view_file",
        "args": {
          "AbsolutePath": "c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs\\README.md"
        }
      }
    }
  ]
}
```

#### Field Semantics
- `ephemeralMessage`: Injected transiently for the current turn only. Consumes prompt tokens during inference, but is **NOT persisted** in `transcript.jsonl` and disappears from subsequent turns.
- `userMessage`: Injected as a persistent user message into the trajectory. Durably recorded in `transcript.jsonl`.
- `toolCall`: Pre-emptively executes a synthetic tool step.

---

### 3.2 `PreToolUse` Hook `[OFFICIAL]` `[OBSERVED]`

Fires after the LLM proposes a tool call, before physical execution. Filtered by the regex `matcher`.

#### Input Schema (`stdin`)
```json
{
  "conversationId": "string",
  "workspacePaths": ["string"],
  "transcriptPath": "string",
  "artifactDirectoryPath": "string",
  "modelName": "string",
  "toolCall": {
    "name": "write_to_file",
    "args": {
      "TargetFile": "c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs\\critical.py",
      "CodeContent": "print('hello')",
      "Overwrite": true,
      "Description": "Test file update"
    }
  },
  "stepIdx": 12
}
```

#### Output Schema (`stdout`)
```json
{
  "decision": "allow",
  "reason": "Authorized file modification within workspace boundary.",
  "permissionOverrides": ["command(npm test)"],
  "overwrite": {
    "TargetFile": "c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs\\critical_safe.py"
  }
}
```

#### Field Semantics
- `decision` (Required): Must be one of `"allow"`, `"deny"`, `"ask"`, `"force_ask"`.
  - `"allow"`: Approves tool execution immediately.
  - `"deny"`: Aborts execution. Replaces tool output with the string provided in `reason`.
  - `"ask"`: Prompts human for interactive UI approval. Honors prior "Always Allow" selections.
  - `"force_ask"`: Prompts human for confirmation unconditionally.
- `overwrite` (Optional): Object performing a **shallow top-level merge** into `toolCall.args`. Any key specified in `overwrite` replaces that top-level key in `args`.
- **CRITICAL TRAP (`decision` is mandatory)**: Returning `{}` or omitting `decision` triggers an `invalid_args` error, and the runtime defaults to **FAIL-CLOSED (deny all)** (`[EXTERNAL_REPORT]` Issue #5358).

---

### 3.3 `PostToolUse` Hook `[OFFICIAL]` `[OBSERVED]`

Fires immediately after physical execution of a tool completes.

#### Input Schema (`stdin`)
```json
{
  "conversationId": "string",
  "workspacePaths": ["string"],
  "transcriptPath": "string",
  "artifactDirectoryPath": "string",
  "modelName": "string",
  "stepIdx": 12,
  "error": "Command failed with exit code 1"
}
```

#### Output Schema (`stdout`)
```json
{}
```

#### Field Semantics & Observability Reality
- **Payload Contents**: Contains `stepIdx` and optional `error`.
- **BLINDSPOT**: **`PostToolUse` input DOES NOT contain `toolName`, `args`, or the tool execution `result`/`stdout`!**
- **Strict Output Contract**: **MUST RETURN EMPTY `{}`**. Returning any keys or non-JSON output triggers deserialization failures.
- **Reconstruction Architecture**: To observe what tool executed and what it returned, an external observer must open and read `transcriptPath` (`transcript.jsonl`) at offset `stepIdx`.

---

### 3.4 `PostInvocation` Hook `[OFFICIAL]` `[OBSERVED]`

Fires after the LLM inference loop and any triggered tool chain complete for that turn.

#### Input Schema (`stdin`)
```json
{
  "conversationId": "string",
  "workspacePaths": ["string"],
  "transcriptPath": "string",
  "artifactDirectoryPath": "string",
  "modelName": "string",
  "invocationNum": 2,
  "initialNumSteps": 14
}
```

#### Output Schema (`stdout`)
```json
{
  "injectSteps": [
    {
      "ephemeralMessage": "Lint check completed with 0 errors."
    }
  ],
  "terminationBehavior": "force_continue"
}
```

#### Field Semantics
- `injectSteps`: Injects steps into the trajectory prior to the next action.
- `terminationBehavior`:
  - `"force_continue"`: Re-enters the model inference loop immediately, bypassing idle wait states.
  - `"terminate"`: Forces immediate termination of the session turn.
  - `""` or omitted: Normal lifecycle continuation.

---

### 3.5 `Stop` Hook (Physical Stop Gate) `[OFFICIAL]` `[OBSERVED]`

Fires when the agent attempts to conclude its work and mark the task as complete.

#### Input Schema (`stdin`)
```json
{
  "conversationId": "string",
  "workspacePaths": ["string"],
  "transcriptPath": "string",
  "artifactDirectoryPath": "string",
  "modelName": "string",
  "executionNum": 1,
  "terminationReason": "model_stop",
  "error": "",
  "fullyIdle": true
}
```

#### Output Schema (`stdout`)
```json
{
  "decision": "continue",
  "reason": "STOP GATE REJECTION: Verification test suite failed (exit code 1). You must fix failing tests before terminating."
}
```

#### Field Semantics
- `terminationReason`: Possible values include `"model_stop"`, `"max_steps_exceeded"`, `"error"`.
- `fullyIdle`: Boolean indicating whether all child subagents and background tasks have finished.
- `decision`:
  - `"continue"`: **Physically rejects session termination**. Re-engages the agent in reasoning mode and injects `reason` as an instruction prompt.
  - `"allow"` or `{}`: Permits clean session exit.

---

## 4. Canonical Hook Specification Matrix

| Hook Name | Trigger Point | Matcher Regex? | Input Fields on `stdin` | Output Fields on `stdout` | Execution Mode | Failure Mode | AntiOS 2.0 Status |
|---|---|---|---|---|---|---|---|
| **`PreInvocation`** | Pre-LLM inference call | No | `invocationNum`, `initialNumSteps`, metadata | `injectSteps` (`ephemeralMessage`, `userMessage`, `toolCall`) | Blocking synchronous | **Fail-Open** (logs error, continues turn) | Unregistered |
| **`PreToolUse`** | Pre-tool physical execution | **Yes** (e.g. `run_command\|write_to_file`) | `toolCall` (`name`, `args`), `stepIdx`, metadata | `decision` (`allow`, `deny`, `ask`, `force_ask`), `overwrite`, `reason` | Blocking synchronous | **Fail-Closed** (empty `{}` or crash $\rightarrow$ `invalid_args` deny all) | **Registered** (`pre_tool_guard.py`) |
| **`PostToolUse`** | Post-tool physical execution | **Yes** (e.g. `*`) | `stepIdx`, `error`, metadata (**NO toolName, NO args, NO result**) | **Strictly `{}`** | Blocking synchronous | **Fail-Closed** (non-empty output fails step) | **NOT REGISTERED** |
| **`PostInvocation`** | Post-turn tool resolution settlement | No | `invocationNum`, `initialNumSteps`, metadata | `injectSteps`, `terminationBehavior` (`force_continue`, `terminate`) | Blocking synchronous | **Fail-Open** (logs error, continues) | Unregistered |
| **`Stop`** | Session termination request | No | `terminationReason`, `error`, `fullyIdle`, metadata | `decision` (`continue`, `allow`), `reason` | Blocking synchronous | **Fail-Open** (crash exits session) / **Fail-Closed** via explicit Python handler | **Registered** (`stop_gate.py`) |

---

## 5. Architectural Conclusions

1. **Protocol Rigidity**: Every hook requires precise JSON schemas. Omitting required keys (such as `decision` in `PreToolUse` or returning content in `PostToolUse`) causes severe execution failures.
2. **Deterministic Control Slices**: Antigravity gives runtime governance frameworks two primary control levers:
   - **Interception & Modification Gate**: `PreToolUse` allows pre-execution validation, blocking, and argument sanitation.
   - **Verification Gate**: `Stop` enforces test suite integrity, boundary cleanliness, and verification audits before admitting task completion.
3. **Passive vs Active Telemetry**: Because `PostToolUse` lacks tool payloads, building an observability plane requires combining `PostToolUse` triggers with incremental parsing of `transcriptPath`.
