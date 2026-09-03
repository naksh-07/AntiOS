# AntiOS Responsibility Boundary Matrix (`ANTIOS_RESPONSIBILITY_BOUNDARY.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish an unambiguous, non-overlapping division of responsibilities across the Platform (Antigravity), the Engineering Governance Layer (AntiOS v1), and the Application Domain (StudyLab).

---

## 1. The Tripartite Governance Matrix

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 RESPONSIBILITY BOUNDARIES                                 │
├───────────────────────┬─────────────────────────┬─────────────────────────┬───────────────┤
│ ANTIGRAVITY (Platform)│ ANTI OS (Core Governed) │ PROJECT ADAPTER (Config)│ TARGET PROJECT│
├───────────────────────┼─────────────────────────┼─────────────────────────┼───────────────┤
│ • Subagent Runtime    │ • Security Guards       │ • Manifest Fingerprint  │ • Domain Truth│
│ • Tool Transport      │ • Stop Gate Ratchet     │ • Scoped Test Runners   │ • Source Code │
│ • Planning UI         │ • Task State Machine    │ • Protected Zones       │ • Native Tests│
│ • Transcript Log      │ • Maker-Checker Policy  │ • Dynamic Commands      │ • Build Steps │
│ • Scheduling & Cron   │ • Memory Distillation   │ • Member Topology       │ • Schemas     │
│ • MCP Client Engine   │ • Telemetry Aggregator  │ • Tool CWD Bindings     │ • App Logic   │
│ • Shell Execution     │ • Self-Protection       │ • Zero Core Mutations   │ • Products    │
└───────────────────────┴─────────────────────────┴─────────────────────────┴───────────────┘
```

---

## 2. Detailed Dimension Breakdown

### A. Antigravity Owns (The Execution Platform)

Antigravity is the host engine and foundation. AntiOS never duplicates these capabilities:

1. **Subagent Runtime Lifecycle**:
   - Spawning subagents via `invoke_subagent`.
   - Managing subagent processes, checking state, and killing tasks via `manage_subagents`.
   - Segregating context windows across agents so children do not inherit polluted parent contexts.
2. **Tool Transport & Interception**:
   - Marshaling arguments to tools (`write_to_file`, `replace_file_content`, `run_command`).
   - Invoking configured hooks before tool execution (`PreToolUse`) and upon turn completion (`Stop`).
   - Piping structured JSON payloads via `sys.stdin` and interpreting JSON decisions via `sys.stdout`.
3. **Interactive Planning Mode**:
   - Rendering interactive plan artifacts (`implementation_plan.md`) and diff walkthroughs (`walkthrough.md`).
   - Rendering interactive user-approval prompts (`Proceed` button) and modal UI dialogs (`ask_question`).
4. **Transcript Logging**:
   - Capturing complete, immutable, chronological JSONL records (`transcript.jsonl`, `transcript_full.jsonl`).
   - Maintaining conversation history keyed by Conversation ID.
5. **Background Scheduling**:
   - Managing one-shot timers and recurring cron jobs (`schedule`).
   - Reactive wakeups when subagent or task messages arrive.
6. **MCP Client Transport**:
   - Stdio and SSE client transports, JSON-RPC serialization, and tool registry management.
7. **Shell Execution**:
   - Spawning terminal sessions via PowerShell/Bash for `run_command`.

---

### B. AntiOS Owns (Project Engineering Governance)

AntiOS is the operating layer within the repository that constrains, directs, and verifies agent actions:

1. **Project Engineering Policy**:
   - Enforcing that code and documentation changes are delivered in the **Same Change Set**.
   - Directing agents toward safe working trees and branches.
2. **Protected Boundaries & Immutability**:
   - Enforcing strict immutability of upstream core components (`rslib/`).
   - Enforcing self-protection of AntiOS configurations (`.agents/hooks.json`) and security scripts.
   - Providing canonical path resolution to defeat traversal and aliasing attacks.
3. **Verification Policy & Test Ratchet**:
   - Demanding physical OS process execution (exit code 0) before any task is permitted to terminate.
   - Dynamic discovery of native project test suites (`package.json`, `pyproject.toml`).
   - Rejecting conversational self-certification ("looks good to me") and insecure ad-hoc test scripts.
4. **Task-State Conventions**:
   - Standardizing `docs/ACTIVE_CONTEXT.md` with strict line limits ($\le 60$ lines) and structured sections (Objective, Active Tasks, Blockers, Dead Ends).
   - Preventing state amnesia across session context wipes.
5. **Skill Design & Progressive Disclosure**:
   - Authoring discoverable, token-efficient skills at `.agents/skills/` that introduce non-native project policies without duplicating native planning mode.
6. **Hook Policy**:
   - Implementing **Fail-Closed** security logic across all hook scripts.
   - Authoring actionable denial messages that explain why an action was blocked and provide immediate, productive recovery paths.
7. **Maker-Checker Policy**:
   - Defining risk tiers (Low, Medium, High) to balance verification rigor against token/latency overhead.
   - Formulating verifier subagent prompt templates and acceptance criteria.
8. **Recovery Protocol**:
   - Standardizing escalation procedures when test runners fail, boundaries are hit, or tools are missing.
9. **Source-of-Truth Governance**:
   - Maintaining the strict hierarchy of authority so that no architectural fact has competing canonical sources.

---

### C. Target Project Owns (Domain Truth & Application Logic)

Target projects (e.g. StudyLab, Pallets/Click) define domain truth. AntiOS does not absorb, re-implement, or dilute domain semantics:

1. **Application Behavior & Features**:
   - User-facing business logic, APIs, schemas, and UI components.
2. **Domain Contracts & Schemas**:
   - Application data contracts, serialization models, and database migrations.
3. **Packaging & Distribution**:
   - Artifact compilation, package bundling, wheel/crate generation, and release pipelines.
4. **Application Test Suites**:
   - Unit tests, integration tests, fuzzers, and end-to-end assertions in native frameworks (`pytest`, `vitest`, `cargo test`).
5. **Compiler & Toolchain Correctness**:
   - Compiler configuration (`tsconfig.json`, `Cargo.toml`, `pyproject.toml`).
6. **Product Decisions**:
   - Functional requirements, roadmap priorities, and architecture trade-offs.

---

## 3. Boundary Crossing Invariants

```text
Rule 1: AntiOS Core never implements domain validation.
        If a schema or build artifact needs validation, AntiOS invokes the project's native toolchain.

Rule 2: AntiOS Core never rebuilds platform orchestration.
        If a subagent needs to run, AntiOS invokes Antigravity's invoke_subagent.

Rule 3: Antigravity never assumes domain safety.
        The platform allows any tool call unless AntiOS hooks intercept and block it.

Rule 4: Target Projects never implement agent governance.
        Target codebase source files contain zero knowledge of prompts, skills, or agent personas.
```
