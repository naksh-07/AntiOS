# AntiOS Documentation Index (`docs/INDEX.md`)

Welcome to the definitive documentation map for **AntiOS** (Agent-Native Engineering OS for Google Antigravity). This portal is structured for progressive disclosure to help both human developers and autonomous AI agents navigate the framework deterministically without exploration amnesia.

---

## 1. Executive Entrypoints & Core Laws
- [README](../README.md) — Product overview, quick start, architecture summary, and mission.
- [Master Source of Truth](../ANTIOS_SOURCE_OF_TRUTH.md) — Canonical authority hierarchy and precedence model (Phases 1–42 consolidated).
- [Universal Constitution](../ANTIOS_CONSTITUTION.md) — The 7 non-negotiable engineering invariants (Protected zones, Same Change Set, etc.).
- [Master Architecture Specification (v1.0.0-GA)](../ANTIOS_V1.md) — Canonical 4-tier model, 7 subsystems, 34 core modules.
- [Architectural Decision Register](../DECISION_REGISTER.md) — Complete consensus history of all architectural decisions (ADR 01–35).
- [Contributing Guide](../CONTRIBUTING.md) — Engineering standards, Same Change Set policy, and test validation.

## 2. Architecture & Subsystems (`docs/architecture/`)
- [System Architecture Overview](architecture/OVERVIEW.md) — High-level system architecture, subsystem interaction map, and data flows.
- [Canonical Component Model](architecture/COMPONENT_MODEL.md) — 34 core Python modules across all 7 subsystems.
- [Responsibility Boundary Matrix](architecture/RESPONSIBILITY_BOUNDARY.md) — 4-tier demarcation (Platform vs. Core vs. Adapter vs. Target).
- [Core vs. Adapter Demarcation](architecture/CORE_VS_ADAPTER.md) — Universal framework core invariants vs. project-specific configuration.
- [Capability Matrix](architecture/CAPABILITY_MATRIX.md) — 18-layer capability hierarchy and resolution mechanics.
- [Certification Matrix](architecture/CERTIFICATION_MATRIX.md) — Formal certification specifications (C-01 to C-50).
- [Skill Architecture Specification](architecture/SKILL_ARCHITECTURE.md) — Token-bounded skills, shallow delegation depth (<= 2).
- [Task State & Memory Model](architecture/STATE_MODEL.md) — 3-tier state hierarchy (Working Memory, Episodic, Procedural).
- [Verification Model & Test Ratchet](architecture/VERIFICATION_MODEL.md) — Dynamic runner discovery, fail-closed stop gates, and verdicts.
- [Platform Hook Security Model](architecture/HOOK_SECURITY_MODEL.md) — PreToolUse containment, process confinement, and immutability.
- [Rejected Architecture Patterns](architecture/REJECTED_ARCHITECTURE.md) — Formally rejected designs (vector DBs, AST regex, custom daemons).

## 3. Agent Operations, Skills & Workflows (`.agents/`)
- [Global Agent Constitution](AGENTS.md) — Strict operating constraints for autonomous agents in AntiOS workspaces.
- [Active Context Ledger](ACTIVE_CONTEXT.md) — Bounded working memory tracking active status and next actions (<= 60 lines).
- [Validated Project Lessons](LESSONS.md) — Cross-session lessons and distilled procedural memory.
- **Canonical Agent Skills** (`.agents/skills/`):
  - [antios-engineer](../.agents/skills/antios-engineer/SKILL.md) — Universal engineering workflow policy skill (Plan, Act, Consolidate).
  - [antios-verifier](../.agents/skills/antios-verifier/SKILL.md) — Maker-Checker independent verification audit contract.
  - [antios-debug](../.agents/skills/antios-debug/SKILL.md) — 5-step systematic root-cause debugging procedure.
  - [antios-adapt-project](../.agents/skills/antios-adapt-project/SKILL.md) — Universal project discovery and adapter configuration.
- **Standard Operating Workflows** (`.agents/workflows/`):
  - [Workflows SOP Catalog](../.agents/workflows/README.md) — Lifecycle mapping and workflow selection matrix.
  - [FEATURE](../.agents/workflows/FEATURE.md) | [BUG](../.agents/workflows/BUG.md) | [REFACTOR](../.agents/workflows/REFACTOR.md) | [INVESTIGATION](../.agents/workflows/INVESTIGATION.md) | [DOCUMENTATION](../.agents/workflows/DOCUMENTATION.md) | [RELEASE_MAINTENANCE](../.agents/workflows/RELEASE_MAINTENANCE.md)

## 4. Technical Reference & Guides
- [Universal Project Adoption Guide](guides/ADOPT_ANTIOS.md) — Step-by-step onboarding of unfamiliar repositories into AntiOS governance.
- [Project Adapter Guide](guides/PROJECT_ADAPTER.md) — Declarative adapter configuration schema (`antios.config.json`).
- [Command Line Interface Reference](reference/CLI.md) — Reference for all 8 deterministic CLI tools in `framework/scripts/tools/`.
- [Configuration Reference](reference/CONFIGURATION.md) — Complete specification of `antios.config.json` options.
- [Tool, Provider & MCP Policy](reference/MCP_POLICY.md) — 6-tier preference hierarchy and 8 canonical MCP justification rules.
- [AntiOS Failure Taxonomy](reference/FAILURE_TAXONOMY.md) — Deterministic vs. agent failure classification and mitigations.
- [Testing & Verification Guide](operations/TESTING.md) — Test suite architecture, 447 tests across 62 modules, and commands.
- [Security Architecture & Threat Model](SECURITY.md) — Process confinement, protected zone immutability, and boundary rules.

## 5. Historical Archive & Research (`reports/archive/`)
- [Archive Master Index](../reports/archive/INDEX.md) — Overview of historical evolution and archival structure.
- [Phase Reports Index](../reports/archive/phases/INDEX.md) — Historical reports detailing Phases 1–42 development progression.
- [Original Research Archive](../reports/archive/research/INDEX.md) — Prior art evaluations, single-idea studies, and foundational blueprints.
- [Prototype Experiments](../reports/archive/prototype/PROTOTYPE_TEST_RESULTS.md) — Early empirical feasibility tests and benchmarks.
