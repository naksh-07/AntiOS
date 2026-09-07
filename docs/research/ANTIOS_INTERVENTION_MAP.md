# AntiOS Architectural Intervention Map & System Taxonomy
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: Architectural Synthesis & Integration Blueprint  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. Native Antigravity Attachment Topology

AntiOS does not replace or fork the Antigravity runtime. It attaches directly to Antigravity's seven native extension surfaces:

```
GOOGLE ANTIGRAVITY ENGINE (language_server.exe)
│
├── 1. CONTEXT PIPELINE
│     └── Dynamic Ephemeral Injections (PreInvocation injectSteps)
│     └── Static XML Manifests (<user_information>, <skills> catalog)
│
├── 2. RULES ENGINE
│     └── Hierarchical Directory Rules (AGENTS.md / GEMINI.md)
│     └── Persistent Project Behavioral Contracts (.agents/rules/)
│
├── 3. SKILLS ENGINE
│     └── Progressive Engineering Runbooks (.agents/skills/*)
│     └── Deep Procedural Tools (antios, antios-engineer, antios-verifier)
│
├── 4. AGENTS & SUBAGENTS
│     └── Context-Isolated Maker-Checker Archetypes (invoke_subagent)
│     └── Adversarial Audit Verification (Victory Auditors)
│
├── 5. TOOL LIFECYCLE HOOKS (hooks.json)
│     ├── PreToolUse  ──> Physical Boundary Guard (pre_tool_guard.py)
│     ├── PostToolUse ──> Zero-Dependency Telemetry Emitter (emit_event.py)
│     └── Stop        ──> Physical Test Ratchet & Verification Gate (stop_gate.py)
│
├── 6. PROJECT FILESYSTEM & STATE
│     ├── Declarative Project Adapter (antios.config.json)
│     └── Append-Only Engineering Memory (handoff.md, dead-ends.md)
│
└── 7. SESSION CONTINUITY
      └── Zero-Turn State Resumption across Compaction and Fresh Sessions
```

---

## 2. Precise Lifecycle Intervention Mapping

Every AntiOS capability must justify its existence by anchoring to an exact lifecycle event. If an item does not participate in a native event, it is classified as **QUESTIONABLE / DEFERRED**:

| AntiOS Capability | Antigravity Event / Surface | Exact Lifecycle Intervention Point | Status & Role |
| :--- | :--- | :--- | :--- |
| **Boundary Guard** (`pre_tool_guard.py`) | `PreToolUse` hook | Before `write_to_file`, `replace_file_content`, and destructive `run_command` execute. Evaluates target path against protected zones. | **ESSENTIAL**: Physical fail-closed security. |
| **Stop Gate** (`stop_gate.py`) | `Stop` hook | When agent attempts to conclude task. Spawns independent test runner process; blocks exit if tests fail. | **ESSENTIAL**: Physical verification ratchet. |
| **Project Adapter** (`antios.config.json`) | Filesystem Read (`view_file`) | Consulted during Stage 2 (Locate) to resolve subsystem paths, entrypoints, and test runners in 0 search turns. | **ESSENTIAL**: Deterministic wayfinding. |
| **Operational Rules** (`AGENTS.md`) | System Prompt Injection | Read at Stage 1 (Understand). Enforces engineering discipline and maker-checker protocols. | **ESSENTIAL**: Behavioral foundation. |
| **Engineering Skills** (`.agents/skills/*`) | Progressive Disclosure | Activated on demand when complex debugging, engineering, or verification runbooks are needed. | **ESSENTIAL**: Procedural runbooks. |
| **Handoff Memory** (`handoff.md`) | File Read / Write | Read at Stage 1 of fresh sessions; updated at Stage 12 upon task completion. Eliminates amnesia. | **ESSENTIAL**: Session continuity. |
| **Dead-End Memory** (`dead-ends.md`) | File Read / Write | Consulted during Stage 4/9 (Reason/Diagnose) to prevent repeating falsified hypotheses. | **HIGH VALUE**: Prevents fix oscillation. |
| **Standalone Telemetry Emitter** | `PostToolUse` hook | Immediately after tool execution. Appends sanitized event JSON to local file or SQLite without blocking. | **VIABLE**: Only if zero-dependency. |
| **`.antios/*.json` Metadata Dumps** | Static disk files | Generated during adapt; never read by platform or model during live tasks. | **DEFERRED / EXCISION**: Dead weight. |
| **`framework/core/` (84 modules)** | Monolithic Python codebase | Never imported by target projects due to Runtime Closure Contract. | **REFACTOR TO CLI TOOLS**: Keep in AntiOS dev repo as CLI utilities; do not deploy to target projects. |
| **In-Hook Transcript Tailer** | `Stop` hook | Synchronous heavy parsing inside latency-sensitive hook. Fragile and prone to timeouts. | **ABANDONED**: Replace with decoupled CLI tailer or post-session ingestor. |

---

## 3. Redefining the Project Environment: Adaptation vs Installation

### The Paradigm Shift
- **Old Flawed Conception**: *"Install AntiOS into a project."* (Assumed AntiOS was an operating system or runtime daemon that gets installed alongside the code, requiring complex runtime infrastructure).
- **Discovered Reality**: *"Compile/adapt an Agent-Native Project Environment for Antigravity."* (AntiOS is a **compiler and specification** that transforms an ordinary repository into an environment optimized for Antigravity agents).

