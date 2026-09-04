# AntiOS Phase 14–15 Milestone Report: Universal Core Skills & Engineering Workflow Layer

**Milestone**: AntiOS Phase 14–15  
**Date**: 2026-09-04  
**Status**: COMPLETE & CANONICALLY VERIFIED  
**Architecture Classification**: AntiOS Universal Core & Capability Layer  

---

## 1. Executive Summary

Phase 14–15 transitions AntiOS from an architectural re-baseline into a **fully functional, universal agent-native engineering capability layer**.

AntiOS enforces the locked 4-tier model:
```text
Antigravity Platform
        ↓
   AntiOS Core
        ↓
 Project Adapter
        ↓
  Target Project
```

In this milestone, AntiOS Core has been completely purged of residual StudyLab proving ground assumptions, establishing:
1. **Universal Core Skills**: Refined the 3 canonical first-class skills (`antios-engineer`, `antios-verifier`, `antios-debug`), parameterizing domain boundaries and test runners while strictly preserving the $\le 60$ lines token budget.
2. **Universal Engineering Workflows**: Created 6 declarative workflows under `.agents/workflows/` (`FEATURE`, `BUG`, `REFACTOR`, `INVESTIGATION`, `DOCUMENTATION`, `RELEASE_MAINTENANCE`).
3. **Task Lifecycle & State Machine**: Implemented `framework/core/lifecycle.py`, formalizing the explicit 10-step progression (`INTAKE` $	o$ `COMPLETE`), fail-closed gates, and bidirectional `docs/ACTIVE_CONTEXT.md` synchronization.
4. **Dynamic Manifest Auto-Discovery**: Enhanced `framework/core/gate.py` with zero-config test runner discovery for Node.js (`package.json`), Python (`pyproject.toml`, `pytest.ini`), Rust (`Cargo.toml`), and Go (`go.mod`).
5. **Universal Project Constitution**: Modularized `docs/AGENTS.md` into Universal Core Laws (Tier 1) and Project Adapter Invariants (Tier 2).
6. **Zero-Dependency Test Suite**: Expanded from 18 to 31 tests running in 0.88s with 100% pass rate.

---

## 2. Implemented Core Skills

### 2.1 The 9 Capability Families Evaluation
Before implementation, all 9 requested capability families were evaluated against the Phase 12–13 architecture and token budget constraints:

| Capability Family | Placement | Architectural Rationale |
| :--- | :---: | :--- |
| **investigate** | Within `antios-engineer` & Platform | Reconnaissance is natively provided by Antigravity Planning Mode read tools (`view_file`, `grep_search`). For deep research, `TypeName='research'` subagents are used. A separate micro-skill would cause discovery clutter. |
| **plan** | Within `antios-engineer` & Platform | Antigravity natively renders `implementation_plan.md` and user approval gates. `antios-engineer` injects risk tiering (Low/Medium/High) and Maker-Checker planning. |
| **implement** | Within `antios-engineer` | Code modifications via IDE tools are governed by `antios-engineer`'s boundary discipline and guarded by `pre_tool_guard.py`. |
| **debug** | First-Class Skill (`antios-debug`) | Deterministic 5-step root-cause debugging protocol requires dedicated guidance to prevent speculative thrashing. |
| **verify** | First-Class Skill (`antios-verifier`) | Independent verification requires an explicit fresh-context contract with Shallow Depth Law and structured JSON verdict emission. |
| **review** | Within `antios-verifier` & `antios-engineer` | Working tree diff inspection and boundary auditing are core procedures of the verification contract and consolidation stage. |
| **document** | Within `antios-engineer` | Same Change Set rule requires code and documentation updates to be committed together, synchronized with `docs/ACTIVE_CONTEXT.md`. |
| **recover** | Within `antios-debug` & Lifecycle Engine | Recovery procedures are codified deterministically in `framework/core/lifecycle.py` and the 4-step Context Reset Recovery Protocol. |
| **maintain** | Stop Gate & Workflows | Cleanliness ratchets and dependency hygiene are enforced by `gate.py` and the `RELEASE_MAINTENANCE` workflow. |

