# AntiOS Component Model Specification (`ANTIOS_COMPONENT_MODEL.md`)

**Version**: 2.0.0-draft (Universal Re-baseline)  
**Date**: 2026-09-04  
**Status**: Canonical Component Model Specification  

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
|  [framework/core/guard.py]    [framework/core/gate.py]   [framework/core/verdict.py]
|            ^                             ^                            ^           |
|            |                             |                            |           |
|            +-----------------------------+----------------------------+           |
|                                          |                                        |
|                            [framework/core/config.py]                             |
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
|  [.agents/skills/antios-debug/]     [docs/AGENTS.md]       [docs/ACTIVE_CONTEXT.md]   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Framework Core Library (`framework/core/`)

The Core Library is a zero-dependency Python 3 (3.8+) package providing deterministic validation, execution, and data parsing.

### 2.1 Configuration Engine (`framework/core/config.py`)
- **Purpose**: Loads, validates, and defaults the Project Adapter configuration.
- **Key Data Models**:
  ```python
  @dataclass
  class TestRunnerConfig:
      name: str
      command: List[str]
      manifest: Optional[str] = None
      cwd: Optional[str] = None
      timeout_seconds: int = 120
      required: bool = True

  @dataclass
  class AntiOSConfig:
      name: str = "AntiOS-Universal-Core"
      version: str = "1.0.0"
      protected_zones: List[str] = field(default_factory=lambda: [".agents", "framework", "antios.config.json"])
      protected_domain_paths: List[str] = field(default_factory=list)
      forbidden_patterns: List[str] = field(default_factory=list)
      test_runners: List[TestRunnerConfig] = field(default_factory=list)
      fail_closed: bool = True
  ```
- **Primary Function**: `load_config(workspace_root: str) -> AntiOSConfig`
  - Attempts to parse `antios.config.json` at `workspace_root`.
  - On `FileNotFoundError` or malformed JSON, returns safe universal defaults protecting `.agents/`, `framework/`, and `antios.config.json`.
  - In Universal Core v2, fallback defaults contain **zero domain-specific paths** (`rslib`) or domain runners (`vitest:once`).

### 2.2 PreToolUse Path Guard Engine (`framework/core/guard.py`)
- **Purpose**: Intercepts IDE file-mutating tool calls before execution.
- **Contract**:
  - Input: Stdio JSON payload containing `tool_name` (`write_to_file`, `replace_file_content`) and `tool_input` (`TargetFile`).
  - Output: Stdio JSON payload `{"decision": "allow"}` or `{"decision": "deny", "reason": "..."}`.
- **Path Canonicalization Pipeline**:
  ```text
  Raw Input Path (e.g. "rslib/../.agents/hooks.json" or "rslib~1/mod.rs")
                          |
                          v
  os.path.realpath -> Resolves symlinks, normalizes traversal (..)
                          |
                          v
  os.path.normcase -> Normalizes case for Windows / Unix portability
                          |
                          v
  os.path.commonpath -> Prefix-based ancestor containment verification
                          |
                          v
  fnmatchcase -> Lexical wildcard matching against forbidden_patterns
  ```
- **Self-Protection Law**:
  - Any mutating tool targeting `.agents/` (including `hooks.json` and skills) or `framework/` is unconditionally denied.

### 2.3 Stop Gate Verification Engine (`framework/core/gate.py`)
- **Purpose**: Enforces physical completion ratchets upon task termination signals (`Stop`).
- **Contract**:
  - Input: Stdio JSON payload containing `task_id` and ambient session metadata.
  - Output: Stdio JSON payload `{"decision": "approve"}` or `{"decision": "continue", "reason": "..."}`.
- **Verification Pipeline**:
  1. **Working Tree Cleanliness**: Runs `git diff --check` if `.git/` exists. Fails with `continue` if unresolved merge conflict markers are detected.
  2. **Test Runner Resolution**:
     - Resolves runners declared in `config.test_runners`.
     - If none configured, scans workspace for recognized manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
  3. **Subprocess Execution (`run_command_safe`)**:
     - Spawns OS subprocess with `shell=False` (or platform wrapper).
     - Caps execution time at `timeout_seconds`.
     - Evaluates exit code:
       - Code `0`: Passed.
       - Code `!= 0`: Block completion (`decision: continue`), capturing stderr/stdout diagnostics.
       - Missing Binary (`FileNotFoundError`): Traps `ENVIRONMENT_UNAVAILABLE`, halts safely, and alerts the developer.

### 2.4 Verdict Protocol Engine (`framework/core/verdict.py`)
- **Purpose**: Standardizes the communication contract between Maker and Checker agents.
- **Data Model**:
  ```python
  @dataclass
  class ResultItem:
      category: str  # "boundary", "test", "doc_sync", "code_quality"
      target: str
      passed: bool
      details: str

  @dataclass
  class VerificationVerdict:
      verdict: str  # "PASS" or "FAIL"
      summary: str
      results: List[ResultItem]
      timestamp: str = field(default_factory=...)
  ```
