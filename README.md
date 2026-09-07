# AntiOS

**Agent-Native Project Environment Compiler and Governance Plane for Google Antigravity**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-1086%20passed%20(100%25)-brightgreen.svg)](tests/run_all.py)
[![Dependencies](https://img.shields.io/badge/dependencies-zero%20(stdlib%20only)-blueviolet.svg)](INVARIANT_REGISTRY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Stage 0](https://img.shields.io/badge/status-Stage%200%20(Architecture%20Reconstruction)-orange.svg)](docs/architecture/MIGRATION_PLAN.md)

---

## 1. What AntiOS IS

> **AntiOS makes the project legible, navigable, stateful, verifiable, and continuously maintainable for an AI agent.**

AntiOS is an **Agent-Native Project Environment Compiler and Governance Plane for Google Antigravity**. It compiles an arbitrary software repository into a low-noise, progressively disclosed, verifiable engineering environment by generating native Antigravity configurations (`.agents/hooks.json`, `.agents/routes.json`, `.agents/skills/`, and `antios.config.json`).

### Conceptual Pipeline
```
TARGET PROJECT (Source of Truth)
      ↓
PROJECT ENVIRONMENT COMPILER (antios compile)
      ↓
Agent-Native Project Environment (.agents/routes.json, hooks, rules, skills)
      ↓
Antigravity Native Execution (External LLM Loop & Language Server)
```

---

## 2. What AntiOS IS NOT

To prevent scope creep and architectural amnesia, AntiOS maintains strict negative boundaries:

- ❌ **NOT an agent runtime**: It does not execute language models, schedule LLM worker loops, or manage prompt turns.
- ❌ **NOT an Antigravity replacement**: Google Antigravity remains the sole execution substrate.
- ❌ **NOT a mandatory workflow tax**: Simple tasks execute SOLO with zero ritual or multi-agent ceremony.
- ❌ **NOT a background daemon**: Zero background watcher processes (`watchdog`, `inotify`, polling services). All operations are synchronous hook events or static compilations.
- ❌ **NOT a vector / dense RAG platform**: Zero embedding models or vector databases (`chromadb`, FAISS). Navigation is deterministic via Subsystem Route Maps and AST symbol outlines.
- ❌ **NOT a second coding-agent runtime**: Never spawns competing agent runtimes within the Antigravity sandbox.

---

## 3. Four-Zone Ownership Boundaries

$$\text{SOURCE} \neq \text{INSTANCE} \neq \text{PROJECT} \neq \text{ANTIGRAVITY}$$

1. **AntiOS Owns**: The Project Environment Compiler, Subsystem Route Maps, physical lifecycle hooks (`PreToolUse`, `Stop`), 6-Dimension MVR verification engine, and epistemic memory schemas.
2. **Antigravity Owns**: The agent execution loop, LLM context compaction, conversation SQLite databases, transcript streaming, native tool execution, and subagent process management.
3. **Target Project Owns**: Application source code, physical build manifests (`pyproject.toml`, `Cargo.toml`, `package.json`), physical test suites, Git repository tree, and declarative configuration (`antios.config.json`).
4. **Experience Plane (System B) Owns**: Centralized developer telemetry store (`experience.db`). Completely isolated from project code; data flows strictly one-way (A $\to$ B) via sanitized NDJSON.

---

## 4. Repository Structure & Source Boundaries

```
AntiOS/
├── .agents/                 # Native Antigravity integration
│   ├── hooks.json           # Platform lifecycle hooks (PreToolUse, Stop)
│   └── skills/              # Native procedural skills (antios, antios-engineer, antios-verifier...)
│
├── framework/               # AntiOS Core & Compiler
│   ├── cli.py               # Unified product CLI entrypoint (antios)
│   ├── core/                # Governance, discovery, verification, and telemetry engines
│   ├── scripts/             # Hook entrypoint scripts and deterministic CLI tools
│   └── templates/           # Clean runtime & skill templates for target compilation
│
├── tests/                   # Zero-dependency test suite
│   ├── run_all.py           # Canonical master test runner (1,086 tests across 140 modules)
│   ├── fixtures/            # 17 multi-lingual project archetypes (Rust, TS, Go, Python...)
│   └── test_*.py            # Unit, integration, adversarial, and benchmark test suites
│
├── docs/                    # Authoritative engineering documentation
│   ├── architecture/        # Architecture 3.0, migration plan, migration matrix, runtime audit
│   ├── research/            # Foundational Research 1–4 monographs & empirical evidence
│   ├── guides/              # Adoption & project adapter guides
│   ├── operations/          # Testing guide & operational runbooks
│   └── reference/           # CLI, configuration, failure taxonomy, and MCP policy
│
├── scripts/                 # Convenience wrappers (test.bat/sh, clean.bat/sh, verify.bat/sh)
├── antios.config.json       # Sovereign repository adapter configuration
└── pyproject.toml           # Package definition and CLI entrypoint
```

---

## 5. Where Key Resources Live

| Resource Area | Path | Description |
| :--- | :--- | :--- |
| **Source Code** | [`framework/`](framework/) | Compiler, CLI, governance primitives, and hook scripts |
| **Test Suites** | [`tests/`](tests/) | Canonical regression suites and multi-stack fixtures |
| **Architecture** | [`docs/architecture/`](docs/architecture/) | [AntiOS 3.0 Architecture](docs/architecture/ANTIOS_3_ARCHITECTURE.md) & [Migration Plan](docs/architecture/MIGRATION_PLAN.md) |
| **Research Evidence** | [`docs/research/`](docs/research/) | Foundational Research 1–4 monographs and empirical benchmarks |
| **Constitutional Invariants** | [`INVARIANT_REGISTRY.md`](INVARIANT_REGISTRY.md) | 20 non-negotiable platform and engineering invariants |
| **Decision History** | [`DECISION_REGISTER.md`](DECISION_REGISTER.md) | Complete consensus history of Architectural Decision Records |

---

## 6. How to Run Validation

AntiOS enforces 100% deterministic test execution using standard library Python (zero external test dependencies required).

### Canonical Test Command
```bash
# Execute master test suite (140 modules, 1,086 tests)
python tests/run_all.py
```

### Pytest Execution
```bash
python -m pytest
```

### Diagnostics & Doctor
```bash
python -m framework.cli verify
python -m framework.cli doctor
```

---

## 7. Current Implementation Status

**Current Phase**: **Stage 0 — Architecture Reconstruction & Project Hygiene**
- Research 1–4 evidence synthesis: **COMPLETE**
- Canonical 4-plane boundary formalization: **COMPLETE**
- Component migration matrix & legacy runtime audit: **COMPLETE**
- Stage 1 Compiler implementation: **NOT STARTED** (Begins in Stage 1)

---

## 8. Strictly Protected Boundaries (What NOT to Touch)

1. **Target Project Sovereignty**: AntiOS never injects framework code into target repositories. Target projects receive zero-dependency standard-library runtime scripts.
2. **`sandbox/StudyLab` & StudySourceCore**: Strictly protected test proving ground. Never inspect, modify, clone, or integrate StudyLab or StudySourceCore.
3. **Antigravity Execution Primitives**: Never attempt to override or emulate native Antigravity scheduling, compaction, or subagent dispatch.
4. **System A / System B Firewall**: Target projects must never read or depend on the central experience database (`experience.db`).
