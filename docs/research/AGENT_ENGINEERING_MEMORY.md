# AntiOS Research 4: Agent Engineering Memory & Epistemic Hygiene
## Historical Persistence, Epistemic Safety, and Cross-Session Recall

**Status**: CANONICAL RESEARCH MONOGRAPH  
**Phase**: AntiOS Research 4 — Large Repository Agent Engineering & Project Intelligence  
**Target Repository**: `naksh-07/AntiOS`  
**Evidence Standard**: `[OFFICIAL]`, `[OBSERVED]`, `[INFERRED]`, `[EXTERNAL_REPORT]`, `[HYPOTHESIS]`, `[UNKNOWN]`, `[CONFLICT]`  

---

## 1. Executive Summary

Autonomous software agents frequently suffer from **Episodic Amnesia**: across successive turns, compacting context windows, or new conversation sessions, the agent resets to a blank slate. Without structured engineering memory, agents repeatedly re-attempt failed fixes, re-introduce previously diagnosed bugs, and re-explore known architectural dead ends.

However, unconstrained agent memory introduces an equally hazardous failure mode: **Epistemic Pollution**. When unverified hypotheses, hallucinated assumptions, or obsolete observations are stored as "truth," future agents accept them unconditionally, leading to systemic regression cascades.

This monograph formulates the **Agent Engineering Memory Architecture** for AntiOS. We define:
1. The **8 Canonical Categories of Engineering Memory** required for multi-session software projects.
2. The trade-offs between **Git-versioned Markdown**, **Structured SQLite (`experience.db`)**, and **Ephemeral Session Buffers**.
3. The **Epistemic Hygiene Protocol**: a strict cryptographic and evidentiary gating mechanism that prevents memory pollution and guarantees safe invalidation upon code drift.

---

## 2. The 8 Canonical Categories of Engineering Memory

Software engineering memory is not homogeneous. Attempting to dump all memory into a single unstructured chat log or scratchpad creates noise. AntiOS delineates 8 distinct, strongly typed memory categories:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 THE 8 CANONICAL ENGINEERING MEMORY CATEGORIES               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Architectural Decisions (ADRs)                                           │
│    • Why an architectural path was chosen and what alternatives were rejected│
│    • E.g., ADR-004: Adopting Merkle trees over SQLite file watchers (INV-15)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Failed Hypotheses & Dead Ends                                            │
│    • What fixes were attempted, why they failed, and what error was produced│
│    • Prevents future agents from thrashing on the exact same pseudo-solution│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Root Cause Analyses (RCAs) & Historical Bug Causes                       │
│    • Underlying mechanics of past incidents and non-obvious failure modes.  │
│    • E.g., Subprocess hangs when executing `git status` without stdout pipe │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Environment Quirks & Host Workarounds                                    │
│    • Platform-specific oddities: Windows NTFS path separators, PTY quirks,  │
│      PowerShell escaping rules, or Node.js memory limits.                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Tool Hazards & Forbidden Flags                                           │
│    • Commands or tools that trigger infinite loops, hang hooks, or corrupt  │
│    • E.g., Never invoke `npm test` without `--watchAll=false`.              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 6. Verification Runbooks & Target Matrices                                  │
│    • Exact mappings between modified files and mandatory test invocations.  │
│    • E.g., Touching `framework/hooks/gate.py` requires `tests/run_all.py`.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 7. Performance Baselines & Regressions                                      │
│    • Benchmark timings: hook execution latency (<100ms), test duration.    │
│    • Detects slow creeping regressions before they violate SLAs.            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 8. User Preferences & Project Idioms                                        │
│    • Direct stylistic or workflow mandates from human operators.            │
│    • E.g., Prefer single-line docstrings; always use `replace_file_content`.│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Storage Substrates: Git Markdown vs. SQLite vs. Vector Stores

We evaluated three candidate storage substrates for agent engineering memory:

