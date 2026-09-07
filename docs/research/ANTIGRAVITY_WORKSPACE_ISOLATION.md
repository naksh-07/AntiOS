# Antigravity Workspace Isolation & Concurrent Execution Architecture

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity SDK & Subagent Docs (`https://antigravity.google/docs/subagents`), `[OBSERVED]` Empirical AntiOS Test Harness (`test_lifecycle_primitives.py`), `[EXTERNAL_REPORT]` Upstream Forums (Issue #137246)

---

## 1. Executive Summary

When orchestrating multi-agent engineering workflows, concurrent execution on shared file systems introduces severe concurrency hazards: race conditions, file write collisions, corrupted Git index locks, and broken build states. To mitigate these hazards, Antigravity introduces three explicit workspace isolation modes via `invoke_subagent(Workspace=...)`: `inherit`, `branch`, and `share`.

This monograph evaluates the internal mechanics of each workspace mode, audits their concurrency safety profiles, details verified upstream edge cases (including Git `extensions.worktreeConfig` crashes), and defines the operational safety matrix for AntiOS subagent workflows.

---

## 2. Deep Dive: The Three Workspace Isolation Modes

```
                              invoke_subagent(Workspace=...)
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
    Workspace='inherit'              Workspace='branch'               Workspace='share'
 ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
 │ Parent Working Tree  │        │ Isolated Git Worktree│        │ Shared Git Object DB │
 │ Single .git Directory│        │ Dedicated Branch     │        │ Shared Working Path  │
 │ Shared File Handles  │        │ Independent Lock     │        │ Shared Locks         │
 └──────────────────────┘        └──────────────────────┘        └──────────────────────┘
   Read: Fast & Zero Cost          Read: Isolated Baseline         Read: Fast
   Write: HIGH RISK COLLISION      Write: FULLY SAFE ISOLATION     Write: MEDIUM RISK
```

---

### 2.1 Mode 1: `Workspace='inherit'` (Default) `[OFFICIAL]` `[OBSERVED]`
- **Implementation**: The subagent executes directly inside the parent's current working directory (`workspacePaths[0]`).
- **File System State**: Child and parent share identical file descriptors and directory pointers.
- **Git State**: Operations by child and parent target the same `.git` directory and active branch.
- **Concurrency Hazards**:
  - **Git Index Lock Contention**: If parent and child (or two children) execute `git add`, `git commit`, or `git status` simultaneously, Git halts with:
    `fatal: Unable to create '.git/index.lock': File exists.`
  - **Write Clobbering**: Two subagents modifying different functions in the same file simultaneously overwrite each other's changes without conflict detection.
- **Safe Usage**: Strictly for **read-only tasks** (research, static code analysis, test auditing without writing artifacts).

---

### 2.2 Mode 2: `Workspace='branch'` `[OFFICIAL]` `[OBSERVED]`
- **Implementation**: Antigravity provisions a dedicated **`git worktree`** on a detached temporary branch in the background.
- **File System State**: A separate directory tree isolated from the parent working tree. Changes made inside this directory do not affect the parent's uncommitted files.
- **Git State**: Independent Git working tree linked to the parent object database. Has its own separate `index` file, eliminating Git lock contention.
- **Concurrency Hazards**: **Zero write collisions**. Subagents can make destructive modifications, refactors, and test runs safely in parallel.
- **Known Limitations & Failure Modes**:
  1. **The `extensions.worktreeConfig` Platform Crash `[EXTERNAL_REPORT]` (Google AI Developers Forum #137246)**:
     - If the repository has Git worktree extension config enabled (`git config extensions.worktreeConfig true`), Antigravity crashes during worktree creation with:
       `"run state not found"`.
     - Repositories utilizing advanced Git features or managed by certain third-party tools (e.g. Claude Code worktrees) trigger this failure unless the setting is disabled.
  2. **Cold-Start Environment Overhead**:
     - Git worktrees only track committed files.
     - Untracked directories (such as `.venv/`, `node_modules/`, `target/`, and `.cache/`) are **NOT present** in the new worktree.
     - If a subagent attempts to execute tests (`pytest` or `npm test`) inside a branched worktree, the command fails immediately unless the subagent installs dependencies or sets `PYTHONPATH` / `NODE_PATH` back to the parent directory.
  3. **Lifecycle Reconciliation**:
     - When the subagent completes, its worktree remains as a dangling Git branch until explicitly merged or pruned. Antigravity does not automatically reconcile merge conflicts into the parent tree.

---

### 2.3 Mode 3: `Workspace='share'` `[OFFICIAL]`
- **Implementation**: Uses a shared underlying repository directory, similar to Mercurial `hg share` or a shared Git object cache, allowing independent branching without duplicating object storage.
- **Concurrency Hazards**: Intermediate risk. Shared temporary directories or untracked lockfiles can still experience race conditions.

---

## 3. Concurrency Safety & Task Mapping Matrix

The following matrix establishes operational guidelines across the engineering lifecycle:

| Engineering Phase | Recommended Mode | Rationale & Safety Profile | Required Guardrails |
|---|---|---|---|
| **Phase 1: Exploration & Research** | `Workspace='inherit'` | Zero setup latency. Subagent only reads existing files; zero risk of file write collisions. | Enforce read-only tools (`enable_write_tools: false`). |
| **Phase 2: Architectural Planning** | `Workspace='inherit'` | Needs access to existing project documents and plans. Writes only to artifact directories. | Restrict edits to `.gemini/` and brain artifacts. |
| **Phase 3: Parallel Implementation** | `Workspace='branch'` | **Mandatory for concurrent writers**. Completely isolates working trees and Git indexes. | Symlink or point virtual environment to parent `.venv`. Reconcile branch upon completion. |
| **Phase 4: Maker-Checker Verification** | `Workspace='inherit'` | **Checker must inspect the actual working tree**. A branched worktree would not see the Maker's uncommitted edits. | Serial execution: Maker completes edits, yields; Checker inspects working tree. |
| **Phase 5: Baseline Regression Audit** | `Workspace='branch'` | Spawns a clean worktree from `origin/main` to run regression tests against pristine code. | Ensure environment caches are accessible. |

---

## 4. Architectural Rules for AntiOS Subagents

To guarantee absolute safety during multi-agent execution, AntiOS adheres to three mandatory rules:

1. **The Single-Writer Invariant in Inherited Workspaces**:
   - Never allow two concurrent subagents with write permissions (`enable_write_tools: true`) to execute in `Workspace='inherit'`.
   - If parallel implementation is required, all implementing subagents MUST specify `Workspace='branch'`.
2. **Checker Transparency Invariant**:
   - The verification subagent (`antios-verifier`) MUST always execute in `Workspace='inherit'`, because its job is to audit the Maker's uncommitted diff in the active working tree.
   - The Checker MUST be provisioned with `enable_write_tools: false` to guarantee it cannot contaminate the working tree during verification.
3. **Environment Propagation Guard**:
   - When invoking subagents with `Workspace='branch'`, AntiOS must prepend virtual environment paths to the prompt or execution wrapper (`VIRTUAL_ENV` / `PATH`) to prevent cold-start test failures.