### What an Agent-Native Project Environment Contains:
1. **Identity & Wayfinding**: Compact `antios.config.json` defining monorepo subsystems, build manifests, entrypoints, and test commands.
2. **Behavioral Invariants**: Scoped `AGENTS.md` rules tailored to the repository's technology stack.
3. **Deterministic Guardrails**: `.agents/hooks.json` mapping `pre_tool_guard.py` (`PreToolUse`) and `stop_gate.py` (`Stop`).
4. **Targeted Capability Skills**: `.agents/skills/` containing localized runbooks (`antios-engineer`, `antios-debug`, `antios-verifier`).
5. **Living Engineering Memory**: Root-level `handoff.md` and `dead-ends.md` maintaining persistent state across sessions.

---

## 4. System A vs System B Epistemic Architecture

To ensure data integrity, zero vendor lock-in, and strict privacy, AntiOS enforces an absolute firewall between **System A** and **System B**:

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM A: PROJECT-NATIVE CONTROL PLANE (The Sovereign Repo) │
│ - Location: <project_root>/ (.agents/, antios.config.json)   │
│ - Contents: Subsystem maps, tests, rules, handoff.md        │
│ - Nature: Epistemic Ground Truth (Physical Disk Bytes)      │
│ - Dependency: 100% Zero external dependencies. Standard lib. │
│ - Portability: Operates anywhere without AntiOS framework.  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                       ONE-WAY SANITIZED
                       TELEMETRY STREAM
                               │
┌──────────────────────────────▼──────────────────────────────┐
│ SYSTEM B: CROSS-PROJECT EXPERIENCE STORE (Product Intel)    │
│ - Location: <central_data>/experience.db (Os-Collection)    │
│ - Contents: Cross-project tool friction, tokens, strategies  │
│ - Nature: Inert Observational Analytics                     │
│ - Privacy: Stripped of PII, secrets, code, and paths        │
│ - Rule: System A NEVER reads or depends on System B!        │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Separation Matrix:
- **Ownership**: System A is owned by the project repository and tracked in VCS. System B is machine-local and owned by the developer.
- **Dependency Invariant**: System A **MUST NEVER** require System B to execute. If `experience.db` is deleted, locked, or corrupted, engineering in System A proceeds with zero disruption.
- **Data Flow**: Strictly **One-Way (A $\to$ B)**. Experience data never automatically overrides or modifies System A codebase rules without explicit human curation.
- **Closure Guarantee**: Instance runtime scripts in System A contain zero imports from System B.

---

## 5. Failure Mode Analysis & Architectural Prevention

| Failure Mode | Root Cause | Architectural Prevention Mechanism |
| :--- | :--- | :--- |
| **1. Agent Ignores Skills** | LLM forgets to call skill; prompt lacks clear trigger. | High-quality, imperative skill descriptions in frontmatter; slash command alias (`/antios`). |
| **2. Agent Ignores Rules** | Model hallucinates past markdown constraints under pressure. | **Physical Interception**: Never rely on rules for safety. Back every critical constraint with a `PreToolUse` hook. |
| **3. Agent Never Reads Generated Docs** | Excessive documentation dumped in non-standard folders. | Eliminate dead `.antios/*.json` models. Place single, compact `antios.config.json` at root; reference it in `AGENTS.md`. |
| **4. Context Overload** | Injecting thousands of lines of documentation on turn 1. | **Progressive Disclosure**: Only catalogs injected initially; full text read only when activated. |
| **5. Redundant Project Scanning** | No file index in prompt; agent uses brute-force grep. | **Declarative Subsystem Manifests**: `antios.config.json` maps features to directories in 0 search turns. |
| **6. Stale Project Maps** | Code refactored but JSON manifests remain old. | **Physical Verification Check**: Stop Gate verifies that manifests referenced in config still exist on disk. |
| **7. Hooks Not Firing** | Wrong working directory (`cwd = .agents/`) or path mismatch. | Scripts compute paths relative to `__file__` using `normcase(abspath(...))`; robust cwd-agnostic resolution. |
| **8. Shell Bypass Vulnerability** | `PreToolUse` matcher only watches IDE edit tools. | Expand matcher or enforce security policies via native Antigravity permission grants. |
| **9. Telemetry Blackout** | Complex framework imports in target runtime violate closure. | **Zero-Dependency In-Process Emitter**: Plain Python append to local file or direct sqlite3 call with fallback. |
| **10. Verification Theater** | Agent claims tests pass without running them. | **Physical Stop Gate**: `stop_gate.py` runs tests independently; demands exit code 0. |
| **11. Mandatory Workflow Tax** | Forcing rigid multi-agent ceremonies on simple 1-line typo fixes. | **Adaptive Sizing**: Below complexity threshold, agent executes SOLO (0 subagents) with zero ceremony. |
| **12. Fighting Native Behavior** | Trying to build custom daemons or agent runtimes. | **Platform Alignment**: Build strictly on `.agents/skills/`, `.agents/hooks.json`, and `AGENTS.md`. |
