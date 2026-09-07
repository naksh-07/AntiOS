# Google Antigravity Agent Engineering Lifecycle Model
**Status**: ARCHITECTURAL RESEARCH DOSSIER  
**Classification**: Grounded Empirical & Documentation Analysis  
**Author**: AntiOS Architecture Research Taskforce  

---

## 1. The Practical Agent Execution Loop

Antigravity agents working on non-trivial software engineering tasks do not operate in a single linear step. In real-world projects, the agent operates through an empirical 12-state cyclic state machine:

```
[Understand] ──> [Locate] ──> [Inspect] ──> [Reason] ──> [Plan] ──> [Change]
      ▲                                                                 │
      │                                                                 ▼
[Continue] <── [Re-verify] <── [Repair] <── [Diagnose] <── [Verify] <── [Execute]
```

This model is derived from observing live interaction trajectories across complex repositories (including multi-member Rust/PyQt/TypeScript monorepos) and analyzing Antigravity's internal step-processing pipeline (`language_server.exe` / `cortex`).

---

## 2. Stage-by-Stage Forensic Lifecycle Breakdown

---

### Stage 1: Understand
- **Information the Agent Has**: `[FACT]` The user prompt; static system instructions; XML `<user_information>` (active workspace paths, OS, app data directory, conversation ID); `<skills>` catalog summaries; active directory rules (`AGENTS.md` / `GEMINI.md`).
- **Information It Lacks**: `[FACT]` Codebase topology, file tree, dependencies, internal architecture, build commands, and past session history.
- **How It Obtains Information**: `[FACT]` Ingests system prompt and user text.
- **Antigravity Primitive Involved**: Language Server Prompt Compiler (`PreInvocation` lifecycle event).
- **Where Context is Introduced**: Initial system prompt assembly + any `injectSteps` from `PreInvocation` hooks.
- **Where Decisions are Made**: Decides whether to enter Planning Mode, activate a specific skill, or respond directly.
- **Where Mistakes Occur**: `[OBSERVED]` Misinterpreting user intent, assuming an incorrect technology stack, or assuming outdated API versions.
- **Where Rediscovery Occurs**: No prior conversation context exists; starts with zero codebase knowledge.
- **Where State is Lost**: N/A (Initial turn).
- **Where Verification Happens**: N/A.
- **Where Recovery Happens**: N/A.

---

### Stage 2: Locate
- **Information the Agent Has**: `[FACT]` The goal; keywords, error messages, or feature names mentioned in prompt.
- **Information It Lacks**: `[FACT]` The specific files, directories, modules, or configurations responsible for the feature.
- **How It Obtains Information**: `[OBSERVED]` Executes `list_dir`, `grep_search`, `find_by_name`.
- **Antigravity Primitive Involved**: Built-in ripgrep (`grep_search`) and directory lister (`list_dir`).
- **Where Context is Introduced**: Tool step results injected into conversation history.
- **Where Decisions are Made**: Selects candidate files to inspect based on grep matches and file paths.
- **Where Mistakes Occur**: `[OBSERVED]` Searching in massive generated directories (`node_modules`, `target`, `.git`), running broad unstructured regexes, or hallucinating paths that do not exist.
- **Where Rediscovery Occurs**: Agent must scan disk from scratch because no project map is injected into the prompt.
- **Where State is Lost**: Excessive grep output bloats token context, accelerating history truncation.
- **Where Verification Happens**: Compares search hit paths against expected module names.
- **Where Recovery Happens**: If grep yields zero results, agent re-tries with broader keywords or case-insensitive flags.

---

