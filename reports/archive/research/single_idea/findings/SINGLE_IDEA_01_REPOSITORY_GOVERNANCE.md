# SINGLE IDEA FORENSIC REPORT: 01 — DETERMINISTIC REPOSITORY GOVERNANCE

## 1. Idea Identity
- **Idea Name**: Deterministic Repository Governance
- **Primary Mechanism**: Strict Multi-Tier Artifact Partitioning (`specs/`, `plans/`, `docs/`, `.agents/skills/`) enforced via Canonical Operating Contracts (`AGENTS.md`) and Deterministic CI Governance Oracles (`validate_factory.py`).
- **Core Concept**: Eliminating agent ambiguity and operational drift by transforming repository conventions from polite conversational prompts into strict directory-level boundary contracts, verifiable build gates, and clear role boundaries.

---

## 2. Source Repository
- **Repository**: `artreimus/software-factory-starter`
- **URL**: https://github.com/artreimus/software-factory-starter
- **Authors**: Arthur Reimus (`@artreimus`)
- **License**: MIT License
- **Technologies**: Python 3.11, POSIX Shell / Make, GitHub Actions CI, Docker, Cursor MDC Rules (`.cursor/rules/`), Agent Skills (`.agents/skills/`).

---

## 3. Revision / Commit
- **Inspected Branch**: `main`
- **Commit SHA**: `73caae568a22e40f56f22663b178f532ad8b2588`
- **Commit Date**: 2026-03-24
- **Commit Title**: `Merge pull request #2 from artreimus/codex/remove-templates`

---

## 4. Problem Being Solved
Autonomous AI agents frequently exhibit **operational drift, context corruption, and boundary confusion**:
1. **Ambiguity of Intent vs. Implementation**: Agents conflate "what the product should do" (product specifications) with "how I will code it today" (task plans) and "how the system currently works" (architecture documentation). This leads to agents overwriting production documentation with speculative plans or burying architectural decisions in transient PR descriptions.
2. **Ungoverned Agent Workflows**: Without structural boundaries, agents create random ad-hoc directories (e.g., `/scratch`, `/temp`, `/notes`), leave unfinished plan fragments scattered across the tree, or modify protected configuration files without authorization.
3. **Prompt-Only Governance Illusions**: Most agent setups rely exclusively on system prompts ("Please be careful and follow TDD"). When prompt attention degrades or context compresses, agents ignore these suggestions.
4. **Subagent Collision**: In multi-agent setups, multiple workers attempt to edit the same files concurrently, leading to merge conflicts and lost work.

---

## 5. Original Implementation
The repository implements a cohesive software factory governance model structured across three interlocking layers:

### A. Canonical Entry Point and Operating Contract (`AGENTS.md`)
`AGENTS.md` (79 lines at repository root) serves as the non-negotiable constitution for human and synthetic contributors. It establishes:
- **Core Rules**: Mandatory research before planning; mandatory planning before code (`plans/PLAN_<NAME>.md`); follow the plan during execution; validate before finalizing; record durable lessons in docs/tests rather than chat.
- **Artifact Boundaries**:
  - `specs/`: Intended behavior, user problems, acceptance criteria, non-goals.
  - `plans/`: Task-specific execution strategy, file changes, rollout, tests.
  - `docs/`: Current-state architecture, setup, security, operational reference.
  - `.agents/skills/`: Reusable agent procedural workflows.
  - `.cursor/rules/`: Editor rules mirroring `AGENTS.md`.
- **Subagent Boundaries**: Subagents are strictly restricted to independent tasks with disjoint write sets. The supervisor agent owns the task split, integration, and final verification.

### B. Deterministic Governance Oracle (`scripts/validate_factory.py`)
Rather than hoping an LLM respects the folder structure, the repository ships a deterministic Python validator (`validate_factory.py`) integrated directly into the `Makefile` and GitHub Actions CI:
- Asserts that every required governance file exists (`AGENTS.md`, `DESIGN.md`, core docs, core skills, core specs).
- Asserts that `docs/` contains at least 11 Markdown files.
- Asserts that `.agents/skills/` contains at least 7 operational skills.
- Asserts that `specs/use-cases/` contains at least 3 active specifications.
- Strictly forbids deprecated/legacy directories (such as `templates/`), throwing `SystemExit`.

### C. Explicit Tool & Security Boundaries (`docs/MCP_TRUST_BOUNDARY.md`)
External capabilities (MCP tools) are strictly partitioned:
- Disallows hardcoded credentials in prompts or environment samples.
- Requires allowlists for tool names, session IDs, and execution scopes.
- Mandates approval gates for destructive operations.

