# AntiOS v1 Architecture Specification (`ANTIOS_V1_ARCHITECTURE.md`)

**Version**: 1.0.0-rc1  
**Date**: 2026-09-04  
**Status**: Canonical Architecture Specification  
**Governing Axiom**:
> *"If Antigravity already provides the mechanism $\to$ USE THE PLATFORM.*  
> *If the language/compiler/test framework provides verification $\to$ USE THE NATIVE TOOLCHAIN.*  
> *If StudyLab already owns a domain contract $\to$ DEFER TO STUDYLAB.*  
> *AntiOS owns: PROJECT POLICY, SAFETY BOUNDARIES, ENGINEERING WORKFLOW, VERIFICATION POLICY, TASK STATE, AGENT GOVERNANCE."*

---

## 1. System Mission & Core Purpose

**AntiOS** is a lean, deterministic project-governance framework designed to enable Google Antigravity and its autonomous AI agents to safely develop, modify, verify, document, and maintain software repositories over long-running sessions without human micromanagement.

### The Immediate Target vs Long-Term Reusability
- **Immediate Target**: StudyLab (a complex TypeScript/Svelte/Rust desktop application with strict pedagogical invariants, double SQLite persistence, and an upstream Anki core engine).
- **Architecture Philosophy**: AntiOS v1 is designed directly around StudyLab's empirical engineering reality, but is cleanly architected into **Domain-Agnostic Core Governance** and **StudyLab Domain Adapters**.
- **No Premature Generalization**: We do not build an abstract multi-repo plug-in engine or dynamic DSL. Reusability is achieved through structural modularity and clean interface boundaries.

---

## 2. The Three-Tier Architectural Model

Phase 10 forensic analysis disproved the speculative multi-layered architectures of early proposals. The empirical reality establishes a strict, three-tier separation of concerns:

```text
                     =========================================
                               TIER 1: ANTIGRAVITY
                              (Platform Mechanism)
                     =========================================
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  [TOOL HOOKS]                   [SUBAGENT RUNTIME]               [EXECUTION & MCP]
  - PreToolUse / Stop            - invoke_subagent                - run_command (Shell)
  - Stdio JSON-RPC IPC           - Isolated Context               - Native MCP Client
  - Process Interception         - Native Planning Mode           - transcript.jsonl
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                     =========================================
                                 TIER 2: AntiOS v1
                               (Project Governance)
                     =========================================
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[SAFETY BOUNDARIES]             [ENGINEERING WORKFLOW]           [VERIFICATION POLICY]
- Fail-Closed Hook Logic         - AGENTS.md (Constitution)       - Physical OS Test Runner
- Canonical Path Guards          - ACTIVE_CONTEXT.md (State)      - Working Tree Ratchet
  (.agents/ & rslib/)            - antios-engineer Skill          - Risk-Tiered Maker-Checker
- Shell Limitation Notice        - Non-Redundant RPAC             - Auto-Discovery (Vitest/Pytest)
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                     =========================================
                                TIER 3: STUDYLAB
                                  (Domain Truth)
                     =========================================
                                         │
  - Source → APKG Contract & Canonical Question Schema (20-field)
  - Double SQLite Architecture & Reviewer FSM Invariants
  - Upstream Anki Core (rslib/ - strictly immutable)
  - Native Application Compilers & Test Suites (tsc, vitest, pytest)
```

---

## 3. Tier Evaluation & Demarcation

### Tier 1: What Antigravity Owns (Platform Mechanisms)
1. **Subagent Execution**: Native creation, isolation, token budgeting, and termination of child agents (`invoke_subagent`, `manage_subagents`).
2. **Hook Transport**: Platform intercepts tool calls (`PreToolUse`) and task termination (`Stop`), marshaling JSON payloads over stdio to configured executables.
3. **Tool Execution**: Raw execution of shell commands (`run_command`), file modifications (`write_to_file`, `replace_file_content`), and MCP server RPC calls.
4. **Interactive Planning UI**: Rendering and capturing user approvals via `<planning_mode>` (`implementation_plan.md`, `walkthrough.md`).
5. **Session Persistence**: Chronological, immutable logging of all turns and tool calls in `transcript.jsonl`.
6. **Background Scheduling**: Timer events and recurring cron schedules (`schedule`).

> **Platform Boundary Limitation Law**:  
> *Antigravity hooks intercept IDE tool calls, not OS kernel filesystem syscalls. Any tool invocation passed to `run_command` (PowerShell, Bash, Python) executes directly in the ambient OS environment, completely bypassing `PreToolUse` file write hooks. AntiOS explicitly recognizes this as an architectural platform boundary and enforces defense-in-depth through Constitution directives, restricted shell policies, and Stop gate verification.*

### Tier 2: What AntiOS v1 Owns (Project Governance)
1. **Safety Boundaries**: Deterministic Python hook scripts implementing **Fail-Closed** security, canonical path resolution, ancestor isolation, and hook self-protection.
2. **Global Project Constitution**: The minimal, high-signal set of engineering rules (`AGENTS.md`) governing agent behavior, boundary respect, and context discipline.
3. **Active Task State**: A bounded, file-backed working set (`ACTIVE_CONTEXT.md`) maintaining focus, tracking subtasks, logging blockers, and preventing context amnesia.
4. **Engineering Skills**: Lean, discoverable Antigravity skills (`.agents/skills/antios-engineer/`) guiding the agent through non-native governance policies (Maker-Checker dispatch, ratchet compliance).
5. **Verification Policy**: The deterministic ratchet requiring verified OS process execution (exit code 0) against the final working tree before marking any task complete.
6. **Maker-Checker Protocol**: Policy defining when and how to spawn independent, fresh-context verifier subagents to eliminate LLM confirmation bias.

