# AntiOS Adaptive Mission Orchestration Model (`docs/architecture/ORCHESTRATION_MODEL.md`)

**Date**: 2026-09-05  
**Status**: Authoritative Architectural Specification (Phases 49–54 Consolidated)  
**Governing Principle**:
> *"Maximize useful parallel progress, verification quality, and correctness per credit and token — never optimize for agent headcount.*  
> *The team must shrink as the problem narrows. After useful parallel work completes, collapse workforce aggressively to zero."*

---

## 1. System Overview

AntiOS Adaptive Mission Orchestration provides the execution brain for autonomous coding missions in Google Antigravity. It governs how missions are sized, how work is partitioned into bounded waves, how concurrency and launches are metered, and how independent verification is enforced.

AntiOS does **not** implement a custom agent runtime, daemon, broker, or external task scheduler. It operates as the deterministic control and governance plane over native Google Antigravity mechanisms:
- `invoke_subagent` for specialist and verifier dispatch
- `manage_subagents` for worker listing, inspection, and termination (`kill`)
- `define_subagent` for dynamic on-demand coordinator instantiation
- `Workspace='branch'` for isolated parallel workspace writes
- `<planning_mode>` for interactive user alignment and execution dispatch

---

## 2. The 7 Adaptive Workforce Sizing Modes

AntiOS categorizes all missions into one of seven adaptive workforce modes:

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                 TASK COMPLEXITY EVALUATION                  │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
         [ SOLO ]                [ FOCUSED ]                 [ SMALL ]
      0 subagents               1 specialist               2 specialists
   Direct parent work        Isolated bug/invest.       Paired workstreams
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
       [ PARALLEL ]               [ STAGED ]             [ HIERARCHICAL ]
    2–4 specialists           Multi-wave staged          1 Coordinator with
   Disjoint streams              refactoring             1–2 leaf children
            │                         │                         │
            └─────────────────────────┴─────────────────────────┘
                                      │
                                      ▼
                                   [ MAX ]
                          Constitutional Ceiling:
                          <= 10 Active Subagents
                          <= 20 Lifetime Launches
```

### Sizing Decision Matrix

| Mode | Minimum Delegation | Typical Workstreams | Write Policy | Verification Strategy |
| :--- | :---: | :--- | :--- | :--- |
| **SOLO** | 0 | 1 narrow stream (typo, doc, 1-file fix) | Single writer (Parent) | Solo sanity check + Stop Gate |
| **FOCUSED** | 1 | 1 difficult bug or deep research lane | Single writer (Specialist) | Maker-Checker (verifier subagent) |
| **SMALL** | 2 | 2 genuinely independent lanes | Disjoint or Single Writer | Independent verifier |
| **PARALLEL** | 2–4 | 3+ independent modules or domains | Disjoint (`Workspace='branch'`) | Verifier + Challenger |
| **STAGED** | 2–3 / wave | Large multi-phase migration | Staged write phases | Gate verification between waves |
| **HIERARCHICAL**| 1 coord + 1–2 children | Decomposable subsystem requiring local lead | Scoped child writes | Coordinator synthesis + Verifier |
| **MAX** | Bounded ceiling | Huge enterprise initiative | Strictly partitioned | Multi-stage Victory audit |

---

## 3. Constitutional Resource Ledger & Invariants

Every mission operates under a shared, tree-wide resource ledger (`MissionLedger`):

```text
-------------------------------------------------------------------
                       CONSTITUTIONAL LIMITS