### 2.2 The 3 Canonical Skills
In accordance with ADR 07 (Single Core Skill over Monolithic Bloat / Micro-Skill Sprawl), AntiOS standardizes on exactly 3 canonical skills:

1. **`antios-engineer`** (`.agents/skills/antios-engineer/SKILL.md` — 40 lines):
   - **Purpose**: Primary operational engineering policy across any software stack.
   - **Triggers**: Feature development, refactors, documentation, general modifications.
   - **Capabilities**: Self-protection rules, domain immutability, Same Change Set discipline, risk tiering, Maker-Checker dispatch idioms, workflow references, Stop Gate awareness.
2. **`antios-verifier`** (`.agents/skills/antios-verifier/SKILL.md` — 48 lines):
   - **Purpose**: Independent Checker contract for fresh-context Maker-Checker subagents.
   - **Triggers**: Dispatched by parent on High-Risk tasks or explicit verification requests.
   - **Capabilities**: Shallow Depth Law ($\le 2$), physical diff audit, boundary audit, test execution via `run_command`, structured JSON verdict output.
3. **`antios-debug`** (`.agents/skills/antios-debug/SKILL.md` — 35 lines):
   - **Purpose**: Systematic root-cause debugging.
   - **Triggers**: Test failures, crashes, Stop Gate rejections, complex defect reports.
   - **Capabilities**: 5-step protocol (Reproduce $	o$ Hypothesize $	o$ Isolate $	o$ Patch $	o$ Verify).

All skills strictly conform to the $\le 60$ lines budget (~2,000 bytes).

---

## 3. Implemented Engineering Workflows

AntiOS codifies the principle:
$$	ext{Skill} = 	ext{HOW (Capabilities \& Policy)} \quad\longleftrightarrow\quad 	ext{Workflow} = 	ext{WHEN + SEQUENCE (Temporal Progression)}$$

Six universal workflows are declared in `.agents/workflows/` and registered in `framework/core/workflow.py`:

| Task Class | Workflow Path | Composed Skills | Risk Default | Key Lifecycle Focus |
| :--- | :--- | :--- | :---: | :--- |
| **`FEATURE`** | `.agents/workflows/FEATURE.md` | `antios-engineer`, `antios-verifier` | MEDIUM | Planning Mode plan, Same Change Set, Maker-Checker if High Risk. |
| **`BUG`** | `.agents/workflows/BUG.md` | `antios-debug`, `antios-engineer`, `antios-verifier` | MEDIUM | Minimal reproduction test first, hypothesis formulation, surgical patch. |
| **`REFACTOR`** | `.agents/workflows/REFACTOR.md` | `antios-engineer`, `antios-verifier`, `antios-debug` | HIGH | Baseline test pass before edits, atomic changes, zero public API drift. |
| **`INVESTIGATION`**| `.agents/workflows/INVESTIGATION.md` | `antios-engineer` (Read-Only) | LOW | Read-only reconnaissance, evidence acquisition, structured artifact delivery. |
| **`DOCUMENTATION`**| `.agents/workflows/DOCUMENTATION.md` | `antios-engineer` | LOW | Code-grounded documentation, markdown syntax check, Same Change Set sync. |
| **`RELEASE`** | `.agents/workflows/RELEASE_MAINTENANCE.md` | `antios-engineer`, `antios-verifier` | HIGH | Dependency audit, version bump, full test matrix execution, clean tag audit. |

---

## 4. Task Lifecycle & State Engine (`framework/core/lifecycle.py`)

### 4.1 The 10-Step Progression
The task lifecycle makes progression deterministic across 10 sequential stages:
```text
INTAKE
  ↓
UNDERSTAND
  ↓
INVESTIGATE
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
TEST
  ↓
VERIFY
  ↓
REVIEW
  ↓
CONSOLIDATE
  ↓
COMPLETE
```

