# AntiOS

**Universal, Domain-Agnostic Agent-Native Engineering OS for Google Antigravity**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-447%20passed%20(100%25)-brightgreen.svg)](tests/run_all.py)
[![Dependencies](https://img.shields.io/badge/dependencies-zero%20(stdlib%20only)-blueviolet.svg)](ANTIOS_CONSTITUTION.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/version-v1.0.0--GA-green.svg)](ANTIOS_V1.md)

---

## What is AntiOS?

Autonomous AI coding agents operating in software repositories frequently suffer from **context drift, boundary violations, unverified code claims, broken changesets, and tool sprawl**. 

**AntiOS** is an Agent-Native Engineering Operating System that wraps repository interactions with deterministic, compile-free, zero-dependency engineering governance. Operating seamlessly within Google Antigravity, AntiOS transforms autonomous LLM coding agents into disciplined, auditable, and reliable software engineers.

It provides an integrated operating environment:
```
Antigravity Platform
        ?
   AntiOS Core
        ?
 Project Adapter
        ?
  Target Project
```

---

## Key Capabilities

- **Fail-Closed Security Guards**: Native `PreToolUse` hook interception protects framework assets (`.agents/`, `framework/`) and project domain cores from unauthorized file modifications.
- **Physical Process Stop Gate**: Agents cannot conclude tasks based on verbal claims. The Stop Gate executes physical test runners and verifies working tree hygiene before granting task completion.
- **Same Change Set Discipline**: Enforces that functional code changes are accompanied by tests and documentation within the same atomic change set.
- **Maker-Checker Independent Verification**: High-risk tasks mandate independent audit by an unbiased, fresh-context verifier subagent.
- **Universal Project Adapter**: Declarative `antios.config.json` configuration binds any software stack (Python, TypeScript, Rust, Go, polyglot) to AntiOS without modifying core code.
- **Deterministic Repository Wayfinding**: Sub-millisecond navigation tool resolves task intent to owning subsystems, test suites, and blast radius.
- **Strict 6-Tier Tooling & MCP Policy**: Prioritizes local, deterministic tools over unvetted Model Context Protocol servers.
- **Zero Third-Party Dependencies**: Pure Python 3.8+ standard library. Zero pip dependencies required.

---

## Quick Start: Adopting AntiOS

Adopting AntiOS for any repository takes under two minutes:

```bash
# 1. Inspect target repository traits and runners
python framework/scripts/tools/inspect_repo.py /path/to/repo

# 2. Preview the proposed adapter configuration (dry run)
python framework/scripts/tools/adapt_project.py /path/to/repo --dry-run

# 3. Apply the adapter configuration (creates antios.config.json)
python framework/scripts/tools/adapt_project.py /path/to/repo --apply

# 4. Verify repository wayfinding and tool routing
python framework/scripts/tools/navigate_repo.py --repo-root /path/to/repo --list

# 5. Run the AntiOS test suite
python tests/run_all.py
```

For detailed guidance, see the [Universal Project Adoption Guide](docs/guides/ADOPT_ANTIOS.md).

---

## Canonical Documentation

Explore the full documentation portal in [`docs/INDEX.md`](docs/INDEX.md):

| Category | Document | Description |
| :--- | :--- | :--- |
| **Portal** | [`docs/INDEX.md`](docs/INDEX.md) | Definitive navigation portal for humans and agents |
| **Architecture** | [`ANTIOS_V1.md`](ANTIOS_V1.md) | Canonical Master Architecture Specification (v1.0.0-GA) |
| **Architecture** | [`docs/architecture/OVERVIEW.md`](docs/architecture/OVERVIEW.md) | 4-tier model, 7 subsystems, and 34-module model |
| **Architecture** | [`docs/architecture/CAPABILITY_MATRIX.md`](docs/architecture/CAPABILITY_MATRIX.md) | Core capability catalog and taxonomy |
| **Architecture** | [`docs/architecture/CERTIFICATION_MATRIX.md`](docs/architecture/CERTIFICATION_MATRIX.md) | 50 canonical certification rules (C-01 to C-50) |
| **Governance** | [`ANTIOS_CONSTITUTION.md`](ANTIOS_CONSTITUTION.md) | Universal non-negotiable axioms and invariants |
| **Governance** | [`ANTIOS_SOURCE_OF_TRUTH.md`](ANTIOS_SOURCE_OF_TRUTH.md) | Definitive system source of truth |
| **Decisions** | [`DECISION_REGISTER.md`](DECISION_REGISTER.md) | Architectural Decision Register (ADR 01–35) |
| **Operations** | [`.agents/skills/`](.agents/skills/antios-engineer/SKILL.md) | Canonical agent skills (`antios-engineer`, `antios-verifier`, etc.) |
| **Guides** | [`docs/guides/ADOPT_ANTIOS.md`](docs/guides/ADOPT_ANTIOS.md) | Step-by-step onboarding guide for any repo |
| **Guides** | [`docs/guides/PROJECT_ADAPTER.md`](docs/guides/PROJECT_ADAPTER.md) | Guide on `antios.config.json` customization |
| **Reference** | [`docs/reference/CLI.md`](docs/reference/CLI.md) | Reference for all 8 deterministic CLI tools |
| **Reference** | [`docs/reference/CONFIGURATION.md`](docs/reference/CONFIGURATION.md) | Field-by-field `antios.config.json` schema reference |
| **Reference** | [`docs/reference/MCP_POLICY.md`](docs/reference/MCP_POLICY.md) | 6-tier tooling hierarchy & MCP justification |
| **Testing** | [`docs/operations/TESTING.md`](docs/operations/TESTING.md) | Test suite catalog, running tests, benchmarks |
| **Contributing**| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution standards and Same Change Set policy |

---

## Deterministic CLI Tools

AntiOS provides 8 standard library CLI tools in `framework/scripts/tools/`:

- `inspect_repo.py` — Inspect repository topology, manifests, and host toolchains.
- `adapt_project.py` — Analyze adaptation requirements and generate `antios.config.json`.
- `navigate_repo.py` — Wayfinding tool resolving task intent to subsystems and test suites.
- `audit_docs.py` — Staleguard Layer 1 documentation reference auditor.
- `check_changeset.py` — Same Change Set integrity evaluator (code + tests + docs).
- `check_worktree.py` — Git working tree conflict inspector.
- `distill_memory.py` — Cross-session lesson distillation and promotion tool.
- `recover_session.py` — Session recovery and state contradiction resolver.

---

## Running Tests

AntiOS includes 447 deterministic automated tests covering all 34 core modules:

```bash
python tests/run_all.py
```

```
======================================================================
AntiOS Master Test Suite
Ran 447 tests in 25.2s
OK (100% passed, 0 failures, 0 errors)
======================================================================
```

---

## License

AntiOS is released under the [MIT License](LICENSE).
