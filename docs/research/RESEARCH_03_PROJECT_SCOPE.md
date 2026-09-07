# AntiOS Research 3: Antigravity Project, Workspace, Repository & Scope Reality

**Status:** Canonical Master Executive Monograph  
**Research Phase:** AntiOS Research 3 — Foundational Scope, Project Model & Boundary Architecture  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Target Milestone:** AntiOS 3.0 Project Environment Compiler Foundation  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Runtime Experiments, `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Conclusion

> **"What is the actual scope of an Antigravity project environment, and where should AntiOS live?"**

Prior research established how context is constructed (Research 1) and what the execution lifecycle can observe, influence, transform, and enforce (Research 2). Research 3 resolves the fundamental structural and spatial question of the engineering environment.

Through physical inspection of local application data (`~/.gemini/`), deep analysis of upstream Antigravity 2.0 specifications, and controlled empirical experiments across multi-folder, multi-repository, and worktree sandboxes, this research establishes the following foundational conclusions:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        EXECUTIVE ARCHITECTURAL CONCLUSIONS                             │
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│ 1. Project ≠ Repo │ In Antigravity 2.0, a Project is an administrative management       │
│                   │ container (~/.gemini/config/projects/<id>.json) that binds 1..N    │
│                   │ folders and Git repositories. A Git repo is merely a storage unit. │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ 2. Dual-Plane     │ Filesystem Plane: Unified workspace; relative paths cross repos.  │
│    Scope Model    │ Rule/Git Plane: Strict isolation; upward rule walks stop at .git.  │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ 3. Hook Isolation │ Workspace hooks (.agents/hooks.json) are scoped to their repository│
│                   │ root. An edit in Repo B does NOT trigger hooks in Repo A.          │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ 4. AntiOS Deficit │ AntiOS 2.0 hardcodes workspacePaths[0], failing closed on multi-    │
│                   │ folder/multi-repo projects and fragmenting worktree project_ids.   │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ 5. Hybrid Model   │ AntiOS must adopt a Repository + Project Hybrid Boundary:          │
│    for AntiOS 3.0 │ Federated repo-local enforcement linked by project-level identity. │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

---

## 2. Formal Scope Hierarchy

The execution substrate operates across eight clearly delineated entities arranged into three distinct planes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. ADMINISTRATIVE PLANE                         │
│  Antigravity Project Container (~/.gemini/config/projects/<id>.json)   │
│  Owns: Global UUID, Display Name, Settings, Sandbox, Permission Grants │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Binds 1..N Resources
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  2. FILESYSTEM & VERSION CONTROL PLANE                 │
│  Active Workspace Boundary (workspacePaths: [Folder A, Repo B, ...])   │
│                                                                        │
│  ┌─────────────────────────┐             ┌──────────────────────────┐  │
│  │   Plain Folder Scope    │             │     Repository Scope     │  │
│  │   (Unversioned OS dir)  │             │     Tracked by .git/     │  │
│  └─────────────────────────┘             └────────────┬─────────────┘  │
│                                                       │ git worktree   │
│                                                       ▼                │
│                                          ┌──────────────────────────┐  │
│                                          │      Worktree Scope      │  │
│                                          │   Isolated branch & idx  │  │
│                                          └──────────────────────────┘  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Mounts Active Session
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       3. RUNTIME & EXECUTION PLANE                     │
│  Conversation Session (SQLite DB + brain/<conv-id>/transcript.jsonl)   │
│                                                                        │
│  ┌─────────────────────────┐             ┌──────────────────────────┐  │
│  │   Primary Agent Loop    │             │     Subagent Worker      │  │
│  │   User dialogue, MCP    │────spawn───▶│ Zero Context Inheritance │  │
│  │   orchestration & state │             │ Headless, pristine window│  │
│  └─────────────────────────┘             └──────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Canonical Scope Matrix (Part 13 Requirement)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                             CANONICAL SCOPE MATRIX                                               │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ Scope        │ Context      │ Rules        │ Skills       │ Hooks        │ State / Mem  │ Git VCS      │ Subagents   │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Project      │ Declared     │ Inherits     │ Registered   │ Project-wide │ Persistent   │ None         │ Inherits    │
│              │ Resources    │ global rules │ skill config │ policy grants│ config JSON  │ (Container)  │ permissions │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Workspace    │ Mounted      │ Upward walk  │ .agents/     │ Active       │ Session      │ Enclosing    │ Mounts      │
│              │ paths array  │ from CWD     │ skills/ dir  │ hooks.json   │ working tree │ git roots    │ paths       │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Repository   │ Enclosed     │ Walk stops   │ Local to     │ Local to     │ Committed    │ Canonical    │ Inherits    │
│              │ tree root    │ at .git root │ repo .agents │ repo .agents │ docs/ & JSON │ .git/ store  │ repo bounds │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Worktree     │ Isolated     │ Inherited    │ Inherited    │ Inherited    │ Untracked    │ Private idx, │ Dedicated   │
│              │ checkout dir │ from branch  │ from branch  │ from branch  │ files GAP!   │ private ref  │ workspace   │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Conversation │ Multi-turn   │ Cached per   │ Parsed front-│ Intercepts   │ SQLite DB +  │ Read-only    │ Spawns new  │
│              │ token window │ session      │ matter index │ tool calls   │ JSONL stream │ operations   │ conv ID     │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Primary Agent│ User dialog  │ Enforces     │ Full tool    │ Subprocess   │ Active token │ Direct tool  │ Dispatches  │
│              │ & planning   │ root rules   │ invocation   │ execution    │ window       │ actuation    │ children    │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼─────────────┤
│ Subagent     │ Zero Parent  │ Enforces     │ Eager tools; │ Intercepted  │ Isolated     │ Scoped to    │ Flat / Leaf │
│              │ Inheritance  │ root rules   │ Lazy MCP BROK│ per trigger  │ child SQLite │ assigned wt  │ execution   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
```

