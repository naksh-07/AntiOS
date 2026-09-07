# Google Antigravity Platform Operating Model
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: High-Confidence Forensic Analysis  
**Primary Sources**: Builtin Skills (`antigravity_guide`, `agy-customizations`), SDK Reference (`google-antigravity`), Runtime Configuration (`~/.gemini/config/`), and Binary Execution Traces (`language_server.exe` / `localharness`).  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. System Architecture & Topology

Google Antigravity is not a monolithic application or a simple wrapper around an LLM API. It is a distributed, multi-tiered client-server development platform comprising:

1. **The Core Language Server Engine (`language_server.exe` / `localharness`)**:
   - Compiled Go/C++ binary (internal package `google3/third_party/jetski/cortex`).
   - Acts as the central Language Server Protocol (LSP) and Model Context Protocol (MCP) host.
   - Manages process trees, terminal multiplexers, filesystem monitors (`fsnotify`), Git worktree bindings, tool policy evaluation, and token budget counters.
   - Connects upstream to Gemini foundation models via high-throughput gRPC/REST conduits, utilizing internal `gemini-3.7-flash` or `gemini-3.8-flash` with adaptive thinking budgets.

2. **The Four Unified Presentation Surfaces**:
   - **Antigravity 2.0 (Desktop Electron Application)**: Parallel multi-turn conversational desktop environment providing chat canvas, auxiliary sidebars (Subagents, Background Tasks, Artifacts, Files Changed, Terminals), and project permission management.
   - **Antigravity IDE (VS Code Fork)**: AI-first integrated development environment integrating passive tab autocomplete, instructive inline edits (`Ctrl+I` / `Cmd+I`), code lenses, and sidebar chat.
   - **Antigravity CLI (`agy`)**: Terminal TUI and headless automation engine capable of streaming NDJSON tool calls and completions over stdio (`--output-format stream-json`).
   - **Antigravity Python SDK (`google-antigravity`)**: Programmatic async library for running, configuring, and leasing agents in test harnesses and external pipelines (`async with Agent(config) as agent:`).

All four surfaces share identical underlying runtime primitives, customization discovery engines, and execution loops.

```
                      ┌─────────────────────────────────────────┐
                      │    Google Antigravity Core Engine       │
                      │ (language_server.exe / localharness)    │
                      └────┬──────────────┬───────────────┬─────┘
                           │              │               │
            ┌──────────────▼───┐   ┌──────▼────────┐   ┌──▼────────────────┐
            │ Antigravity 2.0  │   │  Antigravity  │   │    agy CLI        │
            │ Desktop Electron │   │   IDE (VSCode)│   │ (Headless/Stream) │
            └──────────────┬───┘   └──────┬────────┘   └──┬────────────────┘
                           │              │               │
                           └──────────────┼───────────────┘
                                          │
                           ┌──────────────▼────────────────┐
                           │    Python SDK Engine Binding   │
                           │  (google-antigravity / PyPI)   │
                           └───────────────────────────────┘
```

---

## 2. Exhaustive Analysis of the 22 Platform Mechanisms

Every mechanism is evaluated across 10 standardized criteria, with claims classified under strict evidence tiers:
- `[FACT]`: Official documentation or verified code artifact.
- `[OBSERVED]`: Witnessed in runtime files, system prompt headers, or execution logs.
- `[INFERENCE]`: Deduced logically from multiple converging technical facts.
- `[HYPOTHESIS]`: Grounded theoretical proposal.
- `[UNKNOWN]`: Unverified internal implementation detail.

---

### Mechanism 1: Workspace & Project Model

1. **What is it?**: `[FACT]` The abstraction representing active local filesystem directories and associated settings under which an agent operates. In Desktop, a project maps folders (`folderUri`) to metadata stored in `~/.gemini/config/projects/<uuid>.json`.
2. **When does Antigravity load/use it?**: `[OBSERVED]` Loaded at startup. The language server resolves the working directory, locates `.git` or `.agents/`, and sets the workspace boundary.
3. **Who decides whether it is used?**: `[FACT]` The user (via GUI directory open, CLI execution root, or SDK configuration).
4. **What context does the agent receive?**: `[OBSERVED]` Injected into system prompt `<user_information>`:
   ```xml
   <user_information>
   The USER's OS version is windows.
   The user has 1 active workspaces... [URI] -> [CorpusName]
   App Data Directory: C:\Users\Suraj\.gemini\antigravity
   Conversation ID: ...
   </user_information>
   ```
