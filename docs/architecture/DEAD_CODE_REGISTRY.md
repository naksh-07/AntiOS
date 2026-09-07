# AntiOS 3.0 Dead Code & Legacy Runtime Registry

**Document**: `docs/architecture/DEAD_CODE_REGISTRY.md`  
**Status**: CANONICAL STAGE 1 INVENTORY  
**Version**: 3.0.0-STAGE1  
**Authority**: Grounded in `docs/architecture/LEGACY_RUNTIME_AUDIT.md`, `ANTIOS_3_ARCHITECTURE.md`, and `MIGRATION_MATRIX.md`.  
**Execution Law**: **INVENTORY ONLY — NOT A DELETION CAMPAIGN**.

---

## 1. Executive Summary & Forensic Context

During AntiOS 2.x development, the framework attempted to build an in-process agent operating system (state machines, custom task schedulers, in-memory context token counters, and simulated runtime components) alongside Antigravity. However, empirical research (`RESEARCH_01` through `RESEARCH_04`) revealed that Antigravity executes out-of-process as an autonomous LLM loop. As a result:

- **82 of 84 Python modules** (41,282 lines) in `framework/core/` were never invoked during active Antigravity agent runtime.
- Only 14 modules are CLI-reachable.
- Only 2 modules are hook-reachable.
- 83 modules are test-reachable in `tests/run_all.py` (preserving the 1,086-test verification suite).

Stage 1 strictly adheres to the **Ratchet Principle** (`MIGRATION_PLAN.md` §1.2):
> **All existing modules are frozen and preserved without mutation during Stage 1 to guarantee 100% pass rate across the baseline test suite. No files are deleted.**

This registry establishes architectural visibility into legacy code, prevents accidental reactivation of obsolete abstractions, and defines the migration disposition for future stages.

---

## 2. Classification Taxonomy

Each legacy module is classified according to its reachability and future disposition:

| Classification | Meaning | Stage 1 Policy |
| :--- | :--- | :--- |
| `RUNTIME_INVOKED` | Invoked during active Antigravity session hooks | Maintain active hook scripts |
| `CLI_INVOKED` | Invoked directly through `antios` CLI subcommands | Retain and maintain CLI entrypoints |
| `HOOK_INVOKED` | Invoked synchronously via `.agents/hooks.json` | Retain, enforce stdlib-only closure |
| `TEST_ONLY` | Reachable exclusively through test suite execution | **FROZEN** — preserve to keep test suite green |
| `CANDIDATE_FOR_CONSOLIDATION` | Functional utility with overlapping responsibility | Mark for consolidation in later stages |
| `OBSOLETE_FROZEN` | In-process state machines or simulated runtimes | **FROZEN** — banned from new imports |
| `UNCERTAIN` | Ambiguous usage requiring further trace analysis | Retained under investigation |

---

## 3. Comprehensive Inventory of `framework/core/` (84 Modules)

### Category 1: Governance & Boundaries (7 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `guard.py` | 174 | `HOOK_INVOKED` / Core-Internal | Active | `KEEP` | Path canonicalization and traversal checks. |
| `governance.py` | 149 | Core-Internal | Active | `KEEP` | Immutable core zone boundary definitions. |
| `changeset.py` | 255 | `CLI_INVOKED` / Script-Reachable | Active | `KEEP` | Git working tree diff inspection. |
| `worktree.py` | 332 | `CLI_INVOKED` / Script-Reachable | Active | `KEEP` | Git conflict marker detector (`<<<<<<<`). |
| `runtime_contract.py` | 266 | Core-Internal | Active | `KEEP` | Runtime Closure Axiom validator. |
| `two_way_contract.py` | 314 | Core-Internal | Active | `KEEP` | Core vs Adapter separation rules. |
| `architecture_freeze.py` | 573 | `CLI_INVOKED` (`antios issue triage`) | Active | `KEEP` | Constitutional invariant evaluation. |

