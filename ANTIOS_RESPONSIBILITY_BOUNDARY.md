# AntiOS Responsibility Boundary Matrix (`ANTIOS_RESPONSIBILITY_BOUNDARY.md`)

**Date**: 2026-09-04  
**Status**: Canonical Responsibility Matrix (Universal 4-Tier Model)  
**Objective**: Establish an unambiguous, non-overlapping division of responsibilities across the Platform (Antigravity), the Engineering Governance Layer (AntiOS Core), the Project Adapter, and the Target Project.

---

## 1. The 4-Tier Governance Matrix

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
1. **Subagent Runtime Lifecycle**: Spawning (`invoke_subagent`), lifecycle inspection, and termination (`manage_subagents`).
2. **Tool Transport & Interception**: Marshaling arguments to tools, invoking hooks (`PreToolUse`, `Stop`) over stdio JSON IPC.
3. **Interactive Planning Mode**: Rendering plan artifacts (`implementation_plan.md`) and walkthroughs (`walkthrough.md`).
4. **Transcript Logging**: Capturing chronological JSONL records (`transcript.jsonl`, `transcript_full.jsonl`).
5. **Background Scheduling**: One-shot timers, crons, and reactive wakeups (`schedule`).
6. **MCP Client Transport**: Connecting to external stdio/SSE MCP servers.
7. **Shell Execution**: Spawning terminal sessions for `run_command`.

### B. AntiOS Core Owns (Universal Project Governance)
1. **Protected Boundaries & Immutability**: Enforcing fail-closed protection on `.agents/`, `framework/`, `antios.config.json`, and configured protected zones.
2. **Verification Policy & Test Ratchet**: Demanding physical OS process exit code 0 on native test runners before completion.
3. **Task-State Conventions**: Standardizing `docs/ACTIVE_CONTEXT.md` (<= 60 lines) to prevent state amnesia.
4. **Engineering Skills & Workflows**: Providing discoverable skills at `.agents/skills/` without duplicating native planning mode.
5. **Wayfinding & Knowledge**: Providing deterministic component lookup and L0-L5 progressive context disclosure.
6. **Capability & Agent Routing**: Signal-based matching of tasks to capabilities and least-privilege agent roles.
7. **Tool Preference Governance**: Enforcing 6-tier preference (`Native > Script > Project > External > MCP > Rejected`).

### C. Project Adapter Owns (Project-Specific Declarations)
1. **Concrete Protected Paths**: List of repository-specific immutable paths (`protected_domain_paths`).
2. **Test Runner Bindings**: Exact commands for running unit, integration, and e2e tests (`test_runners`).
3. **Linter & Typechecker Bindings**: Commands for project linters and type checkers.
4. **Monorepo Member Topology**: Package boundaries and workspace relationships.
5. **Agent Topology Customization**: Declaring project-specific specialist roles.

### D. Target Project Owns (Application Reality)
1. **Domain Truth & Schemas**: Business logic, database tables, and API contracts.
2. **Source Code**: All application implementation files.
3. **Native Test Suites**: The physical unit, integration, and e2e test implementations.
4. **Build & Release Pipelines**: Packaging scripts and production deployment steps.
