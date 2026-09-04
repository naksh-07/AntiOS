# AntiOS Subsystem Architecture Overview (`docs/architecture/OVERVIEW.md`)

## 1. Architectural Philosophy & Foundations

AntiOS is a universal, domain-agnostic **Agent-Native Engineering OS** designed to govern autonomous LLM coding agents operating in Google Antigravity. It enforces safety boundaries, physical process verification ratchets, bounded operational memory, deterministic repository wayfinding, and disciplined Maker-Checker verification.

AntiOS operates on four core principles:
1. **Zero Third-Party Dependencies**: The entire core framework and test harness run on standard library Python 3.8+.
2. **Fail-Closed Security**: Any ambiguity, unauthorized mutation, or path escape defaults strictly to denial.
3. **Physical Process Verification**: An agent cannot claim completion without physical OS exit code 0 from native test suites.
4. **Universal Domain Agnosticism**: Core framework logic contains zero assumptions about specific target applications.

---

## 2. The 4-Tier Architectural Model

AntiOS strictly demarcates responsibilities across four distinct layers:

```
+-------------------------------------------------------------------------+
| Tier 1: Antigravity Platform (Native Mechanisms)                        |
|  - Agent execution, subagent lifecycles, and tool transport             |
|  - Tool interception hooks (PreToolUse & Stop)                          |
|  - Interactive Planning Mode UI & background task scheduler             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 2: AntiOS Core (Universal Engineering Operating System)             |
|  - Fail-closed security guard & framework self-protection               |
|  - Physical process verification gate & Stop hook ratchet               |
|  - Same Change Set evaluator & git working tree conflict auditor        |
|  - Subsystem wayfinding, tool routing, and memory distillation          |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 3: Project Adapter (Declarative Workspace Bindings)                |
|  - Declarative configuration file (antios.config.json)                  |
|  - Declares protected zones, protected domain cores, and test runners   |
|  - Configures tool routing preferences and workspace topology           |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 4: Target Project Application (Target Codebase)                     |
|  - Domain-specific source code, schemas, and assets                     |
|  - Native test suites (pytest, vitest, cargo test, go test)             |
|  - Domain application runtime and build pipelines                       |
+-------------------------------------------------------------------------+
```

---

## 3. The 7 Core Subsystems (34 Core Modules)

All core logic resides within `framework/core/`, organized into 7 cohesive subsystems:

### 1. Governance & Boundaries Subsystem
- [`guard.py`](../../framework/core/guard.py) — Fail-closed tool mutation guard with path canonicalization, 8.3 alias blocking, and shell security.
- [`gate.py`](../../framework/core/gate.py) — Physical process verification executing native project test suites.
- [`verdict.py`](../../framework/core/verdict.py) — Maker-Checker verification verdict schema and multi-format parser.
- [`config.py`](../../framework/core/config.py) — Loads and validates `antios.config.json`.
- [`changeset.py`](../../framework/core/changeset.py) — Validates Same Change Set discipline across code, tests, and docs.
- [`worktree.py`](../../framework/core/worktree.py) — Audits git working tree cleanliness and prevents dirty-state commits.
- [`telemetry.py`](../../framework/core/telemetry.py) — Lightweight execution telemetry capturing command runtimes and exit codes.
- [`governance.py`](../../framework/core/governance.py) — High-level governance policies and invariant enforcement.

### 2. Lifecycle & Memory Subsystem
- [`lifecycle.py`](../../framework/core/lifecycle.py) — 10-stage task lifecycle state machine (`INTAKE` -> `LOCATE` -> `PLAN` -> `ACT` -> `TEST` -> `VERIFY` -> `COMPLETE`).
- [`memory.py`](../../framework/core/memory.py) — Bounded operational memory, 5 memory categories, and dead-end distillation.
- [`recovery.py`](../../framework/core/recovery.py) — Session state reconstruction and contradiction detection.

### 3. Project Intelligence & Adaptation Subsystem
- [`discovery.py`](../../framework/core/discovery.py) — Static inspection discovering project traits, archetypes, manifests, and test runners.
- [`profile.py`](../../framework/core/profile.py) — Structured `ProjectProfile` with evidence tiers.
- [`topology.py`](../../framework/core/topology.py) — Monorepo workspace graph analysis and blast-radius escalation.
- [`adapter.py`](../../framework/core/adapter.py) — Generates and verifies declarative `AdaptationProposal` schemas.

### 4. Subsystem & Knowledge Subsystem
- [`subsystem.py`](../../framework/core/subsystem.py) — Agent-oriented Subsystem Manifest schemas.
- [`wayfinding.py`](../../framework/core/wayfinding.py) — Inverted index and prefix tree component wayfinding.
- [`knowledge.py`](../../framework/core/knowledge.py) — In-memory multi-index Knowledge Graph and L0-L5 progressive disclosure.
- [`docaudit.py`](../../framework/core/docaudit.py) — Staleguard Layer-1 syntactic reference drift auditor.

### 5. Capability Subsystem
- [`capability.py`](../../framework/core/capability.py) — Canonical capability models and enum taxonomy (8 types).
- [`capability_pack.py`](../../framework/core/capability_pack.py) — Bounded capability prompt card formatter (<= 25 lines).
- [`capability_registry.py`](../../framework/core/capability_registry.py) — Deterministic capability registration and secondary indexing.
- [`capability_router.py`](../../framework/core/capability_router.py) — Signal-based capability resolution with 5-tier rule precedence.

### 6. Agent Topology & Specialization Subsystem
- [`agent_role.py`](../../framework/core/agent_role.py) — Canonical `AgentRole` contracts with capability boundaries.
- [`agent_routing_pack.py`](../../framework/core/agent_routing_pack.py) — Token-bounded handoff contracts for Primary <-> Specialist.
- [`agent_topology.py`](../../framework/core/agent_topology.py) — Multi-key index for Primary, Specialist, and Checker roles.
- [`agent_router.py`](../../framework/core/agent_router.py) — Conservative delegation engine enforcing the Shallow Depth Law (<= 2).
- [`workflow.py`](../../framework/core/workflow.py) — Maps high-level workflow archetypes to capabilities and roles.

### 7. Tool & Provider Layer
- [`tool.py`](../../framework/core/tool.py) — Standardized tool abstractions and 6-tier preference taxonomy.
- [`tool_pack.py`](../../framework/core/tool_pack.py) — Token-bounded tool selection cards (<= 25 lines).
- [`provider.py`](../../framework/core/provider.py) — Provider definitions, operational states, and capability mappings.
- [`tool_registry.py`](../../framework/core/tool_registry.py) — In-memory multi-dimensional tool registry with sub-millisecond lookups.
- [`tool_policy.py`](../../framework/core/tool_policy.py) — Centralized `MCPJustificationEngine` enforcing the 8-question framework.

---

## 4. Key Operational Invariants

1. **Framework Self-Protection**: Tools cannot modify `.agents/` or `framework/` directly.
2. **Upstream Domain Immutability**: Tools cannot modify paths defined in `protected_domain_cores` without explicit unlock.
3. **Same Change Set Discipline**: Any code change requires contemporary documentation and test updates.
4. **Shallow Depth Law**: Subagent nesting depth is strictly <= 2 ($	ext{Parent} 	o 	ext{Child}$). Subagents never spawn subagents.
5. **Maker-Checker Verification**: High-risk modifications mandate independent audit by a fresh-context Checker subagent.