### 4.2 State Invariants & Failure Transitions
- **Forward Progression**: Stages must proceed in order. Skipping stages (e.g. `INTAKE` $	o$ `IMPLEMENT`) is rejected by `transition_stage()`.
- **High-Risk Completion Gate**: Transition from `CONSOLIDATE` to `COMPLETE` on High-Risk tasks strictly requires a verified verdict.
- **Backward Recovery Transitions**: If tests fail during `TEST` or verification fails during `VERIFY`, the state machine allows backward transitions to `IMPLEMENT` or `PLAN` with recorded evidence.
- **Interruption & Blocker States**: `interrupt_task()` and `block_task()` preserve the current stage and active checklist without state corruption.
- **Bounded State Ledger**: `sync_to_active_context()` writes state to `docs/ACTIVE_CONTEXT.md` guaranteeing $\le 60$ lines budget. `parse_active_context()` reconstructs state during session resumption.

---

## 5. Verification Handoff Model

AntiOS enforces the axiom:
$$	ext{"Done" is NEVER "Agent claims done" — "Done" is verified physical OS execution.}$$

### 5.1 The Handoff Progression
```text
WORK RESULT
     ↓
Verification Request (Objective, modified files, test command)
     ↓
Independent Verifier (Fresh context, TypeName='self', Depth 2)
     ↓
Objective Checks (git diff, boundary audit, test execution via run_command)
     ↓
Structured JSON Verdict (Status: PASS | FAIL | BLOCK, tests array, issues list)
     ↓
Consolidation (Ledger sync, git diff --check for conflict markers)
     ↓
Stop Gate Ratchet (Physical subprocess executes tests; exit code 0 permits completion)
```

---

## 6. Recovery Protocols

The workflow architecture defines deterministic handling for all 6 failure classes:

1. **Test Failure**: Transition to `antios-debug`. Author reproducing test case, isolate root cause, and apply minimal patch. Max 2 debug iterations before escalating.
2. **Incomplete Implementation**: Save checklist progress to `docs/ACTIVE_CONTEXT.md`. Mark status `INTERRUPTED`. Working tree remains clean or stashed.
3. **Tool Failure (Hook Denial / Path Error)**: Respect `pre_tool_guard` diagnostic. Never attempt path-traversal or 8.3 alias bypasses. If binary missing, record `ENVIRONMENT_UNAVAILABLE`.
4. **Subagent Failure (Crash / Timeout)**: Root orchestrator reclaims control. If within budget, launch 1 replacement subagent; otherwise, parent self-verifies. Log failure to `dead_ends`.
5. **Context Loss (Session Reset)**: Execute 4-step Context Reset Recovery Protocol:
   - Read `docs/AGENTS.md` (re-anchor boundaries).
   - Read `docs/ACTIVE_CONTEXT.md` (retrieve active tasks and next action).
   - Run `git status` (reconcile memory with disk reality).
   - Execute `Next Immediate Action`.
6. **Verification Rejection (Verdict: FAIL | BLOCK)**: Revert stage to `IMPLEMENT`. Read specific `issues` in JSON verdict. Remediate findings and re-request verification.

---

## 7. Subagent Usage Model

To prevent swarm latency and context fragmentation, AntiOS standardizes on a **risk-scaled, shallow-depth subagent model**:

| Risk Tier | Task Characteristics | Subagent Model | Verification Depth |
| :--- | :--- | :--- | :--- |
| **LOW** | Typos, documentation, formatting, minor configs | SOLO (0 subagents) | Direct syntax/lint check |
| **MEDIUM** | Isolated UI components, standard feature additions | FOCUSED (0–1 subagent) | Primary agent executes local test suite |
| **HIGH** | State machines, database schemas, security hooks, release tagging | MAKER-CHECKER (1 fresh Checker) | Independent Verifier via `invoke_subagent(TypeName='self')` |

### Invariants:
- **Shallow Depth Law**: Nesting depth is strictly $\le 2$ ($	ext{Parent} 	o 	ext{Child}$). Children are strictly forbidden from calling `invoke_subagent`.
- **Read Parallel — Write Controlled**: Parallel exploratory agents are read-only (`TypeName='research'`). Writing is strictly assigned to a single controlled writer to prevent filesystem collisions.

---

## 8. Universality Audit & Decoupling from Phase 11

