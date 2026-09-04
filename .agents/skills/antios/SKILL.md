---
name: antios
description: >-
  Universal project-native control plane under AntiOS 2.0 governance.
  Use when planning, navigating, implementing, debugging, verifying,
  or orchestrating any engineering task in this repository.
---

# AntiOS Project Operating Interface (`/antios`)

You are operating under **AntiOS 2.0 (Project Agent OS)** governance.
This skill is your **single authoritative control plane** (`/antios`). Follow the canonical 9-step execution pipeline below.

## 1. Operating Axioms & Responsibility Boundaries
- **Platform (Antigravity)**: Owns execution primitives (`invoke_subagent`, `manage_subagents`, `define_subagent`), tool transport, and planning mode.
- **AntiOS Core**: Owns engineering governance, safety boundaries, task dispatch, adaptive orchestration, and verification gates.
- **Project Adapter (`antios.config.json` / `.antios/`)**: Owns project topology, protected paths, and configured test runners.
- **Target Project**: Owns domain application logic, schemas, and native test suites.

## 2. Canonical 9-Step Dispatch Pipeline
1. `UNDERSTAND`: Clarify user objective, scope, constraints, and non-goals.
2. `CHECK STATE`: Read `.antios/knowledge.json` and `docs/ACTIVE_CONTEXT.md` (must be $\le 60$ lines).
3. `LOCATE`: Run wayfinding via `python framework/scripts/tools/navigate_repo.py --query "<query>"`.
4. `CLASSIFY`: Classify TaskClass (`FEATURE`|`BUG`|`REFACTOR`|`INVESTIGATION`|`DOCUMENTATION`|`RELEASE`) and RiskTier.
5. `SELECT CAPABILITIES`: Resolve skills, rules, and tools via `CapabilityRouter`.
6. `SELECT WORKFORCE`: Evaluate Gate A (Pre-Planning) and Gate B (Execution Dispatch).
7. `EXECUTE`: Controlled single writer or disjoint parallel workers (`Workspace='branch'`).
8. `VERIFY`: Physical test suite (exit code 0) + Maker-Checker audit via `antios-verifier`.
9. `REMEMBER`: Record observations, distill lessons via learning engine, update `docs/ACTIVE_CONTEXT.md`.
*CLI Helper*: `python framework/scripts/tools/dispatch_task.py "<task summary>" [--json]`

## 3. Adaptive Workforce Sizing & Constitutional Limits
Select the minimal effective workforce:
- **SOLO** (0 workers): Parent executes directly for narrow, local, or doc edits.
- **FOCUSED** (1 specialist): Isolated bug or deep investigation (`antios-debug`).
- **SMALL** (2 specialists): 2 disjoint, independent workstreams.
- **PARALLEL** (2–4 specialists): 3+ independent workstreams with disjoint file boundaries.
- **STAGED** (sequential waves): Multi-phase architectural changes with wave collapse.
- **HIERARCHICAL** (1 coordinator + 1–2 children): Bounded subproblem requiring local decomposition.
- **MAX** (broad initiative): Hard-capped by constitutional ceilings.

### Hard Constraints
- **Max Active Subagents Per Wave**: $\le 10$ across the active wave.
- **Max Lifetime Launches Per Mission**: $\le 20$ global launches total.
- **Shallow Depth Law**: Depth $\le 2$ (`Root -> Coordinator -> Child/Verifier`).
- **Mandatory Wave Collapse**: `NEXT_WAVE_ALLOWED` only when active workers == 0.

## 4. Fundamental Law: Read-Parallel, Write-Controlled
- **READ Operations**: Parallelize freely for codebase navigation, symbol discovery, and research.
- **WRITE Operations**: Strictly controlled. Single writer default. Parallel writes require disjoint paths and `Workspace='branch'`. Overlapping concurrent writes are prohibited.

## 5. Progressive Disclosure: Specialist Skills
Activate specialized skills only when justified:
- `antios-debug`: Root-cause diagnosis, test failure reproduction, minimal fix isolation.
- `antios-engineer`: Feature implementation, refactoring, and test-driven engineering.
- `antios-verifier`: Independent Maker-Checker audit, test runner execution, verdict generation.
- `antios-adapt-project`: Repository onboarding, project manifest, adapter tuning.

## 6. Stop Gate & Task Completion
1. Ensure all active workers are collapsed (`manage_subagents(Action='kill', ...)`).
2. Execute configured test runner (e.g., `python tests/run_all.py` must exit code 0).
3. Ensure `docs/ACTIVE_CONTEXT.md` is updated and strictly $\le 60$ lines.
4. Stop Gate will physically verify test pass before turn completion.
