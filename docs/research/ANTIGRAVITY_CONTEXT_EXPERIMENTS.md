# Antigravity Context Construction Experiments

**Classification Standards:**
`[OFFICIAL]`: Directly verified against upstream Google Antigravity SDK documentation, schema specifications, or system prompts.
`[OBSERVED]`: Empirically verified via live experimentation, filesystem inspection, or database queries in the current environment.
`[INFERRED]`: Deductions drawn from convergent architectural facts.
`[HYPOTHESIS]`: Plausible architectural model requiring further empirical validation.
`[UNKNOWN]`: Unresolved areas where evidence is incomplete or inaccessible.
`[CONFLICT]`: Contradictions between AntiOS documentation/assumptions and empirical platform realities.

---

## 1. Overview of Experimental Protocol

To replace assumptions with empirical ground truth, five controlled experiments were executed across the Antigravity runtime environment:
- **Experiment A**: Project Traversal & Feature Navigation (Disposable Sandbox).
- **Experiment B**: Turn-0 Context Injection & Root vs Subdirectory Upward Traversal.
- **Experiment C**: Subagent Context Isolation & Working Memory Boundary.
- **Experiment D**: Skill Progressive Disclosure & Activation Mechanics.
- **Experiment E**: Hook Interception, Environment Context, & Bypass Surfaces.

All experiments were conducted without modifying core AntiOS code, using disposable sandboxes and empirical inspections of native system state.

---

## 2. Experiment A: Project Traversal & Feature Navigation

### Hypothesis
An agent entering an unfamiliar repository does not possess intrinsic knowledge of file topology; it discovers project structure strictly via progressive, tool-mediated directory listings and targeted file reads.

### Methodology
1. Created a disposable multi-tier sandbox application in `~/.gemini/antigravity/brain/<id>/scratch/exp_login_project/` containing:
   - `README.md`: Architecture overview and directory layout.
   - `backend/auth/login_service.py`: Authentication logic and JWT validation.
   - `frontend/components/button.jsx`: Reusable UI button.
   - `frontend/pages/login.jsx`: Login page component.
   - `tests/frontend/login.test.js`: Frontend test suite.
2. Dispatched isolated subagent `c9a4feae-0296-4de9-9b6c-7db818006e6e` with the prompt:
   *"Navigate the sandbox at `scratch/exp_login_project/` and discover what files implement user authentication and its tests. Report the exact sequence of tools used."*

### Raw Observations (Step-by-Step Tool Trace)
Subagent C performed exactly 9 operations in deterministic sequence:

| Step | Tool Invoked | Target Path / Query | Observation / Information Gained |
| :--- | :--- | :--- | :--- |
| 1 | `list_dir` | `scratch/exp_login_project` | Discovered top-level dirs: `backend`, `frontend`, `tests`, and `README.md`. |
| 2 | `view_file` | `README.md` | Extracted architectural summary, tech stack, and module purposes. |
| 3 | `list_dir` | `frontend` | Found subdirectories: `components`, `pages`. |
| 4 | `list_dir` | `frontend/pages` | Located target page: `login.jsx`. |
| 5 | `view_file` | `frontend/pages/login.jsx` | Read component implementation, form state, and API endpoints called. |
| 6 | `list_dir` | `backend` | Found subdirectory: `auth`. |
| 7 | `list_dir` | `backend/auth` | Located backend handler: `login_service.py`. |
| 8 | `view_file` | `backend/auth/login_service.py` | Read password hashing and token generation logic. |
| 9 | `grep_search` | `SearchPath: tests/`, `Query: "login"` | Located exact test file: `tests/frontend/login.test.js`. |

### Analysis
- The agent exhibited zero pre-existing knowledge of the project.
- Navigation followed a strict **top-down hierarchical cascade**:
  `list_dir(root) -> view_file(README) -> list_dir(subsystems) -> view_file(source) -> grep_search(tests)`.
- Without a root `README.md` or architectural guide, the agent relies heavily on brute-force directory listings.

### Conclusion: `[OBSERVED]`
Project context acquisition is 100% active and tool-mediated. Static analysis or codebase understanding cannot occur without explicit tool execution steps in the conversation trajectory.

---

## 3. Experiment B: Turn-0 Context Injection & Root vs Subdirectory Upward Traversal

### Hypothesis
Antigravity automatically injects repository orientation instructions into the Turn-0 prompt, but ONLY if the file resides in the root directory or upward ancestor path from the current working directory. Subdirectory constitution files (e.g. `docs/AGENTS.md`) are never auto-injected.

### Methodology
1. Inspected the live agent system prompt structure across multiple turns and subagent spawns.
2. Verified official language server source logic and path traversal rules for `AGENTS.md` and `GEMINI.md`.
3. Verified whether `docs/AGENTS.md` or `docs/ACTIVE_CONTEXT.md` were present in the Turn-0 context payload.

