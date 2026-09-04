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
