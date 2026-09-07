# AntiOS Architecture Migration Matrix

**Document**: `docs/architecture/MIGRATION_MATRIX.md`  
**Status**: `CANONICAL` (Phase 109 Architecture Review)  
**Version**: 2.1.0-GA  
**Role**: Migration Matrix & Runtime Audit Specification  
**Parent Specifications**:
- [`docs/architecture/OVERVIEW.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/OVERVIEW.md)
- [`docs/architecture/REJECTED_ARCHITECTURE.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/REJECTED_ARCHITECTURE.md)
- [`docs/architecture/antigravity/BOUNDARIES.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/antigravity/BOUNDARIES.md)
- [`docs/architecture/antigravity/LIFECYCLE.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/antigravity/LIFECYCLE.md)
- [`docs/architecture/ambient/BOOTSTRAP.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/BOOTSTRAP.md)
- [`docs/architecture/ambient/COMPILER.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/COMPILER.md)
- [`docs/architecture/experience/SYSTEM_A_B_SEPARATION.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/experience/SYSTEM_A_B_SEPARATION.md)

---

## 1. Executive Summary & Transition Philosophy

AntiOS is undergoing an architectural evolution from an explicit, ceremony-heavy framework (Prototype v0.1 / AntiOS v1) into the **Ambient Project OS (AntiOS 2.1)**. 

### The Core Architectural Shift
In earlier prototype iterations, AntiOS experimented with monolithic in-process state machines, custom background daemons, vector embeddings, multi-tier agent swarms, and bespoke execution journals. Systematic empirical research and adversarial proving ground campaigns (Phases 6–108) proved that these patterns introduced high latency, prompt bloat, fragile state loss across resets, and duplicate capabilities natively provided by the Google Antigravity platform.

The **Ambient Project OS** architecture establishes seven non-negotiable architectural axioms:
1. **Platform Sovereignty (`INV-01`)**: If Google Antigravity natively provides an orchestration, execution, scheduling, or logging primitive $\to$ **USE THE PLATFORM**. AntiOS never wraps or competes with platform capabilities.
2. **Four-Boundary Demarcation (`INV-10`)**: $\text{SOURCE} \ne \text{INSTANCE} \ne \text{PROJECT} \ne \text{ANTIGRAVITY}$. Target repositories receive standalone, compiled runtime scripts (`.antios/runtime/`) with zero dependency on the upstream source repository.
3. **Runtime Closure**: Runtime scripts generated into target instances must have zero imports from `framework.core` and zero third-party dependencies, executing exclusively on Python standard library modules.
4. **Zero-Ceremony Ambient Operation**: AI agents work normally without mandatory slash commands (`/antios`). Context orientation is bounded: [`docs/AGENTS.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/AGENTS.md) is strictly $\le 40$ lines (< 250 tokens), and [`docs/ACTIVE_CONTEXT.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/ACTIVE_CONTEXT.md) is strictly $\le 60$ lines (< 400 tokens).
5. **Toolchain Ground Truth (`INV-04`)**: Verification is enforced through the project's native physical test process exit code (`0`), eliminating synthetic test fallbacks or unverified conversational claims.
6. **Epistemic & Operational Firewall (System A vs System B)**: Project memory (System A) is local, git-versioned, and evidence-grounded. Cross-project telemetry (System B) is external, statistical, sanitized, and stored in `<central_data>/experience.db`. Zero telemetry database files may exist in project repositories.
7. **Zero Background Daemons (`INV-15`)**: All execution is strictly synchronous and event-driven, triggered by platform lifecycle hooks (`PreToolUse`, `Stop`) or explicit CLI commands. No background watchers or daemon threads are permitted.

### Classification Taxonomy
Every component and subsystem in this matrix is classified into strictly one of six states:

| Classification | Definition |
| :--- | :--- |
| **KEEP** | Architecturally sound, verified by empirical evidence, actively aligns with Ambient Project OS axioms. Maintained without structural redesign. |
| **REWORK** | High-value subsystem requiring refactoring, decoupling, or closure hardening to satisfy Ambient Project OS invariants (e.g. eliminating framework imports, bounding line counts). |
| **REPLACE** | Architectural purpose remains vital, but existing implementation is flawed or superseded by a superior platform primitive or file-backed mechanism. |
| **DEPRECATE** | Legacy component preserved temporarily for backward compatibility; replaced by modern unified interfaces. Scheduled for removal in v2.2. |
| **REMOVE** | Anti-pattern, speculative design, or disproved concept formally evaluated and permanently excised per [`REJECTED_ARCHITECTURE.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/REJECTED_ARCHITECTURE.md). Must never be reintroduced. |
| **UNKNOWN** | Insufficient empirical data or pending proving ground validation. No production subsystem may remain in this state upon baseline freeze. |

