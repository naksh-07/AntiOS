# AntiOS Master Operating Model: Dual-Mode Engineering Lifecycle

**Version**: `2.1.0-operating-model`  
**Status**: `RATIFIED OPERATING MODEL` (Phase 108)  
**Authority**: Rank 5 in Precedence (`ANTIOS_SOURCE_OF_TRUTH.md`)  
**Scope**: Universal Operating Lifecycle for AI-Assisted Software Engineering  

---

## 1. The Dual-Mode Engineering Lifecycle

To balance velocity on routine changes with rigorous governance on complex architectural initiatives, AntiOS operates under the **Dual-Mode Engineering Lifecycle**:

```
                       ENGINEERING TASK INTAKE
                                   │
                  Is `/antios` explicitly invoked?
                  OR is task classified HIGH-RISK?
                                   │
                  ┌────────────────┴────────────────┐
                  ▼ NO                              ▼ YES
       ┌─────────────────────┐           ┌─────────────────────┐
       │    MODE 1: AMBIENT  │           │   MODE 2: EXPLICIT  │
       │    EXECUTION MODE   │           │    CONTROL MODE     │
       └──────────┬──────────┘           └──────────┬──────────┘
                  │                                 │
                  ▼                                 ▼
         Direct Agile Flow                 Full Governance Plane
         - SOLO / Single Writer            - 9-Stage Pipeline
         - Passive PreTool Guard           - Formal Workforce Sizing
         - Native Test Execution           - Maker-Checker Audit
         - Stop Gate Exit Code 0           - Evidence Promotion
```

### 1.1 Mode 1: Ambient Execution Mode (Default / Normal Engineering)
Ambient Mode is the frictionless default for day-to-day software development:
- **Trigger**: Any normal user prompt without `/antios` prefix (e.g., *"Fix the off-by-one bug in parser.py"*, *"Add unit tests for the auth helper"*, *"Update README instructions"*).
- **Workforce Sizing**: Default is `SOLO` (Parent agent operates as Single Controlled Writer; 0 subagents).
- **Procedural Ceremony**: Zero multi-stage planning ceremony. The agent reads necessary code directly, authors the change, and executes tests.
- **AntiOS Governance**: Operates purely out-of-band:
  - `pre_tool_guard.py`: Silently verifies path containment and protected zone immutability on every file write in $< 10$ms.
  - `stop_gate.py`: Enforces the physical test ratchet upon task completion (scans conflict markers, runs discovered project test suite, verifies exit code 0).
  - `telemetry_bridge.py`: Non-blockingly captures telemetry into the external experience store.

### 1.2 Mode 2: Explicit Control Mode (`/antios`)
Explicit Control Mode is the authoritative command plane for high-stakes, multi-file, or architectural initiatives:
- **Trigger**: Explicit invocation of `/antios` or tasks touching high-risk zones (database schemas, core security hooks, compiler definitions, multi-package refactors).
- **Workforce Sizing**: Evaluated dynamically across the 7 modes (`SOLO` through `MAX`).
- **Structured Pipeline**: Traverses the formal 9-stage engineering sequence:
  1. `UNDERSTAND`: Dissects goal, constraints, and success criteria.
  2. `CHECK_STATE`: Audits git working tree status and bounded `docs/ACTIVE_CONTEXT.md`.
  3. `LOCATE`: Deterministic wayfinding via `.antios/anatomy.json` prefix indexing.
  4. `CLASSIFY`: Determines technical domain, coupling, and risk level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  5. `SELECT_CAPABILITIES`: Generates bounded capability pack ($\le 25$ lines) via `capability_router.py`.
  6. `SELECT_WORKFORCE`: Sizes team based on independent workstreams; issues Phase 1 and Phase 2 dispatch gates.
  7. `EXECUTE`: Single controlled writer or isolated branch workspaces (`Workspace='branch'`).
  8. `VERIFY`: Executes physical test suite + independent fresh-context Maker-Checker audit (`antios-verifier`).
  9. `REMEMBER`: Distills observed empirical facts into System A (`docs/ACTIVE_CONTEXT.md`, `docs/LESSONS.md`).

---

## 2. Adaptive Workforce Sizing Modes

Workforce sizing in AntiOS adheres to the **Adaptive Workforce Sizing Protocol** (`ORCHESTRATION_MODEL.md`):

| Sizing Mode | Typical Concurrency | Lifetime Launches | Primary Application |
| :--- | :---: | :---: | :--- |
| **SOLO** | 0 subagents | 0 | Bug fixes, single-file edits, documentation, typos, test additions |
| **FOCUSED** | 1 subagent | 1–2 | Isolated complex investigation, focused research spike |
| **SMALL** | 2 subagents | 2–3 | Two independent workstreams (e.g. backend endpoint + frontend UI) |
| **PARALLEL** | 2–3 subagents | 3–5 | Repository-wide linting, broad independent audit, multi-module tests |
| **STAGED** | 2–3 across waves | 4–6 | Sequential migrations (Wave 1: Schema $\to$ Wave 2: API $\to$ Wave 3: UI) |
| **HIERARCHICAL**| 1 Lead + 1–2 Children | 4–8 | Highly decomposable domain requiring specialist coordinator |
| **MAX** | 4 subagents | 10 total | Large-scale mission-critical initiative under strict budget cap |

### Hard Resource Ceilings (`INV-06`, `INV-07`, `INV-08`)
- **Concurrency Ceiling**: Maximum 4 concurrent active subagents globally across the entire mission tree.
- **Launch Ceiling**: Maximum 10 total launches across Root + Children + Grandchildren.
- **Shallow Depth Law**: Subagent nesting depth strictly $\le 2$ (Root $\to$ Specialist $\to$ Leaf). Specialists cannot create recursive subagents.
- **Mandatory Wave Collapse**: All active subagents must complete and be terminated (`manage_subagents(kill)`) to reach 0 active workers before the next wave begins.

