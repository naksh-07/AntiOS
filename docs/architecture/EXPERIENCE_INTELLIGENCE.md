# AntiOS 2.1 Experience Intelligence Engine (`docs/architecture/EXPERIENCE_INTELLIGENCE.md`)

## 1. Overview & Architectural Demarcation

AntiOS 2.1 introduces the **Experience Intelligence Engine (Phase 106)**, a deterministic, local-first analytics layer built on top of the Phase 103–105 Experience Store (`experience.db`).

The system transforms sanitized telemetry into auditable engineering intelligence without modifying AntiOS runtime behavior, project learning, or memory.

```text
Experience Store (<data-dir>/experience.db)
                     ↓
       Deterministic Analytics Engine
                     ↓
   Core Metrics (Observed / Derived / Unknown)
                     ↓
Failure & Friction & Success Trajectory Patterns
                     ↓
       Structured Product Intelligence
                     ↓
        External Report & Export CLI
```

---

## 2. The Critical Architectural Boundary: System A vs System B

There are two intentionally separate systems within AntiOS:

```text
┌─────────────────────────────────────────────────────────────┐
│             SYSTEM A: PROJECT LEARNING & MEMORY             │
│                 "AntiOS learns ABOUT THE PROJECT"           │
├─────────────────────────────────────────────────────────────┤
│ • Scope: Target project repo (docs/, .antios/)              │
│ • Modules: learning.py, memory.py, evidence.py, proofs.py   │
│ • Assets: PROJECT_KNOWLEDGE, LESSONS, DECISIONS, PROOFS     │
│ • Authority: Sovereign epistemic evaluation of project facts│
│ • Purpose: Improve future work INSIDE THAT PROJECT          │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ ABSOLUTE SEPARATION FIREWALL
                              │ (NO AUTOMATIC PROMOTION)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          SYSTEM B: ANTIOS EXPERIENCE INTELLIGENCE           │
│                 "AntiOS learns ABOUT ANTIOS ITSELF"         │
├─────────────────────────────────────────────────────────────┤
│ • Scope: External central store (<ANTIOS_DATA_DIR>)         │
│ • Modules: experience_analytics.py, experience.py, cli.py   │
│ • Assets: sessions, missions, tool_calls, events, metrics   │
│ • Authority: Passive analytical ledger; zero code authority │
│ • Purpose: External product & engineering intelligence      │
└─────────────────────────────────────────────────────────────┘
```

### The Absolute Separation Rule
Experience Intelligence **MUST NOT** automatically feed into:
- `framework/core/learning.py`
- `framework/core/memory.py`
- `docs/LESSONS.md`
- `docs/PROJECT_KNOWLEDGE.md`
- `docs/ACTIVE_CONTEXT.md`
- `DECISION_REGISTER.md`
- `.antios/learning_observations.json`
- `.antios/learning_proposals.json`
- `.antios/proofs/proofs.json`
- Skills, rules, configuration, or governance state

> [!IMPORTANT]
> **No Autonomous Self-Modification**: The Experience Store is a telemetry ledger; the Experience Intelligence Engine is an analysis layer. Neither is an authority or autonomous self-improvement mechanism. Any future engineering change based on these findings must be a separate, human-directed AntiOS engineering decision.

---

## 3. Epistemic Classification of Metrics

The engine categorizes every metric into one of three strict epistemic tiers:

1. **`OBSERVED`**: Directly witnessed from raw recorded counts (e.g. `mission_count`, `turn_count`, `tool_call_count`, `missions_completed`, `missions_failed`).
2. **`DERIVED`**: Deterministically computed mathematical ratios (e.g. `success_rate`, `failure_rate`, `recovery_rate`, `retry_rate`, `verification_pass_rate`, `navigation_efficiency`).
3. **`UNKNOWN`**: When denominator is zero or telemetry data is unrecorded. The engine **never** invents heuristic guesses or produces fake certainty.

---

## 4. Analytical Dimensions

### A. Failure Intelligence
Identifies recurring engineering failure patterns across:
- Tool execution errors (`TOOL_FAILURE`, non-zero exit codes)
- Verification test failures (`TEST_FAILURE`)
- Stop Gate verification rejections (`STOP_GATE_RESULT: continue`)
- Categorized by root cause, affected projects, tool correlations, and recurrence frequency.

