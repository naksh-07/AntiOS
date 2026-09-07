# Antigravity Instruction Scope: Rules, Skills & Hooks Resolution

**Status:** Canonical Platform Research Monograph  
**Research Phase:** AntiOS Research 3 — Project, Workspace, Repository & Scope Reality  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Runtime Experiments (Part 5), `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Summary

In Antigravity, instruction steering is not a monolithic prompt injection. Instead, it is governed by a multi-tiered, hierarchical resolution engine that discovers, evaluates, and merges rules, skills, and hooks based on the active file path, working directory, and repository boundaries.

This monograph documents the exact scope of:
1. `AGENTS.md` (Constitutional and directory-level instructions)
2. `GEMINI.md` (Legacy and alternative instruction document)
3. `.agents/rules/*.md` (Modular, conditional rule documents)
4. `.agents/skills/*/SKILL.md` (Progressive procedural capabilities)
5. `.agents/hooks.json` (Deterministic lifecycle interception)

Across six operational environments:
- **A.** Project Root
- **B.** Repository Root
- **C.** Nested Subfolder
- **D.** Sibling Repository
- **E.** Subagent Execution
- **F.** Branch Git Worktree

---

## 2. The Instruction Scope Matrix

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       INSTRUCTION RESOLUTION SCOPE MATRIX                                        │
├───────────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬───────────────────┤
│ Instruction Type  │ A. Project   │ B. Repo      │ C. Nested    │ D. Sibling   │ E. Subagent  │ F. Branch         │
│                   │ Root         │ Root         │ Folder       │ Repo         │ Execution    │ Worktree          │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────┤
│ AGENTS.md         │ Ingested if  │ Ingested at  │ Ingested if  │ Isolated;    │ Ingested at  │ Tracked copy      │
│                   │ in workspace │ Turn 0 & walk│ in subtree   │ stops at .git│ Turn 0 (Root)│ ingested directly │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────┤
│ GEMINI.md         │ Supported;   │ Co-exists    │ Ingested if  │ Isolated;    │ Supported    │ Tracked copy      │
│                   │ lower prec.  │ with AGENTS  │ in subtree   │ stops at .git│ at Turn 0    │ ingested directly │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────┤
│ .agents/rules/    │ Discovered if│ Discovered   │ Inherited by │ Isolated     │ Discovered & │ Tracked copy      │
│                   │ declared     │ dynamically  │ descendants  │ to repo      │ matched      │ discovered        │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────┤
│ .agents/skills/   │ Registered if│ Discovered   │ Inherited by │ Isolated     │ Declared in  │ Tracked copy      │
│                   │ declared     │ at workspace │ descendants  │ to repo      │ tool schema  │ discovered        │
├───────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼───────────────────┤
│ .agents/hooks.json│ Registered   │ Registered at│ Inherited by │ Isolated     │ Executed     │ Tracked copy      │
│                   │ per root     │ workspace    │ descendants  │ to repo      │ per trigger  │ executed          │
└───────────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴───────────────────┘
```

---

## 3. Deep-Dive Resolution Mechanics

### 3.1 `AGENTS.md` and `GEMINI.md` Upward Traversal
- `[OFFICIAL]` `[OBSERVED]` Traversal algorithm:
  1. Start at the canonical directory of the active file or current working directory.
  2. Check for `AGENTS.md` and `GEMINI.md`. If present, append to the rule ingestion list.
  3. Ascend to parent directory (`curr = curr.parent`).
  4. **Stop condition**: If `curr` contains a `.git` directory, process `AGENTS.md`/`GEMINI.md` at that root, and **immediately terminate traversal**.
- **Coexistence**: Both `AGENTS.md` and `GEMINI.md` can coexist in the same directory. When both are present, `AGENTS.md` is processed with primary precedence, followed by `GEMINI.md`.
- **Deduplication**: Files are indexed by canonical absolute path. The same rule document is never ingested twice in a single turn.