| Evaluated Dimension | Substrate A: Git-Tracked Markdown (`docs/memory/`) | Substrate B: Structured SQLite (`.agents/experience.db`) | Substrate C: Vector Database (Embeddings) |
| :--- | :--- | :--- | :--- |
| **Human Auditability** | **Optimal**: 100% human-readable diffs via `git log`. | **Moderate**: Requires SQL query tool or GUI. | **Zero**: High-dimensional floating point vectors. |
| **Branch Alignment** | **Perfect**: Memory branches, merges, and rebases with code. | **Conflict Prone**: Binary file; merge conflicts corrupt DB. | **Hazardous**: Embeddings drift out of sync with branches. |
| **Query Latency** | **Fast**: Instant file read (`view_file`). | **Sub-millisecond**: Indexed B-tree lookups (<1ms). | **Slow**: Subprocess/API vector similarity search (100–500ms). |
| **Machine Interception** | **Moderate**: Requires markdown parsing. | **Optimal**: Strongly typed relational schema and triggers. | **Poor**: Semantic fuzziness; probabilistic ranking. |
| **Constitutional Status** | **Approved**: Fully compliant with AntiOS charter. | **Approved (Local Cache Only)**: Must not be git-committed. | **BANNED (INV-09)**: Prohibited under Architecture Freeze. |

### The AntiOS Dual-Storage Architecture
AntiOS adopts a **Dual-Storage Memory Model**:
1. **Authoritative Semantic Memory**: Stored as Git-tracked Markdown files in `docs/architecture/` and `docs/memory/`. Because these files live in git, they automatically stay aligned with git branches, pull requests, and rollbacks.
2. **Ephemeral Operational Telemetry**: Stored in a local, untracked SQLite database (`.agents/telemetry.db`). This records ephemeral hook execution timings, turn tokens, and run metrics without polluting git history.

---

## 4. Epistemic Hygiene: Preventing Memory Contamination

### 4.1 The Hallucination Poisoning Problem
In multi-agent systems, Agent A makes an unverified assumption (e.g. *"The test suite is broken due to Windows path separators"*). Agent A writes this into a memory file. Agent B reads the memory file, treats the assumption as a verified axiom, and spends 10 turns refactoring path logic while the real bug was an uninstalled dependency.

### 4.2 The 4-Tier Epistemic Ladder
To prevent epistemic contamination, all memory records in AntiOS must carry a verified epistemic classification tag:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EPISTEMIC HYGIENE LADDER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tier 1: [VERIFIED_FACT]                                                     │
│   • Backed by physical command execution and exit code 0 or compiler output.│
│   • Must include execution timestamp, command line, and observed output.    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tier 2: [ARCHITECTURAL_DECISION]                                            │
│   • Explicit human operator mandate or signed ADR document.                 │
│   • Permanent until explicitly repealed by a subsequent ADR.                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tier 3: [TESTED_NEGATIVE] (Dead End)                                        │
│   • An approach that was physically executed and failed with an exact error.│
│   • Must record: Target File, Applied Diff, Exact Error Output.             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Tier 4: [WORKING_HYPOTHESIS]                                                │
│   • Unproven conjecture formulated by an agent during reasoning.            │
│   • Prohibited from persisting across sessions. Quarantined to active turn. │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Cryptographic Memory Invalidation
A memory record referencing a specific file or function becomes stale when that file is modified. AntiOS introduces **Cryptographic Target Binding**:
- Every memory record stores the `TargetFile` and the `TargetContentHash` (SHA-256 of the target function or file) at the time of memory creation.
- When an agent retrieves the memory record, the retrieval engine checks the target's current hash against the stored hash.
- If the hashes differ, the memory record is tagged `[STALE_EVIDENCE]` and suppressed from the agent's primary working context until re-verified.

---

## 5. Standardized Memory Schema Formats

