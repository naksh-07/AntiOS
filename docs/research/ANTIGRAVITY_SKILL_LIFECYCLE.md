# Antigravity Skill Lifecycle & Progressive Disclosure Model
**Document**: `ANTIGRAVITY_SKILL_LIFECYCLE.md`  
**Status**: Foundational Research Dossier (Research 1)  
**Classification**: Rigorous Evidence-Backed Specification  
**Authority**: Official Customization Guide & Empirical Verification  

---

## 1. Executive Summary

Skills in Google Antigravity are modular packages of procedural knowledge designed to extend an agent's problem-solving capabilities without overwhelming its context window. This document details the exact lifecycle of a skill—from directory discovery and metadata injection to model-selected activation, multi-file execution, and trajectory persistence.

Crucially, this research audits whether skills can serve as the foundational mechanism for **ambient project governance and deterministic routing** (as hypothesized in AntiOS 2.0). The evidence demonstrates that while skills excel as on-demand operational runbooks, **they are structurally unsuited to act as unprompted, ambient, or non-bypassable control planes**.

---

## 2. The Two-Tier Progressive Disclosure Lifecycle

Antigravity implements the open Agent Skills specification (`https://agentskills.io/home`) using strict two-tier progressive disclosure:

```text
       [ TIER 1: Ambient Prompt Manifest ]
       ┌─────────────────────────────────────────────────────────────┐
       │ Platform scans skills/ directories at initialization.       │
       │ Parses YAML frontmatter of every SKILL.md.                  │
       │ Injects ONLY `name` and `description` into <skills> block. │
       │ Overhead: ~20–50 tokens per skill.                          │
       │ The full body of SKILL.md is NOT loaded into prompt.        │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                         User Request / Task Ingestion
                                      │
                                      ▼
                      [ Semantic Relevance Assessment ]
                      Model compares prompt intent against
                      third-person descriptions in <skills>
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
        [ Match Confirmed ]                    [ Match Rejected ]
        Agent issues explicit                  Agent relies on parametric
        tool call: `view_file(SKILL.md)`       knowledge & native tools
                   │                                     │
                   ▼                                     ▼
       [ TIER 2: Full Body Execution ]         [ Unspecialized Execution ]
       Full markdown instructions enter
       active conversation trajectory.
       Agent executes linked `scripts/`
       or inspects lazy `references/`.
```

---

## 3. Customization Discovery & Precedence Order

When Antigravity initializes a workspace, it traverses five distinct customization roots. If multiple skills share the identical `name`, they are resolved in strict priority order, with higher-priority skills completely shadowing lower-priority ones:

1. `[OFFICIAL]` **1. Workspace Project Customizations (Highest Priority):**
   * Path: Walks UP from the current working directory (CWD) to the Git repository root (folder containing `.git`) searching for `.agents/skills/` (also `.agent/skills/`, `_agents/skills/`, `_agent/skills/`).
   * Purpose: Team-shared, version-controlled project runbooks.
2. `[OFFICIAL]` **2. Workspace Declared Configurations:**
   * Path: Explicit declarations in `.agents/skills.json` or `.agents/plugins.json`.
   * Purpose: Explicitly mounted skills from relative or external paths; supports selective filtering (`include_only`, `exclude`).
3. `[OFFICIAL]` **3. Global Machine Discovery:**
   * Path: `~/.gemini/config/skills/` on the local developer host.
   * Purpose: User-specific tools, personal macros, and cross-project utilities.
4. `[OFFICIAL]` **4. Built-in Customizations:**
   * Path: Bundled natively with the Antigravity application (e.g. `antigravity_guide`, `agy-customizations`, `migrate-workflows`). Mounted by identifier rather than directory discovery.
5. `[OFFICIAL]` **5. Global Declared Configurations (Lowest Priority):**
   * Path: Listed in `~/.gemini/config/skills.json`.

---

## 4. Activation Mechanics & The Model Autonomy Dilemma

### 4.1 How Relevance is Evaluated
`[OFFICIAL]` The YAML frontmatter `description` field is the **sole textual signal** available to the foundation model when deciding whether to activate a skill:

```yaml
---
name: database-migrator
description: >-
  Executes safe schema migrations and dry-run validation for PostgreSQL.
  Use when modifying database schemas or running Alembic/Flyway migrations.
  Do NOT use for generic SQL queries.
---
```

* `[OFFICIAL]` **Third-Person Imperative:** The description must explicitly declare **what** the skill does and **when** it should be used.
* `[OFFICIAL]` **Negative Scoping:** Anti-triggers ("Do NOT use when...") prevent false-positive activations when queries touch adjacent topics.

### 4.2 Can the Agent Choose Not to Load a Relevant Skill?
* `[OFFICIAL]` & `[OBSERVED]` **YES**. In autonomous agent mode (`agent_behavior=AgentBehavior.AUTONOMOUS`), the LLM retains full discretionary judgment. If an agent believes its internal training weights or basic tools (`grep_search`, `run_command`) are sufficient to solve the problem, it will bypass loading `SKILL.md`.
* `[OBSERVED]` **Empirical Proof:** During baseline testing on AntiOS tasks, when an agent received *"Fix bug in parser"*, it did not load `antios` or `antios-engineer`; it directly inspected source files using `list_dir` and `view_file`.
* `[OFFICIAL]` **Forced Activation Surfaces:** Skill execution can only be guaranteed deterministically through:
  1. **User Slash Command**: User explicitly types `/antios` in the chat canvas.
  2. **User At-Mention**: User explicitly tags `@antios` in the message.
  3. **Explicit Orchestrator Directive**: An upstream orchestrator prompt explicitly commands: *"ACTIVATE the 'antios' skill before taking any action."*

