# AntiOS 2.1 Storage & Data Directory Foundation (`docs/architecture/STORAGE_FOUNDATION.md`)

## 1. Overview & Primary Objective

AntiOS 2.1 establishes a **Central Data Directory Model** for persistent engineering intelligence, decoupling local operational telemetry from target project repositories.

Target repositories governed by AntiOS **never** contain central experience databases or binary SQLite artifacts (satisfying Invariant **INV-10: SOURCE ≠ INSTANCE ≠ PROJECT**). Instead, all telemetry, sessions, and events reside inside a user-configurable central AntiOS Data Directory.

```text
<ANTIOS_DATA_DIR>/                     <-- User-configured central data directory
├── experience.db                      <-- Authoritative SQLite 3 database
├── experience.db-wal                  <-- Active WAL journal
├── experience.db-shm                  <-- Shared memory index
├── config.toml                        <-- Telemetry & retention configuration
├── backups/                           <-- Hot timestamped online backups
└── exports/                           <-- Scrubbed JSON / Markdown exports
```

---

## 2. Configuration & Precedence

The central data directory location is resolved via the single authoritative resolver: `AntiOSDataResolver.resolve_data_dir()`.

Resolution follows strict deterministic precedence:
1. **Explicit Argument**: `--data-dir <path>` passed via CLI or direct API invocation.
2. **Environment Variable**: `ANTIOS_DATA_DIR` environment variable.
3. **Project Adapter Configuration**: `"data_dir": "<path>"` in `antios.config.json`.
4. **Project Manifest Metadata**: `"data_dir": "<path>"` in `.antios/manifest.json`.
5. **Fail-Closed Default**: If no data directory is configured, storage operations fail closed with a clear diagnostic message. AntiOS **never** silently creates a database inside the project or invents an unsafe fallback location.

---

## 3. Installation & CLI Usage

### Initial Installation with Data Directory
To establish the AntiOS Data Directory during project installation:
```bash
antios install --path <project> --data-dir <directory>
```
This command:
- Establishes `<directory>/` with `backups/`, `exports/`, and default `config.toml`.
- Initializes `experience.db` with WAL mode and foundational schema tables.
- Registers the project with a deterministic `project_id`.
- Stores the data directory reference in `antios.config.json` and `.antios/manifest.json`.

### Changing or Re-Pointing the Data Directory
To bind a project to an existing or new data directory:
```bash
antios data set-dir <directory> [--path <project>]
```

### Inspecting Storage Health
To inspect data directory health, database size, PRAGMA status, and registered tables:
```bash
antios data status [--path <project>] [--json]
```

`antios doctor` and `antios status` also perform non-destructive diagnostics on the configured data directory and report errors or missing assets.

---

## 4. SQLite Engine & Concurrency Baseline

The storage engine uses the Python standard library `sqlite3` exclusively (zero third-party dependencies).

Mandatory PRAGMA settings applied to every connection:
- `PRAGMA journal_mode = WAL;` (Write-Ahead Logging for non-blocking concurrent readers).
- `PRAGMA synchronous = NORMAL;` (1 fsync per checkpoint for high performance and durability).
- `PRAGMA busy_timeout = 5000;` (5,000ms wait on lock contention).
- `PRAGMA foreign_keys = ON;` (Relational integrity across all tables).
- `PRAGMA auto_vacuum = INCREMENTAL;` (Page reclamation during retention pruning).

AntiOS operates with **zero background daemons, watchers, or socket servers**. All storage interactions are event-driven and execute synchronously within CLI commands, hooks, or test runners.

---

## 5. Entity Schema & Tenant Scoping

The initial schema establishes the foundational entity hierarchy:
```text
GLOBAL (Data Dir / config.toml)
  └── projects (Unique deterministic codebase identity)
        └── sessions (Antigravity conversation lifecycle)
              └── missions (Bounded engineering tasks under AntiOS governance)
                    └── turns (Agent invocation steps)
                          └── tool_calls (Deterministic tool executions)
                                └── engineering_events (Canonical taxonomy events)
```

### Tenant Isolation
Multi-tenancy is enforced logically in `experience.db`:
- Every session, mission, and event is explicitly scoped to a `project_id`.
- Operational queries parameterize `WHERE project_id = ?`.
- Queries executed in Project A context return zero records from Project B.

---

## 6. Current Phase 103 Limitations

> [!IMPORTANT]
> **Phase 103 establishes ONLY the storage foundation.**
> - **Telemetry collection is NOT active yet.**
> - **No transcript ingestion, prompt recording, or chain-of-thought capture is performed.**
> - **No automatic event recording takes place during normal 2.0 tool execution.**
> - **No background daemon or watcher exists.**
>
> Ingestion hooks, secret redaction, and pattern mining will be introduced in subsequent phases (104–106). AntiOS 2.0 architectural invariants remain 100% intact.
