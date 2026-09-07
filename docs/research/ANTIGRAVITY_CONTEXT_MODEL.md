# Antigravity Native Context Construction Pipeline
**Document**: `ANTIGRAVITY_CONTEXT_MODEL.md`  
**Status**: Foundational Research Dossier (Research 1)  
**Classification**: Rigorous Evidence-Backed Specification  
**Authority**: Empirical & Official Architectural Reference  

---

## 1. Executive Summary

This document establishes the precise operational mechanics of how a Google Antigravity agent acquires, constructs, prioritizes, and utilizes context when interacting with a software engineering repository. 

Treating previous architectural assumptions as unverified hypotheses, this research combines:
1. `[OFFICIAL]` Upstream specifications from built-in customization guides (`agy-customizations`), Antigravity guides (`antigravity_guide`), and the `google-antigravity` SDK.
2. `[OBSERVED]` Empirical data from controlled disposable sandbox experiments, transcript audits, and language server runtime traces.
3. `[INFERRED]` Conclusions logically derived from verified behavioral constraints.

The central discovery of this investigation is that **Antigravity operates a heterogeneous, multi-tiered context assembly pipeline with strict boundaries between cognitive guidance and deterministic enforcement**. The agent does not experience an ambient memory space; rather, every turn reconstructs an ephemeral prompt payload combining static system constraints, dynamically discovered directory rules, lazy-loaded skill runbooks, and tool execution outputs.

---

## 2. The Native Context Execution Loop

The lifecycle of an Antigravity turn proceeds through distinct, observable phases:

```text
               User Prompt / Slash Command / Mentions
                                 │
                                 ▼
         [ 1. Pre-Invocation Runtime Pipeline ]
         ├── Ingest workspace paths & system identity (<identity>, <user_information>)
         ├── Query active MCP servers (tools/list) & native tool schemas
         ├── Scan skill customization roots (inject <skills> metadata catalog)
         ├── Directory traversal: walk UP from CWD to repo root for AGENTS.md / GEMINI.md
         ├── Ingest conversation trajectory from SQLite (<conversation-id>.db)
         └── Execute PreInvocation lifecycle hooks (hooks.json -> injectSteps[])
                                 │
                                 ▼
         [ 2. Prompt Payload Serialization & Assembly ]
         ├── Combine System Prompt + Tool Declarations + Conversation History
         └── Pre-inference token accounting & budget truncation
                                 │
                                 ▼
         [ 3. Foundation Model Inference (Gemini Pro/Flash) ]
         ├── Adaptive thinking budget execution (response.thoughts)
         └── Emit text response OR strongly-typed ToolCall events
                                 │
                                 ▼
         [ 4. Tool Execution & Boundary Interception ]
         ├── PreToolUse Hook: stdin JSON -> inspect tool call -> allow / deny / overwrite
         ├── Platform Tool Policy: Short-circuit whitelist/blacklist evaluation
         └── Native Execution: run_command, view_file, replace_file_content, etc.
                                 │
                                 ▼
         [ 5. Tool Result Handling & Post-Tool Lifecycle ]
         ├── Result truncation (view_file <= 46KB / 800 lines; grep <= 50 matches)
         ├── PostToolUse Hook: audit, lint, post-processing
         └── Append tool result step into conversation trajectory
                                 │
                                 ▼
         [ 6. Model Re-Invocation or Stop Gate ]
         ├── Model continues multi-step plan OR attempts model_stop
         └── Stop Hook: intercept completion -> inspect tests -> exit code 0 or continue
```

---

## 3. The 12 Canonical Context Sources: 10-Dimension Evaluation

Every piece of information entering an agent's cognitive awareness originates from one of twelve canonical sources. Each source exhibits unique operational characteristics across ten fundamental dimensions:

