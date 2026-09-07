# AntiOS Forensic Failure Analysis & Codebase Audit
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: High-Confidence Forensic Audit & Post-Mortem  
**Case Study**: Empirical Adaptation of the `Anki-maths` Monorepo  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. Executive Summary

This forensic audit investigates the architecture of AntiOS 2.0/2.1 and diagnoses the empirical failure observed during the real-world adaptation of the **Anki-maths** repository.

### Key Forensic Findings:
1. **The Paradox of the Experience Store**: In the central data store (`experience.db`), the `projects` table contains an authoritative project registration row (`proj_ad9a1400eac88aee`), but the tables `sessions`, `missions`, `turns`, `tool_calls`, and `engineering_events` contain **exactly zero rows**.
2. **The Architectural Contradiction**: AntiOS enacted two mutually incompatible architectural mandates:
   - **Mandate A (`RuntimeClosureContract` / System A/B Firewall)**: Installed target instances must be 100% self-contained standard-library scripts in `.antios/runtime/` with **zero imports from AntiOS `framework/`**. Furthermore, Rule 2 of the System A/B Firewall (`docs/architecture/experience/SYSTEM_A_B_SEPARATION.md`) strictly forbade runtime templates from importing `telemetry_bridge.py` or `experience.py`, enforced by AST unit tests.
   - **Mandate B (Phase 105 Continuous Telemetry Pipeline)**: Telemetry was designed to be captured without background daemons (`INV-15`), relying entirely on lifecycle hooks (`Stop` and `PostToolUse`) invoking `framework.core.telemetry_bridge.AntigravityEventBridge`.
3. **The Fatal Severance**: Because the instance runtime scripts complied with Mandate A, all telemetry code was stripped from the target instance. No telemetry hook was installed in `.agents/hooks.json`. No background daemon existed (`INV-15`). Consequently, **no running process ever invoked `AntigravityEventBridge`** during agent execution in `Anki-maths`.
4. **Platform Reality vs AntiOS Illusion**: While Google Antigravity *does* possess a native lifecycle hook execution engine, 80% of AntiOS's 84 framework modules existed solely as dead code on disk, completely uncoupled from the live Antigravity execution loop. AntiOS behaved as "many useful files beside the agent" rather than a system embedded into the agent's actual lifecycle.

---

## 2. Comprehensive AntiOS Capability Audit Table

