# AntiOS Rollback & Recovery Guide

This document describes the rollback model, guarantees, and boundaries of AntiOS.

---

## 1. The Single Non-Negotiable Invariant

> **AntiOS Rollback is Strictly Scoped to AntiOS Assets. AntiOS NEVER Touches or Reverts User Application Code.**

When you run `antios rollback`, AntiOS restores:
- `.antios/` metadata files (manifest, knowledge graph, anatomy, tool policy)
- `.antios/runtime/` scripts (pre-tool guard, stop gate, wayfinder)
- `.agents/skills/antios/SKILL.md`
- `antios.config.json`

AntiOS **never** rolls back:
- Uncommitted user application files (`src/`, `app/`, `tests/`, etc.)
- Git working tree changes made to user code
- User-authored custom skills or configs

---

## 2. Rollback Execution

### Rollback to Most Recent Prior Snapshot
```bash
antios rollback
```
AntiOS inspects `.antios/backups/`, selects the latest snapshot file, and restores all managed artifacts to their previous state.

### Rollback to a Specific Version Snapshot
```bash
antios rollback --version 2.0.0
```

### Preview Rollback (Dry-Run)
```bash
antios rollback --dry-run
```

---

## 3. Honest Reporting: When Rollback is Unavailable

If no prior snapshot exists (e.g. fresh installation or backups directory was purged), AntiOS **honestly reports that rollback is unavailable**:

```
[BLOCKED] Rollback unavailable: No prior snapshot recorded.
  - No rollback points available: .antios/backups directory does not exist.
```

AntiOS will **never** pretend a rollback succeeded when no snapshot was available.

---

## 4. Snapshot Storage Format

Snapshots are stored in `.antios/backups/` as self-contained JSON records:
```json
{
  "timestamp": "2026-09-06T12:00:00Z",
  "antios_version": "2.0.0",
  "label": "pre-update",
  "manifest": { ... },
  "files": {
    ".antios/manifest.json": "...",
    ".antios/knowledge.json": "...",
    "antios.config.json": "..."
  }
}
```
User-owned files are excluded from backup snapshots to prevent duplicate data storage.