1. **Automatic Availability**: Is it injected without agent tool calls?
2. **Discoverability**: Can the agent find it via tools if not pre-injected?
3. **Deciding Authority**: Who decides whether it enters context (Runtime, User, Model)?
4. **Loading Stage**: When does it enter the context window?
5. **Initial Token Size**: How much token space does it occupy initially?
6. **Agent Ignorability**: Can the model rationalize away or ignore the information?
7. **Execution Updatability**: Can it mutate mid-session?
8. **Session Survival**: Does it persist across new conversations?
9. **Subagent Inheritance**: Does a freshly spawned subagent inherit it?
10. **Surface Parity**: Does behavior differ between Desktop (2.0), IDE, CLI (`agy`), and SDK?

---

### Source 1: System Instructions (`<identity>`, `<user_information>`, System Contract)
* `[OFFICIAL]` **Automatic Availability**: YES. Injected at the head of every inference prompt.
* `[OFFICIAL]` **Discoverability**: N/A (Always present).
* `[OFFICIAL]` **Deciding Authority**: Platform Runtime / Language Server (`cortex`).
* `[OFFICIAL]` **Loading Stage**: Turn 0 and refreshed upon every turn.
* `[OFFICIAL]` **Initial Token Size**: ~1,500–3,500 tokens (includes tool definitions, MCP catalog, environment metadata).
* `[OFFICIAL]` **Agent Ignorability**: NO. Forms the system prompt foundation defining cognitive persona and tool rules.
* `[OFFICIAL]` **Execution Updatability**: Static within a session; runtime updates dynamic metadata (e.g. current time, task status).
* `[OFFICIAL]` **Session Survival**: Reconstructed fresh in new sessions.
* `[OFFICIAL]` **Subagent Inheritance**: Subagents receive a specialized system contract based on role (e.g. `research` subagent receives read-only tool contracts).
* `[OFFICIAL]` **Surface Parity**:
  * *Desktop 2.0*: Injects auxiliary panel instructions and Electron app settings.
  * *IDE*: Injects editor-specific modalities (code lenses, tab completion hints, active file buffer).
  * *CLI (`agy`)*: Injects concise TUI directives.
  * *SDK*: Caller provides custom system string via `LocalAgentConfig(system_instructions="...")`.

---

### Source 2: Directory & Project Rules (`AGENTS.md`, `GEMINI.md`)
* `[OFFICIAL]` **Automatic Availability**: YES, but **only for active directory scopes**.
* `[OFFICIAL]` **Discoverability**: Traversed automatically by Language Server directory walkers.
* `[OFFICIAL]` **Deciding Authority**: Platform Language Server file watcher.
* `[OFFICIAL]` **Loading Stage**: Session startup and dynamically when opening/editing files within the directory.
* `[OFFICIAL]` **Initial Token Size**: Full file content size of discovered rules. (Official best practice: $\le 40$ to $120$ lines).
* `[OFFICIAL]` **Agent Ignorability**: **YES (Cognitive Guidance Only)**. The agent sees instructions as prompt text, but has physical capability to call tools counter to instructions unless blocked by hooks.
* `[OFFICIAL]` **Execution Updatability**: Dynamic. Disk updates are re-read on subsequent file operations.
* `[OFFICIAL]` **Session Survival**: Permanent on disk.
* `[OFFICIAL]` **Subagent Inheritance**: Subagents inherit directory rules when accessing paths within that directory scope.
* `[CONFLICT]` **Subdirectory Misconception**: AntiOS assumed `docs/AGENTS.md` is automatically indexed. Official Antigravity behavior only indexes `AGENTS.md` / `GEMINI.md` at the **repository root** or in directory ancestor chains. Subdirectory files like `docs/AGENTS.md` are **never auto-loaded** when working at the repository root!

---

### Source 3: Modular Rules (`.agents/rules/*.md`)
* `[OFFICIAL]` **Automatic Availability**: Conditional based on frontmatter trigger mode.
* `[OFFICIAL]` **Discoverability**: Discovered within `.agents/rules/`, `.agent/rules/`, `_agents/rules/`.
* `[OFFICIAL]` **Deciding Authority**: Runtime rule engine for `always_on` and `glob`; model judgment for `model_decision`.
* `[OFFICIAL]` **Loading Stage**:
  * `always_on: true`: Injected on turn 0.
  * `glob: "<pattern>"`: Injected when a file matching the glob is viewed or edited.
  * `trigger: model_decision`: Injected progressively when the model assesses relevance.
