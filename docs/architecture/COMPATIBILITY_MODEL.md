# Compatibility & Migration Model (`docs/architecture/COMPATIBILITY_MODEL.md`)

## 1. Overview
AntiOS 2.0 provides an idempotent, fail-closed compatibility and migration engine to inspect, upgrade, and repair Project Agent OS instances across framework versions.

---

## 2. Compatibility States

| State | Description | Action Required |
|---|---|---|
| `COMPATIBLE` | Instance version and manifest schema align with Core | Normal operation |
| `UPGRADE_AVAILABLE` | Minor/patch update available with backward compatibility | Optional clean upgrade |
| `MIGRATION_REQUIRED` | Manifest schema delta or compiler adjustments required | Execute migration plan |
| `INCOMPATIBLE` | Major version leap breaking backward contracts | Manual intervention |
| `CORRUPTED` | Malformed manifest JSON or violated integrity checks | Fail closed; repair manifest |
| `UNKNOWN` | Target folder lacks `.antios/manifest.json` | Run initial project compilation |

---

## 3. Seven-Stage Migration Lifecycle
Migrations adhere to a strict sequential progression:
$$\text{INSPECT} \longrightarrow \text{PLAN} \longrightarrow \text{CONFLICT\_CHECK} \longrightarrow \text{SNAPSHOT} \longrightarrow \text{MIGRATE} \longrightarrow \text{VERIFY} \longrightarrow \text{COMMIT\_STATE}$$

1. **Inspect**: Determine `CompatibilityState` by inspecting `.antios/manifest.json` against Core SemVer.
2. **Plan**: Formulate granular, idempotent `MigrationStep` items (e.g. `SCHEMA_UPGRADE`, `ARTIFACT_REGENERATE`).
3. **Conflict Check**: Cross-examine proposed changes against artifact provenance:
   - User-authored files (`USER_AUTHORED`) are strictly preserved.
   - Unresolved conflicts cause the migration plan to fail closed (`is_executable = False`).
4. **Snapshot**: Capture pre-migration state of all modified files and manifest.
5. **Migrate**: Execute discrete steps (schema upgrades, artifact rewrites).
6. **Verify**: Run verification gates and check file integrity.
7. **Commit State**: Save updated manifest and bump revision. Rollback immediately if errors occur.

---

## 4. CLI Tooling
AntiOS provides a dedicated CLI tool in `framework/scripts/tools/migrate_instance.py`:
```bash
# Check compatibility status
python framework/scripts/tools/migrate_instance.py . --check

# Dry-run migration planning
python framework/scripts/tools/migrate_instance.py . --dry-run

# Execute full atomic migration
python framework/scripts/tools/migrate_instance.py .
```