### Category 2: Repository Intelligence & Adaptation (8 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `adapter.py` | 546 | `CLI_INVOKED` (`antios adapt`) | Active | `KEEP` | Adapter generator for `antios.config.json`. |
| `discovery.py` | 1,180 | `CLI_INVOKED` (`antios adapt`, `doctor`) | Active | `REFACTOR` | Manifest/test runner discovery. Replaced by `framework/compiler/`. |
| `profile.py` | 274 | Core-Internal | Active | `KEEP` | Project profile dataclass models. |
| `topology.py` | 590 | Script-Reachable | Active | `KEEP` | Monorepo/workspace boundary detector. |
| `anatomy.py` | 675 | Core-Internal | Frozen | `REPLACE` | Prefix trees. Replaced by `.agents/routes.json`. |
| `component_intelligence.py` | 173 | Core-Internal | Frozen | `CONSOLIDATE` | Component coupling analysis. |
| `universal_adoption.py` | 613 | Core-Internal (`antios install`) | Active | `KEEP` | Migration orchestration for diverse repos. |
| `config.py` | 131 | `CLI_INVOKED` / Script-Reachable | Active | `KEEP` | Parser for `antios.config.json`. |

### Category 3: Memory, Wayfinding & Learning (7 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `memory.py` | 1,004 | Script-Reachable | Active | `KEEP` | Bounds `ACTIVE_CONTEXT.md` ($\le 60$ lines). |
| `wayfinding.py` | 363 | Script-Reachable | Frozen | `REPLACE` | Inverted word index. Superseded by `routes.json`. |
| `knowledge.py` | 901 | Script-Reachable | Frozen | `REPLACE` | 3-tier context disclosure logic. |
| `learning.py` | 1,194 | Script-Reachable | Frozen | `REWORK` | System A evidence ladder. |
| `docaudit.py` | 290 | Script-Reachable | Active | `KEEP` | Documentation link and path validator. |
| `documentation_compiler.py` | 450 | Core-Internal | Frozen | `REPLACE` | Emitted legacy markdown. Superseded by `emit.py`. |
| `recovery.py` | 458 | Script-Reachable | Active | `KEEP` | Session state reconstruction after amnesia. |

### Category 4: Capability & Tool Hierarchy (13 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `capability.py` | 302 | `CLI_INVOKED` (`antios doctor`) | Active | `KEEP` | Capability dataclass definitions. |
| `capability_registry.py` | 689 | Core-Internal | Frozen | `CONSOLIDATE` | Standard capability registry. |
| `capability_router.py` | 537 | Script-Reachable | Frozen | `REPLACE` | In-process task router. Superseded by Antigravity. |
| `capability_pack.py` | 133 | Core-Internal | Frozen | `DEPRECATE` | Prompt injection packs. |
| `capability_gap.py` | 302 | Core-Internal (`antios doctor`) | Active | `KEEP` | Missing tool diagnostic engine. |
| `tool.py` | 322 | Script-Reachable | Active | `KEEP` | Tool classification models. |
| `tool_registry.py` | 870 | Script-Reachable | Frozen | `CONSOLIDATE` | Central tool registry. |
| `tool_policy.py` | 813 | Script-Reachable | Frozen | `DEPRECATE` | Custom tool priority enforcer. |
| `tool_pack.py` | 137 | Script-Reachable | Frozen | `DEPRECATE` | Tool bundling dataclasses. |
| `tool_gap.py` | 293 | Core-Internal (`antios doctor`) | Active | `KEEP` | Tool availability gap detector. |
| `provider.py` | 129 | Core-Internal | Active | `KEEP` | Tool provider abstractions. |
| `git_capability.py` | 222 | `CLI_INVOKED` (`antios doctor`, `release`) | Active | `KEEP` | Native git CLI operations wrapper. |
| `github_capability.py` | 270 | `CLI_INVOKED` (`antios issue`) | Active | `KEEP` | GitHub issue card formatter. |