* `[OFFICIAL]` **Initial Token Size**: 0 tokens for inactive rules; full body size when triggered.
* `[OFFICIAL]` **Agent Ignorability**: Cognitive guidance.
* `[OFFICIAL]` **Execution Updatability**: Immediate on-disk reload.
* `[OFFICIAL]` **Session Survival**: Permanent on disk.
* `[OFFICIAL]` **Subagent Inheritance**: Discovered if subagent touches matching file paths.
* `[OFFICIAL]` **Surface Parity**: Supported uniformly across Desktop, IDE, CLI, and SDK. Rules are deduplicated strictly by canonical resolved file path.

---

### Source 4: Workspace & Global Skills (`skills/<name>/SKILL.md`)
* `[OFFICIAL]` **Automatic Availability**: **NO**. Only progressive metadata (`name`, `description`, path) is injected into `<skills>`.
* `[OFFICIAL]` **Discoverability**: Discovered via hierarchical traversal (`.agents/skills/`, `~/.gemini/config/skills/`, built-ins).
* `[OFFICIAL]` **Deciding Authority**: Model (semantic selection) OR User (explicit `/` slash command or `@` mention).
* `[OFFICIAL]` **Loading Stage**: Loaded strictly on-demand when `view_file` is called on `SKILL.md`.
* `[OFFICIAL]` **Initial Token Size**: ~20–50 tokens per skill in prompt catalog.
* `[OFFICIAL]` **Agent Ignorability**: **YES**. Autonomous agents frequently choose not to load a relevant skill if they assume generic reasoning suffices.
* `[OFFICIAL]` **Execution Updatability**: Editing `SKILL.md` or scripts takes effect immediately on next tool access.
* `[OFFICIAL]` **Session Survival**: Permanent on disk; loaded skill instructions remain in conversation trajectory until compaction.
* `[OFFICIAL]` **Subagent Inheritance**: Subagents receive the `<skills>` catalog; can load skills independently.
* `[OFFICIAL]` **Surface Parity**: Desktop and IDE render slash command popups; SDK requires mounting via `LocalAgentConfig(skills_paths=[...])`.

---

### Source 5: Workspace Configuration (`hooks.json`, `skills.json`, `plugins.json`, `antios.config.json`)
* `[OFFICIAL]` **Automatic Availability**: Processed out-of-band by the Language Server and hook runtime.
* `[OFFICIAL]` **Discoverability**: Located in `.agents/` or workspace root.
* `[OFFICIAL]` **Deciding Authority**: Platform runtime.
* `[OFFICIAL]` **Loading Stage**: Platform initialization and hook event dispatch.
* `[OFFICIAL]` **Initial Token Size**: 0 tokens in model prompt (unless explicitly read via `view_file`).
* `[OFFICIAL]` **Agent Ignorability**: **CANNOT BE IGNORED**. Hooks execute as native operating system processes (`sh -c` / `cmd /c`).
* `[OFFICIAL]` **Execution Updatability**: Immediate upon file save.
* `[OFFICIAL]` **Session Survival**: Permanent on disk.
* `[OFFICIAL]` **Subagent Inheritance**: Workspace hooks govern all subagents executing within the repository workspace.
* `[OFFICIAL]` **Surface Parity**: `hooks.json` operates identically across Desktop, IDE, and CLI.

---

