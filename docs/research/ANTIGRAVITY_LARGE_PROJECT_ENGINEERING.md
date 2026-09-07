# Engineering on Large Repositories in Google Antigravity
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: Applied Engineering & Architectural Gap Analysis  
**Target Scenario**: Monorepos & Large Codebases (100,000+ Lines of Code)  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. The Large Software Project Challenge

In an enterprise or polyglot repository spanning hundreds of thousands of lines of code (e.g. monorepos combining Rust native engines, Python services, PyQt desktops, and Svelte/TypeScript frontends), a human developer says:

> **"Fix the bug where clicking the 'Export' button in the study dashboard fails with a network timeout."**

For a software engineering agent, this simple prompt presents a severe navigational challenge:
- Where is the study dashboard? (`ts/src/`, `apps/desktop/`, `packages/web/`?)
- Which button component triggers the export?
- What API endpoint or local IPC bridge does it call?
- What architectural constraints protect the database or native core from corruption?
- What test command exercises this specific button without running 40 minutes of unrelated end-to-end suites?
- What decisions were made last week regarding export timeouts?

Without an engineering operating layer, an agent either drowns in context by attempting brute-force exploration or wanders aimlessly across unrelated subsystems.

---

## 2. The Ideal Engineering Trajectory

To solve this task safely and efficiently without scanning the entire repository, the agent must execute a disciplined 10-step trajectory:

```
[1. Task Ingestion]
       │
[2. Feature Localization]
       │
[3. Subsystem Identification]
       │
[4. File Set Isolation]
       │
[5. Architectural Constraint Lookup]
       │
[6. Relevant Documentation Inspection]
       │
[7. Targeted Verification Discovery]
       │
[8. Invariant Affirmation]
       │
[9. Controlled Code Modification]
       │
[10. Physical Multi-Tier Verification]
```

Below is the forensic examination of each step:

### Step 1: Task Ingestion
- **Goal**: Parse user intent, extract key semantic anchors (`Export button`, `study dashboard`, `network timeout`).
- **Ideal Behavior**: Anchor the task to known project capabilities without jumping to assumptions.

### Step 2: Feature Localization
- **Goal**: Map "study dashboard" to the frontend user interface package.
- **Ideal Behavior**: Resolve the feature name directly to `packages/frontend/src/dashboard/` in 0 tool calls using a structured project manifest.

### Step 3: Subsystem Identification
- **Goal**: Determine the boundary of the frontend dashboard and its dependencies.
- **Ideal Behavior**: Recognize that the dashboard is a TypeScript/Svelte component communicating over an IPC bridge to an internal Rust core (`rslib/`).

### Step 4: File Set Isolation
- **Goal**: Pinpoint the exact files: `ExportButton.svelte` and `exportClient.ts`.
- **Ideal Behavior**: Targeted symbol search (`grep_search` restricted to the dashboard directory), reading only lines 40–90 of the component.

### Step 5: Architectural Constraint Lookup
- **Goal**: Check what rules govern this subsystem.
- **Ideal Behavior**: Mount directory rules (`AGENTS.md` in `packages/frontend/`) establishing that frontend components must never mutate database state directly and must route all requests through `exportClient.ts`.

### Step 6: Relevant Documentation Inspection
- **Goal**: Read API contracts or timeouts.
- **Ideal Behavior**: Ingest only the specific reference file (`docs/api/export_contract.md`) via progressive disclosure, avoiding unrelated architecture documents.

### Step 7: Targeted Verification Discovery
- **Goal**: Locate the exact test suite exercising the export button.
- **Ideal Behavior**: Identify `npm run test:dashboard` or `vitest packages/frontend/src/dashboard/ExportButton.test.ts`, rather than executing the entire monorepo test suite.

### Step 8: Invariant Affirmation
- **Goal**: Verify that fixing the timeout does not violate upstream core immutability or introduce security risks.
- **Ideal Behavior**: Confirm that changes remain confined to the frontend client without modifying `rslib/` or framework files.

### Step 9: Controlled Code Modification
- **Goal**: Apply minimal, surgical diff increasing timeout threshold and adding proper retry backoff.
- **Ideal Behavior**: Single contiguous replacement using `replace_file_content` in `exportClient.ts`.