### Stage 3: Inspect
- **Information the Agent Has**: `[FACT]` Candidate file paths.
- **Information It Lacks**: `[FACT]` Actual code syntax, function signatures, imports, data models, and local invariants.
- **How It Obtains Information**: `[FACT]` Calls `view_file` (with optional `StartLine` and `EndLine` slices).
- **Antigravity Primitive Involved**: Built-in `view_file` tool (capped at 800 lines / 46,080 bytes per view).
- **Where Context is Introduced**: Injected as tool output in the message stream. Large outputs are truncated into `.system_generated/steps/<stepIdx>/output.txt`.
- **Where Decisions are Made**: Determines whether the viewed lines contain the defect or require inspecting imported dependencies.
- **Where Mistakes Occur**: `[OBSERVED]` Reading entire large files at once without line slicing; missing crucial context due to truncation; misinterpreting unfamiliar architectural abstractions.
- **Where Rediscovery Occurs**: Rereading files viewed in prior sessions because prior conversations are not loaded into context.
- **Where State is Lost**: Large file dumps in conversation context consume tokens, pushing early user instructions out of attention focus.
- **Where Verification Happens**: Mental verification: verifying that symbol definitions match usage.
- **Where Recovery Happens**: Reads additional slices using `StartLine`/`EndLine` when truncation occurs.

---

### Stage 4: Reason
- **Information the Agent Has**: `[FACT]` Target code snippets, error symptoms, and user constraints.
- **Information It Lacks**: `[FACT]` Full blast radius across untracked callers; hidden runtime invariants not visible in local file.
- **How It Obtains Information**: `[FACT]` Foundation model internal chain-of-thought (`thoughts_token_count`).
- **Antigravity Primitive Involved**: Gemini Thinking Conduit (streaming thoughts).
- **Where Context is Introduced**: Internal hidden reasoning buffer.
- **Where Decisions are Made**: Identifies root cause and synthesizes candidate fix.
- **Where Mistakes Occur**: `[OBSERVED]` Jumping to local quick-fixes that violate architectural invariants, break downstream callers, or introduce security flaws.
- **Where Rediscovery Occurs**: Re-deriving conclusions that may have been established and discarded in previous missions.
- **Where State is Lost**: `[FACT]` Internal thoughts are ephemeral and often discarded or compacted in long session transcripts.
- **Where Verification Happens**: Deductive verification against language semantics and stated constraints.
- **Where Recovery Happens**: N/A.

---

### Stage 5: Plan
- **Information the Agent Has**: `[FACT]` Problem root cause and proposed conceptual solution.
- **Information It Lacks**: `[FACT]` Explicit test commands, rollback strategy, and dependency order.
- **How It Obtains Information**: `[FACT]` Generates structured implementation plan artifact.
- **Antigravity Primitive Involved**: Planning Mode, `write_to_file` on `brain/<id>/implementation_plan.md`.
- **Where Context is Introduced**: Written into artifact storage; referenced in chat summary.
- **Where Decisions are Made**: Decomposes change into ordered phases (dependencies first, tests, changes, verification).
- **Where Mistakes Occur**: `[OBSERVED]` Skipping edge cases; forgetting verification commands; planning destructive mutations to immutable upstream directories.
- **Where Rediscovery Occurs**: Reformulating standard project build/test steps that should be known statically.
- **Where State is Lost**: If planning mode is skipped or turbo mode is enabled, the plan exists only ephemerally in model attention.
- **Where Verification Happens**: User review or automated auto-proceed check.
- **Where Recovery Happens**: User feedback requests revisions to `implementation_plan.md`.

---

### Stage 6: Change
- **Information the Agent Has**: `[FACT]` Plan, target file path, and exact replacement lines.
- **Information It Lacks**: `[FACT]` Concurrent disk modifications that occurred since file was viewed.
- **How It Obtains Information**: `[FACT]` Executes `replace_file_content` or `write_to_file`.
- **Antigravity Primitive Involved**: File mutation tools; **`PreToolUse` lifecycle hook**.
- **Where Context is Introduced**: Diff confirmation returned as tool output.
- **Where Decisions are Made**: Exact line-by-line code mutation.
- **Where Mistakes Occur**: `[OBSERVED]` Off-by-one line replacement; whitespace mismatch causing replace failure; modifying protected governance files (`.agents/`, `antios.config.json`, upstream submodules).
- **Where Rediscovery Occurs**: N/A.
- **Where State is Lost**: Overwrites prior file state on disk (relying on git for history).
- **Where Verification Happens**: **The Physical Interception Gate**: `PreToolUse` hook checks destination path against protected zones and 8.3 shortname aliases. If forbidden, hook returns `{"decision": "deny"}`.
- **Where Recovery Happens**: If `replace_file_content` errors due to non-unique match, agent re-reads file and retries with broader context.