### 3.2 Modular Rules (`.agents/rules/*.md`)
- `[OFFICIAL]` Rules in `.agents/rules/` provide modular, trigger-based steering:
  ```markdown
  ---
  trigger: always | file_pattern: *.py | intent: debug
  ---
  # Modular Architecture Rule
  ```
- **Discovery**: Evaluated dynamically by the Language Server.
  - `trigger: always`: Auto-injected whenever the enclosing workspace is active.
  - `trigger: file_pattern: <glob>`: Injected into the context window only when a file matching the glob is viewed, edited, or active in editor.
  - `trigger: intent: <regex>`: Injected when the user prompt matches the regex intent pattern.

### 3.3 Progressive Skill Loading (`.agents/skills/*/SKILL.md`)
- `[OFFICIAL]` **Two-Phase Loading Pattern**:
  - **Phase 1 (Registration)**: At startup, Antigravity parses only the YAML frontmatter (`name` and `description`). This creates an entry in the `<skills>` system prompt block with zero procedural text overhead (~50 tokens per skill).
  - **Phase 2 (Actuation)**: When an agent decides a skill is relevant (or user invokes `/skill-name`), the agent invokes `view_file` on the explicit `SKILL.md` path. The procedural instructions enter the prompt window on-demand.

### 3.4 Hook Resolution (`.agents/hooks.json`)
- `[OFFICIAL]` `[OBSERVED]`
  - Registered at workspace root.
  - Enforces policy across all tools (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`).
  - **CWD Invariant**: Hook commands execute with `cwd = <workspace_root>/.agents/`. Any Python script executed via hooks must compute repository root via `Path(__file__).resolve().parent.parent` or receive `workspacePaths` from `stdin`.

---

## 4. Scope Dimension Analysis (A Through F)

### A. Project Root (Above Git Repositories)
- In a multi-repo project where the project container encloses multiple `.git` repositories, an `AGENTS.md` placed in the parent directory is **ignored** by agents operating inside child repositories because upward walks stop at each child's `.git` root.

### B. Repository Root
- The canonical home for baseline instructions. `AGENTS.md`, `.agents/rules/`, `.agents/skills/`, and `.agents/hooks.json` placed here govern the entire repository and all nested directories.

### C. Nested Subfolder
- Specialized instructions in `src/subfolder/AGENTS.md` apply to that subfolder and its descendants. They merge with and inherit parent rules discovered during upward ascent.

### D. Sibling Repository
- Total isolation. Repo A and Repo B do not share rules, skills, or hooks. A mutation in Repo B does not trigger hooks in Repo A.

### E. Subagent Execution
- Subagents inherit the root `AGENTS.md`, active `.agents/rules/`, registered skills index, and workspace hooks. They do **not** inherit parent conversational turns, thoughts, or scratchpad files (Zero Context Inheritance).

### F. Branch Git Worktree (`Workspace='branch'`)
- Because a Git worktree checks out tracked files, all version-controlled rules (`AGENTS.md`), skills, and `hooks.json` are present and fully functional. Untracked configuration files (such as `.antios/`) are missing unless committed or explicitly populated.

---

## 5. Architectural Implications for AntiOS 3.0

1. **Constitutional Grounding Must Reside at Repository Roots**:
   AntiOS cannot rely on a single root `AGENTS.md` in a multi-repo parent directory. The compiler must ensure every enrolled repository root receives its own `.agents/` directory with canonical grounding.
2. **Hook Scripts Must Be Tracked in VCS**:
   Hooks and runtime scripts must be committed to Git so that when subagents operate in isolated worktrees (`Workspace='branch'`), the hook guards and Stop Gates remain 100% active.
3. **Skill Discovery Relies on Standard Paths**:
   Skills must always reside in `<repo_root>/.agents/skills/` to guarantee discoverability by Antigravity's native engine.