5. **Can it affect agent behavior?**: `[FACT]` Yes. Bounds tool path resolution, anchors relative paths, controls permission policies, and scopes rule discovery.
6. **Can it observe execution?**: `[OBSERVED]` Yes. File watching (`fsnotify`) tracks all filesystem modifications and git branch mutations.
7. **Can it enforce behavior?**: `[FACT]` Yes. Through `policy.workspace_only()` or `nonWorkspaceFileAccessPolicy: AGENT_SETTING_POLICY_DENY`, it physically blocks tools (`view_file`, `create_file`, `edit_file`) from operating outside the workspace root.
8. **Can it persist state?**: `[OBSERVED]` Persists project settings (sandbox, policies, permission allowlists) in `~/.gemini/config/projects/<uuid>.json`.
9. **What are its limitations?**: `[OBSERVED]` Windows cross-drive path handling can break commonpath checks. Context is shared across all workspace folders if multiple roots are opened.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Treat `workspacePaths[0]` as the immutable anchor; mount declarative project adapters (`antios.config.json`) strictly within this tree.

---

### Mechanism 2: Agent Lifecycle

1. **What is it?**: `[FACT]` The full operational lifecycle of an autonomous or interactive AI entity (instantiation, configuration, turn loop, tool execution, context compaction, and termination).
2. **When does Antigravity load/use it?**: `[FACT]` Instantiated upon conversation creation, tab launch, or programmatic subagent dispatch.
3. **Who decides whether it is used?**: `[FACT]` User prompt, slash command, or parent agent dispatch.
4. **What context does the agent receive?**: `[FACT]` System prompt, persona, tool definitions, rules, progressive skill summaries, and turn history.
5. **Can it affect agent behavior?**: `[FACT]` Yes. Operational modes (`AUTONOMOUS` vs `INTERACTIVE`) determine whether the agent prompts the user or drives tasks to conclusion.
6. **Can it observe execution?**: `[FACT]` Native logging, token usage tracking (`prompt_token_count`, `candidates_token_count`, `thoughts_token_count`), and streaming thought/tool deltas.
7. **Can it enforce behavior?**: `[FACT]` Enforces budget ceilings (`BudgetConfig`: `max_model_calls`, `max_tool_calls`, `max_total_tokens`).
8. **Can it persist state?**: `[FACT]` Ephemeral in-memory process; state delegates to the conversation database and filesystem artifacts.
9. **What are its limitations?**: `[INFERENCE]` Bounded by context window size; long runs inevitably suffer attention degradation unless decomposed.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Wrap the lifecycle using physical verification gates, ensuring no agent can conclude without passing deterministic tests.

---

### Mechanism 3: Conversation Lifecycle

1. **What is it?**: `[FACT]` The stateful representation of a multi-turn interaction between a user (or parent agent) and the agent.
2. **When does Antigravity load/use it?**: `[OBSERVED]` Initialized on "New Conversation"; resumed when passing `conversation_id` with an existing storage directory.
3. **Who decides whether it is used?**: `[FACT]` The platform or user.
4. **What context does the agent receive?**: `[FACT]` Ordered message trajectory: user prompts, model thoughts, tool calls, tool results, and system injection events.
5. **Can it affect agent behavior?**: `[FACT]` Directly determines model reasoning; prior outputs establish conversational ground truth.
6. **Can it observe execution?**: `[OBSERVED]` Persists turns, steps, and tool execution states in real-time.
7. **Can it enforce behavior?**: `[FACT]` Enforces sequential turn order and triggers context compaction when token thresholds are exceeded.
8. **Can it persist state?**: `[OBSERVED]` Fully persisted in `C:\Users\<User>\.gemini\antigravity\conversations\<id>.db` via SQLite with WAL mode.
9. **What are its limitations?**: `[OBSERVED]` Once written, past context cannot be modified in-memory; bloated conversations dilute instruction adherence.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Maintain append-only disk transaction logs (`handoff.md`, `progress.md`) that survive conversation restarts and compaction.

---

### Mechanism 4: Context Construction

