# **Deep Research Mission 01: Google Antigravity Internals — Forensic Capability & Boundary Audit**

## **1\. Executive Summary**

This forensic investigation analyzes Google’s **Antigravity** agentic development platform to determine its architectural boundary against **StudyLab**. The primary objective is to delineate what Antigravity natively provides as an execution substrate, what it offloads to project configuration, and which governance, semantic invariants, and domain contracts must be authored and maintained within the StudyLab repository.  
Google Antigravity—launched in Public Preview in November 2025 and expanded in mid-2026 to **Antigravity 2.0**—is a multi-surface agentic development platform powered by frontier Gemini models (notably Gemini 3.5 Flash and Gemini 3.7 Flash). It encompasses four primary operational surfaces:

> 1. **Antigravity 2.0 Standalone Desktop Application**: A centralized multi-agent orchestration desktop command center (macOS, Linux, Windows) supporting parallel asynchronous agent management, Git worktree isolation, scheduled/unattended tasks, and visual review panes.  
> 2. **Antigravity IDE**: A code-first agentic IDE combining language server capabilities with an embedded agent manager, visual artifact generation, and code review panels.  
> 3. **Antigravity CLI (agy)**: A lightweight, keyboard-driven terminal environment with an interactive TUI, background subagent controls, headless/non-interactive execution, and sandboxed terminal execution.  
> 4. **Antigravity SDK (antigravity-sdk-python)**: A programmatic Python library (google.antigravity) exposing the underlying agent loop, tool harnesses, MCP bridges, subagent delegation interfaces, and execution lifecycle hooks.

### **Core Architectural Conclusion**

