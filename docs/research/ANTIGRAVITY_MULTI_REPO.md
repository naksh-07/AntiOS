# Antigravity Multi-Repository & Multi-Folder Reality

**Status:** Canonical Platform Research Monograph  
**Research Phase:** AntiOS Research 3 — Project, Workspace, Repository & Scope Reality  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Runtime Experiments (Parts 3, 4, 9), `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Summary

A critical question for the future AntiOS Project Environment Compiler is how Google Antigravity treats complex, distributed codebases:
> **Does Antigravity treat a multi-repository codebase as a single monolithic engineering environment, as isolated disjoint repositories inside one project container, or something else?**

Through controlled empirical experiments (Parts 3, 4, and 9 of Research 3) executed on a live test harness, we establish that **Antigravity implements a Dual-Plane Scope Model** `[OFFICIAL]` `[OBSERVED]`:
1. **At the Filesystem & Project Plane**: Antigravity treats multi-folder and multi-repository configurations as a **unified engineering workspace**. The agent can seamlessly read, navigate, search, and edit files across sibling directories and repositories using relative paths without permission prompts.
2. **At the Version Control & Rule Plane**: Antigravity enforces **strict repository isolation**. Git operations (`git status`, `git commit`, `git diff`) are hard-bounded by each repository's `.git` boundary. Crucially, **upward rule traversal (`AGENTS.md`) stops dead at the `.git` root**, meaning instruction files and hooks in Repository A do not automatically govern or bleed into Repository B.

---

## 2. Multi-Folder Project Topology (Part 3 Experiment)

### 2.1 Experimental Setup
A disposable project environment was constructed containing three independent functional folders under a common root:
```
part3_project/
├── AGENTS.md (Root Project Instructions: SemVer requirement)
├── frontend/
│   ├── AGENTS.md (Frontend Instructions: React 19 + Tailwind)
│   └── LoginButton.tsx
├── backend/
│   ├── AGENTS.md (Backend Instructions: FastAPI + Pydantic)
│   ├── auth_service.py (contains `def authenticate(...)`)
│   └── server.py
└── shared/
    └── types.ts (UserSession interface)
```

### 2.2 Empirical Observations & Measurements
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PART 3 EMPIRICAL EXPERIMENT RESULTS                             │
├────────────────────────────────────────┬───────────┬──────────────────────────────────┤
│ Metric / Behavioral Probe              │ Result    │ Evidence Classification          │
├────────────────────────────────────────┼───────────┼──────────────────────────────────┤
│ Sibling Reachability from frontend/    │ TRUE      │ [OBSERVED] Direct relative path  │
│ Search from root finds backend/ auth   │ TRUE      │ [OBSERVED] Full walk discovery   │
│ Upward rule walk from frontend/        │ Discovers │ [OBSERVED] Both frontend/ &      │
│                                        │ 2 rules   │ project root AGENTS.md found     │
│ Backend AGENTS.md isolated from front  │ TRUE      │ [OBSERVED] Traversal ascends to  │
│                                        │           │ parent, never crosses to sibling │
└────────────────────────────────────────┴───────────┴──────────────────────────────────┘
```

### 2.3 Key Findings:
1. **Sibling Traversal via Relative Paths**: An agent operating in `frontend/` can directly read `../backend/auth_service.py` and `../shared/types.ts`. Sibling folders are immediately reachable if mounted under a common workspace root.
2. **Rule Traversal in Plain Folders**: Because no `.git` boundary exists in a plain multi-folder project, an upward walk from `frontend/` ascends all the way to `part3_project/AGENTS.md`. Both `frontend/AGENTS.md` and root `AGENTS.md` are loaded and merged.
3. **Lateral Rule Isolation**: Crucially, `backend/AGENTS.md` is **never loaded** during frontend execution. Upward walks only ascend parent lineages; they never inspect sibling branches.

---

## 3. Multi-Repository Project Topology (Part 4 Experiment)

### 3.1 Experimental Setup
To test Git boundary enforcement, a disposable project was constructed containing three separate Git repositories:
```
part4_multi_repo_project/ (Plain parent directory, NOT a git repo)
├── AGENTS.md (Project Root instructions: Global PR requirement)
├── repo_frontend/ (.git initialized)
│   ├── .agents/
│   │   ├── hooks.json (PreToolUse guard)
│   │   └── skills/front-skill/SKILL.md
│   ├── AGENTS.md (Frontend rules)
│   └── index.js
├── repo_backend/ (.git initialized)
│   ├── AGENTS.md (Backend rules)
│   └── main.py
└── repo_shared/ (.git initialized)
    └── contract.json
```