| Existing AntiOS Capability | Intended Purpose | Actual Integration Point | Native Antigravity Mechanism Used? | Likely Value | Suspected Problem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PreToolUse Boundary Guard** (`pre_tool_guard.py`) | Deterministically intercept and block unauthorized file writes (e.g. `.agents/`, `.antios/`, `framework/`, `antios.config.json`, path traversal, 8.3 aliases). | `.agents/hooks.json` under `"PreToolUse"` matcher `write_to_file\|replace_file_content` executing `python .antios/runtime/pre_tool_guard.py`. | **YES (Native Platform Hook)**. Matches Antigravity's `PreToolUse` hook engine via stdio JSON. | **HIGH**: Successfully prevented IDE file-modification tools from corrupting configuration or writing outside workspace. | **Shell Bypass Vulnerability**: Only intercepts `write_to_file` and `replace_file_content`. Completely blind to shell mutations via `run_command` (PowerShell/cmd/bash). |
| **Stop Gate Verification Engine** (`stop_gate.py`) | Prevent agent task completion if physical tests fail (`cargo test`, `pytest`) or unresolved merge conflicts exist (`INV-04`). | `.agents/hooks.json` under `"Stop"` executing `python .antios/runtime/stop_gate.py`. | **YES (Native Platform Hook)**. Returns `{"decision": "continue", "reason": "..."}` on test failure to force agent to continue. | **CRITICAL**: Enforces exit code 0 on real test runners before task handoff. | **Zero Telemetry Hooked**: Telemetry ingestion was never wired into the instance script; test timeouts block agent loop synchronously. |
| **Master Declarative Adapter** (`antios.config.json`) | Central configuration declaring protected zones, active test runners, linters, and changeset policies. | Read by runtime scripts (`pre_tool_guard.py`, `stop_gate.py`) and AntiOS CLI. | **NO**. Passive JSON configuration on local disk; Antigravity platform core is unaware of it. | **HIGH**: Provides deterministic runner discovery for the Stop Gate. | **No Native Platform Binding**: If an agent doesn't run the hooks or CLI, this config is inert. |
| **Constitutional Prompt Contract** (`AGENTS.md`) | Govern agent behavior, mandate 8-stage lifecycle, wayfinding, shallow depth, and Maker-Checker audits. | Root workspace file mounted into `<user_rules>` in the system prompt. | **YES (Native Rules Mounting)**. Antigravity natively loads root `AGENTS.md` and `CLAUDE.md`. | **HIGH**: Shapes model reasoning and operational discipline. | **Advisory Only**: LLMs can hallucinate past markdown guidance unless backed by physical deterministic hooks. |
| **Instance Wayfinding Engine** (`inspect_instance.py`) | Resolve codebase subsystems and tests from semantic keywords/intent queries without sprawling file reads. | Run manually via CLI: `python .antios/runtime/inspect_instance.py --query "..."`. | **NO**. Relies on agent proactively calling `run_command`. Antigravity has no native wayfinding hook. | **MEDIUM**: Useful search heuristic for large monorepos if agent chooses to call it. | **Advisory & Voluntary**: Agents frequently bypass it and use native `view_file` or `grep_search` directly. |
| **Project Intelligence Metadata** (`.antios/*.json`) | Bounded epistemic models of project anatomy, profile, agent topology, tool policies, knowledge, and learning proposals. | Files written to `.antios/` directory on disk. | **NO**. Zero native platform integration. | **LOW (in current state)**: Stagnant JSON snapshots generated during `adapt`. | **Merely Existed on Disk**: Antigravity never reads these files. Without runtime active query integration, they are dead data. |
| **Runtime Closure Contract** (`verify_runtime.py`) | Ensure target instance runtime is 100% self-contained standard library with zero imports from AntiOS source. | Standalone verification script executing AST inspection over `.antios/runtime/*.py`. | **NO**. Developer-facing verification utility. | **HIGH (Architectural Soundness)**: Successfully prevented target projects from breaking due to missing framework imports. | **Created Telemetry Dead-End**: By prohibiting imports from `framework/`, it severed the target instance from `telemetry_bridge.py`. |
| **Telemetry & Event Bridge** (`telemetry_bridge.py`) | Non-blocking capture of platform transcripts (`transcript.jsonl`) and hook events into `experience.db`. | Intended to be invoked by lifecycle hooks during natural turn interactions (`INV-15`). | **FAILED TO INTEGRATE**. Native hooks exist, but target instance hooks did not call this module. | **ZERO (in practice)**: Never executed outside of unit tests in the core repo. | **Fatal Architectural Disconnect**: Never installed in target instances; collection mode defaults to `OFF`; no process ever invoked it. |
| **Privacy Sanitizer Engine** (`sanitizer.py`) | Fail-closed scrubbing of API keys, tokens, PII, paths, and raw chain-of-thought before persistence. | Sits between `telemetry_bridge.py` and `experience.py`. | **NO**. Internal library module. | **HIGH (Design Quality)**: Rigorous regex and entropy filters; passes all 12 unit tests. | **Unreachable in Target Projects**: Sits idle because `telemetry_bridge.py` is never invoked in target projects. |
| **Central Experience Store** (`experience.db`) | Central WAL-mode SQLite database tracking cross-project sessions, missions, tool friction, and engineering telemetry. | Located at `<central_data>/experience.db` (`Os-Collection`). | **PARTIALLY CONNECTED**. Connected during `antios install` / `antios adapt` CLI execution only. | **VERY LOW (1 Row)**: Successfully registered project metadata, but received 0 operational telemetry rows. | **Completely Dark at Runtime**: No active runtime process writes to it during agent sessions. |
| **Project-Level Skills** (`.agents/skills/*`) | Operational runbooks for orchestration (`antios`), adaptation (`antios-adapt-project`), debugging, engineering, verification. | `.agents/skills/` directory in target workspace root. | **YES (Native Skill System)**. Antigravity discovers and registers skills in `.agents/skills/`. | **HIGH**: Available in model tool schema for explicit activation. | **Passive Tooling**: The agent must choose to activate the skill; it does not automatically enforce execution steps. |
| **Subagent Workforce Governance** (`agent_topology.json` / `INV-06-08`) | Enforce shallow depth ($\le 2$), concurrency ceiling ($\le 4$), launch budget ($\le 10$), and wave collapse. | Declared in `.antios/agent_topology.json` and documented in `AGENTS.md`. | **NO (Native Enforcement Absent)**. Antigravity's `invoke_subagent` has no built-in depth/concurrency throttling hook. | **MEDIUM**: Enforced only when parent agent self-regulates or runs `antios` skill. | **Advisory Unless Governed**: If a raw agent executes `invoke_subagent` without the skill, Antigravity does not restrict depth. |

---

## 3. The 10 Case Study Diagnostic Questions for `Anki-maths`

### 1. What actually worked?
- `[FACT]` **Project Adaptation (`antios adapt`)**: Successfully crawled `Anki-maths`, discovered 14 monorepo subsystems across Rust, Python, and TypeScript, identified documentation drift against physical build manifests (Cargo, yarn, uv), and synthesized `antios.config.json` (1,096 lines).
- `[FACT]` **Project Registration**: Successfully connected to `Os-Collection/experience.db` and registered `proj_ad9a1400eac88aee`.
- `[FACT]` **Stop Gate Verification**: When triggered on `Stop`, `stop_gate.py` executed `cargo test -p procedural --lib`, verified 146 tests passed in 0.10s, and confirmed 0 git conflict markers.
- `[FACT]` **Boundary Guard**: Intercepted unauthorized IDE writes to protected areas.

