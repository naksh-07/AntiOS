# AntiOS 3.0 Migration & Implementation Plan
## The Authoritative 5-Stage Engineering Roadmap from AntiOS 2.x to AntiOS 3.0

**Status**: CANONICAL MIGRATION SPECIFICATION  
**Document Version**: 3.0.0-PROPOSED  
**Authority**: Architecture Review Board / Core Engineering  
**Target Architecture**: [`docs/architecture/ANTIOS_3_ARCHITECTURE.md`](./ANTIOS_3_ARCHITECTURE.md)  
**Date**: September 2026  
**Classification**: Production-Grade Implementation Roadmap  

---

## 1. Executive Overview & Migration Principles

### 1.1 The Imperative for Migration
Prior iterations of AntiOS (v1.x through v2.1) established critical physical security assets—most notably the **Physical Stop Gate (`gate.py`)** and **PreToolUse Guard (`guard.py`)** which pass 1,086 automated unit tests today. 

However, the empirical research findings documented in `docs/research/` (`RESEARCH_01` through `RESEARCH_04`) revealed that large portions of AntiOS were built on **disproven architectural assumptions**:
1. **The In-Process Python Runtime Illusion**: 82 of 84 Python modules in `framework/core/` were never executed by Antigravity during real agent sessions.
2. **The Telemetry Import Contradiction**: Enforcing `RuntimeClosureContract` (zero framework imports in target projects) resulted in target project adaptations stripping telemetry completely, rendering the Central Experience Store idle.
3. **The Multi-Resource / Multi-Repo Gap**: Hooks hardcoded `workspacePaths[0]`, breaking in multi-folder workspaces and multi-repo project containers.
4. **The Unguided Grep Flood**: Native agents wasted thousands of tokens per turn on lexical rediscovery because the project lacked a compact subsystem route map.

AntiOS 3.0 restructures the platform into an **Agent-Native Project Environment Compiler and Governance Plane**.

### 1.2 The Five Constitutional Migration Principles
1. **Zero Test Regressions (Ratchet Principle)**: The existing 1,086 unit tests in `tests/run_all.py` must remain green across every migration stage.
2. **Additive Evolution**: New compiler and wayfinding capabilities are introduced alongside existing hooks before deprecating legacy modules.
3. **Zero Framework Pollution (INV-11)**: No stage may introduce third-party dependencies or runtime framework imports into target repositories.
4. **Zero Background Daemons (INV-15)**: All freshness and maintenance mechanisms must execute strictly within synchronous lifecycle turn hooks (<100ms) or one-shot CLI commands.
5. **Maker-Checker Verified Progress**: Every stage requires independent verification before being certified as complete.

---

## 2. 5-Stage Migration Master Sequence

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          ANTIOS 3.0 FIVE-STAGE MIGRATION                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ STAGE 0: Architecture Reconstruction & Project Hygiene (CURRENT BASELINE)              │
│   • Synthesize Research 1–4 into Canonical Architecture & Migration Plan               │
│   • Verify 1,086 / 1,086 unit tests passing; clean untracked test debris               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                           │ (Stage 0 Gate Passed)                      │
│                                           ▼                                            │
│ STAGE 1: Project Environment Compiler & Project Intelligence                           │
│   • Build `antios compile` CLI & static compiler engine                                │
│   • Emit `.agents/routes.json` (0-turn route maps) & AST symbol outlines               │
│   • Isolate and freeze dead modules in `framework/core/`                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                           │ (Stage 1 Gate Passed)                      │
│                                           ▼                                            │
│ STAGE 2: Native Antigravity Integration                                                │
│   • Dynamic multi-path resolution in `gate.py` and `pre_tool_guard.py` (`workspacePaths`) │
│   • Zero-dependency NDJSON event emitter (`.agents/telemetry.ndjson`)                  │
│   • Hook `cwd` normalization & canonical skill runbooks update                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                           │ (Stage 2 Gate Passed)                      │
│                                           ▼                                            │
│ STAGE 3: State + Memory + Freshness + Verification                                     │
│   • 91.5ms Combined Git Token check & 59µs incremental Merkle tree update              │
│   • 8-category epistemic memory system with SHA-256 code binding                       │
│   • 6-dimension MVR manifest (`antios.config.json`) & physical Stop Gate ratchet       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                           │ (Stage 3 Gate Passed)                      │
│                                           ▼                                            │
│ STAGE 4: Real-Project Certification                                                    │
│   • AntiOS self-compilation verification                                               │
│   • Real external project adaptation certification (Click / enterprise monorepo)       │
│   • Full 15-Invariant compliance sign-off & release tag v3.0.0                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stage-by-Stage Detailed Engineering Specifications

