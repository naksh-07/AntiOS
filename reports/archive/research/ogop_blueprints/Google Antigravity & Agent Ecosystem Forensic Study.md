# **Deep Research Mission 2: Google Antigravity & Agent Ecosystem Forensic Study**

## **1\. Executive Summary**

Google's agentic development ecosystem is anchored by **Google Antigravity**—launched in public preview in November 2025 ([Introducing Google Antigravity](https://antigravity.google/blog/introducing-google-antigravity)) and upgraded to **Antigravity 2.0** in May 2026 ([Introducing Google Antigravity 2.0](https://antigravity.google/blog/introducing-google-antigravity-2)). Antigravity is a dedicated, agent-first software engineering platform comprising a standalone desktop command center (Antigravity 2.0), a full-featured agentic IDE fork ([Overview | Antigravity Docs](https://antigravity.google/docs/ide/overview/)), a terminal user interface and headless engine ([Antigravity CLI Overview](https://antigravity.google/docs/cli/overview/)), and a programmatic Python runtime ([Antigravity SDK Overview](https://antigravity.google/docs/sdk/overview/)).  
Rather than embedding an assistant inside a traditional text editor side-panel, Google Antigravity inverts the control hierarchy: **the development environment is embedded inside the agent runtime**. The platform natively solves multi-agent execution, local Git worktree isolation, sandbox containerization, interactive artifact generation (implementation plans, code diffs, Mermaid diagrams, browser screen/video recordings), Model Context Protocol (MCP) transport, and dynamic subagent delegation powered by frontier reasoning models (**Gemini 3 Pro / Gemini 3.1** and **Gemini 3.6/3.7 Flash**).  
**Core Strategic Finding for StudyLab:** StudyLab must **not** build an agent runtime, process supervisor, container sandbox, or low-level tool dispatcher. Antigravity already provides a production-grade execution harness. Instead, StudyLab must construct an **Antigravity-First Agent Operating System**: a declarative repository layer of **Skills** (methodology and domain tasks), **Rules** (invariants and style boundaries), **Workflows** (trajectory-level sequences), **MCP servers** (domain-specific inspection), and **Repository-Local Memory Banks** (to bridge Antigravity's session-reset boundary).

## **2\. Antigravity Architecture Map**

Based on official technical documentation from [Google Antigravity Docs](https://antigravity.google/docs/home/), the runtime architecture separates execution mechanisms from project policy:  
`┌─────────────────────────────────────────────────────────────────────────────┐`  
`│                              REASONING MODEL                                │`  
`│          Gemini 3 Pro / Gemini 3.1  │  Gemini 3.6 / 3.7 Flash               │`  
`│           (Optional third-party: Claude Sonnet 4.5, GPT-OSS)                │`  
`└──────────────────────────────────────┬──────────────────────────────────────┘`  
                                       `│`  
`┌──────────────────────────────────────▼──────────────────────────────────────┐`  
`│                    ANTIGRAVITY AGENT HARNESS (RUNTIME)                      │`  
`│                                                                             │`  
`│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────┐  │`  
`│  │ Execution Modes       │ │ Security / Sandbox    │ │ Worktree Manager  │  │`  
`│  │ - Planning Mode       │ │ - System Sandboxing   │ │ - Inherit / Local │  │`  
`│  │ - Fast Mode           │ │ - Network Allowlists  │ │ - Isolated Branch │  │`  
`│  │ - /boost (Deep Pipe)  │ │ - Tool Approval Gates │ │ - Shared Dir      │  │`  
`│  └───────────────────────┘ └───────────────────────┘ └───────────────────┘  │`  
`└──────┬────────────┬─────────────┬────────────┬─────────────┬───────────┬────┘`  
       `│            │             │            │             │           │`  
       `▼            ▼             ▼            ▼             ▼           ▼`  
`┌─────────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐`  
`│    TOOLS    ││   SKILLS  ││   RULES   ││ WORKFLOWS ││    MCP    ││ SUBAGENTS │`  
`│ Local Bash, ││.agents/   ││.agents/   ││.agents/   ││stdio, SSE,││invoke_sub-│`  
`│ File Read / ││  skills/  ││  rules/   ││workflows/ ││Streamable ││  agent:   │`  
`│ Write/Diff, ││SKILL.md,  ││GEMINI.md, ││/workflow- ││HTTP, OAuth││ research, │`  
`│ Browser UI  ││scripts/,  ││Glob, Mode,││name       ││Google Auth││ browser,  │`  
`│ Actuation   ││references ││Always On  ││Composable ││mcp_config ││ self, cust│`  
`└──────┬──────┘└─────┬─────┘└─────┬─────┘└─────┬─────┘└─────┬─────┘└─────┬─────┘`  
       `│             │            │            │            │            │`  
       `└─────────────┴────────────┴─────┬──────┴────────────┴────────────┘`  
                                        `│`  
                                        `▼`  
`┌─────────────────────────────────────────────────────────────────────────────┐`  
`│                          PROJECT CONTEXT & MEMORY                           │`  
`│  - Ephemeral Session Context (Clean Slate on New Conversation)              │`  
`│  - Knowledge Items (Agent-generated heuristics, stored in project metadata) │`  
`│  - Codebase AST / Symbol Index (Indexed on repository trust confirmation)   │`  
`└──────────────────────────────────────┬──────────────────────────────────────┘`  
                                       `│`  
                                       `▼`  
`┌─────────────────────────────────────────────────────────────────────────────┐`  
`│                            EVIDENCE & ARTIFACTS                             │`  
`│  - Implementation Plans (.md with task checklists)                          │`  
`│  - Unified File Diffs & Granular Line Comments                              │`  
`│  - Visual Artifacts: Mermaid architecture charts & screenshots              │`  
`│  - Verification Media: WebM video recordings of browser execution           │`  
`└──────────────────────────────────────┬──────────────────────────────────────┘`  
                                       `│`  
                                       `▼`  
`┌─────────────────────────────────────────────────────────────────────────────┐`  
`│                         SURFACES / INTERACTION                              │`  
`│  Antigravity 2.0 (Desktop) │ Antigravity IDE │ CLI (agy) │ Python SDK       │`  
`│  Remote Control Web App (with mobile push notifications)                    │`  
`└─────────────────────────────────────────────────────────────────────────────┘`

### **Layer Ownership Breakdown**

| Layer | Primary Owner | Responsibility |
| :---- | :---- | :---- |
| **Model / Foundation Reasoning** | Google Antigravity | Token generation, reasoning, function calling, tool parameter emission. |
| **Agent Harness & Sandbox** | Google Antigravity | Container sandboxing, process execution, network allowlists, git worktree lifecycle. |
| **Tools (Core)** | Google Antigravity | File I/O, diff patching, terminal command execution, headless Chrome automation. |
| **Domain Tools & Integrations** | StudyLab (via MCP) | Anki collection introspection, APKG validation, custom database connectors. |
| **Skills (Capability Packages)** | StudyLab (.agents/skills/) | Specific domain procedures, algorithmic instructions, test runner scripts. |
| **Rules (Invariants)** | StudyLab (.agents/rules/) | Architectural boundaries, linting standards, immutable project contracts. |
| **Workflows (Pipelines)** | StudyLab (.agents/workflows/) | Multi-step operational trajectories (release, audit, sync). |
| **Subagent Delegation Policy** | StudyLab (in Prompts/Skills) | Instructing parent agents when and how to invoke subagents for fan-out. |
| **Evidence & Verification Policy** | StudyLab | Establishing acceptance criteria for generated artifacts and diff reviews. |
| **Long-Term Project Memory** | StudyLab (Repository Files) | Grounded file-based memory banks (context/, task.md) surviving chat resets. |

## **3\. Antigravity Capability Inventory**

Every capability is classified into one of four architectural categories:

> 1. **PLATFORM-PROVIDED**: Antigravity reliably provides this; StudyLab must not rebuild it.  
> 2. **PROJECT-PROVIDED**: Antigravity has no domain knowledge; StudyLab must build/encode this.  
> 3. **HYBRID**: Antigravity supplies the execution harness; StudyLab supplies policy, schema, or content.  
> 4. **FUTURE / OPTIONAL**: Valuable later, but not required for Day 1 baseline.

| Capability Area | Specific Feature | Classification | Technical Rationale & StudyLab Strategy |
| :---- | :---- | :---- | :---- |
| **Agent Execution** | Autonomous reasoning loop | **PLATFORM-PROVIDED** | Built into Gemini 3 / Antigravity harness. Handles multi-turn tool loops natively. |
| **Agent Execution** | Planning Mode vs Fast Mode | **PLATFORM-PROVIDED** | Native conversation-level setting. StudyLab uses Planning Mode for multi-file work. |
| **Agent Execution** | Deep Reasoning (/boost) | **PLATFORM-PROVIDED** | Multi-agent iterative verification pipeline for complex bugs and architectural refactoring. |
| **Workspace / Isolation** | Git Worktree Provisioning | **PLATFORM-PROVIDED** | Antigravity 2.0 spins up dedicated background worktrees (New Worktree Mode) automatically. |
| **Workspace / Isolation** | Multi-Folder Projects | **PLATFORM-PROVIDED** | Projects can group multiple discrete local repos/directories into a unified agent scope. |
| **Security / Execution** | Terminal Command Sandboxing | **PLATFORM-PROVIDED** | Containerized sandbox with permission presets (Default, Full machine, Unrestricted). |
| **Security / Execution** | Network Allowlisting | **PLATFORM-PROVIDED** | Outbound domains filtered by read\_url and execute\_url policies. |
| **Security / Execution** | Project Safety Invariants | **PROJECT-PROVIDED** | Antigravity does not know domain-specific forbidden file mutations or database safety rules. |
| **Browser Integration** | Chrome Automation (/browser) | **PLATFORM-PROVIDED** | Dedicated browser subagent using isolated Chrome profiles and DevTools protocol. |
| **Browser Integration** | WebM Video & Screenshots | **PLATFORM-PROVIDED** | Visual actuation recordings automatically saved as reviewable artifacts. |
| **Browser Integration** | Web Verification Suites | **PROJECT-PROVIDED** | StudyLab encodes explicit acceptance criteria and assertions for browser runs. |
| **Artifact System** | Interactive Implementation Plans | **PLATFORM-PROVIDED** | Agent generates rich Markdown plans with checkable tasks and dependency breakdowns. |
| **Artifact System** | Visual Diff & Review Panel | **PLATFORM-PROVIDED** | Side-by-side file diffs with line-level commenting across desktop and CLI. |
| **Artifact System** | Evidence Audit Contract | **HYBRID** | Antigravity produces artifacts; StudyLab mandates what evidence must be included. |
| **Skills System** | Skill Discovery & Loading | **PLATFORM-PROVIDED** | Progressive disclosure: matches name & description before reading SKILL.md. |
| **Skills System** | Skill Folder Standards | **HYBRID** | Standard directory format (SKILL.md, scripts/, references/) populated by StudyLab. |
| **Rules System** | Rule Scoping & Activation | **PLATFORM-PROVIDED** | Supports Always On, Manual (@), Model Decision, and Glob pattern triggers. |
| **Rules System** | Domain Constraints | **PROJECT-PROVIDED** | StudyLab writes .agents/rules/\*.md (typing, APKG schema, commit standards). |
| **Workflows System** | Trajectory Sequencer | **PLATFORM-PROVIDED** | Parses markdown steps, supports composable workflow calls (/workflow-name). |
| **Workflows System** | Domain Pipelines | **PROJECT-PROVIDED** | StudyLab authors release, testing, and synchronization workflow recipes. |
| **Subagents** | Subagent Invocation | **PLATFORM-PROVIDED** | Native invoke\_subagent tool with context-isolated sessions and permission bubbling. |
| **Subagents** | Built-in Archetypes | **PLATFORM-PROVIDED** | Out-of-the-box research, browser, and self subagents. |
| **Subagents** | Multi-Agent Coordination | **HYBRID** | Runtime launches workers; StudyLab skills define decomposition and handoff rules. |
| **MCP Integration** | MCP Client Transport | **PLATFORM-PROVIDED** | Native stdio, SSE, and Streamable HTTP support with OAuth and Google Auth integration. |
| **MCP Integration** | Custom Domain Servers | **PROJECT-PROVIDED** | Custom MCP servers for local StudyLab SQLite/Anki collection access. |
| **Context & Memory** | Codebase Symbol Indexing | **PLATFORM-PROVIDED** | Automatic AST indexing of files upon granting repository trust. |
| **Context & Memory** | Ephemeral Knowledge Items | **PLATFORM-PROVIDED** | UI-surfaced knowledge items extracted automatically during sessions. |
| **Context & Memory** | Persistent Cross-Session Memory | **PROJECT-PROVIDED** | Native memory resets between chats; StudyLab must maintain file-based memory banks. |
| **Automation / CI** | Headless CLI Streaming Mode | **PLATFORM-PROVIDED** | agy \--input-format stream-json \--output-format stream-json for scripted invocation. |
| **Automation / CI** | Scheduled Tasks (/schedule) | **PLATFORM-PROVIDED** | Recurring and one-off timer-based prompts configured via UI or slash command. |
| **Remote Operations** | Remote Control Dashboard | **PLATFORM-PROVIDED** | Cloud relay dashboard to drive and monitor local agents from mobile or browser. |
| **Programmatic Runtime** | Antigravity Python SDK | **FUTURE / OPTIONAL** | google.antigravity SDK available for standalone external services if CLI is insufficient. |

## **4\. Skills, Rules, Workflows, Agents, and Subagents Comparison**

Understanding the structural boundaries between Antigravity’s primitives prevents architectural confusion:

### **Comparative Matrix**

| Mechanism | Purpose | Scope | Trigger Mechanism | Persistent? | StudyLab Architectural Use |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Rules** | Impose constraints, invariants, coding standards, and negative instructions. | Global (\~/.gemini/GEMINI.md) or Workspace (.agents/rules/\*.md). | Always On, Glob match (\*.py), Model Decision, or manual @mention. | Yes (committed in Git). | **Guardrails**: APKG integrity rules, strict typing, no unauthorized external dependencies. |
| **Workflows** | Automate deterministic or guided multi-step procedural pipelines. | Global or Workspace (.agents/workflows/\*.md). | Slash command (/workflow-name) or nested call from another workflow. | Yes (committed in Git). | **Pipelines**: /audit-repo, /build-deck, /verify-release, /generate-anki-notes. |
| **Skills** | Teach specialized domain capabilities, mental models, and black-box script execution. | Workspace (.agents/skills/\<name\>/) or Global (\~/.gemini/skills/). | Progressive Disclosure: Model matches frontmatter description during intent routing. | Yes (committed in Git). | **Specialist Capabilities**: anki-apkg-builder, deep-research, pedagogical-formatter. |
| **Agents (Main)** | Execute primary conversation goal, orchestrate tools, manage user dialog. | Workspace / Project level. | User prompt, schedule trigger, or remote command. | Ephemeral session state. | Primary developer pairing interface in IDE/CLI/Desktop. |
| **Subagents** | Concurrently execute isolated, narrow subtasks without context bloat. | Child process spawned by parent agent. | Platform tool call (invoke\_subagent) or /boost. | Ephemeral (terminates on completion). | Parallel file auditing, independent research streams, web verification. |

### **Deep Dive: Antigravity Native Skills**

Antigravity adopts an open skill format aligned with emerging industry standards ([Skills | Antigravity Docs](https://antigravity.google/docs/skills/)):  
`.agents/skills/<skill-name>/`  
`├── SKILL.md                  # Required: frontmatter metadata and operational instructions`  
`├── scripts/                  # Executable deterministic code (black boxes)`  
`├── references/               # Deep technical specs, schemas, and lookup tables`  
`└── assets/                   # Templates, boilerplate, and static files`

#### **Progressive Disclosure Architecture**

> 1. **Discovery (Level 1):** When a conversation initializes, Antigravity loads *only* the skill name and description into the system prompt context. Token overhead is minimal (\~30–50 tokens per skill).  
> 2. **Activation (Level 2):** When the agent encounters a task matching the description, it triggers an internal tool to load the full SKILL.md body.  
> 3. **Execution (Level 3):** The agent reads referenced files in references/ or executes deterministic scripts in scripts/ on demand via bash/terminal tools, preventing context window exhaustion.

#### **YAML Frontmatter Specification**

`---`  
`name: anki-apkg-generator`  
`description: Generates valid Anki .apkg packages from structured flashcard notes using genanki. Use when creating, converting, or validating Anki decks.`  
`---`

*Best Practice Rule:* The description must be written in the third person, state concrete verbs, and list exact trigger scenarios and file types.

### **Comparison: Antigravity Skills vs External Skill Frameworks**

| Feature | Antigravity Native Skills | Anthropic Agent Skills (\~/.claude/skills) | Superpowers (Prime Radiant) | planning-with-files Standard |
| :---- | :---- | :---- | :---- | :---- |
| **Directory** | .agents/skills/\<name\>/ & Global | \~/.claude/skills/\<name\>/ | Repo root / config plugins | Project root / .skills/ |
| **File Structure** | SKILL.md \+ scripts/ \+ references/ | SKILL.md \+ bundled tools | Composable markdown rules | Markdown files \+ state files |
| **Loading Model** | Progressive disclosure on demand | Static load or pre-prompt injection | Injected into system prompt | Progressive file reading |
| **Script Execution** | Native container sandbox or host | Host bash tool execution | CLI execution harness | Agent bash tools |
| **Plugin Packaging** | Supported (plugins/\<name\>/plugin.json) | Custom npm / JSON bundles | Git repository / submodules | Flat directory |

*Conclusion:* Antigravity’s .agents/skills/ convention is structurally identical to the broader 2026 Agent Skills standard. StudyLab should build 100% compliant .agents/skills/ packages.

## **5\. Artifacts, Knowledge, and Memory Analysis**

### **The Antigravity Artifact Model**

Antigravity explicitly separates raw conversational churn from structured deliverables called **Artifacts** ([Artifacts \- Google Antigravity](https://antigravity.google/docs/artifacts/)):

> * **Implementation Plans:** Markdown documents detailing architectural decisions, phased tasks, and verification steps. Humans review and approve these before code modification begins.  
> * **Unified Diffs:** Staged file changes presented in interactive side-by-side views. Developers can submit line-by-line comments that the agent consumes as corrective feedback.  
> * **Mermaid Diagrams:** Declarative architecture and sequence charts rendered visually in the desktop UI and CLI overlay.  
> * **Browser Playbacks:** High-frame-rate WebM recordings capturing how the browser subagent navigated and verified a local web server or web application.

### **The Knowledge & Memory Problem: What Antigravity Lacks**

A critical architectural boundary lies in **state persistence across sessions**:

> 1. **Context Reset Boundary:** When a user starts a new conversation in Antigravity or runs an independent CLI turn, the conversational context window completely resets to a clean slate.  
> 2. **Ephemeral Knowledge Items:** While Antigravity 2.0 has an internal "Knowledge" tab where the agent logs discovered heuristics ([Antigravity Knowledge Items](https://discuss.ai.google.dev/t/knowledge-items/126774)), developer experience in the field confirms this storage is opaque, semi-automatic, and frequently unpopulated across fresh tasks.  
> 3. **The Solution — Repository-Local Memory Banks:** External systems such as agentmemory and planning-with-files solve this by treating **Git repository files as long-term memory**.

### **Memory Stratification: Where State Should Live**

`┌───────────────────────────────────────┬───────────────────────────────────────┐`  
`│     INSIDE GOOGLE ANTIGRAVITY         │        INSIDE STUDYLAB (GIT REPO)     │`  
`├───────────────────────────────────────┼───────────────────────────────────────┤`  
`│ • Ephemeral conversation context      │ • Canonical architecture decisions    │`  
`│ • Staged uncommitted file diffs       │ • Domain data schemas & invariants    │`  
`│ • Active subagent task checklists     │ • Continuous progress ledger (task.md)│`  
`│ • Temporary browser recordings (.webm)│ • System patterns & architectural log │`  
`│ • Local codebase AST / symbol index   │ • Historical audit & verification logs│`  
`│ • UI-level tool permission grants     │ • Golden test cases and Anki fixtures │`  
`└───────────────────────────────────────┴───────────────────────────────────────┘`

*Architectural Directive:* StudyLab must maintain an explicit context/ or memory/ folder in the repository containing systemPatterns.md, activeContext.md, and progress.md (the "Memory Bank" pattern). Antigravity agents must be instructed via Rules to read these files on session start and update them on session close.

## **6\. CLI, SDK, IDE, and Standalone 2.0 Comparison**

Google provides four distinct interaction surfaces for Antigravity ([Choose Your Surface | Antigravity Docs](https://antigravity.google/docs/home/)):

| Attribute | Antigravity 2.0 Standalone | Antigravity IDE | Antigravity CLI (agy) | Antigravity Python SDK |
| :---- | :---- | :---- | :---- | :---- |
| **Primary Form Factor** | Dedicated Desktop App (Electron) | VS Code Fork / Extension | Terminal User Interface (TUI) | Headless Python Library |
| **Core Target User** | Agent Orchestrator / Lead Dev | Hands-on Software Developer | Terminal Power User / DevOps | Systems Engineer / Platform Dev |
| **Multi-Agent Manager** | Full visual Manager UI (5+ parallel) | Integrated side panel | Background panel (Alt+J) | Programmatic Task Concurrency |
| **Workspace Handling** | Git worktrees & Multi-folder | Single workspace or worktree | CWD repo / Worktree branches | Configurable directory scopes |
| **Artifact Inspection** | Visual diff viewer, WebM player | VS Code diff editor & webview | Keyboard TUI reviewer (/artifact) | Programmatic data objects |
| **CI / Automation Fit** | Unsuitable (GUI-only) | Unsuitable (GUI-only) | **High** (--input-format stream-json) | **Very High** (custom pipelines) |
| **Slash Commands** | Supported via prompt input | Supported via prompt input | Supported natively | Custom handlers / API methods |
| **StudyLab Role** | Daily mission control & monitoring | Core manual editing & code review | **Automation, scheduled tasks, CI** | Future external microservices |

### **Automation Blueprint: CLI Headless Streaming Mode**

The Antigravity CLI includes a high-performance headless mode designed for automated execution ([Headless mode | Antigravity Docs](https://antigravity.google/docs/cli/headless/)):  
`agy --input-format stream-json --output-format stream-json --workspace /path/to/studylab`

By keeping standard input open, external CI scripts or local daemons can feed sequential tasks into a single warmed-up conversation process, bypassing startup latency and receiving structured JSON execution telemetry line-by-line.

## **7\. Google AI Studio and "Google Spark" Investigation**

### **Google AI Studio vs Google Antigravity**

| Feature / Dimension | Google AI Studio | Google Antigravity |
| :---- | :---- | :---- |
| **Primary Purpose** | Fast model prototyping, prompt engineering, API key management. | End-to-end autonomous software development and repo orchestration. |
| **Execution Environment** | Ephemeral cloud playground; sandbox code execution for Python. | Local filesystem, native terminal, host compilers, local Docker/sandbox. |
| **Tool Calling Surface** | Manual OpenAPI/JSON function declarations. | Native file system tools, terminal, browser agent, MCP servers. |
| **Project Awareness** | Limited to uploaded files / system prompt context. | Full AST indexing of local repository, Git worktrees, multi-folder projects. |
| **Multi-Agent Routing** | None (single model playground). | Native subagent delegation, /boost, and parallel agent management. |
| **Output Delivery** | Text tokens, structured JSON schemas. | Functional code commits, implementation plan artifacts, visual browser diffs. |

*Verdict:* Google AI Studio is optimal for drafting prompt templates, evaluating raw Gemini 3 reasoning parameters, and testing structured Pydantic schemas. Antigravity is the platform where software is engineered, executed, and verified.

### **The "Google Spark" Forensic Investigation**

The term "Spark" in Google's AI ecosystem refers to a specific, recently unveiled product:

> * **Official Product Name:** **Gemini Spark** ([Gemini Spark Overview](https://gemini.google/overview/agent/spark/)).  
> * **Launch & Availability:** Announced by Sundar Pichai at **Google I/O in May 2026**; rolled out to Google AI Ultra subscribers across mid-2026 ([Gemini Spark Updates](https://blog.google/innovation-and-ai/products/gemini-app/gemini-spark-updates-july-2026/)).  
> * **Product Classification:** A **24/7 autonomous personal AI agent** hosted in Google Cloud.  
> * **Core Capabilities:**  
  1. *Continuous Background Execution:* Operates asynchronously on dedicated cloud compute even when the user is offline or laptops are closed.  
  2. *Deep Google Workspace Integration:* Direct API access to read, create, and modify Gmail, Google Calendar, Google Drive, Docs, Sheets, Slides, Tasks, and Google Keep.  
  3. *Cloud Web Browsing:* Built-in cloud Chrome agent for navigating web portals, research extraction, and travel booking.  
  4. *Multi-Modal Trigger Schedules:* Event-driven scheduling including cron/time-based intervals, conditional web monitors, and email arrival triggers.  
  5. *Agent Skills:* Supports natural-language capability skills loaded dynamically into the personal assistant persona.  
> * **Relationship to Antigravity:**  
  * **Gemini Spark** is consumer- and productivity-centric: it manages digital life, communication, personal files, and schedule automation in Google Cloud.  
  * **Antigravity** is developer- and engineering-centric: it operates locally on filesystems, drives compilers, executes unit tests in terminal containers, manages Git worktrees, and connects to developer MCP servers.  
> * **StudyLab Relevance:**  
  * *Antigravity* is the engine that builds and maintains the StudyLab software codebase.  
  * *Gemini Spark* can act as an external scheduler or alerting agent that notifies the user when scheduled Antigravity builds finish or when study decks are due for review.

## **8\. Whitepaper and Research Landscape**

### **Verification of Whitepaper Existence**

**Forensic Finding:** A formal academic paper or standalone technical report titled *"Google Antigravity"* or *"Antigravity Agent Architecture"* **does not exist**. Google released Antigravity as a developer product via the Google Developer Group / Google Labs organization, documenting its architecture through official product documentation ([Antigravity Docs](https://antigravity.google/docs/home/)), technical engineering blogs ([Antigravity Blog](https://antigravity.google/blog/introducing-google-antigravity)), and interactive developer codelabs ([Getting Started with Google Antigravity \- Codelabs](https://codelabs.developers.google.com/getting-started-google-antigravity)).

### **Relevant Technical Publications and Literature**

The underlying algorithmic foundations, agent protocols, and evaluations supporting Antigravity are documented across the following peer-reviewed and official corporate publications:

> 1. **Google Technical Whitepaper: "Agent Tools & Interoperability" (May 2026):** Released as part of Google's AI Agents curriculum ([5-Day AI Agents Intensive](https://www.kaggle.com/learn-guide/5-day-agents-vibecoding)). Details the standardization of open protocols including **Model Context Protocol (MCP)**, **Agent2Agent (A2A)** collaboration primitives, **Agent-to-User Interface (A2UI)** for generative artifacts, and transactional safety layers.  
> 2. **Google DeepMind: "AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms" (May 2025 / May 2026 update):** Documents DeepMind's research on Gemini-driven coding loops that iteratively generate code patches, evaluate them against execution test harnesses, and discover novel algorithmic solutions ([AlphaEvolve Blog](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)).  
> 3. **Model Card & Foundations: "Gemini 3 Pro Model Card" (Google DeepMind, 2025/2026):** Documents the core reasoning capabilities, multi-step tool use, code generation benchmarks (SWE-bench Verified), and extended reasoning trajectories that power Antigravity's Planning Mode and /boost pipeline ([Gemini 3 Pro Model Card](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf)).  
> 4. **Empirical Case Study on Antigravity in Research: arXiv:2605.16191 (May 2026):** *"Optimized Three-Dimensional Photovoltaic Structures with LLM..."* ([arXiv:2605.16191](https://arxiv.org/html/2605.16191v1)). Demonstrates combining autonomous LLM tree-search with **Google's Antigravity coding agent** to identify reward-hacking exploits in physics simulations and write automated Python patches.  
> 5. **Agent-Computer Interface Research: "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" (arXiv:2405.15793 / arXiv:2604.26275):** Foundational research establishing that structuring tool interfaces (custom file viewers, lint linters, constrained diffs) significantly outperforms granting agents raw shell access. This research directly influenced Antigravity's Artifact and Review panel designs.  
> 6. **Industry Framework: "Agentic Software Engineering: Foundational Pillars and a Research Roadmap" (arXiv:2509.06216):** Defines the Structured Agentic Software Engineering (SASE) paradigm, advocating for hierarchical task planning, isolated execution worktrees, and artifact-grounded human-in-the-loop approvals.

## **9\. Antigravity vs. External Prior Art Comparison**

| Capability | Antigravity Native Capability | External Community Best Practice | StudyLab Recommendation |
| :---- | :---- | :---- | :---- |
| **Agent Execution** | Built-in Gemini 3 harness with Planning/Fast modes | Python ReAct loops, LangGraph, AutoGen | **Antigravity Native** (Do not rebuild) |
| **Skills System** | .agents/skills/\<name\>/SKILL.md (progressive disclosure) | \~/.claude/skills, Superpowers | **Antigravity Native** (Author compliant skills) |
| **Rules System** | .agents/rules/\*.md (Glob, Model Decision, Always On) | .cursorrules, CLAUDE.md, .windsurfrules | **Antigravity Native** (Define declarative rules) |
| **Workflows** | .agents/workflows/\*.md invoked via /workflow-name | Task shell scripts, Makefile chains | **Antigravity Native** (Encode procedural steps) |
| **Planning System** | Interactive Markdown Implementation Plans & Checklists | task.md checklists, markdown scratchpads | **Hybrid** (Antigravity plan \+ StudyLab file log) |
| **Memory System** | Codebase index \+ ephemeral Knowledge tab | agentmemory, Mem0 MCP, Memory Bank | **StudyLab Owns** (Repository file memory bank) |
| **Orchestration** | Parallel desktop Manager \+ Worktree isolate | Multi-agent swarms, CrewAI, AutoGen | **Antigravity Native** (Use Manager \+ worktrees) |
| **Subagents** | invoke\_subagent (research, browser, self, custom) | Sub-processes, LangGraph sub-graphs | **Antigravity Native** (Govern via prompt/skills) |
| **Verification** | Code diff review, terminal test run, WebM video | Custom pytest runners, CI gatekeepers | **Hybrid** (Antigravity harness \+ StudyLab tests) |
| **Evidence** | Artifacts panel (Markdown, Mermaid, Diffs, Media) | Structured JSON logs, PR descriptions | **Hybrid** (Antigravity UI \+ StudyLab checklists) |
| **Docs Management** | Native file read/write, AST symbol index | Vector DB RAG, LlamaIndex | **Antigravity Native** (Use local docs & tools) |
| **Git / GitHub** | Worktree provisioning, branch isolation, diff review | Git CLI, GitHub CLI (gh), PR bots | **Hybrid** (Antigravity worktree \+ git commands) |
| **Browser Auto** | Chrome subagent via DevTools MCP, video recordings | Playwright, Puppeteer, Browserbase | **Antigravity Native** (Use /browser subagent) |
| **MCP Integration** | Native client (stdio, SSE, Streamable HTTP, OAuth) | FastMCP, official MCP SDKs | **Antigravity Native** (Deploy custom servers) |
| **Scheduling** | Native Scheduled Tasks (/schedule, time triggers) | System cron, GitHub Actions, Celery | **Antigravity Native** (Use native schedules) |
| **Evaluation** | Pre/PostInvocation lifecycle hooks, token auditing | DeepEval, Braintrust, promptfoo | **Hybrid** (Hooks \+ StudyLab golden test suites) |

## **10\. DO NOT REBUILD (Platform-Provided)**

StudyLab must strictly avoid spending engineering effort creating custom software for the following capabilities:

> 1. **Custom Agent Execution Runtime / Loop:** Do not write Python ReAct loops, state-machine steppers, or LLM API polling harnesses. Antigravity manages context window management, tool selection, error retries, and token streaming natively.  
> 2. **Multi-Agent Worker Supervisors & Worktree Isolation:** Do not implement custom Git branch managers or multi-process thread pools. Antigravity 2.0 spawns and tracks parallel agent sessions in isolated background Git worktrees (New Worktree Mode) out of the box.  
> 3. **Headless Browser & Screen Recording Framework:** Do not integrate Playwright or Puppeteer harnesses for web testing. Antigravity’s browser subagent handles Chrome DevTools actuation, DOM navigation, screenshots, and WebM video artifact generation natively.  
> 4. **Interactive Artifact & Diff Review Panels:** Do not build bespoke web dashboards to show file diffs or progress steps. Antigravity provides rich desktop and terminal review panels (/artifact) with line-level commenting.  
> 5. **Terminal Sandboxing & Permission Proxies:** Do not build custom Docker or eBPF sandboxes for executing bash commands. Antigravity provides configurable sandbox modes with granular network and filesystem allowlists.  
> 6. **Model Context Protocol (MCP) Client Infrastructure:** Do not write custom MCP client managers or connection pools. Antigravity connects directly to stdio, SSE, and Streamable HTTP MCP servers via configuration.  
> 7. **Task Scheduling Engine:** Do not build local cron daemons for periodic agent execution. Antigravity natively supports scheduled tasks via the /schedule slash command and Settings panel.

## **11\. STUDYLAB MUST OWN (Project-Provided)**

Antigravity is completely domain-agnostic. StudyLab must engineer the following project-specific assets:

> 1. **StudyLab Domain Schemas & Invariants:** The specifications governing flashcard hierarchies, Cloze syntax, Anki deck IDs, tag taxonomies, and note schemas. Antigravity has no intrinsic understanding of spaced repetition or educational curricula.  
> 2. **APKG Binary Packaging Contracts & Verification:** The deterministic Python scripts (genanki, SQLite schema checks) that compile, validate, and verify .apkg files without database corruption.  
> 3. **Repository-Local Memory Banks:** A dedicated repository directory (context/ or memory/) containing activeContext.md, systemPatterns.md, decisions.md, and task.md. This preserves project truth across Antigravity conversation resets.  
> 4. **Domain-Specific Rules (.agents/rules/):** Declarative Markdown guardrails enforcing coding style (e.g., strict TypeScript/Python typing, no raw SQL mutations, zero external network calls without flags).  
> 5. **Operational Workflows (.agents/workflows/):** Markdown workflow playbooks (audit.md, release.md, sync-anki.md) that guide the agent through multi-step repository procedures.  
> 6. **Custom StudyLab MCP Servers:** A specialized lightweight MCP server exposing read/query operations over the local Anki SQLite database and StudyLab content repositories.  
> 7. **Golden Verification Test Suites:** Automated integration test suites that the agent must execute and pass before submitting any implementation plan or code diff for human review.

## **12\. HYBRID RESPONSIBILITIES (Mechanism vs. Policy)**

Where Antigravity provides the technical mechanism, StudyLab must inject the organizational policy:  
`┌─────────────────────────────────────────────────────────────────────────────┐`  
`│                       HYBRID OPERATIONAL CONTRACT                           │`  
`├──────────────────────┬───────────────────────────┬──────────────────────────┤`  
`│ COMPONENT            │ ANTIGRAVITY MECHANISM     │ STUDYLAB POLICY / INPUT  │`  
`├──────────────────────┼───────────────────────────┼──────────────────────────┤`  
`│ Skills System        │ Progressive disclosure,   │ Domain skill content,    │`  
`│                      │ SKILL.md parsing, script  │ decision trees, Anki     │`  
`│                      │ execution harness.        │ generation logic.        │`  
`├──────────────────────┼───────────────────────────┼──────────────────────────┤`  
`│ Subagent Delegation  │ invoke_subagent tool,     │ Orchestration heuristics,│`  
`│                      │ context isolation,        │ task decomposition rules,│`  
`│                      │ permission bubbling.      │ specialist role prompts. │`  
`├──────────────────────┼───────────────────────────┼──────────────────────────┤`  
`│ Artifacts & Evidence │ Interactive markdown,     │ Mandatory verification   │`  
`│                      │ diff viewers, WebM video  │ gates, test coverage     │`  
`│                      │ playback UI.              │ requirements, checklists.│`  
`├──────────────────────┼───────────────────────────┼──────────────────────────┤`  
`│ MCP Integration      │ JSON configuration,       │ StudyLab custom server   │`  
`│                      │ stdio/HTTP transport,     │ endpoints, SQLite schema │`  
`│                      │ tool exposure to model.   │ queries, domain methods. │`  
`├──────────────────────┼───────────────────────────┼──────────────────────────┤`  
`│ Lifecycle Hooks      │ Pre/PostInvocation events,│ CI status reporting,     │`  
`│                      │ injectSteps capability,   │ custom audit logs,       │`  
`│                      │ trajectory telemetry.     │ memory bank auto-sync.   │`  
`└──────────────────────┴───────────────────────────┴──────────────────────────┘`

## **13\. Research-Derived StudyLab Architecture**

### **DRAFT ONLY — TO BE VALIDATED IN ANTIGRAVITY AUDIT**

The StudyLab Agent Operating System is structured in three clear tiers:  
`===============================================================================`  
                       `TIER 1: PLATFORM RUNTIME (Google)`  
`===============================================================================`  
   `Google Antigravity 2.0 Desktop / Antigravity IDE / Antigravity CLI (agy)`  
     `├── Execution Engine: Gemini 3 Pro (Planning) & Gemini 3.6 Flash (Fast)`  
     `├── Isolation Harness: Git Worktree Manager (Background branches)`  
     `├── Security: Terminal Container Sandbox & Domain Allowlists`  
     `└── Native Surfaces: Artifact Reviewer, DevTools Browser Subagent, MCP Client`  
`===============================================================================`  
                                      `│`  
                                      `▼`  
`===============================================================================`  
                   `TIER 2: STUDYLAB OS LAYER (Repository Policies)`  
`===============================================================================`  
   `.agents/`  
     `├── rules/                          # Invariants & Guardrails`  
     `│     ├── anki-integrity.md         # Schema constraints (Always On)`  
     `│     ├── code-style.md             # Python/TS standards (*.py, *.ts)`  
     `│     └── safe-terminal.md          # Disallowed commands & operations`  
     `├── workflows/                      # Trajectory Automation (/workflow)`  
     `│     ├── audit-codebase.md         # /audit-codebase pipeline`  
     `│     ├── generate-curriculum.md    # /generate-curriculum pipeline`  
     `│     └── build-apkg.md             # /build-apkg packaging & test`  
     `├── skills/                         # Domain Capability Packages`  
     `│     ├── apkg-builder/             # SKILL.md + scripts/genanki_build.py`  
     `│     ├── curriculum-parser/        # SKILL.md + references/taxonomy.json`  
     `│     └── deep-audit/               # SKILL.md + scripts/verify_links.py`  
     `└── mcp_config.json                 # Project MCP Server Registrations`  
`===============================================================================`  
                                      `│`  
                                      `▼`  
`===============================================================================`  
                `TIER 3: STUDYLAB DATA & REPOSITORY STATE (Source of Truth)`  
`===============================================================================`  
   `context/                              # Persistent File Memory Bank`  
     `├── activeContext.md                # Current sprint goals, recent changes`  
     `├── systemPatterns.md               # Architecture diagrams & component design`  
     `└── decisions.md                    # ADRs (Architectural Decision Records)`  
   `src/studylab/                         # Application Source Code`  
   `tests/                                # Golden Verification Suites`  
   `decks/                                # Generated Learning Decks & Artifacts`  
`===============================================================================`

## **14\. New Ideas Discovered During Research**

Several undocumented or non-obvious platform capabilities emerged during this investigation:

> 1. **Interactive Prompt Alignment (/grill-me):** Antigravity features a dedicated slash command, /grill-me ([Getting Started with Antigravity 2.0](https://antigravity.google/docs/getting-started/)), which instructs the model to pause before planning and rigorously interview the developer with targeted questions to resolve ambiguities upfront.  
> 2. **Deep Reasoning Multi-Agent Pipeline (/boost):** The /boost command ([Boost deep reasoning](https://antigravity.google/docs/boost/)) activates an automated pipeline that decomposes hard problems across specialized subagents and runs iterative verification loops before proposing code diffs.  
> 3. **Native Headless Stream JSON Protocol:** The CLI supports bidirectional streaming over standard I/O (agy \--input-format stream-json \--output-format stream-json), allowing external orchestrators to run long-running, interactive sessions without process restart overhead.  
> 4. **Trajectory Step Injection via Hooks (hooks.json):** Through PreInvocation hooks ([Hooks | Antigravity Docs](https://antigravity.google/docs/hooks/)), developers can inject synthetic tool calls, ephemeral messages, or prompt context dynamically before the model executes a turn.  
> 5. **Session Forking (/fork):** The CLI allows developers to type /fork ([Managing Conversations](https://antigravity.google/docs/cli/conversations/)) to branch both the conversational thread and the workspace state into an exploratory path, with /resume allowing an instant rollback.  
> 6. **Mobile Remote Control with Push Notifications:** Antigravity 2.0 features a web dashboard ([Remote Control](https://antigravity.google/docs/remote-control/)) enabling developers to monitor agent execution on desktop workstations from mobile devices, receiving push alerts when implementation plans need approval.

## **15\. Risks and Unknowns (Requiring Hands-On Testing)**

The following operational risks cannot be verified from documentation alone and must be audited directly in the local Antigravity environment:

> 1. **Subagent File Lock Contention:** When multiple subagents operate in inherit mode (sharing the working directory rather than using branch/worktree mode), simultaneous file writes or git operations may collide.  
> 2. **Context Window Degradation on Large Repositories:** How gracefully the AST index scales on repositories exceeding 10,000 files, and whether symbol lookups cause context truncation during Planning Mode.  
> 3. **Custom Python Tool Sandboxing Limits:** When the agent executes custom scripts inside skills/\<name\>/scripts/, does the default sandbox isolate network calls (e.g., preventing outbound calls to external APIs without explicit grants)?  
> 4. **Native Knowledge Items Reliability:** Determining the exact conditions under which Antigravity populates its internal "Knowledge" tab, and confirming whether it can be relied upon for critical architectural invariants.  
> 5. **MCP Latency Overheads:** Evaluating the latency overhead added to the model's reasoning loop when multiple local stdio MCP servers are active simultaneously.

## **16\. Antigravity Audit Checklist (Tomorrow's Field Validation)**

Use this concrete checklist when executing the direct, hands-on audit inside the Antigravity desktop and CLI environment:

### **Phase A: Workspace & Worktree Verification**

> * \[ \] **Test 1: Project Creation:** Initialize an Antigravity Project pointing to the StudyLab repository. Verify multi-folder configuration options.  
> * \[ \] **Test 2: Worktree Isolation:** Start an agent in New Worktree Mode. Verify via terminal that git worktree list displays the newly allocated branch directory.  
> * \[ \] **Test 3: Parallel Sessions:** Spawn two concurrent agents on the same repository (one in Local Mode, one in New Worktree Mode). Confirm zero git index lock interference.

### **Phase B: Skills & Progressive Disclosure**

> * \[ \] **Test 4: Skill Discovery:** Place a minimal test skill at .agents/skills/test-evaluator/SKILL.md with distinct frontmatter. Prompt the agent generally and verify it detects the skill's existence without reading full contents.  
> * \[ \] **Test 5: Skill Activation:** Issue a prompt triggering the skill's exact domain. Verify in the trajectory log that the agent executes the internal read tool to load SKILL.md.  
> * \[ \] **Test 6: Script Black-Box Execution:** Have the skill instruct the agent to run an executable in scripts/runner.py. Verify execution succeeds within the terminal sandbox.

### **Phase C: Rules & Workflows Enforcement**

> * \[ \] **Test 7: Rule Glob Trigger:** Add a rule in .agents/rules/no-raw-eval.md matching \*.py. Ask the agent to edit a Python file and verify the rule is automatically injected into the turn context.  
> * \[ \] **Test 8: Workflow Invocation:** Create a workflow at .agents/workflows/sanity-check.md. Run /sanity-check in the chat panel. Verify sequential execution of each step.  
> * \[ \] **Test 9: Prompt Elicitation (/grill-me):** Run /grill-me "Add user auth". Verify that the agent pauses and asks structured clarifying questions before drafting a plan.

### **Phase D: Artifacts, Browser & MCP**

> * \[ \] **Test 10: Artifact Generation:** In Planning Mode, request an architectural plan. Confirm the artifact appears in the visual Artifact Review panel with checkable tasks.  
> * \[ \] **Test 11: Line Comment Feedback:** Add a line comment on a proposed code diff in the review pane. Submit feedback and verify the agent modifies the diff accordingly.  
> * \[ \] **Test 12: Browser Automation (/browser):** Run /browser targeting a local HTTP server. Verify navigation, screenshot capture, and .webm recording playback in the review UI.  
> * \[ \] **Test 13: Local MCP Server Registration:** Add a test SQLite MCP server into mcp\_config.json. Confirm that the server tools appear in the agent's available tools list.

### **Phase E: Memory Bank Verification**

> * \[ \] **Test 14: Cross-Session Memory Retention:** In Chat Session 1, write a specific architectural constraint into context/decisions.md. Terminate the chat. Start Chat Session 2 with a clean slate, instruct the agent to check context/decisions.md, and confirm full contextual recall.

### **Verified Primary Sources & Citations**

> * [Google Antigravity Official Portal](https://antigravity.google/)  
> * [Google Antigravity Documentation Home](https://antigravity.google/docs/home/)  
> * [Introducing Google Antigravity (Nov 18, 2025\)](https://antigravity.google/blog/introducing-google-antigravity)  
> * [Introducing Google Antigravity 2.0 (May 19, 2026\)](https://antigravity.google/blog/introducing-google-antigravity-2)  
> * [Getting Started with Google Antigravity \- Google Codelabs](https://codelabs.developers.google.com/getting-started-google-antigravity)  
> * [Antigravity Skills Specification](https://antigravity.google/docs/skills/)  
> * [Antigravity Rules and Workflows](https://antigravity.google/docs/rules-workflows/)  
> * [Antigravity Subagents Architecture](https://antigravity.google/docs/subagents/)  
> * [Antigravity Artifact Review & Steering](https://antigravity.google/docs/artifacts/)  
> * [Antigravity Browser Overview](https://antigravity.google/docs/ide/browser/)  
> * [Antigravity CLI Overview & Headless Mode](https://antigravity.google/docs/cli/overview/)  
> * [Antigravity Python SDK Reference](https://antigravity.google/docs/sdk/overview/)  
> * [Gemini Spark Official Product Page](https://gemini.google/overview/agent/spark/)  
> * [Gemini Spark Chrome Web Browsing Updates (July 2026\)](https://blog.google/innovation-and-ai/products/gemini-app/gemini-spark-updates-july-2026/)  
> * [Gemini 3 Pro Model Card (Google DeepMind)](https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf)  
> * [Google 5-Day AI Agents Course & Agent Tools Whitepaper](https://www.kaggle.com/learn-guide/5-day-agents-vibecoding)  
> * [DeepMind AlphaEvolve: Gemini-powered Coding Agent](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)  
> * [Case Study with Antigravity Coding Agent (arXiv:2605.16191)](https://arxiv.org/html/2605.16191v1)