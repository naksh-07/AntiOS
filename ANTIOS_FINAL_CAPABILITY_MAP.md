# AntiOS Final Capability Map (`ANTIOS_FINAL_CAPABILITY_MAP.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Objective**: Demarcate architectural responsibilities across the platform, project framework, hybrid interfaces, and identify components that are unnecessary bloat.  
**Classification Categories**: `PLATFORM` | `PROJECT` | `HYBRID` | `UNNECESSARY` | `UNKNOWN`

---

## 1. Architectural Capability Taxonomy Map

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CAPABILITY TAXONOMY                             │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ PLATFORM          │ Mechanism provided natively by Antigravity engine       │
│ PROJECT           │ Policy, rules, and scripts owned strictly by AntiOS     │
│ HYBRID            │ Platform mechanism configured by Project policy         │
│ UNNECESSARY       │ Redundant abstractions, disproved ideas, or framework   │
│                   │ bloat that must be pruned                               │
│ UNKNOWN           │ Open research frontiers requiring further calibration   │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Capability Classification Matrix

| Capability / Mechanism | Classification | Ownership / Location | Rationale & Architectural Demarcation |
| :--- | :---: | :--- | :--- |
| **Subagent Runtime Lifecycle** | **PLATFORM** | Antigravity Engine (`invoke_subagent`, `manage_subagents`) | Antigravity natively creates, isolates, monitors, and terminates subagents with segregated context windows. AntiOS must never build custom agent daemons. |
| **Tool Interception Engine** | **PLATFORM** | Antigravity Engine (`PreToolUse`, `Stop`) | Platform engine intercepts tool calls and completion events, dispatching configured external scripts via JSON IPC. |
| **Immutable Audit Logging** | **PLATFORM** | Antigravity Engine (`transcript.jsonl`) | JSONL transcript logging is natively persistent, chronological, and tamper-proof. AntiOS should not maintain custom execution journals. |
| **Background Scheduling & Daemons** | **PLATFORM** | Antigravity Engine (`schedule`) | One-shot timers and recurring cron monitoring are platform primitives. |
| **Interactive Planning Mode** | **PLATFORM** | Antigravity Engine (`<planning_mode>`) | `implementation_plan.md` and user approval gates are built into the platform UI. |
| **Shell Command Execution** | **PLATFORM** | Antigravity Engine (`run_command`) | Shell access is an execution mechanism provided by the platform. Bypassing tool hooks in the shell is an inherent platform boundary limitation. |
| **MCP Client Transport** | **PLATFORM** | Antigravity Engine | Transport, protocol framing, and tool registration are native to Antigravity. |
| **Upstream Domain Boundary Guard** | **PROJECT** | `framework/scripts/hooks/pre_tool_guard.py` | Specific policy forbidding writes to `rslib/` (Anki core) is unique to the StudyLab project. |
| **Stop Gate Test Verification** | **PROJECT** | `framework/scripts/hooks/stop_gate.py` | Enforcing native test passage (`vitest:once`, `pytest`) before task completion is project policy. |
| **Project Global Constitution** | **PROJECT** | `docs/AGENTS.md` | Defining the 6 core engineering directives for agents in StudyLab is project-specific. |
| **Bounded Memory Bank** | **PROJECT** | `docs/ACTIVE_CONTEXT.md` | File-backed working set tracking active workstreams and task progress belongs in project repo. |
| **Task Lifecycle Workflow (RPAC)** | **PROJECT** | `.agents/skills/studylab-task-runner` | Codifying Refine, Plan, Act, Consolidate is project engineering process. |
| **Hook-Based Safety Gating** | **HYBRID** | Platform Hook Runner + AntiOS Python Hook Scripts | Platform provides the interception event and JSON transport; AntiOS provides the validation logic and denial reasons. |
| **Maker-Checker Verification** | **HYBRID** | Platform Subagent Runtime + AntiOS RPAC Verification Protocol | Platform provides isolated subagent execution; AntiOS provides the checker prompt discipline and Stop gate backstop. |
| **Error Recovery Lifecycle** | **HYBRID** | Platform Message Delivery + AntiOS Denial Guidance | Platform delivers hook outputs to the agent; AntiOS craft rejection messages containing actionable redirection guidance. |
| **Same Change Set Enforcement** | **HYBRID** | Platform Stop Hook + AntiOS Git Diff Inspection Script | Platform invokes Stop; AntiOS validates that docs and code are staged together before permitting completion. |
| **Custom Schema Validators** | **UNNECESSARY** | Formerly proposed AntiOS Python validators | **DISPROVED (Phase 8)**. Validation of domain artifacts belongs natively to StudyLab's compiler toolchain (`generate_apkg.py`, `tsc`). |
| **External GitHub MCP Server** | **UNNECESSARY** | `github-mcp-server` | **REDUNDANT (Phase 8)**. Local `git` CLI via `run_command` is strictly faster, token-free, offline, and supports local sandboxes. |
| **StudySourceCore MCP Integration** | **UNNECESSARY** | `studysource-core` | **DISPROVED & OUT OF SCOPE**. Domain contracts reside in StudyLab. StudySourceCore is completely out of scope. |
| **Cryptographic Receipts / Hashes** | **UNNECESSARY** | `evidence/` directory | **REJECTED (Phase 8)**. File hashes prove state changes, not functional or pedagogical correctness. Static receipts expire upon subsequent code changes. |
| **AST / Dependency Graph Parsers** | **UNNECESSARY** | Proposed AntiOS AST analyzer | **REDUNDANT**. TypeScript compiler (`tsc`) and Vitest native module graphs are universally superior to custom regex/AST parsers. |
| **`verify_task.py` Fallback** | **UNNECESSARY** | `stop_gate.py:58-69` | **DANGEROUS / VULNERABILITY**. Primary vector for test forgery (`sys.exit(0)`). Must be pruned in favor of native test runners. |
| **Large Hierarchical Agent Swarms** | **UNNECESSARY** | Multi-agent trees (>3 agents) | **OVERHEAD (Phase 6/7)**. Massive agent swarms add coordination latency and token waste without improving quality on bounded software tasks. |
| **Maker-Checker Tuning on Trivial Tasks** | **UNKNOWN** | AntiOS RPAC Policy | Latency and token trade-off of dispatching a fresh verifier for 1-line typo fixes vs risk reduction. |
| **Autonomous Environment Recovery** | **UNKNOWN** | AntiOS Hook Exception Protocol | How an agent can autonomously recover from broken ambient runtime binaries (missing Node/Python) without human intervention. |

---

## 3. The Demarcation Rule of AntiOS

```text
       ┌────────────────────────────────────────────────────────┐
       │                   ANTIOS DESIGN LAW                    │
       ├────────────────────────────────────────────────────────┤
       │ 1. If Antigravity provides the mechanism:              │
       │    DO NOT REBUILD IT. USE PLATFORM PRIMITIVES.         │
       │                                                        │
       │ 2. If the language/compiler provides the toolchain:    │
       │    DO NOT REBUILD IT. RELY ON TSC / VITEST / PYTEST.   │
       │                                                        │
       │ 3. If StudyLab owns the contract:                      │
       │    DO NOT DUPLICATE IT. DEFER TO STUDYLAB NATIVE CODE. │
       │                                                        │
       │ 4. What remains is the sole legitimate scope of AntiOS:│
       │    PROJECT POLICY, HOOK SCRIPTS, CONSTITUTION & STATE. │
       └────────────────────────────────────────────────────────┘
```
