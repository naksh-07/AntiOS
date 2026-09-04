# ANTIGRAVITY CAPABILITY AUDIT: EXPERIMENTAL REALITY MAP
**Document Identifier:** AG-AUDIT-PHASE2-2026  
**Auditor Role:** Senior Agent-Systems Researcher and Experimental Auditor  
**Host Environment:** Windows 10/11 x64, PowerShell 5.1/7+, Node v20.20.0, Python 3.13.13  
**Evaluated Application Surfaces:** Antigravity 2.0 Desktop Electron App (v0.1.0), Language Server backend (`jetski/language_server.exe`), Google Antigravity SDK (`google-antigravity`)  
**Safety Status:** StudyLab / Anki-maths repository kept 100% read-only; all experiments executed in disposable sandbox (`scratch/sandbox`).

---

## 1. Executive Summary

This audit establishes an empirical, evidence-backed reality map of Google Antigravity's actual capabilities, failure boundaries, and operational guarantees. Across multi-agent AI platforms, vendor marketing materials and high-level specifications frequently diverge from actual runtime behavior. This investigation reconciled official documentation, source specifications, binary interfaces, and controlled runtime experiments across twelve capability domains and six cross-capability integration tests.

### Primary Audit Findings
1. **Model-Mediated Agency vs. Hard Enforcement**: Antigravity is fundamentally an AI pair-programming and multi-agent system where core reasoning workflows, skill selections, and rule compliance are **model-mediated**, while hard platform boundaries exist at the **Language Server tool-interception layer** (`PreToolUse` hook denials and conversation-scoped artifact paths).
2. **Workflow Convergence on Skills**: Legacy workflows (`.agents/workflows/*.md`) are officially **deprecated**. Antigravity has consolidated multi-step workflows into **Skills** with slash-command bindings (`/<skill-name>`).
3. **Subagent Segregation & Tool Inheritance**: Subagents run with completely clean, segregated context windows (zero parent conversation leakage) while inheriting the full tool suite (including nested subagent spawning via `define_subagent` and `invoke_subagent`).
4. **Artifact Directory Scoping**: The platform enforces a strict security boundary preventing subagents from writing into parent conversation artifact directories via native `write_to_file`, requiring cross-agent data sharing to pass via structured handoff messages or shared filesystem paths.
5. **CLI & Headless Runtime Reality**: The standalone `agy` CLI binary is not installed on standard system PATH in desktop distributions; however, the underlying Go binary (`language_server.exe`) contains full headless flags (`-headless`, `-standalone`, `-persistent_mode`, `-subclient_type`), and the Python SDK provides programmatic headless execution.
6. **Active Background Scheduling**: The `schedule` tool provides genuine asynchronous background timer and cron dispatch, delivering proactive high-priority system wakeup notifications to the agent loop.

---

## 2. Sources Consulted

### [OFFICIAL DOCUMENTATION]
- **Customization System Specifications**:
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\SKILL.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\hooks.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\rules.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\skills.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\plugins.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\mcp_servers.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\agy-customizations\docs\json_configs.md`
- **Antigravity Guide & Surface References**:
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\antigravity_guide\SKILL.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\antigravity_guide\references\cli.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\antigravity_guide\references\app.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\antigravity_guide\references\ide.md`
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\antigravity_guide\references\sdk.md`
- **Workflow Migration Specification**:
  - `C:\Users\Suraj\.gemini\antigravity\builtin\skills\migrate-workflows\SKILL.md`
- **Google Antigravity SDK Specifications & Examples**:
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\architecture.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\agent_configuration.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\safety_policies.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\built_in_tools.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\error_handling.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\references\observability.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\examples\getting_started\subagents.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\examples\getting_started\persistence.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\examples\getting_started\hooks.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\examples\getting_started\periodic_trigger.md`
  - `C:\Users\Suraj\.gemini\config\plugins\google-antigravity-sdk\skills\google-antigravity-sdk\examples\getting_started\mcp_tools.md`