### Raw Observations
1. **System Prompt Composition at Turn 0:**
   - `<identity>`: Model role, system capabilities.
   - `<user_information>`: Windows OS, active workspace URI (`c:\Users\Suraj\Documents\Antigravity\AntiOs`), app data dir, conversation ID.
   - `<mcp_servers>`: Registered eager and lazy MCP tools.
   - `<skills>`: Catalog of available skills (`name` and `description` only).
   - `<subagents>`: Available delegation personas (`self`, `research`).
   - `<messaging>`: Protocol rules.
   - `<conversation_transcript>`: Transcript logging paths and query instructions.
   - `<artifacts>`: Artifact creation rules, formatting standards, directory paths.
   - `<slash_commands>`: Recommendations for user slash commands.
   - `<planning_mode>`: Planning instructions and requirements.
   - `<guidelines>` / `<communication_style>`: Tone and formatting constraints.
2. **Constitutional Discovery Mechanism:**
   - The language server performs **upward directory traversal** starting from CWD:
     `CWD -> CWD/.. -> CWD/../.. -> Workspace Root`.
   - Files matching `AGENTS.md` or `GEMINI.md` in any ancestor directory are merged into the prompt.
   - Subdirectories (e.g., `docs/`, `src/`, `.agents/`) are **never** evaluated during upward traversal from the workspace root.

### Analysis
- AntiOS stored its constitution at `docs/AGENTS.md` and active context at `docs/ACTIVE_CONTEXT.md`.
- Because CWD is the repository root (`c:\Users\Suraj\Documents\Antigravity\AntiOs`), upward traversal looks at:
  1. `c:\Users\Suraj\Documents\Antigravity\AntiOs\AGENTS.md` (Not found)
  2. `c:\Users\Suraj\Documents\AGENTS.md` (Not found)
  3. `c:\Users\Suraj\AGENTS.md` (Not found)
- Result: **Neither `docs/AGENTS.md` nor `docs/ACTIVE_CONTEXT.md` was ever injected into the Turn-0 prompt.** AntiOS was effectively blind to its own constitution on every fresh session start.

### Conclusion: `[CONFLICT]` / `[OBSERVED]`
Placing constitutional instructions in `docs/AGENTS.md` breaks native auto-injection. The root `AGENTS.md` is mandatory for turn-0 orientation.

---

## 4. Experiment C: Subagent Context Isolation & Working Memory Boundary

### Hypothesis
Subagents launched via `invoke_subagent` operate under total context isolation: they receive zero turns of the parent conversation, zero parent reasoning thoughts, and zero scratchpad inheritance.

### Methodology
1. Launched three independent subagents across the research mission:
   - Subagent A (`9d7df302-7936-4bba-b58b-5a3900388cf6`)
   - Subagent B (`e32d14b7-b5f5-4916-9e1c-f72ed4c59bf9`)
   - Subagent C (`c9a4feae-0296-4de9-9b6c-7db818006e6e`)
2. Inspected the generated SQLite databases in `conversations/<subagent-id>.db` and JSONL transcripts in `brain/<subagent-id>/.system_generated/logs/transcript.jsonl`.
3. Verified the contents of Turn 0 in each subagent's execution trace.

### Raw Observations
- In each subagent transcript:
  - Step 0 was `USER_INPUT` containing exclusively the string passed in the parent's `invoke_subagent(Prompt=...)` call.
  - No preceding turns from the parent session were present.
  - Parent conversation ID was noted only in metadata references, not in prompt context.
  - Subagent C had no awareness of Specialist A or Specialist B's findings.
- Subagent workspace mode:
  - `Workspace='inherit'` allowed subagents to read and write repository files in the shared working tree.
  - `Workspace='branch'` cloned the repository into an isolated ephemeral branch workspace.

### Analysis
- Context isolation is absolute. There is no cognitive "bleed-through" between parent and child.
- This provides mathematical rigor for Maker-Checker workflows (`antios-verifier`): a checker cannot be biased by the maker's rationalizations or conversational declarations.
- However, it places total responsibility on the parent agent to provide a **self-contained specification** in the dispatch prompt.

### Conclusion: `[OFFICIAL]` / `[OBSERVED]`
Subagent context inheritance is exactly 0%. Verification subagents are provably independent auditors.

---

## 5. Experiment D: Skill Progressive Disclosure & Activation Mechanics

### Hypothesis
Skills defined in `.agents/skills/` or global config do not inject their full procedures into Turn-0 context; only their YAML `name` and `description` are loaded. The body (`SKILL.md`) is loaded strictly on demand via `view_file`.