### B. Navigation & Workflow Friction
Detects measurable friction in agent trajectories:
- **`REPEATED_NAVIGATION_INSPECTION`**: Consecutive redundant views of the same file.
- **`SEARCH_THRASHING_BEFORE_NAVIGATION`**: Sequences of 3+ consecutive `grep_search` or `find_by_name` calls before file inspection.
- **`TOOL_RETRY_LOOP`**: Repeated invocations of identical tool configurations $\ge 3$ times.
- **`VERIFICATION_RECOVERY_CYCLE`**: Test failures followed by successful fix cycles.
- **`HIGH_TURN_TRAJECTORY_LENGTH`**: Missions requiring $> 10$ turns to reach conclusion.

### C. Successful Execution Strategies
Mines recurring execution trajectories from completed missions:
$$\text{Task Category} \longrightarrow \text{Canonical Tool Sequence} \longrightarrow \text{Verification} \longrightarrow \text{Success}$$

### D. Tenant Isolation & Cross-Project Aggregation
- **Project-Scoped Analysis** (`--project <id>` or default project context): Evaluates telemetry filtered strictly to the target project.
- **Cross-Project Global Analysis** (`--global`): Aggregates cross-project metrics (total volume, average missions, high-level patterns) without leaking project-specific source file paths.

---

## 5. Unified CLI Interface

Phase 106 extends the canonical `antios` CLI:

### 1. Analyze Telemetry
```bash
antios experience analyze [--project <id> | --global] [--data-dir <dir>] [--json]
```
Displays core metrics, failure patterns, friction patterns, capability stats, and data coverage.

### 2. Generate Intelligence Report
```bash
antios experience report [--project <id> | --global] [--format {text,markdown,json}] [--output <file>]
```
Generates a structured human- or machine-readable report.

### 3. Export Intelligence Snapshot
```bash
antios experience export [--project <id> | --global] [--format {json,markdown}] [--output <dir_or_file>]
```
Exports a deterministic, machine-readable snapshot to `<data-dir>/exports/` or a specified target path.

---

## 6. Experience Lifecycle Operations (Phase 107)

Phase 107 introduces complete operational control over the Experience Plane via `antios data`:

### 1. Online Hot Backup
```bash
antios data backup [--output <path>] [--data-dir <dir>] [--json]
```
Creates an atomic, consistent SQLite online backup using `sqlite3.backup()` into `<data-dir>/backups/`.

### 2. Database Restore
```bash
antios data restore --backup <path> [--confirm] [--dry-run] [--data-dir <dir>] [--json]
```
Restores database state from a verified backup with:
- Pre-flight `PRAGMA quick_check` integrity validation
- Mandatory `--confirm` safety gate (fail-closed without it)
- Automatic pre-restore hot backup before overwriting
- `--dry-run` inspection mode

### 3. Data Purge & Retention
```bash
antios data purge [--project <id> | --all] [--older-than <days>] [--confirm] [--dry-run] [--data-dir <dir>] [--json]
```
Safely deletes experience records with:
- Mandatory tenant scoping (`--project <id>` or `--all`)
- Mandatory `--confirm` flag
- Automatic pre-purge hot backup
- Transactional cascade across relational tables
- Immediate post-purge incremental vacuum
- `--dry-run` record count preview

### 4. Database Vacuum & Space Reclamation
```bash
antios data vacuum [--full] [--data-dir <dir>] [--json]
```
Reclaims fragmented disk space using `PRAGMA incremental_vacuum` (or `VACUUM` with `--full`).

### 5. Raw Experience Export
```bash
antios data export [--project <id>] [--output <file>] [--data-dir <dir>] [--json]
```
Streams raw sessions, missions, turns, tool_calls, and engineering_events to portable JSONL.

---

## 7. Safety, Determinism & Privacy Guarantees

- **Zero Background Daemons**: 100% on-demand CLI and API invocation.
- **Zero Vector Embeddings / External Services**: Pure Python standard library and SQLite WAL queries.
- **Fail-Closed Isolation**: Telemetry or database errors never crash the host engineering task; collection mode defaults to `OFF`.
- **Cryptographic Immutability**: Verified by automated regression tests (`test_experience_learning_separation.py`, `test_experience_operations.py`) proving byte-for-byte non-mutation of target project files.
- **Adversarial Privacy & Redaction**: Multi-tier secret scrubbing (Google API keys, GitHub PATs, JWTs, PEM keys, credential URIs, KV assignments) and prompt injection defanging verified under adversarial conditions.
- **Restart Idempotency**: Byte-offset checkpointing, SHA-256 event signatures, and `INSERT OR IGNORE` ensure zero duplicate event multiplication across crashes or restarts.

