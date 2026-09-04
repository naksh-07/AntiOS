# AntiOS Phase 27 — Decision Register (`PHASE27_DECISION_REGISTER.md`)

**Document ID**: `PHASE27_DECISION_REGISTER`  
**Date**: 2026-09-04  
**Author**: AntiOS System Architect  
**Status**: APPROVED ARCHITECTURAL DECISIONS (ADR-09 through ADR-13)  
**Format**: Every decision records `DECISION`, `EVIDENCE`, `ALTERNATIVES`, `WHY SELECTED`, `CONSEQUENCES`, and `REVERSIBILITY`.  

---

## DECISION 09 (ADR-09): Deterministic Component Wayfinding over Vector Databases & Regex AST

- **DECISION**: AntiOS implements repository wayfinding and locality indexing via deterministic, file-backed inverted indices and prefix tree mapping (`framework/core/wayfinding.py`). Vector databases (Chroma, Pinecone, Qdrant) and regex-based AST dependency parsers are permanently rejected.
- **EVIDENCE**: 
  1. Single-Idea Repo 03 audit (`RavByte-AI/agent-memory-system`) proved regex-based AST parsers miss dynamic imports, produce dead caller graphs, and emit false confidence.
  2. Research findings across Phases 6, 10, and 21 demonstrated that vector databases suffer from temporal blindness (retrieving obsolete code based on fuzzy semantic similarity), add heavy dependencies (C++ compilation, SQLite locks), and lack Git diffability.
  3. Deterministic path prefix and keyword matching executes in $<20$ms, returns 100% reproducible results, and requires zero third-party dependencies.
- **ALTERNATIVES**:
  - Embedded vector database with sentence-transformer embeddings.
  - Custom regex-based AST parser.
  - Live language server protocol (LSP) indexing daemon.
- **WHY SELECTED**: Maximizes speed, determinism, portability across all OS environments (Windows, Linux, macOS), and operates completely offline with zero API token cost.
- **CONSEQUENCES**:
  - Requires declarative component declarations or heuristic directory scanning.
  - Wayfinding resolution is strictly predictable and testable with standard unit tests.
- **REVERSIBILITY**: High; isolated to `framework/core/wayfinding.py`.

---

## DECISION 10 (ADR-10): Agent-Oriented Subsystem Manifests and Layer-1 Syntactic Reference Drift Auditing

- **DECISION**: AntiOS establishes a machine/agent-oriented Subsystem Manifest standard (`framework/core/subsystem.py`) and implements Staleguard Layer 1 Syntactic Reference Auditing (`framework/core/docaudit.py`). LLM-as-a-judge documentation checkers (e.g. `driftee-ai/drift`) are permanently rejected.
- **EVIDENCE**:
  1. Single-Idea Repo 07 audit (`Arthur920/Staleguard` vs `driftee-ai/drift`) proved that Staleguard Layer 1 scans backticked paths and markdown references against physical disk in $\sim 1.2$s with 0% false positives.
  2. In contrast, LLM drift checkers take 30–60s per turn, cost hundreds of tokens, hallucinate semantic conflicts, and are vulnerable to prompt injection.
  3. Machine-oriented subsystem manifests directly solve the agent's "Where should I look?" problem by pairing entrypoints, test commands, invariants, and dependencies in a compact schema.
- **ALTERNATIVES**:
  - LLM-based documentation evaluator.
  - Pure prose READMEs without structured machine headers.
  - Relying exclusively on human PR review for documentation freshness.
- **WHY SELECTED**: Provides instant, zero-cost, zero-hallucination verification that all documentation links and cited code files physically exist on disk.
- **CONSEQUENCES**:
  - Broken file paths or hallucinated test commands in documentation fail the Stop Gate ratchet.
  - Agents can reliably consume subsystem documentation without reading full prose documents.
- **REVERSIBILITY**: High; isolated to `framework/core/subsystem.py` and `framework/core/docaudit.py`.

---

## DECISION 11 (ADR-11): Three-Tier Tooling Hierarchy: Python Scripts First, Decoupled MCP Bridge

- **DECISION**: AntiOS strictly enforces the tooling hierarchy:
  $$\text{NATIVE ANTIGRAVITY} \;\succ\; \text{ANTI OS SCRIPT / CLI} \;\succ\; \text{MCP}$$
  Internal framework logic remains 100% Python standard library. Local deterministic CLI scripts (`framework/scripts/tools/*.py`) executed via `run_command` are the primary tool interface. An MCP server is defined strictly as an optional, decoupled protocol adapter (`antios-mcp-server`) for IDEs that require stdio JSON-RPC palettes.
