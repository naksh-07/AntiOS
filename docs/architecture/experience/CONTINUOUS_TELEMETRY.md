# Continuous Experience Telemetry Pipeline

**Specification**: `docs/architecture/experience/CONTINUOUS_TELEMETRY.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 9  

---

## 1. Non-Blocking Telemetry Axiom

Telemetry in AntiOS adheres to the **Non-Blocking Telemetry Axiom**:
> *"Experience telemetry must never become a dependency for normal engineering. Telemetry failure must never block, delay, or fail an active development task."*

Engineering tasks proceed normally regardless of database locks, telemetry disk errors, or missing logging files.

---

## 2. Ingestion Architecture: Event-Driven & Hook-Embedded

To satisfy `INV-15` (Zero Background Daemons), AntiOS avoids long-running watcher processes. Ingestion is triggered directly by platform lifecycle hooks during natural developer interactions:

```
[ Antigravity Tool / Hook Event ]
                │
                ▼ (Hook Ingestion Trigger in Stop Gate / Guards)
       telemetry_bridge.py
                │
                ▼ (Incremental Read via Byte-Offset Checkpoint)
       Reads transcript.jsonl (from last_byte_offset)
                │
                ▼ (Privacy Sanitizer: sanitizer.py)
       Fail-closed secret & path scrubbing
                │
                ▼ (Batch Append to External Store)
     <central_data>/experience.db (SQLite WAL Mode)
```

### 2.1 Incremental Byte-Offset Checkpointing
Rather than re-parsing entire multi-megabyte transcripts on every turn, `TelemetryBridge` tracks an `IngestionCheckpoint` record in `experience.db`:
- Stores the exact `last_byte_offset` and line count for each transcript file.
- Reads only newly appended bytes using file seek.
- Parses newly added JSON lines in $< 15$ms.
- Updates checkpoint atomically inside a SQLite transaction.

---

## 3. The Privacy Sanitization Pipeline (`sanitizer.py`)

Before any event or tool call is committed to `experience.db`, it passes through the multi-tier fail-closed privacy sanitizer:

```
RAW TELEMETRY EVENT
        │
        ├─► Secret Scrubbing:
        │   - Google API keys (`AIza[0-9A-Za-z-_]{35}`)
        │   - GitHub tokens (`gh[pousr]_[0-9A-Za-z]{36}`)
        │   - AWS Access Key IDs & Secrets (`AKIA...`)
        │   - Bearer tokens, passwords, private SSH keys
        │   - High-entropy base64/hex token strings
        │
        ├─► Path Containment:
        │   - Replaces external absolute paths with `<EXTERNAL_PATH>`
        │   - Anonymizes user home directories (`C:\Users\<USER>`)
        │
        └─► Model Output Containment:
            - Redacts raw prompt inputs
            - Strips model internal chain-of-thought (`thinking` fields)
            - Retains only tool names, execution duration, and sanitized parameters
```

---

## 4. Centralized Storage Layout (`experience.db`)

To comply with `INV-10` (4-Boundary Demarcation), zero telemetry files are created inside the target project repository. All data resides in an external user data directory resolved via `AntiOSDataResolver`:

- **Windows**: `%LOCALAPPDATA%\AntiOS\central_data\experience.db`
- **macOS**: `~/Library/Application Support/AntiOS/central_data/experience.db`
- **Linux**: `~/.local/share/antios/central_data/experience.db`

### SQLite Configuration
- **Journal Mode**: `WAL` (Write-Ahead Logging) for concurrent reader/writer support.
- **Synchronous**: `NORMAL` (optimal balance of crash safety and high performance).
- **Busy Timeout**: `5000ms` (handles transient lock contention smoothly).

---

## 5. Fail-Safe Degradation & Error Handling

If `experience.db` encounters an error (disk full, database locked, corrupted schema, or missing permissions):
1. `TelemetryBridge` catches the exception fail-safe.
2. A non-intrusive warning is emitted to `stderr` or local debug logs.
3. The hook process exits with code 0.
4. The developer's tool call or task turn finishes successfully without interruption.