### 3.2 Empirical Observations & Measurements
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PART 4 EMPIRICAL EXPERIMENT RESULTS                             │
├────────────────────────────────────────┬───────────┬──────────────────────────────────┤
│ Metric / Behavioral Probe              │ Result    │ Evidence Classification          │
├────────────────────────────────────────┼───────────┼──────────────────────────────────┤
│ Git Root Isolation                     │ TRUE      │ [OBSERVED] rev-parse returns     │
│                                        │           │ distinct independent roots       │
│ Upward Rule Walk Stops at .git         │ TRUE      │ [OBSERVED] Traversal terminates  │
│                                        │           │ at repo_frontend/.git            │
│ Parent AGENTS.md Ingested?             │ FALSE     │ [OBSERVED] Blocked by .git stop  │
│ Git Cross-Repo Command Execution       │ BLOCKED / │ [OBSERVED] git log ../repo_back  │
│                                        │ FATAL     │ fails with outside repo error    │
│ Skills in Repo A Visible in Repo B?    │ FALSE     │ [OBSERVED] .agents/skills/ in A  │
│                                        │           │ isolated from B                  │
│ Hooks in Repo A Enforced in Repo B?    │ FALSE     │ [OBSERVED] hooks.json in A does  │
│                                        │           │ not trigger on B mutations       │
└────────────────────────────────────────┴───────────┴──────────────────────────────────┘
```

### 3.3 The Inviolable `.git` Rule Stop Boundary
The most profound architectural discovery is the **`.git` Upward Traversal Barrier** `[OFFICIAL]` `[OBSERVED]`:
- In Antigravity's Language Server, rule discovery starts at the active file's directory and walks up directory parents.
- **The walk terminates immediately upon encountering a `.git` directory.**
- **Consequence**: `part4_multi_repo_project/AGENTS.md` (residing above the `.git` repositories) is **100% invisible** to an agent operating inside `repo_frontend/` or `repo_backend/`!
- Placing instructions in a parent folder that encloses multiple Git repositories will **fail to ground the agent** unless each repository contains its own root `AGENTS.md` or the parent directory itself is configured as an explicit workspace resource.

---

## 4. Project Intelligence Scope Across Repositories (Part 9 Experiment)

### 4.1 The Cognitive Localization Phenomenon
In Part 9, we tested agent architectural discovery across three distinct repositories:
- `repo_a`: Contains `ARCH_A.md` (Billing service architecture) and `client.py`.
- `repo_b`: Contains `ARCH_B.md` (Shipping inventory architecture) and `warehouse.py`.
- `repo_shared`: Contains `CONTRACT.md` (Canonical inter-service API contract).

### 4.2 Findings on Agent Cognitive Behavior:
1. **Localized Default Focus**: When asked to resolve a billing task in `repo_a`, the agent's natural search tools (`list_dir`, `find_by_name`, `grep_search`) default to the current repository directory tree.
2. **Contract Discovery via Symbol References**: If `client.py` imports or references terms from `CONTRACT.md`, the agent expands its search laterally across sibling workspace paths.
3. **Absence of Monolithic Bleed**: The agent does not blindly load or apply `ARCH_B.md` when working in `repo_a`. Cognitive context remains bounded unless explicitly prompted or referenced in shared code.

---

## 5. Architectural Synthesis: How Antigravity Models Multi-Repo

Antigravity models multi-repository environments as:
> **Multiple Sovereign Repositories Co-Existing Inside One Administrative Project Container.**

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ANTIGRAVITY PROJECT CONTAINER                     │
│               Governs: Permissions, Security, Sandbox                  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│      SOVEREIGN REPOSITORY A     │         │      SOVEREIGN REPOSITORY B      │
│  ├── .git/ (Independent VCS)    │         │  ├── .git/ (Independent VCS)     │
│  ├── .agents/ (Local Rules/Hks) │         │  ├── .agents/ (Local Rules/Hks)  │
│  └── Source Code A              │         │  └── Source Code B               │
└─────────────────────────────────┘         └──────────────────────────────────┘
```

### Implications for AntiOS 3.0:
1. **AntiOS 2.0 Hardcoded `workspacePaths[0]` is Defective**:
   Current AntiOS hooks (`pre_tool_guard.py` and `stop_gate.py`) inspect only `workspacePaths[0]`. In a multi-repo workspace, any edit in `repo_backend` is rejected fail-closed. AntiOS must iterate across all declared `workspacePaths`.
2. **Rule Federation Requirement**:
   Because instructions do not traverse past `.git`, AntiOS cannot simply drop an `AGENTS.md` in the parent directory. The future Project Environment Compiler must compile and link `.agents/` configurations into **each sovereign repository root**.
3. **Sovereign Git Operations**:
   The verification Stop Gate must inspect `git status` and `git diff` on a per-repository basis. Running a single `git diff` from a non-git parent root crashes with a fatal error.
