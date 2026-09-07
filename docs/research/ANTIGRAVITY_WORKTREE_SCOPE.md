# Antigravity Git Worktree Scope: Isolation, Identity & Concurrent Execution

**Status:** Canonical Platform Research Monograph  
**Research Phase:** AntiOS Research 3 — Project, Workspace, Repository & Scope Reality  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Runtime Experiments (Part 6), `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Summary

In autonomous multi-agent software engineering, concurrent file writes and Git staging operations represent a primary failure mode. If two agents attempt to stage files simultaneously in a single Git repository, the operation crashes with a fatal `.git/index.lock` contention error.

Antigravity solves this problem by supporting three workspace isolation modes for subagents:
1. `Workspace='inherit'`: Shares the exact physical working directory of the parent.
2. `Workspace='branch'`: Provisions a completely isolated Git worktree backed by a private branch and private staging index.
3. `Workspace='share'`: Shares the underlying repository directory via a lightweight link without duplicating storage.

Through controlled empirical experiments (Part 6 of Research 3), this monograph maps the physical boundaries of Git worktrees, resolves project identity in worktrees, identifies the **Cold-Start Dependency Gap**, and formulates the canonical Maker-Checker workspace assignment policy.

---

## 2. The Three Workspace Modes Compared

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              WORKSPACE MODE COMPARISON                                 │
├──────────────────┬──────────────────────┬──────────────────────┬───────────────────────┤
│ Dimension        │ Workspace='inherit'  │ Workspace='branch'   │ Workspace='share'     │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Physical Path    │ Same directory as    │ Dedicated temporary  │ Shared root with      │
│                  │ parent agent         │ directory on disk    │ linked refs           │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Git Identity     │ Same branch and      │ Private branch       │ Independent branch    │
│                  │ parent staging index │ (e.g. `feat_sub_x`)  │ pointer               │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Staging Index    │ Shared `.git/index`  │ Isolated private     │ Isolated index        │
│                  │ (Lock contention!)   │ `.git/worktrees/idx` │                       │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Uncommitted Edits│ 100% visible to      │ 0% visible (starts   │ 0% visible            │
│ Visibility       │ subagent             │ from branch HEAD)    │                       │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Untracked Files  │ Visible (.venv,      │ MISSING! Untracked   │ Missing               │
│ (.venv, node_mod)│ node_modules present)│ files NOT checked out│                       │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Concurrency      │ Read-only parallel;  │ Full concurrent read │ Full concurrent read  │
│ Safety           │ Concurrent write BAD │ and write safe!      │ and write safe        │
├──────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ AntiOS Role      │ Checker / Verifier   │ Parallel Implementer │ Long-running Worker   │
│ Suitability      │ (`antios-verifier`)  │ (`antios-engineer`)  │                       │
└──────────────────┴──────────────────────┴──────────────────────┴───────────────────────┘
```

---

## 3. Physical Architecture of a Branched Worktree (Part 6 Findings)

In Part 6, a Git worktree was created and inspected via empirical instrumentation:
```
main_repo/ (.git directory, master branch)
├── .git/
│   ├── objects/ (Shared canonical object database)
│   ├── index (Main staging index)
│   └── worktrees/
│       └── branch_worktree/
│           ├── gitdir
│           ├── HEAD (refs/heads/feature_branch)
│           └── index (Private worktree staging index!)
└── (tracked and untracked files)

branch_worktree/ (Linked worktree, feature_branch)
├── .git (POINTER FILE: "gitdir: .../main_repo/.git/worktrees/branch_worktree")
├── README.md (Tracked file -> PRESENT)
├── .agents/ (Tracked hooks & skills -> PRESENT)
├── .venv/ (Untracked directory -> MISSING!)
└── .antios/ (Untracked directory -> MISSING!)
```

### 3.1 The `.git` Pointer File
In a branched worktree, `.git` is **not a directory**. It is an ASCII text file containing a pointer:
`gitdir: C:/Users/.../main_repo/.git/worktrees/branch_worktree`
All Git commands executed within `branch_worktree/` follow this pointer to read repository history from `main_repo/.git/objects/` while writing staging changes strictly to `.../worktrees/branch_worktree/index`.

### 3.2 Elimination of Index Lock Contention
In our concurrent execution experiment (Part 6), the parent repository staged `main_edit.txt` while the worktree simultaneously staged `wt_edit.txt`:
```
Parent: git add main_edit.txt -> Exit Code 0
Worktree: git add wt_edit.txt -> Exit Code 0
```
Because the worktree utilizes its own independent index file (`.git/worktrees/branch_worktree/index`), **both processes staged concurrently with zero lock collisions**.

---

## 4. The Cold-Start Dependency Gap

The most dangerous architectural vulnerability in branched worktrees is the **Untracked Environment Gap** `[OFFICIAL]` `[OBSERVED]`:
- Git worktrees check out **only committed, tracked files**.
- Untracked artifacts—including virtual environments (`.venv/`), Node dependencies (`node_modules/`), compiled binaries, and uncommitted `.antios/` metadata—**do not exist in the worktree**.
- **Failure Mode**: If a subagent operating in `Workspace='branch'` attempts to execute a test suite via `stop_gate.py` (e.g. `pytest` or `npm test`), the runner crashes immediately with:
  `pytest : The term 'pytest' is not recognized` or `Error: Cannot find module 'express'`.
- **Remediation Requirement**: The subagent environment must explicitly inject parent binary paths (`$env:PATH`, `PYTHONPATH`, `NODE_PATH`) or execute test runners using absolute interpreter paths from the parent environment.

---

## 5. Project Identity Divergence in Worktrees

In AntiOS 2.0, `AntiOSDataResolver.resolve_project_identity()` derives `project_id` by hashing the canonical filesystem path:
```python
canonical_path = normalize_path(project_root)
digest = hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()[:16]
return f"proj_{digest}", project_name
```

### The Fragmentation Bug:
When an agent operates in `Workspace='branch'`, its `project_root` is `.../branch_worktree/` rather than `.../main_repo/`.
- As a result, the worktree generates a **completely different `project_id`**.
- Cross-project telemetry, learning observations, and experience logs written to `experience.db` are recorded under an orphaned, ephemeral project identity that vanishes when the worktree is deleted!
- **Fix for AntiOS 3.0**: Project identity must be derived from a stable, path-independent identifier: either the Git origin URL or a committed `project_id` in `.antios/manifest.json`.

---

## 6. The Constitutional Maker-Checker Workspace Assignment Law

The findings of this monograph validate the AntiOS Master Constitution (`INV-04`, `INV-12`):

```
                                  MISSION ORCHESTRATION
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
          MAKER SUBAGENT (Implementer)                  CHECKER SUBAGENT (Verifier)
          Workspace = 'branch'                          Workspace = 'inherit'
          ────────────────────────────                  ───────────────────────────
          • Isolated Git worktree                       • Shares parent working tree
          • Writes code in private branch               • Audits Maker's uncommitted diffs
          • Zero index lock collisions                  • Runs full physical test suites
          • Reconciled via merge/diff                   • Emits binary GO/NOGO verdict
```

1. **Makers Must Use `Workspace='branch'`**: Prevents dirtying the parent working tree during experimental code modifications and permits parallel implementers.
2. **Checkers Must Use `Workspace='inherit'`**: A branched worktree cannot see uncommitted working tree modifications made by the Maker. The Checker must operate in `inherit` to physically audit the live working tree diff.
