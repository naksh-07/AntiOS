# Antigravity Lifecycle Integration Model

**Specification**: `docs/architecture/antigravity/LIFECYCLE.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 8  

---

## 1. Native Extension Points

AntiOS integrates into Google Antigravity exclusively via standard, supported platform configuration and extension hooks defined in `.agents/hooks.json`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "command": "python .antios/runtime/pre_tool_guard.py",
        "timeout_ms": 2000,
        "tools": ["write_to_file", "replace_file_content"]
      }
    ],
    "Stop": [
      {
        "command": "python .antios/runtime/stop_gate.py",
        "timeout_ms": 30000
      }
    ]
  }
}
```

---

## 2. The Hook Execution Pipeline

### 2.1 PreToolUse Interceptor (`pre_tool_guard.py`)
- **Event**: Fires synchronously before Antigravity executes a modifying file tool (`write_to_file`, `replace_file_content`).
- **Input**: JSON payload passed via `stdin` containing tool name, target file path, and parameters.
- **Enforcement**:
  1. Resolves canonical real path using `os.path.realpath`.
  2. Blocks path traversal sequences (`../`, `..\`, null bytes).
  3. Verifies target file is contained within approved workspace roots.
  4. Blocks writes targeting protected governance zones (`.agents/`, `.antios/`, `framework/`, `antios.config.json`).
- **Execution Performance**: Executes in $< 10$ms using standard library Python.
- **Fail-Closed Guarantee**: Any exception, unexpected format, or missing target denies the tool call (`exit 1`).

### 2.2 Stop Gate Interceptor (`stop_gate.py`)
- **Event**: Fires synchronously when an agent invokes the `Stop` event to conclude a task turn.
- **Input**: Context metadata on `stdin`.
- **Enforcement**:
  1. Scans modified git files for unmerged conflict markers (`<<<<<<<`, `=======`).
  2. Discovers registered project test suites from `antios.config.json` or project manifests.
  3. Executes the physical test process via subprocess.
  4. Ratchets task completion to return code 0.
- **Fail-Closed Guarantee**: If tests fail, exit code 1 prevents task conclusion and surfaces actionable test failure logs.

---

## 3. Subagent Lifecycle & Workforce Governance

When tasks require parallel investigation or independent verification, AntiOS governs Antigravity subagent spawning through rigid constitutional rules:

```
[ Root Agent Session ]
         │
         ▼ (Evaluates Orchestration Gate)
   invoke_subagent
         │
         ├─► Shallow Depth Law: Nesting depth strictly ≤ 2 (INV-06)
         ├─► Concurrency Ceiling: Max 4 active subagents globally (INV-07)
         ├─► Launch Budget: Max 10 launches total across entire tree
         └─► Workspace Isolation: Workspace='branch' for parallel writers
```

### 3.1 Wave Collapse Protocol (`INV-08`)
Multi-wave missions execute sequentially. Before Wave $N+1$ may launch, Wave $N$ must collapse completely:
1. Subagents complete tasks and emit standardized structured Handoff Reports.
2. The orchestrator calls `manage_subagents(Action='kill', ConversationIds=[...])`.
3. Active worker count is confirmed to reach 0.
4. Synthesized findings are recorded before subsequent wave dispatch.

### 3.2 Branch Workspace Isolation
When multiple subagents are authorized to write code simultaneously:
- Each worker must be dispatched with `Workspace='branch'`.
- Workers modify isolated Git branches in memory/sandbox.
- The parent agent reviews diffs and merges changes sequentially, eliminating write collisions.
