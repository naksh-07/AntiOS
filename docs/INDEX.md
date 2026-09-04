# AntiOS Documentation Portal (`docs/INDEX.md`)

Welcome to the definitive documentation portal for **AntiOS**, the universal, domain-agnostic Agent-Native Engineering OS for Google Antigravity.

---

## 1. System Architecture & Design
- [Subsystem Architecture Overview](architecture/OVERVIEW.md) — The 4-tier model, 7 core subsystems, and 34-module component architecture.
- [Canonical Component Model](../ANTIOS_COMPONENT_MODEL.md) — Exhaustive directory layout, subsystem boundaries, and module inventories.
- [AntiOS Capability Matrix](../ANTIOS_CAPABILITY_MATRIX.md) — Core capability catalog and functional taxonomy.
- [AntiOS Certification Matrix](../ANTIOS_CERTIFICATION_MATRIX.md) — 50 canonical certification rules (C-01 through C-50) and test suites.

## 2. Canonical Specifications & Governance
- [Source of Truth](../ANTIOS_SOURCE_OF_TRUTH.md) — Single definitive source of truth across all 42 phases.
- [Universal Constitution](../ANTIOS_CONSTITUTION.md) — Non-negotiable framework axioms, invariants, and boundaries.
- [AntiOS v1 Specification](../ANTIOS_V1.md) — Foundational baseline specification and frozen axioms.
- [Responsibility Boundary](../ANTIOS_RESPONSIBILITY_BOUNDARY.md) — Demarcation between Platform, Framework, Adapter, and Target.
- [Core vs. Adapter Demarcation](../ANTIOS_CORE_VS_ADAPTER.md) — Strict separation between reusable core logic and project bindings.
- [Skill Architecture](../ANTIOS_SKILL_ARCHITECTURE.md) — Lean 4-skill model, delegation depth laws, and discovery contracts.
- [MCP & Tooling Policy](../ANTIOS_MCP_POLICY.md) — 6-tier tool hierarchy, 8 canonical justification criteria, and credential security.
- [Architectural Decision Register](../DECISION_REGISTER.md) — Complete history of architectural decisions (ADR 01–35).

## 3. User & Integration Guides
- [Universal Project Adoption Guide](guides/ADOPT_ANTIOS.md) — How to inspect, adapt, and run AntiOS on any code repository.
- [Project Adapter Guide](guides/PROJECT_ADAPTER.md) — Configuring `antios.config.json` for custom test runners, protected zones, and builds.

## 4. Reference Manuals
- [Command Line Reference](reference/CLI.md) — Comprehensive guide for all 8 deterministic CLI tools in `framework/scripts/tools/`.
- [Configuration Reference](reference/CONFIGURATION.md) — Complete schema reference for `antios.config.json`.

## 5. Operations, Security & Quality
- [Testing & Quality Assurance](operations/TESTING.md) — Test suite architecture, 447 test catalog, benchmarks, and regression gates.
- [Security Posture & Boundary Policy](SECURITY.md) — PreToolUse interception, framework self-protection, and path safety.
- [Active Context Ledger](ACTIVE_CONTEXT.md) — Bounded operational memory tracking current task state (<= 60 lines).
- [Agent Constitution](AGENTS.md) — Operational instructions for autonomous agents in AntiOS workspaces.
- [Validated Project Lessons](LESSONS.md) — Durable cross-session lessons and verified failure resolutions.

## 6. Historical Archive
- [Historical Archive Index](../reports/archive/INDEX.md) — Permanent archive of Phase 1–39 implementation reports, benchmarks, and legacy proposals.
