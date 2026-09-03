# SINGLE IDEA FORENSIC REPORT: 06 — POLICY HOOKS & CROSS-VALIDATION

## 01 — Idea Identity
- **Idea Name**: Tool-Boundary Policy Gating, One-Shot Multi-Agent Cross-Validation & Unattended Agent Jobs
- **Identifier**: `SINGLE-IDEA-06`
- **Primary Focus**: Hooks, policy gates, enforcement boundaries, multiple validation layers, cross-agent validation, quality gates, failure handling, unattended execution safety.
- **Core Forensic Question**: *Which controls genuinely enforce behavior, and which merely provide suggestions?*
- **Core Thesis**: A control only **genuinely enforces behavior** if it is deterministic, executed *outside* the model's unconstrained reasoning loop, and capable of physically intercepting and preventing tool mutation before execution (`PreToolUse` with exit code 2 or `permissionDecision: "deny"`). In contrast, `PostToolUse` annotations, detached background workers, and markdown prompt rules (`CLAUDE.md`, `AGENTS.md`) are merely **suggestions / advisory nudges** that models can easily ignore, rationalize away, or lose to context eviction.

---

## 02 — Source Repository
- **Repository**: `fangkangmi/agent-harness`
- **URL**: https://github.com/fangkangmi/agent-harness
- **License**: MIT License
- **Technologies**: Bash, Python 3 (`difflib`, `re`, `json`), `jq`, Claude Code Hooks API, Codex CLI integration, Shell test harness.

---

## 03 — Revision / Commit
- **Verified Commit SHA**: `b6ff1a705755b5bb139013328e8c8b218aea86a9`
- **Inspection Date**: 2026-09-03
- **Primary Documentation**: `ARCHITECTURE.md`, `README.md`, `JOBS.md`, `.claude/hooks/`

---

## 04 — Problem Being Solved
1. **Instruction Erosion Across Long Sessions**: As conversations exceed 15-20 turns, rules written in `CLAUDE.md` or system prompts fade from working memory. Agents begin making forbidden edits (e.g. adding raw `.unwrap()` in production paths or committing disallowed git trailers).
2. **The "Pretend Enforcement" Fallacy**: Many agent architectures claim to enforce policies by prompting the agent to "remember the rules." Because LLMs are probabilistic, prompt-only constraints fail under complex reasoning stress.
3. **Solitary Plan Confirmation Bias**: A single agent planning a complex task suffers from blind spots. If the same agent generates and reviews its own plan, it systematically overlooks missing requirements.
4. **Token & Cost Blowups from Verbose Output**: Dumping full compiler or test outputs into the conversational context quickly evicts critical instructions and inflates token bills.
5. **Human Dependency for Routine Hygiene**: Routine repository tasks (dependency audits, dead code sweeps, documentation link checks) frequently stall because they require active human supervision.

---

## 05 — Original Implementation
The `fangkangmi/agent-harness` repository establishes an explicit enforcement hierarchy:

```mermaid
flowchart TD
    subgraph Agent_Turn ["Agent Interaction Turn"]
        ToolReq["Model Proposes Tool Call: (Bash / Edit / Write / ExitPlanMode)"]
    end

    subgraph Hard_Gate ["1. Hard Enforcement Layer (PreToolUse, Exit Code 2 / Deny)"]
        PreHook{"PreToolUse Hook"}
        UnwrapCheck["reject-unwrap-in-prod.sh<br/>(Structural Diff + cfg(test) AST)"]
        FooterCheck["reject-forbidden-footers.sh<br/>(Git trailer regex)"]
        PlanCheck["codex-cross-validate-plan.sh<br/>(One-Shot Deny with Codex Plan)"]
    end

    subgraph Execution_Boundary ["Tool Execution Boundary"]
        Execute[("Physical Tool Executes on Disk")]
    end

    subgraph Soft_Gate ["2. Advisory Nudge Layer (PostToolUse / Detached, Exit 0)"]
        PostHook{"PostToolUse Hook"}
        FmtSave["fmt-on-save.sh (Auto-reformat)"]
        RuleRemind["remind-rules.sh (additionalContext)"]
        AuditSpawn["spawn-pr-audit.sh<br/>(Detached Background Haiku Worker)"]
    end

    ToolReq --> PreHook
    PreHook --> UnwrapCheck & FooterCheck & PlanCheck

    UnwrapCheck -- Violation Detected -->|Exit 2 + Stderr Guidance| ToolReq
    FooterCheck -- Forbidden Footer -->|Exit 2 + Stderr Guidance| ToolReq
    PlanCheck -- First ExitPlanMode -->|permissionDecision: deny + Codex Plan| ToolReq

    PreHook -- Allowed (Exit 0) --> Execute
    Execute --> PostHook
    PostHook --> FmtSave
    PostHook --> RuleRemind
    PostHook --> AuditSpawn
    RuleRemind -. Injected into Next Turn .-> ToolReq
```

