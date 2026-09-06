# Epistemic & Operational Firewall: System A vs System B

**Specification**: `docs/architecture/experience/SYSTEM_A_B_SEPARATION.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 10  

---

## 1. The Separation Mandate

AntiOS bifurcates its learning and intelligence architecture into two strictly segregated systems:

```
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│       SYSTEM A: PROJECT MEMORY       │     │     SYSTEM B: EXPERIENCE INTEL       │
├──────────────────────────────────────┤     ├──────────────────────────────────────┤
│ Scope: Target Project Local          │     │ Scope: Cross-Project / AntiOS Wide   │
│ Location: docs/, .antios/            │     │ Location: <central_data>/experience.db│
│ Epistemics: High (Evidence Ladder)   │     │ Epistemics: Statistical / Empirical  │
│ Purpose: Target project engineering  │     │ Purpose: Framework health & quality  │
│ Mutation: Git version-controlled     │     │ Mutation: Central append-only SQLite │
│ Agent Feedback: Direct & Active      │     │ Agent Feedback: Offline & Read-Only  │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │
                   └────────────── THE ABSOLUTE FIREWALL ───────┘
```

---

## 2. System A Specification: Project-Specific Learning & Memory

- **Location**: Resides exclusively inside the target project repository (`docs/ACTIVE_CONTEXT.md`, `docs/LESSONS.md`, `.antios/proofs/`).
- **Core Axiom**: *"Learning is evidence accumulation, not memory mutation."* (`framework/core/learning.py:L11`).
- **Evidence Promotion Ladder**:
  1. `OBSERVED`: Raw empirical tool output or command result.
  2. `CANDIDATE`: Repeated pattern observed across $\ge 2$ task turns.
  3. `VALIDATED`: Tested and confirmed by physical verification pass.
  4. `DURABLE`: Proven invariant grounded by SHA-256 hash of codebase files.
- **Safety Gate**: `LearningSafetyGate` filters prompt injections, destructive commands, and caps storage ($\le 50$ lessons, $\le 50$ proofs).
- **Human-in-the-Loop**: Self-modifying proposals (`learning_proposals.json`) require explicit developer authorization before graduating to permanent project rules.

---

## 3. System B Specification: AntiOS-Wide Experience Intelligence

- **Location**: Resides strictly outside all project repositories in the centralized user data store (`<central_data>/experience.db`).
- **Purpose**: Tracks operational friction, tool failure rates, session durations, and navigation efficiency across multiple projects.
- **Privacy First**: 100% of credentials, keys, private file paths, and raw model thinking chains are scrubbed prior to persistence.
- **Epistemic Classification**: Every reported metric is tagged with its empirical validity:
  - `OBSERVED`: Direct factual count from sanitized events.
  - `DERIVED`: Mathematically computed ratio (e.g. success rate).
  - `UNKNOWN`: Insufficient sample size or zero denominator (no guessing).

---

## 4. The Four Firewall Rules

### Rule 1: Zero Repository Database Pollution (`INV-10`)
System B SQLite files (`experience.db`, `experience.db-wal`, `experience.db-shm`) must **NEVER exist inside any target project repository**. Automated test `tests/test_experience_operations.py:test_multi_project_no_db_in_project_repos` cryptographically enforces this across all project trees.

### Rule 2: Code Import Firewall (Enforced by AST)
Modules governing System A (`framework/core/learning.py`, `memory.py`, `project_proof.py`) and runtime templates (`.antios/runtime/*.py`) are strictly forbidden from importing any System B module (`experience.py`, `experience_analytics.py`, `telemetry_bridge.py`). This is verified by AST static analysis in `tests/test_experience_learning_separation.py`.

### Rule 3: Zero Automatic Feedback Loop
Telemetry metrics from System B can **NEVER automatically mutate project memory or configuration in System A**. Statistical friction observed in Project X cannot silently inject rules into Project Y. System B is an offline diagnostic ledger for human engineers, not an autonomous feedback controller.

### Rule 4: Byte-for-Byte Non-Mutation Verification
Any System B administrative operation (backup, restore, purge, vacuum, export) must leave target project files 100% untouched. Automated tests compute SHA-256 trees of the workspace before and after operations, verifying byte-for-byte immutability.
