# AntiOS Legacy Runtime & Codebase Audit

**Document**: `docs/architecture/LEGACY_RUNTIME_AUDIT.md`  
**Status**: `CANONICAL` (Phase 109 Architecture Review)  
**Version**: 2.1.0-GA  
**Role**: Exhaustive Reachability, Consumer Analysis & Migration Disposition Audit  
**Parent Specifications**:
- [`docs/architecture/MIGRATION_MATRIX.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/MIGRATION_MATRIX.md)
- [`docs/architecture/CORE_VS_ADAPTER.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/CORE_VS_ADAPTER.md)
- [`docs/architecture/ambient/COMPILER.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/COMPILER.md)
- [`docs/architecture/ambient/BOOTSTRAP.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/BOOTSTRAP.md)
- [`docs/architecture/experience/SYSTEM_A_B_SEPARATION.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/experience/SYSTEM_A_B_SEPARATION.md)

---

## 1. Executive Summary & Audit Methodology

This document performs an exhaustive, evidence-grounded forensic audit of the **84 Python modules in `framework/core/`**, the **16 scripts in `framework/scripts/`**, and the **5 templates in `framework/templates/`**. 

Every module has been inspected via static Abstract Syntax Tree (AST) analysis, caller dependency graphing, CLI command wiring, and test harness execution to determine its:
1. **Runtime Reachability**: How the module is entered at runtime (CLI entrypoint, lifecycle hook, standalone tool script, internal core dependency, test-only execution, or dead code/orphan).
2. **Current Consumers**: Exact upstream callers and test suites that depend on the module.
3. **Target Instance Deployment Status**: Whether the module is deployed to target project repositories (Tier 1 Canonical Source, Tier 2 Managed Config, Tier 3 Generated Runtime Closure, Tier 4 Operating Interface, or Source-Only).
4. **Future Role & Action**: Target state under the Ambient Project OS architecture (`KEEP`, `REWORK`, `REPLACE`, `DEPRECATE`, `REMOVE`).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RUNTIME REACHABILITY TAXONOMY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. CLI-Reachable      │ Directly wired to unified `framework/cli.py`        │
│ 2. Hook-Reachable     │ Invoked synchronously via `.agents/hooks.json`      │
│ 3. Script-Reachable   │ Invoked via standalone `framework/scripts/tools/`   │
│ 4. Core-Internal      │ Required dependency of other core modules           │
│ 5. Test-Only          │ Reachable exclusively through test suite execution  │
│ 6. Orphaned (Dead)    │ Zero callers across CLI, scripts, core, and tests   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Category 1: Governance & Boundaries (7 Modules, 2,063 Lines)

Modules responsible for path canonicalization, workspace containment, working tree conflict detection, and architectural boundaries.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `guard.py` (174 lines) | Internal (Core-Dependency) | Core: `compiler`, `installation`; Tests: `test_guard`, `test_guard_hardened` (7 suites) | Canonical core path traversal and security verification engine. Validates canonical path boundaries across platforms. | **KEEP** — Retain as Tier-1 core source logic; compiled into `.antios/runtime/pre_tool_guard.py` template. |
| `governance.py` (149 lines) | Internal (Core-Dependency) | Core: `compiler`, `installation`; Tests: `test_governance`, `test_guard` (6 suites) | Canonical definitions of immutable core zones (`.agents`, `.antios`, `antios.config.json`). | **KEEP** — Authoritative zone boundary registry in Core; synchronized with `antios.config.json`. |
| `changeset.py` (255 lines) | Script-Reachable | Scripts: `check_changeset.py`; Core: `release_engine`, `proving_ground`, `docaudit`; Tests: `test_changeset` (9 suites) | Inspects git working tree changesets, unstaged files, and dirty diffs. | **KEEP** — Core diff inspector for release checks and Maker-Checker audits. |
| `worktree.py` (332 lines) | Script-Reachable | Scripts: `check_worktree.py`; Core: `git_capability`, `proving_ground`, `docaudit`, `compiler`; Tests: `test_worktree` (6 suites) | Git worktree conflict marker detector (`<<<<<<<`, `=======`, `>>>>>>>`) and dirty tree auditor. | **KEEP** — Standalone conflict detection logic embedded into compiled `.antios/runtime/stop_gate.py`. |
| `runtime_contract.py` (266 lines) | Internal (Core-Dependency) | Core: `compiler`, `installation`, `drift_health`; Tests: `test_runtime_closure` (1 suite) | Validates Runtime Closure Axiom: verifies zero framework imports and zero 3rd-party dependencies in `.antios/runtime/`. | **KEEP** — Critical compiler pre-flight check ensuring target instances are 100% self-contained. |
| `two_way_contract.py` (314 lines) | Internal (Core-Dependency) | Core: `adapter`, `discovery`; Tests: `test_two_way_contract` (3 suites) | Governs two-way contract between AntiOS Core abstractions and project-specific adapters (`antios.config.json`). | **KEEP** — Enforces domain decoupling and Core vs Adapter separation. |
| `architecture_freeze.py` (573 lines) | Internal (Core-Dependency) | Core: `github_capability`; Tests: `test_architecture_freeze` (1 suite) | Evaluates proposed changes and feature requests against constitutional architectural invariants (`INV-01` to `INV-15`). | **KEEP** — Powers `antios issue triage` to block architectural regression and scope creep. |

---

## 3. Category 2: Repository Intelligence & Adaptation (8 Modules, 4,182 Lines)

Modules that inspect target projects, discover tech stacks, build anatomy prefix trees, and generate declarative adapters.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `adapter.py` (546 lines) | Direct (CLI-Reachable) | CLI: `antios adapt`; Scripts: `adapt_project.py`, `inspect_repo.py`; Core: `discovery`, `compiler`, `installation`; Tests (12 suites) | Canonical adapter generator, validator, and synchronizer for `antios.config.json`. | **KEEP** — Primary engine for zero-ceremony project onboarding and configuration maintenance. |
| `discovery.py` (1,180 lines) | Direct (CLI-Reachable) | CLI: `antios adapt`, `doctor`; Scripts: `adapt_project.py`, `navigate_repo.py`; Core: `adapter`, `topology`, `anatomy`, `profile` (10 core modules); Tests (15 suites) | Deep stack detector (Python, TypeScript, Rust, Go, polyglot), package manifest parser, and test runner finder. | **KEEP** — High-performance heuristic engine for automatic test suite and tool discovery. |
| `profile.py` (274 lines) | Internal (Core-Dependency) | Core: `discovery`, `topology`, `adapter`, `anatomy`, `installation`, `compiler`; Tests (9 suites) | Data models representing project profile facts, detected toolchains, and environment constraints. | **KEEP** — Core dataclass contracts for repository characterization. |
| `topology.py` (590 lines) | Script-Reachable | Scripts: `inspect_repo.py`, `navigate_repo.py`; Core: `discovery`, `adapter`, `anatomy`, `dispatch`, `subsystem`, `worktree`; Tests (15 suites) | Monorepo and workspace member detector (pnpm, npm/yarn, Cargo, Go, uv/poetry workspaces). Safe traversal skipping `node_modules`, `.git`. | **KEEP** — Essential for polyglot monorepo boundary detection and member-scoped verification. |
| `anatomy.py` (675 lines) | Internal (Core-Dependency) | Core: `compiler`, `wayfinding`, `component_intelligence`, `discovery`, `installation`; Tests (5 suites) | Generates prefix trees and subsystem boundaries; compiles into `.antios/anatomy.json`. | **KEEP** — Enables sub-millisecond locality wayfinding without vector databases. |
| `component_intelligence.py` (173 lines) | Internal (Core-Dependency) | Core: `anatomy`, `discovery`; Tests: `test_component_intelligence` (2 suites) | Analyzes code component coupling, cohesion, and blast radius within detected subsystems. | **REWORK** — Consolidate heuristics with `anatomy.py` to streamline intelligence compilation. |
| `universal_adoption.py` (613 lines) | Internal (Core-Dependency) | Core: `installation`; Tests: `test_universal_adoption` (2 suites) | Onboarding orchestration across diverse target environments and legacy project structures. | **KEEP** — Powers `antios install` safe migration pathways. |
| `config.py` (131 lines) | Script-Reachable | Scripts: `adapt_project.py`, `check_changeset.py`, `inspect_repo.py`, `navigate_repo.py`; Core: `adapter`, `compiler`, `gate` (11 core modules); Tests (27 suites) | Schema validator and parser for `antios.config.json`. | **KEEP** — Standard config parser with fail-closed defaults. |

---

## 4. Category 3: Memory, Wayfinding & Learning (7 Modules, 4,660 Lines)

Modules governing working memory, deterministic locality navigation, documentation integrity, and System A evidence-grounded learning.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `memory.py` (1,004 lines) | Script-Reachable | Scripts: `distill_memory.py`; Core: `learning`, `recovery`; Tests (8 suites) | Parses, validates, bounds, and synchronizes `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines) and `docs/LESSONS.md` ($\le 50$ items). | **KEEP** — Core working memory governance engine for System A. |
| `wayfinding.py` (363 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `anatomy`, `knowledge`, `discovery`, `dispatch`, `subsystem`; Tests (15 suites) | Deterministic locality navigation engine using prefix trees and inverted word indexes; sub-millisecond lookup, 0 tokens. | **KEEP** — The permanent, zero-overhead alternative to vector databases. |
| `knowledge.py` (901 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `wayfinding`, `memory`, `docaudit`, `learning`; Tests (13 suites) | Implements 3-tier progressive disclosure (Platform Directives $\to$ Active Task State $\to$ Historical Archive). | **KEEP** — Enforces token-conscious context delivery. |
| `learning.py` (1,194 lines) | Script-Reachable | Scripts: `distill_memory.py`; Core: `memory`, `evolution_governance`, `project_proof`, `evidence`, `evolution_proposal`; Tests (8 suites) | System A Evidence Promotion Ladder (OBSERVED $\to$ CANDIDATE $\to$ VALIDATED $\to$ DURABLE). Contains `LearningSafetyGate`. | **KEEP** — Core engine for verified project learning; strictly firewalled from System B telemetry. |
| `docaudit.py` (290 lines) | Script-Reachable | Scripts: `audit_docs.py`; Core: `documentation_compiler`, `doctor`, `changeset`, `worktree`; Tests (3 suites) | Audits documentation reference links, broken paths, and stale symbol cross-references. | **KEEP** — Validates documentation integrity during `antios doctor` and release checks. |
| `documentation_compiler.py` (450 lines) | Internal (Core-Dependency) | Core: `compiler`; Tests: `test_documentation_compiler` (3 suites) | Generates and validates `docs/AGENTS.md` bounded to $\le 40$ lines. | **KEEP** — Compiles compact ambient orientation contracts. |
| `recovery.py` (458 lines) | Script-Reachable | Scripts: `recover_session.py`; Core: `memory`, `mission_state`; Tests (7 suites) | Reconstructs session state from `ACTIVE_CONTEXT.md` and `transcript.jsonl` following agent amnesia or context resets. | **KEEP** — Critical resilience engine for session continuity. |

---

## 5. Category 4: Capability & Tool Hierarchy (13 Modules, 5,019 Lines)

Modules defining capabilities, tool routing, tool policies, git CLI wrappers, and GitHub issue generation.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `capability.py` (302 lines) | Direct (CLI-Reachable) | CLI: `doctor`; Scripts: `navigate_repo.py`; Core: `capability_registry`, `capability_router`, `tool` (15 core modules); Tests (23 suites) | Core dataclass definitions for capabilities, requirements, and execution contracts. | **KEEP** — Foundation models for project capabilities. |
| `capability_registry.py` (689 lines) | Internal (Core-Dependency) | Core: `capability_router`, `discovery`, `compiler`; Tests (4 suites) | Registry of standard project capabilities (build, test, lint, format, typecheck, package). | **KEEP** — Core catalog of domain-agnostic capabilities. |
| `capability_router.py` (537 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `dispatch`, `orchestration`, `capability`, `tool_policy`; Tests (8 suites) | Routes user task intents to appropriate capabilities and test suites. | **KEEP** — Core dispatch routing logic. |
| `capability_pack.py` (133 lines) | Internal (Core-Dependency) | Core: `capability_router`, `dispatch`, `orchestration`, `memory`; Tests (7 suites) | Bounded 25-line capability cards for prompt injection. | **KEEP** — Context-bounding mechanism for capability metadata. |
| `capability_gap.py` (302 lines) | Internal (Core-Dependency) | Core: `evolution_proposal`, `doctor`, `adapter`; Tests (5 suites) | Detects missing tools or unimplemented project capabilities. | **KEEP** — Diagnostic engine for `antios doctor`. |
| `tool.py` (322 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `tool_registry`, `tool_policy`, `tool_pack`, `provider` (11 core modules); Tests (22 suites) | 6-tier tool policy definitions and tool metadata contracts. | **KEEP** — Core tool classification models. |
| `tool_registry.py` (870 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `tool_policy`, `dispatch`, `orchestration`; Tests (8 suites) | Catalogs available IDE tools, CLI commands, and platform tools. | **KEEP** — Central tool registry in Core. |
| `tool_policy.py` (813 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `dispatch`, `orchestration`; Tests (9 suites) | Deterministic tool selector enforcing tier policies (CLI > MCP > Fallback). | **KEEP** — Enforces platform tool priority rules. |
| `tool_pack.py` (137 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `dispatch`; Tests (2 suites) | Bundles tool declarations into compact execution packs. | **KEEP** — Lightweight tool bundle model. |
| `tool_gap.py` (293 lines) | Internal (Core-Dependency) | Core: `capability_gap`, `doctor`; Tests (2 suites) | Analyzes gaps between requested tools and available execution environments. | **KEEP** — Diagnostic engine for tool availability. |
| `provider.py` (129 lines) | Internal (Core-Dependency) | Core: `tool`, `tool_registry`, `tool_policy`; Tests (6 suites) | Abstractions for tool providers (Native Platform, Local Shell, External MCP). | **KEEP** — Provider abstraction layer. |
| `git_capability.py` (222 lines) | Direct (CLI-Reachable) | CLI: `doctor`, `release`; Core: `release_engine`, `changeset`; Tests (1 suite) | High-performance, zero-dependency local git CLI operations wrapper. | **KEEP** — Replaces redundant GitHub MCP for local git operations. |
| `github_capability.py` (270 lines) | Direct (CLI-Reachable) | CLI: `antios issue {triage,discover,create}`; Tests: `test_git_github_release_capabilities` (2 suites) | Formats structured issue evidence cards and triages feature requests against Architecture Freeze. | **KEEP** — Powers `antios issue` subcommands. |

---

## 6. Category 5: Agent Topology & Dispatch (7 Modules, 2,300 Lines)

Modules governing agent roles, workforce topologies, specialist generation, and task dispatch pipelines.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `agent_role.py` (283 lines) | Internal (Core-Dependency) | Core: `agent_topology`, `agent_router`, `dispatch`, `orchestration`, `workforce_contract`; Tests (10 suites) | Dataclass models for agent roles, permissions, and responsibility boundaries. | **KEEP** — Core definitions of Maker, Checker, and Specialist roles. |
| `agent_topology.py` (435 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `agent_router`, `dispatch`; Tests (8 suites) | Maps project requirements to workforce topologies; enforces Shallow Depth Law ($\le 2$). | **KEEP** — Sizing and dispatch policy engine. |
| `agent_router.py` (284 lines) | Internal (Core-Dependency) | Core: `dispatch`, `orchestration`, `agent_routing_pack`; Tests (7 suites) | Routes engineering tasks to appropriate agent roles. | **KEEP** — Core task routing logic. |
| `agent_routing_pack.py` (108 lines) | Internal (Core-Dependency) | Core: `agent_router`, `dispatch`, `orchestration`, `memory`; Tests (1 suite) | Bounded context pack containing agent role and routing metadata. | **KEEP** — Prompt bounding contract for multi-agent dispatch. |
| `dispatch.py` (684 lines) | Script-Reachable | Scripts: `dispatch_task.py`; Core: `orchestration`, `subsystem`, `wayfinding`; Tests (4 suites) | Task dispatch pipeline; orchestrates prompt generation, tool bindings, and worker dispatch. | **REWORK** — Decouple from explicit ceremony; delegate process launching to Antigravity `invoke_subagent`. |
| `specialist_generator.py` (264 lines) | Internal (Core-Dependency) | Core: `compiler`, `installation`; Tests: `test_specialist_generation` (1 suite) | Generates specialized subagent markdown definitions from project anatomy. | **REWORK** — Simplify generation into standard subagent prompts; retire complex specialist hierarchies. |
| `skill_generator.py` (242 lines) | Internal (Core-Dependency) | Core: `compiler`, `installation`; Tests: `test_skill_generation` (1 suite) | Generates project-specific `SKILL.md` operating interfaces in `.agents/skills/`. | **KEEP** — Compiles Tier-4 operating skills for target repositories. |

---

## 7. Category 6: Lifecycle, Compilation & Runtime (9 Modules, 4,056 Lines)

Modules governing project compilation, installation lifecycle, manifest hashing, versioning, and runtime closure.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `compiler.py` (368 lines) | Internal (Core-Dependency) | Core: `installation`, `doctor`, `release_engine`, `drift_health`; Tests (8 suites) | Authoritative Project Environment Compiler. Generates `.antios/runtime/` closure, `.antios/manifest.json`, and `.antios/anatomy.json`. | **KEEP** — Core build engine enforcing Four-Boundary Demarcation (`INV-10`). |
| `installation.py` (680 lines) | Direct (CLI-Reachable) | CLI: `antios install`, `update`, `rollback`, `repair`, `remove`, `adapt`, `verify`; Scripts: `install_project.py`; Core: `doctor`, `release_engine`; Tests (9 suites) | Unified installation lifecycle manager. Handles atomic writes, backups, rollbacks, and repair plans. | **KEEP** — The administrative backbone of AntiOS CLI instance operations. |
| `manifest.py` (325 lines) | Direct (CLI-Reachable) | CLI: `doctor`, `data`; Scripts: `migrate_instance.py`; Core: `compiler`, `installation`, `provenance`, `drift_health` (14 core modules); Tests (15 suites) | Cryptographic manifest ledger manager (`.antios/manifest.json`) tracking LF-normalized SHA-256 hashes. | **KEEP** — Authoritative integrity verification ledger. |
| `provenance.py` (268 lines) | Direct (CLI-Reachable) | CLI: `cmd_data`; Core: `compiler`, `installation`, `manifest`, `doctor`, `drift_health` (9 core modules); Tests (2 suites) | Computes LF-normalized SHA-256 hashes, file sizes, and assigns artifact ownership tiers. | **KEEP** — Cryptographic utility engine for manifest generation and drift detection. |
| `lifecycle.py` (449 lines) | Internal (Core-Dependency) | Core: `installation`, `dispatch`, `orchestration`, `doctor` (11 core modules); Tests (18 suites) | System lifecycle state machine (INITIALIZING $\to$ ORIENTING $\to$ EXECUTING $\to$ VERIFYING $\to$ CONCLUDED). | **REWORK** — Re-orient from in-process state machine to declarative phase definitions; state survives in `ACTIVE_CONTEXT.md`. |
| `migration.py` (390 lines) | Script-Reachable | Scripts: `migrate_instance.py`; Core: `installation`; Tests: `test_migration_contract` (3 suites) | Schema and instance migration engine. Upgrades `.antios/` instances across versions. | **KEEP** — Supports seamless instance updates via `antios update`. |
| `subsystem.py` (109 lines) | Script-Reachable | Scripts: `navigate_repo.py`; Core: `anatomy`, `discovery`, `dispatch`, `wayfinding`, `doctor` (10 core modules); Tests (18 suites) | Metadata declarations for AntiOS subsystems. | **KEEP** — Lightweight subsystem enumeration. |
| `workflow.py` (206 lines) | Internal (Core-Dependency) | Core: `lifecycle`, `dispatch`, `orchestration`; Tests: `test_workflows` (2 suites) | Legacy workflow definitions (FEATURE, BUG, REFACTOR). | **DEPRECATE / REWORK** — Retain legacy dataclasses for test compatibility; standard engineering workflow superseded by `.agents/skills/antios-engineer/SKILL.md`. |
| `__init__.py` (1,261 lines) | Package Root | None directly (Module namespace exporter) | Canonical package namespace and public API exporter. | **REWORK** — Prune obsolete prototype exports, organize into clean public sub-packages, and reduce monolithic file size. |

---

## 8. Category 7: Quality, Verification & Proving Grounds (9 Modules, 4,888 Lines)

Modules governing test suite execution, Maker-Checker verdicts, durable test proofs, failure injection, and certification.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `gate.py` (421 lines) | Script-Reachable | Scripts: `stop_gate.py`, `inspect_repo.py`; Core: `proving_ground`, `intelligence_verifier`; Tests (13 suites) | Discovers project test runners and executes physical test processes with timeouts and exit code evaluation. | **KEEP** — Core verification logic; mirrored into `.antios/runtime/stop_gate.py` template. |
| `verdict.py` (254 lines) | Internal (Core-Dependency) | Core: `gate`, `proving_ground`; Tests (10 suites) | Structured Maker-Checker verdict model (`PASSED`, `FAILED`, `BLOCKED`, `CONDITIONAL`). | **KEEP** — Data contract for verification verdicts. |
| `project_proof.py` (450 lines) | Internal (Core-Dependency) | Core: `gate`, `learning`, `drift_health`, `release_certification`, `proving_ground` (7 core modules); Tests (8 suites) | Generates and verifies durable test proofs in `.antios/proofs/` grounded in physical test execution exit code 0. | **KEEP** — Durable physical proof engine; replaces flawed static file hashes. |
| `proving_ground.py` (924 lines) | Internal (Core-Dependency) | Core: `failure_injection`, `long_horizon`, `release_certification`; Tests (3 suites) | Multi-repository scenario harness and integration benchmark framework (tested against StudyLab, Click). | **KEEP** — Internal adversarial testing and validation framework. |
| `failure_injection.py` (607 lines) | Internal (Core-Dependency) | Core: `proving_ground`; Tests: `test_failure_injection`, `test_failure_injection_campaign` (3 suites) | Injects synthetic faults (flaky tests, corrupt files, permission drops) to certify resilience. | **KEEP** — Essential proving ground tool for adversarial certification. |
| `intelligence_verifier.py` (474 lines) | Script-Reachable | Scripts: `verify_intelligence.py`; Core: `compiler`; Tests: `test_intelligence_verification` (3 suites) | Verifies machine-generated intelligence files (`anatomy.json`, `capabilities.json`) for syntax and semantic validity. | **KEEP** — Post-adaptation verification pass. |
| `certification_audit.py` (683 lines) | Internal (Core-Dependency) | Core: `proving_ground`; Tests: `test_system_certification` (1 suite) | Formally audits AntiOS deployments against the 15 Constitutional Invariants. | **KEEP** — Automated invariant auditing engine. |
| `agent_native_certification.py` (269 lines) | Script-Reachable | Scripts: `certify_agent_native.py`; Core: `doctor`; Tests: `test_agent_native_certification` (3 suites) | Evaluates repository agent-readiness (documentation brevity, test determinism, path hygiene). | **KEEP** — Powers `antios doctor` agent-nativeness diagnostics. |
| `agent_native_score.py` (806 lines) | Internal (Core-Dependency) | Core: `agent_native_certification`, `doctor`; Tests: `test_agent_native_score` (3 suites) | Multi-dimensional scoring algorithm computing agent friction and repository ergonomics. | **KEEP** — Analytical scoring model for repository health. |

---

## 9. Category 8: Orchestration & Context Governance (8 Modules, 4,576 Lines)

Modules defining multi-agent wave orchestration, workforce contracts, context budgeting, and mission continuity.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `orchestration.py` (1,547 lines) | Internal (Core-Dependency) | Core: `dispatch`, `workforce_contract`, `proving_ground`; Tests (12 suites) | Multi-agent orchestration policies, wave collapse protocols (`INV-08`), and shallow depth enforcement. | **REWORK** — Strip out redundant custom thread pooling; align strictly with Antigravity native primitives (`invoke_subagent`, `manage_subagents`). |
| `workforce_contract.py` (319 lines) | Internal (Core-Dependency) | Core: `orchestration`; Tests: `test_workforce_contract`, `test_workforce_planner` (3 suites) | Declarative contracts defining workforce sizing: Shallow Depth Law ($\le 2$), Concurrency Ceiling ($\le 4$), Launch Budget ($\le 10$). | **KEEP** — Canonical constitutional contract for multi-agent delegation. |
| `context_budget.py` (383 lines) | Internal (Core-Dependency) | Core: `orchestration`, `context_freshness`; Tests: `test_context_budget_governor` (3 suites) | In-process context token budget calculator. | **REPLACE / REWORK** — In-process token counters die across turn resets. Replace with declarative file bounds (`AGENTS.md` $\le 40$ lines, `ACTIVE_CONTEXT.md` $\le 60$ lines) and linting in `doctor`. |
| `context_freshness.py` (266 lines) | Internal (Core-Dependency) | Core: `orchestration`, `memory`; Tests: `test_context_freshness_compaction` (3 suites) | Analyzes session staleness, amnesia risks, and triggers `docs/ACTIVE_CONTEXT.md` compaction. | **KEEP** — Logic for identifying context staleness and recommending compaction. |
| `mission_state.py` (466 lines) | Internal (Core-Dependency) | Core: `orchestration`, `recovery`, `mission_evaluation`, `proving_ground`, `long_horizon`, `evidence`; Tests (6 suites) | Tracks mission milestones, objectives, blockers, and continuity across turns. | **REWORK** — Serializes directly to `docs/ACTIVE_CONTEXT.md` instead of maintaining in-process state machines. |
| `mission_evaluation.py` (521 lines) | Internal (Core-Dependency) | Core: `mission_benchmark`, `proving_ground`, `release_certification`, `long_horizon`, `evidence` (7 core modules); Tests (7 suites) | Evaluates mission outcome quality, test pass rates, and token efficiency. | **KEEP** — Core evaluation framework for proving ground benchmarks. |
| `mission_benchmark.py` (532 lines) | Internal (Core-Dependency) | Core: `proving_ground`, `long_horizon`; Tests: `test_mission_benchmark` (4 suites) | Standardized benchmarks measuring agent mission execution speed, accuracy, and cost. | **KEEP** — Benchmark test harness. |
| `long_horizon.py` (542 lines) | Internal (Core-Dependency) | Core: `proving_ground`; Tests: `test_long_horizon` (3 suites) | Evaluates agent autonomy across long-horizon multi-turn tasks ($\ge 10$ turns) with simulated context resets. | **KEEP** — Long-horizon resilience validation harness. |

---

## 10. Category 9: Productization, Release & Diagnostics (10 Modules, 3,988 Lines)

Modules providing system diagnostics, semantic versioning, release engineering, drift detection, and controlled evolution.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `doctor.py` (509 lines) | Direct (CLI-Reachable) | CLI: `antios doctor`, `antios status`; Tests: `test_doctor`, `test_system_certification` (3 suites) | Comprehensive diagnostic engine checking installation health, runtime drift, config validity, test runner discovery, and storage status. | **KEEP** — Primary operational diagnostics command for human developers and agents. |
| `version.py` (246 lines) | Direct (CLI-Reachable) | CLI: `antios version`; Core: `installation`, `doctor`, `manifest`, `migration`, `release_engine`; Tests (5 suites) | Semantic version parser, release channel classifier, and compatibility comparator. | **KEEP** — Authoritative version registry. |
| `release_engine.py` (300 lines) | Direct (CLI-Reachable) | CLI: `antios release {check,notes}`; Tests: `test_lifecycle_productization` (1 suite) | Pre-flight release checks, git tag validation, and automated release note generation. | **KEEP** — Powers `antios release` engineering workflows. |
| `release_certification.py` (409 lines) | Internal (Core-Dependency) | Core: `release_engine`, `proving_ground`; Tests: `test_release_certification` (5 suites) | Evaluates release gates: zero failing tests, zero uncommitted merge conflicts, zero untracked runtime drift. | **KEEP** — Quality gate for production releases. |
| `drift_health.py` (581 lines) | Internal (Core-Dependency) | Core: `doctor`, `installation`, `compiler`, `manifest`, `provenance`, `release_engine`, `release_certification` (7 core modules); Tests (4 suites) | Scans installed instance files against `manifest.json` SHA-256 hashes to detect tampering or drift. | **KEEP** — Cryptographic drift detection engine embedded in `antios doctor`. |
| `evolution_governance.py` (300 lines) | Internal (Core-Dependency) | Core: `learning`, `evolution_proposal`; Tests: `test_controlled_evolution` (4 suites) | Governs autonomous rule graduation; requires explicit human authorization for rule promotion. | **KEEP** — Human-in-the-loop safety gate for project rule updates. |
| `evolution_proposal.py` (355 lines) | Internal (Core-Dependency) | Core: `evolution_governance`, `learning`, `adapter`, `capability_gap`; Tests (6 suites) | Generates structured evolution proposal cards for human review. | **KEEP** — Proposal generation mechanism for System A learning. |
| `agent_improvement.py` (543 lines) | Internal (Core-Dependency) | Core: `agent_friction`, `agent_refactoring`; Tests: `test_agent_improvement` (3 suites) | Analyzes agent execution transcripts to suggest repository friction reductions. | **KEEP** — Offline analytics engine for improving developer ergonomics. |
| `agent_friction.py` (548 lines) | Internal (Core-Dependency) | Core: `agent_improvement`, `doctor`, `agent_native_score`, `experience_analytics`; Tests (5 suites) | Quantifies friction points (repeated failed tool calls, path errors, test retry loops). | **KEEP** — Metric calculation engine for System B telemetry. |
| `agent_refactoring.py` (197 lines) | Internal (Core-Dependency) | Core: `agent_improvement`; Tests: `test_agent_refactoring` (3 suites) | Suggests codebase refactorings to improve agent autonomy. | **REWORK / CONSOLIDATE** — Consolidate with `agent_improvement.py` to eliminate unnecessary module fragmentation. |

---

## 11. Category 10: Local Engineering Intelligence & Telemetry (6 Modules, 5,550 Lines)

Modules implementing the System B centralized SQLite foundation, multi-tier privacy sanitizer, and non-blocking telemetry bridge.

| Module | Runtime Reachability | Current Consumers | Future Role | Action |
| :--- | :--- | :--- | :--- | :--- |
| `experience.py` (1,726 lines) | Direct (CLI-Reachable) | CLI: `antios data {status,set-dir,backup,restore,purge,vacuum,export}`; Core: `experience_analytics`, `telemetry_bridge`, `installation`, `doctor` (5 core modules); Tests (6 suites) | SQLite foundation (WAL mode) located outside project repositories (`<central_data>/experience.db`). Manages schema, backups, hot restores, vacuuming, and scoping. | **KEEP** — System B central persistence engine. Adheres strictly to `INV-10` and the Epistemic Firewall. |
| `experience_analytics.py` (1,141 lines) | Direct (CLI-Reachable) | CLI: `antios experience {analyze,report,export}`; Core: `doctor`; Tests: `test_experience_intelligence` (3 suites) | Statistical analytics engine computing tool success rates, session durations, friction metrics, and exporting reports. | **KEEP** — Offline analytical mining engine for human engineers. |
| `sanitizer.py` (977 lines) | Internal (Core-Dependency) | Core: `telemetry_bridge`, `experience`, `experience_analytics`; Tests: `test_telemetry_sanitizer` (6 suites) | Multi-tier fail-closed privacy sanitizer. Scrubs API keys, GitHub tokens, AWS secrets, private user paths, and internal reasoning chains. | **KEEP** — Absolute prerequisite for telemetry collection. Guarantees zero sensitive data leakage into `experience.db`. |
| `telemetry.py` (108 lines) | Direct (CLI-Reachable) | CLI: `antios telemetry status`; Scripts: `telemetry_hook.py`, `stop_gate.py`; Core: `telemetry_bridge`; Tests (4 suites) | Configuration dataclasses and enums (`TelemetryCollectionMode: ON, OFF, ANONYMIZED`). | **KEEP** — Canonical telemetry settings contracts. |
| `telemetry_bridge.py` (1,093 lines) | Direct (CLI-Reachable) | CLI: `antios telemetry ingest`; Scripts: `telemetry_hook.py`, `stop_gate.py`; Core: `experience`; Tests (3 suites) | Incremental byte-offset checkpoint parser for `transcript.jsonl`. Parses session events in $<15$ms; non-blocking fail-safe design. | **KEEP** — Event bridge connecting Antigravity raw session logs to System B storage. |
| `evidence.py` (505 lines) | Internal (Core-Dependency) | Core: `github_capability`, `learning`, `mission_evaluation`, `project_proof` (9 core modules); Tests (9 suites) | Evidence collection and formatting models for bug reproduction, issue evidence cards, and verification logs. | **KEEP** — Standardized evidence models across Core. |

---

## 12. Category 11: Scripts (Hooks & Tools) Audit (16 Scripts)

Audit of entrypoint scripts located in `framework/scripts/hooks/` and `framework/scripts/tools/`.

| Script | Runtime Reachability | Dependencies Imported | Target Deployment Status | Action |
| :--- | :--- | :--- | :--- | :--- |
| `hooks/pre_tool_guard.py` | Hook-Reachable (`.agents/hooks.json`) | None (0 framework imports; stdlib only) | Tier 3 (Compiled into `.antios/runtime/pre_tool_guard.py`) | **KEEP / CONSOLIDATE** — Standalone hook script. Identical in function to runtime template. Standardize on compiled template in target instances. |
| `hooks/stop_gate.py` | Hook-Reachable (`.agents/hooks.json`) | `framework.core.gate`, `framework.core.telemetry_bridge` | Legacy Hook (Source dependent) | **REWORK** — Target projects must NOT depend on this script; compiled `.antios/runtime/stop_gate.py` must be used instead to satisfy Runtime Closure. |
| `hooks/telemetry_hook.py` | Hook-Reachable (`.agents/hooks.json`) | `framework.core.telemetry_bridge` | Non-blocking post-tool hook | **REWORK** — Migrate to standalone stdlib wrapper or invoke via compiled CLI bridge `antios telemetry ingest`. |
| `tools/adapt_project.py` | Script-Reachable | `framework.core.adapter`, `discovery`, `config` | Source-Only Tool | **DEPRECATE** — Superseded by unified CLI command `antios adapt`. |
| `tools/audit_docs.py` | Script-Reachable | `framework.core.docaudit` | Source-Only Tool | **KEEP** — Useful standalone maintenance utility; also callable via `antios doctor`. |
| `tools/certify_agent_native.py` | Script-Reachable | `framework.core.agent_native_certification` | Source-Only Tool | **DEPRECATE** — Integrated into `antios doctor`. |
| `tools/check_changeset.py` | Script-Reachable | `framework.core.changeset`, `config` | Source-Only Tool | **KEEP** — Standalone pre-commit and CI helper script. |
| `tools/check_worktree.py` | Script-Reachable | `framework.core.worktree` | Source-Only Tool | **KEEP** — Standalone git conflict verification script. |
| `tools/dispatch_task.py` | Script-Reachable | `framework.core.dispatch` | Source-Only Tool | **REWORK** — Transition to Antigravity native subagent dispatch patterns. |
| `tools/distill_memory.py` | Script-Reachable | `framework.core.memory`, `learning` | Source-Only Tool | **KEEP** — Standalone maintenance utility for memory distillation. |
| `tools/inspect_repo.py` | Script-Reachable | `framework.core.adapter`, `config`, `gate`, `topology` | Source-Only Tool | **DEPRECATE** — Superseded by `antios status` and `antios doctor`. |
| `tools/install_project.py` | Script-Reachable | `framework.core.installation` | Precursor Installer Tool | **DEPRECATE** — Superseded by unified CLI commands `antios install`, `antios update`, `antios repair`, `antios remove`. |
| `tools/migrate_instance.py` | Script-Reachable | `framework.core.manifest`, `migration` | Source-Only Tool | **DEPRECATE** — Integrated into `antios update`. |
| `tools/navigate_repo.py` | Script-Reachable | `framework.core.wayfinding`, `knowledge`, `tool_registry` | Source-Only Tool | **KEEP** — Standalone locality inspection tool for debugging prefix trees. |
| `tools/recover_session.py` | Script-Reachable | `framework.core.recovery` | Source-Only Tool | **KEEP** — Standalone session recovery utility. |
| `tools/verify_intelligence.py` | Script-Reachable | `framework.core.intelligence_verifier` | Source-Only Tool | **DEPRECATE** — Integrated into `antios verify`. |

---

## 13. Category 12: Templates Audit (5 Templates)

Templates located in `framework/templates/` that are compiled into target project instances.

| Template | Runtime Reachability | Framework Dependencies | Target Deployment Status | Action |
| :--- | :--- | :--- | :--- | :--- |
| `runtime/pre_tool_guard.py` | Hook-Reachable (Target instances) | **Zero (0)** — 100% Python standard library | Deployed to `.antios/runtime/pre_tool_guard.py` (Tier 3) | **KEEP** — Canonical template satisfying Runtime Closure Axiom. Canonical path resolution, traversal prevention, fail-closed JSON output. |
| `runtime/stop_gate.py` | Hook-Reachable (Target instances) | **Zero (0)** — 100% Python standard library | Deployed to `.antios/runtime/stop_gate.py` (Tier 3) | **KEEP** — Canonical template satisfying Runtime Closure Axiom. Working tree conflict checks, test runner discovery, physical test execution ratchets. |
| `runtime/inspect_instance.py` | CLI-Reachable (Target instances) | **Zero (0)** — 100% Python standard library | Deployed to `.antios/runtime/inspect_instance.py` (Tier 3) | **KEEP** — Standalone instance health inspector for target projects. |
| `runtime/verify_runtime.py` | Test-Reachable / Self-Audit | **Zero (0)** — 100% Python standard library | Deployed to `.antios/runtime/verify_runtime.py` (Tier 3) | **KEEP** — Validates runtime closure and checksum integrity within target instances. |
| `skills/antios/SKILL.md` | Skill-Reachable (Antigravity platform) | Markdown / Directive specification | Deployed to `.agents/skills/antios/SKILL.md` (Tier 4) | **KEEP** — Canonical universal project-native control plane skill under AntiOS 2.0 governance. |

---

## 14. Target Instance Deployment & Runtime Closure Ledger

The following ledger establishes the exact deployment disposition of every AntiOS component when compiled into a target project workspace:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 TARGET WORKSPACE DEPLOYMENT MAPPING (TIERS)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: CANONICAL SOURCE (Upstream AntiOS repository ONLY)                  │
│   - framework/core/*.py (84 modules)                                        │
│   - framework/cli.py                                                        │
│   - tests/*.py                                                              │
│   - reports/                                                                │
│                                                                             │
│ TIER 2: MANAGED CONFIG & HOOKS (Target repository root)                     │
│   - antios.config.json (Declarative project adapter manifest)               │
│   - .agents/hooks.json (Hooks pointing to .antios/runtime/*.py)             │
│   - docs/AGENTS.md (Constitutional directives, strictly ≤ 40 lines)         │
│   - docs/ACTIVE_CONTEXT.md (Active task state, strictly ≤ 60 lines)         │
│                                                                             │
│ TIER 3: GENERATED INTELLIGENCE & RUNTIME CLOSURE (Target .antios/ dir)      │
│   - .antios/manifest.json (LF-normalized cryptographic SHA-256 ledger)      │
│   - .antios/anatomy.json (Subsystem prefix trees & locality mapping)        │
│   - .antios/runtime/pre_tool_guard.py (Zero framework imports, stdlib only) │
│   - .antios/runtime/stop_gate.py (Zero framework imports, stdlib only)      │
│   - .antios/runtime/inspect_instance.py (Self-contained diagnostics)        │
│   - .antios/runtime/verify_runtime.py (Runtime closure validator)           │
│   - .antios/proofs/*.proof.json (Durable test execution tokens)             │
│                                                                             │
│ TIER 4: OPERATING INTERFACE (Target .agents/skills/ dir)                    │
│   - .agents/skills/antios/SKILL.md (Project control plane)                  │
│   - .agents/skills/antios-engineer/SKILL.md (Engineering workflow)          │
│   - .agents/skills/antios-verifier/SKILL.md (Maker-Checker verifier)        │
│   - .agents/skills/antios-debug/SKILL.md (Systematic root-cause debug)      │
│   - .agents/skills/antios-adapt-project/SKILL.md (Adaptation procedure)     │
│                                                                             │
│ TIER 5: TARGET PROJECT CODE (100% Sovereign & Untouched)                    │
│   - Application source code (src/, lib/, app/)                              │
│   - Native test suites (tests/, spec/, __tests__/)                          │
│   - Toolchain configs (package.json, Cargo.toml, pyproject.toml)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Cross-Cutting Dependency Analysis & Migration Roadmap

### 15.1 High Fan-In Modules (Core Dependencies)
The following modules have the highest fan-in within `framework/core/` and form the bedrock that must not be disrupted during refactoring:
1. `capability.py`: 15 incoming core imports
2. `manifest.py`: 14 incoming core imports
3. `config.py`: 11 incoming core imports
4. `lifecycle.py`: 11 incoming core imports
5. `tool.py`: 11 incoming core imports
6. `discovery.py`: 10 incoming core imports
7. `subsystem.py`: 10 incoming core imports
8. `provenance.py`: 9 incoming core imports
9. `evidence.py`: 9 incoming core imports

### 15.2 Consolidation Candidates for AntiOS 2.2
1. **Consolidate Standalone Tools into CLI Subcommands**:
   - `tools/install_project.py`, `tools/migrate_instance.py`, `tools/inspect_repo.py`, `tools/certify_agent_native.py`, `tools/verify_intelligence.py` are redundant with `framework/cli.py` (`antios install`, `antios update`, `antios status`, `antios doctor`, `antios verify`). These scripts should be reduced to simple backward-compatible forwarding wrappers.
2. **Consolidate Fine-Grained Agent Suggestion Engines**:
   - Merge `agent_refactoring.py` into `agent_improvement.py`.
   - Merge `component_intelligence.py` into `anatomy.py`.
3. **Streamline Hook Declarations**:
   - Ensure development `.agents/hooks.json` points to compiled `.antios/runtime/` templates rather than source `framework/scripts/hooks/`, verifying dogfooding of the Runtime Closure Axiom.

### 15.3 Conclusion & Certification Verdict
This audit certifies that:
- **84 of 84** `framework/core/` modules are fully accounted for, classified, and analyzed for reachability.
- **16 of 16** scripts in `framework/scripts/` have clear migration dispositions.
- **5 of 5** templates in `framework/templates/` strictly satisfy the Runtime Closure Axiom (0 framework imports).
- The Four-Boundary Demarcation (`INV-10`) is rigorously upheld across all tiers.