### Step 10: Physical Multi-Tier Verification
- **Goal**: Prove that the fix works and caused no regressions.
- **Ideal Behavior**: Run the targeted component test, verify exit code 0, confirm clean `git status`, and allow the Stop Gate to validate the changeset.

---

## 3. What Antigravity Already Provides Natively

Antigravity provides powerful low-level primitives:
1. **High-Performance Ripgrep (`grep_search`)**: `[FACT]` Searches millions of lines in milliseconds; supports glob filtering (`Includes: ["*.svelte"]`).
2. **Directory Slicing (`list_dir`, `find_by_name`)**: `[FACT]` Allows fast directory tree discovery.
3. **Targeted Line Viewing (`view_file`)**: `[FACT]` Restricts file reading to specific line ranges (`StartLine`, `EndLine`), preventing token waste.
4. **Directory-Scoped Rules (`AGENTS.md`)**: `[FACT]` Automatically mounts local guidelines when working inside a directory.
5. **Planning Mode**: `[FACT]` Encourages drafting an `implementation_plan.md` before coding.
6. **Tool-Level Gating (`hooks.json`)**: `[FACT]` `PreToolUse` can intercept and reject invalid file modifications.

---

## 4. What is Missing: The Large-Project Architectural Gap

Despite these powerful primitives, native Antigravity lacks the higher-level engineering operating substrate required for complex codebases:

| Engineering Dimension | Native Antigravity State | Impact on Large Codebases | Architectural Solution Required |
| :--- | :--- | :--- | :--- |
| **1. Wayfinding & Project Maps** | **MISSING**. No machine-readable index of subsystems, packages, or entrypoints. | Agent performs brute-force directory walks and random grep searches, wasting 5–10 turns. | **Declarative Project Adapter (`antios.config.json`)**: Explicit map of subsystems, directories, and manifests. |
| **2. Subsystem Boundaries** | **MISSING**. Platform treats all workspace files identically. | Agent attempts to modify upstream core files (`rslib/`, submodules) to fix high-level UI bugs. | **Deterministic Boundary Guard (`pre_tool_guard.py`)**: Fail-closed physical blocks on protected zones. |
| **3. Blast Radius & Dependency Understanding** | **MISSING**. Platform has no dependency graph awareness across monorepo members. | Agent modifies shared interfaces without knowing which other packages break. | **Monorepo Member Mapping**: Declared dependency graph in project anatomy. |
| **4. Verification Discovery** | **MISSING**. Agent must guess test commands or run slow root scripts. | Agent runs nothing, runs full 1-hour test suites, or hallucinates test success. | **Runner Registry**: Pre-configured mapping connecting subsystems to exact test commands. |
| **5. Progressive Project Knowledge** | **MISSING**. Project docs are either dumped in full or ignored. | Context bloat or complete ignorance of design rationale. | **Progressive Knowledge Tiers**: Skills with concise `SKILL.md` runbooks linking to targeted references. |
| **6. Historical Decisions & Dead-Ends** | **MISSING**. Trajectory history is lost across conversations. | Agent repeats previously attempted, failed implementation strategies. | **Append-Only Dead-End Memory (`dead-ends.md`)**: Persistent record of falsified hypotheses. |
| **7. Cross-Session Continuity** | **MISSING**. Fresh sessions start with 100% amnesia. | Tomorrow's agent has no context on what was changed or why. | **5-Part Handoff Contract (`handoff.md`)**: Checked into repo root for zero-turn state recovery. |

---

## 5. Architectural Assessment: Can Antigravity Alone Solve This?

`[Strong Inference]` **No.** Antigravity is a foundation platform and tool runtime. It cannot know the idiosyncratic architectural boundaries, member relationships, or test suites of every proprietary project in advance.

Attempting to solve this inside Antigravity Core by training foundation models to "guess" project structures leads to brittle heuristics and hallucination.

The correct architectural solution is a **Project-Native Operating Layer**: a lightweight set of declarative manifests, deterministic hooks, and progressive skills checked into the repository itself. This is the exact role that AntiOS is designed to fulfill.
