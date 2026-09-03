# AntiOS Responsibility Boundary Matrix (`ANTIOS_RESPONSIBILITY_BOUNDARY.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish an unambiguous, non-overlapping division of responsibilities across the Platform (Antigravity), the Engineering Governance Layer (AntiOS v1), and the Application Domain (StudyLab).

---

## 1. The Tripartite Governance Matrix

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RESPONSIBILITY BOUNDARIES                          │
├───────────────────────┬─────────────────────────┬───────────────────────────┤
│ ANTIGRAVITY (Platform)│ ANTI OS (Engineering)   │ STUDYLAB (Domain Truth)   │
├───────────────────────┼─────────────────────────┼───────────────────────────┤
│ • Subagent Runtime    │ • Project Engineering   │ • Application Behavior    │
│ • Tool Transport      │   Policy                │ • Domain Contracts        │
│ • Planning UI         │ • Protected Boundaries  │ • APKG Semantics          │
│ • Transcript Log      │ • Verification Policy   │ • Application Test Suites │
│ • Scheduling & Cron   │ • Task-State Model      │ • Compiler & Toolchain    │
│ • MCP Client Engine   │ • Skill Design          │ • Product Decisions       │
│ • Shell Execution     │ • Hook Policy           │ • Reviewer FSM            │
│                       │ • Maker-Checker Policy  │ • Double SQLite Storage   │
│                       │ • Recovery Protocol     │ • Pedagogical Invariants  │
│                       │ • Source-of-Truth Rules │                           │
└───────────────────────┴─────────────────────────┴───────────────────────────┘
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

### C. StudyLab Owns (Domain Truth & Application Logic)

StudyLab is the application under development. AntiOS does not absorb, re-implement, or dilute its domain semantics:

1. **Application Behavior & Features**:
   - User interface logic, flashcard rendering, review modes, deck management.
2. **Domain Contracts & Schemas**:
   - The canonical 20-field source question schema.
   - Mathematical and LaTeX formatting standards.
   - Telemetry firewall rules and double SQLite database schemas.
3. **APKG Packaging & Compilation**:
   - Artifact generation logic (`generate_apkg.py`).
   - SQLite generation and Anki package format serialization.
4. **Application Test Suites**:
   - The actual assertions, test suites, and fixtures in TypeScript (`ts/tests/`) and Rust (`rslib/`).
5. **Compiler & Toolchain Correctness**:
   - TypeScript compilation (`tsc`), bundling (`esbuild`/`vite`), Rust compilation (`cargo`).
6. **Product & Pedagogical Decisions**:
   - Curriculum design, learning science principles, spaced repetition algorithms.

---

## 3. Boundary Crossing Invariants

```text
Rule 1: AntiOS never implements domain validation.
        If an APKG or schema needs validation, invoke StudyLab's generate_apkg.py or tsc.

Rule 2: AntiOS never rebuilds platform orchestration.
        If a subagent needs to run, invoke Antigravity's invoke_subagent.

Rule 3: Antigravity never assumes domain safety.
        The platform allows any tool call unless AntiOS hooks intercept and block it.

Rule 4: StudyLab never implements agent governance.
        StudyLab code contains zero knowledge of prompts, skills, or agent personas.
```
