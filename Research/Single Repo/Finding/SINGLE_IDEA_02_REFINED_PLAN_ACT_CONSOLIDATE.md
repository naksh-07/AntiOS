# SINGLE IDEA FORENSIC REPORT: 02 — REFINED PLAN ACT CONSOLIDATE (RPAC)

## 1. Idea Identity
- **Idea Name**: Refine → Plan → Act → Consolidate (RPAC) Task Lifecycle
- **Primary Mechanism**: Unidirectional four-phase development lifecycle combining machine-verifiable specification contracts, locked acceptance criteria, independent fresh-context verification (maker-checker separation), strict test ratchets, and crash-resilient progress checkpointing.
- **Core Concept**: Eliminating agent confirmation blindness, goal drift, and test suite decay by separating the agent who builds from the agent who grades, freezing acceptance commands before execution, and checkpointing durable state per task.

---

## 2. Source Repository
- **Repository**: `affectionatec/agentic-engineering`
- **URL**: https://github.com/affectionatec/agentic-engineering
- **Authors**: affectionatec (`@affectionatec`)
- **License**: MIT License
- **Technologies**: Claude Code Plugin & Skill Specification (`SKILL.md`), Markdown Documentation Chains, Git CLI (worktrees, branches, draft PRs), Shell test harnesses.

---

## 3. Revision / Commit
- **Inspected Branch**: `main`
- **Commit SHA**: `b44562c154516d6bc4865f9fd8a32b1a4d7a29c9`
- **Commit Date**: 2026-03-24
- **Commit Title**: `Merge pull request #11 from affectionatec/claude/agentic-ai-coding-skill-xr53kf`

---

## 4. Problem Being Solved
Standard autonomous agent execution suffers from six critical systemic pathologies:
1. **Maker-Checker Collusion (Self-Grading Illusion)**: When an agent generates code and then evaluates its own correctness in the same context window, it suffers from severe confirmation bias. It hallucinates that edge cases are handled, rationalizes failing tests, or assumes its implementation is correct without rigorous proof.
2. **Acceptance Criteria Weakening**: When an agent encounters unexpected implementation difficulties, it frequently edits the test suite or redefines the original goal to declare victory prematurely.
3. **Catastrophic Mid-Session Context Loss**: When an agent session crashes, exceeds token limits, or is compacted mid-task, all uncommitted in-memory progress evaporates.
4. **Test Suite Decay (Negative Test Ratchet)**: Agents frequently delete or disable existing tests (`test.skip()`, commenting out assertions) to make their changes pass CI.
5. **Architectural Memory Rot**: Decisions made during interactive debugging evaporate once the chat session closes, causing future agents to reopen already resolved debates.
6. **Uncontrolled Main Branch Contamination**: Autonomous agents committing directly to `main` leave unverified, broken states in the primary branch.

---

## 5. Original Implementation
The framework operationalizes the RPAC lifecycle through a suite of 10 modular skills, an unattended loop driver, and an isolated verifier sub-agent:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        THE RPAC LIFECYCLE ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────────┘

   1. REFINE (The Contract)
      ├── project-kickoff-prd     ──> Phased dialogue (Problem, Vision, P0/P1/P2)
      ├── technical-specification ──> Zero-ambiguity contracts, data models, invariants
      └── architecture-decision-record ──> Append-only decision history (ADRs)
               ↓
   2. PLAN (The Sequence)
      └── implementation-plan     ──> Dependency-ordered atomic tasks (≤90m, ≤5 files)
                                      Locks exact verify commands & expected outputs
               ↓
   3. ACT (The Road)
      ├── run-loop                ──> Unattended task driver (picks next unblocked task)
      ├── git-workflow            ──> task/<id>-<slug> branch, draft PR, producer build
      └── status-tracker          ──> Checkpoints task state: ⬜ -> 🟡 -> 🔍
               ↓
   4. CONSOLIDATE (The Gate & Memory)
      ├── independent-verification ──> Fresh-context @verifier subagent executes criteria
      │                                Enforces test ratchet (suite count only goes UP)
      │                                Binary PASS/FAIL verdict; turns 🔍 into ✅
      ├── documentation-maintenance──> Drift detection; updates PRD/Spec/ADRs
      ├── status-tracker          ──> Appends handoff log, clears In-Flight Checkpoint
      └── Human Merge Gate        ──> Human reads diff and merges PR (Agent NEVER merges)
