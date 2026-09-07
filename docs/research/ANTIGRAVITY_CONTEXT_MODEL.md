# Google Antigravity Context Flow & Memory Architecture
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: Grounded Technical Analysis  
**Primary Sources**: Builtin Customization Guides (`agy-customizations`), Context Pipeline Specifications, and Empirical Token Diagnostics.  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. The Four Tiers of Context Delivery

Context in Google Antigravity does not arrive as a single undifferentiated prompt. It is constructed through a 4-tier pipeline managed by the Language Server on every invocation turn:

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: AUTOMATICALLY AVAILABLE (Static System Context)    │
│ System Identity + <user_information> + Tool Declarations    │
│ + <skills> Catalog (Metadata) + AGENTS.md (Root/CWD Rules)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ TIER 2: PROGRESSIVE DISCLOSURE (Loaded On Demand)           │
│ SKILL.md (via view_file) + Lazy MCP Schemas + Model Rules   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ TIER 3: EPHEMERAL INJECTION (Synchronous Hook Payloads)     │
│ PreInvocation injectSteps + Stop hook rejection reasons     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ TIER 4: TRANSIENT TRAJECTORY (Conversation Memory)          │
│ User Prompts + Model Thoughts + Tool Arguments + Outputs    │
└─────────────────────────────────────────────────────────────┘
```

---

### Tier 1: Automatically Available (Static System Context)
- **Platform System Prompt**: `[FACT]` Invariant system instructions establishing identity ("Antigravity, a powerful agentic AI coding assistant designed by Google DeepMind"), tool usage guidelines, communication style, and planning mode directives.
- **`<user_information>`**: `[OBSERVED]` Environment metadata:
  - Host OS (`windows`).
  - Active workspace URIs and CorpusNames (`[URI] -> [CorpusName]`).
  - App Data Directory (`C:\Users\Suraj\.gemini\antigravity`).
  - Current `Conversation ID`.
- **Tool Schema Injections**: `[FACT]` Full parameter schemas for native tools (`run_command`, `view_file`, `replace_file_content`, `write_to_file`, `list_dir`, `grep_search`, `invoke_subagent`, `manage_subagents`, etc.).
- **Eager MCP Tools**: `[FACT]` Full schemas for pre-registered tools (e.g. `mcp_gemini-api-docs_*`).
- **Lazy MCP Catalog**: `[FACT]` Simple list of server names and tool identifiers without parameters (e.g. `# chrome-devtools-mcp`, `# github-mcp-server`).
- **`<skills>` Catalog**: `[FACT]` XML manifest containing skill `name`, physical `path`, and `description`. Crucially, **the body of the skill is NOT present**.
- **Root & CWD Rules (`AGENTS.md` / `GEMINI.md`)**: `[FACT]` The runtime walks up from CWD to repository root and mounts discovered markdown rules into the system prompt.

---

### Tier 2: Progressive Disclosure (Loaded On Demand)
To prevent context exhaustion in token-dense workflows, Antigravity avoids frontloading heavy documentation:
- **Skill Activation**: `[FACT]` When the agent or user invokes a skill, the agent calls `view_file` on `SKILL.md`. Only then are procedural runbooks, step lists, and script paths read into active context. Reference manuals under `references/` are read on an even deeper tier on demand.
- **Lazy MCP Tool Schemas**: `[FACT]` If the model decides to invoke a lazy MCP tool, it calls `view_file` on `~/.gemini/antigravity/mcp/<server>/<tool>.json` to read the arguments, then executes via `call_mcp_tool`.
- **Model-Decision Rules**: `[FACT]` Rules configured with `trigger: model_decision` remain unloaded until the semantic matcher detects relevance to the prompt.

---

### Tier 3: Ephemeral Injection (Lifecycle Hooks)
- **`PreInvocation` Hooks**: `[FACT]` Hook scripts can return `injectSteps: [{"ephemeralMessage": "..."}]`. This injects a transient system alert into the current turn without polluting permanent conversation history.
- **`Stop` Hook Rejections**: `[FACT]` When the Stop Gate rejects task conclusion, it returns `decision: "continue"` with `reason: "..."`. This reason is injected as an authoritative corrective directive forcing the model back into the execution loop.

---

### Tier 4: Transient Trajectory (Conversation Memory)
- **Turn History**: `[FACT]` The sequence of user messages, assistant thinking tokens, tool invocations, and tool execution outputs.
- **Compaction & Truncation**: `[OBSERVED]` When tool outputs exceed 46,080 bytes, they are truncated and written to `.system_generated/steps/<stepIdx>/output.txt`. When total conversation tokens approach model limits, older turns are compacted, losing granular tool outputs.

---

## 2. Subagent Context Isolation

When an agent calls `invoke_subagent`:
- **Context Inheritance**: `[FACT]` **ZERO.** Subagents do NOT inherit the parent conversation history, tool results, or prior thoughts.
- **Injected Context**: `[FACT]` The subagent receives:
  1. Standard system instructions and environment `<user_information>`.
  2. Active workspace rules (`AGENTS.md`).
  3. Available skill catalog.
  4. The explicit `Prompt` passed by the parent in `invoke_subagent`.