1. **What is it?**: `[FACT]` The dynamic prompt compilation pipeline that synthesizes the LLM prompt payload on every turn.
2. **When does Antigravity load/use it?**: `[FACT]` Reconstructed immediately before every foundation model inference call.
3. **Who decides whether it is used?**: `[FACT]` Language Server runtime (`cortex`).
4. **What context does the agent receive?**: `[OBSERVED]` System identity, `<user_information>`, eager/lazy MCP declarations, `<skills>` catalog, active rules, `<artifacts>` instructions, conversation history, and hook-injected ephemeral messages.
5. **Can it affect agent behavior?**: `[FACT]` Completely dictates reasoning boundaries, tool availability, and operational directives.
6. **Can it observe execution?**: `[FACT]` Calculates token counts across prompt, candidate, and thinking tokens.
7. **Can it enforce behavior?**: `[FACT]` Tool omission from prompt prevents the model from attempting unauthorized operations.
8. **Can it persist state?**: `[OBSERVED]` Persisted turn-by-turn in the SQLite database and transcript files.
9. **What are its limitations?**: `[FACT]` Hard context limits (1M / 2M tokens). Excessive prompt injections create distraction and degrade reasoning.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Use `PreInvocation` hook injection (`injectSteps[].ephemeralMessage`) to inject critical project alerts just-in-time before reasoning.

---

### Mechanism 5: Workspace Understanding

1. **What is it?**: `[OBSERVED]` Semantic and lexical codebase indexing performed by the Language Server (ripgrep, AST symbol tracking, directory graphs).
2. **When does Antigravity load/use it?**: `[OBSERVED]` Spun up in the background upon workspace initialization.
3. **Who decides whether it is used?**: `[FACT]` Platform core.
4. **What context does the agent receive?**: `[OBSERVED]` The agent does NOT receive an automatic dump of the codebase. It receives only root paths and must actively explore via `list_dir`, `grep_search`, or `view_file`.
5. **Can it affect agent behavior?**: `[OBSERVED]` Accelerates symbol location and navigation via high-performance ripgrep.
6. **Can it observe execution?**: `[OBSERVED]` Tracks file changes and git worktrees.
7. **Can it enforce behavior?**: `[OBSERVED]` Informational only; does not enforce.
8. **Can it persist state?**: `[OBSERVED]` Local index caches stored in `~/.gemini/antigravity/knowledge/`.
9. **What are its limitations?**: `[OBSERVED]` Provides zero-shot memory to the model; the agent must expend tool calls to locate files.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Provide deterministic project wayfinding manifests (`antios.config.json`) so the agent routes to subsystems without exploratory searches.

---

### Mechanism 6: AGENTS.md / GEMINI.md

1. **What is it?**: `[FACT]` Hierarchical markdown rule files placed directly in directories to govern agent behavior within that directory tree.
2. **When does Antigravity load/use it?**: `[FACT]` Discovered by walking up from the current working directory to the repository root, or when files within those directories are opened or modified.
3. **Who decides whether it is used?**: `[FACT]` Discovered automatically by runtime; authored by developers.
4. **What context does the agent receive?**: `[FACT]` Full markdown contents injected into the context window under active rules. Deduplicated by resolved path. Does not support frontmatter.
5. **Can it affect agent behavior?**: `[FACT]` Strongly guides style, architectural rules, forbidden packages, and conventions.
6. **Can it observe execution?**: `[FACT]` No.
7. **Can it enforce behavior?**: `[INFERENCE]` Soft guidance only. Models can hallucinate past markdown text under pressure.
8. **Can it persist state?**: `[FACT]` Persisted in VCS.
9. **What are its limitations?**: `[FACT]` Consumes tokens unconditionally; lacks programmable logic or interception hooks.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Standardize core project governance in root `AGENTS.md`, and reinforce every critical constraint with deterministic hooks in `hooks.json`.

---

### Mechanism 7: Rules (`.agents/rules/*.md`)

1. **What is it?**: `[FACT]` Modular rule files inside `.agents/rules/` supporting frontmatter triggers (e.g. `always_on`, `trigger: model_decision`).
2. **When does Antigravity load/use it?**: `[FACT]` `always_on` rules load at startup; `model_decision` rules load via progressive disclosure when triggered.
3. **Who decides whether it is used?**: `[FACT]` Runtime or model trigger match.
4. **What context does the agent receive?**: `[FACT]` Rule summary or full markdown text once triggered.
5. **Can it affect agent behavior?**: `[FACT]` Highly targeted behavioral guidance.
6. **Can it observe execution?**: `[FACT]` No.
7. **Can it enforce behavior?**: `[INFERENCE]` Soft guidance only.
8. **Can it persist state?**: `[FACT]` Static repository files.
9. **What are its limitations?**: `[FACT]` Prone to context loss during token pruning; depends on model compliance.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Store domain-specific engineering policies (`antios-engineer`, `antios-debug`) in rules.

---

### Mechanism 8: Skills (`.agents/skills/`, user skills, builtin skills)

