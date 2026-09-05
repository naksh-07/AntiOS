# AntiOS 2.0 Context Governance Specification
**Phases 87–88: Context Budget Governor, Freshness & Safe Compaction**
**Status**: Authoritative Architectural Specification | **Version**: 2.0.0

---

## 1. Overview & Guiding Doctrine

Context is the primary resource and vulnerability surface in agentic operating systems. Unbounded context leads to high token consumption, model distraction, reasoning degradation, and security vulnerabilities (e.g. indirect prompt injection or governance circumvention).

AntiOS 2.0 establishes the fundamental doctrine:
> **"Optimize USEFUL INFORMATION / CONTEXT COST, not MINIMUM TOKENS AT ANY COST."**

A compressed context that destroys architectural relationships, ownership tiers, or safety constraints is a catastrophic failure. Context governance is an internal AntiOS responsibility located at Stage 7 (`BUILD CONTEXT`) of the canonical 10-stage capability pipeline:
`UNDERSTAND` $\rightarrow$ `CHECK STATE` $\rightarrow$ `LOCATE` $\rightarrow$ `CLASSIFY` $\rightarrow$ `SELECT CAPABILITIES` $\rightarrow$ `SELECT WORKFORCE` $\rightarrow$ `BUILD CONTEXT` $\rightarrow$ `EXECUTE` $\rightarrow$ `VERIFY` $\rightarrow$ `REMEMBER`.

---

## 2. Phase 87: Context Budget Governor

The `ContextBudgetGovernor` (`framework/core/context_budget.py`) performs deterministic task-time context budgeting. It classifies all candidate sources and assigns deterministic governor actions.

### A. Epistemic Context Classification
Every candidate context item is classified into one of 6 states:
1. `MANDATORY`: Safety invariants, constitutional policies, acceptance criteria, and active blockers. Must be loaded unconditionally.
2. `RELEVANT`: Component intelligence, covering test commands, direct dependencies, and assigned target files.
3. `OPTIONAL`: Historical background, peripheral members, and reference guides.
4. `STALE`: Out of sync with disk reality, git HEAD, or manifest fingerprint.
5. `REDUNDANT`: Duplicate observations, identical skill cards, or repeated definitions.
6. `UNKNOWN`: Unverified or unclassified sources.

### B. Governor Action Allocations
The governor assigns one of 5 actions to each source:
- `LOAD`: Inject full content into the active turn context.
- `DEFER`: Omit from initial context; load on-demand when wave depth increases.
- `SUMMARIZE`: Safely compact content, preserving facts, invariants, and provenance.
- `DISCARD`: Exclude completely (redundant noise or irrelevant artifacts).
- `REFRESH`: Invalidate cache and reload from physical disk/manifest.

### C. Context Budget Reasoning Card
The governor emits a token-bounded reasoning card ($\le 16$ lines):
```text
=== ANTIOS CONTEXT BUDGET CARD ===
Budget Ceiling:        4000 tokens
Requested / Allocated: 2850 / 1420 tokens
Selected / Deferred:   5 / 2
Discarded / Redundant: 1
Refreshes Required:    none
Active Injections:     constitutional-invariants, subsystem-core, active-context-md
Governance Rationale:  Allocated 1420 tokens under budget 4000 with 5 active sources.
==================================
```

---

## 3. Phase 88: Context Freshness & Safe Compaction

### A. Freshness Model & Signals
The `FreshnessEvaluator` (`framework/core/context_freshness.py`) models freshness into:
- `FRESH`: Identical file SHA-256 and manifest fingerprint.
- `AGING`: Valid but unverified across recent commits.
- `STALE`: Physical file modified, git HEAD advanced, or manifest drifted.
- `INVALID`: Physical file missing or tests failing.
- `UNKNOWN`: Missing provenance.

**Governing Law**: *A stale source must NEVER silently appear as authoritative current context.*

### B. Safe Compaction Invariants
The `SafeContextCompactor` compacts text without losing critical semantic information:
1. **Fact Preservation**: All physical observations, test outputs, exit codes, and commit hashes are preserved.
2. **Invariants & Constraints**: Security boundaries (`IMMUTABLE_CORE_ZONES`), concurrency caps, and acceptance criteria are never truncated.
3. **No Inference-to-Fact Mutation**: Hypotheses or agent interpretations remain explicitly marked as inferences.
4. **Provenance Continuity**: All compacted blocks retain explicit provenance headers and source tracking.

---

## 4. Security & Boundary Hardening

Context must never become an authority escalation channel:
- **Constitutional Immunity**: Project text or external comments cannot override system instructions or modify `.agents/hooks.json`.
- **Pre-Tool Guard Synchronization**: File mutations are checked against `IMMUTABLE_CORE_ZONES` regardless of prompt claims.
- **Fail-Closed Stale Handling**: Stale context triggers a mandatory `REFRESH` action before worker execution.