### Tier 3: What StudyLab Owns (Domain Truth)
1. **Domain Semantics**: Mathematical correctness, pedagogical rules, card formatting, and telemetry firewalls.
2. **Canonical Schemas**: The 20-field source question contract and package manifests.
3. **Application Toolchain**: Native compilation (`tsc`, `cargo`), package generation (`generate_apkg.py`), and test runners (`vitest`, `pytest`).
4. **Domain Invariants**: The double SQLite architecture and reviewer finite state machine (FSM).

---

## 4. Reusability Model: Core vs StudyLab Adapter

To achieve genuine reusability without premature generalization, AntiOS v1 separates its implementation into two logical layers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ANTIOS REUSABLE CORE (Generic)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Fail-Closed Hook Framework (Input parsing, JSON IPC, error handling)      │
│ 2. Self-Protection Guards (Protects .agents/, hooks.json, and hook scripts) │
│ 3. Working Tree Cleanliness & Ratchet Verification Protocol                 │
│ 4. Risk-Tiered Maker-Checker Delegation Logic                               │
│ 5. Bounded Memory Bank Convention (ACTIVE_CONTEXT.md & Constitution format) │
│ 6. Dynamic Test Runner Auto-Discovery (package.json, pyproject.toml)        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STUDYLAB DOMAIN ADAPTER (Project)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Upstream Immutability Boundary (rslib/ protection rules)                 │
│ 2. StudyLab Specific Test Commands (npm run vitest:once, yarn run ...)       │
│ 3. Source → APKG Contract Awareness (generate_apkg.py execution)            │
│ 4. High-Risk Classification for Reviewer FSM & Double SQLite modules        │
└─────────────────────────────────────────────────────────────────────────────┘
```

When porting AntiOS to another repository:
- The **Reusable Core** remains untouched.
- The **Domain Adapter** is configured with the project's forbidden paths, native test runners, and domain risk classifications.

---

## 5. End-to-End Task Lifecycle in AntiOS v1

```text
  1. INGESTION & ORIENTATION
     │ - Agent reads AGENTS.md (Constitution) and ACTIVE_CONTEXT.md (Working Set)
     │ - Ingests user request; identifies risk tier (Low, Medium, High)
     ▼
  2. RESEARCH & PLANNING (Platform Native)
     │ - Conducts codebase reconnaissance using read-only tools
     │ - Generates implementation_plan.md via native <planning_mode>
     │ - If required, requests and receives user approval
     ▼
  3. EXECUTION & SAFETY ENFORCEMENT
     │ - Agent applies code and documentation edits (Same Change Set)
     │ - PreToolUse Hook (pre_tool_guard.py) validates every tool write:
     │     - Denies writes to .agents/ (Self-Protection)
     │     - Denies writes to rslib/ (Upstream Immutability)
     │     - Normalizes paths (resolves 8.3 aliases, directory traversal)
     │     - Fails closed on any error
     ▼
  4. INDEPENDENT VERIFICATION (Maker-Checker)
     │ - For High-Risk tasks (or complex Medium-Risk):
     │     - Spawns fresh verifier subagent via invoke_subagent(TypeName='self')
     │     - Checker verifies acceptance criteria and runs native test suites
     ▼
  5. TASK CONSOLIDATION & STOP GATE
     │ - Agent attempts to finish task
     │ - Stop Hook (stop_gate.py) intercepts termination:
     │     - Discovers native test suite (package.json / pyproject.toml)
     │     - Executes physical test process with strict timeout (60s)
     │     - Verifies working tree status (cleanliness / final state)
     │     - If tests fail or crash: returns 'decision: continue' with exact stderr
     │     - If tests pass (exit 0): returns 'decision: allow'
     ▼
  6. STATE SYNCHRONIZATION
       - Agent updates ACTIVE_CONTEXT.md (records progress, clears blockers)
       - Authors walkthrough.md artifact
       - Turn concludes successfully
```

---

## 6. Architectural Guarantees & Non-Guarantees

### What AntiOS v1 Strictly Guarantees
1. **Zero Silent Tool Modifications to Protected Directories**: IDE tool calls targeting `rslib/` or `.agents/` are deterministically blocked by OS-level Python processes.
2. **Zero False Task Completions via Conversational Hallucination**: An agent cannot declare victory by claiming "all tests pass" in chat; task completion requires a physical OS exit code of 0.
3. **Zero Test Forgery via Custom Scripts**: Removal of `verify_task.py` guarantees tests execute strictly through registered project configurations.
4. **Context Recovery Across Resets**: Resuming agents inherit bounded, accurate project state from version-controlled markdown files.

### What AntiOS v1 Does NOT Guarantee (Platform Boundary Limitations)
1. **Raw Shell Immutability**: If an agent executes raw destructive commands via `run_command` (e.g. `rm -rf rslib`), tool hooks cannot intercept the shell's sub-processes.
2. **Semantic Documentation Drift**: AntiOS verifies that code compiles and passes tests; verifying whether markdown prose accurately captures subtle algorithmic changes requires LLM / human review.
3. **Environment Self-Healing**: If an external binary (e.g. Node, Python) is corrupted or missing from the host machine, AntiOS halts execution safely but cannot autonomously rebuild the OS environment.