1. **What is it?**: `[FACT]` Modular capability packages structured as a directory containing `SKILL.md` (with YAML frontmatter `name` and `description`) and optional `scripts/`, `examples/`, `resources/`, and `references/`.
2. **When does Antigravity load/use it?**: `[FACT]` Uses **Progressive Disclosure**. At startup, only `name`, `path`, and `description` are loaded into `<skills>`. The full `SKILL.md` is loaded ONLY when explicitly activated via `view_file` or slash command.
3. **Who decides whether it is used?**: `[FACT]` Model prompt match against `description`, or explicit user invocation (`/skill-name`).
4. **What context does the agent receive?**: `[OBSERVED]` Lightweight catalog summary initially. Full step-by-step procedures upon activation. Bulky documentation in `references/` read on demand.
5. **Can it affect agent behavior?**: `[FACT]` Completely dictates complex multi-step procedural execution and tool usage patterns.
6. **Can it observe execution?**: `[FACT]` The skill text cannot observe; scripts inside `scripts/` can execute diagnostics and emit logs.
7. **Can it enforce behavior?**: `[INFERENCE]` Soft procedural enforcement.
8. **Can it persist state?**: `[FACT]` Scripts can write state to disk.
9. **What are its limitations?**: `[FACT]` Priority resolution: Workspace Project > Declared JSON > Global Config > Built-in. Must adhere to strict directory layout.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Package the AntiOS control plane (`antios`, `antios-engineer`, `antios-verifier`) as native workspace skills, ensuring zero external dependencies.

---

### Mechanism 9: Lifecycle Hooks (`hooks.json`)

1. **What is it?**: `[FACT]` Deterministic shell execution hooks defined in `.agents/hooks.json` or `plugins/<name>/hooks.json` that intercept the agent loop.
2. **When does Antigravity load/use it?**: `[FACT]` Loaded at startup. Synchronously triggered at 5 lifecycle events:
   - `PreInvocation`: Before model reasoning.
   - `PreToolUse`: Before tool execution (matched via regex).
   - `PostToolUse`: After tool execution completes.
   - `PostInvocation`: After tool steps finish.
   - `Stop`: When the agent execution loop attempts to conclude.
3. **Who decides whether it is used?**: `[FACT]` Language server automatically invokes them; hook scripts emit decisions via stdio.
4. **What context does the agent receive?**: `[FACT]` Hooks receive camelCase JSON on `stdin`:
   - Common fields: `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`, `modelName`.
   - `PreToolUse`: `toolCall: {name, args}`, `stepIdx`.
   - `PostToolUse`: `stepIdx`, `error`.
   - `PreInvocation`/`PostInvocation`: `invocationNum`, `initialNumSteps`.
   - `Stop`: `executionNum`, `terminationReason`, `error`, `fullyIdle`.
5. **Can it affect agent behavior?**: `[FACT]` **Absolute authority.**
   - `PreToolUse` can rewrite arguments via shallow `overwrite: {...}` or block via `decision: "deny"`.
   - `PreInvocation` can inject steps via `injectSteps: [{"ephemeralMessage": "..."}]`.
   - `Stop` can reject termination via `decision: "continue"` with `reason: "..."`.
6. **Can it observe execution?**: `[FACT]` Full visibility over every tool call, argument, return code, and lifecycle event.
7. **Can it enforce behavior?**: `[FACT]` **YES. This is the only unbypassable physical enforcement mechanism in Antigravity.**
8. **Can it persist state?**: `[FACT]` Yes. Hook scripts run as independent processes (`type: "command"`) and can write to SQLite, JSON, or disk.
9. **What are its limitations?**: `[FACT]`
   - Only `type: "command"` is supported.
   - Runs synchronously, blocking the agent loop (default 30s timeout).
   - **Crucial Ground-Truth Discovery**: Hooks execute with `cwd = .agents/`, NOT the repository root (`hooks.md:L126`).
10. **What can AntiOS safely build around it?**: `[FACT]` AntiOS bases its core security on this mechanism: `pre_tool_guard.py` (`PreToolUse`) and `stop_gate.py` (`Stop`).

---

### Mechanism 10: Custom Agents & Subagents

