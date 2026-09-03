# Phase 10 Forensic Baseline (`PHASE_10_BASELINE.md`)

**Date**: 2026-09-03  
**Audit Scope**: AntiOS Framework Repository  
**Audit Objective**: Establish empirical ground truth for all components of AntiOS, rejecting documentation claims and recording actual disk state.  
**Critical Boundary Check**: StudySourceCore is 100% OUT OF SCOPE (0 files accessed, 0 tools modified). Production StudyLab remains pristine.

---

## 1. Version Control & Repository Topology

### Root Workspace
- **Workspace URI**: `c:\Users\Suraj\Documents\Antigravity\AntiOs`
- **Git Status**: **NOT AN INITIALIZED GIT REPOSITORY**.
  - `git status` output: `fatal: not a git repository (or any of the parent directories): .git`
  - Parent directories (`C:\Users\Suraj\Documents\Antigravity`) are also unversioned.
  - **Forensic Impact**: Root AntiOS development has been conducted entirely outside direct git versioning. State recovery via `git log`, `git diff`, or git commits at the root level is impossible.

### Sub-Workspaces / Sandboxes
- **`sandbox/StudyLab`**:
  - **Git Initialized**: YES (`.git` present).
  - **Active Branch**: `experiment-v0.1`
  - **Head Commit**: `0036520b1` (`feat(reviewer): unify mistake classification into native bottom toolbar and update procedural tests`)
  - **Working Tree Status**: Dirty (`M uv.lock`, untracked `?? --help`).
- **`sandbox/StudyLab_Control`**:
  - **Git Initialized**: YES (`.git` present).
  - **Active Branch**: `experiment-v0.1` (`0036520b1`)
  - **Working Tree Status**: Dirty (`D .agents/ORIGINAL_REQUEST.md`, `D .agents/sentinel/*`, `M uv.lock`, `?? --help`).
- **`sandbox/StudyLab_Treatment`**:
  - **Git Initialized**: YES (`.git` present).
  - **Active Branch**: `experiment-v0.1` (`0036520b1`)
  - **Working Tree Status**: Dirty (`M uv.lock`, `?? --help`, `?? scripts/`).

---

## 2. Directory Structure & Inventory

```text
c:\Users\Suraj\Documents\Antigravity\AntiOs\
├── AGENT_VS_AGENT_ADVERSARIAL_RESULTS.md (Duplicate of reports/)
├── ANTIOS_FAILURE_TAXONOMY.md (Duplicate of reports/)
├── ARCHITECTURE_PROPOSAL.md
├── DECISION_REGISTER.md
├── EXPERIMENT_BASELINE.md
├── FRAMEWORK_REQUIREMENTS.md
├── OPEN_QUESTIONS.md
├── PHASE_6_SYNTHESIS.md
├── PHASE_7_REPORT.md
├── PHASE_9_ATTACK_MATRIX.md (Duplicate of reports/)
├── PHASE_9_REPORT.md (Duplicate of reports/)
├── PHASE_9_REPORTS.zip
├── PROTOTYPE_IMPLEMENTATION.md
├── PROTOTYPE_OPEN_ISSUES.md
├── PROTOTYPE_TEST_RESULTS.md
├── PROTOTYPE_V0_1_SPEC.md
├── RECOVERY_TEST_REPORT.md (Duplicate of reports/)
├── SECURITY_ADVERSARIAL_REPORT.md (Duplicate of reports/)
├── VERIFICATION_ADVERSARIAL_REPORT.md (Duplicate of reports/)
├── docs\
│   ├── ACTIVE_CONTEXT.md (Stale, frozen at Prototype v0.1)
│   └── AGENTS.md (AntiOS Global Constitution)
├── evidence\ (0 files, empty directory)
├── experiments\
│   ├── EXPERIMENT_01.md
│   └── EXPERIMENT_02.md
├── framework\
│   ├── .agents\
│   │   ├── hooks.json
│   │   └── skills\
│   │       └── studylab-task-runner\
│   │           └── SKILL.md
│   └── scripts\
│       └── hooks\
│           ├── pre_tool_guard.py
│           └── stop_gate.py
├── reports\
│   ├── AGENT_VS_AGENT_ADVERSARIAL_RESULTS.md
│   ├── AGENT_VS_AGENT_RESULTS.md
│   ├── ANTIOS_FAILURE_TAXONOMY.md
│   ├── BEST_IN_BREED_GAP_ANALYSIS.md
│   ├── COMPLEXITY_AUDIT.md
│   ├── MCP_REEVALUATION_REPORT.md
│   ├── MEMORY_AND_RECOVERY_REPORT.md
│   ├── PHASE_8_REPORT.md
│   ├── PHASE_9_ATTACK_MATRIX.md
│   ├── PHASE_9_REPORT.md
│   ├── RECOVERY_TEST_REPORT.md
│   ├── SECURITY_ADVERSARIAL_REPORT.md
│   ├── SECURITY_HARDENING_REPORT.md
│   ├── VERIFICATION_ADVERSARIAL_REPORT.md
│   └── VERIFICATION_HARDENING_REPORT.md
└── sandbox\
    ├── StudyLab\ (Full clone, dirty git tree)
    ├── StudyLab_Control\ (Bare Antigravity testbed)
    └── StudyLab_Treatment\ (AntiOS testbed)
```

---

## 3. Skills Inventory & Empirical Discoverability