---

## 6. Execution / Data Flow

```text
[Human Intent / Feature Request]
              ↓
           (INPUT)
              ↓
[Role 1: Product Owner / Spec Skill] ──> writes/updates ──> [STATE 1: specs/use-cases/*.md]
              ↓
           (TRANSITION: Spec Approved)
              ↓
[Role 2: Planning Agent / Plan Skill] ──> writes/updates ──> [STATE 2: plans/PLAN_<NAME>.md]
              ↓
           (TRANSITION: Plan Approved)
              ↓
[Role 3: Implementation Agent / TDD]  ──> writes scoped code ──> [STATE 3: apps/service/ + tests/]
              ↓
           (OUTPUT: Working Diff)
              ↓
[Quality Gate 1: Local Make Targets] ──> executes ──> make lint && make test && make validate-factory
              ↓
[Role 4: Review Agent] ──> inspects diff against AGENTS.md + specs ──> [Review Record]
              ↓
           (TRANSITION: Review Passed)
              ↓
[Quality Gate 2: GitHub Actions CI] ──> runs in container ──> [Enforces validate_factory.py]
              ↓
[Role 5: Maintainer (Human Gate)] ──> merges PR ──> main branch updated
              ↓
[Role 6: Retrospective / Doc Sync] ──> updates ──> [STATE 4: docs/*.md & .agents/skills/]
```

### Forensic Trace:
1. **INPUT**: User provides a feature request or bug report.
2. **MECHANISM**: The agent consults `AGENTS.md` and routes to `.agents/skills/spec-to-plan/SKILL.md`. It does not edit code; it writes a frozen markdown contract.
3. **STATE**: Artifacts are created in their dedicated directories (`specs/`, `plans/`). Each artifact adheres to predefined headings.
4. **OUTPUT**: The implementation agent writes code and companion tests strictly within the bounds of the plan.
5. **CONSUMER**: The CI runner (`ci.yml`) executes `scripts/validate_factory.py`, ensuring repository invariants cannot be broken by rogue agent edits.

---

## 7. Required Dependencies
1. **File System Conventions**: Dedicated root folders (`specs/`, `plans/`, `docs/`, `.agents/skills/`).
2. **Python 3.11 Runtime**: For executing `scripts/validate_factory.py` (standard library only: `pathlib`, `sys`).
3. **Task Runner**: `make` or equivalent script runner to bind `lint`, `test`, and `validate-factory`.
4. **CI Engine**: GitHub Actions or local pre-commit hook to guarantee non-bypassable enforcement.
5. **Git & Codeowners**: `.github/CODEOWNERS` and protected branches (`main`).

---

## 8. Verification Evidence
During our live forensic session in the research workspace:
1. **Repository Invariants Check**:
   Executed `python3.11 scripts/validate_factory.py` inside `software-factory-starter`. Returned: `factory validation passed` (Exit code: 0).
2. **Unit Test Execution**:
   Executed `$env:PYTHONPATH="apps/service"; python3.11 -m unittest discover -s apps/service/tests -p "test_*.py"`. Returned: `Ran 2 tests in 0.001s, OK` (Exit code: 0).
3. **Tamper Test**: Intentionally deleting a required file (`docs/REPOSITORY_GOVERNANCE.md`) immediately caused `scripts/validate_factory.py` to fail with:
   `Missing required factory files: docs/REPOSITORY_GOVERNANCE.md` (Exit code: 1).

---

## 9. Failure Modes
1. **Shallow File Count Gaming**: `validate_factory.py` checks for file existence and file counts (e.g., `>= 11 docs`), but does not perform AST or semantic validation on document content. A misbehaving agent could create empty markdown files to pass CI.
2. **Plan Staleness**: While `AGENTS.md` mandates updating plans when code diverges, there is no compile-time or CI link between code diffs and plan checkboxes.
3. **Overhead on Micro-Fixes**: Requiring a formal `specs/` update, a `plans/PLAN_*.md`, and a review pass for a 1-line typo introduces high friction unless bypass rules are documented.
4. **Platform Coupling**: Relies on specific GitHub features (`CODEOWNERS`, branch protection APIs, PR templates) that do not translate automatically to local bare git environments.

---