---

### Stage 7: Execute
- **Information the Agent Has**: `[FACT]` Code modified on disk; intended build/compile command.
- **Information It Lacks**: `[FACT]` Process exit code, compiler errors, build warnings.
- **How It Obtains Information**: `[FACT]` Executes `run_command`.
- **Antigravity Primitive Involved**: Local terminal execution (`run_command`), **`PostToolUse` lifecycle hook**.
- **Where Context is Introduced**: Stdout/stderr returned to conversation stream.
- **Where Decisions are Made**: Evaluates compiler/linter feedback.
- **Where Mistakes Occur**: `[OBSERVED]` Running commands in wrong directory; using incorrect package manager; hanging processes on interactive prompts.
- **Where Rediscovery Occurs**: Experimenting with CLI flags to find how the project builds.
- **Where State is Lost**: Shell variables and directory changes (`cd`) do not persist to subsequent tool steps.
- **Where Verification Happens**: Compiler syntax check and typechecking.
- **Where Recovery Happens**: PostToolUse hook can trigger automated linters or error capture.

---

### Stage 8: Verify
- **Information the Agent Has**: `[FACT]` Built code; test runner commands (`cargo test`, `pytest`, `npm test`).
- **Information It Lacks**: `[FACT]` Whether test suite actually passes across all affected packages.
- **How It Obtains Information**: `[FACT]` Executes physical test runners via `run_command`.
- **Antigravity Primitive Involved**: Subprocess execution, **`Stop` lifecycle hook**.
- **Where Context is Introduced**: Test report stdout/stderr injected into context.
- **Where Decisions are Made**: Evaluates test assertion failures.
- **Where Mistakes Occur**: `[OBSERVED]` **Verification Bias**: Agent sees 1 passing test and assumes full suite passes; agent hallucinates that tests passed without executing them; agent edits the test to hide a defect.
- **Where Rediscovery Occurs**: Testing wrong module because monorepo member mapping is unknown.
- **Where State is Lost**: If test output is massive, failure lines may be truncated in stdout.
- **Where Verification Happens**: **The Physical Stop Gate**: When agent attempts to conclude, the `Stop` hook runs test runners independently. If tests fail, it forces loop re-entry via `{"decision": "continue"}`.
- **Where Recovery Happens**: If tests fail, transition to Diagnose stage.

---

### Stage 9: Diagnose
- **Information the Agent Has**: `[FACT]` Test failure stack trace and assertion diffs.
- **Information It Lacks**: `[FACT]` Root cause of the regression; whether regression is in modified code or pre-existing in repository.
- **How It Obtains Information**: `[FACT]` Greps test files, inspects logs, runs isolated single-test commands.
- **Antigravity Primitive Involved**: `run_command`, `view_file`.
- **Where Context is Introduced**: Failure details parsed into reasoning stream.
- **Where Decisions are Made**: Identifies the flaw in the change.
- **Where Mistakes Occur**: `[OBSERVED]` Misdiagnosing failure; blaming environment; modifying unrelated code.
- **Where Rediscovery Occurs**: Re-debugging issues that were previously solved.
- **Where State is Lost**: Error logs scroll out of active context.
- **Where Verification Happens**: Isolating failure reproduction to a single deterministic command.
- **Where Recovery Happens**: Dead-end memory logs falsified hypotheses to avoid repeating bad fixes.

---

