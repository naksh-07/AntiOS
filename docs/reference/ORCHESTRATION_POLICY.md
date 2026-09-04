# AntiOS Orchestration Policy & Invariants (`docs/reference/ORCHESTRATION_POLICY.md`)

**Date**: 2026-09-05  
**Status**: Authoritative Policy Specification (Phases 49–54 Consolidated)  
**Authority**: Master Engineering Invariant (Precedence Rank 4)

---

## 1. Constitutional Orchestration Invariants

Every agent and subagent operating under AntiOS governance is bound by five constitutional orchestration invariants:

1. **Active Wave Concurrency Ceiling**:
   $$\text{ACTIVE\_SUBAGENTS}_{\text{wave}} \le 10$$
   Globally across all direct children, coordinators, and descendant workers active in a wave.
2. **Mission Launch Budget Ceiling**:
   $$\text{TOTAL\_LAUNCHES}_{\text{mission}} \le 20$$
   Across the entire mission lifecycle. Every invocation of `invoke_subagent` consumes 1 launch slot permanently, including failed workers, retries, and verifiers.
3. **Shallow Depth Law**:
   $$\text{DELEGATION\_DEPTH} \le 2 \quad (\text{Root}=0 \rightarrow \text{Coordinator/Specialist}=1 \rightarrow \text{Child/Verifier}=2)$$
   Subagents at depth 2 are strictly forbidden from spawning children. Recursive swarms fail closed.
4. **Mandatory Wave Collapse**:
   $$\text{NEXT\_WAVE\_ALLOWED} \iff (\text{PREVIOUS\_WAVE\_STATE} == \text{COLLAPSED} \land \text{ACTIVE\_TOTAL} == 0)$$
   A new wave cannot begin until all workers from the previous wave are terminated and state is consolidated.
5. **Controlled Write Safety**:
   Concurrent writes to the same file are strictly prohibited. Multi-worker writing requires disjoint file boundaries and isolated worktree branches (`Workspace='branch'`).

---

## 2. Workforce Sizing & No-Solo Justification

AntiOS defaults to **SOLO** (0 subagents) for narrow, focused tasks to prevent token and credit waste.

### When SOLO is Permitted
SOLO execution is authorized **only** when all of the following conditions hold:
- Task touches $< 3$ domains or subsystems.
- Task contains only 1 execution track.
- File scope touches $< 5$ files or resides within 1 module.
- No user request for parallel/teamwork execution exists.
- Task is not a high-risk security or core persistence modification.

### When Delegation is Mandatory
If **any** of the following triggers fire, SOLO is strictly prohibited:
- **3+ domains** touched $\rightarrow \ge 2$ specialists.
- **2+ independent workstreams** in approved plan $\rightarrow \ge 2$ implementers.
- **5+ files across 2+ modules** $\rightarrow \ge 1$ specialist.
- **Substantial research + implementation** $\rightarrow \ge 1$ explorer before planning.
- **High-risk modifications** $\rightarrow$ mandatory independent verifier.

---

## 3. Coordinator Allocation & Reservation Protocol

When Root creates a Coordinator subagent:
1. **Pre-Allocation**: Root reserves $N$ launches ($1 \le N \le 4$) from the unreserved mission budget.
2. **Quota Tracking**: Every child spawned by the Coordinator decrements its local quota and the global ledger.
3. **No Independent Minting**: A Coordinator cannot mint, borrow, or exceed its assigned quota.
4. **Quota Reversion**: Upon Coordinator termination, all unused quota reverts back to Root:
   $$\text{Unused\_Quota} = \text{Reserved\_Quota} - \text{Actually\_Spawned}$$

---

## 4. Write Safety & Workspace Isolation Rules

```text
┌───────────────────────────┬─────────────────────────────────────────────────────────┐
│ WRITE CONDITION           │ GOVERNING POLICY                                        │
├───────────────────────────┼─────────────────────────────────────────────────────────┤
│ Read-Only Investigation   │ Unrestricted parallel reads across all specialists      │
├───────────────────────────┼─────────────────────────────────────────────────────────┤
│ Coupled / Single File     │ Controlled Single Writer (Parent or dedicated worker)   │
├───────────────────────────┼─────────────────────────────────────────────────────────┤
│ Disjoint Files / Modules  │ Parallel workers authorized with Workspace='branch'     │
├───────────────────────────┼─────────────────────────────────────────────────────────┤
│ Overlapping File Targets  │ Strictly prohibited; fallback to Controlled Single Writer│
└───────────────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 5. Failure Recovery & Escalation State Machine

When a worker stalls, encounters an error, or fails verification:

```text
1. RETRY    ──> Nudge worker with specific corrective prompt (Max 1 retry per worker)
2. REASSIGN ──> Reassign task to an existing active/idle capable worker
3. REPLACE  ──> Spawn replacement worker (consumes 1 global launch slot)
4. TAKEOVER ──> Calling orchestrator/coordinator executes task directly
5. BLOCKED  ──> Report blocker to user with concrete partial evidence
```

A worker is classified as **stalled** if it repeats the identical failing command $\ge 3$ times with identical error output.
