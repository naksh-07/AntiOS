# AntiOS Release Engineering & Publishing Guide

This document defines the canonical release lifecycle, gates, and procedures for AntiOS.

---

## 1. Canonical Release Lifecycle

Every release of AntiOS follows an immutable, sequential 7-stage lifecycle:

```
1. DEVELOPMENT  ──> Feature / bugfix development under Same Change Set policy
        │
2. TEST         ──> Full test suite execution (tests/run_all.py, 100% pass)
        │
3. CERTIFY      ──> Verification of 20 canonical invariants and doctor health
        │
4. TAG          ──> Annotated Git tag creation (e.g. v2.0.0-beta.1)
        │
5. RELEASE      ──> GitHub Release publication with verified notes
        │
6. VERIFY       ──> Post-release installation verification in a clean sandbox
        │
7. ANNOUNCE     ──> Release distribution to developers and agents
```

---

## 2. Release Channels

AntiOS supports four formal release channels:

| Channel | Format | Audience | Stability |
| :--- | :--- | :--- | :--- |
| **stable** | `MAJOR.MINOR.PATCH` (e.g. `2.0.0`) | Production projects | Maximum stability, zero breaking changes |
| **rc** | `MAJOR.MINOR.PATCH-rc.N` (e.g. `2.0.0-rc.1`) | Pre-release validation | Feature complete; bugfixes only |
| **beta** | `MAJOR.MINOR.PATCH-beta.N` (e.g. `2.0.0-beta.1`) | Early adopters & feedback | Product-ready beta; experimental features |
| **development**| `git rev-parse --short HEAD` | Core contributors | Untagged branch builds |

---

## 3. Pre-Flight Release Validation Gate (`antios release check`)

Before tagging or publishing any release, the deterministic release pre-flight validator **MUST** pass with zero blocking errors:

```bash
antios release check
# Or machine-readable:
antios release check --json
```

### Verification Checks:
1. **Version Alignment**: `pyproject.toml`, `framework/core/version.py`, and `framework/core/manifest.py` must declare the identical target version.
2. **Git Working Tree Cleanliness**: Working tree must have zero uncommitted modifications.
3. **Git Tag Uniqueness**: The target tag must not already exist on a different commit.
4. **Certification Artifacts**: All 5 Phase 99–101 certification artifacts must be present:
   - `FINAL_CERTIFICATION.md`
   - `ARCHITECTURE_FREEZE.md`
   - `INVARIANT_REGISTRY.md`
   - `PRODUCTION_READINESS.md`
   - `UNIVERSAL_ADOPTION.md`
5. **CHANGELOG.md Entry**: `CHANGELOG.md` must contain an entry for the target version.
6. **20 Canonical Invariants**: All invariants `INV-01` through `INV-20` verified.
7. **Active Context Budget**: `docs/ACTIVE_CONTEXT.md` must remain strictly $\le 60$ lines (`INV-09`).
8. **Test Suite Execution**: `python tests/run_all.py` must exit code 0 with 100% pass rate.

---

## 4. Release Preparation Workflow

### Step 1: Execute Pre-Flight Validation
```bash
python -m framework.cli release check
```

### Step 2: Assemble Release Notes
```bash
python -m framework.cli release notes > RELEASE_NOTES.md
```

### Step 3: Create Annotated Git Tag
```bash
git tag -a v2.0.0-beta.1 -m "AntiOS 2.0.0-beta.1 Productization & Beta Release"
```

### Step 4: Publish GitHub Release (via gh CLI or GitHub MCP)
```bash
gh release create v2.0.0-beta.1 --prerelease --title "AntiOS 2.0.0-beta.1" --notes-file RELEASE_NOTES.md
```

### Step 5: Verify in Fresh Sandbox
```bash
python -m framework.cli install --path /tmp/test-project
python -m framework.cli verify --path /tmp/test-project
python -m framework.cli remove --path /tmp/test-project
```