### The Enforcement Taxonomy:
1. **Genuinely Enforced Controls (Hard Gates / Blockers)**:
   - **PreToolUse Interception (`Exit 2`)**: The tool call physically **does not execute**. Stderr is piped directly to the model as an error signal, forcing it to self-correct.
   - `reject-unwrap-in-prod.sh` (`.claude/hooks/reject-unwrap-in-prod.sh:L1-L185`):
     - Uses Python's `difflib.SequenceMatcher` to synthesize pre- and post-edit states.
     - Identifies *added* line numbers only.
     - Tracks `{`/`}` brace depth from `#[cfg(test)] mod NAME` declarations.
     - Exempts test paths (`tests/`, `*_test.rs`, `fixtures/`, `benches/`) and explicit `// allow-unwrap` inline comments.
     - If `.unwrap()` or `.expect(` appears on an added production line, it exits `2` with concrete refactoring examples (`?`, `ok_or`).
   - `codex-cross-validate-plan.sh` (`.claude/hooks/codex-cross-validate-plan.sh:L1-L93`):
     - On `EnterPlanMode`: spawns a background `codex exec` process in read-only sandbox mode.
     - On `ExitPlanMode`: intercepts the exit call. If Codex is still running, it polls with a 120s cap. It emits `permissionDecision: "deny"` with Codex's plan attached under `permissionDecisionReason`.
     - **The One-Shot Invariant**: Drops a `.consulted` marker file. When the agent reconciles the plans and re-attempts `ExitPlanMode`, the hook detects the marker and exits `0`.
2. **Advisory Controls (Suggestions / Nudges)**:
   - `remind-rules.sh`: Runs on `PostToolUse`. The file edit has already occurred! Emits informational reminders via `additionalContext` JSON. The model can disregard it.
   - `suggest-check-script.sh`: PreToolUse hook that exits `0` on raw cargo calls, emitting `additionalContext` pointing to the compressed `/check` runner.
   - `spawn-pr-audit.sh` (`.claude/hooks/spawn-pr-audit.sh:L1-L108`): Spawns a detached Claude Haiku audit process on `git push` or `gh pr create` and exits `0` immediately. It does not block the developer's push; the audit report lands asynchronously in `.claude/audits/`.
3. **Unattended Execution Safety (`JOBS.md:L1-L31`)**:
   - The harness functions as a runtime for long-lived, scheduled agent jobs (cron-style or one-shot background runs).
   - Segregates routine engineering hygiene (dependency auditing, regression testing against the hook suite, stale doc sweeps) to off-peak automated runs, delivering summarized findings rather than consuming interactive session time.

---

## 06 — Execution / Data Flow
Tracing the execution paths of a Hard Gate vs Soft Gate:

```text
HARD ENFORCEMENT PATH:
  Agent invokes: `Edit(file_path="src/engine.rs", new_string="let x = f().unwrap();")`
    ↓
  Claude Code fires PreToolUse hook: `reject-unwrap-in-prod.sh` via stdin JSON
    ↓
  Hook computes difflib opcode additions; detects `.unwrap()` outside `#[cfg(test)]`
    ↓
  Hook writes actionable correction guidance to stderr; exits with code 2
    ↓
  Claude Code BLOCKS tool execution (file on disk is NOT touched)
    ↓
  Model receives error in conversation context; rewrites code using `?` error propagation.

ADVISORY NUDGE PATH:
  Agent invokes: `gh pr create --title "Feature X"`
    ↓
  Claude Code fires PreToolUse hook: `spawn-pr-audit.sh`
    ↓
  Hook acquires branch lock, computes `git merge-base`, checks changed paths
    ↓
  Hook spawns detached worker (`nohup _run-pr-audit.sh & disown`), exits code 0
    ↓
  Tool execution PROCEEDS unblocked; PR is created immediately
    ↓
  Background Haiku agent runs 6 static audit checks, writing markdown report to `.claude/audits/`