---

## 4. Antigravity Project Model Reality

- `[OFFICIAL]` Defined in upstream documentation as a persistent administrative entity.
- `[OBSERVED]` Backed by physical JSON documents in `~/.gemini/config/projects/<project-id>.json` and indexed in `~/.gemini/projects.json`.
- Key Schema Fields:
  - `id`: Project UUID.
  - `name`: Human-readable identifier.
  - `projectResources`: List of `folderUri` and `gitFolder` entries.
  - `settings`: `fileAccessPolicy`, `sandboxMode`, `autoExecutionPolicy`, `artifactReviewMode`.
  - `permissionGrants`: Scoped tool allowlists (`command(...)`, `read_file(...)`).
  - `isWorkspaceOnly`: Strict boundary enforcement flag.
- Sparse Persistence: Persists only explicit deviations from global defaults (`~/.gemini/config/config.json`).

---

## 5. Workspace Model Reality

- `[OFFICIAL]` The active set of filesystem paths (`workspacePaths`) mounted into the Language Server during an execution session.
- In prompt headers, represented as:
  `[URI] -> [CorpusName]` (e.g. `c:\Users\...\AntiOs -> naksh-07/AntiOS`).
- Defines the **Auto-Allowed Boundary**: Tools modifying files within `workspacePaths` proceed without permission friction. Accessing paths outside this set triggers `fileAccessPolicy` prompt prompts.

---

## 6. Repository Model Reality

- `[OFFICIAL]` `[OBSERVED]` A physical filesystem tree containing a `.git` database.
- Boundaries:
  - Git commands (`git log`, `git status`, `git commit`) cannot cross repository boundaries.
  - Upward rule traversal terminates at the repository root (`.git`).
  - Repositories enrolled inside the same project container maintain completely sovereign commit histories and branches.

---

## 7. Worktree Model Reality

- `[OFFICIAL]` `[OBSERVED]` Implements subagent isolation via `Workspace='branch'`.
- Physical structure: A directory containing an ASCII `.git` file:
  `gitdir: .../main_repo/.git/worktrees/<name>`
- **Index Lock Elimination**: Provisions an independent staging index (`.git/worktrees/<name>/index`). Permits fully parallel concurrent staging without `.git/index.lock` collisions.
- **The Untracked Environment Gap**: Worktrees check out tracked files only. Untracked `.venv/`, `node_modules/`, and `.antios/` files are absent, causing test runners to crash unless interpreter paths are propagated.

---

## 8. Conversation, Primary Agent & Subagent Model Reality

