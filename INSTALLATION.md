# AntiOS Installation Guide

This document describes how to install, initialize, and verify AntiOS in any software project.

---

## 1. Prerequisites

- **Python**: `>= 3.8` (standard library only; zero pip dependencies required)
- **Git**: `>= 2.20` (recommended for local working tree inspection)
- **Google Antigravity**: 2.0+ (supported platform runtime)

---

## 2. Deterministic Installation Lifecycle

The canonical AntiOS adoption workflow follows:

```
INSTALL  ──>  VERIFY  ──>  ADAPT  ──>  USE
```

### Step 1: Install AntiOS into Target Project
```bash
antios install --path /path/to/project
```
- Creates `.antios/` metadata directory and canonical instance files.
- Generates `antios.config.json` adapter configuration.
- Configures `.agents/hooks.json` to attach deterministic pre-tool and stop guards.
- Installs `.agents/skills/antios/SKILL.md`.
- **Idempotency Guarantee**: Running `antios install` on an already-installed, healthy project is a deterministic no-op (`status=IDEMPOTENT`, 0 files modified).

### Step 2: Verify Installation Health
```bash
antios verify --path /path/to/project
```
- Validates SHA-256 digests against `.antios/manifest.json`.
- Audits `.antios/runtime/` closure (verifies zero source leaks).
- Confirms adapter policies and runner availability.

### Step 3: Adapt to Project Stack
```bash
antios adapt --path /path/to/project
```
- Discovers project topology, manifests, and test suites.
- Generates stack-specific runners and protected zones.

---

## 3. Installation CLI Options

| Flag | Purpose | Default |
| :--- | :--- | :--- |
| `--path <DIR>` | Target project root directory | Current working directory |
| `--version <V>` | Target AntiOS version to install | Current framework version |
| `--dry-run` | Preview installation actions without writing files | `False` |
| `--force` | Overwrite managed files even if modified | `False` |
| `--force-downgrade` | Explicitly permit installing an older version over a newer one | `False` (Blocked) |
| `--json` | Output machine-readable JSON summary | `False` |

---

## 4. What AntiOS Changes & What It Never Changes

### AntiOS Creates / Manages:
- `.antios/` (manifest, knowledge graph, anatomy, runtime guards)
- `antios.config.json` (declarative adapter configuration)
- `.agents/skills/antios/SKILL.md` (project control plane skill)
- `.agents/hooks.json` (managed Antigravity hook registrations)

### AntiOS NEVER Modifies:
- User application source code (`src/`, `app/`, `lib/`, etc.)
- User domain configuration or business logic
- User-authored custom skills in `.agents/skills/*`
- User test suites or package lockfiles