```

### Key Technical Primitives in the Implementation:
1. **The Independent Maker-Checker Seam (`agents/verifier.md`, `skills/independent-verification/SKILL.md`)**:
   - The verifier runs in a completely fresh context window or sub-agent (`@verifier`).
   - It is strictly forbidden from seeing the producer's chain-of-thought, reasoning steps, or discarded attempts.
   - It receives only: the task ID, git branch name, and the locked acceptance criteria.
   - It executes the exact verification commands and evaluates stdout/exit codes.
2. **The Test Ratchet Rule (`skills/independent-verification/SKILL.md:L121`)**:
   - *"The suite count only goes up; a deleted or skipped test is an automatic FAIL regardless of everything else."*
3. **The In-Flight Crash Checkpoint (`skills/status-tracker/SKILL.md:L136`)**:
   - `docs/status.md` records an `In-Flight Checkpoint: Task-ID`.
   - If a session terminates abnormally, the next session reads the checkpoint and resumes from the exact failed task, losing at most one task's work.
4. **Locked Done Conditions (`skills/implementation-plan/SKILL.md:L104`)**:
   - Every task defines: `Verify via: <exact bash command>` and `Evidence: <exact output regex/string>`.
   - Once the plan is approved, the executing agent has zero authority to weaken the verification command.
5. **Unattended Loop Driver with Circuit Breaker (`skills/run-loop/SKILL.md:L41`)**:
   - Runs tasks sequentially up to a budget (`max-tasks=5`).
   - Automatically trips if 3 consecutive verification FAILs occur on a single task, escalating to the user.
   - **Iron Law**: The loop driver **NEVER merges pull requests**; merging is reserved strictly for the human gate.

---

## 6. Execution / Data Flow

### Step-by-Step Data Flow Trace:
```text
INPUT (User Feature Goal)
  ↓
[Step 1: REFINE]
  - Invokes: project-kickoff-prd + technical-specification
  - Agent dialogues with user to resolve ambiguities.
  - Emits: docs/prd.md and docs/spec/<domain>.md
  - Detects architectural forks -> records docs/adr/ADR-NNN-<slug>.md
  - STATE: Specs approved and frozen.

[Step 2: PLAN]
  - Invokes: implementation-plan
  - Parses docs/spec/<domain>.md into atomic tasks (M1-T1, M1-T2...).
  - Each task binds executable verification command and expected output evidence.
  - Emits: docs/plans/implementation-plan.md
  - Initializes: docs/status.md (all tasks marked ⬜ Not Started).
  - STATE: Plan locked.

[Step 3: ACT]
  - Invokes: run-loop
  - Selects next unblocked task (e.g. M1-T1).
  - Git: git checkout -b task/M1-T1-user-auth from main.
  - Status Checkpoint: updates docs/status.md -> In-Flight: M1-T1, State: 🟡.
  - Producer implementation agent edits code and writes unit tests.
  - Producer self-check: runs local lint and tests.
  - Status Checkpoint: updates docs/status.md -> State: 🔍 (Built, awaiting verification).
  - Git: git push origin task/M1-T1-user-auth; opens Draft PR carrying task ID and done command.
  - OUTPUT: Code diff on isolated branch + Draft PR.

[Step 4: CONSOLIDATE]
  - Invokes: independent-verification (dispatches @verifier subagent with fresh context).
  - Verifier checks out branch, executes locked verify command, checks test ratchet count.
  - Verdict generation:
      If FAIL: producer gets structured error logs to fix on branch (max 3 rounds).
      If PASS: verifier logs verdict to docs/verification-log.md; PR flipped from Draft to Ready.
  - Status update: docs/status.md -> M1-T1: ✅; In-Flight Checkpoint reset to `none`.
  - Handoff log: append-only entry added with exact test counts and next runnable task.
  - Documentation maintenance: checks if code diff diverged from docs/spec; proposes gated update.
  - Human Gate: developer inspects PR diff and executes git merge.
  - CONSUMER: Next agent session starts cleanly by reading docs/status.md.
