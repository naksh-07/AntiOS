# Changelog

All notable changes to AntiOS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0-beta.1] - 2026-09-06

### Added
- **Unified Product CLI (`antios`)**: First-class command-line interface registered via `pyproject.toml` console scripts (`antios version`, `antios status`, `antios doctor`, `antios install`, `antios update`, `antios rollback`, `antios repair`, `antios remove`, `antios adapt`, `antios verify`, `antios issue`, `antios release`).
- **Authoritative Semantic Versioning**: Created `framework/core/version.py` defining single authoritative SemVer source of truth with formal release channels (`stable`, `beta`, `rc`, `development`), SemVer comparison logic, and dynamic Git short SHA/dirty resolution.
- **Pre-Update Snapshotting & Rollback**: Added automated instance snapshotting in `.antios/backups/` prior to mutations and added `antios rollback` to restore prior framework states without touching user application source code.
- **Diagnostic Doctor (`antios doctor`)**: First-class diagnostic engine inspecting installation, manifest validity, runtime closure, toolchain availability, Git working tree cleanliness, and 10 canonical drift domains with automated secret/credential redaction.
- **Compact Operational Status (`antios status`)**: Concise operational health card providing instant visibility into version, installation, adaptation, drift, proofs, and update availability.
- **Git Capability Abstraction**: Deterministic local Git CLI wrapper (`framework/core/git_capability.py`) distinguishing read-only inspections from guarded mutating operations.
- **GitHub Capability & Freeze Gatekeeper**: External capability engine (`framework/core/github_capability.py`) integrating `gh` CLI and GitHub MCP with issue deduplication, evidence capture, and Architecture Freeze gating for feature requests.
- **Automated Release Pre-Flight Gate (`antios release check`)**: Deterministic release validator checking tree cleanliness, version alignment, test suite pass rate, invariant registry compliance, and certification integrity.
- **CI Matrix & Maintainer Scripts**: Added `.github/workflows/ci.yml` matrix pipeline across Python 3.8–3.12 on Linux/Windows and cross-platform maintainer wrapper scripts in `scripts/`.
- **End-to-End Beta Proving Ground**: Automated 14-step end-to-end lifecycle verification test (`tests/test_beta_productization_e2e.py`) in an isolated sandbox.

### Changed
- `pyproject.toml`: Upgraded version to `2.0.0-beta.1`, migrated to SPDX `license = "MIT"`, configured setuptools package discovery with `include = ["framework*"]`, and registered console script `antios`.
- `framework/core/installation.py`: Added version-aware installation with silent downgrade prevention (requiring explicit `--force-downgrade`), snapshot backup generation, rollback execution, and residual cleanup verification.
- `framework/core/manifest.py`: Synchronized version constants to import directly from `framework.core.version`.
- `framework/core/__init__.py`: Updated docstrings and exposed `__version__ = ANTIOS_VERSION`.
- `framework/core/drift_health.py`: Enhanced test ownership drift detection to respect project-configured test runners in `antios.config.json`.
- `tests/run_all.py`: Integrated new productization test suites into the master test runner.

### Fixed
- Fixed setuptools flat-layout multi-package discovery error preventing package installation and pytest execution.
- Fixed Windows terminal UnicodeEncodeError by using ASCII-safe status indicators in CLI reports.
- Corrected test runner ownership drift false-positive on adopted projects without `tests/run_all.py`.

### Security
- Added automated secret redaction filter in `framework/core/doctor.py` scrubbing GitHub tokens (`gho_*`), API keys, and credential strings from diagnostic outputs.
- Enforced strict fail-closed downgrade protection preventing accidental downgrades without explicit `--force-downgrade`.

---

## [2.0.0] - 2026-09-06

### Added
- Phase 99: Final System Certification Audit (`certification_audit.py`, 12 areas, cards <= 25 lines).
- Phase 100: Fresh Project Universal Adoption (`universal_adoption.py`, 19 steps, 0 Core mutations).
- Phase 101: Production Readiness & Architecture Freeze (`architecture_freeze.py`, INV-01..20, 15 dimensions).
- Ratified 20 canonical invariants (`INV-01` through `INV-20`) in `INVARIANT_REGISTRY.md`.
- Locked `ARCHITECTURE_FREEZE.md` defining permitted maintenance categories and permanent architectural bans.
- Zero-dependency master test runner `tests/run_all.py` passing 900/900 tests (100% pass rate).

### Changed
- Consolidated Phases 1–101 into canonical architecture specification.
- Ratified ADRs 01 through 85 in `DECISION_REGISTER.md`.

---

## Known Issues
- GitHub remote capabilities require local `gh` CLI or GitHub MCP authentication; offline local Git operations remain authoritative.
- Rollback is scoped to AntiOS-generated assets and will not revert uncommitted user application code.