-------------------------------------------------------------------
1. MAX ACTIVE SUBAGENTS PER WAVE   = 10
2. MAX TOTAL MISSION LAUNCHES      = 20
3. SHALLOW DEPTH LAW               = Depth <= 2 (Root=0 -> Child=1 -> Grandchild=2)
-------------------------------------------------------------------
```

### Tree-Aware Concurrency & Launch Accounting
1. **Global Shared Budget**: Root + Coordinators + Children share **one unified pool of 20 launches**. A Coordinator never acquires its own independent launch budget.
2. **Every Launch Consumes Budget**: Initial specialists, retries, replacement workers, verifiers, challengers, and child workers consume one launch slot each. Terminated or failed workers still consume their slot.
3. **Pre-Spawn Gate**: Before every spawn, the ledger verifies:
   $$\text{REMAINING\_BUDGET} > 0 \quad \text{and} \quad \text{ACTIVE\_TOTAL} < 10 \quad \text{and} \quad \text{DEPTH} \le 2$$
   If any condition is false, spawn is denied fail-closed.
4. **Epistemic Fail-Closed**: If state cannot be verified or context is truncated, assume zero remaining budget and take over directly in the calling session.

---

## 4. Dual Dispatch Gates

To eliminate premature or uncontrolled subagent spawning, AntiOS enforces **two non-bypassable dispatch gates**:

### Gate A: Pre-Planning Dispatch Gate
Evaluated immediately after user prompt intake, **before** substantial repository exploration:
- **Trigger A (Multiple domains)**: Task touches $\ge 3$ distinct subsystems $\rightarrow$ $\ge 2$ concurrent specialists.
- **Trigger B (Independent lanes)**: Task contains $\ge 2$ independent investigation tracks $\rightarrow$ $\ge 2$ concurrent specialists.
- **Trigger C (Large scope)**: Task touches $\ge 5$ files across $\ge 2$ modules $\rightarrow$ $\ge 1$ specialist ($\ge 2$ if independent).
- **Trigger D (Research + Impl)**: Task requires substantial investigation AND implementation $\rightarrow$ $\ge 1$ explorer/researcher.
- **Trigger E (High-Risk Investigation)**: Security or architecture spike $\rightarrow$ $\ge 1$ dedicated specialist.
- **Trigger F (Explicit Request)**: User explicitly requests delegation or parallel execution $\rightarrow$ mandatory delegation.

*If any trigger fires, solo reconnaissance by parent is forbidden; required specialists must be dispatched first.*

### Gate B: Execution Dispatch Gate
Evaluated after the implementation plan is approved by the user or authorized via auto-proceed, **before** the first code modification:
- Evaluates concrete implementation workstreams from approved plan.
- **1 workstream**: Controlled Single Writer (Parent or 1 Implementer).
- **2 independent streams**: Mandatory delegation to $\ge 2$ implementers (SOLO is strictly forbidden).
- **3+ independent streams**: PARALLEL or HIERARCHICAL delegation across disjoint file boundaries.
- **Tightly Coupled Override**: If changes share locks, types, or dense couplings, enforce Controlled Single Writer to prevent collision.

---

## 5. Wave Lifecycle & Mandatory Workforce Collapse

Missions execute in bounded waves with strict barrier synchronization:

```text
WAVE 1: RECONNAISSANCE
   │  (Explorers & Researchers gather facts)
   ▼
CONSOLIDATE & COLLAPSE (Active Workers -> 0)
   │
   ▼
WAVE 2: PLANNING / SYNTHESIS
   │  (Parent reconciles findings, authors implementation plan)
   ▼
[ GATE B: EXECUTION DISPATCH EVALUATION ]
   │
   ▼
WAVE 3: IMPLEMENTATION
   │  (Implementers write code to assigned disjoint files/workspaces)
   ▼
CONSOLIDATE & COLLAPSE (Active Workers -> 0)
   │
   ▼
WAVE 4: INDEPENDENT VERIFICATION
   │  (Fresh-context Checker/Verifier executes tests & audits diffs)
   ▼
CONSOLIDATE & COLLAPSE (Active Workers -> 0)
   │
   ▼
WAVE 5: DELIVERY & FINAL VERDICT
   │  (Stop Gate validates physical test exit code 0)
   ▼
