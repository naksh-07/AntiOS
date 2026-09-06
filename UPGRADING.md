# AntiOS Upgrading & Migration Guide

This document describes how to safely update AntiOS instances to newer framework versions and schemas.

---

## 1. The Safe Update Lifecycle

AntiOS executes updates through a deterministic 6-stage lifecycle:

```
1. INSPECT   ──> Determine installed version vs available target version
       │
2. VALIDATE  ──> Check schema compatibility and detect potential conflicts
       │
3. SNAPSHOT  ──> Save restorable instance snapshot into .antios/backups/
       │
4. UPDATE    ──> Recompile boundary and synchronize generated runtime scripts
       │
5. VERIFY    ──> Execute verification checks on fresh runtime closure
       │
6. REPORT    ──> Emit detailed summary of updated files and backup location
```

---

## 2. Checking for Updates

Before updating, you can run a non-mutating update check:

```bash
# Check if updates are available:
antios update --check

# Machine-readable check:
antios update --check --json
```

If an update is available, the CLI reports the version delta (e.g. `2.0.0` -> `2.0.0-beta.1`).

---

## 3. Applying an Update

```bash
# Update to latest framework revision:
antios update

# Update to specific version:
antios update --version 2.0.0-beta.1

# Preview update without modifying disk:
antios update --dry-run
```

### Pre-Update Snapshotting Guarantee
Before writing any file during an update, AntiOS automatically saves a full JSON snapshot of all manifest-tracked files into:
```
.antios/backups/snapshot_<TIMESTAMP>_<VERSION>_pre-update.json
```
If an update encounters conflicts or fails verification, the prior state can be immediately restored via `antios rollback`.

---

## 4. Migration Architecture

If a new AntiOS version introduces changes to instance schemas:
1. `MigrationEngine` (`framework/core/migration.py`) constructs a `MigrationPlan`.
2. Each step is evaluated (`SCHEMA_UPGRADE`, `ARTIFACT_REGENERATE`, `REPAIR_MISSING`, `CLEANUP_STALE`).
3. User-owned or modified files are never overwritten silently.
4. If unresolved conflicts exist, migration **fails closed** with an actionable diagnostic report.