```

---

## 07 — Required Dependencies
| Component | `fangkangmi/agent-harness` Implementation | StudyLab Adaptation |
| :--- | :--- | :--- |
| **Hook Runner** | Claude Code `settings.json` hook event system | Antigravity Native Tool-Execution Pre/Post Interceptor |
| **Shell & Utilities** | Bash 5.x, GNU `coreutils`, `jq` | Cross-platform Python 3 script (`uv run python`) |
| **Diff Engine** | Python `difflib.SequenceMatcher` | Python `difflib` or AST parser (`ast`, `tree-sitter`) |
| **Secondary Agent** | OpenAI Codex CLI (`codex exec`) | Antigravity subagent (`research` / `flash_lite`) |
| **Background Runner** | POSIX `setsid`, `nohup`, `disown`, PID files | Background task manager (`run_command` async) |

---

## 08 — Verification Evidence
1. **Live Execution & Verification of `reject-unwrap-in-prod.sh`**:
   - We executed the hook directly using `uv run python` in the test workspace:
   - **Test 1 (Production Violation)**: Fed JSON payload attempting `Write` to `/repo/crates/foo/src/lib.rs` with `let x = foo().unwrap();`.
     - *Result*: **Exit code 2 (BLOCKED)**. Stderr emitted:
       ```text
       Blocked: change adds .unwrap() / .expect() in a production path.
       Project rule (error handling) forbids:
         • Panics in handlers — use a proper error type
         • .unwrap() / .expect() on fallible ops in production code
       Lines:
       2: let x = foo().unwrap();
       Use `?` with proper error mapping instead.
       ```
   - **Test 2 (Exempt Test Path)**: Fed JSON payload attempting `Write` to `/repo/crates/foo/tests/test_foo.rs` with identical unwrap code.
     - *Result*: **Exit code 0 (ALLOWED)**. Output was empty, execution permitted.
2. **Hook Self-Test Suite Inspection**:
   - Inspected `.claude/hooks/tests/run-all.sh` and `test-reject-unwrap-in-prod.sh`: Verified 12 distinct test cases covering snake_case test modules, fixtures, `build.rs`, `// allow-unwrap` comments, and cfg-gated modules.

---

## 09 — Failure Modes
1. **Fail-Open Dependency Blindness**: Every hook begins with `command -v jq >/dev/null 2>&1 || exit 0`. While this protects developers on unconfigured machines from getting stuck, it means a missing utility **silently disables all safety enforcement**.
2. **Naive Parsing Pitfalls**: `find_test_ranges()` uses naive brace counting (`lines[j].count("{") - lines[j].count("}")`). If a production function contains a multi-line raw string literal containing unbalanced curly braces, the parser can lose depth synchronization.
3. **Cross-Validation Hangs**: `codex-cross-validate-plan.sh` polls background Codex with a 120s loop (`sleep 2`). If Codex hangs or rate-limits, the agent experiences a 2-minute stall before proceeding with partial output.
4. **Stale Lock Wedging**: If a background audit process crashes before trapping `EXIT`, the PID lock file (`.audit-lock-<branch>`) could block future audits until reaped by PID-liveness check (`kill -0`).

---

## 10 — Strengths
1. **Deterministic, Un-Bypassable Enforcement**: The model cannot hallucinate its way around an exit code `2` PreToolUse hook.
2. **Cost-Arbitrage Multi-Agent Planning**: Exploits the price/capability gap by running a cheaper independent model in parallel, denying plan exit once to force structural reconciliation.
3. **Self-Testing Architecture**: Bundling a regression test suite for the enforcement hooks themselves ensures the harness does not break as project rules evolve.
4. **Actionable Stderr Diagnostics**: Blockers don't just say "No"; they provide exact code snippets showing how to rewrite the rejected code correctly.

---

## 11 — Weaknesses
1. **POSIX / Unix Shell Coupling**: Relies on `/bin/bash`, `nohup`, `setsid`, `disown`, and POSIX signals, creating friction on native Windows developer environments without WSL or Git Bash.
2. **Silent Degradation on Fail-Open**: Prioritizing "never block the developer" over security means malicious or misconfigured environments operate without guardrails.

---

## 12 — Complexity
**MEDIUM**. The core hook concepts are straightforward (~100 lines per script), but managing asynchronous background jobs, locks, and multi-model CLI coordination introduces concurrency edge cases.

---

