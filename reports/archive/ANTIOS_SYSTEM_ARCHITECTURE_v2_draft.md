# AntiOS System Architecture Specification (`ANTIOS_SYSTEM_ARCHITECTURE.md`)

**Version**: 2.0.0-draft (Universal Re-baseline)  
**Date**: 2026-09-04  
**Status**: Canonical System Architecture Specification  
**Governing Vision**:
```text
   ┌─────────────────────────────────────────────────────────────────┐
   │                  Google Antigravity Platform                    │
   │      (Agent Lifecycle, Hook Transport, Tool Runtimes, MCP)      │
   └────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                           AntiOS Core                           │
   │       (Fail-Closed Guards, Stop Ratchets, Maker-Checker)        │
   └────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                         Project Adapter                         │
   │    (Declarative Boundaries, Test Runners, Linters, Workflows)   │
   └────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                 Target Project (e.g., StudyLab)                 │
   │     (Domain Schemas, Business Logic, Native Toolchains)         │
   └─────────────────────────────────────────────────────────────────┘
```

---

## 1. System Mission & Core Axioms

### 1.1 Mission
**AntiOS** is a universal, reusable, agent-native engineering operating system designed for **Google Antigravity**. Its purpose is to transform unconstrained, non-deterministic AI coding assistants into disciplined, verifiable, boundary-respecting software engineering systems operating over long-running sessions without human micromanagement.

### 1.2 The Proving Ground Principle
- **StudyLab is the proving ground, NOT the domain boundary.**
- AntiOS was battle-tested and refined against StudyLab's complex desktop architecture (TypeScript, Svelte, Rust `rslib`, double SQLite persistence, 20-field question schemas).
- While StudyLab's empirical trials proved the necessity of fail-closed hooks and process-level ratchets, **AntiOS Core contains zero hardcoded assumptions about StudyLab**.
- All domain semantics, immutable paths, schema rules, and test runner invocations are encapsulated within the **Project Adapter**.

### 1.3 The Governing Axioms of AntiOS
1. **Platform Sovereignty**: If Google Antigravity natively provides an orchestration, execution, scheduling, or logging primitive $\to$ **USE THE PLATFORM**. Do not rebuild what Antigravity already provides.
2. **Toolchain Ground Truth**: If a native compiler, type checker, or test framework provides verification $\to$ **USE THE NATIVE TOOLCHAIN**. Never replace compilers with brittle regex or AST parsers.
3. **Domain Sovereignty**: If the target application owns a contract, business invariant, or data schema $\to$ **DEFER TO THE PROJECT**. AntiOS does not validate application business logic.
4. **Code Over Prompt**: Prompt rules are cognitive orientation, not security boundaries. LLMs reliably violate text-only instructions under pressure. Critical safety invariants and completion ratchets **MUST be enforced by deterministic code** running outside the LLM context.
5. **Fail-Closed Standard**: In the event of missing parameters, parse errors, unhandled exceptions, or missing environment runtimes, AntiOS **always denies mutating actions and blocks task completion**.
6. **Shallow Depth Law**: Subagent nesting depth is strictly $\le 2$ ($\text{Parent} \to \text{Child}$). Recursive agent swarms create latency, context fragmentation, and token burn without quality improvement.

---

## 2. The 4-Tier Architectural Hierarchy

AntiOS establishes a strict four-tier separation of concerns:

```text
===================================================================================
                       TIER 1: GOOGLE ANTIGRAVITY PLATFORM
                               (Platform Mechanism)
===================================================================================
  - Subagent Lifecycle: invoke_subagent, manage_subagents, send_message
  - Tool Runtimes: run_command (PowerShell/Bash), write_to_file, replace_file_content
  - Tool Hook Transport: Stdio JSON-RPC IPC for PreToolUse and Stop events
  - User Interaction: Native Planning Mode (<planning_mode>, implementation_plan.md)
  - Immutable Logging: transcript.jsonl & transcript_full.jsonl
  - Ambient Tooling: Native MCP Client, background timers (schedule)
                                        │
                                        ▼
===================================================================================
                            TIER 2: ANTIOS CORE
                           (Universal Governance)
===================================================================================
  - Fail-Closed Path Guard Engine: framework/core/guard.py (path canonicalization,
    ancestor isolation, self-protection, 8.3 alias blocking)
  - Physical Stop Gate Ratchet: framework/core/gate.py (OS process exit code 0,
    git merge conflict checks, ENVIRONMENT_UNAVAILABLE trapping)
  - Maker-Checker Protocol & Verdict Engine: framework/core/verdict.py
  - Universal Engineering Skills: .agents/skills/ (antios-engineer, antios-verifier, antios-debug)
  - Universal Constitution: docs/AGENTS.md (core behavioral invariants)
  - Bounded Working State: docs/ACTIVE_CONTEXT.md (rolling ledger <= 60 lines)
  - Self-Test Harness: tests/ (zero-dependency standard library unit tests)
                                        │
                                        ▼
===================================================================================
                          TIER 3: PROJECT ADAPTER
                           (Declarative Binding)
===================================================================================
  - Configuration Manifest: antios.config.json (JSON schema)
  - Protected Domain Paths: Project-specific immutable files (e.g. rslib/, vendor/)
  - Forbidden Patterns: Wildcard matchers (e.g. rslib~*)
  - Dynamic Test Runners: Registered runners (npm test, pytest, cargo test, go test)
  - Code Quality Linters: Typechecks and linters (tsc, ruff, clippy)
  - Change Set Rules: Documentation sync constraints (Same Change Set)
                                        │
                                        ▼
===================================================================================
                          TIER 4: TARGET PROJECT
                               (Domain Truth)
===================================================================================
  - Application Source Code: TypeScript, Python, Rust, Go, Java, C++, etc.
  - Domain Semantics & Schemas: APKG schemas, database models, business rules
  - Native Compilers & Build Tools: tsc, cargo, vite, pyright, gcc
  - Test Suites: Unit, integration, visual regression, end-to-end tests
===================================================================================
```

