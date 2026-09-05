# AntiOS Master Architecture Specification (`ANTIOS_V1.md`)

**Version**: 1.0.0-GA  
**Date**: 2026-09-04  
**Status**: Canonical Master Architecture Specification (Phases 1–42 Consolidated)  
**Governing Axiom**:
> *"If Antigravity already provides the mechanism $	o$ USE THE PLATFORM.*  
> *If the language/compiler/test framework provides verification $	o$ USE THE NATIVE TOOLCHAIN.*  
> *If the target application owns a contract $	o$ DEFER TO THE TARGET PROJECT.*  
> *AntiOS owns: PROJECT POLICY, SAFETY BOUNDARIES, ENGINEERING WORKFLOW, VERIFICATION GATES, TASK STATE, AGENT TOPOLOGY, TOOL SELECTION."*

---

## 1. What is AntiOS?

**AntiOS** is a universal, reusable, agent-native engineering operating system designed for **Google Antigravity**. It provides the deterministic behavioral policies, safety boundaries, task-state conventions, wayfinding mechanisms, and verification gates that allow autonomous AI coding agents to safely plan, implement, test, document, and maintain complex software repositories without human micromanagement.

AntiOS is **not** an agent runtime, a database, or an application framework. It is the minimal set of repository policies, deterministic hooks, and structural indices required to eliminate agent hallucination, confirmation blindness, and blast-radius destruction.

---

## 2. The 4-Tier Architectural Hierarchy

AntiOS strictly separates concerns across four distinct architectural tiers:

```text
===================================================================================
                         TIER 1: GOOGLE ANTIGRAVITY
                            (Platform Mechanism)
===================================================================================
• Subagent execution & context isolation (invoke_subagent, manage_subagents)
• Tool interception & JSON stdio transport (PreToolUse, Stop hooks)
• Interactive Planning UI (<planning_mode>, implementation_plan.md)
• Immutable chronological transcript streaming (transcript.jsonl)
• Background scheduling, timers, and cron triggers (schedule)
• Host shell execution (run_command) and file manipulation primitives
                                    │
                                    ▼
===================================================================================
                             TIER 2: ANTI OS CORE
                        (Universal Project Governance)
===================================================================================
• Fail-closed path guard & ancestor containment (framework/core/guard.py)
• Physical process verification & Stop Gate ratchet (framework/core/gate.py)
• Standardized Maker-Checker verdict evaluation (framework/core/verdict.py)
• In-memory multi-index Knowledge Graph (framework/core/knowledge.py)
• Deterministic wayfinding & locality indexing (framework/core/wayfinding.py)
• 8-type Project Capability Layer (framework/core/capability*.py)
• Canonical Agent Roles & Topology Registry (framework/core/agent_*.py)
• 8-Tier Hybrid Capability Matrix & Provider Engine (framework/core/tool*.py)
• Same Change Set & Worktree Cleanliness (framework/core/changeset.py, worktree.py)
• Bounded working memory & distillation (framework/core/memory.py)
                                    │
                                    ▼
===================================================================================
                          TIER 3: PROJECT ADAPTER
                        (Declarative Configuration)
===================================================================================
• antios.config.json (Schema-validated configuration)
• Configured test runners, manifests, linters, and typecheckers
• Project-specific protected zones & forbidden wildcard patterns
• Project-specific agent topology & specialist overrides
• Zero Core code mutations: all project adaptations remain project-local
                                    │
                                    ▼
===================================================================================
                           TIER 4: TARGET PROJECT
                             (Target Codebase)
===================================================================================
• Python / FastAPI | TypeScript / Node / React | Go | Rust | Polyglot monorepos
• Application schemas, domain invariants, business logic
• Native test suites (pytest, vitest, cargo test, go test)
===================================================================================
```

---

## 3. Core Subsystems Map (63 Core Modules)

AntiOS Core is organized into cohesive, loosely coupled subsystems totaling 63 standard-library Python modules:

1. **Governance & Boundaries (`guard.py`, `gate.py`, `verdict.py`, `config.py`, `changeset.py`, `worktree.py`, `telemetry.py`, `governance.py`)**:
   Enforces fail-closed tool mutation guards, physical process exit-code-0 ratchets, merge conflict blocking, Same Change Set discipline, and worktree verification.