TURN COMPLETE (Active Workforce == 0)
```

### The Collapse Invariant
$$\text{NEXT\_WAVE\_ALLOWED} \iff (\text{PREVIOUS\_WAVE\_STATE} == \text{COLLAPSED} \land \text{ACTIVE\_TOTAL} == 0)$$
New workers can be launched in the new wave, provided total mission launches remain $\le 20$ and active workers remain $\le 10$. Idle workers are never kept alive across wave barriers.

---

## 6. Hierarchical Delegation & Capacity Reservation

When a subproblem warrants internal decomposition, Root may designate an agent as a **Coordinator**:
1. **Pre-Allocation**: Root reserves a local child quota (`LOCAL_CHILD_BUDGET = N`, where $N \le 4$) from the unreserved global budget.
2. **Quota Enforcement**: The Coordinator may launch at most $N$ child subagents.
3. **No Independent Minting**: Coordinators cannot increase or bypass the global 20-launch ceiling.
4. **Quota Reversion**: When a Coordinator completes, all unused quota immediately reverts back to Root:
   $$\text{Unused} = \text{Reserved} - \text{Actually\_Spawned}$$
5. **Sibling Race Prevention**: Root partitions reserved capacity before dispatching sibling coordinators, guaranteeing global active workers remain $\le 10$ at all times.

---

## 7. Structured Evidence Handoff Protocol

Every specialist must return a standardized structured handoff before termination:

```text
### HANDOFF REPORT
- OBJECTIVE:           [Assigned mandate]
- OBSERVATIONS:        [Key factual findings with file paths and line numbers]
- LOGIC_CHAIN:         [Technical reasoning and causal analysis]
- EVIDENCE:            [Exact command outputs, diffs, line references, or test results]
- CAVEATS:             [Assumptions, risks, edge cases, or unverified items]
- CONCLUSION:          [Actionable deliverable or recommendation]
- VERIFICATION_METHOD: [Exact test command next owner can execute to verify]
- NEXT_OWNER:          [Recommended next role]
```

**Deterministic Validation**: Handoffs lacking concrete evidence (file paths, symbols, command outputs) or missing verification methods are rejected fail-closed.

---

## 8. Read-Parallel / Write-Controlled Policy

- **Parallel Reads**: Exploratory searches, greps, type analysis, and documentation reads may execute concurrently across multiple workers.
- **Controlled Writes**:
  - Multiple workers must **never** modify the same file concurrently.
  - Concurrent implementers must be assigned **disjoint file boundaries**.
  - When concurrent writing occurs, assign `Workspace='branch'` to isolate git worktrees; the parent reconciles diffs prior to verification.
  - If file boundaries overlap, the system falls back to **Controlled Single Writer**.

---

## 9. 12-Input Adaptive Workforce Sizer & Cost Reasoning Engine (Phase 84)

Rather than relying on ad-hoc heuristics, `AdaptiveWorkforcePlanner` deterministically evaluates **12 decision inputs**:
1. `task_class`: Complexity classification (`BUG`, `FEATURE`, `REFACTOR`, `DOCUMENTATION`, `INVESTIGATION`, etc.)
2. `risk_tier`: Security and blast radius (`LOW`, `MEDIUM`, `HIGH`)
3. `pre_planning_decision`: Gate A reconnaissance authorization
4. `execution_decision`: Gate B execution dispatch authorization
5. `write_policy`: File write safety policy (`READ_ONLY`, `CONTROLLED_SINGLE_WRITER`, `SAFELY_PARALLELIZABLE`, `DISJOINT_BRANCHES`)
6. `subsystem_count`: Number of decoupled subsystems involved
7. `file_count`: Number of concrete target files
8. `has_disjoint_boundaries`: Whether worker file boundaries are mutually disjoint
9. `remaining_mission_budget`: Global lifetime launches remaining ($\le 20$)
10. `historical_worker_success_rate`: Observed completion rate of worker roles
11. `estimated_token_cost_budget`: Mission token budget ceiling
12. `active_workers_in_wave`: Concurrency already allocated in active wave ($\le 10$)

### Token-Bounded Cost Reasoning Card
Every workforce plan emits a token-bounded `WorkforceCostReasoning` explanation card ($\le 12$ lines) justifying the sizing:
- **Why This Workforce**: Explicit justification for the chosen mode and worker count.
- **Why Not Fewer**: Marginal cost/risk of reducing worker count (e.g. latency vs serialization).
- **Why Not More**: Marginal coordination overhead and conflict risk of adding workers.

---

## 10. Teamwork-Grade Wave Lifecycle & Anti-Hydra Protection (Phase 85)

### Anti-Hydra Invariants
Every worker spawn requires a fully validated `WorkerMetadata` instance. The system enforces 4 deterministic anti-hydra gates:
1. **Duplicate Specialist Prevention**: Rejects spawning multiple active workers with the same role and goal in the same wave.
2. **Runaway Retry Loop Guard**: Enforces `max_retries_per_role = 2`. If a role accumulates $\ge 2$ failures, further spawns are blocked and escalated.
3. **Write Boundary Collision Check**: Rejects concurrent workers with intersecting write target sets unless safe branching is active.
4. **Shallow Depth Law Guard**: Strictly forbids leaf specialists at depth 2 from attempting delegation.

### Wave Persistence & Failure Recovery
- **Crash Recovery**: `WavePersistenceEngine` serializes active wave state and mission ledgers to `.antios/wave_state.json`. Uncompleted waves can be resumed without re-running earlier stages.
- **Deterministic Recovery Actions**: `FailureRecoveryEngine` categorizes worker terminations into 11 failure types (timeouts, syntax crashes, ungrounded handoffs, write collisions) and prescribes deterministic actions (`RETRY_WITH_CONTEXT`, `REPLACE_SPECIALIST`, `REDUCE_WORKFORCE`, `FAIL_CLOSED`).

---

## 11. 8-Tier Hybrid Capability Execution Matrix (Phase 86)

AntiOS resolves requested engineering capabilities through a strict 8-tier hierarchy:

```text
[Tier 1: Native Antigravity Built-in Tool] (view_file, write_to_file, grep_search, run_command)
       │
       ▼