### Category 5: Agent Topology & Dispatch (7 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `agent_role.py` | 283 | Core-Internal | Active | `KEEP` | Role definition models (Maker, Checker). |
| `agent_topology.py` | 435 | Script-Reachable | Frozen | `DEPRECATE` | In-process topology simulator. |
| `agent_router.py` | 284 | Core-Internal | Frozen | `DEPRECATE` | Custom task dispatch router. |
| `agent_routing_pack.py` | 108 | Core-Internal | Frozen | `DEPRECATE` | Prompt pack models. |
| `dispatch.py` | 684 | Script-Reachable | Frozen | `REWORK` | Superseded by Antigravity native subagents. |
| `specialist_generator.py` | 264 | Core-Internal | Frozen | `REWORK` | Generates specialized subagent prompts. |
| `skill_generator.py` | 242 | Core-Internal | Active | `KEEP` | Compiles `.agents/skills/` interfaces. |

### Category 6: Lifecycle, Compilation & Runtime (9 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `compiler.py` | 368 | Core-Internal | Frozen | `REPLACE` | Legacy boundary compiler. Preserved for tests; superseded by `framework/compiler/`. |
| `installation.py` | 680 | `CLI_INVOKED` (`install`, `update`, etc.) | Active | `KEEP` | Installation lifecycle management. |
| `manifest.py` | 325 | `CLI_INVOKED` (`antios doctor`, `data`) | Active | `KEEP` | Cryptographic manifest ledger. |
| `provenance.py` | 268 | `CLI_INVOKED` (`antios data`) | Active | `KEEP` | SHA-256 hash calculation and ownership. |
| `lifecycle.py` | 449 | Core-Internal | Frozen | `REWORK` | In-process lifecycle state machine. |
| `migration.py` | 390 | Script-Reachable | Active | `KEEP` | Schema and instance migration. |
| `subsystem.py` | 109 | Script-Reachable | Frozen | `REPLACE` | Legacy subsystem enumeration. |
| `workflow.py` | 206 | Core-Internal | Frozen | `DEPRECATE` | Superseded by `.agents/skills/antios-engineer/`. |
| `__init__.py` | 1,261 | Package Namespace | Active | `REWORK` | Monolithic export namespace. |

### Category 7: Quality, Verification & Proving Grounds (9 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `gate.py` | 421 | `HOOK_INVOKED` (`stop_gate.py`) | Active | `KEEP` | Physical test process runner and exit code auditor. |
| `verdict.py` | 254 | Core-Internal | Active | `KEEP` | Maker-Checker verdict models. |
| `project_proof.py` | 450 | Core-Internal | Active | `KEEP` | Durable test execution tokens in `.antios/proofs/`. |
| `proving_ground.py` | 924 | Core-Internal | Active | `KEEP` | Multi-scenario integration benchmark harness. |
| `failure_injection.py` | 607 | Core-Internal | Active | `KEEP` | Synthetic fault injection for resilience testing. |
| `intelligence_verifier.py` | 474 | Script-Reachable | Active | `KEEP` | Machine-generated JSON validator. |
| `certification_audit.py` | 683 | Core-Internal | Active | `KEEP` | Invariant audit engine. |
| `agent_native_certification.py` | 269 | Script-Reachable | Active | `KEEP` | Repository agent-readiness audit. |
| `agent_native_score.py` | 806 | Core-Internal | Active | `KEEP` | Friction scoring algorithm. |

### Category 8: Orchestration & Context Governance (8 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `orchestration.py` | 1,547 | Core-Internal | Frozen | `OBSOLETE_FROZEN` | Custom thread pooling & agent orchestration loop. Obsolete under Antigravity. |
| `workforce_contract.py` | 319 | Core-Internal | Active | `KEEP` | Constitutional sizing contract ($\le 4$ concurrent, $\le 10$ launches). |
| `context_budget.py` | 383 | Core-Internal | Frozen | `OBSOLETE_FROZEN` | In-process token calculator. Dies across turn resets. |
| `context_freshness.py` | 266 | Core-Internal | Active | `KEEP` | Analyzes session staleness and amnesia risk. |
| `mission_state.py` | 466 | Core-Internal | Frozen | `OBSOLETE_FROZEN` | In-process state machine. Replaced by `ACTIVE_CONTEXT.md`. |
| `mission_evaluation.py` | 521 | Core-Internal | Active | `KEEP` | Outcome evaluation and test pass rates. |
| `mission_benchmark.py` | 532 | Core-Internal | Active | `KEEP` | Benchmark execution harness. |
| `long_horizon.py` | 542 | Core-Internal | Active | `KEEP` | Multi-turn resilience validator. |