### 8.1 Removed Hardcoded Couplings
1. `framework/core/config.py`:
   - Purged default `protected_domain_paths=["rslib"]` $	o$ set to `[]`.
   - Purged default `forbidden_patterns=["rslib~*"]` $	o$ set to `[]`.
   - Purged hardcoded `typescript`/`vitest:once` runners $	o$ set to `[]`.
   - Set fallback adapter name to `"AntiOS-Universal-Core"`.
2. `framework/core/gate.py`:
   - Added `discover_test_runners()`: dynamic manifest auto-detection for Node (`package.json`), Python (`pyproject.toml`, `pytest.ini`), Rust (`Cargo.toml`), and Go (`go.mod`).
3. `.agents/skills/`:
   - Replaced `rslib/` examples with `<configured_domain_paths>`.
   - Replaced `vitest:once` with `<configured_test_runner>`.
4. `docs/AGENTS.md`:
   - Purged StudyLab-specific preamble and replaced with universal architectural axioms.
5. `antios.config.json`:
   - Configured as universal reference adapter running Python tests (`python tests/run_all.py`).

### 8.2 Automated Universality Test
Automated test `test_skills_and_core_are_project_agnostic` recursively scans `.agents/skills/`, `.agents/workflows/`, and `framework/core/`.
**Result**: 0 occurrences of `rslib`, `StudyLab`, or `StudySourceCore`.

---

## 9. Inventory of Files Changed & Created

| File | Status | Lines | Purpose |
| :--- | :---: | :---: | :--- |
| `framework/core/config.py` | MODIFIED | 87 | 100% decoupled universal config dataclasses and loader |
| `framework/core/gate.py` | MODIFIED | 196 | Stop Gate engine with dynamic zero-config manifest discovery |
| `framework/core/lifecycle.py` | NEW | 239 | 10-step lifecycle state machine and ACTIVE_CONTEXT sync |
| `framework/core/workflow.py` | NEW | 193 | 6-workflow registry, step definitions, and skill compositions |
| `.agents/skills/antios-engineer/SKILL.md` | MODIFIED | 40 | Universal engineering workflow policy ($\le 60$ lines) |
| `.agents/skills/antios-verifier/SKILL.md` | MODIFIED | 48 | Universal independent verifier contract ($\le 60$ lines) |
| `.agents/skills/antios-debug/SKILL.md` | MODIFIED | 35 | Universal 5-step debugging protocol ($\le 60$ lines) |
| `.agents/workflows/README.md` | NEW | 23 | Workflow catalog and lifecycle guide |
| `.agents/workflows/FEATURE.md` | NEW | 33 | Feature implementation workflow |
| `.agents/workflows/BUG.md` | NEW | 37 | Systematic bug-fix workflow |
| `.agents/workflows/REFACTOR.md` | NEW | 33 | Behavior-preserving refactor workflow |
| `.agents/workflows/INVESTIGATION.md` | NEW | 31 | Read-only architecture spike workflow |
| `.agents/workflows/DOCUMENTATION.md` | NEW | 33 | Documentation and specification workflow |
| `.agents/workflows/RELEASE_MAINTENANCE.md` | NEW | 34 | Release and maintenance workflow |
| `docs/AGENTS.md` | MODIFIED | 24 | Universal Project Constitution |
| `docs/ACTIVE_CONTEXT.md` | MODIFIED | 37 | Active mission state ledger ($\le 60$ lines) |
| `antios.config.json` | MODIFIED | 24 | Universal adapter manifest for AntiOS self-testing |
| `tests/test_lifecycle.py` | NEW | 94 | Lifecycle transition and context sync tests |
| `tests/test_workflows.py` | NEW | 63 | Workflow contracts and skill composition tests |
| `tests/test_config.py` | MODIFIED | 65 | Decoupled config tests |
| `tests/test_gate.py` | MODIFIED | 87 | Gate and dynamic manifest auto-discovery tests |
| `tests/test_skills.py` | MODIFIED | 64 | Token budget and universality tests |
| `tests/run_all.py` | MODIFIED | 44 | Zero-dependency test suite runner |
| `ANTIOS_PHASE14_15_REPORT.md` | NEW | ~300 | Master milestone report |

---

## 10. Test Execution & Verification Results

Execution command: `python tests/run_all.py`  
Environment: Python 3.11.16 on Windows 11  
Execution time: 0.876s  