[Tier 2: Project-Native Skill] (.agents/skills/antios-*, project skills)
       │
       ▼
[Tier 3: Project Tool / Script] (tests/run_all.py, pytest, npm test)
       │
       ▼
[Tier 4: AntiOS Core Runtime Service] (wayfinder, stop_gate, workforce_planner)
       │
       ▼
[Tier 5: Antigravity Built-in Specialist Agent] (research, flutter_a11y_agent)
       │
       ▼
[Tier 6: Standard CLI Execution] (git, python, npm, cargo, docker)
       │
       ▼
[Tier 7: User-Approved External Service] (cloud_storage, bigquery - requires explicit approval)
       │
       ▼
[Tier 8: Managed MCP Tool] (GitHub, Chrome DevTools, Playwright - highest barrier)
```

### Local Git CLI Strict Preference
Local Git CLI (Tier 6) is strictly preferred over GitHub MCP (Tier 8) for all local operations (`git status`, `git diff`, `git log`, `git commit`). Local CLI executes in $<50$ms, offline, with zero token cost. GitHub MCP is strictly forbidden for local repository inspection.

### 7-Field MCP Escalation Protocol
Managed MCP tools require a complete 7-field escalation audit report. Missing fields trigger immediate fail-closed rejection:
1. `capability_sought`: Specific operation sought.
2. `why_native_failed`: Why Tiers 1–6 cannot satisfy the requirement.
3. `least_privilege_scope`: Scoped tool permissions required.
4. `risk_assessment`: Security and remote latency risk profile.
5. `rollback_plan`: Exact remediation if the MCP call fails or disconnects.
6. `user_approval_required`: Boolean flag indicating if user consent is needed.
7. `audit_trail_entry`: Structured dictionary logging the escalation event.