### Category 9: Productization, Release & Diagnostics (10 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `doctor.py` | 509 | `CLI_INVOKED` (`doctor`, `status`) | Active | `KEEP` | Operational diagnostics command. |
| `version.py` | 246 | `CLI_INVOKED` (`antios version`) | Active | `KEEP` | Version and channel classifier. |
| `release_engine.py` | 300 | `CLI_INVOKED` (`antios release`) | Active | `KEEP` | Pre-flight release checks and notes. |
| `release_certification.py` | 409 | Core-Internal | Active | `KEEP` | Release gate validator. |
| `drift_health.py` | 581 | Core-Internal (`antios doctor`) | Active | `KEEP` | Cryptographic drift detection engine. |
| `evolution_governance.py` | 300 | Core-Internal | Active | `KEEP` | Human-in-the-loop rule promotion gate. |
| `evolution_proposal.py` | 355 | Core-Internal | Active | `KEEP` | Evolution proposal card generator. |
| `agent_improvement.py` | 543 | Core-Internal | Active | `KEEP` | Transcript analysis for repository ergonomics. |
| `agent_friction.py` | 548 | Core-Internal | Active | `KEEP` | Quantifies repeated tool failures. |
| `agent_refactoring.py` | 197 | Core-Internal | Frozen | `CONSOLIDATE` | Codebase refactoring suggestions. |

### Category 10: Local Engineering Intelligence & Telemetry (6 Modules)
| Module | Lines | Reachability Classification | Stage 1 Status | Migration Disposition | Notes |
| :--- | ---: | :--- | :--- | :--- | :--- |
| `experience.py` | 1,726 | `CLI_INVOKED` (`antios data`) | Active | `KEEP` | Central SQLite persistence (`experience.db`). |
| `experience_analytics.py` | 1,141 | `CLI_INVOKED` (`antios experience`) | Active | `KEEP` | Tool success rates & telemetry mining. |
| `sanitizer.py` | 977 | Core-Internal | Active | `KEEP` | Fail-closed secret & privacy scrubber. |
| `telemetry.py` | 108 | `CLI_INVOKED` (`antios telemetry`) | Active | `KEEP` | Telemetry configuration models. |
| `telemetry_bridge.py` | 1,093 | `CLI_INVOKED` (`antios telemetry ingest`) | Active | `KEEP` | Byte-offset parser for `transcript.jsonl`. |
| `evidence.py` | 505 | Core-Internal | Active | `KEEP` | Standardized evidence models. |

---

## 4. Anti-Reactivation Directives for Stage 1 & Beyond

To prevent regression and eliminate cognitive clutter:

1. **No New Imports of Obsolete In-Process Modules**:
   New code in `framework/compiler/`, `framework/hooks/`, or skills must **NEVER** import:
   - `framework.core.orchestration` (obsolete thread runner)
   - `framework.core.mission_state` (obsolete in-process state)
   - `framework.core.context_budget` (obsolete in-process token counter)
   - `framework.core.compiler` (legacy boundary compiler; use `framework.compiler` instead)
2. **Preserve Baseline Tests**:
   Existing tests in `tests/` that exercise these modules remain untouched during Stage 1. They serve as backwards compatibility tests and regression guards.
3. **Formal Consolidation in Later Stages**:
   Dead and obsolete modules will be consolidated or archived in Stage 4 according to the schedule in `MIGRATION_PLAN.md`.
