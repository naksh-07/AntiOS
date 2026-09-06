# AntiOS Versioning Specification

This document defines the Semantic Versioning contract, authority hierarchy, and compatibility rules for AntiOS.

---

## 1. Authoritative Version Source

AntiOS enforces a **Single Source of Truth** for version declarations:

```
framework/core/version.py (ANTIOS_VERSION = "2.0.0-beta.1")
             │
             ├──> pyproject.toml ([project] version = "2.0.0-beta.1")
             ├──> framework/core/manifest.py (CURRENT_ANTIOS_VERSION)
             ├──> framework/core/__init__.py (__version__)
             ├──> antios version CLI command
             └──> Instance .antios/manifest.json
```

**Rule**: No component or documentation file may declare a version conflicting with `framework/core/version.py`. Any discrepancy is flagged as a blocking error during `antios release check`.

---

## 2. Semantic Versioning Format

AntiOS strictly adheres to [SemVer 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

### Format Elements:
- **MAJOR**: Incompatible architectural shifts (e.g. AntiOS 3.0).
- **MINOR**: Backward-compatible new capabilities, project adapters, or workflow tooling.
- **PATCH**: Backward-compatible bugfixes, security patches, and documentation corrections.
- **PRERELEASE**: Pre-release tags:
  - `-alpha.N`: Internal developer builds
  - `-beta.N`: Beta preview builds for public testing
  - `-rc.N`: Release candidates for final validation

---

## 3. Version Compatibility Matrix

AntiOS maintains strict backward compatibility within the `2.x` line:

| AntiOS Version | Python Required | Git Required | Adapter Schema | Antigravity Platform |
| :--- | :--- | :--- | :--- | :--- |
| `2.0.0` | `Python >= 3.8` | `Git >= 2.20` | `1.0` | Antigravity 2.0+ |
| `2.0.0-beta.1` | `Python >= 3.8` | `Git >= 2.20` | `1.0` | Antigravity 2.0+ |
| `2.x.x` | `Python >= 3.8` | `Git >= 2.20` | `1.0` | Antigravity 2.0+ |

### Compatibility Rules:
1. **Adapter Schema Version (`1.0`)**: Represents the declarative schema of `antios.config.json`. Stays at `1.0` across `2.x` to prevent breaking existing user project configurations.
2. **Project-Side Isolation**: Target projects adapted by AntiOS record the generating version in `.antios/manifest.json`. Projects remain functional even if the AntiOS source repository is updated.
3. **Downgrade Safety**: Downgrades are blocked by default to prevent silent regression of project metadata. Explicit intent (`--force-downgrade`) is required.

---

## 4. Querying Version Information

```bash
# Human-readable output:
antios version

# Machine-readable JSON output:
antios version --json
```

Output includes:
- AntiOS version & channel
- Manifest schema version & adapter schema version
- Current Git revision (short SHA and `-dirty` flag if uncommitted changes exist)
- Python runtime version & platform
- Prerelease status
- Compatibility matrix facts