Antigravity operates as an **execution engine, tool harness, sandbox, and context-assembly substrate**. It provides native facilities for running processes, managing browser sessions, orchestrating subagents, enforcing filesystem and network sandboxing, isolating concurrent branches via Git worktrees, and rendering structured artifacts (implementation plans, diffs, walkthroughs).  
However, Antigravity is **completely agnostic to domain semantics, syllabus taxonomy, knowledge decay, pedagogy, and data-integrity invariants**. It contains no native concepts of spaced-repetition schedules, Anki APKG compilation invariants, pedagogical progression, or source-grounded evidence ledgers.  
Therefore, **Antigravity provides the runtime and mechanical governance, while StudyLab must provide the domain architecture, policy rules, and verification contracts**. Attempting to rebuild Antigravity’s terminal sandbox, agent scheduler, worktree isolation, or subagent dispatch within StudyLab would be redundant engineering. Conversely, expecting Antigravity to maintain pedagogical consistency without strict repository-encoded rules, workflows, and test harnesses would fail silently.  
**Authoritative Whitepaper Status**: Extensive investigation across Google Research, Google DeepMind, Google Developer Documentation, and academic archives confirms: **"No authoritative Antigravity whitepaper/technical paper was found."** All architectural specifications in this report have been forensically reconstructed from Tier 1 primary sources ([Google Antigravity Documentation](https://antigravity.google/docs/home/), [Google Developers Blog](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/), [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/expanding-google-antigravity-for-enterprise-customers), [Google Codelabs](https://codelabs.developers.google.com/getting-started-google-antigravity)), Tier 2 conference/video releases ([Google I/O 2026 Highlights](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/)), and verified Tier 3 independent engineering analyses.

## **2\. Antigravity Architecture Reconstruction**

### **2.1 The Platform and Its Problem Space**

Antigravity was conceived to solve the transition from **synchronous AI code-completion** (e.g., Tab-completion, reactive chat) to **asynchronous, autonomous, multi-step agentic orchestration**. Rather than having developers manually step through every file modification and terminal execution, Antigravity acts as a supervisory control platform where autonomous agents plan, execute, debug, and verify complex engineering workflows across the filesystem, the shell, and the web browser.

### **2.2 Reconstructed Conceptual Hierarchy**

Based on [Antigravity Projects Documentation](https://antigravity.google/docs/projects/) and [Antigravity Architecture Overview](https://antigravity.google/docs/agent), the system hierarchy is reconstructed as follows:  
`Project (Boundary definition: folders, repositories, security policies)`  
  `│`  
  `├── Workspaces / Checkouts (Local folders or Git worktree branches)`  
  `│     │`  
  `│     ├── Agent Session (Active multi-turn conversation thread, model tier)`  
  `│     │     │`  
  `│     │     ├── Context Assembly (GEMINI.md, AGENTS.md, Rules, Symbols)`  
  `│     │     │`  
  `│     │     ├── Task Trajectory (Reasoning loop, planning mode)`  
  `│     │     │     │`  
  `│     │     │     ├── Tool Harness (Terminal, Filesystem, Browser, MCP)`  
  `│     │     │     │`  
  `│     │     │     ├── Skills Engine (Discovered via progressive disclosure)`  
  `│     │     │     │`  
  `│     │     │     ├── Subagent Dispatch (Asynchronous, isolated context)`  
  `│     │     │     │`  
  `│     │     │     └── Lifecycle Hooks (PreToolUse, PostToolUse, Pre/PostInvocation)`  
  `│     │     │`  
  `│     │     └── Artifacts (Plans, Diffs, Walkthroughs, Screenshots, Recordings)`  
  `│     │`  
  `│     └── Scheduled Tasks (Cron / periodic triggers bound to the Project)`  
  `│`  
  `└── Global Configuration (~/.gemini/ config, global skills, global rules)`

### **2.3 Core Concept Definitions**

> * **Project**: The top-level administrative boundary in Antigravity 2.0. It defines one or more linked filesystem directories (single repository, monorepo, or multi-repo setup) and enforces scoped security presets, permission allowlists, and default execution policies ([Feature Overview](https://antigravity.google/docs/features/)).  
> * **Workspace**: A specific folder or Git checkout directory within a Project. In "New Worktree Mode," Antigravity automatically isolates the workspace into a separate Git worktree ([Projects Documentation](https://antigravity.google/docs/projects/)).  
> * **Agent**: The primary reasoning entity instantiated within a Project/Workspace. Configured with a system persona, reasoning model (e.g., Gemini 3.5/3.7), and active toolset.  
> * **Session / Conversation**: A discrete, stateful, multi-turn dialogue thread between the user and an agent. History is scoped to the workspace directory to prevent semantic pollution across unrelated repos ([Managing Conversations](https://antigravity.google/docs/cli/conversations/)).  
> * **Task**: A specific engineering objective initiated via prompt, slash command, workflow, or scheduled trigger. Executes across multi-turn reasoning loops.  
> * **Worktree**: An isolated Git working directory spawned dynamically from the target repository, allowing agents to test code, install dependencies, and stage diffs without modifying the developer's active working tree ([Projects Documentation](https://antigravity.google/docs/projects/)).

## **3\. Capability-by-Capability Forensic Analysis**

Each capability is audited below with explicit evidence labeling: \[DOCUMENTED\], \[OBSERVED\], \[INFERRED\], \[COMMUNITY REPORT\], or \[UNKNOWN\].  
`Classification Categories:`  
`- PLATFORM-PROVIDED: Antigravity natively provides the mechanism.`  
`- PROJECT-PROVIDED: The capability/policy must be encoded inside StudyLab.`  
`- HYBRID: Antigravity provides the mechanism; StudyLab provides policy/contracts.`  
`- UNKNOWN: Documentation or evidence is insufficient.`

### **3.1 Skills**

> * **Classification**: HYBRID  
> * **Location & Conventions**: \[DOCUMENTED\]  
  * Workspace Skills: \<workspace-root\>/.agents/skills/\<skill-folder\>/ (with legacy backward compatibility for .agent/skills/ and deprecated .gemini/skills/).  
  * Global Skills: \~/.gemini/config/skills/\<skill-folder\>/ ([Skills Documentation](https://antigravity.google/docs/skills/), [Migrating from Gemini CLI](https://antigravity.google/docs/cli/gcli-migration/)).  
> * **SKILL.md Format & Frontmatter**: \[DOCUMENTED\]  
  * Requires a SKILL.md file within each skill folder.  
  * Frontmatter fields:  
    * name: Lowercase string with hyphens (e.g., ankigen-builder). Defaults to directory name if omitted.  
    * description: Third-person string detailing the exact intent, trigger conditions, and keywords. This description is exposed to the agent during discovery.  
    * Optional metadata fields: compatibility, version.  
> * **Discovery & Progressive Disclosure**: \[DOCUMENTED\]  
  * Skills follow a strict 3-stage progressive disclosure architecture:  
    1. *Discovery (Tier 1\)*: At session start, the agent loads only the name and description of all available workspace and global skills into system context.  
    2. *Activation (Tier 2\)*: When the agent determines a task matches a skill's description (or when explicitly called via slash command, e.g., /refactor-ui), it loads the full SKILL.md instruction body.  
    3. *Execution (Tier 3\)*: The agent executes the instructions and may access supporting resource files or execute bundled scripts located in scripts/, references/, or assets/.  
> * **Precedence & Conflicts**: \[DOCUMENTED\] Workspace-level skills override global skills with the same name.  
> * **Self-Modification**: \[OBSERVED\] Skills are regular files on the filesystem; the agent *can* edit SKILL.md using file tools if permitted by filesystem sandbox rules, but dynamic hot-reloading mid-session is unverified.  
> * **StudyLab Architectural Boundary**: Antigravity owns skill discovery, prompt-budget-saving progressive disclosure, and slash-command routing. StudyLab must own the domain skill definitions (e.g., APKG generation, syllabus ingestion, semantic cross-referencing).

### **3.2 Rules**

> * **Classification**: HYBRID  
> * **Location & Scope**: \[DOCUMENTED\]  
  * Workspace Rules: .agents/rules/ directory at workspace or git root ([Rules Documentation](https://antigravity.google/docs/rules-workflows/)).  
  * Global Rules: \~/.gemini/GEMINI.md.  
  * Context Rules: Legacy root files GEMINI.md and AGENTS.md are also parsed automatically ([Migrating from Gemini CLI](https://antigravity.google/docs/cli/gcli-migration/)).  
> * **Activation Mechanisms**: \[DOCUMENTED\] Rules support four explicit activation modes:  
  1. *Manual*: Activated only when explicitly @-mentioned in the prompt (e.g., @strict-types).  
  2. *Always On*: Injected into the agent's context window on every turn.  
  3. *Model Decision*: Model dynamically reads the rule's metadata description and decides whether to load the rule body.  
  4. *Glob*: Applied conditionally whenever the agent inspects or edits files matching a glob pattern (e.g., \*.py, src/\*\*/\*.ts).  
> * **Constraints & References**: \[DOCUMENTED\]  
  * Hard limit of 12,000 characters per rule file.  
  * Supports @filename transclusion within rules (resolved relative to the rule file or workspace root) ([Rules Reference](https://antigravity.google/docs/ide/rules/)).  
> * **Core Distinction from Skills**: Rules provide *declarative constraints and invariant policies* at the prompt/file level. Skills provide *procedural, multi-step task methodologies and executable tools*.  
> * **StudyLab Architectural Boundary**: Antigravity provides rule parsing, glob evaluation, and context injection. StudyLab must encode its domain invariants (e.g., "Never overwrite raw audio without hash verification", "Strict APKG schema validation") as .agents/rules/.

### **3.3 Workflows**

> * **Classification**: HYBRID  
> * **Format & Trajectory**: \[DOCUMENTED\]  
  * Saved as Markdown files defining a deterministic sequence of prompts/steps.  
  * Limited to 12,000 characters per workflow file ([Rules & Workflows Documentation](https://antigravity.google/docs/rules-workflows/)).  
> * **Invocation & Composition**: \[DOCUMENTED\]  
  * Invoked manually via slash commands (e.g., /deploy-service, /run-e2e).  
  * Supports nested composition: /workflow-1 can instruct the agent to execute /workflow-2 and /workflow-3.  
  * Agent-Generated Workflows: The agent can synthesize a workflow from a successful conversation trajectory.  
> * **Core Distinction**: While Rules govern *constraints* and Skills govern *capabilities*, Workflows define *ordered trajectory-level recipes* guiding the model through end-to-end procedural sequences.  
> * **StudyLab Architectural Boundary**: Antigravity executes the workflow steps and provides the slash-command interface. StudyLab must encode its multi-step pipeline recipes (e.g., ingestion \-\> chunking \-\> flashcard extraction \-\> verification).

### **3.4 Agents**

> * **Classification**: PLATFORM-PROVIDED (Runtime) / PROJECT-PROVIDED (Personas)  
> * **Built-in Agents**: \[DOCUMENTED\] Primary general-purpose coding and reasoning agent, Browser agent, and specialized Review agents.  
> * **Custom Agents**: \[DOCUMENTED\]  
  * Defined in Markdown format with YAML frontmatter.  
  * Workspace Custom Agents: .agents/agents/\<name\>.md or .agents/agents/\<name\>/agent.md.  
  * Global Custom Agents: \~/.gemini/config/agents/ ([Background Tasks & Subagents](https://antigravity.google/docs/cli/subagents/)).  
> * **Configuration**: YAML frontmatter defines system persona, instruction set, default execution mode, and tool access permissions.  
> * **StudyLab Architectural Boundary**: Antigravity provides the agent loop, cognitive harness, and execution runtime. StudyLab configures role-specific personas via .agents/agents/.

### **3.5 Subagents**

> * **Classification**: PLATFORM-PROVIDED (Dispatch/Harness) / PROJECT-PROVIDED (Delegation Policy)  
> * **Invocation & Isolation**: \[DOCUMENTED\]  
  * Parent agents call the native invoke\_subagent tool ([Subagents Documentation](https://antigravity.google/docs/subagents/)).  
  * Custom agents with subagent: true in their frontmatter can be targeted by invoke\_subagent.  
  * **Context Isolation**: Subagents run with a completely isolated context window (clean slate); they do *not* inherit the parent's conversation history, preventing prompt bloat.  
  * **Workspace Modes**: Subagents can operate in inherit (same directory), share (shared storage), or branch (isolated Git worktree).  
> * **Concurrency & Permissions**: \[DOCUMENTED\]  
  * Asynchronous parallel execution supported.  
  * Subagents inherit permission scopes from the parent. If a subagent attempts an action requiring interactive authorization, the prompt bubbles up to the primary user interface.  
> * **StudyLab Architectural Boundary**: Antigravity provides the multi-process execution harness, UI panels (TUI Alt+J, desktop subagent manager), and context isolation. StudyLab must define the delegation criteria and task contracts so the parent agent knows *when* and *how* to partition work.

### **3.6 Hooks**

> * **Classification**: HYBRID  
> * **Specification & Config**: \[DOCUMENTED\]  
  * Defined via hooks.json at project root or in plugins ([Plugins Documentation](https://antigravity.google/docs/plugins/), [Hooks Documentation](https://antigravity.google/docs/hooks/)).  
  * Programmatically supported via decorators in the Python SDK (@agent.hook) ([SDK Lifecycle](https://antigravity.google/docs/sdk/lifecycle/)).  
> * **Supported Events**: \[DOCUMENTED\]  
  1. PreToolUse: Fires prior to tool execution. Takes tool name and arguments. Can return gating decisions: "allow", "deny", "ask", "force\_ask", or "deny\_unless\_prior\_grant". Can also modify parameters or inject explanation messages.  
  2. PostToolUse: Fires immediately after a tool finishes. Captures tool execution output, duration, and error messages.  
  3. PreInvocation: Fires before sending context to the frontier LLM.  
  4. PostInvocation: Fires immediately after the model finishes generating its thought/action trajectory.  
  5. Stop: Fires when an agent task terminates or completes.  
> * **Matcher Syntax**: Regex matching on tool names (e.g., "run\_command", "browser\_.\*", "\*").  
> * **StudyLab Architectural Boundary**: Antigravity exposes the hook interception engine. StudyLab can write deterministic scripts or JSON policies (e.g., enforcing that run\_command cannot execute git push \--force or validating modified file schemas before tool completion).

### **3.7 Context**

> * **Classification**: PLATFORM-PROVIDED  
> * **Codebase Indexing & Symbol Discovery**: \[DOCUMENTED\]  
  * Employs local workspace scoping, native ripgrep-based /codesearch (with fuzzy symbol search and line jump), and semantic file discovery ([Code Search](https://antigravity.google/docs/cli/commands/codesearch/), [Managing Conversations](https://antigravity.google/docs/cli/conversations/)).  
> * **Context Compaction & Reset**: \[DOCUMENTED\]  
  * Automatic compaction when token limits are approached.  
  * Dedicated CLI slash commands: /clear (resets conversation context), /rollback (reverts trajectory to a previous turn), /fork (branches conversation thread into a parallel session) ([CLI Reference](https://antigravity.google/docs/cli/reference/)).  
> * **StudyLab Architectural Boundary**: Antigravity automatically indexes the repository, navigates symbols, and manages token budgets. StudyLab does not need to build a custom code search or symbol retrieval engine.

### **3.8 Knowledge**

> * **Classification**: HYBRID  
> * **Definition & Scoping**: \[DOCUMENTED\]  
  * "Knowledge" refers to persistent documentation and structural conventions that ground the agent across tasks.  
  * Supported via workspace files (AGENTS.md, GEMINI.md), .agents/rules/, and the local storage directory \~/.gemini/antigravity/ ([Agent Settings](https://antigravity.google/docs/agent-settings/), [Migrating from Gemini CLI](https://antigravity.google/docs/cli/gcli-migration/)).  
> * **StudyLab Architectural Boundary**: Antigravity provides the file discovery and automatic injection mechanism. StudyLab is the **sole source of truth** for repository architecture, domain data models, and invariant contracts. These must reside in Git-tracked files (AGENTS.md, docs/architecture/), never locked inside proprietary local IDE state.

### **3.9 Memory**

> * **Classification**: PROJECT-PROVIDED (Cross-Session Invariants) / PLATFORM-PROVIDED (Session State)  
> * **Platform Capabilities**: \[DOCUMENTED\]  
  * Session state persistence is supported via the SDK (persistence.py) and CLI session resume (/resume, /history) ([SDK Overview](https://antigravity.google/docs/sdk/overview/), [CLI Reference](https://antigravity.google/docs/cli/reference/)).  
  * Cross-task episodic "learning" or autonomous long-term memory across completely separate project sessions is **not** an automatic native feature. The platform relies on persistent filesystem artifacts and rules.  
> * **StudyLab Architectural Boundary**: StudyLab must **not** rely on ephemeral agent memory. All critical project memory, progress tracking, audit logs, and architectural decisions must be written to Git-versioned Markdown files (e.g., docs/decisions/, records/progress.md).

### **3.10 Artifacts**

> * **Classification**: PLATFORM-PROVIDED (Generation/Rendering) / HYBRID (Evidence Workflow)  
> * **Supported Formats**: \[DOCUMENTED\]  
  * Implementation Plans (markdown task breakdowns generated in Planning Mode).  
  * Visual Code Diffs (multi-file patch inspection).  
  * Walkthroughs (summaries of changes with visual proofs) ([Walkthrough Documentation](https://antigravity.google/docs/walkthrough/)).  
  * Visual Media & Screenshots (browser snapshots, custom Mermaid diagram rendering).  
  * Screen Recordings (video playback of browser agent actions) ([Artifacts Documentation](https://antigravity.google/docs/artifacts/)).  
> * **Lifecycle & Storage**: \[DOCUMENTED\]  
  * Stored locally in \~/.gemini/antigravity/ and accessible via the desktop sidebar or CLI /artifact panel.  
  * Users can attach line-level review comments, which feed back directly into the agent's prompt stream ([Reviewing Artifacts](https://antigravity.google/docs/cli/artifacts/)).  
> * **StudyLab Architectural Boundary**: Antigravity provides the UI review panels, diff inspectors, and recording players. However, because \~/.gemini/antigravity/ is outside the repository Git tree, StudyLab must ensure that any formal verification reports or audit deliverables are explicitly copied or written to repository paths (reports/, audits/) to remain versioned and auditable.

### **3.11 Terminal and Code Execution**

> * **Classification**: PLATFORM-PROVIDED (Sandbox & Runtime) / PROJECT-PROVIDED (Safety Policies)  
> * **Sandboxing & Boundaries**: \[DOCUMENTED\]  
  * Integrates a native Terminal Sandbox.  
  * Restricts filesystem writes to designated project directories.  
  * Network sandboxing: Blocks unauthorized outbound network calls unless explicitly permitted via domain allowlists (AllowedDomains compiled from read\_url grants) ([Permissions](https://antigravity.google/docs/permissions/), [Sandbox Documentation](https://antigravity.google/docs/cli/sandbox/)).  
> * **Execution Modes**: \[DOCUMENTED\]  
  * default: Interactive human-in-the-loop review for file edits and commands.  
  * accept-edits: Auto-approves file writes, prompting only for shell commands.  
  * plan: Read-only planning and trajectory analysis without disk writes ([Execution Modes](https://antigravity.google/docs/cli/modes/)).  
  * CLI flag \--dangerously-skip-permissions exists for fully autonomous execution in trusted CI/container environments.  
> * **StudyLab Architectural Boundary**: Antigravity owns OS-level process isolation, containerization, and interactive approval prompts. StudyLab encodes domain-specific test runners and build scripts.

### **3.12 Browser Agent**

> * **Classification**: PLATFORM-PROVIDED  
> * **Capabilities & Tooling**: \[DOCUMENTED\]  
  * Drives dedicated Chrome instances via internal browser tools (browser\_navigate, browser\_click, browser\_type, read\_url\_content).  
  * Gated by dual permissions: read\_url (loading and inspecting DOM markdown) and execute\_url (interactive actuation, clicking buttons, submitting forms) ([Permissions Documentation](https://antigravity.google/docs/permissions/)).  
  * Captures full-page screenshots and records video walkthroughs of UI interactions ([Screenshots Documentation](https://antigravity.google/docs/screenshots/)).  
> * **Limitations**: \[OBSERVED\] Cannot bypass CAPTCHAs, third-party SSO MFA walls, or hardware-bound security keys without human intervention.  
> * **StudyLab Architectural Boundary**: Antigravity provides the headless/headful browser driving mechanism. StudyLab can trigger it via workflows for local web UI verification (e.g., verifying an Anki deck export preview or local dashboard render).

### **3.13 Model Context Protocol (MCP)**

> * **Classification**: PLATFORM-PROVIDED (Protocol Engine) / HYBRID (Server Integration)  
> * **Transports & Schema**: \[DOCUMENTED\]  
  * Fully supports the open Model Context Protocol (MCP).  
  * Transports: Local subprocess stdio (command \+ args) and remote HTTP/SSE (serverUrl) ([MCP Documentation](https://antigravity.google/docs/mcp/)).  
> * **Configuration Paths**: \[DOCUMENTED\]  
  * Workspace configuration: .agents/mcp\_config.json.  
  * Global configuration: \~/.gemini/config/mcp\_config.json ([Migrating from Gemini CLI](https://antigravity.google/docs/cli/gcli-migration/)).  
  * Plugin configuration: mcp\_config.json at plugin root.  
> * **Relationship with Skills**: Skills provide *operational instructions and procedural logic* that guide the agent on *when* and *how* to call external MCP tools ([Authoring Skills Codelab](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)).  
> * **StudyLab Architectural Boundary**: Antigravity provides the MCP client runtime, handshake, and tool dispatch. StudyLab should only expose an MCP server if it needs to connect the agent to external databases (e.g., SQLite/Postgres note repositories) or complex out-of-process daemon tools; simple scripts should remain regular workspace files.

### **3.14 Worktrees**

> * **Classification**: PLATFORM-PROVIDED  
> * **Git Worktree Integration**: \[DOCUMENTED\]  
  * Antigravity 2.0 Projects provide native "New Worktree Mode" ([Projects Documentation](https://antigravity.google/docs/projects/)).  
  * When starting a task or spawning a subagent with workspace option branch, Antigravity provisions an independent Git worktree in an isolated background folder.  
  * Keeps the developer’s active working checkout clean.  
  * Prevents race conditions and file collisions between concurrent subagents working on the same codebase.  
> * **StudyLab Architectural Boundary**: Antigravity completely owns Git worktree lifecycle, folder provisioning, and branch isolation. StudyLab **must not** implement custom Git checkout or branch-swapping scripts.

### **3.15 Scheduling / Background Tasks**

> * **Classification**: PLATFORM-PROVIDED (Desktop App & SDK) / UNKNOWN (Headless Daemon Persistence)  
> * **Capabilities**: \[DOCUMENTED\]  
  * Antigravity 2.0 introduces scheduled tasks allowing users to define periodic time-based triggers (cron/minute-level) that automatically spawn agent sessions while away ([Feature Overview](https://antigravity.google/docs/features/)).  
  * Python SDK provides programmatic event triggers via triggers.py ([SDK Overview](https://antigravity.google/docs/sdk/overview/)).  
  * Antigravity CLI provides background task monitoring via /tasks and the /agents panel ([CLI Background Tasks](https://antigravity.google/docs/cli/subagents/)).  
> * **Unknown / Audit Item**: \[UNKNOWN\] Does the Antigravity 2.0 desktop scheduler run as a persistent system background daemon (systemd/launchd service), or does it terminate if the GUI desktop app is closed? (Queued for tomorrow's audit).  
> * **StudyLab Architectural Boundary**: Antigravity provides the task scheduling and execution trigger. StudyLab defines the target workflows or maintenance scripts to be invoked.

### **3.16 CLI (agy)**

> * **Classification**: PLATFORM-PROVIDED  
> * **Binary & TUI**: \[DOCUMENTED\]  
  * Installed as agy (binary path \~/.local/bin/agy on Linux/macOS) ([Getting Started with Antigravity CLI](https://antigravity.google/docs/cli/getting-started/)).  
  * Full-featured Terminal User Interface (TUI) with interactive slash commands (/agents, /tasks, /codesearch, /artifact, /rules, /skills).  
  * Fast keyboard shortcuts: Alt+J (teleport between running subagents), Ctrl+K (fast-path approvals).  
> * **Headless & CI/CD**: \[DOCUMENTED\]  
  * Supports headless execution for scripting and CI pipelines: agy \--headless (or passing direct prompts in non-interactive mode) with \--dangerously-skip-permissions for unattended runs ([Headless Mode](https://antigravity.google/docs/cli/headless/)).  
> * **StudyLab Architectural Boundary**: Antigravity CLI serves as the automation interface for running StudyLab verification tasks, linting passes, and agentic workflows from standard terminal scripts and GitHub Actions.

### **3.17 SDK (antigravity-sdk-python)**

> * **Classification**: PLATFORM-PROVIDED  
> * **Architecture**: \[DOCUMENTED\]  
  * Python library (google-antigravity, namespace from google.antigravity import Agent, LocalAgentConfig, types) ([Subagents SDK](https://antigravity.google/docs/sdk/subagents/), [Tools & Skills SDK](https://antigravity.google/docs/sdk/tools/)).  
  * Directly exposes the core Antigravity harness: multi-turn chat loops, custom tool registration, Pydantic structured output validation, streaming thoughts, MCP bridges, subagent spawning, and lifecycle hooks (PreToolUse, PostToolUse).  
> * **Maturity & Classification for StudyLab**:  
  * **NOW**: LATER. StudyLab should initially interface with Antigravity via standard configuration files (.agents/rules/, .agents/skills/, .agents/workflows/, and agy CLI). The Python SDK provides high future value for writing custom automated regression harnesses or headless orchestrators, but is not required for Day 1 repository operation.

### **3.18 Security Model**

> * **Classification**: PLATFORM-PROVIDED (Enforcement) / PROJECT-PROVIDED (Rules & Boundaries)  
> * **Platform Controls**: \[DOCUMENTED\]  
  * OS-level sandbox isolating filesystem writes to the project root.  
  * Domain-allowlisted network proxy gating all outbound HTTP/WebSocket requests.  
  * Granular permissions system (read\_url, execute\_url, terminal\_command).  
  * Security presets: "Default" (strict prompts), "Full machine" (broader filesystem access), "Unrestricted" (developer bypass) ([Feature Overview](https://antigravity.google/docs/features/), [Permissions](https://antigravity.google/docs/permissions/)).  
  * Permission persistence: User-granted permissions can be saved per-project in project settings.  
> * **StudyLab Controls**:  
  * Domain invariants (e.g., prohibiting modification of historical test logs, protecting master data files).

### **3.19 Extensions / Plugins**

> * **Classification**: PLATFORM-PROVIDED (Plugin Container) / PROJECT-PROVIDED (Contents)  
> * **Plugin Structure**: \[DOCUMENTED\]  
  * An Antigravity Plugin bundles:  
    * skills/: Subdirectory containing custom skills (SKILL.md).  
    * rules/: Subdirectory containing declarative rules (.md).  
    * mcp\_config.json: External tool integrations.  
    * hooks.json: Lifecycle shell event hooks ([Plugins Documentation](https://antigravity.google/docs/plugins/)).  
> * **StudyLab Architectural Boundary**: StudyLab itself can either be structured as an agentic project repository containing .agents/ or packaged as a reusable internal Antigravity plugin.

## **4\. Platform vs. Project vs. Hybrid Boundary**

The operational separation between Google Antigravity and StudyLab is delineated in the matrix below:

| Architectural Domain | Antigravity Responsibility | StudyLab Responsibility | Classification |
| :---- | :---- | :---- | :---- |
| **Agent Runtime & Loop** | Frontier LLM inference (Gemini 3.5/3.7), token streaming, multi-turn reasoning | None | PLATFORM-PROVIDED |
| **Workspace & Isolation** | Git worktree provisioning, directory isolation, cleanup | Branch naming conventions, commit message standards | PLATFORM-PROVIDED |
| **Terminal & Sandbox** | Process containerization, OS write restrictions, network domain gating | Domain build scripts, test suites, CLI tool definitions | PLATFORM-PROVIDED |
| **Browser Actuation** | Chrome automation, DOM extraction, clicking, typing, screenshots | Web application endpoints, UI verification criteria | PLATFORM-PROVIDED |
| **CLI & TUI** | Terminal interface, Alt+J subagent switcher, /artifact review | Headless CI/CD pipeline triggers and shell scripts | PLATFORM-PROVIDED |
| **Skills System** | Progressive disclosure (Tier 1/2/3), slash-command registry, script runner | Domain engineering skills (.agents/skills/\*) | HYBRID |
| **Rules Engine** | Parsing .agents/rules/, glob matching, always-on injection, character budget | Declarative project invariants and style rules | HYBRID |
| **Workflows** | Trajectory step sequencing, /workflow invocation, sub-workflow calls | Pipeline definitions (.agents/workflows/\*) | HYBRID |
| **Subagents** | Process spawning, context isolation, permission bubbling | Delegation criteria, task contracts, subagent roles | HYBRID |
| **Lifecycle Hooks** | Interception engine (PreToolUse, PostToolUse, Stop), exit code gating | Custom validation scripts, lint checks, audit filters | HYBRID |
| **Tool Integration (MCP)** | MCP protocol client (stdio / SSE), connection lifecycle | Domain MCP servers (if specialized daemons needed) | HYBRID |
| **Artifacts & Proofs** | Rendering diffs, plans, walkthroughs, screen recordings | Evidence storage standards, archiving to repository Git | HYBRID |
| **Domain Contracts** | None (platform is domain-blind) | Anki APKG schemas, study schedules, data integrity | PROJECT-PROVIDED |
| **Project Memory** | Ephemeral session state, conversation history | Git-versioned architectural decision records (ADRs) | PROJECT-PROVIDED |

## **5\. Antigravity vs. External Prior Art**

The following analysis compares Antigravity’s native architecture against established external agent frameworks:

### **5.1 Anthropic Skills (anthropics/skills)**

> * **What External Solves that Antigravity Already Solves**: Standardized SKILL.md structure with YAML frontmatter, tool integration instructions, and progressive discovery. Antigravity natively adopts an identical three-tier progressive disclosure model (Discovery \-\> Activation \-\> Execution) and integrates skills directly into slash commands.  
> * **What Antigravity Does NOT Solve**: Domain-specific skill content. Antigravity provides the empty harness; the actual instructions, scripts, and evaluation criteria remain the responsibility of the repository author.

### **5.2 Superpowers (obra/superpowers)**

> * **What External Solves that Antigravity Already Solves**: Subagent delegation, process monitoring, and tool management. Antigravity provides native asynchronous subagents with complete context isolation and interactive terminal navigation (Alt+J).  
> * **What Antigravity Does NOT Solve**: Opinionated task management patterns and specialized prompt choreography for specific multi-agent role handoffs. StudyLab must define its own handoff contracts.

### **5.3 Agent-Toolkit & Agentic Workspace Core (eai-org/agent-toolkit, agentic-workspace-core)**

> * **What External Solves that Antigravity Already Solves**: Filesystem sandboxing, workspace root restrictions, and safe terminal execution wrappers. Antigravity builds sandboxing directly into its native runtime.  
> * **What Antigravity Does NOT Solve**: Semantic validation of outputs. Antigravity checks whether a command is permitted by policy, not whether the output meets application-level correctness.

### **5.4 AGENTS.md Ecosystem**

> * **What External Solves that Antigravity Already Solves**: Global and local project context injection. Antigravity natively reads AGENTS.md and GEMINI.md at workspace root, plus .agents/rules/.  
> * **What Antigravity Does NOT Solve**: Synthesis of concise documentation. If AGENTS.md exceeds context budgets or contains ambiguous directives, the agent degrades. StudyLab must maintain high-density, concise documentation.

### **5.5 Planning-with-Files & Agent-Memory Systems (agentmemory, agent-memory-system)**

> * **What External Solves that Antigravity Already Solves**: Session history persistence and conversation rollback.  
> * **What Antigravity Does NOT Solve**: Structured cross-session knowledge consolidation. External memory systems often use vector embeddings to store memories across years. Antigravity scopes memory strictly to the project directory and session trees. StudyLab must use repository-backed, Git-versioned Markdown records instead of external vector memory.

## **6\. "DO NOT REBUILD" Analysis (Anti-Patterns to Avoid)**

The following capabilities are adequately provided by the Antigravity platform and **must not be engineered inside StudyLab**:

> 1. **DO NOT build a custom Agent Loop or LLM Orchestrator**: *Evidence*: Antigravity provides native multi-turn reasoning powered by frontier Gemini models with automatic context compaction and tool execution loops.  
> 2. **DO NOT build a custom Terminal Sandbox or Command Interceptor**: *Evidence*: Antigravity’s native Terminal Sandbox restricts filesystem access to workspace boundaries and enforces outbound network domain allowlists ([Sandbox Documentation](https://antigravity.google/docs/cli/sandbox/)).  
> 3. **DO NOT build a custom Git Worktree / Workspace Isolation Daemon**: *Evidence*: Antigravity 2.0 natively provisions, tracks, and isolates Git worktrees for parallel agents via "New Worktree Mode" ([Projects Documentation](https://antigravity.google/docs/projects/)).  
> 4. **DO NOT build a custom Browser Driving / Scraping Infrastructure**: *Evidence*: Antigravity includes a built-in browser subagent capable of DOM extraction, form actuation, full-page screenshot generation, and video walkthrough recording ([Screenshots](https://antigravity.google/docs/screenshots/)).  
> 5. **DO NOT build a custom Skill Discovery or Slash-Command Engine**: *Evidence*: Antigravity automatically indexes .agents/skills/, parses YAML frontmatter, handles 3-tier progressive disclosure, and maps skills to slash commands.  
> 6. **DO NOT build an external Vector Database for Code Search**: *Evidence*: Antigravity features instant workspace ripgrep querying and symbol search via /codesearch (/cs) with interactive keyboard navigation ([Code Search Documentation](https://antigravity.google/docs/cli/commands/codesearch/)).  
> 7. **DO NOT build a custom Subagent Process Manager**: *Evidence*: Antigravity natively manages concurrent subagents with isolated context windows, status bars, and keyboard shortcuts (Alt+J) ([CLI Background Tasks](https://antigravity.google/docs/cli/subagents/)).  
> 8. **DO NOT build an Artifact Diff / Review Viewer**: *Evidence*: Antigravity provides native desktop review panes and CLI /artifact panels with line-level commenting for diffs, plans, and walkthroughs.

## **7\. "STUDYLAB MUST OWN" Analysis**

The following responsibilities cannot be delegated to Antigravity and must be authored and maintained within the StudyLab repository:

> 1. **APKG Schema & Compilation Invariants**: Antigravity does not understand Anki database structures, note-type models, cloze deletion syntax, media hashing, or sync boundaries. StudyLab must encode these contracts into automated test suites and validation scripts.  
> 2. **Pedagogical Taxonomies & Syllabus Maps**: Curriculum structures (e.g., Computer Science diploma topics, Railway Recruitment Board exam modules) must live in repository knowledge files (docs/syllabus/).  
> 3. **Declarative Quality Rules (.agents/rules/)**: Project-specific invariants—such as "Never emit non-deterministic timestamps in generated media", "Always run Pytest before declaring task completion", and "Format output to Markdown tables"—must be maintained in .agents/rules/.  
> 4. **Domain Engineering Skills (.agents/skills/)**: The actual procedural guides (e.g., how to convert raw PDF textbook chapters into Anki flashcards, how to clean up audio transcriptions) must be authored as domain skills.  
> 5. **Pipeline Trajectories (.agents/workflows/)**: End-to-end task sequences (e.g., /ingest-chapter, /generate-anki, /audit-fidelity) must be authored as repeatable Markdown workflows.  
> 6. **Git-Tracked Project Memory & Decision Records**: Because Antigravity’s internal memory is ephemeral and session-scoped, StudyLab must maintain its own long-term memory in versioned records (e.g., docs/decisions/, records/changelog.md).  
> 7. **Verification & Audit Test Harnesses**: StudyLab must provide deterministic shell scripts and Python test suites that the agent can execute via run\_command to objectively verify its work.

## **8\. Hybrid Responsibilities Matrix**

The table below details where Antigravity mechanisms intersect with StudyLab policies:

| Mechanism | Antigravity Platform Provides | StudyLab Repository Provides | Concrete Interface |
| :---- | :---- | :---- | :---- |
| **Skills** | Discovery, frontmatter parsing, progressive disclosure, slash-command routing | Domain procedural instructions, reference materials, specialized Python scripts | Files in .agents/skills/\<skill-name\>/SKILL.md |
| **Rules** | Multi-mode activation (Manual, Always-on, Model decision, Glob), 12k char enforcement | Domain constraints, language standards, schema invariants, file boundaries | Files in .agents/rules/\*.md |
| **Workflows** | Trajectory orchestration, slash-command invocation (/name), step tracking | Deterministic step-by-step engineering procedures and quality gates | Files in .agents/workflows/\*.md |
| **Subagents** | Asynchronous execution harness, context isolation, permission bubbling | Delegation contracts, role personas, expected output schemas | YAML frontmatter (subagent: true) & invoke\_subagent prompts |
| **Lifecycle Hooks** | Interception points (PreToolUse, PostToolUse), gating return codes | Deterministic validation scripts, security assertions, pre-commit style checks | .agents/hooks.json mapping to local scripts |
| **Artifacts** | Visual presentation, diff viewers, screen video players, line-level feedback | Deliverable requirements, markdown report templates, Git-archived evidence | \~/.gemini/antigravity/ \-\> committed to reports/ |
| **External Tools** | MCP client transport (stdio / SSE), handshake, tool injection | Domain tool servers (if database or hardware integration needed) | .agents/mcp\_config.json |
| **Code Execution** | Isolated sandbox container, network proxy allowlist, execution approvals | Build scripts, Makefile targets, virtual environments, Pytest suites | Native terminal via run\_command |

## **9\. Unknowns, Conflicts, and Unverified Claims**

During this forensic audit, the following specific uncertainties and technical gaps were identified:

> 1. **Scheduled Task Daemon Lifetime** \[UNKNOWN\]: *Gap*: Documentation confirms scheduled tasks in Antigravity 2.0 can trigger agent sessions periodically ([Feature Overview](https://antigravity.google/docs/features/)). However, it is unverified whether this scheduler runs as a persistent OS background daemon (systemd/launchd) or requires the Antigravity desktop GUI process to remain running continuously.  
> 2. **Hook Execution Latency and Failure Semantics** \[UNKNOWN\]: *Gap*: While PreToolUse and PostToolUse are documented in hooks.json ([Hooks Documentation](https://antigravity.google/docs/hooks/)), the exact failure behavior when a hook script exits with non-zero or times out is not fully specified. Does it gracefully abort the tool call with a readable error to the model, or does it crash the agent session?  
> 3. **Subagent File Visibility Across Worktrees** \[UNKNOWN\]: *Gap*: In inherit workspace mode, can a subagent immediately read uncommitted, unstaged file edits made in-memory by the parent agent, or does it only see disk state?  
> 4. **Glob Rule Evaluation Mechanics** \[UNKNOWN\]: *Gap*: For rules configured with Glob: \*.py, does the rule inject dynamically only when the agent opens/edits a Python file, or does the mere presence of Python files in the workspace trigger it at session start?  
> 5. **CLI Headless Non-Interactive Parity** \[UNKNOWN\]: *Gap*: Does agy \--headless support all subagent delegation features and MCP tools with 100% fidelity compared to the interactive TUI, or are certain interactive prompts silently dropped?

## **10\. Tomorrow's Hands-On Audit Queue**

These concrete empirical experiments must be executed during tomorrow’s hands-on Antigravity audit session:

### **Experiment 01: Subagent Worktree File Visibility**

> * **Question**: Can a subagent operating in inherit mode read uncommitted file changes made by the parent agent, and how do worktrees isolate parallel agents?  
> * **Why It Matters**: Dictates whether StudyLab subagents can perform review passes on uncommitted code without manual disk flushes.  
> * **Current Evidence**: Documentation states subagents have isolated context windows and support inherit vs. branch workspaces ([Subagents Documentation](https://antigravity.google/docs/subagents/)).  
> * **Exact Hands-On Procedure**:  
  1. In the parent session, modify README.md with a unique string (TEST\_SENTINEL\_12345) but do NOT commit or save to Git index.  
  2. Invoke a subagent via invoke\_subagent instructing it to read README.md and report if TEST\_SENTINEL\_12345 is present.  
  3. Next, invoke a subagent with worktree mode (branch) and verify if the sentinel string is visible or isolated.  
  4. Record exact tool outputs and behavior.

### **Experiment 02: PreToolUse Hook Gating and Abort Behavior**

> * **Question**: Does returning "deny" from a PreToolUse hook script cleanly halt execution and surface the explanation string to the agent without crashing the session?  
> * **Why It Matters**: Essential for enforcing StudyLab’s safety boundaries (e.g., preventing irreversible deletion of source datasets).  
> * **Current Evidence**: Documentation specifies "deny" and "explanation" in PreToolUse hook schema ([Hooks Documentation](https://antigravity.google/docs/hooks/)).  
> * **Exact Hands-On Procedure**:  
  1. Configure .agents/hooks.json with a PreToolUse hook targeting run\_command matching rm \-rf \*.  
  2. Have the hook script output {"decision": "deny", "explanation": "Protected StudyLab directory"} and exit 0\.  
  3. Prompt the agent to attempt deleting a test scratch folder.  
  4. Verify whether the agent receives the explanation message and plans an alternative approach.

### **Experiment 03: Glob-Activated Rule Ingestion Boundary**

> * **Question**: At what exact moment does a Glob-based rule enter the active LLM context?  
> * **Why It Matters**: Prevents context window exhaustion if hundreds of glob-targeted rules are defined.  
> * **Current Evidence**: Documentation states glob rules apply to matching files ([Rules & Workflows](https://antigravity.google/docs/rules-workflows/)).  
> * **Exact Hands-On Procedure**:  
  1. Create a rule .agents/rules/python-invariants.md with glob src/\*\*/\*.py containing a unique keyword (PY\_INVARIANT\_ASSERTED).  
  2. Start an agent session and ask: "What rules are currently active in your context?" (Check if keyword is present).  
  3. Have the agent read a non-matching file (docs/notes.md). Check context.  
  4. Have the agent read src/main.py. Check if PY\_INVARIANT\_ASSERTED is now cited by the model.

### **Experiment 04: Headless CLI (agy) Execution with Subagents**

> * **Question**: Can the Antigravity CLI run unattended in CI pipelines while orchestrating subagents?  
> * **Why It Matters**: Validates whether StudyLab automated nightly builds can run via agy \--headless.  
> * **Current Evidence**: Documentation outlines headless flags ([Headless Mode](https://antigravity.google/docs/cli/headless/)).  
> * **Exact Hands-On Procedure**:  
  1. Write a shell command: agy \--headless \--dangerously-skip-permissions "Run pytest and generate summary".  
  2. Run the command inside a terminal and pipe output to ci\_test.log.  
  3. Inspect exit code, log output, and whether any subagents spawned during the trajectory succeeded.

### **Experiment 05: Desktop Scheduler Persistence Without GUI**

> * **Question**: Does a scheduled recurring task fire if the desktop window is closed or killed?  
> * **Why It Matters**: Determines if an external cron service is required for unattended background processing.  
> * **Current Evidence**: Scheduled tasks exist in Antigravity 2.0 ([Feature Overview](https://antigravity.google/docs/features/)).  
> * **Exact Hands-On Procedure**:  
  1. Schedule a task in Antigravity 2.0 to run in 3 minutes that appends a timestamp to heartbeat.txt.  
  2. Fully quit the Antigravity application (pkill antigravity or Quit via dock).  
  3. Wait 5 minutes. Inspect heartbeat.txt to verify if the file was modified by a background helper daemon.

## **11\. Provisional Architectural Boundary Model**

The verified operational boundary between Google Antigravity and StudyLab is represented below:  
`===================================================================================`  
                             `GOOGLE ANTIGRAVITY`  
                       `(Native Platform Substrate)`  
`===================================================================================`  
  `[ Frontier Reasoning Core ]  ──  Gemini 3.5 / Gemini 3.7 Flash Model Harness`  
  `[ Execution Sandbox ]        ──  Containerized OS Sandbox + Outbound Network Proxy`  
  `[ Workspace Manager ]        ──  Git Worktree Auto-Provisioning & Isolation`  
  `[ Tool Runtime ]             ──  Native Shell, Browser Actuation, MCP Client`  
  `[ Subagent Engine ]          ──  Asynchronous Parallel Worker Threads + Context Reset`  
  `[ Interception Engine ]      ──  Lifecycle Hooks (PreToolUse, PostToolUse, Stop)`  
  `[ UI & Presentation ]        ──  TUI (agy), Review Panes, Diff Inspectors, Artifacts`  
`===================================================================================`  
                                       `│`  
                                       `▼ (Bound via .agents/ config & Git tree)`  
`===================================================================================`  
                             `STUDYLAB REPOSITORY`  
                     `(Agent-Native Repository Governance)`  
`===================================================================================`  
  `┌─────────────────────────────────────────────────────────────────────────────┐`  
  `│ 1. DECLARATIVE INVARIANTS (.agents/rules/)                                  │`  
  `│    - Strict typing, data schema validation, deterministic audio hashes      │`  
  `│    - Glob-targeted rules for Python files, notes, and APKG compilers        │`  
  `├─────────────────────────────────────────────────────────────────────────────┤`  
  `│ 2. PROCEDURAL CAPABILITIES (.agents/skills/)                                │`  
  `│    - Domain SKILL.md packages with bundled black-box validation scripts     │`  
  `│    - 3-Tier progressive disclosure triggered by agent intent keywords       │`  
  `├─────────────────────────────────────────────────────────────────────────────┤`  
  `│ 3. END-TO-END TRAJECTORIES (.agents/workflows/)                             │`  
  `│    - Repeatable multi-step recipes (ingest -> extract -> compile -> test)    │`  
  `│    - Invoked via slash commands (/ingest, /build-apkg)                      │`  
  `├─────────────────────────────────────────────────────────────────────────────┤`  
  `│ 4. CANONICAL KNOWLEDGE & MEMORY (Git Versioned)                             │`  
  `│    - AGENTS.md / GEMINI.md (High-density architectural invariants)           │`  
  `│    - docs/decisions/ (Architectural Decision Records)                       │`  
  `│    - docs/syllabus/ (Pedagogical taxonomy and curriculum maps)              │`  
  `├─────────────────────────────────────────────────────────────────────────────┤`  
  `│ 5. VERIFICATION & SAFETY TEST HARNESSES                                     │`  
  `│    - Pytest suites, data integrity assertions, regression checkers          │`  
  `│    - Automated scripts wired to .agents/hooks.json for tool gating           │`  
  `└─────────────────────────────────────────────────────────────────────────────┘`  
                                       `│`  
                                       `▼`  
                              `Git Version Control`  
                     `(Sole Authoritative Source of Truth)`

## **12\. New Ideas Discovered**

During this forensic investigation, four high-value architectural ideas emerged from Antigravity’s native capabilities that can be integrated into StudyLab:

> 1. **Tiered Hook Safety Gates (PreToolUse)**: Instead of writing custom pre-commit Git hooks, StudyLab can use Antigravity’s PreToolUse hook in .agents/hooks.json with "decision": "deny" to deterministically intercept destructive commands (e.g., modifying raw learning logs or force-pushing Git branches) before the shell ever executes them.  
> 2. **Worktree Isolation for Risky Refactoring**: By triggering complex tasks in "New Worktree Mode" or using branch workspace mode for subagents, StudyLab can instruct agents to experiment with aggressive codebase refactoring in fully isolated branches. If the task fails, the worktree is discarded without touching the main checkout.  
> 3. **Mermaid Diagram Generation within Artifacts**: Antigravity CLI and Desktop natively render Mermaid diagrams embedded inside Markdown artifacts ([Reviewing Artifacts](https://antigravity.google/docs/cli/artifacts/)). StudyLab workflows can instruct agents to produce architecture and syllabus dependency diagrams as Mermaid artifacts for visual verification.  
> 4. **Agent Trajectory Recording for Verification Proofs**: For browser-based UI validation (e.g., verifying web preview renders of generated study cards), Antigravity automatically captures screen recordings and screenshots in its Walkthrough artifacts ([Walkthrough Documentation](https://antigravity.google/docs/walkthrough/)). StudyLab can mandate that any UI change include an artifact screenshot before approval.

## **13\. Risks and Open Questions**

> 1. **Context Window Inflation from Broad Rules**: *Risk*: If too many rules in .agents/rules/ are configured as Always On, they will consume a significant portion of the prompt budget on every turn, degrading reasoning performance and triggering early context compaction. *Mitigation*: Default to Glob or Model Decision activation modes; keep Always On strictly reserved for universal safety invariants.  
> 2. **Local Path Lock-in (\~/.gemini/antigravity/)**: *Risk*: Antigravity stores artifacts, walkthrough recordings, and knowledge cache in \~/.gemini/antigravity/ outside the project repository. If a developer runs tasks across different machines, these artifacts do not automatically synchronize via Git. *Mitigation*: Mandate that workflows copy all final verification reports and data deliverables into repository-tracked paths (e.g., artifacts/, reports/).  
> 3. **Drift Between Global and Workspace Configurations**: *Risk*: If developer workstations have conflicting global rules in \~/.gemini/GEMINI.md or global skills in \~/.gemini/config/skills/, agent behavior will diverge across environments. *Mitigation*: Enforce repository-local configuration (.agents/rules/, .agents/skills/, .agents/mcp\_config.json) as the primary standard and treat global configuration as strictly developer-personal preferences.

## **14\. Verified Source List**

The findings in this report are grounded in the following primary and secondary sources:

### **Tier 1 — Official Google Antigravity Documentation & Announcements**

> * [Google Antigravity Home & Overview](https://antigravity.google/docs/home/) — Architectural structure, surface offerings, and developer roadmap.  
> * [Google Antigravity Agent Overview](https://antigravity.google/docs/agent) — Multi-step reasoning system, tool harnesses, and planning trajectory.  
> * [Google Antigravity Skills Specification](https://antigravity.google/docs/skills/) — SKILL.md format, YAML frontmatter, directory conventions, and progressive disclosure.  
> * [Google Antigravity Rules and Workflows](https://antigravity.google/docs/rules-workflows/) — Declarative constraints, glob matching, always-on behavior, and 12k character limits.  
> * [Google Antigravity Subagents Architecture](https://antigravity.google/docs/subagents/) — Context isolation, asynchronous multi-threading, invoke\_subagent, and workspace options.  
> * [Google Antigravity Hooks Specification](https://antigravity.google/docs/hooks/) — PreToolUse, PostToolUse, Stop events, regex matchers, and gating decisions.  
> * [Google Antigravity Projects & Worktrees](https://antigravity.google/docs/projects/) — Project scoping, multi-folder configurations, and Git worktree isolation.  
> * [Google Antigravity Model Context Protocol (MCP)](https://antigravity.google/docs/mcp/) — stdio and SSE transport schemas and server configurations.  
> * [Google Antigravity Artifacts Documentation](https://antigravity.google/docs/artifacts/) — Implementation plans, diff reviews, line comments, and visual media.  
> * [Google Antigravity Walkthroughs](https://antigravity.google/docs/walkthrough/) — Task summaries, screenshots, and browser recordings.  
> * [Google Antigravity Permissions Model](https://antigravity.google/docs/permissions/) — read\_url, execute\_url, and terminal sandboxing domain allowlists.  
> * [Google Antigravity CLI Reference & Subagents](https://antigravity.google/docs/cli/subagents/) — TUI navigation, Alt+J teleport, Ctrl+K, and custom agent Markdown schemas.  
> * [Google Antigravity CLI Headless Mode](https://antigravity.google/docs/cli/headless/) — Non-interactive execution, scripting, and CI/CD parameters.  
> * [Google Antigravity Python SDK Overview](https://antigravity.google/docs/sdk/overview/) — Programmatic interfaces, custom tools, policies, and lifecycle hooks.  
> * [Migrating from Gemini CLI to Antigravity](https://antigravity.google/docs/cli/gcli-migration/) — Directory mappings (.agents/skills/, .agents/mcp\_config.json, GEMINI.md, AGENTS.md).  
> * [Google Developers Blog: Build with Google Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/) — Platform launch and agent-first development paradigm (Nov 20, 2025).  
> * [Google Developers Codelab: Getting Started with Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity) — Antigravity 2.0 standalone application, IDE, and project setup (July 22, 2026).  
> * [Google Developers Codelab: Authoring Antigravity Skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills) — Declarative skill authoring and tool directorship (June 18, 2026).  
> * [Google AI for Developers: Antigravity Managed Agent](https://ai.google.dev/gemini-api/docs/antigravity-agent) — Gemini API interaction and hosted sandbox environments (Aug 26, 2026).  
> * [Google Cloud Blog: Expanding Antigravity for Enterprise Customers](https://cloud.google.com/blog/products/ai-machine-learning/expanding-google-antigravity-for-enterprise-customers) — Enterprise Gemini integration and developer tool bundling (Aug 21, 2026).

### **Tier 2 — Google Talks, Demos, and Conference Publications**

> * [Google I/O 2026 Developer Highlights](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/) — Antigravity 2.0 multi-agent collaboration, Gemini API enhancements (May 19, 2026).  
> * [Official Demo: Google Antigravity Hands-On](https://www.youtube.com/watch?v=uzFOhkORVfk) — Practical multi-surface walkthrough and tool execution (Nov 20, 2025).  
> * [Official Session: Inside Google Antigravity 2.0](https://www.youtube.com/watch?v=K3YYr6yauAw) — SDLC automation, multi-agent dispatch, and worktree isolation (July 11, 2026).

### **Tier 3 — Verified Independent Technical Analyses**

> * [Google Antigravity Agent Manager Explained: Deep Dive](https://arjankc.com.np/blog/google-antigravity-agent-manager-explained/) — Architectural origin, cognitive harness, MCP integration, and systemic boundaries (Feb 18, 2026).  
> * [Antigravity Architectural Audit & Security Analysis](https://dev.to/dmitry_labintcev_9e611e04/why-google-antigravity-is-an-architectural-house-of-cards-70-vulnerabilities-mass-bans-3i69) — Process lifecycle analysis, local gRPC communication, and token handling (March 5, 2026).