### 4.3 Semantic Description Collision
* `[INFERRED]` When two skills share overlapping trigger phrases, the model suffers from semantic routing confusion.
* `[OBSERVED]` **The AntiOS Collision Case:**
  * `antios/SKILL.md`: *"Universal project-native control plane under AntiOS 2.0 governance. Use when planning, navigating, implementing, debugging, verifying, or orchestrating any engineering task in this repository."*
  * `antios-engineer/SKILL.md`: *"Universal engineering workflow policy for projects under AntiOS governance. Use when planning, implementing, modifying, or verifying features, bug fixes, refactors, and maintenance tasks across any software stack."*
  * **Result**: Both skills claim jurisdiction over all engineering tasks. The LLM either randomly picks one, loads both (wasting tokens), or loads neither.

---

## 5. Directory Anatomy & Lazy Asset Loading

`[OFFICIAL]` A production Antigravity skill is organized into a modular directory structure:

```text
skills/<skill_name>/
├── SKILL.md          # Required: Main instruction file with YAML frontmatter
├── scripts/          # Optional: Deterministic executable utilities (bash, python)
├── references/       # Optional: Bulky reference documentation and schemas
├── examples/         # Optional: Input/output examples and golden templates
└── resources/        # Optional: Static templates and boilerplate assets
```

### Best Practice Token Optimization Laws:
1. `[OFFICIAL]` **Lean SKILL.md:** The root instruction file should contain procedural workflow logic, decision trees, and relative links. It should stay under 150–250 lines.
2. `[OFFICIAL]` **Lazy Reference Deferral:** Bulky API specifications, database schemas, and migration manuals belong in `references/`. The agent reads them via `view_file` only if a specific sub-task requires them.
3. `[OFFICIAL]` **Encapsulated Automation:** Multi-step shell sequences or complex AST parsers should be packaged in `scripts/` (e.g. `python scripts/validate_schema.py`). The agent executes them via `run_command`, preventing prompt pollution.

---

## 6. Persistence & Context Trajectory

* `[OFFICIAL]` **Turn Persistence:** Once an agent invokes `view_file` on `SKILL.md`, the entire text of the skill is recorded as a `tool_result` step in the active conversation trajectory.
* `[OFFICIAL]` **Multi-Turn Retention:** The skill content remains visible in context across all subsequent turns within that conversation session until a **context compaction event** occurs.
* `[OFFICIAL]` **Session Boundary:** In a brand-new conversation session, the skill is **not** loaded. The new session starts with only the Tier 1 metadata catalog.
* `[OFFICIAL]` **Subagent Isolation:** Subagents do not inherit loaded skill text from the parent agent. They receive the Tier 1 `<skills>` catalog and must issue their own `view_file` call if they need the skill.

---

## 7. Strategic Audit: Can Skills Serve as AntiOS Operating Infrastructure?

| Candidate Role for Skills | Feasibility | Evidence Classification | Architectural Reality & Limitations |
| :--- | :---: | :---: | :--- |
| **Project Task Routing** | **POOR** | `[INFERRED]` | Skills rely on probabilistic model selection. If the user does not type `/skill` and the model does not trigger on the description, routing fails. Routing requires deterministic entrypoint rules. |
| **Persistent Project Memory** | **POOR** | `[OFFICIAL]` | Skills are static on-disk files. Modifying `SKILL.md` dynamically to store task state violates git discipline and risks prompt corruption. Task memory belongs in git-tracked docs or brain artifacts. |
| **Ambient Project OS Control Plane** | **UNFEASIBLE**| `[OBSERVED]` | An "Ambient OS" must govern every turn silently and reliably. Skills require voluntary model activation or explicit user invocation; an agent cannot be governed ambiently by a mechanism it can simply ignore. |
| **Procedural Runbooks & Workflows** | **EXCELLENT** | `[OFFICIAL]` | This is the exact native design purpose of skills. Highly effective for complex multi-step procedures (e.g. Maker-Checker verification, project adaptation, release certification). |
| **Deterministic Tool Automation** | **EXCELLENT** | `[OFFICIAL]` | Encapsulating validation scripts in `scripts/` provides physical execution guarantees without token bloat. |

---

## 8. Summary of Findings

1. `[OFFICIAL]` Skills operate strictly via **two-tier progressive disclosure** (metadata manifest in prompt $\to$ full body on demand).
2. `[OFFICIAL]` Discovery follows a strict 5-tier precedence order; identical skill names shadow lower layers completely.
3. `[OBSERVED]` Model-selected skill activation is probabilistic. The agent can and will bypass skills on routine prompts unless forced by slash commands, mentions, or parent prompts.
4. `[CONFLICT]` AntiOS's premise that skills can function as an "Ambient Control Plane" contradicts platform reality. Skills are **on-demand procedural runbooks**, not ambient execution kernels.