| Skill Name | Physical Location | Registered in Platform `<skills>`? | Discovery Status | Description / Purpose |
| :--- | :--- | :---: | :---: | :--- |
| **`studylab-task-runner`** | `framework\.agents\skills\studylab-task-runner\SKILL.md` | **NO** | **UNDISCOVERABLE** | Intended to guide RPAC lifecycle and verifier subagent dispatch. Because it resides inside `framework/` rather than the workspace root (`.agents/skills`), the Antigravity engine never loads it. |
| **Sandbox Mirror** | `sandbox\StudyLab\.agents\skills\studylab-task-runner\SKILL.md` | **NO** (unless sub-folder opened) | **SUB-WORKSPACE ONLY** | Loaded only if an agent session has `sandbox/StudyLab` as its primary workspace. |

---

## 4. Rules & Constitutional State

- **Platform Rules (`<user_rules>`)**: Empty in active agent configuration.
- **Rule Directory (`.agents/rules/`)**: **DOES NOT EXIST**.
- **Documented Constitution**: `docs/AGENTS.md` (27 lines, 1,343 bytes).
  - Directive 1: Upstream Immutability (`rslib/` off-limits).
  - Directive 2: Isolation & Safety (Execute in `sandbox/StudyLab`).
  - Directive 3: Same Change Set Synchronization (Code + Docs together).
  - Directive 4: Independent Verification (Done $\neq$ Verified).
  - Directive 5: Test Ratchet (Exit code 0 mandatory).
  - Directive 6: StudySourceCore Is Out of Scope.
- **Enforcement Status**: Passive markdown text. Not enforced natively by platform without hooks.

---

## 5. Hooks Inventory & Operational Status

- **Configuration File**: `framework/.agents/hooks.json` (401 bytes).
  ```json
  {
    "study-lab-guard": {
      "PreToolUse": [
        {
          "matcher": "write_to_file|replace_file_content",
          "hooks": [{ "type": "command", "command": "python ./scripts/hooks/pre_tool_guard.py" }]
        }
      ],
      "Stop": [
        {
          "type": "command", "command": "python ./scripts/hooks/stop_gate.py"
        }
      ]
    }
  }
  ```
- **Active Workspace Hook**: **NONE**. The root workspace `c:\Users\Suraj\Documents\Antigravity\AntiOs` does NOT have an `.agents/hooks.json` file.
- **Execution Scripts**:
  - `framework/scripts/hooks/pre_tool_guard.py` (2,095 bytes)
  - `framework/scripts/hooks/stop_gate.py` (3,822 bytes)
- **Runtime Environment Gap**: Scripts specify `python ...`. On this Windows system, `python.exe` is NOT in PATH; only `python3.11.exe` exists in `~/.local/bin`. Without aliasing or full path resolution, Windows shell fails to spawn `python`.

---

## 6. Subagents & Multi-Agent Architecture

- **Predefined Subagents in Environment**:
  - `self`: Full parent inheritance (Read/Write/Exec).
  - `research`: Read-only (Cannot run commands or tests).
  - `flutter_a11y_agent`: Specialized accessibility reviewer.
- **Maker-Checker Mechanism**: Relies on `invoke_subagent(TypeName='self')` to launch fresh-context verifiers.
- **AntiOS Custom Subagents**: None defined via `define_subagent` in configuration files; dynamically spawned in-turn.
- **Contaminated Subagent Remains**: `sandbox/StudyLab_Treatment/.agents/sentinel/` contains dead artifacts (`BRIEFING.md`, `handoff.md`) referencing an external project `Anki-maths`.

---

## 7. MCP (Model Context Protocol) Configuration

The platform environment currently has 10 MCP servers configured:
1. `chrome-devtools-mcp`: Browser debugging and snapshotting.
2. `docker-mcp`: Container operations and browser sandboxing.
3. `gemini-api-docs`: Native SDK documentation lookups.
4. `github-mcp-server`: GitHub issue/PR management (Redundant with Git CLI).
5. `notion-mcp-server`: Notion workspace integration.
6. `playwright` / `playwright-mcp-server`: Web automation and testing.
7. `posthog`: Analytics execution.
8. `postman-mcp-server`: API testing.
9. `studysource-core`: StudySourceCore domain tools (**STRICTLY OUT OF SCOPE**).

---

## 8. Memory & State Persistence

- **Bounded Memory Bank**:
  - `docs/AGENTS.md`: Intended Tier-1 Global Rules (Static).
  - `docs/ACTIVE_CONTEXT.md`: Intended Tier-2 Working Set. **Status: Corrupt/Stale** (Unchanged since Phase 6; describes Prototype v0.1 setup as active).
- **Evidence Storage**:
  - `evidence/`: Completely empty (0 bytes).
  - `artifacts/` in brain: In-session transient markdown files.

---

## 9. Verification & Test Infrastructure

- **Test Discovery in `stop_gate.py`**:
  1. `package.json` $\to$ `vitest:once` (via `npm` or `yarn`).
  2. `pyproject.toml` $\to$ `uv run pytest`.
  3. `verify_task.py` $\to$ `python verify_task.py` (Trivial forgery vulnerability).
- **Actual Tests in Sandboxes**:
  - `sandbox/StudyLab/ts/tests/e2e/`: Real Playwright/Vitest TypeScript tests.
  - Rust backend tests in `sandbox/StudyLab/rslib/` (Protected/Out of Scope).

---

## 10. Baseline Summary Verdict

AntiOS exists on disk as a **fragmented prototype** rather than an integrated operational system:
1. The root project is not a git repository.
2. The custom skill is undiscoverable because it is nested under `framework/`.
3. The hooks are mounted in `framework/.agents` and `sandbox/StudyLab_Treatment/.agents`, but not in the root workspace.
4. `pre_tool_guard.py` and `stop_gate.py` are identical to Phase 8; no Phase 9 patches have been applied to source code.
5. Seven duplicate report files clutter both root and `reports/`.
