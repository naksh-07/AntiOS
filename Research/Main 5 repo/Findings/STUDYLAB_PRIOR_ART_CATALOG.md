# STUDYLAB PRIOR-ART ADAPTATION CATALOG

## Overview
This catalog classifies all 39 architectural ideas extracted across the Top 5 prior-art repositories into five actionable tiers for the upcoming StudyLab Agent-Native Engineering Framework:
1. **ADOPT CANDIDATE**: Strong evidence and high StudyLab value; direct inclusion recommended.
2. **ADAPT CANDIDATE**: Compelling concept but must be redesigned for StudyLab's mathematics and Anki domain.
3. **EXPERIMENT CANDIDATE**: Promising mechanism requiring empirical validation in Phase 5.
4. **REFERENCE ONLY**: Valid architecture but not immediately needed for StudyLab's current scope.
5. **REJECT**: Anti-patterns or excessive complexity that should be explicitly avoided.

---

## 1. ADOPT CANDIDATES (Direct Adoption Recommended)

### `IDEA-HARNESS-001`: Client-Seam Semantic Cassette Recording & Replay
- **Source**: `nderman/agent-harness` (`src/harness/cassette/recording-client.ts`, `replay-client.ts`)
- **Rationale**: Provides 100% deterministic, zero-cost, offline CI/CD test execution for agent interactions. In StudyLab, agents generating cards or modifying math rendering templates can be regression-tested in CI without hitting live LLM APIs.

### `IDEA-HARNESS-002`: Strict Canonical Fingerprinting for Prompt Drift Detection
- **Source**: `nderman/agent-harness` (`src/harness/cassette/fingerprint.ts`)
- **Rationale**: SHA-256 hash over canonicalized `(model, system, messages, tools)` converts invisible prompt and tool schema regressions into loud, reproducible CI build failures. Essential for maintaining strict contract discipline in StudyLab.

### `IDEA-HARNESS-003`: Two-Gate Guardrail Architecture (Gate 1 Schema + Gate 2 Domain Policy)
- **Source**: `nderman/agent-harness` (`src/agent/guardrails.ts`)
- **Rationale**: Isolating syntax validation (Gate 1) from domain business rules (Gate 2) is the ultimate safety model. In StudyLab: Gate 1 validates JSON/card schemas; Gate 2 enforces Anki database invariants, deck uniqueness, and math model constraints.

### `IDEA-HARNESS-005`: Deterministic Structural Faithfulness Evaluation
- **Source**: `nderman/agent-harness` (`src/harness/eval/faithfulness.ts`)
- **Rationale**: Replaces flaky, expensive LLM judges with deterministic structural checks (verifying that claimed resolutions match actual tool calls in the trace). Guarantees zero false positives in automated builds.

### `IDEA-SPW-01`: Cognitive Defense Rationalization Tables & Iron Laws
- **Source**: `obra/superpowers` (`skills/using-superpowers/SKILL.md`, `skills/test-driven-development/SKILL.md`)
- **Rationale**: Tabular mapping of model rationalizations to non-negotiable rules crushes corner-cutting in math derivations, card validation, and test authoring.

### `IDEA-SPW-02`: Subagent-Driven Development with Brief Slicing & Review Packages
- **Source**: `obra/superpowers` (`skills/subagent-driven-development/SKILL.md`)
- **Rationale**: Slicing tasks into isolated task briefs and review diffs prevents parent context bloat while enabling clean parallel execution across curriculum modules.

### `IDEA-SPW-04`: Five-Round Fix Loop with Capability Escalation & Circuit Breaker
- **Source**: `obra/superpowers` (`skills/subagent-driven-development/SKILL.md:372-430`)
- **Rationale**: Directly solves pathological review thrashing: 3 in-place fix attempts, escalate to Pro model on rounds 4-5, and trippable controller circuit breaker on round 5.