1. **What is it?**: `[FACT]` Hierarchical multi-agent delegation mechanism (`invoke_subagent`, `start_subagent`, `manage_subagents`).
2. **When does Antigravity load/use it?**: `[FACT]` When parent calls delegation tools or SDK launches child agents.
3. **Who decides whether it is used?**: `[FACT]` Parent agent or user command.
4. **What context does the agent receive?**: `[FACT]` **Strict context isolation.** Subagents do NOT inherit parent conversation history. They receive only the dispatch prompt, system instructions, active rules, and granted tools.
5. **Can it affect agent behavior?**: `[FACT]` Assigns dedicated personas, scoped toolsets, and isolated workspaces (`Workspace='branch'`).
6. **Can it observe execution?**: `[FACT]` Parent receives asynchronous progress messages via `send_message` or completion notifications.
7. **Can it enforce behavior?**: `[FACT]` Enforces depth ceilings (`max_subagent_depth`) and allowlists (`allowed_subagents`).
8. **Can it persist state?**: `[OBSERVED]` Subagent conversations persist in dedicated SQLite databases (`conversations/<subagent-id>.db`).
9. **What are its limitations?**: `[OBSERVED]` Subagent communication is strictly message-based; parent must actively reconcile results upon branch completion.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Implement Maker-Checker workflows: parent dispatches an un-biased `antios-verifier` subagent to audit git diffs and execute physical tests.

---

### Mechanism 11: Artifacts (`brain/<conversation-id>/...`)