- **Parent Visibility**: `[FACT]` The parent cannot read the subagent's internal reasoning or tool calls directly; it receives only structured handoff messages via `send_message` or completion notifications.

---

## 3. Session Persistence & Cross-Session Amnesia

| Entity | Turn Boundary | Session Boundary (Same Chat) | Session Boundary (New Chat) | Machine Restart |
| :--- | :---: | :---: | :---: | :---: |
| **Active LLM Context Window** | Preserved | Preserved | **LOST (Zeroed)** | **LOST (Zeroed)** |
| **Conversation SQLite DB** | Appended | Persisted | Stored as separate file | Persisted |
| **Transcript (`transcript.jsonl`)** | Appended | Appended | New transcript file | Persisted |
| **Artifacts (`brain/<id>/`)** | Preserved | Persisted | Isolated to old ID | Persisted |
| **Workspace Files / Git** | Persisted | Persisted | **PERSISTED (Ground Truth)** | **PERSISTED** |
| **Central Experience DB** | Stagnant | Stagnant | Persisted | Persisted |

**The Amnesia Law**: In native Antigravity, a fresh session starts with **100% amnesia**. It retains zero memory of past decisions, tested hypotheses, or architectural discoveries unless those discoveries were written directly to **Workspace Files** or loaded via declarative adapters.

---

## 4. The Critical Problem: Why Does an Agent Rediscover a Project Instead of Navigating Directly to the Subsystem?

When a user gives a command in a large repository (e.g. "Fix the button bug in the frontend"), why does a standard Antigravity agent spend 5–10 turns searching, listing directories, and stumbling through irrelevant files instead of going straight to the exact component?

The investigation reveals five foundational causes:

### 1. Zero File Tree in System Prompt
The system prompt contains only the root path string: `c:\Users\Suraj\Documents\Antigravity\AntiOs`. It does NOT contain a directory tree or file listing. The LLM has zero knowledge of whether the frontend is in `frontend/`, `src/ui/`, `packages/web/`, `client/`, or `static/`. It must guess and search.

### 2. Context Window Cost Economics
A large enterprise repository contains 20,000 to 100,000 files. Dumping a recursive file tree or symbol table into the prompt would consume 200,000+ tokens on *every turn*, costing immense latency, credit expenditure, and diluting model attention. Antigravity intentionally leaves the prompt lean.

### 3. Stateless Foundation Model Design
The Gemini model is inherently stateless. While Antigravity's local language server indexes the codebase via ripgrep and AST trackers, it does not push this knowledge into the model's context window unless queried. Information is **pull-based**, never push-based.

### 4. Codebase Volatility Guarantee
In real software development, git branches switch, dependencies update, and human developers edit files asynchronously. If an agent assumed yesterday's file map was immutable ground truth, it would make hallucinated edits against deleted or refactored files. The agent searches to ground its actions in physical disk reality.

### 5. Lack of Standardized Project Wayfinding Manifests
In most repositories, project architecture is buried in unstructured human markdown (`README.md`, developer wikis) written for humans, not agents. Without a structured, machine-readable navigation index, the agent has no choice but to execute exploratory commands (`list_dir`, `grep_search`).

---

## 5. How AntiOS Solves the Rediscovery Penalty

AntiOS eliminates project rediscovery **without dumping the repository into context and without custom agent runtimes** by introducing **Three-Tier Deterministic Wayfinding**:

```
                              User Task
                                  │
                       ┌──────────▼──────────┐
                       │  AGENTS.md Directive│
                       │ "Consult Adapter"   │
                       └──────────┬──────────┘
                                  │
                       ┌──────────▼──────────┐
                       │ antios.config.json  │
                       │ Subsystem Manifests │
                       └──────────┬──────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   Frontend Module          Backend Module          Database Layer
   `packages/ui/`           `services/api/`         `migrations/`
   Test: `npm test`         Test: `cargo test`      Test: `pytest`
```

1. **Declarative Wayfinding Adapter (`antios.config.json`)**:
   - Pre-indexes key subsystems, root entrypoints, protected boundaries, and required test runners in a compact (<100 lines) JSON manifest at the repository root.
   - The agent reads this single small file and instantly knows the exact filesystem coordinate and test command for every subsystem.

2. **Progressive Control Plane Skill (`.agents/skills/antios`)**:
   - When active, instructs the agent to read `antios.config.json` before initiating codebase search, cutting exploration turns from 8 turns to 1 turn.

3. **Physical Handoff Memory (`handoff.md`)**:
   - When a session concludes, the agent commits a standardized 5-part transition block (Observation, Logic Chain, Caveats, Conclusion, Verification Method) directly into the repository root.
   - When a fresh session starts tomorrow, reading `handoff.md` immediately restores the prior session's state in exactly 1 tool call.