### `IDEA-ANTH-01`: Three-Tier Progressive Disclosure Architecture
- **Source**: `anthropics/skills` (`template/SKILL.md`, `spec/agent-skills-spec.md`)
- **Rationale**: The gold standard for skill organization: Tier 1 metadata in system prompt (<100 words), Tier 2 instructions on trigger (<500 lines), Tier 3 resources on-demand. Keeps StudyLab system prompts lightweight.

### `IDEA-ANTH-02`: Deterministic Script Execution vs LLM Reasoning Separation
- **Source**: `anthropics/skills` (`skills/pdf/`, `skills/xlsx/`)
- **Rationale**: Offload Anki SQLite generation, `.apkg` ZIP compression, LaTeX rendering verification, and cloze syntax checking to deterministic Python scripts (`studysource-core`), reserving LLMs strictly for mathematical and pedagogical reasoning.

### `IDEA-PWF-01`: Durable 3-File Working Memory Pattern
- **Source**: `OthmanAdi/planning-with-files` (`skills/planning-with-files/SKILL.md`)
- **Rationale**: Separates working state into Roadmap (`study_plan.md`), Knowledge Base (`subject_knowledge.md`), and Execution Log (`generation_progress.md`). Survives context limits, crashes, and resets.

---

## 2. ADAPT CANDIDATES (Redesign for StudyLab Required)

### `IDEA-PWF-04`: 5-Guard Termination Oracle Completion Gate
- **Source**: `OthmanAdi/planning-with-files` (`scripts/check-complete.sh`, `hooks/hooks.json`)
- **StudyLab Adaptation**: Adapt from bash script hook into an Antigravity-native completion check. Before an agent concludes a card generation task, verify: (1) target card count achieved, (2) cloze syntax validated via `validate_artifact`, (3) subject policy resolved via `resolve_subject_policy`, and (4) stall detection cap not exceeded.

### `IDEA-PWF-05`: Structure-Aware Smart AST Injection (`inject-smart`)
- **Source**: `OthmanAdi/planning-with-files` (`scripts/inject-plan.sh`)
- **StudyLab Adaptation**: When an agent works through a large syllabus (e.g. Linear Algebra with 10 units), inject only the active unit and immediate next steps into the context window, keeping prompt overhead under 250 tokens per turn.

### `IDEA-EAI-02`: Quantitative Context Window Hygiene & Startup Audit
- **Source**: `eai-org/agent-toolkit` (`skills/context-checkup/SKILL.md`)
- **StudyLab Adaptation**: Create a startup diagnostic tool in StudyLab that audits active MCP tool schemas (`studysource-core`, `docker-mcp`, `notion-mcp-server`), lazy-loading non-critical tools to prevent upfront context exhaustion.

### `IDEA-EAI-05`: Teach-Back Active Recall Feature Gate
- **Source**: `eai-org/agent-toolkit` (`skills/verify-understanding/SKILL.md`)
- **StudyLab Adaptation**: Turn teach-back into a core pedagogical feature: require the agent to explain mathematical concepts back to the user or verify prerequisite mastery before generating advanced problem sets.

### `IDEA-EAI-06`: Verbatim Requirement Status Ledger
- **Source**: `eai-org/agent-toolkit` (`skills/check-ticket-implementation/SKILL.md`)
- **StudyLab Adaptation**: Map syllabus requirements to generated flashcard IDs (`DONE`, `PARTIAL`, `NOT DONE`), proving that every required mathematical concept is covered in the exported Anki deck.

### `IDEA-EAI-07`: Fresh-Eyes Procedural Blindness Removal
- **Source**: `eai-org/agent-toolkit` (`skills/fresh-eyes-review/SKILL.md`)
- **StudyLab Adaptation**: Dispatch a fresh-eyes reviewer subagent with zero context of previous generation attempts to critique generated math cards for mathematical accuracy, clarity, and LaTeX rendering validity.

### `IDEA-HARNESS-004`: Recoverable Guardrail Denials via Structured Tool Errors
- **Source**: `nderman/agent-harness` (`src/agent/loop.ts`)
- **StudyLab Adaptation**: When an agent attempts an invalid Anki modification (e.g. duplicate note ID or illegal cloze tag), return a structured error with explicit correction guidance, allowing the agent to self-correct within the loop.