- **Parser Robustness**:
  - Primary: Extracts raw JSON verdict.
  - Secondary: Extracts JSON block enclosed in markdown code fences (` ```json ... ``` `).
  - Fallback: Heuristic extraction detecting uppercase `PASS` or `FAIL` tokens when LLM returns unformatted text.

---

## 3. Hook CLI Bridges (`framework/scripts/hooks/`)

The hook CLI bridges are lean executable scripts called directly by Antigravity's hook runner.

### 3.1 Dual-Path Python Launcher
To ensure cross-platform execution regardless of whether Antigravity sets the working directory to `.agents/` or the workspace root, `.agents/hooks.json` uses a dual-path launcher:
```json
{
  "antios-guard": {
    "PreToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"import os,runpy; runpy.run_path('framework/scripts/hooks/pre_tool_guard.py' if os.path.exists('framework/scripts/hooks/pre_tool_guard.py') else '../framework/scripts/hooks/pre_tool_guard.py', run_name='__main__')\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python -c \"import os,runpy; runpy.run_path('framework/scripts/hooks/stop_gate.py' if os.path.exists('framework/scripts/hooks/stop_gate.py') else '../framework/scripts/hooks/stop_gate.py', run_name='__main__')\""
      }
    ]
  }
}
```

---

## 4. Skills Subsystem (`.agents/skills/`)

All AntiOS skills reside under `.agents/skills/` to guarantee native Antigravity indexing. Each skill enforces a **strict $\le 60$-line token budget** to prevent context saturation.

| Skill | Path | Lines | Primary Function |
| :--- | :--- | :---: | :--- |
| **`antios-engineer`** | `.agents/skills/antios-engineer/SKILL.md` | 35 | Injects the core engineering lifecycle: Risk Matrix (Low/Medium/High), Maker-Checker dispatch policy, Shallow Depth Law, Stop Gate awareness, and `ACTIVE_CONTEXT.md` sync. |
| **`antios-verifier`** | `.agents/skills/antios-verifier/SKILL.md` | 49 | Injects the independent Checker contract: Fresh context mandate, prohibition of subagent spawning, physical diff audit (`git diff`), physical test execution via `run_command`, and structured JSON verdict reporting. |
| **`antios-debug`** | `.agents/skills/antios-debug/SKILL.md` | 36 | Injects the systematic 5-step root-cause debugging procedure: Reproduce Deterministically $\to$ Formulate Hypothesis $\to$ Isolate Minimal Cause $\to$ Apply Patch $\to$ Verify & Regress-Check. |

---

## 5. Governance State & Memory Subsystem

AntiOS rejects vector databases, opaque embeddings, and SQLite journals in favor of transparent, version-controlled markdown files.

### 5.1 Project Constitution (`docs/AGENTS.md`)
- **Nature**: Human-authored, read upon agent session startup.
- **Budget**: Strictly bounded ($\le 50$ lines).
- **Invariants**:
  1. *Safety Boundaries*: Absolute prohibition against mutating `.agents/`, `framework/`, and configured protected domain paths.
  2. *Physical Verification*: No self-certification; OS test processes must exit 0.
  3. *Same Change Set*: Code modifications and documentation updates must be committed in the same change set.
  4. *Maker-Checker Dispatch*: High-risk changes require independent verifiers with `TypeName='self'`.

### 5.2 Bounded Active Context (`docs/ACTIVE_CONTEXT.md`)
- **Nature**: Agent-maintained, human-auditable rolling operational state.
- **Budget**: Strictly $\le 60$ lines.
- **Sections**:
  - `## Current Focus`: The active workstream or feature under development.
  - `## Active Subtasks`: Checklist of current tasks (completed vs in progress).
  - `## Invariants & Boundaries`: Active project constraints.
  - `## Blockers & Known Issues`: Unresolved obstacles or runtime gaps.
  - `## Dead-End Memory`: Falsified hypotheses to prevent recurring failures.

---

## 6. Test Harness Subsystem (`tests/`)

The framework test harness guarantees that AntiOS governance logic remains 100% verified across updates.
- **Runner**: Pure standard library `python tests/run_all.py` or `pytest`.
- **Test Modules**:
  1. `test_config.py`: Default config loading, custom adapter parsing, corrupt JSON resilience.
  2. `test_guard.py`: Fail-closed type checking, self-protection of `.agents/` and `framework/`, domain boundary enforcement, Windows 8.3 alias blocking.
  3. `test_gate.py`: Clean non-test directory tolerance, passing test verification, failing test rejection with diagnostic capture, fail-closed on malformed payloads.
  4. `test_verdict.py`: Raw JSON parsing, fenced markdown parsing, heuristic fallback, string formatting.
  5. `test_skills.py`: Skill existence, valid YAML frontmatter, $\le 60$-line token budgets, legacy prototype skill pruning, hook JSON validation.