---

### Stage 0: Architecture Reconstruction & Project Hygiene (Current Baseline)

#### 0.1 Objective
Establish the immutable architectural foundation and formalize all empirical research findings into authoritative specifications. Ensure the current repository passes 100% of existing tests with zero untracked artifacts or uncommitted state.

#### 0.2 Inputs
- Research Monographs: `RESEARCH_01_CONTEXT_COGNITION.md`, `RESEARCH_02_EXECUTION_PRIMITIVES.md`, `RESEARCH_03_PROJECT_SCOPE.md`, `RESEARCH_04_PROJECT_INTELLIGENCE.md`.
- Supporting Monographs: `AGENT_WAYFINDING.md`, `AGENT_INTELLIGENCE_FRESHNESS.md`, `AGENT_VERIFICATION_KNOWLEDGE.md`, `AGENT_ENGINEERING_MEMORY.md`.
- Existing test harness: `tests/run_all.py` (19 test suites).

#### 0.3 Outputs
- [`docs/architecture/ANTIOS_3_ARCHITECTURE.md`](./ANTIOS_3_ARCHITECTURE.md) (Authoritative Architecture Specification).
- [`docs/architecture/MIGRATION_PLAN.md`](./MIGRATION_PLAN.md) (Authoritative Migration Roadmap).
- Updated Documentation Index: `docs/INDEX.md` reflecting AntiOS 3.0 structure.
- Clean Working Tree: Zero untracked test outputs or temporary databases.

#### 0.4 Components Touched
- `docs/architecture/` (New files).
- `docs/INDEX.md` (Update cross-links).

#### 0.5 Components Preserved
- `framework/core/` (All 84 modules preserved without mutation).
- `framework/hooks/gate.py`, `framework/hooks/pre_tool_guard.py` (100% preserved).
- `tests/` (All 19 test modules preserved).
- `.agents/` (Hooks, skills, rules preserved).

#### 0.6 Tests & Proving Commands
```bash
# Verify the baseline test suite passes completely
python tests/run_all.py

# Verify working tree is pristine
git status --porcelain
```

#### 0.7 Acceptance Criteria
- [x] All 1,086 unit tests pass with exit code 0 (`Ran 1086 tests in ... OK`).
- [x] `ANTIOS_3_ARCHITECTURE.md` is complete, covering the 9 Subsystem Concerns and 4-Zone Boundaries.
- [x] `MIGRATION_PLAN.md` defines the exact 5-stage roadmap with acceptance criteria.
- [x] `git status --porcelain` shows only the intentional documentation files.

#### 0.8 Rollback & Degradation Behavior
- Git discard (`git checkout -- docs/`) restores the previous documentation state.
- No runtime code is altered during Stage 0; zero operational risk.

---

### Stage 1: Project Environment Compiler & Project Intelligence

#### 1.1 Objective
Design and implement the standalone **Project Environment Compiler** (`compiler.py` and CLI `antios compile`). The compiler will scan a target project, parse its AST symbol structure, and emit the compact **Subsystem Route Map (`.agents/routes.json`)**, **Hierarchical Merkle State (`.agents/cache/merkle_tree.json`)**, and a token-budgeted root `AGENTS.md` (<250 tokens). Isolate and catalog dead code in `framework/core/` to prevent future developer confusion.

#### 1.2 Inputs
- Project manifests: `pyproject.toml`, `package.json`, `Cargo.toml`, `setup.py`.
- Target repository filesystem tree.
- Subsystem schema definitions: `antios.config.json`.

#### 1.3 Outputs
- `framework/compiler/compiler.py`: Universal static project compiler.
- `framework/compiler/routes.py`: Subsystem route map generator.
- `framework/compiler/ast_extractor.py`: Zero-dependency AST symbol outline extractor.
- `.agents/routes.json`: Generated machine-readable route map.
- `./AGENTS.md`: Compact Turn-0 constitution and subsystem index (<250 tokens).
- `docs/architecture/DEAD_CODE_REGISTRY.md`: Catalog of uninvoked modules in `framework/core/`.

#### 1.4 Components Touched
- `framework/compiler/` (New package).
- `framework/cli.py` (Add `antios compile` command).
- `tests/test_compiler.py` (New test suite).
- `./AGENTS.md` (Updated to reflect AntiOS 3.0 Turn-0 specification).

#### 1.5 Components Preserved
- `framework/hooks/gate.py`, `framework/hooks/pre_tool_guard.py`.
- All existing 1,086 unit tests in `tests/run_all.py`.