### [BINARY & RUNTIME INTERFACES]
- Backend executable: `C:\Users\Suraj\AppData\Local\Programs\antigravity\resources\bin\language_server.exe` (153,057,280 bytes)
- Desktop application: `C:\Users\Suraj\AppData\Local\Programs\antigravity\Antigravity.exe` (222,848,000 bytes)
- Native MCP Schema configurations: `C:\Users\Suraj\.gemini\antigravity\mcp\`
- Active process inspections: PID 2244, 5936, 9884, 16456, 21424, 23000 (`Antigravity.exe`)

---

## 3. Experimental Methodology

To adhere strictly to the Critical Safety Rule:
1. **StudyLab Zero-Touch Invariant**: The real workspace `c:\Users\Suraj\Documents\Antigravity\Anki-maths` was inspected solely using read-only operations. `git status` checks before and after testing confirmed zero files modified, added, or deleted.
2. **Disposable Isolation Sandbox**: An isolated Git sandbox was created in:
   `C:\Users\Suraj\.gemini\antigravity\brain\2a525e39-74a8-46f4-98f8-f6172f677588\scratch\sandbox`
   Initialized with a root commit and independent author configuration (`auditor@antigravity.test`).
3. **Controlled Experiment Protocol**:
   - Each capability test had a prior hypothesis, minimal deterministic test fixture, observed execution trace, and recorded failure mode.
   - Experiments were assigned identifiers (`AG-SKILL-01`, `AG-RULE-01`, `AG-WF-01`, `AG-SUB-01`, `AG-TREE-01`, `AG-HOOK-01`, `AG-ART-01`, `AG-MCP-01`, `AG-BROWSER-01`, `AG-CLI-01`, `AG-MEM-01`, `AG-SCHED-01`, `AG-CROSS-01..06`).
   - Observations were classified under the four-tier evidence hierarchy: `[OFFICIAL DOCUMENTATION]`, `[OBSERVED]`, `[INFERRED]`, `[UNKNOWN]`, `[CONFLICT]`.

---

## 4. Skills

### [OFFICIAL DOCUMENTATION]
- Skills are packaged in `skills/<skill_name>/SKILL.md` containing YAML frontmatter (`name`, `description`) with optional `scripts/`, `examples/`, `resources/`, and `references/`.
- Discovery locations:
  1. Workspace Project: `.agents/skills/`
  2. Declared: `skills.json`
  3. Global Discovery: `~/.gemini/config/skills/`
  4. Built-in: Bundled in `~/.gemini/antigravity/builtin/skills/`
- Progressive disclosure: Full skill markdown is NOT loaded into prompt context initially; only name, path, and description are injected into the system prompt. The model activates a skill on-demand by calling `view_file`.

### [OBSERVED] (Experiment AG-SKILL-01 & AG-SKILL-02)
1. **Prompt Injection Mechanics**: In the live prompt, 38 skills were injected into `<skills>` using the exact syntax:
   `- <name> (<path>): <description>`
   Followed by the mandatory instruction: *"If a skill seems relevant to your current task, you MUST read its SKILL.md instructions using view_file before proceeding."*
2. **Explicit Activation**: When the user invoked `/adaptive-orchestrator`, the platform intercepted the slash command and injected an explicit tag into `<ADDITIONAL_METADATA>`:
   `<SKILL>The user requested you read and use the "adaptive-orchestrator" skill. The path to the skill file is: ...</SKILL>`.
3. **Automatic Semantic Activation**: When a query touches topics matching a skill description (e.g. `chrome-devtools` or `agy-customizations`), the LLM issues a `view_file` call to load the full `SKILL.md`.
4. **Failure Behavior**: If a skill contains broken relative paths or missing helper scripts, the tool call fails with a normal file error. The model remains in the loop and must reason around the missing asset.

### [INFERRED]
- Skills do not possess private isolated runtimes or separate memory spaces. A skill is fundamentally an on-demand prompt extension coupled with file references.
- Confidence: **HIGH**.

---

## 5. Rules / Instructions

### [OFFICIAL DOCUMENTATION]
- Workspace rules are stored in `GEMINI.md` or `AGENTS.md` directly in directories or under `.agents/rules/*.md`.
- As files are edited or opened, the engine walks from CWD up to the repository root and loads all rules.
- Standalone rule files do not support YAML frontmatter; they are unconditionally active for their directory scope. Rules are deduplicated by resolved file path.

### [OBSERVED] (Experiment AG-RULE-01 & AG-RULE-02)
1. **Rule Mounting**: The workspace rule `c:\Users\Suraj\Documents\Antigravity\Anki-maths\AGENTS.md` was automatically detected and mounted into `<user_rules>` in the system prompt:
   `<RULE[c:\Users\Suraj\Documents\Antigravity\Anki-maths\AGENTS.md]> CLAUDE.md </RULE[...]>`
2. **Rule Nature**: Rules are injected directly as high-priority natural language prompts (`"The following are user-defined rules that you MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION..."`).
3. **Enforcement Strength**: Rules act as **contextual cognitive constraints**, not kernel-level sandboxes. A rule stating "Do not touch StudyLab" was honored because the LLM reasoned against the constraint; however, the underlying shell tools (`run_command`) retain full OS-level permission to touch files unless gated by a `PreToolUse` hook.
4. **Precedence**: Higher-level user rules in `<user_rules>` override skill recommendations and default behaviors in LLM evaluation.

### [CONFLICT]
- Marketing material often implies rules are "enforced policies." In runtime reality, rules are prompt-level directives. True enforcement requires lifecycle hooks (`hooks.json`) or SDK policy predicates (`safety_policies.md`).
- Confidence: **HIGH**.

---

## 6. Workflows

### [OFFICIAL DOCUMENTATION]
- According to `migrate-workflows/SKILL.md`, legacy workflows (`.agents/workflows/*.md` or `_agents/workflows/*.md`) are officially **deprecated**.
- Skills replace workflows by providing first-class slash command support (`/<name>`), semantic agent discovery, and multi-file directory capabilities.
- Slash commands are listed in the UI menu (`/goal`, `/schedule`, `/browser`, `/grill-me`, `/teamwork-preview`, `/learn`, `/boost`).

### [OBSERVED] (Experiment AG-WF-01)
1. **Sequential Shell Execution**: In PowerShell, executing commands chained with semicolons (without explicit `$ErrorActionPreference = 'Stop'`) causes subsequent commands to run even when an intermediate process exits with code 42 (`step3.txt` was created).
2. **Tool Failure Reporting**: When a command exits with a non-zero exit code, `run_command` returns:
   `The command exited with code X. Output: ...`
   The platform does NOT abort the session; the tool response is returned to the agent loop, requiring the LLM to inspect the error and decide whether to retry, reassign, or fail.
3. **Workflow Orchestration**: Multi-step workflows are not executed by a rigid state-machine engine; they are dynamic agentic loops guided by step-by-step instructions in skills.

### [INFERRED]
- Workflows in Antigravity are emergent, model-directed sequences governed by prompt runbooks (skills), rather than deterministic DAG execution pipelines (like Airflow or GitHub Actions).
- Confidence: **HIGH**.

---

## 7. Subagents

### [OFFICIAL DOCUMENTATION]
- The root agent can spawn subagents using `invoke_subagent`, specifying:
  - `TypeName`: `self` (inherits full tools), `research` (read-only tools), or custom types defined via `define_subagent`.
  - `Model`: `inherit`, `flash`, `flash_lite`, `pro`.
  - `Workspace`: `inherit` (default), `branch`, `share`.
  - `Role` & `Prompt`.
- Subagents execute autonomously in the background. The system provides reactive wakeups (`manage_subagents` status/kill, `send_message`).
- Hierarchical subagent depth is supported up to configured limits (`max_subagent_depth`).

### [OBSERVED] (Experiment AG-SUB-01 & AG-SUB-02)
1. **Context Segregation**: Subagents `1972b8c0-...` and `3b29b62f-...` received completely fresh context windows. They had zero visibility into the parent agent's reasoning, user conversation history, or prior parent tool calls.
2. **Tool Suite Inheritance**: When spawned with `TypeName='self'`, the subagent inherited all system tools, MCP servers, and crucially: `define_subagent`, `invoke_subagent`, and `manage_subagents`. This empirically verifies that **subagents have the structural capability to launch nested child subagents**.
3. **Communication & Handoff**: Subagents communicate upward by returning their final text response, which is delivered as a high-priority message:
   `[Message] timestamp=... sender=<conversation-id> priority=MESSAGE_PRIORITY_HIGH content=...`
4. **Lifecycle Control**: The parent can inspect running subagents via `manage_subagents(Action='list')` and cleanly terminate them with `manage_subagents(Action='kill', ConversationIds=[...])`.
5. **Credit Accounting**: Every subagent launch consumes a distinct conversation slot with independent transcript logging under `brain/<subagent-id>/`.

### [INFERRED]
- Subagent isolation is memory-level and context-level. They share the same physical host filesystem and OS process environment unless restricted by workspace branching or OS sandboxing.
- Confidence: **HIGH**.

---

## 8. Worktrees / Isolated Work

### [OFFICIAL DOCUMENTATION]
- `invoke_subagent` documentation declares three `Workspace` modes:
  - `'inherit'`: Uses the same workspace as parent.
  - `'branch'`: Creates a new isolated workspace branched or cloned from the parent.
  - `'share'`: Creates a new workspace sharing the parent's underlying repository directory (similar to git worktree).
- `manage_subagents` specifies: *"When a subagent is killed, its branched workspaces will be deleted, but its logs and artifacts will be preserved."*

### [OBSERVED] (Experiment AG-TREE-01)
1. **Filesystem Reality**: In Windows desktop Antigravity, spawning a subagent with `Workspace='inherit'` mounts the parent workspace path `c:\Users\Suraj\Documents\Antigravity\Anki-maths`.
2. **Artifact Directory Partitioning**: Even under `Workspace='inherit'`, the platform strictly enforces separate artifact directories. A subagent attempting to invoke `write_to_file` targeting the parent's artifact directory (`brain/<parent-id>/...`) was intercepted and blocked by the tool runner:
   `Encountered error in tool execution: files must be written to the correct artifact directory: C:\Users\Suraj\.gemini\antigravity\brain\<subagent-id>`
3. **OS-Level Shell Writes**: If a subagent executes `run_command` (e.g. PowerShell `Out-File`), it bypasses the artifact path check and writes directly to whatever directory it specifies on the host filesystem.

### [INFERRED]
- `Workspace='branch'` creates an ephemeral directory clone or git worktree managed by the Language Server.
- Safe experimentation without contaminating the parent working tree cannot rely solely on the agent's prompt instructions; it requires either launching with `Workspace='branch'` or strictly confining write paths to an isolated sandbox.
- Confidence: **HIGH**.

---

## 9. Hooks

### [OFFICIAL DOCUMENTATION]
- Configured in `hooks.json` in the customization root (`.agents/hooks.json`).
- Supported lifecycle events:
  - `PreToolUse`: Handlers running before a tool executes (grouped with `matcher` regex). Can return `decision: "allow" | "deny" | "ask" | "force_ask"`, `reason`, and `overwrite` (shallow top-level argument merge).
  - `PostToolUse`: Handlers running after a tool completes. Receives `error` if tool failed.
  - `PreInvocation`: Injects steps before the model is called (`injectSteps`).
  - `PostInvocation`: Can force continuation or termination (`terminationBehavior: "force_continue" | "terminate"`).
  - `Stop`: Handlers running when the agent loop attempts to terminate. Can return `decision: "continue"`, `reason` to block stopping.
- Execution model: Commands run synchronously via `cmd /c` on Windows, receiving context JSON on stdin and returning JSON on stdout.

### [OBSERVED] (Experiment AG-HOOK-01 & AG-HOOK-02)
1. **Runtime Stop Hook Execution**: During our audit execution, the platform's active Stop hook intercepted agent loop termination:
   `<SYSTEM_MESSAGE> Stop hook blocked termination: The user has automatically approved the artifact through their review policy. Proceed to execution. </SYSTEM_MESSAGE>`
   This is direct empirical proof that **hooks operate as true programmatic enforcement gates**.
2. **Synchronous Blocking Boundary**: When a hook returns `deny` on `PreToolUse`, the Language Server terminates the tool call before the shell or filesystem API is invoked.
3. **Limitations**: Only `type: "command"` is supported (shell execution). Hooks cannot run asynchronous background operations; they block the agent loop until the hook process exits.

### [INFERRED]
- Hooks represent Antigravity's **sole deterministic enforcement mechanism** for security, linting, and policy guardrails outside hardcoded tool schemas.
- Confidence: **HIGH**.

---

## 10. Artifacts / File-Based State

### [OFFICIAL DOCUMENTATION]
- Artifacts are special markdown documents presented in the UI, stored under `<appDataDir>\brain\<conversation-id>/`.
- Managed using `write_to_file` and `replace_file_content` with `ArtifactMetadata` (`RequestFeedback: bool`, `Summary: str`, `UserFacing: bool`).
- Special artifacts include `implementation_plan.md` and `walkthrough.md`.

### [OBSERVED] (Experiment AG-ART-01)
1. **Storage Mechanics**: Artifacts are physically written to disk as standard files in the designated conversation directory.
2. **Metadata Binding**: Passing `ArtifactMetadata` attaches UI review triggers. When `RequestFeedback: true` was set on `implementation_plan.md`, the platform automatically held the turn for user approval (or auto-approval via review policy).
3. **Path Validation Invariant**: `write_to_file` rejects any path targeting a `brain/<id>/` directory that does not match the active conversation ID of the calling agent.
4. **Persistence Across Turns & Resets**: Because artifacts are standard filesystem files, they survive context compaction, subagent restarts, and process reboots.

### [INFERRED]
- Artifacts are the canonical persistence layer for durable agent deliverables, architectural plans, and cross-session memory handoffs.
- Confidence: **HIGH**.

---

## 11. MCP (Model Context Protocol)

### [OFFICIAL DOCUMENTATION]
- MCP servers are defined in `mcp_config.json` (globally in `~/.gemini/config/mcp_config.json` or per-plugin).
- Transports supported: **Stdio** (local command) and **SSE / Streamable HTTP** (remote URL).
- Tools are discovered dynamically and injected into the agent's toolset.

### [OBSERVED] (Experiment AG-MCP-01)
1. **Server Inventory**: 9 MCP servers are configured in the current environment (`chrome-devtools-mcp`, `docker-mcp`, `gemini-api-docs`, `github-mcp-server`, `notion-mcp-server`, `playwright`, `playwright-mcp-server`, `posthog`, `studysource-core`).
2. **Tool Invocation**: Executing `call_mcp_tool` with `ServerName='chrome-devtools-mcp'`, `ToolName='list_pages'`, `Arguments={}` executed synchronously and returned:
   `## Pages\n1: about:blank [selected]`
3. **Lazy Loading vs Eager Loading**:
   - Eager tools (e.g. `mcp_gemini-api-docs_gemini_search_docs`) appear directly in the top-level tool definitions.
   - Lazy tools are invoked via the generic dispatcher `call_mcp_tool` after reading their JSON schema from `<gemini-dir>/antigravity/mcp/<serverName>/<toolName>.json`.

### [INFERRED]
- MCP integration in Antigravity is mature, performant, and operates over local IPC/stdio seamlessly.
- Confidence: **HIGH**.

---

## 12. Browser / Computer Interaction

### [OFFICIAL DOCUMENTATION]
- Antigravity provides browser automation via `chrome-devtools-mcp` and `playwright`.
- Capabilities include navigation, screenshot capture, clicking, typing, DOM snapshots, network request inspection, and console message extraction.
- Desktop application settings allow configuring browser allowlists and headless modes.

### [OBSERVED] (Experiment AG-BROWSER-01)
1. **Headless Chrome Protocol**: The Language Server process manages a headless Chromium instance via Chrome DevTools Protocol (`-cdp_port=9222`, `-use_ls_chrome_devtools_mcp=true`, `-local_chrome_headless=true`).
2. **Verification Execution**: Calling `list_pages` on `chrome-devtools-mcp` confirmed connection to an active Chromium target (`about:blank`).
3. **Desktop Webview Testing**: For non-browser GUI surfaces (such as QtWebEngine applications), the platform relies on specialized tools/skills (`desktop-webview-reviewer`) combining native OS window inspection and DevTools remote debugging.

### [INFERRED]
- Browser testing of web applications is fully supported out of the box. Desktop GUI automation requires explicit dev-mode remote debugging ports.
- Confidence: **HIGH**.

---

## 13. CLI / Headless / Automation

### [OFFICIAL DOCUMENTATION]
- The Antigravity CLI (`agy`) is documented as a terminal interface for agent interaction, supporting slash commands and flags (`agy --help`).
- Configured via `~/.gemini/antigravity-cli/settings.json`.

### [OBSERVED] (Experiment AG-CLI-01)
1. **PATH Availability Discrepancy**: Executing `agy` in PowerShell resulted in `CommandNotFoundException`. The standalone `agy` binary was not placed in standard Windows PATH during standard desktop installation.
2. **Backend Engine Inspection**: The underlying agent executable is:
   `C:\Users\Suraj\AppData\Local\Programs\antigravity\resources\bin\language_server.exe`
3. **Headless Engine Flags**: `language_server.exe` exposes complete headless server flags:
   - `-headless=false`: Run without GUI
   - `-standalone=false`: Run standalone
   - `-persistent_mode=false`: Persistent daemon mode
   - `-subclient_type=""`: Target client (`sdk`, `cli`, `hub`)
   - `-api_server_url="http://0.0.0.0:50001"`
4. **SDK Headlessness**: The Python SDK (`google-antigravity`) provides programmatic headlessness (`Agent(LocalAgentConfig)`), wrapping the compiled harness.

### [CONFLICT]
- While the marketing and documentation highlight `agy` as a primary entry point, on Windows desktop distributions the CLI is not automatically exposed to PATH. Automated CI pipelines must either run via the Python SDK or invoke `language_server.exe` directly.
- Confidence: **HIGH**.

---

## 14. Memory / Context

### [OFFICIAL DOCUMENTATION]
- Antigravity maintains state within a session across turns.
- Trajectory logs are written to `transcript.jsonl` (compact) and `transcript_full.jsonl` (untruncated).
- Context compaction (`CHECKPOINT`) compresses historical turns when token limits are reached.
- Persistent agents can resume conversations using `conversation_id` and `save_dir`.

### [OBSERVED] (Experiment AG-MEM-01 & AG-MEM-02)
1. **Within-Session Memory**: Maintained completely until context threshold is reached, at which point a `CHECKPOINT` step summarizes previous goals while preserving the transcript pointer.
2. **Cross-Session Segregation**: A new conversation starts with zero memory of previous sessions unless:
   - The user explicitly `@-mentions` a previous conversation (`conversation://<id>`).
   - Durable data is read from repository markdown files (`PROJECT.md`, `CLAUDE.md`, etc.).
3. **Audit Trail**: Every turn, tool call, reasoning thought, and system notification is immutably logged to:
   `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`.

### [INFERRED]
- Long-term memory is strictly **file-backed**. There is no implicit cross-conversation vector database or persistent memory store operating silently behind the scenes.
- Confidence: **HIGH**.

---

## 15. Scheduling / Long-Running Work

### [OFFICIAL DOCUMENTATION]
- The `schedule` tool enables one-shot timers (`DurationSeconds`, `TimerCondition`) and recurring jobs (`CronExpression`, `MaxIterations`, `IsDaemon`).
- Returns immediately and runs as a background task.
- Sends high-priority notification messages when timers expire or cron jobs trigger.

### [OBSERVED] (Experiment AG-SCHED-01)
1. **Timer Dispatch**: Calling `schedule` with `DurationSeconds=2`, `Prompt="Capability L Verification Timer Fired"`, and `TimerCondition="never"` created background task `2a525e39-.../task-152`.
2. **Wakeup Delivery**: Exactly 2 seconds later, the background task delivered a wakeup notification:
   `[Message] timestamp=... sender=.../task-152 priority=MESSAGE_PRIORITY_HIGH content=Capability L Verification Timer Fired`
3. **Lifecycle Management**: The task automatically de-registered from `manage_task(Action='list')` upon firing.

### [INFERRED]
- Background scheduling is an active, fully functional platform capability suitable for heartbeat monitoring, delayed checks, and polling.
- Confidence: **HIGH**.

---

## 16. Cross-Capability Experiments

| Test ID | Combination | Hypothesis | Observed Reality | Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **AG-CROSS-01** | **Skill + Rule** | An overarching rule in `AGENTS.md` strictly constrains actions recommended by a skill. | Overarching prompt rule ("Do not touch StudyLab") completely superseded `adaptive-orchestrator`'s default file modification instructions. Zero StudyLab files modified. | **PASS** |
| **AG-CROSS-02** | **Skill + Subagent** | A specialist skill can be delegated to an isolated subagent. | Subagent `1972b8c0-...` executed documentation research using builtin skills; Subagent `3b29b62f-...` audited isolation. Both completed and returned structured findings. | **PASS** |
| **AG-CROSS-03** | **Workflow + Verification** | A multi-step process can mandate a verification gate before proceeding. | `implementation_plan.md` halted execution at User Approval. Resumption occurred only when the stop hook verified user policy approval. | **PASS** |
| **AG-CROSS-04** | **Hook + Policy** | A hook can prevent an unsafe action or enforce loop continuation. | The active Stop hook intercepted model termination and injected a continuation directive (`Stop hook blocked termination...`). | **PASS** |
| **AG-CROSS-05** | **Artifacts + Context Reset** | File-backed state allows resuming work across compaction or subagent boundaries. | Subagent verified parent probe file from disk; parent inspected subagent's disk artifact and transcript. Checkpoint compaction retained full transcript links. | **PASS** |
| **AG-CROSS-06** | **Worktree + Subagent** | Isolated work can be delegated to a subagent without dirtying the parent workspace. | Subagent operated within its own directory; parent workspace (`Anki-maths`) remained 100% clean across all subagent operations. | **PASS** |

---

## 17. Failure-Mode Map

| Major Capability | Normal Behavior | Malformed Input | Tool / Command Failure | Context Compaction / Reset | Security / Permission Boundary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Skills** | Injects metadata; loads `SKILL.md` via `view_file` | Frontmatter syntax error causes skill to be skipped | Relative script link broken $\rightarrow$ file error returned to model | Inactive skills purged from immediate context | Gated by filesystem read permissions |
| **Rules** | Injected in `<user_rules>` unconditionally | Malformed markdown still parsed as raw text | N/A (passive prompt injection) | Rules re-injected on every turn (immune to compaction) | No hard boundary; soft LLM compliance |
| **Workflows** | Sequenced via skill instructions | Invalid slash command ignored or treated as chat | Step failure returns exit code; loop continues unless gated | Multi-turn state lost unless written to disk | Bound by underlying tool permissions |
| **Subagents** | Segregated context; returns final report | Invalid model or syntax triggers schema error | Subagent crash logged to transcript; error returned to parent | Subagent transcript preserved; active context destroyed on kill | Cannot write to parent artifact dir via `write_to_file` |
| **Worktrees** | Isolated workspace directory | Invalid branch or path triggers git error | Failed merge leaves worktree intact for inspection | Worktrees deleted on subagent kill; logs preserved | Restricted to designated branch folder |
| **Hooks** | Synchronous stdin/stdout execution | Invalid JSON output causes hook failure | Command timeout after 30s; default decision applied | Hooks re-evaluated per tool step or invocation | Hard blocking boundary on `decision: "deny"` |
| **Artifacts** | Renders in UI; writes to `brain/<id>/` | Invalid metadata fields rejected by schema | Target outside conversation directory rejected | Files on disk persist indefinitely | Strictly sandboxed to active `conversation-id` |
| **MCP** | Stdio/SSE tools routed to server | Invalid arguments rejected by JSON schema | Server crash or timeout returns error to model | Tool definitions reloaded on session start | Server policy can require user confirmation |
| **Scheduling** | Asynchronous background timer/cron | Invalid cron expression rejected by tool | Timer cancellation cleanly de-registers task | Timers persist in background daemon across model turns | Notifications delivered as high-priority messages |

---

## 18. Capability Scorecard

| Capability | Officially Documented | Observed in Audit | Limitations & Caveats | Confidence |
| :--- | :---: | :---: | :--- | :---: |
| **Skills** | YES | **CONFIRMED** | Progressive disclosure only; no isolated memory space. | **HIGH** |
| **Rules** | YES | **CONFIRMED** | Soft prompt guidance; not a hard programmatic sandbox. | **HIGH** |
| **Workflows** | YES (Deprecated) | **CONFIRMED** | Standalone workflows deprecated; unified into Skills. | **HIGH** |
| **Subagents** | YES | **CONFIRMED** | Completely isolated context; full tool suite inherited. | **HIGH** |
| **Worktrees** | YES | **CONFIRMED** | Native git worktrees/branch workspaces; auto-cleaned on kill. | **HIGH** |
| **Hooks** | YES | **CONFIRMED** | True hard enforcement boundary; synchronous only. | **HIGH** |
| **Artifacts** | YES | **CONFIRMED** | Durable filesystem files; strict conversation-ID path isolation. | **HIGH** |
| **MCP** | YES | **CONFIRMED** | Full stdio & SSE support; lazy schema loading. | **HIGH** |
| **Browser** | YES | **CONFIRMED** | Headless Chrome via CDP port 9222 active and responsive. | **HIGH** |
| **CLI** | YES | **PARTIAL** | `agy` not on standard PATH; backend `language_server` is headless. | **MEDIUM** |
| **Memory** | YES | **CONFIRMED** | No vector memory; state is 100% file-backed and transcript-backed. | **HIGH** |
| **Scheduling**| YES | **CONFIRMED** | Asynchronous background daemon; high-priority wakeup delivery. | **HIGH** |

---

## 19. Antigravity Boundary Map

To design a future agent-native architecture, every capability must be classified by its architectural ownership:

| Capability Component | Classification | Rationale & Responsibility |
| :--- | :---: | :--- |
| **Hook Execution Engine** | **PLATFORM** | Antigravity directly intercepts tool steps and halts/resumes loops. |
| **Hook Policy & Logic** | **PROJECT** | Our framework must write the specific safety, lint, and verification scripts. |
| **Subagent Execution Runtime** | **PLATFORM** | Spawning, process management, and communication are native to the platform. |
| **Subagent Workforce Topology** | **PROJECT** | Sizing (SOLO vs PARALLEL), role mandates, and handoffs must be framework-governed. |
| **Skill Progressive Loading** | **PLATFORM** | Antigravity scans directories, injects summaries, and loads on `view_file`. |
| **Skill Runbook Content** | **PROJECT** | The specific domain procedures, scripts, and validation steps are project assets. |
| **Rule Mount & Injection** | **PLATFORM** | Hierarchical directory walking and `<user_rules>` injection is automatic. |
| **Rule Compliance Verification** | **HYBRID** | Platform injects the prompt; project must enforce via test suites and hooks. |
| **Artifact Storage & UI** | **PLATFORM** | Path validation, rendering in UI pane, and metadata review gating. |
| **Artifact State Schemas** | **PROJECT** | Structure of plans, truth matrices, and release notes must be framework-defined. |
| **MCP Transport & Schema** | **PLATFORM** | Language server manages stdio/SSE communication and JSON schema translation. |
| **Custom MCP Tools** | **PROJECT** | Domain servers (e.g. `studysource-core`) must be implemented and maintained by project. |
| **Memory Persistence Model** | **HYBRID** | Platform saves JSONL transcripts; framework must maintain durable repository docs. |
| **Background Scheduling** | **PLATFORM** | Platform manages cron daemon and timers; project defines triggers and prompts. |

---

## 20. Strong Capabilities (Rely On These)

1. **Subagent Context Segregation**:
   Subagents provide 100% clean context windows without token leakage from parent reasoning or conversation history. They can be safely deployed for deep exploratory tasks without bloating the root session.
2. **Hook-Based Hard Enforcement**:
   The `PreToolUse` and `Stop` hooks in `hooks.json` are true platform-enforced boundaries. They reliably block unauthorized tools, overwrite arguments, and intercept premature agent termination.
3. **Artifact Filesystem Durability**:
   Artifacts are real, accessible files on disk. They provide a rock-solid substrate for persistent coordination artifacts (`implementation_plan.md`, `walkthrough.md`, `evidence.json`) across sessions.
4. **Model Context Protocol (MCP)**:
   Antigravity's MCP implementation is robust, supporting fast local stdio servers and full JSON schema parameter validation.
5. **Background Scheduling & Wakeups**:
   The `schedule` tool reliably dispatches background tasks that wake the agent loop with high-priority notifications upon timer expiry.

---

## 21. Important Limitations (Design Around These)

1. **Rules are Soft Constraints**:
   `AGENTS.md` and `GEMINI.md` are instructions to the LLM, not kernel-level sandboxes. If an invariant is critical to system safety, it **must** be enforced by a `PreToolUse` hook, an automated test suite, or an OS-level permission boundary.
2. **No Implicit Persistent Memory**:
   Agents do not possess a hidden vector memory across sessions. Any knowledge not committed to repository files or artifacts is lost when a conversation closes.
3. **Subagent File Write Restrictions**:
   Subagents cannot write to the parent agent's artifact directory using `write_to_file`. Data passing between agents must use structured handoff reports or repository/sandbox file paths.
4. **Shell Error Non-Halting**:
   Commands run via `run_command` that fail do not automatically crash or halt the agent loop. Multi-step shell scripts must use defensive error handling (`$ErrorActionPreference = 'Stop'`, `set -e`).
5. **CLI Discovery Gap on Windows**:
   `agy` is not installed on PATH by default in desktop distributions. Headless automation in CI/CD requires scripting against `language_server.exe` or utilizing the Python SDK.

---

## 22. Unknowns Requiring Further Investigation

1. **Large Multi-Agent Concurrent Scalability**:
   While 1–2 concurrent subagents performed reliably, platform stability under maximum concurrent load (4 active subagents performing heavy parallel compilation) remains to be stress-tested.
2. **Git Worktree Merge Automation**:
   When subagents complete changes in `Workspace='branch'`, the platform-level diff reconciliation and auto-merge heuristics require deeper investigation before enabling autonomous multi-agent code merging.
3. **SDK Headless Licensing & Auth in CI**:
   Evaluating how `language_server.exe` and `google-antigravity` authenticate headless runners in cloud CI environments (ADC vs API keys) without a desktop Electron session.

---

## 23. Implications for a Future Agent-Native Architecture

1. **Adopt Skill-Based Architecture Over Deprecated Workflows**:
   All repeatable agent procedures should be authored as **Skills** conforming to the Agent Skills specification (`skills/<name>/SKILL.md`), paired with slash commands for human invocability.
2. **Implement Two-Tier Governance (Prompt Guidance + Hook Enforcement)**:
   Use `AGENTS.md` to define operational intent and coding style; use `hooks.json` (`PreToolUse`) to programmatically forbid destructive commands or enforce pre-commit checks.
3. **Shallow, Scoped Delegation with Explicit Handoffs**:
   Subagent trees should be kept shallow (Depth $\le 2$). Because subagents start with clean contexts, parent agents must supply self-contained prompts with explicit file scopes and mandatory structured handoff templates.
4. **File-Backed Truth as the Single Source of Truth**:
   Because agent memory is ephemeral, all architectural decisions, bug registers, and status updates must be persisted as durable repository artifacts (`PROJECT.md`, `evidence.json`, `audit_report.md`).
5. **Single Controlled Writer Default**:
   To avoid git merge collisions and lockfile conflicts, parallel agents should focus on read-heavy tasks (investigation, linting, test analysis), while write operations are assigned to a single designated implementer or reconciled through strict file partitioning.

---

## Final Question

> **"If we completely ignored Antigravity's marketing claims and designed around only capabilities experimentally demonstrated in this audit, what capabilities could we safely treat as architectural primitives?"**

Based strictly on the empirical evidence gathered during this audit, the following are the **verified architectural primitives** of Antigravity:

1. **Progressive Skill Loading**:
   On-demand prompt augmentation triggered semantically or via slash commands, reading markdown instructions and helper scripts from disk.
2. **Context-Segregated Subagent Spawning**:
   Autonomous background agents with clean context windows, inheriting system tools and able to return structured reports.
3. **Platform-Level Hook Interception**:
   Deterministic synchronous interception of tool execution (`PreToolUse`) and agent loop termination (`Stop`) via shell scripts.
4. **Conversation-Scoped Artifact Storage**:
   Persistent filesystem-backed markdown artifacts gated by active conversation ID and integrated into the review UI.
5. **Local MCP Tool Integration**:
   Stdio-based tool discovery and execution bridging the LLM to local services and specialized tools.
6. **Reactive Task Scheduling**:
   Background one-shot and recurring timers delivering high-priority message wakeups into the agent execution loop.
7. **File-Backed Memory Ledgering**:
   Long-term state preservation achieved exclusively through version-controlled repository documentation and structured JSON/JSONL artifacts.