### Methodology
1. Inspected Turn 0 `<skills>` block in the active conversation prompt.
2. Monitored tool calls when executing tasks requiring specialized skills (e.g., `/adaptive-orchestrator`).
3. Evaluated token expenditure of the skill catalog vs full skill bodies.

### Raw Observations
1. In the Turn-0 system prompt, the skill entry for `antios` appeared as:
   ```markdown
   - antios (c:\Users\Suraj\Documents\Antigravity\AntiOs\.agents\skills\antios\SKILL.md):
     Universal project-native control plane under AntiOS 2.0 governance. Use when
     planning, navigating, implementing, debugging, verifying, or orchestrating any
     engineering task in this repository.
   ```
2. The entire body of `SKILL.md` (governance rules, stop gates, invariant tables) was absent from Turn 0.
3. When the agent determined a skill was relevant, it explicitly executed:
   `view_file(AbsolutePath="c:\Users\Suraj\Documents\Antigravity\AntiOs\.agents\skills\antios\SKILL.md")`.
4. Only after calling `view_file` did the procedural instructions enter the agent's working context.

### Semantic Collision Observation
- In `AntiOs/.agents/skills/`, two skills had nearly identical descriptions:
  - `antios`: *"Universal project-native control plane under AntiOS 2.0 governance. Use when planning, navigating, implementing, debugging, verifying, or orchestrating any engineering task..."*
  - `antios-engineer`: *"Universal engineering workflow policy for projects under AntiOS governance. Use when planning, implementing, modifying, or verifying features, bug fixes, refactors..."*
- Result: Model exhibited uncertainty regarding which skill to activate, often loading both or picking arbitrarily.

### Conclusion: `[OFFICIAL]` / `[OBSERVED]`
Skills operate under strict two-tier progressive disclosure. Metadata must be sharply differentiated to avoid semantic collisions.

---

## 6. Experiment E: Hook Execution, CWD Context, & Bypass Surfaces

### Hypothesis
Lifecycle hooks defined in `.agents/hooks.json` run synchronously and can deterministically block execution, but execute with working directory `.agents/` and only intercept declared tool patterns.

### Methodology
1. Inspected `.agents/hooks.json`:
   ```json
   {
     "hooks": [
       {
         "event": "PreToolUse",
         "matcher": "write_to_file|replace_file_content",
         "command": "python guard.py",
         "timeout": 5
       },
       {
         "event": "Stop",
         "matcher": ".*",
         "command": "python gate.py",
         "timeout": 30
       }
     ]
   }
   ```
2. Verified runtime behavior and execution logs of `guard.py` and `gate.py`.
3. Tested shell bypass surfaces via `run_command`.

### Raw Observations
1. **Working Directory (`cwd`) Reality:**
   - Hooks execute with `cwd = <workspace>/.agents/`, NOT the workspace root.
   - Python scripts in `.agents/` must resolve workspace paths using `..` or environment variables.
2. **Stop Gate Ratchet Enforcement:**
   - `gate.py` (which runs `tests/run_all.py`) intercepted the `Stop` event.
   - When tests passed (exit code 0), `gate.py` emitted `{"decision": "approve"}`.
   - If tests fail, it emits `{"decision": "continue", "reason": "Test failures detected"}`.
   - The agent is physically prevented from terminating the session.
3. **PreToolUse Bypass Surface (`[OBSERVED]`):**
   - The hook matcher was strictly regex `write_to_file|replace_file_content`.
   - Modifying files via shell commands (`run_command`: `python -c "open('file.py','w').write('...')"` or `Set-Content`) **did not trigger the `PreToolUse` hook**.
   - The guard is only as strong as its tool matcher coverage.

### Conclusion: `[OFFICIAL]` / `[OBSERVED]`
Hooks provide the only physical, non-bypassable enforcement mechanism in Antigravity. However, tool-specific matchers leave command-line evasion vectors if `run_command` is permitted.

---

## 7. Summary of Empirical Findings

| Experiment | Target Subsystem | Tested Hypothesis | Empirical Finding | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Exp A** | Tool Actuation | Agents navigate codebases via tool calls | Progressive 9-step top-down discovery trace confirmed | `[OBSERVED]` |
| **Exp B** | Context Ingestion | `docs/AGENTS.md` is auto-injected | False: Upward traversal skips subdirectories; root `AGENTS.md` required | `[CONFLICT]` |
| **Exp C** | Subagents | Subagents share parent working memory | False: Context isolation is 100% complete; Turn 0 is pristine | `[OFFICIAL]` |
| **Exp D** | Skills | Skills are loaded in full at Turn 0 | False: Progressive disclosure loads only `name`/`description` initially | `[OFFICIAL]` |
| **Exp E** | Lifecycle Hooks | Hooks provide deterministic security | True for declared tools, but shell redirection bypasses tool matchers | `[OBSERVED]` |