---

## 2. Master Migration Matrix

The following table classifies every primary subsystem, runtime component, governance mechanism, and storage artifact of AntiOS.

| Existing Component | Current Purpose | Research Finding | Classification | Future Role | Action |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Stop Gate Verification** (`stop_gate.py`) | Intercepts agent `Stop` event; executes conflict checks, discovers project test runners, executes tests via subprocess, ratchets exit code 0. | Phase 9/10 audit proved `verify_task.py` fallback permitted test forgery (`sys.exit(0)`). Phase 80/81 verified standalone stdlib runtime closure (`.antios/runtime/stop_gate.py`) eliminates upstream framework imports, running in <30s. | **REWORK** | Tier-3 compiled runtime closure hook (`.antios/runtime/stop_gate.py`); invoked synchronously on `Stop` platform event. | Migrate target instances from source-dependent script (`framework/scripts/hooks/stop_gate.py`) to standalone compiled runtime closure (`.antios/runtime/stop_gate.py`) via `compiler.py`; ensure fail-closed exit codes (1 on failure, 2 on runtime error). |
| **PreToolUse Boundary Guard** (`pre_tool_guard.py`) | Synchronously inspects file-modifying tools (`write_to_file`, `replace_file_content`); enforces workspace containment, canonicalizes paths, protects immutable zones. | Phase 12–18 adversarial testing proved string prefix matching without `realpath` allowed path traversal (`../`) and 8.3 alias bypasses (`PROGRA~1`). Hardened with `os.path.realpath`, case normalization, and fail-closed JSON validation. Runs in <10ms with zero framework dependencies. | **KEEP** | Tier-3 compiled runtime closure security hook (`.antios/runtime/pre_tool_guard.py`); synchronous boundary protection. | Maintain hardened zero-dependency implementation; ensure compiler deploys template to `.antios/runtime/pre_tool_guard.py` and registers in `.agents/hooks.json`. |
| **Governor & Workforce Contracts** (`workforce_contract.py`, `context_budget.py`) | Enforces multi-agent workforce laws (Shallow Depth $\le 2$, Concurrency $\le 4$, Launch Budget $\le 10$) and in-process context token budgeting. | Phase 6/7 swarm experiments proved large agent swarms (>3 agents) induce >120s coordination latency, context fragmentation, and runaway token bills. Phase 83–86 ratified shallow Maker-Checker wave orchestration. In-process token counters (`context_budget.py`) proved ephemeral across turn resets. | **REWORK** | Declarative policy engine (`framework/core/workforce_contract.py`) and constitutional sizing rules; delegates scheduling and thread lifecycle to Antigravity primitives (`invoke_subagent`, `manage_subagents`). | Retain `workforce_contract.py` as pure policy/validation module; deprecate in-memory token counter in `context_budget.py` in favor of declarative prompt bounds (`AGENTS.md` $\le 40$ lines, `ACTIVE_CONTEXT.md` $\le 60$ lines). |
| **Verification Engine** (`project_proof.py`, `gate.py`) | Discovers test runners, captures process exit codes, generates durable proofs (`.antios/proofs/`), and verifies project health. | Phase 8 & 10 rejected static file hashes (fatal Ratchet Expiry); Phase 93–95 proved durable test proofs grounded in physical exit code 0 and toolchain reality (`INV-04`) provide unfalsifiable evidence of correctness. | **KEEP** | Core verification engine (`framework/core/gate.py`, `project_proof.py`, `verdict.py`); provides test discovery and durable proof generation. | Maintain `gate.py` and `project_proof.py`; continue compiling test discovery configurations into declarative `antios.config.json`. |
| **Maker-Checker Subagents** (`antios-verifier`) | Independent verification subagent dispatched with clean, unpolluted context to audit git diffs, run physical tests, and emit structured verdicts. | Phase 23–25 adversarial campaigns proved author agents suffer confirmation bias ("hallucination loops") when checking their own work. Fresh-context Checker caught 100% of injected false-done anomalies and boundary violations. | **KEEP** | Tier-4 standard operating interface skill (`.agents/skills/antios-verifier/SKILL.md`); independent verification contract for high-risk changes. | Maintain skill instructions; ensure strict segregation between Maker prompt and Checker evaluation; ratify shallow depth $\le 2$. |
| **Session Journal & Handoff** (`ACTIVE_CONTEXT.md`, `handoff.md`, `dead-ends.md`) | Working memory across task turns, context resets, and subagent transitions; records active mission, blockers, and disproved dead ends. | Phase 10 forensic findings Q14–Q15 showed unbounded journals froze or caused amnesia. Phase 108 ratified strict line bounding (`docs/ACTIVE_CONTEXT.md` $\le 60$ lines, < 400 tokens) with integrated dead-ends ledger. | **REWORK** | Tier-1 ephemeral working memory (`docs/ACTIVE_CONTEXT.md`); survives amnesia without context bloat. | Consolidate fragmented journal files (`handoff.md`, `dead-ends.md`) into canonical 60-line `docs/ACTIVE_CONTEXT.md`; enforce line limits via automated tests (`tests/test_memory.py`). |
| **Lifecycle Hooks Declaration** (`.agents/hooks.json`) | Declares Antigravity platform extension points for `PreToolUse` and `Stop` hooks. | Phase 108 ratified native platform integration (`docs/architecture/antigravity/LIFECYCLE.md`). Direct path binding to `.antios/runtime/*.py` avoids shell wrappers, improves execution startup (<10ms), and eliminates cross-directory resolution bugs. | **REWORK** | Tier-2 managed platform configuration connecting Antigravity hook events directly to self-contained `.antios/runtime/` binaries. | Update compiler and installer to generate direct paths to `.antios/runtime/*.py` in `.agents/hooks.json` across all target projects; eliminate fragile relative shell invocations. |
| **Project Adapter Manifest** (`antios.config.json`) | Declarative project-specific configuration defining test runners, protected zones, domain paths, forbidden patterns, and telemetry modes. | Core vs Adapter specification (`CORE_VS_ADAPTER.md`) demonstrated that decoupling AntiOS Core from target domain specifics enabled 100% reusable, polyglot governance across Python, TypeScript, Rust, Go, and C. | **KEEP** | Canonical Tier-2 declarative project adapter manifest; the single authoritative configuration contract for target repositories. | Maintain strict JSON schema validation; support automated generation and sync via `antios adapt` (`framework/core/adapter.py`). |
| **Knowledge Compiler** (`compiler.py`) | Compiles AntiOS source into standalone target project instance (`.antios/`), emitting runtime closure scripts, anatomy prefix trees, and cryptographic manifest. | Phase 79–82 verified that compiling standalone runtime closures eliminates target project dependency on AntiOS framework repository, satisfying `INV-10` (`SOURCE != INSTANCE != PROJECT != ANTIGRAVITY`). | **KEEP** | Tier-1 canonical build engine (`framework/core/compiler.py`); builds `.antios/runtime/`, `.antios/anatomy.json`, and `.antios/manifest.json`. | Enhance compiler to enforce LF line-ending normalization, compute SHA-256 manifest ledgers, and verify zero `framework` imports via AST analysis before emission. |
| **Rules Engine** (`AGENTS.md`, `.agents/rules/`) | Defines constitutional rules, operating constraints, and agent directives loaded into agent sessions. | Phase 11 & 108 established that large system prompts (>100 lines) cause prompt bloat and instruction dilution. Ratified `docs/AGENTS.md` strictly $\le 40$ lines (< 250 tokens), focusing purely on axioms, protected zones, and verification laws. | **REWORK** | Ambient Tier-2 project orientation contract (`docs/AGENTS.md`), strictly bounded to $\le 40$ lines; progressive disclosure for deep rules. | Enforce $\le 40$ line bound on `docs/AGENTS.md` via `tests/test_context_bounds.py`; deprecate sprawling multi-file `.agents/rules/` directory in favor of single compact orientation contract. |
| **Skills Engine** (`.agents/skills/*`) | Provides specialized capabilities (`antios`, `antios-adapt-project`, `antios-debug`, `antios-engineer`, `antios-verifier`). | Phase 5 & 6 proved putting skills in `framework/` made them invisible to the platform engine. Placing them in `.agents/skills/` conforms to Antigravity skill discovery. Phase 55–60 validated dynamic skill generation from project anatomy. | **KEEP** | Tier-4 operating interface for developer and agent interaction; progressive on-demand activation. | Maintain core skill quintet (`antios`, `antios-adapt-project`, `antios-debug`, `antios-engineer`, `antios-verifier`); retire redundant legacy workflow scripts. |
| **Framework Core Modules** (`framework/core/*` 84 modules) | Canonical Python implementation of all governance, discovery, memory, capability, topology, verification, release, and telemetry engines. | Comprehensive codebase audit reveals 84 modules (41,282 lines): 14 directly consumed by CLI, 29 consumed by standalone scripts, 83 tested in unit suites. Several modules represent prototype abstractions (`agent_refactoring.py`, `specialist_generator.py`, `workflow.py`) ripe for consolidation. | **REWORK** | Modular canonical core framework library; organized into 10 cohesive subsystems with clean public API in `__init__.py`. | Consolidate overlapping modules, prune obsolete prototype remnants, maintain strict separation between Core and Adapter, and ensure 100% unit test coverage. |
| **In-Process Python State Machines** (`state.py` / `mission_state.py`, `context_budget.py`) | In-memory tracking of mission states, turn transitions, and token consumption within Python runtime processes. | Phase 10 forensics Q14–Q15 proved in-process Python state machines perish when CLI commands or hooks terminate. AI agents cannot maintain active Python process state across conversational turns. State must be persisted to version-controlled markdown or external SQLite. | **REPLACE** | Replaced by file-backed persistent state (`docs/ACTIVE_CONTEXT.md`), platform session transcripts (`transcript.jsonl`), and central event ledger (`experience.db`). | Remove in-memory stateful singleton daemons; re-orient `mission_state.py` to read/write serialized disk checkpoints. |
| **Vector DB / RAG Platform** (ChromaDB / proposed embeddings) | Proposed vector embeddings and semantic search over codebase files and past memories. | Formally and permanently rejected in Phase 6 & 10 (`REJECTED_ARCHITECTURE.md` #9). Vector memory introduces opaque retrieval failures, embedding model dependencies, non-deterministic recall, and high token costs. Deterministic prefix trees (`anatomy.json`, `wayfinding.py`) achieve sub-millisecond lookups with 0 tokens and 100% precision. | **REMOVE** | None (Permanently Excluded). | Prohibit any dependency on ChromaDB, Pinecone, or local embedding models; enforce deterministic wayfinding via `wayfinding.py`. |
| **Background File Watchers** (watchdog / inotify) | Speculative background daemon for real-time filesystem change monitoring and continuous drift detection. | Permanently rejected (`INV-15` Zero Background Daemons; `REJECTED_ARCHITECTURE.md` #8). Background daemons consume battery/CPU, risk file locking on Windows, and fail silently. On-demand verification via lifecycle hooks (`PreToolUse`, `Stop`) and `antios doctor` provides 100% reliability with zero background resource consumption. | **REMOVE** | None (Permanently Excluded). | Prohibit background daemon services; rely exclusively on synchronous platform lifecycle hooks and explicit CLI invocations. |
| **Static Model Snapshots** (`.antios/*.json`) | Machine-generated static intelligence snapshots (`anatomy.json`, `capabilities.json`, `specialists.json`, `manifest.json`). | Phase 55–60 demonstrated that caching repository structure into lightweight JSON files enables instant (<1ms) locality resolution during session startup without recursive git scanning. | **KEEP** | Tier-3 machine-generated project intelligence artifacts in `.antios/`, refreshed deterministically via `antios adapt` and `compiler.py`. | Maintain `.antios/manifest.json` cryptographic tracking; keep generated JSON artifacts compact and schema-validated. |
| **Central Experience Store** (`experience.db`) | External SQLite database (WAL mode) tracking tool metrics, session durations, friction points, and multi-project engineering intelligence. | Phase 103–107 ratified System B separation (`SYSTEM_A_B_SEPARATION.md`). Placing `experience.db` outside project repositories (`<central_data>/experience.db`) satisfies `INV-10`. AST static analysis verifies zero imports from System A. | **KEEP** | System B centralized engineering intelligence repository; external, read-only to active agents, fail-safe non-blocking. | Maintain SQLite schema migrations, automated WAL checkpointing, database backup/restore/purge commands in `antios data`. |
| **Telemetry Hook** (`telemetry_hook.py`) | PostToolUse lifecycle hook script that captures tool execution payloads, invokes privacy sanitizer, and records metrics to `experience.db`. | Phase 105 verified incremental transcript parsing with byte-offset checkpointing. Non-blocking telemetry axiom ensures telemetry failures never fail developer tasks. | **REWORK** | Standardized lifecycle hook or embedded post-execution step; ensuring zero framework imports in target instances. | Migrate `telemetry_hook.py` to adhere to Runtime Closure or execute via compiled CLI bridge `antios telemetry ingest`. |
| **Precursor Installer Script** (`framework/scripts/tools/install_project.py`) | Standalone CLI script for installing, updating, and repairing AntiOS instances. | Replaced in Phase 102 by unified CLI entrypoint `framework/cli.py` (`antios install`, `antios update`, `antios repair`, `antios remove`), which provides richer argument parsing, JSON output, and integrated doctor diagnostics. | **DEPRECATE** | Deprecated legacy wrapper; superseded by canonical `antios` CLI commands. | Retain as thin backwards-compatible shim pointing to `framework.cli:cmd_install`, or schedule for removal in v2.2. |
| **Cryptographic Execution Receipts** (`evidence/*.hash`) | Static SHA-256 state hashes intended to prove task execution validity. | Phase 8 & 10 proved file hashes only prove state changed, not that the change was functionally or pedagogically correct. Suffers fatal Ratchet Expiry: subsequent edits invalidate earlier hashes. Real-time OS process verification replaces static receipts. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #1). | Remove hash receipt generation scripts; rely exclusively on durable test proofs (`project_proof.py`) and exit code 0. |
| **Custom AST Blast-Radius Engine** (regex parser) | Proposed regex AST parser to compute downstream code impact and blast radius. | Phase 8 & 10 proved regex AST parsers give false confidence and miss dynamic imports. Native TypeScript compiler (`tsc`), Vitest module graphs, and pytest dependency tools provide 100% accurate, zero-maintenance dependency analysis. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #2). | Excised permanently; rely on native project toolchains for dependency and blast-radius analysis. |
| **StudyLab Schema Validators** (`validate_schema.py`) | Duplicated StudyLab's 20-field question schema in AntiOS Python scripts. | Phase 8 & 10 proved duplicating domain truth creates synchronization lag and violates Bounded Context. StudyLab's native compiler natively validates artifacts during build. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #3). | Excised permanently; domain schemas belong 100% to the target project. |
| **Arbitrary `verify_task.py` Fallback** | Hardcoded script fallback in `stop_gate.py` that ran arbitrary target scripts. | Phase 9 & 10 proved hardcoded script fallback allowed trivial test forgery (`import sys; sys.exit(0)`), completely bypassing verification. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #4). | Excised permanently; all verification must execute through registered, native project test suites discovered via `antios.config.json`. |
| **Large Hierarchical Swarms** (>3 agents) | Multi-tier agent dispatch trees with deep recursive delegation. | Phase 6 & 7 proved multi-tier agent trees introduce massive coordination latency (120s+), context fragmentation, and runaway token bills. Shallow hierarchy (Depth $\le 2$, Concurrency $\le 4$) is strictly enforced. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #5). | Excised permanently; strictly enforce Shallow Depth Law (`INV-06`) and Concurrency Ceiling (`INV-07`). |
| **Redundant GitHub MCP for Local Git** | Using GitHub MCP tools for local git operations (status, diff, commit). | Phase 8 & 10 proved GitHub MCP was slow, required WAN network roundtrips, consumed unnecessary tokens, and failed on unpushed local sandboxes. Local `git` CLI via `run_command` is strictly superior. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #6). | Excised permanently for local repository work; GitHub MCP reserved solely for remote issue/PR synchronization. |
| **StudySourceCore MCP Integration** | Integrated StudySourceCore stdio MCP server for procedural card generation. | Phase 8, 10 & 11 proved StudySourceCore was an external project. Domain contracts belong to StudyLab. Integrating it violated project scope and added fragile stdio dependencies. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #7). | Strictly forbidden from inspection, cloning, or integration. |
| **Custom Agent Runtime / Runner Daemon** | Building custom agent runner processes, thread pools, or background IPC daemons. | Phase 6 & 10 proved custom agent runner processes duplicate Antigravity's native platform primitives (`invoke_subagent`, `schedule`). AntiOS defines *when* and *why* to delegate, not *how* agents run. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #8). | Excised permanently; rely 100% on Antigravity native orchestration. |
| **Custom State Logging Databases** | In-repo SQLite or JSON databases logging turn-by-turn agent execution state. | Phase 6 & 10 proved custom state logging databases duplicate Antigravity's native, persistent, chronological `transcript.jsonl` audit stream. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #10). | Excised permanently; use platform `transcript.jsonl` for turn-by-turn history and `experience.db` outside the repo for metrics. |
| **LLM-as-a-Judge Drift Checkers** | Using non-deterministic LLM calls as blocking CI/Stop gates. | Phase 6 & 9 proved LLM-as-a-Judge gates introduce flakiness, high token costs, and prompt-injection vulnerabilities. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #11). | Excised permanently; enforce verification via physical test exit codes and Same Change Set rules. |
| **Fail-Open Hook Error Handling** | `except Exception: return allow` pattern in security hooks. | Phase 9 & 10 proved fail-open logic represented a catastrophic security vulnerability, allowing tool execution on script crashes or malformed payloads. | **REMOVE** | None (Permanently Excluded per `REJECTED_ARCHITECTURE.md` #12). | Permanently excised; strict **Fail-Closed** logic is universally mandated across all hooks and gates. |

---

## 3. Subsystem Migration Detail Cards

### 3.1 Subsystem: Runtime Boundary Protection
- **Existing Files**: `framework/scripts/hooks/pre_tool_guard.py`, `framework/templates/runtime/pre_tool_guard.py`
- **Classification**: **KEEP / COMPILE**
- **Research Evidence**: Phase 16–18 attack campaigns proved that Windows 8.3 short filename generation (`PROGRA~1`), alternate data streams (`file.txt::$DATA`), and path traversal (`../`) could bypass naive prefix checks. The hardened standard-library implementation in `framework/templates/runtime/pre_tool_guard.py` resolves canonical paths via `os.path.realpath`, lowercases on Windows, and fails closed with `<10ms` overhead.
- **Migration Plan**:
  1. Maintain `framework/templates/runtime/pre_tool_guard.py` as the canonical source template.
  2. Compiler emits this script to `.antios/runtime/pre_tool_guard.py` in target repositories.
  3. Ensure zero imports from `framework.core` (Runtime Closure).

### 3.2 Subsystem: Stop Gate Verification
- **Existing Files**: `framework/scripts/hooks/stop_gate.py`, `framework/templates/runtime/stop_gate.py`
- **Classification**: **REWORK**
- **Research Evidence**: In early phases, `framework/scripts/hooks/stop_gate.py` imported `framework.core.gate` and `framework.core.telemetry_bridge`. This violated the Four-Boundary Demarcation (`INV-10`) because target instances could not run if the upstream AntiOS repo was moved or missing. Phase 80/81 created the self-contained template in `framework/templates/runtime/stop_gate.py` which discovers tests directly from `antios.config.json` or package manifests without framework imports.
- **Migration Plan**:
  1. Standardize all installed projects to use `.antios/runtime/stop_gate.py`.
  2. Embed non-blocking telemetry payload emission or rely on CLI-level ingestion.
  3. Retire `framework/scripts/hooks/stop_gate.py` in favor of template compilation.

### 3.3 Subsystem: Workforce & Context Governance
- **Existing Files**: `framework/core/workforce_contract.py`, `framework/core/context_budget.py`, `framework/core/context_freshness.py`
- **Classification**: **REWORK**
- **Research Evidence**: Phase 83–86 proved that workforce contracts (max 4 concurrent subagents, max depth 2, max 10 launches) are vital to prevent swarm explosion. However, attempting to track token budgets in Python memory (`context_budget.py`) failed because agent sessions reset their Python processes. Declarative prompt bounding (`docs/AGENTS.md` $\le 40$ lines, `docs/ACTIVE_CONTEXT.md` $\le 60$ lines) solves the context explosion problem at zero computational cost.
- **Migration Plan**:
  1. Keep `workforce_contract.py` as the constitutional specification and validation engine.
  2. Transition `context_budget.py` and `context_freshness.py` into static document linters (`antios doctor`).
  3. Enforce context limits via automated CI tests (`tests/test_context_bounds.py`).

### 3.4 Subsystem: Project Memory & Wayfinding (System A)
- **Existing Files**: `framework/core/memory.py`, `framework/core/wayfinding.py`, `framework/core/anatomy.py`, `docs/ACTIVE_CONTEXT.md`
- **Classification**: **KEEP / REWORK**
- **Research Evidence**: Vector databases were permanently rejected in Phase 6 & 10. `wayfinding.py` and `anatomy.py` implement prefix trees and keyword inverted indexes that resolve file locations in $<1$ms without spending tokens or loading embedding models. Bounded markdown files survive model amnesia transparently.
- **Migration Plan**:
  1. Keep `wayfinding.py` and `anatomy.py` as core deterministic navigation engines.
  2. Enforce strict 60-line cap on `docs/ACTIVE_CONTEXT.md`.
  3. Consolidate historical dead-ends into a compact subsection of `ACTIVE_CONTEXT.md`.

### 3.5 Subsystem: Local Engineering Intelligence (System B)
- **Existing Files**: `framework/core/experience.py`, `framework/core/experience_analytics.py`, `framework/core/sanitizer.py`, `framework/core/telemetry_bridge.py`
- **Classification**: **KEEP**
- **Research Evidence**: Ratified in Phases 103–107. System B places `experience.db` completely outside project repositories (`%LOCALAPPDATA%\AntiOS\central_data\experience.db`). Multi-tier sanitization removes all API keys, GitHub tokens, user home paths, and internal reasoning chains. Incremental byte-offset checkpointing allows parsing session events in $<15$ms without blocking.
- **Migration Plan**:
  1. Retain System B SQLite WAL architecture.
  2. Maintain AST firewall tests ensuring System A never imports System B.
  3. Expand `antios data` and `antios experience` CLI subcommands for database maintenance and analytics.

---

## 4. Decommissioning & Excavation Protocol

For all components classified as **REMOVE** or **DEPRECATE**, AntiOS enforces a strict three-step excavation protocol:

1. **Step 1: Permanent Ledger Entry**: Record the component, evaluation phase, and empirical rationale in [`docs/architecture/REJECTED_ARCHITECTURE.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/REJECTED_ARCHITECTURE.md).
2. **Step 2: AST & Code Sweep**: Remove obsolete files, classes, and dead references. Verify via `grep_search` that no core module or template imports the removed symbol.
3. **Step 3: Negative Test Guard**: Add an automated regression test in `tests/test_architecture_freeze.py` or `tests/test_rejected_architecture.py` to ensure that future agents fail CI if they attempt to recreate the excised pattern.

---

## 5. Summary Disposition Statistics

| Disposition | Count | Percentage | Primary Subsystems |
| :--- | :---: | :---: | :--- |
| **KEEP** | 9 | 30.0% | PreToolUse Guard, Verification Engine, Maker-Checker, Adapter Manifest, Knowledge Compiler, Skills Engine, Static Snapshots, Central Experience Store, System B Sanitizer |
| **REWORK** | 8 | 26.7% | Stop Gate, Workforce Contracts, Session Journal, Hooks Declaration, Rules Engine, Framework Core Modules, Telemetry Hook, Context Budgeting |
| **REPLACE** | 1 | 3.3% | In-Process Python State Machines (replaced by file-backed Active Context & Platform Transcripts) |
| **DEPRECATE** | 1 | 3.3% | Precursor Installer Script (`install_project.py` superseded by unified `antios` CLI) |
| **REMOVE** | 11 | 36.7% | Vector DBs, Background Watchers, Static Receipts, AST Blast-Radius Engine, Domain Schema Validators, `verify_task.py` Fallback, Large Swarms, Redundant GitHub MCP, StudySourceCore MCP, Agent Runner Daemons, LLM Drift Checkers, Fail-Open Hooks |
| **UNKNOWN** | 0 | 0.0% | None (100% classified and grounded) |
| **Total** | **30** | **100.0%** | Comprehensive Component Architecture |

This matrix provides the definitive, unyielding blueprint for the migration of AntiOS components into the ratified Ambient Project OS architecture.
