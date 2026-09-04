# AntiOS 2.0 Project Learning & Safe Intelligence Evolution Architecture (`docs/architecture/PROJECT_LEARNING.md`)

**Date**: 2026-09-05  
**Status**: Canonical Architecture Specification (AntiOS 2.0 Foundation)  
**Scope**: Epistemic Segregation, Observation Capture, Evidence Promotion, Safe Evolution & Knowledge Decay  

---

## 1. Executive Summary & Core Principle

In AntiOS 2.0, learning across development sessions and autonomous agent missions is governed by one foundational law:

> **"Learning is evidence accumulation, not memory mutation."**

Autonomous agents must never treat an agent's self-generated belief, verbal claim, or raw LLM inference as permanent ground truth. Unconstrained self-reflection leads directly to hallucination feedback loops, prompt injection vulnerability, and silent corruption of repository code.

AntiOS 2.0 introduces the **Deterministic Project Learning Engine** (`framework/core/learning.py`), establishing a closed, scientific evidence lifecycle where:
1. Observations are captured deterministically from physical witnesses (test runs, gate verifications, user corrections).
2. Knowledge is stratified across four strict **Epistemic Sources**.
3. Lessons require empirical, reproducible evidence to advance through a four-stage **Evidence Promotion Ladder**.
4. The system **never mutates skills or codebase in-place**; evolution is mediated exclusively through human-reviewable **Evolution Proposals**.
5. Knowledge decays through an explicit lifecycle (`ACTIVE` -> `STALE` -> `SUPERSEDED` -> `INVALIDATED` -> `RETIRED`) when project reality drifts, while preserving permanent historical provenance.
6. A non-bypassable **Learning Safety Gate** enforces 10 safety invariants, defending against prompt injection, privilege escalation, and recursive loops.

---

## 2. Epistemic Segregation & Observation Capture

### 2.1 The Epistemic Source Hierarchy
Every observation captured by AntiOS must explicitly declare its source:

| Epistemic Source | Weight | Trust Level | Description | Promotion Authority |
| :--- | :---: | :---: | :--- | :--- |
| `OBSERVED_FACT` | **1.0** | High | Physical witness evidence: exit codes, test outputs, compiler errors, file diffs. | Can validate lessons with multi-task recurrence or verifier pass. |
| `USER_ASSERTION` | **0.9** | High | Explicit human corrections, feedback, or direct architectural instructions. | Can validate lessons directly. |
| `DERIVED_INFERENCE` | **0.7** | Medium | Deductive conclusions verified against static code, syntax trees, or schemas. | Contributes to candidate evidence; requires corroboration. |
| `AGENT_INTERPRETATION` | **0.3** | Low | Unverified agent hypothesis, LLM rationale, or speculative explanation. | **Strictly prohibited** from promoting candidate lessons to `VALIDATED`. |

### 2.2 Observation Types & Structural Deduplication
Observations are classified into 13 canonical types:
- `TEST_FAILURE`, `TEST_FIX`, `COMPILER_ERROR`, `LINTER_ERROR`, `STOP_GATE_REJECTION`, `VERIFIER_REJECTION`, `USER_CORRECTION`, `TOOL_FAILURE`, `PERFORMANCE_REGRESSION`, `DEPENDENCY_CONFLICT`, `ENVIRONMENT_ANOMALY`, `REFACTOR_INSIGHT`, `SUCCESSFUL_WORKFLOW`.

Each observation generates a normalized, deterministic structural signature:
```text
sig = sha256(f"{obs_type}:{target_path}:{normalized_pattern}")[:16]
```
Duplicate observations with identical signatures do not duplicate entries; instead, they increment recurrence counters, update timestamps, and record distinct task IDs.

### 2.3 Strict Storage Bounds
To prevent uncontrolled state bloat and denial-of-service via token consumption, `ObservationStore` enforces hard caps:
- Store Capacity: $\le 100$ total observations
- Disk Footprint: $\le 200\text{ KB}$ serialized JSON
- Observation Title: $\le 120$ characters
- Observation Content: $\le 1,000$ characters
- Related Files: $\le 10$ paths per observation

When bounds are exceeded, the oldest, non-promoted observations are safely pruned using FIFO replacement.

---

## 3. Causal Distillation & Evidence Promotion Lifecycle

### 3.1 Causal Chain Distillation
The `LessonDistiller` correlates temporal observation streams to distill causal sequences:
- `TEST_FAILURE` followed by `TEST_FIX` on the same file/subsystem produces a `CandidateLesson` capturing what broke, why it broke, and the verified fix.
- `STOP_GATE_REJECTION` or `VERIFIER_REJECTION` produces boundary and contract awareness lessons.
- `USER_CORRECTION` produces prioritized operational lessons.

### 3.2 The Evidence Promotion Ladder
Lessons progress through four distinct states:

```text
┌──────────────┐     Corroborated     ┌──────────────┐
│   OBSERVED   │ ───────────────────> │  CANDIDATE   │
└──────────────┘                      └──────────────┘
                                             │
                       Independent Verifier  │ Multi-Task Recurrence
                       PASS or User Assert   │ (Tasks >= 2, Weight >= 1.5)
                                             ▼
                                      ┌──────────────┐
                                      │  VALIDATED   │
                                      └──────────────┘
                                             │
                                             │ Broad Recurrence (Tasks >= 3)
                                             │ & Cross-Subsystem Verification
                                             ▼
                                      ┌──────────────┐
                                      │   DURABLE    │
                                      └──────────────┘
```

1. **`OBSERVED`**: Initial raw observation recorded with timestamp and task context.
2. **`CANDIDATE`**: Correlated causal pattern distilled into a structured hypothesis with explicit evidence IDs.
3. **`VALIDATED`**: Proven lesson confirmed either by:
   - Independent Verifier `PASS` verdict, OR
   - Explicit human `USER_ASSERTION`, OR
   - Multi-task recurrence across $\ge 2$ distinct tasks with aggregate epistemic weight $\ge 1.5$.
4. **`DURABLE`**: Permanent framework memory confirmed across $\ge 3$ distinct tasks and enduring across project sessions.

**The Golden Anti-Hallucination Rule**: A candidate lesson supported solely by `AGENT_INTERPRETATION` evidence will **never** advance to `VALIDATED`, regardless of how many times the agent asserts it.

---

## 4. Safe Evolution Proposals (No Silent Mutation)

AntiOS strictly prohibits autonomous agents from silently rewriting skills, specialists, or source code in the background. Instead, verified lessons generate structured **Evolution Proposals** (`.antios/learning_proposals.json`).

### 4.1 Proposal Lifecycle
- `PROPOSED`: Emitted by `EvolutionProposalEngine` from a `VALIDATED` or `DURABLE` lesson.
- `PENDING_REVIEW`: Staged for human inspection with explicit blast radius, risk tier, and verification plan.
- `APPLIED`: Approved by human developer and compiled into project configuration or skills.
- `REJECTED`: Dismissed or invalidated due to project drift.

### 4.2 Proposal Invariants
- Proposals cannot be applied automatically; attempting to set status to `APPLIED` without human authorization raises a safety violation.
- Every proposal includes an automated rollback plan, verification contract, and affected subsystem mapping.

---

## 5. Knowledge Decay & Staleness Lifecycle

Knowledge in software repositories is not immortal. Code refactors, deleted files, and retired subsystems render historical lessons obsolete. AntiOS implements active knowledge decay:

```text
  ┌──────────┐      File Deleted or Subsystem Pruned      ┌──────────┐
  │  ACTIVE  │ ─────────────────────────────────────────> │  STALE   │
  └──────────┘                                            └──────────┘
       │                                                        │
       │ Replaced by Newer Pattern                              │ Verified Invalid
       ▼                                                        ▼
┌──────────────┐                                         ┌──────────────┐
│  SUPERSEDED  │                                         │ INVALIDATED  │
└──────────────┘                                         └──────────────┘
       │                                                        │
       └────────────────────┬───────────────────────────────────┘
                            │ Archived after Grace Period
                            ▼
                     ┌──────────────┐
                     │   RETIRED    │
                     └──────────────┘
```

- **Staleness Audit**: `KnowledgeDecayEngine` cross-references all lessons against the physical filesystem and `project_anatomy.json`. If referenced files or subsystems no longer exist, the lesson transitions to `STALE`.
- **Pending Proposals Invalidation**: Proposals referencing stale artifacts are immediately transitioned to `REJECTED`.
- **Provenance Preservation**: Stale or retired knowledge is **never silently erased**. Its evidence ledger, timestamps, and causal chains are preserved in an immutable historical archive for auditability.

---

## 6. The Learning Safety Gate (10 Non-Bypassable Invariants)

The `LearningSafetyGate` acts as an impenetrable barrier around the learning subsystem, verifying 10 invariants on every observation and proposal:

1. **Prompt Injection Defense**: Rejects inputs containing adversarial command sequences (`ignore all previous instructions`, `bypass safety`, DAN/god-mode personas).
2. **Destructive Execution Filter**: Rejects destructive shell payloads (`rm -rf`, format commands, disk wipes).
3. **Markup & XSS Confinement**: Blocks executable HTML/JavaScript tags (`<script>`, `javascript:`) in observation payloads.
4. **Core Framework Immutability**: Strictly denies any proposal attempting to modify `framework/`, `ANTIOS_CONSTITUTION.md`, or core governance (`CORE ≠ ADAPTER`).
5. **Specialist Self-Promotion Block**: Enforces the Shallow Depth Law (`max_depth <= 2`). Rejects any proposal granting `can_delegate=True` to specialists.
6. **MCP Privilege Confinement**: Denies proposals attempting to grant unconfigured MCP tool execution authority.
7. **Storage Resource Caps**: Enforces the 100-item / 200 KB ceiling to eliminate denial-of-service vectors.
8. **Recursive Loop Prevention**: Rejects circular self-reinforcement loops where an agent cites its own prior interpretation without external witnesses.
9. **Ephemeral Evidence Rejection**: Prevents promotion based solely on temporary or volatile cache artifacts.
10. **Human Oversight Mandate**: Guarantees that code or skill modifications require explicit human sign-off.