#### 1.6 Tests & Proving Commands
```bash
# Run the new compiler test suite
pytest tests/test_compiler.py

# Benchmark compilation latency (<100ms requirement)
python -m unittest tests.test_compiler.TestCompilerPerformance

# Verify existing suite remains 100% green
python tests/run_all.py
```

#### 1.7 Acceptance Criteria
- [ ] Compiler executes in **< 100ms** on the AntiOS repository.
- [ ] Emitted `.agents/routes.json` correctly identifies all subsystems, entrypoints, and test bindings.
- [ ] Emitted `./AGENTS.md` is strictly under **250 tokens**.
- [ ] AST symbol outline correctly extracts classes and methods with exact line ranges using standard library `ast`.
- [ ] Full test suite passes: $\ge 1,110$ passing tests (1,086 baseline + new compiler tests), 0 failures.

#### 1.8 Rollback & Degradation Behavior
- If `antios compile` fails or encounters corrupt project manifests, it falls back to generating a generic fallback route map based on top-level directory names.
- If the new compiler package causes regressions, remove `framework/compiler/` and restore baseline `./AGENTS.md`.

---

### Stage 2: Native Antigravity Integration

#### 2.1 Objective
Align AntiOS runtime enforcement with Antigravity 2.0 platform realities. Fix the critical `workspacePaths[0]` defect in `gate.py` and `pre_tool_guard.py` to enable seamless multi-folder and multi-repository execution. Implement the zero-dependency **NDJSON Telemetry Emitter** (`.agents/telemetry.ndjson`) to eliminate the framework import contradiction. Update canonical skill runbooks in `.agents/skills/`.

#### 2.2 Inputs
- Research 2 & 3 findings on platform hook schemas and multi-folder arrays.
- `framework/hooks/gate.py` and `framework/hooks/pre_tool_guard.py`.
- `.agents/skills/antios-engineer/` and `.agents/skills/antios-verifier/`.

#### 2.3 Outputs
- Hardened `framework/hooks/pre_tool_guard.py` with multi-root prefix matching.
- Hardened `framework/hooks/gate.py` with multi-repo test runner resolution.
- `framework/hooks/emitter.py`: Zero-dependency NDJSON event logger.
- Updated `.agents/hooks.json` (registering `PreInvocation`, `PreToolUse`, `PostToolUse`, `Stop`).
- Updated skills: `antios-engineer` (L0-L3 wayfinding instructions) and `antios-verifier` (Maker-Checker dispatch contract).

#### 2.4 Components Touched
- `framework/hooks/gate.py`
- `framework/hooks/pre_tool_guard.py`
- `framework/hooks/emitter.py` (New)
- `.agents/hooks.json`
- `.agents/skills/antios-engineer/SKILL.md`
- `.agents/skills/antios-verifier/SKILL.md`
- `tests/test_gate_hardened.py`, `tests/test_guard_hardened.py`

#### 2.5 Components Preserved
- `framework/compiler/` (From Stage 1).
- Existing test baseline.

#### 2.6 Tests & Proving Commands
```bash
# Test multi-workspace path resolution in guard
python -m unittest tests.test_guard_hardened.TestMultiWorkspaceGuard

# Test multi-repo test execution in gate
python -m unittest tests.test_gate_hardened.TestMultiRepoGate

# Verify zero-dependency NDJSON emitter
python -m unittest tests.test_emitter.TestNDJSONTelemetry

# Run complete regression suite
python tests/run_all.py
```

#### 2.7 Acceptance Criteria
- [ ] Hook scripts resolve target files across multiple `workspacePaths` using longest-prefix matching.
- [ ] Files modified outside all workspace paths are rejected with `decision: "deny"`.
- [ ] `emitter.py` writes sanitized JSON events to `.agents/telemetry.ndjson` with zero third-party dependencies.
- [ ] Hook execution latency remains strictly **< 95ms**.
- [ ] All unit tests pass ($\ge 1,130$ tests), 0 regressions.

#### 2.8 Rollback & Degradation Behavior
- If multi-path resolution encounters edge cases on Windows drives (e.g. UNC paths), fall back to `os.path.commonpath`.
- If NDJSON logging fails (e.g. disk full), catch `IOError` silently to ensure hooks never block developer workflows.

---

### Stage 3: State + Memory + Freshness + Verification