### Source 6: Conversation History & Trajectory Database
* `[OFFICIAL]` **Automatic Availability**: YES. Monotonically grows across turns.
* `[OFFICIAL]` **Discoverability**: Maintained internally in SQLite.
* `[OFFICIAL]` **Deciding Authority**: Runtime session coordinator.
* `[OFFICIAL]` **Loading Stage**: Continuous across turns.
* `[OFFICIAL]` **Initial Token Size**: Starts at 0; accumulates full dialogue, tool invocations, and tool results.
* `[OFFICIAL]` **Agent Ignorability**: NO. Constitutes the active conversational memory.
* `[OFFICIAL]` **Execution Updatability**: Append-only trajectory. Context compaction triggers `@hooks.on_compaction` when context ceiling is neared.
* `[OFFICIAL]` **Session Survival**: Persists indefinitely in SQLite (`~/.gemini/antigravity/conversations/<id>.db` with WAL mode). Resumable in SDK via `conversation_id`.
* `[OFFICIAL]` **Subagent Inheritance**: **ZERO INHERITANCE**. Subagents start with a completely pristine turn 0 containing only the prompt passed to `invoke_subagent`.
* `[OFFICIAL]` **Surface Parity**: Trajectory database format is shared across all surfaces.

---

### Source 7: Artifacts (`<appDataDir>\brain\<conversation-id>\`)
* `[OFFICIAL]` **Automatic Availability**: Path injected into `<artifacts>` prompt section.
* `[OFFICIAL]` **Discoverability**: Agent accesses files via standard tools (`view_file`, `list_dir`).
* `[OFFICIAL]` **Deciding Authority**: Agent / User instruction.
* `[OFFICIAL]` **Loading Stage**: Loaded when explicitly read or written.
* `[OFFICIAL]` **Initial Token Size**: 0 prompt tokens; metadata informs agent of storage rules.
* `[OFFICIAL]` **Agent Ignorability**: Agent chooses whether to author artifacts, subject to `artifactReviewMode`.
* `[OFFICIAL]` **Execution Updatability**: Fully mutable via `write_to_file` and `replace_file_content`.
* `[OFFICIAL]` **Session Survival**: Persistent on disk outside the repository tree.
* `[OFFICIAL]` **Subagent Inheritance**: Subagents can access parent artifacts only if absolute paths are explicitly provided in the dispatch prompt.
* `[OFFICIAL]` **Surface Parity**: Desktop 2.0 renders artifacts in dedicated HTML Auxiliary Panes; IDE opens artifacts in editor tabs.

---

### Source 8: Tool Results (`run_command`, `view_file`, `grep_search`, `list_dir`)
* `[OFFICIAL]` **Automatic Availability**: YES. Injected immediately following tool execution.
* `[OFFICIAL]` **Discoverability**: N/A (Delivered by execution engine).
* `[OFFICIAL]` **Deciding Authority**: Runtime tool execution harness.
* `[OFFICIAL]` **Loading Stage**: Post-tool execution step.
* `[OFFICIAL]` **Initial Token Size**: Bounded by hard tool truncation limits:
  * `view_file`: Max 46,080 bytes / 800 lines.
  * `grep_search`: Max 50 matching lines.
  * `list_dir`: Max directory items per page.
* `[OFFICIAL]` **Agent Ignorability**: Cognitive. Injected into prompt; model processes output in subsequent thinking step.
* `[OFFICIAL]` **Execution Updatability**: Immutable historical step in trajectory.
* `[OFFICIAL]` **Session Survival**: Stored in conversation SQLite database.
* `[OFFICIAL]` **Subagent Inheritance**: Isolated strictly to the agent executing the tool call.
* `[OFFICIAL]` **Surface Parity**: Identical across surfaces.

---