### `IDEA-SPW-05`: Three-Path Router for Proportional Process Ceremony
- **Source**: `obra/superpowers` (`skills/brainstorming/SKILL.md`)
- **StudyLab Adaptation**: Route card authoring tasks by complexity:
  - *Spike*: Quick single-card prototype.
  - *Bounded*: Adding cards to an existing deck schema.
  - *Architectural*: Designing a brand-new interactive math visualization or custom Anki note type.

### `IDEA-SPW-06`: Specification-Driven Bite-Sized TDD Task Breakdown
- **Source**: `obra/superpowers` (`skills/writing-plans/SKILL.md`)
- **StudyLab Adaptation**: Structure study plan tasks with explicit `Consumes:` (source theorems, definitions) and `Produces:` (cards, proofs, tests) contracts.

---

## 3. EXPERIMENT CANDIDATES (Requires Empirical Validation)

### `IDEA-ANTH-03`: Automated Skill Trigger Description Optimization Loop
- **Source**: `anthropics/skills` (`skills/skill-creator/SKILL.md:333-405`)
- **Experiment Plan**: Evaluate whether running empirical train/test description optimization on StudyLab's math skills improves agent tool-calling accuracy on casual student queries.

### `IDEA-ANTH-04`: Dual-Arm Subagent Benchmarking with Blind A/B Comparator
- **Source**: `anthropics/skills` (`skills/skill-creator/SKILL.md:163-330`)
- **Experiment Plan**: Run A/B testing on prompt templates for mathematical card generation: compare cards generated with full CoT derivation vs direct cloze formatting using a blind comparator agent.

### `IDEA-HARNESS-006`: Fault-Injection Model Client Decorator
- **Source**: `nderman/agent-harness` (`src/harness/model-client/fault-injecting-client.ts`)
- **Experiment Plan**: Test StudyLab safety hooks by programmatically injecting corrupt card exports and invalid SQLite queries to confirm that safety barriers hold.

### `IDEA-PWF-03`: SHA-256 Plan Attestation & Tamper Refusal
- **Source**: `OthmanAdi/planning-with-files` (`scripts/attest-plan.sh`)
- **Experiment Plan**: Test whether cryptographic plan locking prevents rogue subagents from modifying approved curriculum structures during multi-agent generation runs.

### `IDEA-PWF-02`: Hardware-Aware Nonce-Delimited Context Framing
- **Source**: `OthmanAdi/planning-with-files` (`scripts/inject-plan.sh`, `.codex/hooks/context_frame.py`)
- **Experiment Plan**: Benchmark whether dynamic nonce framing prevents prompt injection when ingesting third-party web notes or user-uploaded PDFs into StudyLab.

---

## 4. REFERENCE ONLY (Valid Architecture, Future Consideration)

### `IDEA-EAI-03`: Memory-as-Inbox with Relocation Triage
- **Source**: `eai-org/agent-toolkit` (`skills/memory-doctor/SKILL.md`)
- **Status**: Valuable for long-term repository maintenance, but unnecessary during early StudyLab framework development.

### `IDEA-EAI-04`: Closed-Loop Self-Improvement & Discoverability Diagnosis
- **Source**: `eai-org/agent-toolkit` (`skills/self-improve/SKILL.md`)
- **Status**: Keep as reference for post-release rule maintenance.

### `IDEA-EAI-08`: Reviewer-Facing Intent Packaging
- **Source**: `eai-org/agent-toolkit` (`skills/handover/SKILL.md`)
- **Status**: Standard git PR practice; not unique to agent architecture.

### `IDEA-SPW-03`: Resilient Progress Ledger & Compaction Recovery Map
- **Source**: `obra/superpowers` (`skills/subagent-driven-development/SKILL.md`)
- **Status**: Subsumed by `IDEA-PWF-01` (Durable 3-File Working Memory).

### `IDEA-SPW-08`: Automated Test Suite State-Polluter Bisection (`find-polluter.sh`)
- **Source**: `obra/superpowers` (`skills/systematic-debugging/find-polluter.sh`)
- **Status**: Standard testing utility for isolating flaky tests.