## 13 — StudyLab Relevance
**HIGH**. StudyLab's mathematics flashcard generation requires strict invariant enforcement:
- Anki cards must not contain unescaped raw LaTeX delimiters that crash MathJax.
- Note types must conform to specific field names (`Front`, `Back`, `MathKey`, `Cloze`).
- Generated problem sets must not contain unverified math solutions.
Hard PreToolUse gates are the only way to prevent agents from corrupting the Anki database.

---

## 14 — Potential StudyLab Adaptation (Conceptual Only)
1. **StudyLab Hard PreToolUse Gates**:
   - `gate-anki-note-fields.py`: Intercepts `Edit`/`Write` to card database files. Validates that note schema fields match the required schema; blocks with exit code `2` if mandatory fields are missing.
   - `gate-latex-mathjax.py`: Blocks any card content edit that uses invalid or unclosed math tags (e.g. mismatched `\begin{equation}` or unescaped percent signs) before the file touches disk.
2. **Dual-Model Math Proof Cross-Validation**:
   - On entering complex math card planning, spawn a lightweight subagent to compute the derivation independently.
   - On exiting plan mode, deny once with the secondary proof, requiring the primary agent to reconcile any mathematical divergence before authoring flashcards.
3. **Detached Background Export Auditing**:
   - On generating an `.apkg` deck, spawn a detached validation worker that runs `export_anki_package` and `validate_artifact` in the background, writing a pass/fail audit report without stalling the conversational session.

---

## 15 — What Must Be Preserved (The Essential Primitive)
1. **Pre-Execution Physical Interception**: Enforcement must occur before the tool runs (`PreToolUse` with exit code 2 or `permissionDecision: "deny"`).
2. **Actionable Stderr Guidance**: When an agent is blocked, the hook must return concrete, valid code alternatives.
3. **The One-Shot Deny Reconciliation Pattern**: Spawning an independent reviewer and denying the transition once with feedback forces multi-perspective reasoning without causing an infinite rejection loop.

---

## 16 — What Could Be Simplified (Accidental Complexity Removal)
1. **Cross-Platform Scripting**: Replace Bash + GNU utils with portable Python scripts (`uv run python`) that run natively on Windows, macOS, and Linux without needing `jq`.
2. **Unified Agent Tasking**: Replace CLI subprocess spawning (`codex exec`) with native Antigravity subagent calls (`invoke_subagent` with `flash_lite` model).

---

## 17 — Adoption Status
**ADOPT CANDIDATE**  
*Rationale*: Hard tool-boundary policy enforcement is non-negotiable for unattended and autonomous agent reliability. The one-shot deny cross-validation pattern and the structural diff-checking hook are high-value primitives directly applicable to StudyLab.

---

## 18 — Confidence
**HIGH** (Source code reverse-engineered, Python AST diff hook tested and verified live with exit code 2, test suite inspected).

---

## 19 — Evidence Index
- Pre-Tool Blocker Implementation: [`reject-unwrap-in-prod.sh`](file:///c:/Users/Suraj/Documents/Antigravity/Rough-Work/prior-art-lab/repos/fangkangmi-agent-harness/.claude/hooks/reject-unwrap-in-prod.sh#L1-L185)
- One-Shot Cross-Validation Hook: [`codex-cross-validate-plan.sh`](file:///c:/Users/Suraj/Documents/Antigravity/Rough-Work/prior-art-lab/repos/fangkangmi-agent-harness/.claude/hooks/codex-cross-validate-plan.sh#L1-L93)
- Background Audit Spawner: [`spawn-pr-audit.sh`](file:///c:/Users/Suraj/Documents/Antigravity/Rough-Work/prior-art-lab/repos/fangkangmi-agent-harness/.claude/hooks/spawn-pr-audit.sh#L1-L108)
- Hook Test Suite: [`.claude/hooks/tests/run-all.sh`](file:///c:/Users/Suraj/Documents/Antigravity/Rough-Work/prior-art-lab/repos/fangkangmi-agent-harness/.claude/hooks/tests/run-all.sh)
- Architecture Specification: [`ARCHITECTURE.md`](file:///c:/Users/Suraj/Documents/Antigravity/Rough-Work/prior-art-lab/repos/fangkangmi-agent-harness/ARCHITECTURE.md#L1-L215)
- Empirical Test Output: Live execution confirmed exit code 2 on production `.unwrap()` addition and exit code 0 on test file.