### Source 9: Subagent Messaging Results (`invoke_subagent`, `send_message`)
* `[OFFICIAL]` **Automatic Availability**: Delivered automatically into caller context at turn start.
* `[OFFICIAL]` **Discoverability**: Delivered via native messaging event loop.
* `[OFFICIAL]` **Deciding Authority**: Runtime messaging bus.
* `[OFFICIAL]` **Loading Stage**: Reactive wakeup upon subagent message delivery (no manual polling required).
* `[OFFICIAL]` **Initial Token Size**: Exact byte size of the transmitted message payload.
* `[OFFICIAL]` **Agent Ignorability**: Cognitive guidance.
* `[OFFICIAL]` **Execution Updatability**: Append-only message log.
* `[OFFICIAL]` **Session Survival**: Persisted in caller's SQLite trajectory.
* `[OFFICIAL]` **Subagent Inheritance**: Strict hierarchy governed by `max_subagent_depth` (default <= 3).
* `[OFFICIAL]` **Surface Parity**: Desktop 2.0 displays subagents in the live Auxiliary Pane; SDK exposes async event streams.

---

### Source 10: Model Context Protocol (MCP) Results
* `[OFFICIAL]` **Automatic Availability**: Eager tool schemas injected in prompt; lazy tool schemas declared; tool execution returns results.
* `[OFFICIAL]` **Discoverability**: System queries MCP servers via `tools/list` on session start.
* `[OFFICIAL]` **Deciding Authority**: Platform MCP client / Server config (`mcp_config.json`).
* `[OFFICIAL]` **Loading Stage**: Session initialization and tool invocation.
* `[OFFICIAL]` **Initial Token Size**: JSON schema representation of exposed MCP tools.
* `[OFFICIAL]` **Agent Ignorability**: Model decides when to invoke MCP tools.
* `[OFFICIAL]` **Execution Updatability**: Dynamic server reconnect or tool-list notifications.
* `[OFFICIAL]` **Session Survival**: Active while MCP server daemon process remains alive.
* `[OFFICIAL]` **Subagent Inheritance**: Subagents inherit declared MCP server toolkits.
* `[OFFICIAL]` **Surface Parity**: Desktop has GUI to manage and restart MCP connections; CLI and SDK configure via JSON.

---

### Source 11: Repository Files (Working Tree Code)
* `[OBSERVED]` **Automatic Availability**: **NO**. Antigravity injects ZERO file tree or code into prompt context on turn 0.
* `[OBSERVED]` **Discoverability**: Merely discoverable via file system tools (`list_dir`, `view_file`, `grep_search`).
* `[OBSERVED]` **Deciding Authority**: Agent tool invocation.
* `[OBSERVED]` **Loading Stage**: Explicit read tool execution.
* `[OBSERVED]` **Initial Token Size**: 0 tokens.
* `[OBSERVED]` **Agent Ignorability**: Full agent discretion over what files to inspect.
* `[OBSERVED]` **Execution Updatability**: Mutable via edit tools (`replace_file_content`, `write_to_file`).
* `[OFFICIAL]` **Session Survival**: Permanent on disk.
* `[OFFICIAL]` **Subagent Inheritance**: Available to all agents within workspace boundary permissions.
* `[OFFICIAL]` **Surface Parity**: IDE tracks active editor tabs and selections; Desktop/CLI require explicit tool calls.

---

### Source 12: Persistent Machine State (`brain/`, `knowledge/`, `conversations/`)
* `[OFFICIAL]` **Automatic Availability**: Out-of-band management by Language Server daemon.
* `[OFFICIAL]` **Discoverability**: Stored in `~/.gemini/antigravity/` and `~/.gemini/config/`.
* `[OFFICIAL]` **Deciding Authority**: Platform core.
* `[OFFICIAL]` **Loading Stage**: Daemon boot and workspace initialization.
* `[OFFICIAL]` **Initial Token Size**: 0 prompt tokens directly; symbol graphs cached on disk (`agyhub_summaries_proto.pb`).
* `[OFFICIAL]` **Agent Ignorability**: N/A (Platform internal).
* `[OFFICIAL]` **Execution Updatability**: Updated continuously as files and turns progress.
* `[OFFICIAL]` **Session Survival**: Fully persistent across machine reboots and application restarts.
* `[OFFICIAL]` **Subagent Inheritance**: Shared local state.
* `[OFFICIAL]` **Surface Parity**: Identical across surfaces.

---