### Stage 10: Repair
- **Information the Agent Has**: `[FACT]` Isolated failure cause and revised fix strategy.
- **Information It Lacks**: `[FACT]` Whether the repair introduces a secondary regression.
- **How It Obtains Information**: `[FACT]` Applies targeted edits.
- **Antigravity Primitive Involved**: `replace_file_content`, `PreToolUse` hook.
- **Where Context is Introduced**: Edit diff returned to context.
- **Where Decisions are Made**: Fixes the regression without expanding scope.
- **Where Mistakes Occur**: `[OBSERVED]` Code thrashing/oscillation (alternating between Fix A that breaks Test B and Fix B that breaks Test A).
- **Where Rediscovery Occurs**: N/A.
- **Where State is Lost**: Multiple failed edit attempts bloat context history.
- **Where Verification Happens**: PreToolUse guard confirms destination is still valid.
- **Where Recovery Happens**: AntiOS Anti-Oscillation ratchet halts repetitive failure loops.

---

### Stage 11: Re-verify
- **Information the Agent Has**: `[FACT]` Repaired code on disk.
- **Information It Lacks**: `[FACT]` Clean suite status across entire repo; git working tree cleanliness.
- **How It Obtains Information**: `[FACT]` Executes full project test suite and `git status`.
- **Antigravity Primitive Involved**: `run_command`, `stop_gate.py`.
- **Where Context is Introduced**: Passing test logs and clean git status diff.
- **Where Decisions are Made**: Confirms all acceptance criteria are met.
- **Where Mistakes Occur**: `[OBSERVED]` Leaving debug prints, temporary test files, or merge conflict markers in the tree.
- **Where Rediscovery Occurs**: N/A.
- **Where State is Lost**: N/A.
- **Where Verification Happens**: Stop Gate verifies test return code == 0 AND working tree contains 0 conflict markers across staged/unstaged/untracked files.
- **Where Recovery Happens**: If tests fail, reverts to Diagnose stage.

---

### Stage 12: Continue / Conclude
- **Information the Agent Has**: `[FACT]` Passed test proofs, verified diffs, and completion evidence.
- **Information It Lacks**: `[FACT]` What the next agent in tomorrow's session will need to know.
- **How It Obtains Information**: `[FACT]` Writes `walkthrough.md` artifact and updates `handoff.md`.
- **Antigravity Primitive Involved**: Artifact engine, Stop hook clearance.
- **Where Context is Introduced**: Final report output to user.
- **Where Decisions are Made**: Declares mission accomplished; collapses workforce.
- **Where Mistakes Occur**: `[OBSERVED]` Failing to document key decisions or leaving uncommitted changes.
- **Where Rediscovery Occurs**: **CRITICAL SYSTEM FAILURE POINT**: In vanilla Antigravity, if completion documentation is only written to `walkthrough.md` in `<appDataDir>\brain\<id>\`, tomorrow's agent in a fresh session starts back at Stage 1 with ZERO memory of this achievement!
- **Where State is Lost**: Entire conversation database and memory context are severed upon session termination.
- **Where Verification Happens**: Final Victory Audit by independent Checker subagent.
- **Where Recovery Happens**: Handoff contract ensures next session resumes with full context.

---

## 3. Physical Reality vs Model Illusion

A central insight of this research is the profound divergence between the model's internal perception and physical platform reality:

```
┌──────────────────────────────────────────────────────────┐
│                  MODEL PERCEPTION                        │
│  "I am an intelligent agent executing in an OS."         │
│  "I remember what we discussed in the last task."        │
│  "I verified that the code works correctly."             │
│  "The markdown rules prevent me from making errors."     │
└────────────────────────────┬─────────────────────────────┘
                             │
                     DIVERGENCE GAP
                             │
┌────────────────────────────▼─────────────────────────────┐
│                  PHYSICAL PLATFORM REALITY               │
│  1. The model is a stateless token-prediction function.  │
│  2. It has total amnesia across session boundaries.      │
│  3. It cannot 'see' the repository without tools.        │
│  4. Markdown rules have ZERO physical enforcement power. │
│  5. ONLY compiled shell hooks (hooks.json) can enforce.  │
│  6. ONLY exit code 0 from a real OS process proves test  │
│     success. Everything else is ungrounded assertion.    │
└──────────────────────────────────────────────────────────┘
```

AntiOS must be built entirely on the **Physical Platform Reality**, never relying on the model's perception or voluntary discipline.