#### 3.1 Objective
Implement the high-performance freshness engine, epistemic memory framework, and complete 6-dimension MVR verification engine:
1. **Freshness**: Embed the **91.5ms Combined Git Token check** and **59µs incremental Merkle tree update** into `PreInvocation`.
2. **Memory**: Establish the 8-category Git-versioned Markdown memory store in `docs/memory/` with SHA-256 target code binding.
3. **Verification**: Enforce the full 6-dimension MVR schema (`antios.config.json`) with physical Stop Gate test execution, conflict marker scanning, and timeout ratchets.

#### 3.2 Inputs
- `docs/research/AGENT_INTELLIGENCE_FRESHNESS.md` benchmark algorithms.
- `docs/research/AGENT_ENGINEERING_MEMORY.md` epistemic schemas.
- `docs/research/AGENT_VERIFICATION_KNOWLEDGE.md` 6-dimension MVR definitions.

#### 3.3 Outputs
- `framework/intelligence/merkle.py`: Hierarchical Merkle tree with sub-millisecond bubble-up recalculation.
- `framework/intelligence/freshness.py`: Combined Git Token checker (`SHA-256(HEAD + porcelain)`).
- `docs/memory/adr/`: Architectural Decision Records directory.
- `docs/memory/dead_ends.md`: Negative hypotheses registry with SHA-256 code binding.
- `docs/memory/rca/`: Root Cause Analysis post-mortem directory.
- Enhanced `antios.config.json` supporting full 6-dimension MVR schema.

#### 3.4 Components Touched
- `framework/intelligence/` (New/enhanced modules).
- `framework/hooks/gate.py` (Integrate conflict marker scan and MVR execution).
- `docs/memory/` (New directory and schemas).
- `antios.config.json` (Schema update).
- `tests/test_freshness.py`, `tests/test_merkle.py`, `tests/test_mvr.py` (New test suites).

#### 3.5 Components Preserved
- Compiler from Stage 1.
- Hook infrastructure from Stage 2.
- All existing tests.

#### 3.6 Tests & Proving Commands
```bash
# Verify Merkle tree sub-millisecond recalculation (<0.1ms)
python -m unittest tests.test_merkle.TestMerklePerformance

# Verify Combined Git Token state detection
python -m unittest tests.test_freshness.TestCombinedGitToken

# Verify Stop Gate MVR 6-dimension execution
python -m unittest tests.test_mvr.TestMVRStopGate

# Run full test suite
python tests/run_all.py
```

#### 3.7 Acceptance Criteria
- [ ] Combined Git Token detects 100% of committed and uncommitted edits in **< 100ms**.
- [ ] Incremental Merkle update bubbles up dirty path hashes in **< 0.1ms (100 µs)**.
- [ ] Memory records with mismatched SHA-256 hashes are automatically tagged `[STALE_EVIDENCE]` and suppressed.
- [ ] Stop Gate rejects task completion if git conflict markers (`<<<<<<< HEAD`) exist in touched files.
- [ ] Stop Gate physically executes configured MVR test runner and blocks exit on non-zero exit code.
- [ ] Zero background daemons spawned (INV-15 verified).
- [ ] All unit tests pass ($\ge 1,160$ tests), 0 regressions.

#### 3.8 Rollback & Degradation Behavior
- If the Merkle cache file is corrupted or unreadable, the system deletes `.agents/cache/merkle_tree.json` and performs a one-shot clean rebuild.
- If git is unavailable or repo is not a git directory, hooks degrade gracefully to advisory warnings.

---

### Stage 4: Real-Project Certification & Release

#### 4.1 Objective
Conduct end-to-end certification of AntiOS 3.0 across two real-world environments:
1. **Self-Compilation**: AntiOS compiling and governing its own repository (`naksh-07/AntiOS`).
2. **External Application Adaptation**: Compiling and governing an external open-source repository (e.g. `Click` or `Anki-maths`).
Demonstrate 0-turn wayfinding accuracy, physical verification enforcement, independent Maker-Checker audit via `antios-verifier`, and 100% compliance with all 15 Constitutional Invariants. Release AntiOS 3.0.0.

#### 4.2 Inputs
- Complete AntiOS 3.0 codebase (Stages 0–3).
- Real project proving ground repositories.
- AntiOS Verification Suite (`tests/run_all.py`).

#### 4.3 Outputs
- `docs/architecture/CERTIFICATION_3_0.md`: Full empirical certification report.
- Ratified Decision Register Entry (`docs/memory/adr/ADR_001_ANTIOS_3_RELEASE.md`).
- Release Tag: `v3.0.0`.

#### 4.4 Components Touched
- `docs/architecture/CERTIFICATION_3_0.md` (New report).
- `framework/version.py` (Bump version to `3.0.0`).
- `antios.config.json` (Final production configuration).