## 4. Context Pipeline Matrix

| Source # | Context Source | Automatically Available? | Merely Discoverable? | Who Decides? | Loading Stage | Initial Overhead | Can Agent Ignore? | Survives New Session? | Survives New Subagent? |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | System Instructions | **YES** | NO | Runtime | Turn 0 / Every Turn | 1,500–3,500 tok | NO | YES (Template) | Specialized |
| **2** | Project Rules (`AGENTS.md`) | **YES** (In-scope) | NO | Language Server | Directory walk | Full file size | Cognitive only | YES (On disk) | Scope-dependent |
| **3** | Modular Rules (`.agents/rules`) | Conditional | YES | Engine / Model | Trigger match | 0 to full file | Cognitive only | YES (On disk) | Scope-dependent |
| **4** | Skills (`SKILL.md`) | Metadata only | **YES** | Model / User | On `view_file` | 20–50 tok/skill | **YES** | Trajectory only | Manifest only |
| **5** | Workspace Config (`hooks.json`)| Out-of-band | NO | Runtime | Platform start | 0 tokens | **CANNOT IGNORE**| YES (On disk) | YES (Shared) |
| **6** | Conversation Trajectory | **YES** | NO | Runtime | Continuous | Monotonic | NO | SQLite WAL DB | **ZERO (Isolated)**|
| **7** | Artifacts (`brain/`) | Path only | **YES** | Agent | On tool call | Path metadata | YES | YES (On disk) | Explicit path only |
| **8** | Tool Results | **YES** | NO | Tool Harness | Post-execution | Output (Capped) | Cognitive only | Trajectory only | Isolated to caller |
| **9** | Subagent Results | **YES** | NO | Message Bus | Turn wakeup | Message payload | Cognitive only | Trajectory only | Isolated |
| **10**| MCP Tool Declarations | **YES** | YES | Client / Server | Session start | Schema size | YES | Process lifetime| Inherited |
| **11**| Repository Files | **NO** | **YES** | Agent | On tool call | 0 tokens | YES | YES (On disk) | Full access |
| **12**| Persistent Machine State | Out-of-band | NO | Language Server | Daemon boot | 0 tokens | N/A | YES (DB / Disk) | Shared |

---

## 5. Cognitive Guidance vs. Deterministic Enforcement

A critical finding of this research is that Antigravity maintains an uncompromising separation between **Cognitive Guidance** and **Deterministic Enforcement**:

```text
┌───────────────────────────────────────────────┬───────────────────────────────────────────────┐
│ COGNITIVE GUIDANCE LAYER                      │ DETERMINISTIC ENFORCEMENT LAYER               │
│ (Shapes LLM Reasoning & Token Probabilities)  │ (Physical OS Process & Tool Interception)    │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ • System Instructions (<identity>)           │ • Lifecycle Hooks (PreToolUse, Stop in hooks) │
│ • Project Rules (AGENTS.md, GEMINI.md)       │ • SDK Safety Policies (confirm_run_command)   │
│ • Modular Rules (.agents/rules/*.md)          │ • Sandboxing (enableTerminalSandbox)          │
│ • Skills Runbooks (SKILL.md)                  │ • Native Test Process Ratchet (Exit Code 0)   │
│ • Active Task Memory (ACTIVE_CONTEXT.md)      │ • Tool Argument Mutators (overwrite in hooks) │
├───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ Failure Mode: LLM rationalizes away rule;     │ Failure Mode: Hook returns "deny" or non-zero │
│ hallucinates adherence; bypasses guidelines.  │ exit code; tool execution is hard-blocked.    │
└───────────────────────────────────────────────┴───────────────────────────────────────────────┘
```

> **The Architectural Axiom:**  
> Rules written in Markdown are cognitive guidelines, not physical boundaries. Any invariant that must never be violated under any circumstance (such as protected zone immutability or test verification) **must be enforced by deterministic hooks, process exit codes, or tool-level policies, never by prompt instructions alone**.
