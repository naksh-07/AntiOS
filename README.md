# AntiOS

**Universal, Domain-Agnostic Project Agent OS for Google Antigravity**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1086%20passed%20(100%25)-brightgreen.svg)](tests/run_all.py)
[![Dependencies](https://img.shields.io/badge/dependencies-zero%20(stdlib%20only)-blueviolet.svg)](ANTIOS_CONSTITUTION.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/version-v2.1.0--beta.1-green.svg)](CHANGELOG.md)

---

## What is AntiOS?

Autonomous AI coding agents operating in software repositories frequently suffer from **context drift, boundary violations, unverified code claims, broken changesets, and tool sprawl**. 

**AntiOS** is an Agent-Native Project Operating System that wraps repository interactions with deterministic, compile-free, zero-dependency engineering governance. Operating seamlessly within Google Antigravity, AntiOS transforms autonomous LLM coding agents into disciplined, auditable, and reliable software engineers.

It provides an integrated operating environment:
```
Antigravity Platform
        ▼
   AntiOS Core
        ▼
 Project Adapter
        ▼
   Target Project
```

---

## Product Lifecycle

AntiOS exposes a clear, versioned engineering product lifecycle:

```
INSTALL  ──>  VERIFY  ──>  ADAPT  ──>  USE  ──>  UPDATE  ──>  VERIFY
                                                  │
                                                  ├──> ROLLBACK (if required)
                                                  ├──> REPAIR (if drift occurs)
                                                  └──> REMOVE (when desired)
```

- **INSTALL**: Idempotent installation of runtime guards, manifest, and project intelligence.
- **VERIFY**: Checksum and runtime closure validation ensuring zero source leaks.
- **ADAPT**: Declarative stack discovery and runner mapping in `antios.config.json`.
- **USE**: Disciplined agent engineering with pre-tool interception and stop gates.
- **UPDATE**: Safe, snapshot-backed updates to newer AntiOS revisions.
- **ROLLBACK**: Atomic reversion of AntiOS state without touching user application code.
- **REPAIR**: Conservative drift and missing artifact restoration.
- **REMOVE**: Clean, non-destructive uninstallation preserving project business logic.

---

## Unified Command Line Interface (`antios`)

AntiOS provides a single, first-class console binary `antios` registered via package scripts:

```bash
# 1. Version & System Facts
antios version [--json]

# 2. Compact Operational Health
antios status [--json]

# 3. Comprehensive Diagnostics
antios doctor [--json]

# 4. Project Lifecycle Operations
antios install [--path <DIR>] [--version <V>] [--force-downgrade]
antios adapt [--path <DIR>]
antios verify [--path <DIR>]
antios update [--check] [--version <V>]
antios rollback [--version <V>]
antios repair [--check] [--plan] [--apply]
antios remove [--dry-run]

# 5. Remote Engineering & Release
antios issue triage "<DESCRIPTION>"
antios issue discover "<QUERY>"
antios release check [--json]
antios release notes
```

---

## Quick Start: Adopting AntiOS

Adopting AntiOS for any repository takes under one minute:

```bash
# 1. Install AntiOS into target project
antios install --path /path/to/project

# 2. Verify installation health and runtime closure
antios verify --path /path/to/project

# 3. Adapt target project stack (creates antios.config.json)
antios adapt --path /path/to/project

# 4. Run system diagnostic check
antios doctor --path /path/to/project
```

---

## Canonical Product & Governance Documentation

| Category | Document | Description |
| :--- | :--- | :--- |
| **Changelog** | [`CHANGELOG.md`](CHANGELOG.md) | Release history in Keep a Changelog format |
| **Beta Readiness** | [`BETA_READINESS.md`](BETA_READINESS.md) | Official 2.0.0-beta.1 verification dossier |
| **Release Guide** | [`RELEASE.md`](RELEASE.md) | Release lifecycle, pre-flight gates, and tagging |
| **Release Eng** | [`RELEASE_ENGINEERING.md`](RELEASE_ENGINEERING.md) | Release automation, CI pipeline, and maintainer scripts |
| **Versioning** | [`VERSIONING.md`](VERSIONING.md) | SemVer specification, channels, and compatibility matrix |
| **Installation** | [`INSTALLATION.md`](INSTALLATION.md) | Step-by-step installation options and guarantees |
| **Upgrades** | [`UPGRADING.md`](UPGRADING.md) | Update lifecycle, snapshotting, and migrations |
| **Rollback** | [`ROLLBACK.md`](ROLLBACK.md) | Rollback safety, guarantees, and user code preservation |
| **Troubleshooting**| [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | `antios doctor`, error codes, and drift remediation |
| **Maintenance** | [`MAINTENANCE.md`](MAINTENANCE.md) | Architecture Freeze policy and permitted changes |
| **MCP Policy** | [`MCP_CAPABILITIES.md`](MCP_CAPABILITIES.md) | 8-tier capability matrix and external MCP governance |
| **Architecture** | [`ARCHITECTURE_FREEZE.md`](ARCHITECTURE_FREEZE.md) | Phase 101 locked architecture specification |
| **Invariants** | [`INVARIANT_REGISTRY.md`](INVARIANT_REGISTRY.md) | Ledger of the 20 canonical invariants (`INV-01` to `INV-20`) |
| **Constitution** | [`ANTIOS_CONSTITUTION.md`](ANTIOS_CONSTITUTION.md) | Universal non-negotiable axioms and laws |
| **Decisions** | [`DECISION_REGISTER.md`](DECISION_REGISTER.md) | Architectural Decision Register (ADR 01-86) |

---

## Running Tests

AntiOS includes 920 deterministic automated tests covering all core modules, contracts, safety gates, and beta lifecycles:

```bash
python tests/run_all.py
```

```
======================================================================
AntiOS Master Test Suite
Ran 920 tests in 36.1s
OK (100% passed, 0 failures, 0 errors)
======================================================================
```

Alternatively, run via pytest:
```bash
python -m pytest
```

---

## License

AntiOS is released under the [MIT License](LICENSE).
