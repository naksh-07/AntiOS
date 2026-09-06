# AntiOS Release Engineering Dossier

This document details the release engineering infrastructure, automation, and tooling implemented for AntiOS 2.0.

---

## 1. Release Infrastructure Overview

```
                      AntiOS Release Architecture
                     ═════════════════════════════

    [ Local Development & Tests ]
                 │
                 ▼
    [ antios release check ] ─── Pre-flight validation gate
                 │                ├─ Git clean worktree check
                 │                ├─ Version consistency across files
                 │                ├─ Full regression test pass (tests/run_all.py)
                 │                ├─ Certification artifacts check
                 │                ├─ CHANGELOG.md release entry verification
                 │                └─ Active context budget bound (<= 60 lines)
                 ▼
    [ antios release notes ] ─── Automated structured notes assembly
                 │
                 ▼
    [ Annotated Git Tag ]    ─── e.g. v2.0.0-beta.1 (guarded on clean tree)
                 │
                 ▼
    [ GitHub Actions CI ]    ─── .github/workflows/ci.yml matrix test run
                 │
                 ▼
    [ GitHub Release ]       ─── Published release point with changelog notes
```

---

## 2. Release CLI Commands

AntiOS provides native release automation via the unified `antios` CLI:

### Pre-Flight Release Check
```bash
# Human-readable report:
antios release check

# Skip slow tests for fast pre-flight check:
antios release check --skip-tests

# Machine-readable JSON for CI pipelines:
antios release check --json
```

### Release Notes Generation
```bash
# Generate notes for current version:
antios release notes

# Generate notes for specific version:
antios release notes --version 2.0.0-beta.1
```

---

## 3. Continuous Integration Pipeline (`.github/workflows/ci.yml`)

The repository includes a matrix CI pipeline testing across:
- **Operating Systems**: `ubuntu-latest`, `windows-latest`
- **Python Versions**: `3.8`, `3.9`, `3.10`, `3.11`, `3.12`
- **Validation Steps**:
  1. Zero-dependency test execution: `python tests/run_all.py`
  2. Editable package installation: `pip install -e ".[dev]"`
  3. Pytest suite execution: `pytest`
  4. Unified CLI diagnostic verification: `antios version` and `antios doctor`

---

## 4. Maintainer Helper Scripts (`scripts/`)

Platform-independent thin wrappers delegating directly to the canonical CLI:

| Windows Script | POSIX Script | Target Action |
| :--- | :--- | :--- |
| `scripts/test.bat` | `scripts/test.sh` | Run master test suite (`tests/run_all.py`) |
| `scripts/verify.bat` | `scripts/verify.sh` | Run `antios verify` |
| `scripts/release-check.bat` | `scripts/release-check.sh` | Run `antios release check` |
| `scripts/release.bat` | `scripts/release.sh` | Generate release notes |
| `scripts/install.bat` | `scripts/install.sh` | Run `antios install` |
| `scripts/update.bat` | `scripts/update.sh` | Run `antios update` |
| `scripts/rollback.bat` | `scripts/rollback.sh` | Run `antios rollback` |
| `scripts/clean.bat` | `scripts/clean.sh` | Clean pycache and pytest caches |