- **EVIDENCE**:
  1. Phase 8 and Phase 10 audits proved that local CLI tools executed via `run_command` are 20x faster, consume zero API tokens, work offline, and have no background socket/port collision vulnerabilities.
  2. Embedded background servers (such as `obra/superpowers` `server.cjs`) create orphan process leaks and port collisions on Windows.
  3. Python standard library ensures instant execution across any system with zero build step.
- **ALTERNATIVES**:
  - Rebuilding all AntiOS tools exclusively as an MCP server.
  - Spawning a persistent background daemon for AntiOS services.
- **WHY SELECTED**: Eliminates background process thrashing, guarantees 100% offline functionality, and keeps AntiOS Core completely independent of external protocol libraries.
- **CONSEQUENCES**:
  - Agents interact with AntiOS via native tools and fast CLI invocations.
  - External MCP clients can optionally attach without altering core governance.
- **REVERSIBILITY**: High; CLI scripts and MCP adapters wrap core python functions without modifying core logic.

---

## DECISION 12 (ADR-12): Automated Subsystem Discovery & Declarative Wayfinding in Project Adapter

- **DECISION**: Static project discovery (`framework/core/discovery.py`) is extended to automatically infer subsystem boundaries, component directories, entrypoints, and test pairings during onboarding, emitting them as proposed declarations in `AdaptationProposal`. `antios.config.json` stores these as a declarative `components` registry.
- **EVIDENCE**:
  1. Human developers rarely author extensive component catalogs manually. Requiring manual authoring creates an adoption blocker.
  2. Standard software architectures exhibit predictable directory conventions (`src/{name}`, `tests/test_{name}`, `pkg/{name}`, `apps/{name}`).
  3. Automated discovery followed by declarative adapter storage preserves the 4-tier model: AntiOS Core provides universal discovery logic; the project adapter records the project-specific component map.
- **ALTERNATIVES**:
  - Requiring developers to write `subsystem.json` files by hand before AntiOS works.
  - Dynamically rescanning the entire repository on every user turn.
- **WHY SELECTED**: Enables zero-configuration onboarding while maintaining declarative, version-controlled predictability.
- **CONSEQUENCES**:
  - Running `adapt_project.py` automatically discovers components and populates `antios.config.json`.
  - Developers can review, refine, or override discovered components declaratively.
- **REVERSIBILITY**: High; governed by adapter configuration schema.

---

## DECISION 13 (ADR-13): Explicit "LOCATE" Stage & Investigation Delegation in Agent Lifecycle

- **DECISION**: The AntiOS task lifecycle is formally augmented with a mandatory **`LOCATE`** stage between `UNDERSTAND` and `PLAN`:
  $$\text{UNDERSTAND} \;\longrightarrow\; \text{LOCATE} \;\longrightarrow\; \text{PLAN} \;\longrightarrow\; \text{ACT} \;\longrightarrow\; \text{TEST} \;\longrightarrow\; \text{VERIFY} \;\longrightarrow\; \text{REMEMBER} \;\longrightarrow\; \text{RECOVER}$$
  For complex or unfamiliar tasks, agents may dispatch a scoped Investigation Specialist subagent under the Shallow Depth Law (depth $\le 2$) to execute read-only reconnaissance before authoring code diffs.
- **EVIDENCE**:
  1. The "Change This Button" failure mode occurs when agents guess where code lives and begin editing before locating the true owning subsystem.
  2. Shallow Depth Law ($\le 2$) proven in Phases 7–10 prevents coordination latency and token waste.
  3. Requiring an explicit locality resolution card in `ACTIVE_CONTEXT.md` prevents hallucinations and focuses changes strictly within the identified subsystem blast radius.
- **ALTERNATIVES**:
  - Allowing agents to jump directly from intake to code editing.
  - Recursive multi-agent investigation swarms.
- **WHY SELECTED**: Enforces deliberate cognitive orientation before code mutation, minimizing irrelevant file inspections and preventing regressions in unrelated subsystems.
- **CONSEQUENCES**:
  - `antios-engineer` and `antios-debug` skills require checking subsystem locality before planning.
  - `ACTIVE_CONTEXT.md` records the targeted subsystem and covering tests.
- **REVERSIBILITY**: High; governed by skill directives and lifecycle state machine metadata.