1. **What is it?**: `[FACT]` Structured markdown and media documents created in `<appDataDir>\brain\<conversation-id>\`.
2. **When does Antigravity load/use it?**: `[FACT]` Created when drafting plans (`implementation_plan.md`), tracking tasks (`task.md`), or documenting walkthroughs (`walkthrough.md`).
3. **Who decides whether it is used?**: `[FACT]` Agent decision based on prompt instructions, or user command.
4. **What context does the agent receive?**: `[OBSERVED]` Injected `<artifacts>` block specifying storage paths, formatting rules (alerts, carousels, mermaid), and presentation guidelines.
5. **Can it affect agent behavior?**: `[FACT]` Encourages structured, non-redundant reporting in chat.
6. **Can it observe execution?**: `[OBSERVED]` Rendered live in the Desktop Auxiliary Pane.
7. **Can it enforce behavior?**: `[FACT]` Subject to `artifactReviewMode`: if review is required, execution pauses until the user approves the artifact.
8. **Can it persist state?**: `[OBSERVED]` Fully persisted on the local filesystem outside the workspace.
9. **What are its limitations?**: `[FACT]` Stored outside the repository; not tracked in git unless explicitly copied into the repo.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Use artifacts for human-facing reports while keeping project-critical engineering state (`handoff.md`, `progress.md`) in repository files.

---

### Mechanism 12: Terminal & Tool Execution

1. **What is it?**: `[FACT]` The actuation layer: `run_command`, `view_file`, `create_file`, `edit_file`, `replace_file_content`, `list_dir`, `grep_search`.
2. **When does Antigravity load/use it?**: `[FACT]` Active by default when capabilities permit.
3. **Who decides whether it is used?**: `[FACT]` The model proposes tool calls; hooks and policies evaluate execution.
4. **What context does the agent receive?**: `[OBSERVED]` Tool execution output. Large outputs (>46 KB) are truncated and written to `.system_generated/steps/<stepIdx>/output.txt`.
5. **Can it affect agent behavior?**: `[FACT]` Core feedback loop; tool stdout/stderr informs the next model step.
6. **Can it observe execution?**: `[FACT]` Full real-time stream of process outputs and return codes.
7. **Can it enforce behavior?**: `[FACT]` Governed by `autoExecutionPolicy` and security policies (`policy.confirm_run_command()`).
8. **Can it persist state?**: `[OBSERVED]` Invocations, arguments, and outputs are committed to SQLite and transcript files.
9. **What are its limitations?**: `[OBSERVED]` Shell commands execute via `cmd.exe` or PowerShell on Windows; shell state (env vars, cwd) does not persist across separate tool calls.
10. **What can AntiOS safely build around it?**: `[FACT]` Enforce test execution ratchets via `run_command_safe` in `stop_gate.py`, requiring clean exit codes before completion.

---

### Mechanism 13: Model Context Protocol (MCP)

1. **What is it?**: `[FACT]` Standardized tool integration layer supporting local Stdio and remote SSE transports.
2. **When does Antigravity load/use it?**: `[FACT]` Configured in `~/.gemini/config/mcp_config.json` or `plugins/<name>/mcp_config.json`.
3. **Who decides whether it is used?**: `[FACT]` Developer configured; model invoked.
4. **What context does the agent receive?**: `[OBSERVED]` **Eager vs. Lazy Loading Architecture**:
   - **Eager Tools**: Full JSON schemas registered natively in the prompt under `mcp_<server>_<tool>`.
   - **Lazy Tools**: Simple server list in prompt header. Full schemas written to disk in `~/.gemini/antigravity/mcp/<server>/<tool>.json`. Model calls them via `call_mcp_tool(ServerName, ToolName, Arguments)`, saving context tokens.
5. **Can it affect agent behavior?**: `[FACT]` Grants access to specialized external capabilities (Chrome DevTools, GitHub, databases).
6. **Can it observe execution?**: `[FACT]` Language server proxies all MCP tool traffic.
7. **Can it enforce behavior?**: `[FACT]` Governed by allowlists/denylists and safety policies.
8. **Can it persist state?**: `[FACT]` State managed by the external MCP server process.
9. **What are its limitations?**: `[FACT]` Slow stdio startup or crashing servers block tool dispatch.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Expose custom engineering intelligence and verification tools via local stdio MCP servers without modifying platform core.

---

### Mechanism 14: Permissions & Security Policies

1. **What is it?**: `[FACT]` 9-tier priority access control system governing command execution, file modifications, and network access.
2. **When does Antigravity load/use it?**: `[FACT]` Evaluated prior to every tool call.
3. **Who decides whether it is used?**: `[FACT]` Configured globally in `config.json`, per-project in `projects/<id>.json`, or via SDK policies.
4. **What context does the agent receive?**: `[OBSERVED]` Standardized error message if blocked: `"tool call denied by policy: <reason>"`.
5. **Can it affect agent behavior?**: `[FACT]` Forces model to pivot when actions are denied.
6. **Can it observe execution?**: `[FACT]` Evaluates predicates on incoming tool arguments.
7. **Can it enforce behavior?**: `[FACT]` Hard platform gate; denied tools never reach the OS process table.
8. **Can it persist state?**: `[OBSERVED]` "Always Allow" grants persist in project configuration files.
9. **What are its limitations?**: `[OBSERVED]` Permission lists can accumulate obsolete command paths over time.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Complement platform permissions with declarative `antios.config.json` policies enforced at the hook level.

---

### Mechanism 15: Browser & Computer Capabilities

1. **What is it?**: `[FACT]` Native headless browser automation (Playwright/CDP) and desktop inspection tools (`desktop-webview-reviewer`).
2. **When does Antigravity load/use it?**: `[FACT]` Loaded when browser plugins or webview review tools are active.
3. **Who decides whether it is used?**: `[FACT]` Model selection based on user request.
4. **What context does the agent receive?**: `[OBSERVED]` Accessibility trees, DOM snapshots, console messages, network request logs, and screenshot artifacts.
5. **Can it affect agent behavior?**: `[FACT]` Enables end-to-end frontend verification and UI debugging.
6. **Can it observe execution?**: `[OBSERVED]` Captures console errors, failed network requests, and visual layout regressions.
7. **Can it enforce behavior?**: `[FACT]` Governed by `browserJsExecutionPolicy` and domain allowlists.
8. **Can it persist state?**: `[OBSERVED]` Screenshots and video recordings stored in artifacts.
9. **What are its limitations?**: `[OBSERVED]` Ingesting full DOM trees consumes massive token context.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Integrate browser assertions into verification suites to prove UI correctness before Stop Gate clearance.

---

### Mechanism 16: Planning & Execution Behavior

1. **What is it?**: `[FACT]` Two-phase workflow: the agent enters Planning Mode to draft an implementation plan, awaits approval, and then executes.
2. **When does Antigravity load/use it?**: `[FACT]` Active by default for complex or destructive requests.
3. **Who decides whether it is used?**: `[FACT]` User toggle in chat canvas or agent self-regulation based on instructions.
4. **What context does the agent receive?**: `[OBSERVED]` Guidelines directing creation of `implementation_plan.md` and subsequent `walkthrough.md`.
5. **Can it affect agent behavior?**: `[FACT]` Prevents hasty coding; mandates structural decomposition before implementation.
6. **Can it observe execution?**: `[OBSERVED]` UI tracks plan progress with interactive checkmarks.
7. **Can it enforce behavior?**: `[FACT]` In review mode, execution halts until user approves the plan.
8. **Can it persist state?**: `[OBSERVED]` Stored in `brain/<id>/implementation_plan.md`.
9. **What are its limitations?**: `[OBSERVED]` In autonomous or turbo modes, agents may bypass formal planning unless constrained by rules or hooks.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Enforce plan-before-change at the hook level: `PreToolUse` can deny file modifications if no approved plan exists.

---

### Mechanism 17: Verification Behavior

1. **What is it?**: `[FACT]` Procedures by which the agent validates changes before task completion.
2. **When does Antigravity load/use it?**: `[FACT]` Executed post-implementation prior to task handoff.
3. **Who decides whether it is used?**: `[FACT]` Agent guidelines and Stop hooks.
4. **What context does the agent receive?**: `[FACT]` Test runner outputs, compiler messages, and linter exit codes.
5. **Can it affect agent behavior?**: `[FACT]` Test failures force the agent into diagnostic and repair loops.
6. **Can it observe execution?**: `[FACT]` Observes subprocess exit codes and test error traces.
7. **Can it enforce behavior?**: `[FACT]` **Soft in the LLM; HARD when backed by the Stop Gate hook.**
8. **Can it persist state?**: `[OBSERVED]` Documented in walkthrough artifacts.
9. **What are its limitations?**: `[INFERENCE]` Unassisted LLMs suffer from confirmation bias (assuming tests pass without running them).
10. **What can AntiOS safely build around it?**: `[FACT]` AntiOS's `evaluate_stop_gate()` in `gate.py` runs tests in an independent subprocess, eliminating model self-certification.

---

### Mechanism 18: Task Continuation & Fresh-Session Behavior

1. **What is it?**: `[FACT]` Mechanism for resuming long-running engineering missions across conversation boundaries or crashes.
2. **When does Antigravity load/use it?**: `[FACT]` Resumed by selecting an existing conversation or specifying `conversation_id`.
3. **Who decides whether it is used?**: `[FACT]` User or orchestrator.
4. **What context does the agent receive?**: `[FACT]` Full trajectory replay from SQLite in resumed sessions; ZERO conversational history in fresh sessions.
5. **Can it affect agent behavior?**: `[FACT]` Resumed agents continue existing plans; fresh agents start from scratch.
6. **Can it observe execution?**: `[OBSERVED]` Reads prior tool calls and results.
7. **Can it enforce behavior?**: `[OBSERVED]` Prevents repeating known failures if present in replayed history.
8. **What are its limitations?**: `[INFERENCE]` Long resumed sessions suffer from context bloat; fresh sessions have total amnesia.
9. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Maintain a physical, standardized 5-part `handoff.md` in the repository root, allowing a fresh agent to resume work instantly with zero prior context.

---

### Mechanism 19: Teamwork & Multi-Agent Mechanisms

1. **What is it?**: `[FACT]` Native collaborative multi-agent architecture built into `language_server.exe` (`google3/.../cortex/customizations/builtin/teamwork`). Features archetypes: Sentinel, Orchestrator, Explorer, Worker, Reviewer, Challenger, Auditor, Victory Auditor.
2. **When does Antigravity load/use it?**: `[FACT]` Invoked via `/teamwork` slash command or programmatic multi-agent dispatch.
3. **Who decides whether it is used?**: `[FACT]` User or orchestrator.
4. **What context does the agent receive?**: `[FACT]` Specialized archetype prompts enforcing hard boundaries:
   - `DISPATCH-ONLY Orchestrator`: Forbidden from writing code or running tests.
   - `Victory Auditor`: Zero-shared-context validator verifying implementation against `ORIGINAL_REQUEST.md`.
5. **Can it affect agent behavior?**: `[FACT]` Transforms ad-hoc prompting into disciplined multi-agent workstream execution.
6. **Can it observe execution?**: `[FACT]` Sentinel runs recurring cron checks (`*/8 * * * *` progress, `*/10 * * * *` liveness).
7. **Can it enforce behavior?**: `[FACT]` Enforces concurrency limits ($\le 4$), depth ceilings ($\le 10$), and 4-tier milestone gating.
8. **Can it persist state?**: `[FACT]` Manages shared state files: `ORIGINAL_REQUEST.md`, `PROJECT.md`, `SCOPE.md`, `DEAD_ENDS.md`, `GATE_STATUS.md`.
9. **What are its limitations?**: `[OBSERVED]` Extremely resource- and token-heavy.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` The `adaptive-orchestrator` skill replicates Teamwork's governance rigor (dead-end memory, victory audit, dispatch-only orchestration) in a lightweight, resource-capped model.