---

## 3. Progressive Coordination Depth (L0 to L3)

AntiOS scales coordination overhead to match problem complexity without polluting the target repository:

```
[ L0: SOLO / Tiny ]
  - Coordination artifacts: NONE.
  - State tracking: In-memory conversation context.

[ L1: FOCUSED / Small ]
  - Coordination artifacts: Structured Markdown summaries in tool responses.
  - State tracking: Compact handoff report blocks.

[ L2: MULTI-WAVE / Staged ]
  - Coordination artifacts: Created in <appDataDir>\brain\<conversation-id>/
  - Files: mission.md, progress.md, dead-ends.md.

[ L3: HIERARCHICAL / Critical ]
  - Coordination artifacts: Full coordination suite in artifact directory.
  - Files: mission.md, progress.md, dead-ends.md, gates.md, final-audit.md.
```

> [!IMPORTANT]
> **Zero Workspace Pollution**: All coordination markdown files (`mission.md`, `progress.md`, `dead-ends.md`) MUST reside in the conversation's Artifact Directory (`<appDataDir>\brain\<conversation-id>/`). They must **NEVER be written to the target project workspace root**.

---

## 4. Fundamental Law: READ PARALLEL — WRITE CONTROLLED

To eliminate file corruption, race conditions, and merge conflicts:
- **Safe to Parallelize (Read-Heavy)**: Code navigation, log analysis, test gap assessment, dependency audits.
- **Hazardous to Parallelize (Write Operations)**: Editing shared files, updating database schemas, modifying package manifests.
- **Write Governance**:
  - **Single Writer Default**: Changes across related files are assigned to one worker (the Parent or a designated Implementer subagent).
  - **Branch Workspace Isolation**: When multiple subagents must implement independent workstreams concurrently, each subagent MUST be spawned with `Workspace='branch'`. Diffs are reconciled by the parent agent upon task completion.
  - **Zero Overlapping Writers**: Two subagents must never write to the same file path simultaneously.

---

## 5. Toolchain Ground Truth & Physical Stop Gate Ratchet

AntiOS enforces an unbendable rule of verification: **Conversational claims do not equal verification** (`INV-03`, `INV-04`).

### The Stop Gate Protocol (`stop_gate.py`)
When any agent attempts to conclude a task turn (invoking the `Stop` event):
1. **Git Conflict Marker Inspection**: The hook scans all modified files in the git working tree for unresolved merge conflicts (`<<<<<<<`, `=======`, `>>>>>>>`). If found, completion is blocked immediately.
2. **Native Test Runner Discovery**: The hook inspects `antios.config.json` and project manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) to identify registered test runners.
3. **Physical Process Execution**: The hook spawns the discovered test runner via subprocess.
4. **Exit Code 0 Verification**: The test process must exit with physical return code 0. If tests fail, the hook blocks task conclusion, prints test failures to stderr, and forces the agent to resolve issues.
5. **No Synthetic Shortcuts**: Dummy verification scripts (`verify_task.py`) are permanently rejected (`DECISION 03`). Only native project test suites are recognized as verification ground truth.

---

## 6. Risk-Tiered Maker-Checker Verification Policy

In accordance with **ADR 92**, verification rigor scales proportionally with task risk:

```text
               RISK CLASSIFICATION AT VERIFICATION WAVE
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
[ LOW / MEDIUM RISK ]                               [ HIGH / CRITICAL RISK ]
- Typos, docs, formatting                          - Security hooks, auth logic
- Single-module bug fix                             - Database schema migrations
- New isolated unit test                            - Compiler & core state machines
- Parent-level verification:                        - Maker-Checker audit:
  Run test runner exit code 0                         Fresh subagent (antios-verifier)
  Clean git diff review                               Audits diff against acceptance criteria
  Direct conclusion                                   Emits structured JSON verdict
```

### Maker-Checker Audit Contract (`antios-verifier`)
When High-Risk verification is triggered:
1. The parent dispatches a fresh-context subagent: `invoke_subagent(TypeName='self', Role='Independent Verifier')`.
2. The verifier audits the working tree diff via `git diff`.
3. The verifier executes the physical test suite independently.
4. The verifier checks boundary compliance and non-mutation of protected zones.
5. The verifier emits a structured JSON verdict:
   ```json
   {
     "status": "APPROVED",
     "tests_passed": true,
     "clean_diff": true,
     "protected_zones_untouched": true,
     "rationale": "All 14 unit tests pass, no conflict markers, zero core mutations."
   }
   ```
6. If the verdict is `REJECTED`, the parent must resolve defects before concluding.

---

## 7. Context Governance & Token Bounding Laws

To ensure agents never suffer from context bloat or memory saturation:

- **Global Orientation (`docs/AGENTS.md`)**: Strictly bounded to $\le 40$ lines. Sets baseline laws without narrative prose.
- **Active Working Memory (`docs/ACTIVE_CONTEXT.md`)**: Strictly bounded to $\le 60$ lines. Tracks immediate goals, blockers, and verified next steps.
- **Capability Cards (`framework/core/capability_pack.py`)**: Strictly bounded to $\le 25$ lines per pack.
- **Project Lessons (`docs/LESSONS.md`)**: Strictly bounded to $\le 50$ entries. Older entries are pruned or consolidated.
- **Durable Proofs (`.antios/proofs/`)**: Strictly bounded to $\le 50$ proofs.
- **Ephemeral Scratchpad**: Scratch notes are written to temporary session memory and distilled into `docs/ACTIVE_CONTEXT.md` before task conclusion.
