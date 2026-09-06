# AntiOS Documentation Index (`docs/INDEX.md`)

Welcome to the definitive documentation map for **AntiOS** (Agent-Native Engineering OS for Google Antigravity). This portal is structured for progressive disclosure to help both human developers and autonomous AI agents navigate the framework deterministically without exploration amnesia.

---

## 1. Executive Entrypoints & Core Laws
- [README](../README.md) — Product overview, quick start, architecture summary, and mission.
- [Master Source of Truth](../ANTIOS_SOURCE_OF_TRUTH.md) — Canonical authority hierarchy and precedence model (Phases 1–42 consolidated).
- [Universal Constitution](../ANTIOS_CONSTITUTION.md) — The 7 non-negotiable engineering invariants (Protected zones, Same Change Set, etc.).
- [Master Architecture Specification (v1.0.0-GA)](../ANTIOS_V1.md) — Canonical 4-tier model, 7 subsystems, 63 core modules.
- [Architectural Decision Register](../DECISION_REGISTER.md) - Complete consensus history of all architectural decisions (ADR 01-82).
- [Project Agent OS Specification (AntiOS 2.0)](architecture/PROJECT_AGENT_OS.md) - Universal boundary compiler, 5-tier artifact model, lifecycle engine, and orchestration limits.
- [Contributing Guide](../CONTRIBUTING.md) — Engineering standards, Same Change Set policy, and test validation.

## 2. Architecture & Subsystems (`docs/architecture/`)
- [System Architecture Overview](architecture/OVERVIEW.md) — High-level system architecture, subsystem interaction map, and data flows.
- [Project Agent OS Architecture](architecture/PROJECT_AGENT_OS.md) - Boundary demarcation (SOURCE ≠ INSTANCE ≠ PROJECT), manifest provenance, and orchestration constitution.
- [Native Workforce Contract](architecture/WORKFORCE_CONTRACT.md) — Responsibility domain partitioning, anti-emulation constraints, and Teamwork-grade coordination.
- [Context Budget & Governance](architecture/CONTEXT_GOVERNANCE.md) — 6-action context budget governor, token-bounded reasoning cards, and freshness detection.
- [Mission State Continuity](architecture/MISSION_CONTINUITY.md) — Dual-mode persistence, 4-file atomic storage, and deterministic crash recovery.
- [Evidence Architecture](architecture/EVIDENCE_ARCHITECTURE.md) — Epistemic separation, 6 evidence states, cryptographic artifact fingerprints, and bounded packages.
- [Mission Evaluation Engine](architecture/MISSION_EVALUATION.md) — 11-dimension evaluation engine, 4 statuses, and independent Maker-Checker contract.
- [Agent-Native Mission Benchmark](architecture/MISSION_BENCHMARK.md) — Engineering workflow quality metrics, Baseline vs AntiOS comparison, and proving grounds A–J.
- [Durable Project Proofs](architecture/DURABLE_PROOFS.md) — Canonical ProjectProof abstraction, 13 subjects, 7 lifecycle states, and physical hash grounding.
- [Runtime Drift & Intelligence Health](architecture/DRIFT_AND_HEALTH.md) — Event-driven drift detection across 10 domains, 7-dimension health model, and proposal-governed repair.
- [Long-Horizon Release Certification](architecture/RELEASE_CERTIFICATION.md) — 12-dimension evidence-driven release certification, bounded window, and verifiable certification receipts.
- [Real Antigravity Proving Ground](architecture/PROVING_GROUND.md) — 8 canonical engineering scenarios (A–H), native vs simulated trace boundary, and bounded execution cards.
- [Failure Injection & Recovery Matrix](architecture/FAILURE_INJECTION.md) — 16 canonical failure modes, deterministic recovery action matrix, and partial write safety.
- [Long-Horizon Adaptive Engineering](architecture/LONG_HORIZON.md) — RUN-01 to RUN-05 sequences, adaptive knowledge feedback loop, and workflow comparisons.
- [Project Learning & Evolution Model](architecture/PROJECT_LEARNING.md) — Epistemic segregation, evidence promotion ladder, safe evolution proposals, and knowledge decay.

