# AntiOS Component Model Specification (`ANTIOS_COMPONENT_MODEL.md`)

**Version**: 2.0.0-GA  
**Date**: 2026-09-06  
**Status**: Canonical Component Model Specification (63 Core Modules)  

---

## 1. Overview & Architectural Placement

The AntiOS Component Model defines the physical and logical components that constitute the framework, their internal data structures, APIs, lifecycle transitions, and inter-component contracts.

```text
+-----------------------------------------------------------------------------------+
|                           GOOGLE ANTIGRAVITY PLATFORM                             |
|  [Tool Interceptor IPC]        [Subagent Dispatch]         [Workspace Tool Engine] |
+--------------+--------------------------+-----------------------------+-----------+
               | (stdin JSON)             | (context/tools)             |
               v                          v                             v
+--------------+--------------------------+-----------------------------+-----------+
|                               ANTIOS HOOK BRIDGES                                 |
|  [.agents/hooks.json]                                                             |
|       |--> [framework/scripts/hooks/pre_tool_guard.py]                            |
|       `--> [framework/scripts/hooks/stop_gate.py]                                 |
+--------------+--------------------------+-----------------------------------------+
               |                          |
               v                          v
+--------------+--------------------------+-----------------------------------------+
|                               ANTIOS CORE LIBRARY                                 |
|  1. Governance & Boundaries: guard.py, gate.py, verdict.py, config.py,            |
|                              changeset.py, worktree.py, telemetry.py, governance.py|
|  2. Lifecycle & Memory:      lifecycle.py, memory.py, recovery.py                 |
|  3. Project Intelligence:    discovery.py, profile.py, topology.py, adapter.py    |
|  4. Subsystem & Knowledge:   subsystem.py, docaudit.py, wayfinding.py, knowledge.py|
|  5. Capability Layer:        capability.py, pack.py, registry.py, router.py       |
|  6. Agent Topology:          role.py, routing_pack.py, topology.py, router.py     |
|  7. Tool & Provider Layer:   tool.py, tool_pack.py, provider.py, policy.py, reg.py|
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+------------------------------------------+----------------------------------------+
|                              PROJECT ADAPTER LAYER                                |
|  [antios.config.json]                                                             |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+------------------------------------------+----------------------------------------+
|                               GOVERNANCE ARTIFACTS                                |
|  [.agents/skills/antios-engineer/]  [.agents/skills/antios-verifier/]               |
|  [.agents/skills/antios-debug/]     [.agents/skills/antios-adapt-project/]          |
|  [.agents/workflows/*.md]           [docs/AGENTS.md]       [docs/ACTIVE_CONTEXT.md]   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Framework Core Subsystem Inventory

All 63 core modules in `framework/core/` are standard-library Python 3.8+ with zero external dependencies:

### 2.1 Governance & Boundaries
- `guard.py`: Fail-closed tool mutation guard with path canonicalization and 8.3 alias blocking.
- `gate.py`: Physical process verification executing native project test suites.
- `verdict.py`: Maker-Checker verification verdict schema and multi-format parser.
- `config.py`: Loads and validates `antios.config.json`.
- `changeset.py`: Validates Same Change Set discipline across code, tests, and docs.
- `worktree.py`: Audits git working tree cleanliness and prevents dirty-state commits.
- `telemetry.py`: Lightweight execution telemetry capturing command runtimes and exit codes.
- `governance.py`: High-level governance policies and invariant enforcement.

### 2.2 Lifecycle & Memory
- `lifecycle.py`: 10-stage task lifecycle state machine (`INTAKE` -> `LOCATE` -> `PLAN` -> `ACT` -> `TEST` -> `VERIFY` -> `COMPLETE`).
- `memory.py`: Bounded operational memory, 5 memory categories, and dead-end distillation.
- `recovery.py`: Session state reconstruction and contradiction detection.

### 2.3 Project Intelligence & Adaptation
- `discovery.py`: Static inspection discovering project traits, archetypes, and manifests.
- `profile.py`: Structured `ProjectProfile` with evidence tiers.
- `topology.py`: Monorepo workspace graph analysis and blast-radius escalation.
- `adapter.py`: Generates and verifies declarative `AdaptationProposal` schemas.

### 2.4 Subsystem & Knowledge
- `subsystem.py`: Agent-oriented Subsystem Manifest schemas.
- `wayfinding.py`: Inverted index and prefix tree component wayfinding.
- `knowledge.py`: In-memory multi-index Knowledge Graph and L0-L5 progressive disclosure.
- `docaudit.py`: Staleguard Layer-1 syntactic reference drift auditor.

### 2.5 Capability Subsystem
- `capability.py`: Canonical capability models and enum taxonomy (8 types).
- `capability_pack.py`: Bounded capability prompt card formatter (<= 25 lines).
- `capability_registry.py`: Deterministic capability registration and secondary indexing.
- `capability_router.py`: Signal-based capability resolution with 5-tier rule precedence.

### 2.6 Agent Topology & Specialization
- `agent_role.py`: Canonical `AgentRole` contracts with capability boundaries.
- `agent_routing_pack.py`: Token-bounded handoff contracts for Primary <-> Specialist.
- `agent_topology.py`: Multi-key index for Primary, Specialist, and Checker roles.
- `agent_router.py`: Conservative delegation engine enforcing the Shallow Depth Law (<= 2).
- `workflow.py`: Maps high-level workflow archetypes to capabilities and roles.

### 2.7 Tool & Provider Layer
- `tool.py`: Standardized tool abstractions and 8-tier hybrid capability matrix.
- `tool_pack.py`: Token-bounded tool selection cards (<= 25 lines).
- `provider.py`: Provider definitions, operational states, and capability mappings.
- `tool_registry.py`: In-memory multi-dimensional tool registry with sub-millisecond lookups.
- `tool_policy.py`: Centralized `MCPJustificationEngine` enforcing the 8-question framework and escalation protocol.

### 2.8 Project Agent OS & Boundary Compilation
- `manifest.py`: Project manifest provenance and cryptographic hash verification.
- `provenance.py`: Provenance and ownership tracking across 5 artifact tiers.
- `compiler.py`: Universal boundary compiler compiling declarative project boundaries.
- `installation.py`: Installation lifecycle, bootstrap validation, and uninstall cleanliness.
- `runtime_contract.py`: Instance runtime closure and source-independent execution.

### 2.9 Main AntiOS Control Plane & Task Dispatch
- `dispatch.py`: Canonical 10-stage task dispatch pipeline and workforce resolution.
- `anatomy.py`: Structural decomposition of project codebases.
- `component_intelligence.py`: Component-level semantic intelligence and convention discovery.
- `skill_generator.py`: Generates targeted project-specific skills.
- `specialist_generator.py`: Generates least-privilege specialist agent personas.

### 2.10 Project Learning & Controlled Evolution
- `learning.py`: Epistemic observation store and `LearningSafetyGate` fail-closed defenses.
- `evolution_proposal.py`: Structured evolution proposal schemas with atomic snapshots.
- `evolution_governance.py`: Controlled evolution engine with rollback capabilities.
- `intelligence_verifier.py`: Verifies intelligence artifacts against drift and contamination.
- `capability_gap.py`: 9-class failure taxonomy and capability gap detection.
- `tool_gap.py`: Tool and MCP gap analysis engine.
- `two_way_contract.py`: Core immutability vs project adaptation contract.
- `migration.py`: SemVer compatibility and migration lifecycle engine.

### 2.11 Agent-Native Repository Optimization
- `agent_native_score.py`: 10-dimension evidence-backed agent-native scoring.
- `agent_friction.py`: 19-class agent friction detection and telemetry.
- `agent_improvement.py`: Friction-targeted improvement proposals.
- `documentation_compiler.py`: Compiles progressive-disclosure documentation.
- `agent_refactoring.py`: Agent-native structural refactoring suggestions.
- `agent_native_certification.py`: 5-tier formal repository certification engine.

### 2.12 Native Antigravity Workforce & Orchestration
- `workforce_contract.py`: Responsibility domain partitioning, anti-emulation constraints, and Teamwork coordination.
- `orchestration.py`: Adaptive workforce planner, wave manager, wave persistence, and recovery engines.

### 2.13 Context Engineering, Freshness & Continuity
- `context_budget.py`: 6-action context budget governor, token-bounded reasoning cards, and utility optimization.
- `context_freshness.py`: Freshness evaluator detecting hash and git drift, safe compaction engine.
- `mission_state.py`: Dual-mode mission persistence (4-file format) and deterministic crash recovery engine.