- `[OFFICIAL]` `[OBSERVED]`
- **Conversation**: Stored in SQLite (`conversations/<id>.db`) and streaming JSONL (`brain/<id>/.system_generated/logs/transcript.jsonl`).
- **Primary Agent**: Owns the user interface, high-level planning, interactive approvals, and MCP tool orchestration.
- **Subagent**: Operates under **Zero Context Inheritance**. Inherits active workspace files, root `AGENTS.md`, hooks, and skills, but zero parent conversational turns or thoughts.
- **MCP Tool Deficit**: Subagents lack the `call_mcp_tool` wrapper (GitHub Issue #569), failing when invoking lazy MCP tools.

---

## 9. Instruction Scope Reality

- `[OFFICIAL]` `[OBSERVED]`
- `AGENTS.md` and `GEMINI.md` coexist; `AGENTS.md` takes primary precedence.
- Upward traversal algorithm: Ascends from active file directory to parent, terminating immediately at `.git`.
- Rules in `.agents/rules/*.md` support dynamic activation (`trigger: always | file_pattern | intent`).
- Instructions placed in a parent folder above multiple Git repositories are **completely ignored** by agents operating inside child repositories.

---

## 10. Persistence Scope Reality

- Information persists across nine distinct operational transitions:
  1. **Ephemeral**: In-memory tokens, `ephemeralMessage` (wiped per turn).
  2. **Session**: Transcripts, SQLite conversation DB, brain artifacts (persisted on disk, dormant across sessions).
  3. **Project**: `config/projects/<id>.json`, permission allowlists (survives IDE restarts and reboots).
  4. **Repository**: Tracked Git tree, committed `.agents/` rules, skills, hooks (survives checkouts and team clones).
  5. **User / Global**: `config/config.json`, `projects.json`, `experience.db` (machine-wide persistence).

---

## 11. Multi-Repository Findings

- Sibling directories in a multi-repo project are reachable via relative filesystem paths (`../sibling_repo/`).
- Sibling repositories do **not** share Git state, instructions, skills, or hooks.
- A PreToolUse hook in Repo A does not execute when modifying files in Repo B.
- Verifying an entire multi-repo project requires federating Git diffs and test suites across each sovereign repository root.

---

## 12. Security & Sovereignty Audit: The 4-Zone Boundary

AntiOS establishes the constitutional boundary:
$$\text{SOURCE} \neq \text{INSTANCE} \neq \text{PROJECT} \neq \text{ANTIGRAVITY}$$

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ANTIOS 4-ZONE SECURITY BOUNDARY AUDIT                           │
├─────────────┬─────────────────────────────────────────────────┬──────────┬─────────────┤
│ Zone        │ Definition & Physical Location                  │ Validated│ Risk Factor │
├─────────────┼─────────────────────────────────────────────────┼──────────┼─────────────┤
│ SOURCE      │ Universal Core Engine (naksh-07/AntiOS)         │ YES      │ Read-only;  │
│             │ framework/, tests/, scripts/                    │ (INV-10) │ immutable   │
├─────────────┼─────────────────────────────────────────────────┼──────────┼─────────────┤
│ INSTANCE    │ Target Project OS Runtime                       │ YES      │ Confined to │
│             │ <target_root>/.antios/                          │          │ target root │
├─────────────┼─────────────────────────────────────────────────┼──────────┼─────────────┤
│ PROJECT     │ User Application Codebase & Adapters            │ YES      │ Sovereign;  │
│             │ Target repository files & antios.config.json    │          │ untouched   │
├─────────────┼─────────────────────────────────────────────────┼──────────┼─────────────┤
│ ANTIGRAVITY │ Host Execution Substrate                        │ YES      │ Platform    │
│             │ ~/.gemini/, .agents/hooks.json, skills/         │ (INV-01) │ sovereignty │
└─────────────┴─────────────────────────────────────────────────┴──────────┴─────────────┘
```

### Audit Findings:
1. **Cross-Project File Access**: Confined by Antigravity's `isWorkspaceOnly` and `fileAccessPolicy`. AntiOS runtime hooks enforce boundary confinement relative to workspace roots.
2. **Hook Cross-Contamination**: Hooks cannot contaminate external projects because they are registered in workspace-local `.agents/hooks.json`.
3. **True Security Boundary**: The inviolable physical security boundary is the **Stop Gate (`stop_gate.py`) auditing `git diff`**. While shell redirection in PowerShell can bypass regex `PreToolUse`, the Stop Gate physically blocks session exit if unauthorized working tree mutations occur.

---

## 13. Current AntiOS Scope Audit (Part 11 Requirement)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           CURRENT ANTIOS SCOPE AUDIT TABLE                                               │
├────┬─────────────────────────────┬───────────────────────────────┬───────────────────────────┬──────────────┬────────────┤
│ #  │ AntiOS Assumption           │ Antigravity Scope Reality     │ Concrete Evidence         │ Classification│ Verdict   │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 1  │ Repository == Project       │ Project is a multi-resource   │ config/projects/<id>.json │ [OFFICIAL]   │ INCORRECT  │
│    │ (1:1 equivalence)           │ container enclosing N repos   │ projectResources.resources│ [OBSERVED]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 2  │ Single Workspace Path       │ Antigravity passes array of   │ pre_tool_guard.py:L71     │ [OBSERVED]   │ INCORRECT  │
│    │ (workspace_paths[0])        │ workspacePaths [res1, res2]   │ hardcodes index 0         │ [CONFLICT]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 3  │ .agents/ is Repo-Local      │ Native discovery requires     │ DECISION_REGISTER ADR 05; │ [OFFICIAL]   │ CORRECT    │
│    │ (<repo_root>/.agents/)      │ .agents/ at repo root         │ upward walk stops at .git │ [OBSERVED]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 4  │ .antios/ is Repo-Local      │ Pristine worktrees lack       │ Part 6 test: untracked    │ [OBSERVED]   │ PARTIAL    │
│    │ (<repo_root>/.antios/)      │ uncommitted .antios/ files    │ .antios is missing in wt  │ [CONFLICT]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 5  │ Project ID from Path Hash   │ Worktrees get different paths,│ experience.py:L142        │ [OBSERVED]   │ INCORRECT  │
│    │ (hashlib.sha256(path))      │ fragmenting telemetry ID      │ hashlib path hashing      │ [CONFLICT]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 6  │ System A is Git-Versioned   │ Markdown/JSON files in Git    │ ACTIVE_CONTEXT.md,        │ [OFFICIAL]   │ CORRECT    │
│    │ (docs/ACTIVE_CONTEXT.md)    │ survive conversations         │ LESSONS.md survive in VCS │ [OBSERVED]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 7  │ System B is External        │ Central SQLite WAL database   │ experience.db outside repo│ [OFFICIAL]   │ CORRECT    │
│    │ (experience.db)             │ tracks cross-project facts    │ installation.py:L130      │ [OBSERVED]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 8  │ Hooks via Local Python      │ Executes in .agents/ cwd via  │ agy-customizations/hooks  │ [OFFICIAL]   │ CORRECT    │
│    │ subprocess (stdio JSON)     │ system Python binary          │ cmd /c python ...         │ [OBSERVED]   │            │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 9  │ Worktree Environment Parity │ Worktree lacks .venv and      │ Part 6 test: untracked    │ [OFFICIAL]   │ INCORRECT  │
│    │ (Test runners execute fine) │ node_modules dependencies     │ .venv missing in worktree │ [OBSERVED]   │ (Gap)      │
├────┼─────────────────────────────┼───────────────────────────────┼───────────────────────────┼──────────────┼────────────┤
│ 10 │ 4-Zone Security Demarcation │ SOURCE != INSTANCE !=         │ Invariant 10, compiler.py │ [OFFICIAL]   │ CORRECT    │
│    │ (Invariant 10)              │ PROJECT != ANTIGRAVITY holds  │ zero framework leakage    │              │            │
└────┴─────────────────────────────┴───────────────────────────────┴───────────────────────────┴──────────────┴────────────┘
```

---

## 14. Recommended Project Environment Boundary for AntiOS 3.0

Based on empirical evidence, AntiOS 3.0 must adopt a **Repository + Project Hybrid Boundary Model** (Form C):

```
┌────────────────────────────────────────────────────────────────────────┐
│                   ANTIOS 3.0 HYBRID BOUNDARY MODEL                     │
├────────────────────────────────────────────────────────────────────────┤
│ 1. ADMINISTRATIVE TIER (Antigravity Project Scope)                     │
│    • Identity: Stable UUID derived from Git origin remote or project   │
│      manifest, NOT physical working tree filesystem paths.             │
│    • Telemetry: Centralized experience.db indexed by stable Project ID.│
│    • Settings: Project-level permission grants and sandbox policies.   │
├────────────────────────────────────────────────────────────────────────┤
│ 2. ENFORCEMENT TIER (Federated Repository Scope)                       │
│    • Hook Compilation: Compiler compiles .agents/ and .antios/ into    │
│      EACH enrolled repository root within the project container.       │
│    • Multi-Folder Guard: pre_tool_guard.py iterates all workspacePaths │
│      to permit valid cross-repo mutations while blocking escapes.      │
│    • Stop Gate Federation: stop_gate.py audits git diff across each    │
│      repository root, validating localized test suites independently.  │
├────────────────────────────────────────────────────────────────────────┤
│ 3. WORKTREE EXECUTION TIER (Isolated Execution Scope)                  │
│    • Dependency Propagation: Subagents in Workspace='branch' receive   │
│      parent virtualenv/binary paths via environment injection.         │
│    • Maker-Checker Duality: Makers write in isolated worktrees;        │
│      Checkers audit live working trees in Workspace='inherit'.         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Research 4 Foundational Questions

The completion of Research 3 opens the path to **AntiOS Research 4: Project Environment Compilation & Multi-Repository Governance**:

1. **How should the AntiOS Compiler discover, enroll, and compile governance across a multi-repository project container?**
2. **What is the optimal federation protocol for `stop_gate.py` when verifying commits spanning multiple Git repositories?**
3. **How can untracked virtual environment dependencies (`.venv`, `node_modules`) be transparently bridged into isolated Git worktrees (`Workspace='branch'`) without mutating user Git configuration?**
4. **How should cross-repository semantic dependencies (e.g. Repo A depending on schema in Repo B) be represented in `.antios/knowledge.json`?**
5. **Can Antigravity's native `permissionGrants` be programmatically managed by the AntiOS Project Compiler to automate zero-prompt tool approvals?**
