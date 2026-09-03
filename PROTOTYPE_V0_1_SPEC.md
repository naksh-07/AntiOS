# ANTIOS PROTOTYPE V0.1 SPECIFICATION

This specification defines the exact scope of AntiOS Prototype v0.1, to be built in Phase 7.
**Goal:** Prove that the smallest credible AntiOS architecture enables an Antigravity agent to safely and reliably execute a StudyLab task using deterministic boundaries and independent verification.

## 1. Prototype Boundary: What is IN Scope (V0.1)

The v0.1 Prototype will implement a strictly minimal set of components:

### A. Memory & Governance (Project Context)
- **`docs/AGENTS.md`**: The Tier-1 Global Constitution (max 100 lines). Contains the fundamental rules protecting StudyLab.
- **`docs/ACTIVE_CONTEXT.md`**: The Tier-2 Working Set (max 50 lines). Tracks current mission status.

### B. Safety & Enforcement (Hooks)
- **`.agents/hooks.json`**: Registration of one `PreToolUse` hook and one `Stop` hook.
- **`scripts/hooks/pre_tool_guard.py`**: A `PreToolUse` script that strictly blocks any `write_to_file` or `replace_file_content` targeting `rslib/` (upstream Anki core).
- **`scripts/hooks/stop_gate.py`**: A `Stop` script that runs a fast test suite (e.g., `cargo test` or a python script) and denies agent termination if the exit code is non-zero.

### C. Skills (Progressive Loading)
- **`.agents/skills/studylab-task-runner/SKILL.md`**: A focused skill defining the RPAC (Refine, Plan, Act, Consolidate) lifecycle and providing exact instructions on how to use the verification subagent.

### D. Verification (Mechanism)
- **Independent Verifier**: Usage of the native `invoke_subagent` tool (with `TypeName='research'` or `self`) to audit the primary agent's changes against the acceptance criteria before the Stop hook is triggered.

### E. Domain Tooling (MCP)
- **`studysource-core` MCP Server**: Integration of the existing MCP server to allow the agent to call `validate_artifact` deterministically instead of writing shell scripts.

## 2. Prototype Boundary: What is EXCLUDED (Later / Rejected)

- **Excluded (Later):**
  - Full Curriculum AST Blast-Radius analysis.
  - Multi-layer semantic documentation drift detection (Staleguard/Drift).
  - Cryptographic state hashing/receipts (Obsigna).
  - Hierarchical agent swarms > 2 agents.

- **Excluded (Rejected):**
  - Background daemon for receipt tracking.
  - Pure LLM-Judge CI blockers.
  - Custom agent runners / CLI wrappers (Use Antigravity native).
  - Storing task state across 7 fragmented files.

## 3. Experiment Design: Sandbox Validation

To evaluate Prototype v0.1, Phase 7 will conduct a controlled experiment within a disposable Git sandbox.

### The Sandbox
- A fresh copy of the StudyLab repository in an isolated scratch directory.
- Pre-seeded with a deliberate bug (e.g., a broken test or a syntax error in a LaTeX card).

### The Task
- **Goal:** Fix the seeded bug and update the corresponding documentation.
- **Acceptance Criteria:** The bug is fixed, tests pass, documentation is synced, and upstream Anki core remains untouched.

### The Baseline Comparisons
- **CONTROL:** Execute the task using raw Antigravity (no AntiOS hooks, no `AGENTS.md`, no verifier subagent).
- **TREATMENT:** Execute the task using Antigravity + AntiOS Prototype v0.1.

### Measurable Outcomes
1. **Task Success & Correctness:** Did the code actually compile and tests pass?
2. **Verification Quality:** Did the independent verifier catch mistakes the maker agent missed?
3. **Safety (Blast Radius):** Did the agent attempt to edit forbidden files, and did the `PreToolUse` hook successfully block it?
4. **Context Retention:** Did the agent maintain focus via `ACTIVE_CONTEXT.md` without amnesia?
5. **Documentation Sync:** Was the documentation updated in the "Same Change Set" before the `Stop` hook permitted completion?

## 4. Phase 7 Input

This document serves as the direct, actionable input for Phase 7. Phase 7 will physically construct the files listed in Section 1 within a sandbox and execute the Experiment Design in Section 3.