---

## 3. Tier Demarcation & Responsibility Matrix

### 3.1 What Google Antigravity Owns (Platform Mechanisms)
Antigravity is the host substrate. AntiOS never duplicates:
- **Agent Scheduling & Concurrency**: The platform manages threads, execution queues, and token budgets. AntiOS defines *policy* for workforce sizing (SOLO, FOCUSED, PARALLEL) but delegates execution to `invoke_subagent`.
- **Hook Transport**: The platform intercepts tool calls and pipes JSON payloads over standard I/O. AntiOS implements the *hook recipient logic*.
- **Tool Runtimes**: The platform provides file editing and shell execution. AntiOS *governs access* to those tools.
- **Session Persistence**: The platform writes `transcript.jsonl`. AntiOS does not maintain custom execution journals or SQLite turn databases.
- **Interactive UI**: The platform provides Planning Mode. AntiOS does not render custom web UIs or terminal prompts.

### 3.2 What AntiOS Core Owns (Universal Governance)
AntiOS Core is 100% domain-agnostic and language-agnostic:
- **Safety Invariant Enforcement**: Evaluates every mutating IDE tool call against protected paths and denies unauthorized operations.
- **Completion Verification**: Evaluates task termination attempts, discovers tests via the adapter, executes them via subprocess, and blocks completion if tests fail.
- **Maker-Checker Orchestration**: Mandates fresh-context independent verification (`TypeName='self'`) for high-risk modifications, parsing structured JSON verdicts.
- **Systematic Debugging**: Enforces a deterministic 5-step root-cause protocol (`antios-debug`) before any patching.
- **Attention Bounding**: Restricts agent attention to bounded context files (`ACTIVE_CONTEXT.md` $\le 60$ lines) to eliminate context amnesia.

### 3.3 What the Project Adapter Owns (Declarative Binding)
The adapter translates generic AntiOS governance to a concrete repository:
- Maps project-specific directory structures to protected zones.
- Declares native test suites, working directories, timeout limits, and environment requirements.
- Configures domain-specific high-risk triggers (e.g., modifying state-machine files or database schemas).
- Supplies custom linter commands and verification scripts.