2. **Lifecycle & Task State (`lifecycle.py`, `memory.py`, `recovery.py`)**:
   Governs the 10-stage task lifecycle (`INTAKE` $	o$ `LOCATE` $	o$ `PLAN` $	o$ `ACT` $	o$ `TEST` $	o$ `VERIFY` $	o$ `COMPLETE`), bounded active memory (`docs/ACTIVE_CONTEXT.md` $\le 60$ lines), and state recovery.
3. **Project Intelligence & Adaptation (`discovery.py`, `profile.py`, `topology.py`, `adapter.py`)**:
   Discovers project traits, archetypes, manifests, build systems, and monorepo workspaces without hardcoded domain assumptions. Emits declarative `AdaptationProposal` schemas.
4. **Wayfinding & Knowledge Subsystem (`subsystem.py`, `wayfinding.py`, `knowledge.py`, `docaudit.py`)**:
   Provides in-memory multi-index knowledge graphs, BFS blast-radius calculation, progressive context disclosure (L0–L5), and Layer-1 syntactic reference drift auditing.
5. **Capability Subsystem (`capability.py`, `capability_pack.py`, `capability_registry.py`, `capability_router.py`)**:
   Indexes 8 canonical capability types (`SKILL`, `RULE`, `WORKFLOW`, `TOOL`, `VERIFIER`, `SPECIALIST`, `EXTERNAL_PROVIDER`, `MCP_PROVIDER`) with 5-tier rule precedence and bounded capability packs ($\le 25$ lines).
6. **Agent Topology & Specialization (`agent_role.py`, `agent_routing_pack.py`, `agent_topology.py`, `agent_router.py`, `workflow.py`)**:
   Maintains canonical agent role contracts, least-privilege capability boundaries, signal-based routing, Shallow Depth Law ($\le 2$), and token-bounded handoff contracts.
7. **Tool & Provider Layer (`tool.py`, `tool_pack.py`, `provider.py`, `tool_registry.py`, `tool_policy.py`)**:
   Implements the 6-tier preference engine (`NATIVE > SCRIPT > PROJECT > EXTERNAL > MCP > REJECTED`), in-memory multi-dimensional registry, and canonical MCP justification engine.

---

## 4. Agent Governance Layer (`.agents/`)

- **Primary Control Plane (`.agents/skills/antios/SKILL.md`)**: Canonical `/antios` entrypoint orchestrating wayfinding, capability routing, adaptive sizing, and verification.
- **Operating Skills (`.agents/skills/`)**:
  - `antios`: Universal project-native control plane ($\le 80$ lines).
  - `antios-engineer`: Universal engineering lifecycle, risk tiering, and boundary discipline.
  - `antios-verifier`: Independent Maker-Checker audit contract, diff review, and structured verdicts.
  - `antios-debug`: Deterministic 5-step root-cause debugging procedure.
  - `antios-adapt-project`: Universal project intelligence and adaptation procedure.
- **Workflow Retirement**: Dedicated legacy procedural files in `.agents/workflows/` are retired and archived to `reports/archive/legacy_workflows/`; procedural lifecycles route natively via `/antios` and `framework/core/workflow.py`.
- **Hook Manifest (`.agents/hooks.json`)**: Connects platform tool calls and completions to `pre_tool_guard.py` and `stop_gate.py`.

---

## 5. Verification & Quality Standard

- **Test Suite**: Authoritative standard-library runner `tests/run_all.py` executing all 79 test modules and 671 tests with 100% pass rate.
- **Agent-Native Certification**: `framework/scripts/tools/certify_agent_native.py` formally certifies repository agent-native quality across 10 dimensions with fail-closed security.
- **Intelligence Verification**: `framework/scripts/tools/verify_intelligence.py` cryptographically verifies emitted project intelligence, detects architecture drift, and prevents legacy workflow regressions.
- **Zero Token Reference Auditing**: `framework/scripts/tools/audit_docs.py` verifies physical existence of all documentation references and test commands with zero LLM tokens.
- **Changeset & Worktree Validation**: `check_changeset.py` and `check_worktree.py` guarantee repository cleanliness before turn completion.