---

### Mechanism 20: Persistent Project-Level Configuration

1. **What is it?**: `[FACT]` Machine-local project settings overriding global defaults, stored in `~/.gemini/config/projects/<uuid>.json`.
2. **When does Antigravity load/use it?**: `[OBSERVED]` Loaded whenever the active workspace matches the project URI.
3. **Who decides whether it is used?**: `[FACT]` User configures via GUI; runtime loads automatically.
4. **What context does the agent receive?**: `[OBSERVED]` Indirectly via adjusted runtime execution policies.
5. **Can it affect agent behavior?**: `[FACT]` Modifies `fileAccessPolicy`, `sandboxMode`, `autoExecutionPolicy`, and permission grants.
6. **Can it observe execution?**: `[OBSERVED]` Stores timestamps of updates.
7. **Can it enforce behavior?**: `[FACT]` Enforces terminal sandboxing and auto-execution rules.
8. **Can it persist state?**: `[OBSERVED]` Persisted as JSON in `projects/<uuid>.json`.
9. **What are its limitations?**: `[OBSERVED]` Machine-local; NOT committed to version control or shared across developers.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Store authoritative project policies in `antios.config.json` inside the git repository, guaranteeing identical behavior across all environments.

---

### Mechanism 21: CLI vs Desktop vs IDE Differences