### 3.4 What the Target Project Owns (Domain Truth)
The project represents the software under development:
- Authoritative definition of business logic and domain correctness.
- Native build configurations (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`).
- Native test cases verifying application contracts.

---

## 4. Control & Data Flows

### 4.1 Mutating Tool Interception Flow (`PreToolUse`)
```text
Agent emits tool call: replace_file_content(TargetFile="rslib/src/lib.rs")
                              │
                              ▼
        [Antigravity Platform Tool Interceptor]
                              │
                              ▼ (JSON payload over stdin)
            [.agents/hooks.json -> pre_tool_guard.py]
                              │
                              ▼
                [framework/core/guard.py]
  1. Parse payload (tool_name, tool_input).
  2. Canonicalize path: os.path.realpath, os.path.normcase.
  3. Prefix matching via os.path.commonpath against:
     - Framework self-protection (.agents/, framework/)
     - Adapter protected_domain_paths (e.g., rslib/)
     - Adapter forbidden_patterns (e.g., rslib~*)
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
      [Path Protected?]                 [Path Allowed]
             │                                 │
             ▼                                 ▼
    Emit JSON to stdout:              Emit JSON to stdout:
  {"decision": "deny",              {"decision": "allow"}
   "reason": "Mutation forbidden"}             │
             │                                 ▼
             ▼                      [Antigravity Executes Tool]
[Antigravity Blocks Tool Call]
[Agent Receives Denial Error]
```

### 4.2 Task Completion Ratchet Flow (`Stop`)
```text
Agent completes work and signals task completion
                              │
                              ▼
            [Antigravity Platform Stop Trigger]
                              │
                              ▼ (JSON payload over stdin)
              [.agents/hooks.json -> stop_gate.py]
                              │
                              ▼
                 [framework/core/gate.py]
  1. Working Tree Cleanliness:
     - Execute `git diff --check` to block merge conflict markers.
  2. Test Runner Resolution:
     - Query Project Adapter (`antios.config.json`) for registered runners.
     - Fallback: Auto-detect manifests (package.json, pyproject.toml, Cargo.toml).
  3. Subprocess Execution:
     - Execute test command via OS subprocess with timeout ceiling.
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
     [Exit Code != 0]                   [Exit Code == 0]
             │                                 │
             ▼                                 ▼
    Emit JSON to stdout:              Emit JSON to stdout:
  {"decision": "continue",          {"decision": "approve"}
   "reason": "Tests failed: ..."}              │
             │                                 ▼
             ▼                      [Task Successfully Closes]
[Antigravity Resumes Agent Session]
[Agent Must Fix Failing Tests]
```

### 4.3 Maker-Checker Verification Flow
```text
[Maker Agent (Primary)]
  - Completes high-risk code implementation.
  - Updates docs/ACTIVE_CONTEXT.md.
  - Spawns fresh-context Checker:
    invoke_subagent(Role="Independent Verifier", TypeName="self", Prompt=...)
                              │
                              ▼
[Checker Agent (Fresh Context - antios-verifier)]
  - Strictly forbidden from spawning subagents (Depth <= 2).
  - Inspects git working tree: git status, git diff.
  - Executes physical test suite via run_command (zero trust in verbal claims).
  - Validates boundaries and Same Change Set doc synchronization.
  - Emits structured JSON verdict:
    ```json
    {
      "verdict": "PASS",
      "summary": "All tests pass, no protected boundaries touched",
      "results": [...]
    }
    ```
                              │
                              ▼
[Maker Agent Evaluates Verdict (framework/core/verdict.py)]
  - If PASS: Proceeds to complete task (triggers Stop Gate).
  - If FAIL: Fixes regressions identified by Checker and re-verifies.
```

---

## 5. The Platform Boundary & The Shell Gap

### 5.1 The Fundamental Platform Hook Limitation
Antigravity hooks (`PreToolUse`) intercept **IDE tool calls** (`write_to_file`, `replace_file_content`), but **do not intercept OS kernel filesystem syscalls**.
When an agent invokes `run_command`, the command executes directly in the host shell (PowerShell or Bash). A command like:
```powershell
powershell -Command "Set-Content -Path rslib/file.rs -Value 'corrupted'"
```
executes in the ambient OS environment, completely bypassing `PreToolUse` hooks.

### 5.2 Defense-in-Depth Architecture
AntiOS closes this gap through a 3-layer defense-in-depth model:

```
Layer 1: Pre-Execution Cognitive Orientation (docs/AGENTS.md)
  - Agent constitution explicitly forbids modifying protected paths via shell.
  - Sets behavioural guardrails and attention bounds.

Layer 2: Real-Time IDE Tool Interception (framework/core/guard.py)
  - 100% interception of write_to_file and replace_file_content.
  - Intercepts 8.3 short-name aliases and path traversals.

Layer 3: Post-Execution Physical Process Ratchet (framework/core/gate.py)
  - Evaluated at Stop hook before task completion is granted.
  - Inspects `git status` and `git diff` against protected domain paths.
  - If a protected path was mutated via shell, Stop Gate rejects completion.
  - Executes native test suites; corrupted code fails tests and halts completion.
```

---

## 6. Security & Fail-Closed Posture

AntiOS enforces strict **Fail-Closed Security**:
1. **Malformed Input**: If hook stdin contains unparseable JSON, `guard.py` emits `deny` and `gate.py` emits `continue`.
2. **Missing Configuration**: If `antios.config.json` is missing or corrupted, AntiOS falls back to safe universal defaults (protecting `.agents/`, `framework/`, and adapter config).
3. **Environment Missing (`ENVIRONMENT_UNAVAILABLE`)**: If an ambient runtime (e.g. `npm`, `python`, `cargo`) is not installed on the host, the Stop Gate traps `FileNotFoundError` and reports an environment blocker rather than falsely reporting broken application code.
4. **Hook Self-Protection**: AntiOS Core strictly denies any agent attempt to edit `.agents/hooks.json`, `framework/core/`, or `framework/scripts/hooks/`.