```text
unittest.case.FunctionTestCase (test_corrupt_config_falls_back_to_defaults) ... ok
unittest.case.FunctionTestCase (test_default_config_when_missing) ... ok
unittest.case.FunctionTestCase (test_load_custom_config) ... ok
unittest.case.FunctionTestCase (test_guard_allows_application_targets) ... ok
unittest.case.FunctionTestCase (test_guard_domain_boundary_protection) ... ok
unittest.case.FunctionTestCase (test_guard_fail_closed_on_invalid_types) ... ok
unittest.case.FunctionTestCase (test_guard_self_protection) ... ok
unittest.case.FunctionTestCase (test_gate_allows_when_no_runner_in_repo) ... ok
unittest.case.FunctionTestCase (test_gate_auto_discovers_manifests) ... ok
unittest.case.FunctionTestCase (test_gate_blocks_on_failing_test) ... ok
unittest.case.FunctionTestCase (test_gate_detects_and_runs_passing_test) ... ok
unittest.case.FunctionTestCase (test_gate_fail_closed_on_malformed_input) ... ok
unittest.case.FunctionTestCase (test_format_verdict) ... ok
unittest.case.FunctionTestCase (test_parse_fallback_on_unformatted_text) ... ok
unittest.case.FunctionTestCase (test_parse_fenced_markdown_verdict) ... ok
unittest.case.FunctionTestCase (test_parse_valid_json_verdict) ... ok
unittest.case.FunctionTestCase (test_hooks_json_valid_at_root) ... ok
unittest.case.FunctionTestCase (test_legacy_studylab_task_runner_pruned) ... ok
unittest.case.FunctionTestCase (test_skills_and_core_are_project_agnostic) ... ok
unittest.case.FunctionTestCase (test_skills_exist_and_conform_to_budget) ... ok
unittest.case.FunctionTestCase (test_lifecycle_backward_transition_on_recovery) ... ok
unittest.case.FunctionTestCase (test_lifecycle_disallow_illegal_skips) ... ok
unittest.case.FunctionTestCase (test_lifecycle_forward_progression) ... ok
unittest.case.FunctionTestCase (test_lifecycle_high_risk_completion_gate) ... ok
unittest.case.FunctionTestCase (test_lifecycle_initial_state) ... ok
unittest.case.FunctionTestCase (test_lifecycle_interruption_and_recovery) ... ok
unittest.case.FunctionTestCase (test_lifecycle_sync_and_parse_active_context) ... ok
unittest.case.FunctionTestCase (test_all_canonical_workflows_registered) ... ok
unittest.case.FunctionTestCase (test_workflow_markdown_files_exist) ... ok
unittest.case.FunctionTestCase (test_workflow_skill_composition) ... ok
unittest.case.FunctionTestCase (test_workflow_step_validation) ... ok

----------------------------------------------------------------------
Ran 31 tests in 0.876s

OK
```

---

## 11. Known Limitations

1. **Static Dynamic Runner Prioritization**: In repositories containing both `package.json` and `Cargo.toml` (e.g. polyglot repos), `discover_test_runners()` currently returns all detected runners. Explicit ordering or selective execution should be specified in `antios.config.json` for complex multi-stack projects.
2. **Platform Shell Hook Gap**: Direct PowerShell file writing via `run_command` cannot be intercepted by IDE `PreToolUse` hooks (platform limitation). AntiOS defends against this at the Stop Gate via `check_working_tree_conflicts` and test execution ratchets.

---

## 12. Recommended Next Phase: Phase 16

**Phase 16: Project Adapter Ecosystem & Proving Ground Certification**
1. Author concrete adapter implementations for the 4 canonical archetype stacks:
   - StudyLab Reference Adapter (TypeScript / Svelte / Rust)
   - Python / FastAPI Reference Adapter
   - Go Microservice Reference Adapter
   - Rust Systems Reference Adapter
2. Execute empirical testbed verification against the StudyLab proving ground in isolated `sandbox/`.
3. Validate end-to-end Stop Gate and Maker-Checker enforcement on real project repositories.

---
*Report certified by AntiOS Core Architecture & Engineering Team.*