#### 4.5 Components Preserved
- All core compiler, intelligence, hook, and memory modules.
- 100% of the expanded test suite ($\ge 1,160$ tests).

#### 4.6 Tests & Proving Commands
```bash
# Run full universal test runner
python tests/run_all.py

# Execute the Real-Project Proving Ground Campaign
python tests/test_external_proving_ground.py

# Verify All 15 Constitutional Invariants
python -m unittest tests.test_production_readiness.TestProductionReadinessAndFreeze
```

#### 4.7 Acceptance Criteria
- [ ] 100% pass rate across $\ge 1,160$ automated unit tests with 0 failures and 0 errors.
- [ ] 0-turn wayfinding validated: agent locates target implementation with zero exploratory grep calls.
- [ ] Physical Stop Gate successfully blocks task exit on simulated test failure and allows exit on passing test.
- [ ] Subagent Maker-Checker audit succeeds with zero context inheritance and structured verdict emission.
- [ ] All 15 Constitutional Invariants (INV-01 through INV-15) verified compliant by automated audit.
- [ ] Clean uninstallation test passes: `antios remove` leaves target application code 100% untouched.

#### 4.8 Rollback & Degradation Behavior
- AntiOS can be cleanly decoupled from any target project by removing `.agents/` and `antios.config.json`. Target applications remain completely functional with zero dependency fallout.

---

## 4. Component Inventory & Preservation Ledger

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 COMPONENT PRESERVATION LEDGER                                    │
├───────────────────────────────┬────────────┬─────────────┬───────────────────────────────────────┤
│ Component Name                │ Path       │ Action      │ Rationale & Safety Invariant          │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Physical Stop Gate            │ gate.py    │ PRESERVE    │ Core asset; physically executes tests │
│                               │            │ & HARDEN    │ and enforces completion ratchets.     │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Pre-Tool Guard                │ guard.py   │ PRESERVE    │ Core asset; protects framework & git  │
│                               │            │ & HARDEN    │ from unauthorized tool mutation.      │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Project Config Loader         │ config.py  │ EXPAND      │ Expands to support 6-dimension MVR    │
│                               │            │             │ verification schema.                  │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Worktree Auditor              │ worktree.py│ PRESERVE    │ Scans conflict markers & dirty state. │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Changeset Discipline Evaluator│ changes.py │ PRESERVE    │ Verifies Same Change Set rule (INV-07)│
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Maker-Checker Verdict Parser  │ verdict.py │ PRESERVE    │ Formats & parses subagent verdicts.   │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Static Compiler Engine        │ compiler/  │ NEW         │ Compiles .agents/routes.json and AST  │
│                               │            │             │ outlines (<100ms).                    │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Hierarchical Merkle Tree      │ merkle.py  │ NEW         │ Microsecond incremental update (59µs) │
│                               │            │             │ satisfying Zero-Daemon INV-15.        │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ Zero-Dep NDJSON Emitter       │ emitter.py │ NEW         │ Resolves telemetry import paradox.    │
├───────────────────────────────┼────────────┼─────────────┼───────────────────────────────────────┤
│ In-Memory State Machine       │ state.py   │ DEPRECATE   │ Dead code at agent runtime; state is  │
│ (82 unused modules)           │ core/*.py  │ & ISOLATE   │ in Git working tree bytes.            │
└───────────────────────────────┴────────────┴─────────────┴───────────────────────────────────────┘
```

---

## 5. Verification & Rollback Runbook

### 5.1 Verification Commands by Stage
At each stage boundary, execute the mandatory proving sequence:
```bash
# 1. Zero Regressions Check (Mandatory at all stages)
python tests/run_all.py

# 2. Working Tree Cleanliness Check
git status --porcelain

# 3. Memory & Freshness Benchmark Check (Stages 1–4)
python -c "import time, subprocess; t0=time.perf_counter(); subprocess.run(['git', 'status', '--porcelain'], capture_output=True); print(f'Git Latency: {(time.perf_counter()-t0)*1000:.2f}ms')"
```

### 5.2 Universal Rollback Procedure
If any stage fails its acceptance criteria or introduces test regressions:
1. **Identify the failing stage**: Review test failure traces emitted by `tests/run_all.py`.
2. **Abort migration step**:
   ```bash
   # Revert all changes in working directory to last green commit
   git reset --hard HEAD
   git clean -fd
   ```
3. **Verify clean recovery**: Run `python tests/run_all.py` to confirm baseline return to 1,086 passing tests.
4. **Log Negative Finding**: Record a `[TESTED_NEGATIVE]` entry in `docs/memory/dead_ends.md` documenting the exact error trace before re-attempting.

---