- [Two-Way Adaptation Contract](architecture/TWO_WAY_ADAPTATION.md) — Four-tier boundary demarcation, epistemic segregation, and Core Immutability Law.
- [Capability Gap & Tool Escalation Model](architecture/CAPABILITY_GAP_MODEL.md) — 9-class failure taxonomy, gap lifecycle state machine, and 6-tier tool escalation.
- [Controlled Evolution Governance](architecture/EVOLUTION_GOVERNANCE.md) — Structured proposals, 3-tier approval classes, snapshotting, and atomic rollback.
- [Compatibility & Migration Model](architecture/COMPATIBILITY_MODEL.md) — SemVer compatibility assessment, 7-stage migration lifecycle, and CLI tooling.
- [Agent-Native Repository Model](architecture/AGENT_NATIVE_MODEL.md) — 10-dimension evidence-backed scoring, progressive disclosure compiler, and refactoring advisor.
- [Agent Friction Taxonomy & Resolution](architecture/AGENT_FRICTION_MODEL.md) — 19-class friction detection, epistemic segregation, and NO_ACTION improvement proposals.
- [Agent-Native Certification](architecture/AGENT_NATIVE_CERTIFICATION.md) — Formal 5-tier certification, fail-closed security invariants, and CLI tooling.
- [Adaptive Mission Orchestration Model](architecture/ORCHESTRATION_MODEL.md) — Sizing modes (SOLO to MAX), wave lifecycle, dual dispatch gates, and resource ledger.
- [AntiOS Primary Skill Architecture](architecture/ANTIOS_SKILL_MODEL.md) — Single `/antios` control plane specification and progressive disclosure.
- [Canonical Component Model](architecture/COMPONENT_MODEL.md) — 63 core Python modules across all subsystems.
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
  - [antios](../.agents/skills/antios/SKILL.md) — Universal project-native control plane and primary `/antios` entrypoint.
  - [antios-engineer](../.agents/skills/antios-engineer/SKILL.md) — Universal engineering workflow policy skill (Plan, Act, Consolidate).
  - [antios-verifier](../.agents/skills/antios-verifier/SKILL.md) — Maker-Checker independent verification audit contract.
  - [antios-debug](../.agents/skills/antios-debug/SKILL.md) — 5-step systematic root-cause debugging procedure.
  - [antios-adapt-project](../.agents/skills/antios-adapt-project/SKILL.md) — Universal project discovery and adapter configuration.
- **Archived Legacy Workflows** (`reports/archive/legacy_workflows/`):
  - [Legacy Workflows Archive](../reports/archive/legacy_workflows/README.md) — Historical SOP catalog retired to archive; active lifecycle contracts codified in `framework/core/workflow.py`.

## 4. Technical Reference & Guides
- [Universal Project Adoption Guide](guides/ADOPT_ANTIOS.md) — Step-by-step onboarding of unfamiliar repositories into AntiOS governance.
- [Project Adapter Guide](guides/PROJECT_ADAPTER.md) — Declarative adapter configuration schema (`antios.config.json`).
- [Orchestration Policy & Invariants](reference/ORCHESTRATION_POLICY.md) — Constitutional workforce limits, wave collapse rules, and write safety policies.
- [Agent Dispatch Reference](reference/AGENT_DISPATCH.md) — Canonical 10-stage task dispatch pipeline and CLI reference.
- [Command Line Interface Reference](reference/CLI.md) — Reference for deterministic CLI tools in `framework/scripts/tools/` (including `dispatch_task.py` and `verify_intelligence.py`).
- [Configuration Reference](reference/CONFIGURATION.md) — Complete specification of `antios.config.json` options.
- [Tool, Provider & MCP Policy](reference/MCP_POLICY.md) — 8-tier hybrid capability matrix and canonical MCP escalation rules.
- [AntiOS Failure Taxonomy](reference/FAILURE_TAXONOMY.md) — Deterministic vs. agent failure classification and mitigations.
- [Testing & Verification Guide](operations/TESTING.md) — Test suite architecture, 882 tests across 127 modules, and commands.
- [Security Architecture & Threat Model](SECURITY.md) — Process confinement, protected zone immutability, and boundary rules.

## 5. Historical Archive & Research (`reports/archive/`)
- [Archive Master Index](../reports/archive/INDEX.md) — Overview of historical evolution and archival structure.
- [Phase Reports Index](../reports/archive/phases/INDEX.md) — Historical reports detailing Phases 1–42 development progression.
- [Original Research Archive](../reports/archive/research/INDEX.md) — Prior art evaluations, single-idea studies, and foundational blueprints.
- [Prototype Experiments](../reports/archive/prototype/PROTOTYPE_TEST_RESULTS.md) — Early empirical feasibility tests and benchmarks.