1. **What is it?**: `[FACT]` The three operational surfaces supported by Antigravity:
   - **CLI (`agy`)**: Terminal-based TUI for fast, streamable agent execution.
   - **Desktop (Antigravity 2.0)**: Standalone Electron app with Chat Canvas and Auxiliary Panes.
   - **Antigravity IDE**: AI-first integrated editor (VS Code fork) with autocomplete, inline command (`Ctrl+I`), and visual diffs.
2. **When does Antigravity load/use it?**: `[FACT]` Determined by launched executable.
3. **Who decides whether it is used?**: `[FACT]` Developer choice.
4. **What context does the agent receive?**: `[FACT]` All three share the identical core Language Server and capabilities, differing only in surface-specific path metadata:
   - CLI: `transcriptPath` references `antigravity-cli/`
   - Desktop: references `antigravity/`
   - IDE: references `antigravity-ide/`
5. **Can it affect agent behavior?**: `[FACT]` CLI emphasizes concise streamable text; Desktop leverages artifacts; IDE interacts with editor buffers and compiler diagnostics.
6. **Can it observe execution?**: `[FACT]` IDE observes active editor tabs and cursor; Desktop observes auxiliary panes; CLI observes terminal streams.
7. **Can it enforce behavior?**: `[FACT]` Hook and policy enforcement is identical across all surfaces.
8. **Can it persist state?**: `[FACT]` CLI in `antigravity-cli/settings.json`; Desktop/IDE in `config/config.json`.
9. **What are its limitations?**: `[FACT]` CLI cannot render HTML widgets natively; IDE requires a full VS Code environment.
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Remain 100% surface-agnostic by implementing all governance via standard files (`.agents/`), shell hooks (`hooks.json`), and standard terminal runners.

---

### Mechanism 22: Current Supported Extension Surfaces

1. **What is it?**: `[FACT]` The complete matrix of extensibility surfaces:
   - **Skills** (`.agents/skills/<name>/SKILL.md`)
   - **Rules** (`GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md`)
   - **Plugins** (`plugins/<name>/plugin.json`) bundling skills, rules, hooks, and MCP configs
   - **Hooks** (`.agents/hooks.json`) executing shell commands on lifecycle events
   - **MCP Servers** (`mcp_config.json`) exposing custom tools and resources
   - **JSON Configs** (`skills.json`, `plugins.json`) registering custom paths and inheritance
   - **Sidecars** (`enable_sidecars`, `ManageSidecar`) auxiliary background microservices
2. **When does Antigravity load/use it?**: `[FACT]` Loaded at Language Server startup following strict priority resolution.
3. **Who decides whether it is used?**: `[FACT]` Developers and users via configuration files.
4. **What context does the agent receive?**: `[FACT]` Merged skills catalog, active rules, and injected tool schemas.
5. **Can it affect agent behavior?**: `[FACT]` Specializes the generic LLM into a domain-specific engineering agent.
6. **Can it observe execution?**: `[FACT]` Hooks and MCP servers observe tool arguments and execution states.
7. **Can it enforce behavior?**: `[FACT]` Hooks enforce deterministic guardrails; rules and skills guide procedural behavior.
8. **Can it persist state?**: `[FACT]` Persisted on disk in VCS or global config.
9. **What are its limitations?**: `[FACT]` Extensions cannot modify the compiled Go binary (`language_server.exe`).
10. **What can AntiOS safely build around it?**: `[HYPOTHESIS]` Use ONLY the officially supported extension surfaces (`.agents/skills/`, `.agents/hooks.json`, `AGENTS.md`), ensuring complete forward compatibility with future Antigravity releases.