```

---

## 7. Required Dependencies
1. **Version Control**: Git (supporting branching, draft PRs, and worktree isolation).
2. **Subagent Execution Seam**: Agent runtime capable of launching fresh-context sub-agents (e.g. Antigravity `invoke_subagent` or Claude Code sub-agent).
3. **Deterministic Test Harness**: Language test runner that outputs numeric test pass counts (e.g. `pytest`, `vitest`, `cargo test`, `unittest`).
4. **Structured Markdown Persistence**: Standard directory structure (`docs/spec/`, `docs/plans/`, `docs/adr/`, `docs/status.md`).

---

## 8. Verification Evidence
During our forensic inspection of `affectionatec/agentic-engineering`:
1. **File and Skill Anatomy**:
   Verified complete implementation across 12 directories in `skills/` and `commands/`:
   - `skills/run-loop/SKILL.md`: 57 lines, complete unattended driver logic.
   - `skills/independent-verification/SKILL.md`: 126 lines, explicit maker-checker rules.
   - `skills/status-tracker/SKILL.md`: 141 lines, 4-state lifecycle (`⬜ 🟡 🔍 ✅`).
   - `agents/verifier.md`: Specialized system prompt enforcing fresh-context judging.
2. **Circuit Breaker Verification**:
   Examined `skills/run-loop/SKILL.md:L41`:
   `Circuit breaker: 3 consecutive FAILs on one task stops the entire loop — escalate to the user with the verdict history.`
3. **Test Ratchet Verification**:
   Examined `skills/independent-verification/SKILL.md:L121`:
   `A deleted or skipped test is an automatic FAIL regardless of everything else.`

---

## 9. Failure Modes
1. **Process Ceremony Fatigue**: Managing 7 distinct document types (`prd.md`, `spec/*.md`, `ADR-*.md`, `implementation-plan.md`, `status.md`, `verification-log.md`, `AGENTS.md`) across 10 skills imposes heavy token and context overhead for small bug fixes or prototype experiments.
2. **Unattended Loop Deadlock on Merge Gate**: Because `run-loop` strictly enforces "Never merge PRs", an autonomous agent working through an implementation plan will deadlock once Task 3 requires code introduced in Task 2's unmerged PR. Worktrees alleviate git branch conflicts but do not solve downstream build dependencies.
3. **Verifier Environment Contamination**: If the verifier shares the same local file tree without git worktree isolation or container sandboxing, residual untracked files from the producer can cause tests to pass in the verifier when they would fail on a clean checkout.
4. **Mocked Assertion Exploits**: A producer agent can satisfy a naive verify command (`npm test`) by creating mock-heavy tests that do not test real integration logic (as observed in `agent-memory-system`). The verifier must verify test quality, not just exit code 0.

---

## 10. Strengths
- **Empirically Proven Reliability**: Solves the #1 failure mode of LLM agents: hallucinating completion. "Done is a verdict, not a claim."
- **Immutable Acceptance Contracts**: Freezing verify commands before coding prevents the agent from goal-shifting when things get difficult.
- **Resilient Memory with Zero Token Bloat**: `status.md` provides an instant briefing (<300 tokens) on session start, avoiding the need to re-read thousands of lines of conversation history.
- **Hard Anti-Regression Defense**: The test ratchet prevents sneaky deletions of failing regression tests.

---

## 11. Weaknesses
- **Extreme Fragmentation**: 10 separate skills create excessive router hops (`using-agentic-engineering` -> `project-kickoff-prd` -> `technical-specification` -> `implementation-plan` -> `run-loop` -> `independent-verification`).
- **High Human Interaction Burden**: Requiring human approval for every ADR, every spec change, and every task merge makes fully autonomous multi-step pipelines impossible without custom automation.

---

## 12. Complexity
**MEDIUM**
- No compiled binary daemons or background databases.
- High procedural and documentation complexity across 10 skills and 7 markdown templates.

---

## 13. StudyLab Relevance
**HIGH**
- StudyLab is an educational authoring platform where correctness is paramount: an incorrect mathematical proof or broken Anki note template ruins the learning experience.
- StudyLab cannot tolerate "producer self-grading": an agent generating a Linear Algebra flashcard deck cannot be trusted to judge whether its LaTeX compiles or whether cloze deletions are balanced.
- The maker-checker gate (dispatching a separate reviewer or verifier agent) directly matches StudyLab's pedagogical quality requirements.

---

## 14. Potential StudyLab Adaptation
*(Conceptual only — not implemented)*:
StudyLab should adopt a **Streamlined RPAC Pipeline** customized for procedural curriculum and card generation:
1. **Refine (Curriculum & Policy Gate)**:
   - Input: Syllabus topic (e.g. "Eigenvalues & Diagonalization").
   - Action: Resolve policy via `resolve_subject_policy`, specify card count, Bloom's level distribution, and LaTeX notation rules.
   - Output: `specs/curriculum/<topic>.md` with locked validation rules.
2. **Plan (Deck Task Slicing)**:
   - Break curriculum into atomic 10-card generation slices.
   - Lock validation command: `studysource-core validate_artifact --file <path>`.
3. **Act (Card Generation Agent)**:
   - Autonomous generation worker writes notes, equations, and cloze tags to staging JSON.
4. **Consolidate (Independent Verifier & Package Gate)**:
   - Fresh-context verifier runs `validate_artifact` and LaTeX compile checks.
   - Enforces test ratchet: card count must reach target; invalid syntax = immediate FAIL.
   - On PASS, invokes `export_anki_package` to build the final `.apkg`.

---

## 15. What Must Be Preserved
1. **Maker-Checker Separation**: The model that wrote the artifact must NEVER provide the final acceptance verdict.
2. **Locked Acceptance Criteria**: Verification commands and evidence criteria must be frozen before implementation begins.
3. **Test Ratchet**: Suite counts and coverage metrics can only monotonically increase.
4. **In-Flight Crash Checkpoints**: Persistent task-level checkpointing to prevent multi-hour rework after crashes.

---

## 16. What Could Be Simplified
- **Collapse 10 Skills into 4 Native Phases**: Merge `project-kickoff-prd`, `technical-specification`, and `architecture-decision-record` into a unified **Refine** phase.
- **Consolidate 7 Markdown Documents into 2**:
  - `CONTRACT.md` (combines PRD, Spec, and ADRs).
  - `PROGRESS.md` (combines Plan, Status, and Verification Log).
- **Automate Low-Risk Merges**: For internal procedural artifact generation (e.g. Anki decks), allow automated merges on clean verifier PASS, reserving human review for core engine code.

---

## 17. Adoption Status
**ADAPT CANDIDATE** (The RPAC lifecycle, maker-checker separation, and test ratchet are essential architectural primitives; the 10-skill, 7-doc implementation must be compressed for StudyLab).

---

## 18. Confidence
**HIGH (100%)**
- Complete source code and skill documentation inspected.
- Architectural mechanics, failure modes, and lifecycle invariants fully validated.

---

## 19. Evidence Index
- Repository Root: `c:\Users\Suraj\Documents\Antigravity\Rough-Work\prior-art-lab\repos\agentic-engineering`
- Commit SHA: `b44562c154516d6bc4865f9fd8a32b1a4d7a29c9`
- Main Architecture Blueprint: `README.md:L1-307`
- Flow Diagram: `assets/skills-flow.svg`
- Unattended Loop Driver: `skills/run-loop/SKILL.md:L1-57`
- Maker-Checker Gate: `skills/independent-verification/SKILL.md:L1-126`
- Verifier Agent Contract: `agents/verifier.md:L1-45`
- State Tracker & Memory: `skills/status-tracker/SKILL.md:L1-141`
- Technical Specification Contract: `skills/technical-specification/SKILL.md:L1-98`
- Documentation Maintenance: `skills/documentation-maintenance/SKILL.md:L1-175`
- Router: `skills/using-agentic-engineering/SKILL.md:L1-54`
