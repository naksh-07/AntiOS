# AntiOS Research 4: Multi-Repository Agent Intelligence & Dual-Plane Governance
## Cross-Repository Wayfinding, Dependency Mapping, and Federated Stop Gates

**Status**: CANONICAL RESEARCH MONOGRAPH  
**Phase**: AntiOS Research 4 — Large Repository Agent Engineering & Project Intelligence  
**Target Repository**: `naksh-07/AntiOS`  
**Evidence Standard**: `[OFFICIAL]`, `[OBSERVED]`, `[INFERRED]`, `[EXTERNAL_REPORT]`, `[HYPOTHESIS]`, `[UNKNOWN]`, `[CONFLICT]`  

---

## 1. Executive Summary

Modern enterprise software systems rarely live in a single monolithic repository. They are composed of sovereign microservices, shared libraries, desktop shells, and documentation repositories. When an autonomous agent operates across multiple repositories (or within a parent workspace containing multiple git roots), it encounters the **Multi-Repository Boundary Problem**:
1. **Rule Traversal Truncation (`[OFFICIAL]`)**: Google Antigravity upward rule traversal strictly terminates at the enclosing `.git` boundary. Governance rules placed in a parent workspace directory are completely invisible to agents operating within a nested git clone.
2. **Hardcoded Path Fragility (`[OBSERVED]`)**: Existing runtime gates (such as `framework/hooks/gate.py`) frequently hardcode `workspacePaths[0]`, causing silent failures or misdirected test execution when the agent shifts focus between repositories.
3. **Cross-Repo Verification Blindness (`[INFERRED]`)**: Verifying Repository A passes its local unit tests does not guarantee that Repository B (which consumes A's interface) has not suffered a breaking integration regression.

This monograph formulates the **Multi-Repository Agent Intelligence Architecture** for AntiOS. We define:
- The **Dual-Plane Scope Model** (separating the Host/Workspace Plane from the Repository Plane).
- The **Project Environment Compiler** distribution protocol (projecting compiled `.agents/` configurations into every sovereign repository root).
- The **Federated Stop Gate Protocol** for cross-repository verification and dependency mapping.

---

## 2. The Dual-Plane Scope Model

To govern multi-repo environments without violating git sovereignty or platform traversal rules, AntiOS establishes a **Dual-Plane Architecture**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOST / WORKSPACE PLANE                              │
│  Scope: Multi-Repo Workspace Root (e.g. C:\Users\Suraj\Documents\AntiOs)   │
│  Responsibilities:                                                          │
│    • Global Subsystem Catalog (Repo-to-Domain Map)                          │
│    • Cross-Repo Dependency Graph (DAG)                                      │
│    • Cross-Repo Integration Test Harnesses                                  │
│    • Project Environment Compiler (Distribution Authority)                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                     Compiles & Projects Configurations
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
┌───────────────────────────────┐             ┌───────────────────────────────┐
│     REPOSITORY PLANE: REPO A  │             │     REPOSITORY PLANE: REPO B  │
│  Scope: Sovereign Git Root A  │             │  Scope: Sovereign Git Root B  │
│  Contents:                    │             │  Contents:                    │
│    • .git/                    │             │    • .git/                    │
│    • .agents/hooks.json       │             │    • .agents/hooks.json       │
│    • AGENTS.md (Local Rules)  │             │    • AGENTS.md (Local Rules)  │
│    • Local Stop Gate (gate.py)│             │    • Local Stop Gate (gate.py)│
│    • Local MVR Test Suites    │             │    • Local MVR Test Suites    │
└───────────────────────────────┘             └───────────────────────────────┘
```

### 2.1 The Workspace Plane (Coordination Authority)
- Operates at the multi-repo workspace root.
- Maintains the master cross-repo manifest (`antios.workspace.json`), documenting inter-repo dependencies, relative repository paths, and integration contract tests.
- Contains the **Project Environment Compiler**, which runs as a one-shot build step to emit sovereign `.agents/` directories into each child repository.

### 2.2 The Repository Plane (Sovereignty & Physical Enforcement)
- Operates strictly within each child git repository.
- Each child repository possesses its own `.git` root, its own local `.agents/hooks.json`, its own local `AGENTS.md`, and its own local test suite.
- Hooks running inside Repo A execute with Repo A as their working directory, preserving complete git isolation.

---

## 3. Platform Constraint: Upward Rule Traversal Truncation

`[OFFICIAL]` The Google Antigravity platform discovers instructions and rules (`AGENTS.md`) by walking up the directory tree from the target file toward the filesystem root. However, **this traversal halts at the nearest `.git` directory**:

```
Path: C:\Workspace\RepoA\src\core\module.py
  1. Check: C:\Workspace\RepoA\src\core\AGENTS.md -> (Found/None)
  2. Check: C:\Workspace\RepoA\src\AGENTS.md      -> (Found/None)
  3. Check: C:\Workspace\RepoA\AGENTS.md          -> (Found/None)
  4. Encounter C:\Workspace\RepoA\.git             -> [TRAVERSAL TERMINATES]
  X. Never checked: C:\Workspace\AGENTS.md        -> (TOTALLY INVISIBLE)
```

### 3.1 Architectural Impact
Placing global governance rules or route maps exclusively at `C:\Workspace\AGENTS.md` guarantees that **any subagent or tool call operating inside `RepoA` is completely ungoverned and blind to workspace-level intelligence**.

### 3.2 The Compiler Projection Solution
To guarantee governance across all repositories, AntiOS mandates **Compiler Projection**:
- The Project Environment Compiler reads `antios.workspace.json` at the workspace root.
- It compiles a sovereign `AGENTS.md` and `.agents/` folder.
- It projects these files into **every detected repository root**:
  - `RepoA/.agents/hooks.json`
  - `RepoA/AGENTS.md`
  - `RepoB/.agents/hooks.json`
  - `RepoB/AGENTS.md`
- Each local `AGENTS.md` includes a dedicated **Multi-Repo Context Header** linking the child repository to the workspace DAG.

---

## 4. Cross-Repository Wayfinding & Dependency Mapping

When an agent is assigned a task in a multi-repo project, it must first resolve the **Repository Boundary Question**:
> *Which repository owns this feature, and what downstream repositories will break if I modify it?*

### 4.1 The Workspace Repository Directory (`antios.workspace.json`)
The Workspace Plane provides a centralized, deterministic directory of repositories:

```json
{
  "$schema": "https://antios.dev/schema/v1/workspace.json",
  "workspace_root": "C:/Users/Suraj/Documents/AntiOs",
  "repositories": [
    {
      "name": "antios-core",
      "path": ".",
      "role": "Core Framework & Hook Enforcement",
      "exports": ["framework.hooks", "framework.intelligence"],
      "dependencies": []
    },
    {
      "name": "studylab-desktop",
      "path": "sandbox/studylab",
      "role": "Electron Desktop Shell & UI",
      "exports": ["app.ui"],
      "dependencies": ["antios-core"]
    }
  ],
  "cross_repo_verification": [
    {
      "name": "contract-test",
      "command": ["pytest", "tests/integration/test_cross_repo.py"],
      "trigger_paths": ["framework/hooks/**"]
    }
  ]
}
```

### 4.2 Progressive Multi-Repo Wayfinding Funnel
1. **Turn 0 (Repo Resolution)**: Agent inspects `antios.workspace.json` (~150 tokens) to determine which repository owns the target domain.
2. **Turn 1 (Local Navigation)**: Agent enters the sovereign repository and consults its local `SUBSYSTEMS.md` (~300 tokens).
3. **Turn 2 (Blast-Radius Calculation)**: If modifying exported APIs, the agent queries the workspace dependency graph to identify dependent repositories requiring integration checks.

---

## 5. Federated Stop Gate Verification

In a single repository, `gate.py` executes local unit tests. In a multi-repo project, local verification is necessary but insufficient.

### 5.1 The `workspacePaths[0]` Defect in `gate.py`
`[OBSERVED]` Auditing `framework/hooks/gate.py` reveals a critical bug in multi-repo handling:
```python
# CURRENT FLAWED IMPLEMENTATION:
workspace_root = event.get("workspacePaths", ["."])[0]
```
If an Antigravity workspace contains multiple paths `[RepoA, RepoB]`, `gate.py` always anchors its test runner to `workspacePaths[0]`. When an agent works in `RepoB`, the Stop Gate erroneously attempts to execute `RepoA`'s test suite, reporting false failures or executing wrong commands.

### 5.2 The Dynamic Repository Context Resolver
AntiOS 3.0 resolves the active repository dynamically by inspecting the agent's touched files:

```python
def resolve_active_repository(touched_files: list[str], workspace_repos: list[dict]) -> dict:
    """Resolve which sovereign git repository owns the majority of touched files."""
    for file_path in touched_files:
        for repo in workspace_repos:
            if file_path.startswith(repo["path"]):
                return repo
    return workspace_repos[0]
```

### 5.3 Two-Tier Federated Verification Lifecycle

```
                       ┌──────────────────────────────────────────────┐
                       │          AGENT COMPLETES MODIFICATION        │
                       └───────────────────────┬──────────────────────┘
                                               │
                                               ▼
                                   [ Stop Gate Invocation ]
                                               │
                                               ▼
                               Tier 1: Sovereign Local Test
                             Execute active repo's test runner
                                               │
                               ┌───────────────┴───────────────┐
                               │                               │
                          Exit != 0?                       Exit == 0?
                               │                               │
                               ▼                               ▼
                      [ Reject (continue) ]         Touched Exported APIs?
                      Fix local breakage                       │
                                               ┌───────────────┴───────────────┐
                                               │                               │
                                              YES                              NO
                                               │                               │
                                               ▼                               ▼
                                Tier 2: Federated Contract Gate        [ Allow Exit ]
                                Execute cross_repo_verification         Task Passed
                                               │
                               ┌───────────────┴───────────────┐
                               │                               │
                          Exit != 0?                       Exit == 0?
                               │                               │
                               ▼                               ▼
                      [ Reject (continue) ]             [ Allow Exit ]
                      Fix downstream regression          Task Passed
```

1. **Tier 1 (Sovereign Local Suite)**: The Stop Gate executes the active repository's local MVR test suite. If this fails, the agent is immediately rejected.
2. **Tier 2 (Federated Contract Gate)**: If the agent modified files declared in `exports` (e.g. public interfaces or CLI hooks), the Stop Gate automatically invokes the cross-repo contract test suite defined in `antios.workspace.json`.

---

## 6. Concrete AntiOS Architectural Recommendations

1. **Project Configurations into Every Sovereign Repo (`[MANDATORY]`)**:
   Never rely on parent workspace `AGENTS.md`. The Project Environment Compiler must project `.agents/hooks.json` and `AGENTS.md` into each child repository root.

2. **Fix `gate.py` Multi-Repo Path Resolution (`[MANDATORY]`)**:
   Refactor `gate.py` to determine the target repository based on the paths of modified files in the working tree, rather than naively indexing `workspacePaths[0]`.

3. **Define Public Interface Exports in Workspace Config (`[RECOMMENDED]`)**:
   Require repositories in a multi-repo workspace to declare their exported modules in `antios.workspace.json`, enabling automated blast-radius detection.

4. **Implement Tier 2 Federated Verification (`[RECOMMENDED]`)**:
   Configure the Stop Gate to trigger cross-repo integration suites whenever an agent edits exported interface files.

---

## 7. Classification & Verification Ledger

| Claim / Observation | Classification | Evidence Source |
| :--- | :---: | :--- |
| Upward rule traversal halts at `.git` boundary | `[OFFICIAL]` | Antigravity Platform Specification & Research 3 |
| `gate.py` hardcodes `workspacePaths[0]` | `[OBSERVED]` | Code inspection of `framework/hooks/gate.py` (Line 42) |
| Multi-repo parent files are invisible inside child clones | `[OBSERVED]` | Verified in AntiOS Research 3 empirical trials |
| Stop Gate hook can execute multi-tier verification suites | `[OFFICIAL]` | Antigravity Platform Hook Specification |
| Current AntiOS test suite passes 1086/1086 tests | `[OBSERVED]` | `python tests/run_all.py` test run |