### `IDEA-ANTH-05`: Portable Self-Contained Capability Packaging (`.skill` format)
- **Source**: `anthropics/skills` (`spec/agent-skills-spec.md`)
- **Status**: Standard packaging format for distributing skills across teams.

### `IDEA-HARNESS-007`: Terminal Tool-Forcing for Structured Output
- **Source**: `nderman/agent-harness` (`src/agent/resolution.ts`)
- **Status**: Clean pattern, but native structured output APIs may supersede it.

### `IDEA-HARNESS-008`: Error Taxonomy Disentanglement (Transport Retries vs Behavioral Re-prompts)
- **Source**: `nderman/agent-harness` (`src/harness/model-client/classify.ts`)
- **Status**: Standard SDK engineering practice.

### `IDEA-HARNESS-009`: Scaled Multi-Agent Review Pipeline (Shipit Workflow)
- **Source**: `nderman/agent-harness` (`.claude/skills/shipit/SKILL.md`)
- **Status**: High-quality pre-commit workflow, closely aligned with `IDEA-SPW-02`.

### `IDEA-HARNESS-010`: Staged Pre-Commit Secrets Gate Scan
- **Source**: `nderman/agent-harness` (`.claude/skills/shipit/SKILL.md:61`)
- **Status**: Excellent git hygiene rule; easily implemented via pre-commit hook.

---

## 5. REJECT (Anti-Patterns to Explicitly Avoid)

### `REJECT-01`: Manual Terminal/Session Restarts Between Micro-Tasks
- **Source**: `eai-org/agent-toolkit` (`/execute-plan-tasks`)
- **Why Rejected**: Asking the human developer to terminate their CLI session, copy-paste a new launch command, and re-run after every single 15-minute task introduces unbearable friction. StudyLab requires autonomous agentic execution with programmatic context management.

### `REJECT-02`: Seven-File Plan Directory Proliferation
- **Source**: `eai-org/agent-toolkit` (`.agents/plans/<id>-<slug>/`)
- **Why Rejected**: Fragmenting state across `.REQUIREMENTS.md`, `.PLAN.md`, `.DECISIONS.md`, `.TICKET-STATUS.md`, `.SELF-REVIEW.md`, `.HANDOVER.md` creates directory pollution and context fragmentation. The 3-file triad from `planning-with-files` is far cleaner and more cohesive.

### `REJECT-03`: Dual-Stack Shell Scripting (Bash + PowerShell Parallel Maintenance)
- **Source**: `OthmanAdi/planning-with-files` (`scripts/*.sh` and `scripts/*.ps1`)
- **Why Rejected**: Writing every utility twice in Bash and PowerShell leads to severe platform divergence, subtle quoting bugs, and doubled maintenance overhead. StudyLab should build all tooling in a single cross-platform runtime (Python or TypeScript).

### `REJECT-04`: Embedded Background WebSocket Servers for Toolkits
- **Source**: `obra/superpowers` (`skills/visual-companion/server.cjs`)
- **Why Rejected**: Running background HTTP/WebSocket servers inside agent plugins creates port collisions, orphan process leaks, and firewall complications. Modern Antigravity Generative UI artifacts render interactive interfaces natively without background servers.

### `REJECT-05`: Order-Strict Trajectory Assertions in Integration Tests
- **Source**: `nderman/agent-harness` (`src/harness/eval/trajectory.ts`)
- **Why Rejected**: Requiring tools to execute in an exact rigid sequence causes brittle test failures when an agent chooses an equally valid alternative order of read-only operations. Set-based dependency satisfaction is far more robust.

### `REJECT-06`: Polyglot Host Adapter Sprawl
- **Source**: `obra/superpowers`, `planning-with-files`
- **Why Rejected**: Maintaining custom configurations for 8+ disparate agent IDEs (`.cursor`, `.codex`, `.hermes`, `.kimi`, `.pi`) dilutes focus. StudyLab should target the canonical `SKILL.md` standard natively supported by Antigravity.
