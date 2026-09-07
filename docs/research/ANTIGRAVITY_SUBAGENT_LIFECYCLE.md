# Antigravity Subagent Lifecycle & Execution Model

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity SDK & Subagent Docs (`https://antigravity.google/docs/subagents`), `[OBSERVED]` Empirical AntiOS Test Harness (`test_lifecycle_primitives.py`), `[EXTERNAL_REPORT]` Upstream Issue Tracker (#569, #528)

---

## 1. Executive Summary

Autonomous multi-agent orchestration is a cornerstone of modern software engineering frameworks. In Antigravity, subagents are not simulated personas within a single prompt; they are fully isolated, asynchronous child execution sessions created via the native `invoke_subagent` tool.

This monograph documents the architectural lifecycle of Antigravity subagents. It defines the mechanics of the `invoke_subagent` tool, details the **Zero Context Inheritance** principle, analyzes recursive hook enforcement, evaluates concurrent execution patterns, and details verified runtime limitations including GitHub Issue #569 (the Lazy MCP tool dispatch gap in subagents).

---

## 2. The `invoke_subagent` Primitive

Subagents are instantiated through the native `invoke_subagent` tool:

```json
{
  "TypeName": "research",
  "Role": "Independent Test Auditor",
  "Prompt": "Execute the full test suite and verify test isolation. Report all failures.",
  "Model": "inherit",
  "Workspace": "branch"
}
```

### 2.1 Invocation Parameters `[OFFICIAL]`
- `TypeName`: The identifier of the agent template (either built-in like `research` or `self`, or custom-defined via `define_subagent`).
- `Role`: Human-readable 2–5 word description of the subagent's role.
- `Prompt`: The actionable task description for the subagent.
- `Model`: LLM model tier (`"inherit"`, `"flash_lite"`, `"flash"`, `"pro"`).
- `Workspace`: Filesystem isolation mode (`"inherit"`, `"branch"`, `"share"`).

### 2.2 `PreToolUse` Interception of `invoke_subagent` `[OFFICIAL]` `[OBSERVED]`
Because `invoke_subagent` is a native tool call, it passes through the standard `PreToolUse` hook pipeline if the matcher covers it (`matcher: ".*"` or `matcher: "invoke_subagent"`):
- A governance hook can inspect the subagent's `Prompt`, `TypeName`, and `Workspace`.
- The hook can rewrite parameters via `overwrite` (e.g., downgrading expensive models to `"flash"`, or enforcing `Workspace: "branch"`).
- The hook can veto invocation entirely (`decision: "deny"`) to enforce hard agent concurrency limits.

---

## 3. The Zero Context Inheritance Principle `[OFFICIAL]` `[OBSERVED]`

The defining cognitive property of Antigravity subagents is **Zero Context Inheritance**:

```
PARENT AGENT (Turn 25)                    CHILD SUBAGENT (Turn 0)
┌────────────────────────────────┐         ┌────────────────────────────────┐
│ conversationId: 1111-2222      │         │ conversationId: a938-47e4      │
│ Trajectory: 25 turns           │         │ Trajectory: 0 turns (Fresh)    │
│ Tokens: 180,000                │         │ Tokens: ~2,500 (Base Prompt)   │
│ In-Memory Variables / State    │         │                                │
│ Parent Tool Call History       │   ───X  │ ZERO INHERITANCE OF HISTORY    │
│ Parent Reasoning / Thoughts    │         │                                │
└───────────────┬────────────────┘         └───────────────┬────────────────┘
                │                                          │
                │ Invokes via Prompt                       │ Receives Prompt ONLY
                ▼                                          ▼
   System Prompt Framing                      System Prompt Framing
   Workspace Filesystem                       Workspace Filesystem (or Branch)
   Root Rules (GEMINI.md / AGENTS.md)         Root Rules (GEMINI.md / AGENTS.md)
   Workspace Hooks (.agents/hooks.json)       Workspace Hooks (.agents/hooks.json)
```

### 3.1 What Subagents Inherit `[OFFICIAL]`
1. **Workspace Filesystem**: Access to repository files (subject to `Workspace` isolation mode).
2. **Root Instructions**: Automatically executes Upward Rule Walk to discover `GEMINI.md` and `AGENTS.md`.
3. **Workspace Hooks**: Inherits all hooks registered in `.agents/hooks.json`.
4. **Declared Skills**: Discovers registered skills in `.agents/skills/`.

### 3.2 What Subagents DO NOT Inherit `[OFFICIAL]` `[OBSERVED]`
1. **Conversation History**: Completely oblivious to prior parent turns, user instructions, or past tool calls.
2. **In-Memory Reasoning / Scratchpads**: Cannot see parent internal thoughts or chain-of-thought tokens.
3. **Parent Context Budget**: Subagents begin with a completely pristine, empty context window.

### 3.3 The Maker-Checker Opportunity
Zero context inheritance eliminates cognitive confirmation bias. In the AntiOS Maker-Checker architecture:
- The **Maker** implements code changes across turns.
- The **Checker** is spawned as an independent subagent (`antios-verifier`).
- Because the Checker inherits zero parent rationalizations or excuses, it audits the working tree strictly against the physical filesystem and test outputs.

---

## 4. Hook Scoping, Recursion, and Telemetry Isolation

### 4.1 Recursive Hook Enforcement `[OFFICIAL]` `[OBSERVED]`
When a child subagent executes a tool (e.g. `view_file` or `run_command`), Antigravity's hook runner fires `.agents/hooks.json` **for the child agent**:
- The hook receives the child's unique `conversationId`.
- The hook receives the child's distinct `transcriptPath`:
  `.../brain/<child-conversation-id>/.system_generated/logs/transcript.jsonl`
- PreToolUse security policies and Stop Gate invariants apply uniformly to children and parents alike.

### 4.2 Telemetry Partitioning `[OBSERVED]`
- **Separate Transcripts**: Parent and child write to entirely separate `transcript.jsonl` log files.
- **Log Reconstruction**: An external telemetry observer cannot reconstruct a full mission trajectory by reading only the parent transcript. It must index subagent IDs emitted in `invoke_subagent` results and aggregate child transcript directories hierarchically.

---

## 5. Concurrent Execution & Reactive Wakeup

Antigravity handles subagent execution asynchronously without blocking the parent:
1. `invoke_subagent` returns immediately with a unique `conversationId` and initial status.
2. The parent agent does **not** need to poll in a loop.
3. The platform provides a **Reactive Wakeup** mechanism: when the subagent completes its task or sends a message via `send_message`, the parent agent's execution loop is automatically resumed with the subagent's response payload delivered directly into context.

---

## 6. Known Upstream Issues & Real-World Limitations

### 6.1 GitHub Issue #569: The Lazy MCP Dispatch Gap in Subagents `[EXTERNAL_REPORT]`
- **Affected Versions**: Antigravity CLI v1.1.0 – v1.1.11 / current runtime builds.
- **Symptom**: When a subagent is defined with `enable_mcp_tools: true`, the runtime successfully exposes Eager MCP tools. However, for **Lazy MCP tools** (tools requiring dispatch via `call_mcp_tool`), the native `call_mcp_tool` wrapper is **omitted from the subagent's schema**.
- **Impact**: Subagents attempting to invoke lazy-loaded MCP tools (e.g. Playwright, Notion, GitHub MCP) fail with tool execution errors.
- **Workaround for AntiOS**: All complex MCP interactions must be executed directly by the root orchestrator agent or delegated via structured IPC messages (`send_message`).

### 6.2 Unbounded Subagent Forking Risk `[OBSERVED]`
- Antigravity imposes no native ceiling on recursive subagent depth or concurrent subagent count.
- If a subagent prompt inadvertently instructs it to spawn subagents, an exponential fork-bomb can deplete system resources and API rate limits.
- **AntiOS Mitigation**: `PreToolUse` hook on `invoke_subagent` enforces a strict ceiling (e.g., maximum 4 concurrent subagents, maximum tree depth of 1).