## 10. Strengths
- **Predictability by Separation of Concerns**: Partitioning system knowledge into 4 explicit quadrants (`specs`, `plans`, `docs`, `skills`) eliminates cognitive collision. Agents know exactly where to read context and where to output changes.
- **Deterministic Enforcement Over Prompts**: Combining prompt rules in `AGENTS.md` with hard Python validation scripts in CI guarantees that structural rules are backed by machine gates.
- **Copyable Artifact Standardization**: All plans, use cases, and reviews follow identical naming conventions (`PLAN_<FEATURE>.md`, `use-case-NNN-<slug>.md`).
- **Pragmatic Multi-Agent Boundary Definition**: Explicitly disallows overlapping write sets, defining the supervisor as the sole integrator and subagents as isolated evidence gatherers.

---

## 11. Weaknesses
- **Static Invariant Rules**: The validator hardcodes specific file paths (`use-case-001-example.md`), making it slightly brittle as a generic template unless dynamically parameterized.
- **No Semantic Content Linting**: Does not verify whether a plan actually contains acceptance criteria or if a spec includes measurable bounds.
- **Absence of Memory Continuity**: Does not provide an active cross-session memory index or handoff ledger (unlike `agent-memory-system` or `planning-with-files`).

---

## 12. Complexity
**LOW**
- Pure standard library Python script (`validate_factory.py` is only 72 lines).
- Plain Markdown file conventions and simple Makefile targets.
- Zero external database or complex runtime requirements.

---

## 13. StudyLab Relevance
**HIGH**
- StudyLab’s architecture spans multiple distinct domains: mathematics pedagogical policy, Anki card generation, SQLite packaging, and LaTeX validation.
- Without deterministic repository governance, agents working on StudyLab will mix curriculum design documents with code, overwrite core policy guidelines, or produce unverified `.apkg` files.
- Having an unambiguous artifact taxonomy (`specs/` for mathematical syllabus requirements, `plans/` for procedural generation tasks, `docs/` for Anki database schemas) is directly aligned with StudyLab's needs.

---

## 14. Potential StudyLab Adaptation
*(Conceptual only — not implemented)*:
StudyLab can establish a tailored governance structure:
1. `specs/curriculum/`: Curricula, Bloom's taxonomy requirements, theorem coverage targets.
2. `plans/generation/`: Atomic card authoring tasks and generation plans.
3. `docs/engine/`: Schema documentation for Anki SQLite databases, Cloze models, and LaTeX renderers.
4. `scripts/validate_governance.py`: A CI gate that asserts:
   - All subject policies (`policies/*.yaml`) pass schema validation via `resolve_subject_policy`.
   - Core curriculum specs and procedural tests are present.
   - No deprecated Anki package structures exist in the repository.

---

## 15. What Must Be Preserved
The **four-way artifact boundary** (`specs/` vs `plans/` vs `docs/` vs `.agents/skills/`) and the **deterministic CI validation oracle** (`scripts/validate_factory.py`). Treating repository governance as a machine-checked build artifact rather than conversational guidance is essential.

---

## 16. What Could Be Simplified
- Replace hardcoded individual file lists in `validate_factory.py` with schema-based glob validation (e.g. ensure all files in `specs/` match frontmatter contracts).
- Consolidate sample docs to reduce upfront documentation maintenance.

---

## 17. Adoption Status
**ADOPT CANDIDATE** (Artifact Taxonomy & CI Validation Oracle) / **ADAPT CANDIDATE** (Tailored for StudyLab's curriculum and Anki generator domains).

---

## 18. Confidence
**HIGH (100%)**
- Source code inspected, tested, and validated locally on Windows with Python 3.11.
- All test suites passing; validation failures reproduce predictably on intentional schema tampering.

---

## 19. Evidence Index
- Repository Root: `c:\Users\Suraj\Documents\Antigravity\Rough-Work\prior-art-lab\repos\software-factory-starter`
- Commit SHA: `73caae568a22e40f56f22663b178f532ad8b2588`
- Core Contract: `AGENTS.md:L1-79`
- Factory Validation Script: `scripts/validate_factory.py:L1-72`
- Governance Documentation: `docs/REPOSITORY_GOVERNANCE.md:L1-40`
- Operating Model: `docs/OPERATING_MODEL.md:L1-48`
- Artifact Contract: `docs/DOCS_SPECS_PLANS_CONTRACT.md:L1-41`
- Subagent Boundaries: `docs/SUBAGENT_WORKFLOW.md:L1-30`
- MCP Trust Boundary: `docs/MCP_TRUST_BOUNDARY.md:L1-43`
- Cursor Rule Mirror: `.cursor/rules/software-factory.mdc:L1-13`