### 2. What merely existed on disk?
- `[FACT]` The entire set of `.antios/*.json` metadata files (68 KB `project_profile.json`, 41 KB `project_anatomy.json`, 24 KB `knowledge.json`, etc.). Antigravity never parsed or referenced these files.
- `[FACT]` The 84 modules in AntiOS `framework/core/` (drift health, release certification, benchmark simulator, etc.). Target agents never imported them.
- `[FACT]` `inspect_instance.py` existed on disk but was never automatically queried.

### 3. What was actually connected to Antigravity?
- `[FACT]` **`AGENTS.md`**: Read natively into the system prompt.
- `[FACT]` **`PreToolUse` Hook**: Executed by Language Server before `write_to_file` and `replace_file_content`.
- `[FACT]` **`Stop` Hook**: Executed by Language Server when the agent attempted to conclude.
- `[FACT]` **Project Skills**: Discovered in `.agents/skills/` and exposed in `<skills>`.

### 4. What was advisory?
- `[FACT]` `AGENTS.md` prompt rules. The agent could violate them unless intercepted by a hook.
- `[FACT]` Subagent depth and budget limits. Antigravity's native `invoke_subagent` tool does not enforce AntiOS topology limits unless the model voluntarily obeys.
- `[FACT]` Wayfinding commands (`inspect_instance.py`).

### 5. What was enforced?
- `[FACT]` File mutation blocks on protected paths (`pre_tool_guard.py`).
- `[FACT]` Test pass requirements and conflict marker bans upon task conclusion (`stop_gate.py`).

### 6. What was observable?
- `[FACT]` Antigravity's native `transcript.jsonl` was streaming in the user AppData directory, but AntiOS never observed it.
- `[FACT]` Only the exit codes of hook scripts were observed by Antigravity.

### 7. What was persistent?
- `[FACT]` Git repository state and committed configuration files.
- `[FACT]` Project registration row in `experience.db`.

### 8. What participated in normal agent execution?
- `[FACT]` System prompt rules (`AGENTS.md`), pre-tool guard execution, and stop gate verification.

### 9. What did NOT participate in normal agent execution?
- `[FACT]` Telemetry bridge, privacy sanitizer, experience repository, `.antios/*.json` models, and the 84 framework core modules.

### 10. What architectural assumption caused the gap?
- `[HYPOTHESIS]` **The Illusion of Shared Runtime**: The designers assumed that because `telemetry_bridge.py` existed in the AntiOS repository, it would magically execute in the target project. They failed to account for the physical deployment boundary: target repositories are isolated environments where framework dependencies do not exist.

---

## 4. Root Architectural Causes of the Telemetry Blackout

The failure to capture ongoing telemetry was caused by **five compound design defects**:

### 1. The Code Import Firewall Contradiction
To ensure target projects were portable, AntiOS enacted `RuntimeClosureContract` (Decision Phase 80/81) and Rule 2 of the System A/B Firewall (`SYSTEM_A_B_SEPARATION.md`), mandating that `.antios/runtime/` scripts have zero imports from `framework/`. This rule was enforced by AST unit tests. However, the telemetry pipeline was implemented inside `framework/core/telemetry_bridge.py`. Consequently, runtime templates in `.antios/runtime/` could not import the telemetry bridge without failing AST verification. The compiler solved this by stripping telemetry code from instance templates, permanently severing the instance from the telemetry store.

### 2. Missing `PostToolUse` Hook Registration
In `Anki-maths/.agents/hooks.json`, only `PreToolUse` and `Stop` were registered. There was no `PostToolUse` hook. In Antigravity, tool completion telemetry is delivered via `PostToolUse`. Because `PostToolUse` was absent, the platform never invoked any hook after tool executions.

### 3. The Fail-Closed Default Configuration (`OFF`)
`TelemetryConfigResolver` defaults to `OFF`. In `Anki-maths/antios.config.json`, the `"telemetry"` configuration key was omitted. No environment variables (`ANTIOS_TELEMETRY_MODE=ON`) were set. Even if the bridge had been invoked, it would have returned immediately without ingesting data.

### 4. Hook Working Directory Reality
Official documentation (`hooks.md:L126`) reveals that Antigravity executes hooks with `cwd = .agents/`, NOT the repository root. AntiOS source scripts initially relied on relative paths like `framework/scripts/hooks/pre_tool_guard.py`. In target projects, this required creating symlink/junction hacks (`.agents/.antios -> ../.antios`) to resolve paths.

### 5. Shell Mutation Bypass (`run_command`)
`PreToolUse` matcher was configured as:
`"matcher": "write_to_file|replace_file_content"`
The agent performed dozens of filesystem modifications, builds, and test runs using `run_command` (PowerShell/cmd). These shell commands completely bypassed the `PreToolUse` guard, leaving AntiOS blind to shell mutations.

---

## 5. Architectural Verdict: Embedded Layer vs "Files Beside the Agent"

`[Strong Inference]` **AntiOS currently behaves as "many useful files beside the agent", NOT an embedded operating layer.**

Except for `pre_tool_guard.py` and `stop_gate.py`, the rest of AntiOS (90% of its code and data) sits completely idle on disk during agent tasks. For AntiOS to become a genuine project operating layer, it must abandon dead weight and attach directly to the native Antigravity lifecycle surfaces that actually execute.