### 5.1 Dead-End Record Schema (`docs/memory/dead_ends.md`)
```markdown
### DE-042: Bypassing PreToolUse via Shell Subshell Wrapping
- **Status**: [TESTED_NEGATIVE]
- **Timestamp**: 2026-09-08T00:15:22Z
- **Target Subsystem**: `framework/hooks/gate.py`
- **Hypothesis**: Wrapping forbidden command in `powershell -Command { ... }` bypasses the hook.
- **Attempted Action**: Executed `powershell -Command { git tag -d v1.0 }` via `run_command`.
- **Observed Result**: Denied by `PreToolUse` hook (exit code 1, decision: "deny").
- **Root Cause**: The hook parses shell tokens recursively across subshell invocations.
- **Guidance**: Do NOT attempt subshell wrappers; all command variants are intercepted.
```

### 5.2 Root Cause Analysis Schema (`docs/memory/rca/`)
```markdown
# RCA-018: Test Runner Hang on Windows PowerShell

- **Status**: [VERIFIED_FACT]
- **Date**: 2026-09-07
- **Affects**: Windows PowerShell subprocess execution of `tests/run_all.py`
- **Symptom**: Stop Gate hangs for 300 seconds and times out.
- **Physical Root Cause**: The test runner was waiting for `sys.stdin.read()` because `PAGER=cat` was missing, causing git commands invoked by tests to spawn `less.exe`.
- **Verified Remedy**: Always set `PAGER=cat` and `PYTHONUNBUFFERED=1` in the subprocess environment dictionary before launching test runners.
```

---

## 6. Retrieval & Context Budget Management

Memory records must not be injected blindly into turn-0 context. Ingesting 20 dead-end records consumes 4,000 tokens. AntiOS mandates **Targeted On-Demand Memory Retrieval**:

```
                       ┌───────────────────────────────────────┐
                       │           Agent Task Assigned         │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       Resolve Target Subsystem via Route Map
                                           │
                                           ▼
                      Query docs/memory/ for Subsystem Tags
                                           │
                                           ▼
                       Filter: Epistemic Status == [VERIFIED]
                               AND Target Hash Matches Code?
                                           │
                           ┌───────────────┴───────────────┐
                           │                               │
                          YES                              NO
                           │                               │
                           ▼                               ▼
               Inject Max 2 Relevant Records      Suppress Memory Record
               Budget: <= 300 tokens              (Avoid Stale Pollution)
```

---

## 7. Concrete AntiOS Architectural Recommendations

1. **Adopt Git Markdown as the Sole Authoritative Memory Medium (`[MANDATORY]`)**:
   Persist all architectural decisions, dead ends, and RCAs as Markdown files in `docs/memory/`. Reject SQLite databases for authoritative memory to preserve git branching, merging, and pull request reviewability.

2. **Enforce Strict Epistemic Tagging (`[MANDATORY]`)**:
   Prohibit ungrounded agent speculation from persisting in memory files. Any memory entry without a physical command log or verified error output must be rejected during the verification phase.

3. **Bind Memory to Cryptographic Code Hashes (`[RECOMMENDED]`)**:
   Include target AST or SHA-256 hashes in memory records. Automatically invalidate memory entries when target source files drift.

4. **Cap Injected Memory to 300 Tokens per Turn (`[RECOMMENDED]`)**:
   Inject at most 1–2 relevant dead-end records or RCA summaries when an agent touches a specific subsystem, protecting context window attention.

---

## 8. Classification & Verification Ledger

| Memory Principle / Metric | Classification | Evidence Source |
| :--- | :---: | :--- |
| Unstructured memory causes confirmation bias cascades | `[INFERRED]` | Observed agent thrashing on outdated markdown notes |
| SQLite binary databases cause merge conflicts in multi-agent git | `[OBSERVED]` | AntiOS 2.0 git merge conflicts on binary `.db` files |
| Vector embeddings drift out of sync with git branches | `[EXTERNAL_REPORT]` | Cursor & Copilot Workspace engineering reports |
| Target binding via SHA-256 hash invalidation prevents stale memory | `[OBSERVED]` | `sandbox/experiments_r4/exp2_freshness.py` |
| Upward traversal in Antigravity respects repo root | `[OFFICIAL]` | Antigravity Platform Specification |
