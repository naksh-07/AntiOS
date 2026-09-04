# **Deep Research Mission 03: Agent-Native Documentation Architecture**

## **1\. Executive Summary**

Autonomous coding agents (e.g., Google Antigravity, Claude Code, GitHub Copilot) fail in software repositories for two primary reasons: **context saturation** (loading monolithic, unstructured documentation that dilutes instruction following) and **semantic hallucination** (reading outdated prose documentation that contradicts actual code).  
Prior art from ecosystems such as the [AGENTS.md open format](https://github.com/agentsmd/agents.md), [Anthropic Agent Skills](https://github.com/anthropics/skills), [obra/superpowers](https://github.com/obra/superpowers), [eai-org/agent-toolkit](https://github.com/eai-org/agent-toolkit), and [nexus-substrate/nexus-agents](https://github.com/nexus-substrate/nexus-agents) demonstrates a clear consensus: **prose documentation is an advisory layer; executable code and machine-checked schemas are the ground truth.**  
Agent-native documentation must be structured around **Progressive Context Disclosure**:

> 1. A lean, root-level entry point (AGENTS.md) loaded unconditionally on every session, containing only non-negotiable operational invariants, project boundaries, and an index of pointers.  
> 2. Dynamic, on-demand operational guidance encapsulated in task-specific **Skills** (e.g., SKILL.md) that activate only when relevant workflows are executed.  
> 3. Machine-enforceable **Domain Contracts & Invariants** (e.g., schemas, AST linters, invariant tests) that fail builds when breached, rather than relying on an agent's memory.  
> 4. Auto-generated manifests and indexes that eliminate manual documentation synchronization.

For **StudyLab**, where a canonical Source → APKG domain contract already governs source fidelity, provenance, canonical semantics, validation, audit, and package boundaries, the agent-facing documentation layer should act as a **transparent harness**: it must point the agent directly to the domain contract, enforce validation scripts before commits, and provide procedural skills for mutating code without redesigning or duplicating domain invariants.

## **2\. Best Documentation Patterns**

| Pattern | Definition & Mechanics | Agent Utility | Evidence Level |
| :---- | :---- | :---- | :---- |
| **Progressive Disclosure** | Multi-tiered context loading: Tier 1 (Root Invariants in AGENTS.md), Tier 2 (Specialist Skills / Task Workflows in .agents/skills/), Tier 3 (Subsystem Architecture & Deep Specs). | Keeps agent context windows clean; prevents context poisoning and instruction dilution during routine edits. | \[DOCUMENTED\] [agents.md Spec](https://agents.md/), [Anthropic Skills](https://github.com/anthropics/skills) |
| **Executable Invariant Gates** | Replacing prose rules ("Do not mutate field X") with programmatic assertion suites, Pydantic/Zod schemas, and git pre-commit hooks. | Agents do not need to "remember" constraints; the compiler or test harness returns deterministic feedback when rules are broken. | \[IMPLEMENTED\] [nexus-substrate/nexus-agents](https://github.com/nexus-substrate/nexus-agents) |
| **Canonical Pointers (No Duplication)** | Enforcing a single home for every fact. When documentation must cite an invariant, it cites the canonical contract path and test file rather than re-explaining it. | Eliminates documentation divergence when requirements or data structures change. | \[DOCUMENTED\] [eai-org/agent-toolkit](https://github.com/eai-org/agent-toolkit) |
| **Two-Tier Architecture Logs (ADR vs Active Spec)** | ADRs are immutable historical logs recording *why* a choice was made at time T. Current subsystem docs describe *what* exists now. Active docs reference accepted ADR numbers. | Prevents agents from applying outdated architectural states found in historical ADRs. | \[DOCUMENTED\] [me2resh/agent-decision-record](https://github.com/me2resh/agent-decision-record) |
| **Auto-Generated Navigation Manifests** | Automated generation of file trees, API surface maps, and skill catalogs via CI or build scripts (manifest.json / INDEX.md). | Agents instantly discover correct entry points without issuing dozens of exploratory filesystem search calls. | \[IMPLEMENTED\] [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge) |

## **3\. Recommended Information Boundaries**

| Information Category | Best Home | Why |
| :---- | :---- | :---- |
| **Project Identity, Core Stack & Safe CLI Commands** | AGENTS.md (Root) | Agents need immediate orientation on build/test commands, formatting rules, and execution constraints on turn zero. \[DOCUMENTED\] |
| **Forbidden Behaviors & Hard Boundaries** | AGENTS.md (Root) \+ Linter/Pre-commit Hooks | High-severity rules (e.g., "Never modify provenance hashes manually", "Read-only git") must be seen upfront and backed by executable tooling. \[IMPLEMENTED\] |
| **Procedural Task Routines (How-To)** | .agents/skills/\<skill-name\>/SKILL.md | Workflows (e.g., "Add new card type", "Bump package version", "Run APKG compliance suite") should load only when the agent performs that specific task. \[DOCUMENTED\] |
| **System Architecture & Data Flows** | docs/architecture/ (e.g., overview.md, pipeline.md) | Deep design explanations that would bloat root context; accessed on-demand when architectural changes are planned. \[INFERRED\] |
| **Subsystem Specifications & Component Details** | Directory-level README.md or docs/subsystems/\<name\>.md | Localized context for specific modules (e.g., parser engine, media asset pipeline). Agents read these when touching files in that folder. \[DOCUMENTED\] |
| **Architectural Tradeoffs & Historical Decisions** | docs/adr/ADR-XXXX-\<title\>.md | Immutable rationale explaining *why* alternatives were rejected; referenced during refactoring or architectural discussions. \[DOCUMENTED\] |
| **Canonical Domain Contracts & Invariants** | Code Schemas (e.g., src/contracts/\*.py or \*.ts) \+ docs/contracts/ | The contract must be runnable/compilable. Prose docs in docs/contracts/ simply explain the domain rationale and link to the schema source. \[IMPLEMENTED\] |
| **Active Task State & Ephemeral Notes** | Git branches / PR descriptions / Ephemeral plan files (e.g., task.md) | Transient execution state should never pollute permanent repository documentation. \[IMPLEMENTED\] |
| **Catalog / Inventory of Capabilities** | Generated INDEX.md or .agents/manifest.json | Programmatically maintained registry of all skills, ADRs, and subsystems; prevents dead links. \[IMPLEMENTED\] |

## **4\. Source-of-Truth Patterns**

### **Problem Statement**

*"If a rule exists in three places, how do we prevent them from diverging?"*

### **Real-World Solutions & Mechanisms**

> 1. **The Single Canonical Source (Single Point of Truth \- SPOT):**  
   * **Rule:** Never duplicate rule definitions across multiple markdown files.  
   * **Implementation:** A rule is defined exactly once in its authoritative home (e.g., the schema definition src/domain/contracts/apkg.py or a dedicated rule specification docs/rules/provenance.md).  
   * **Referencing Pattern:** In all other documentation (such as AGENTS.md or subsystem guides), use a canonical pointer:Invariant: APKG output must pass strict schema validation. See \[APKG Contract\](src/domain/contracts/apkg.py) and run pytest tests/contracts/test\_apkg.py.  
> 2. **Code as Authoritative Contract (Executable Invariants):**  
   * Real-world implementations in nexus-agents and eai-org/agent-toolkit demonstrate that when documentation contradicts code, agents get confused.  
   * By defining contracts in **schemas (Pydantic / Zod / JSONSchema)** or **Type Definitions**, the schema itself is the primary source of truth. Documentation tools generate markdown representations directly from docstrings and schema fields.  
> 3. **Transclusion & Snippet Injection:**  
   * Documentation frameworks (e.g., mkdocs-monorepo, docusaurus, or custom scripts) use markdown transclusion (e.g., {{ \#include ../contracts/provenance.md }}) to embed canonical snippets into higher-level documents at build time.  
   * If an agent edits the canonical file, all generated references update automatically on build.  
> 4. **Rule Drift Detection in CI:**  
   * AST checkers scan docstrings and markdown files to ensure parameter names, command invocations, and types match current signatures. \[IMPLEMENTED\] [borghei/Claude-Skills doc-drift-detector](https://github.com/borghei/Claude-Skills/blob/main/engineering/doc-drift-detector/SKILL.md).

## **5\. Agent Entry Point (AGENTS.md)**

An effective AGENTS.md must be lean, dense, and operational. It is loaded on every turn; every unnecessary sentence consumes context window and weakens attention to critical invariants.

### **What AGENTS.md MUST Contain**

> * **One-sentence mission statement:** What the system is and its ultimate objective.  
> * **Non-negotiable operational invariants:**  
  * "Never commit directly to main."  
  * "Never alter canonical provenance hashes."  
  * "All schema changes must include a migration and backward-compatibility test."  
> * **Deterministic environment & command cheat-sheet:**  
  * Build command (e.g., pnpm build or poetry run build)  
  * Primary test command (e.g., pytest tests/unit/)  
  * Lint / typecheck command (e.g., ruff check . && mypy .)  
> * **Repository layout map (high-level pointers only):**  
  * 10–15 lines pointing to core directories (src/contracts/, src/engine/, tests/, docs/adr/, .agents/skills/).  
> * **Documentation index pointer:** Direct link to docs/INDEX.md or .agents/manifest.json.  
> * **Standard Operating Procedure (SOP) for changes:**  
  1. Inspect existing tests.  
  2. Implement change.  
  3. Run verification commands.  
  4. Update relevant subsystem docs or skills if behavior changes.

### **What AGENTS.md MUST NOT Contain**

> * **Full API references or data models:** Belongs in code schemas or generated API docs.  
> * **Detailed prose tutorials or onboarding histories:** Belongs in human guides or subsystem design documents.  
> * **Complete copies of ADRs:** Belongs in docs/adr/.  
> * **Outdated commands or multi-step manual setup workflows:** Agents need single-command automated recipes.  
> * **Subjective style guidelines:** Belongs in automated linter configurations (.eslintrc, ruff.toml).

## **6\. Documentation Drift Solutions**

Documentation drift occurs when code evolves but markdown stays static. Real-world solutions fall into three tiers:  
`┌────────────────────────────────────────────────────────┐`  
`│               1. PRE-COMMIT / CLI LEVEL                 │`  
`│  - Markdown link checker (broken relative links)       │`  
`│  - Command runner tests (executes code blocks in docs) │`  
`└──────────────────────────┬─────────────────────────────┘`  
                           `│`  
`┌──────────────────────────▼─────────────────────────────┐`  
`│               2. CI PIPELINE DRIFT GATES               │`  
`│  - Git Diff Mapping (code touched vs doc touched)      │`  
`│  - AST signature validation against docstrings/markdown │`  
`│  - Schema-to-Docs regeneration check (git diff --exit) │`  
`└──────────────────────────┬─────────────────────────────┘`  
                           `│`  
`┌──────────────────────────▼─────────────────────────────┐`  
`│              3. AGENTIC ADVERSARIAL REVIEW             │`  
`│  - PR Handover review (diff-aware doc updates)         │`  
`│  - nexus-agents drift-detected rule auditing           │`  
`└────────────────────────────────────────────────────────┘`

> 1. **Executable Code Blocks in Documentation (pytest-codeblocks / mdx-test):**  
   * Code snippets, CLI examples, and sample scripts in documentation are executed as part of the test suite. If an API signature changes and the sample code in docs/ fails to execute, CI fails. \[DOCUMENTED\]  
> 2. **Git Diff Cross-Verification in CI:**  
   * Script checks if changes to src/subsystem\_a/\*\* occurred without corresponding updates to docs/subsystems/subsystem\_a.md or related skills.  
   * \[IMPLEMENTED\] [Moxiedocs Git diff check pattern](https://moxiedocs.com/learn/what-is-documentation-drift):  
     `CHANGED_FILES=$(git diff --name-only origin/main HEAD)`  
     `if echo "$CHANGED_FILES" | grep -q "src/contracts/"; then`  
       `if ! echo "$CHANGED_FILES" | grep -q "docs/contracts/"; then`  
         `echo "ERROR: Contract code modified without updating docs/contracts/!"`  
         `exit 1`  
       `fi`  
     `fi`

> 3. **AST-Based Signature Verification:**  
   * Tools like doc-drift-detector in borghei/Claude-Skills parse Python/TypeScript ASTs, compare function signatures and parameter types against markdown tables, and flag discrepancies. \[IMPLEMENTED\]  
> 4. **Agent PR Handover Verification:**  
   * The eai-org/agent-toolkit handover pattern enforces that every agent PR generation step inspects modified files and cross-references them against governing documentation before submitting the pull request. \[DOCUMENTED\]

## **7\. ADR & Contract Patterns**

### **Architecture Decision Records (ADRs)**

> * **When an ADR is Useful:**  
  * When making architectural choices with non-obvious tradeoffs (e.g., choosing SQLite over DuckDB for package compilation, adopting a specific AST parsing approach, introducing a new invariant to the Source → APKG pipeline).  
  * When deprecating a major pattern or establishing a new domain boundary.  
> * **What Should NOT Require an ADR:**  
  * Routine bug fixes, adding test cases, minor refactoring within existing boundaries, library patch updates, or localized UI/formatting adjustments.  
> * **ADRs vs. Active Architecture Documentation:**  
  * **ADR (docs/adr/0004-sqlite-storage.md):** Immutable historical record. Represents the context, evaluated alternatives, and decision at a specific point in time. Status transitions: PROPOSED \\to ACCEPTED \\to SUPERSEDED (by ADR-0012).  
  * **Active Architecture (docs/architecture/storage.md):** Describes the system *as it exists right now*. It contains direct links back to accepted ADRs for rationale ("For rationale regarding table indexing, see \[ADR-0004\](docs/adr/0004-sqlite-storage.md)").  
> * **Agent Discovery of ADRs:**  
  * Maintain a lightweight generated index: docs/adr/README.md containing a simple table: ID | Date | Title | Status | Scope. Agents scan this single file to understand historical constraints without reading dozens of ADR files.

### **Contracts & Invariants**

> * **Prose Contracts vs. Executable Contracts:**  
  * *Prose Contract:* "All APKG export cards must retain their original markdown source hash in the metadata header." \\to **High risk of drift and agent violation.**  
  * *Executable Contract:* A Pydantic model (CardProvenance) with validation rules, plus an automated invariant test suite (tests/contracts/test\_provenance\_invariants.py) that runs against every test fixture. \\to **Zero risk of unflagged violation.**  
> * **Architectural Boundaries Enforcement:**  
  * Tools like import-linter (Python) or dependency-cruiser (Node) enforce boundary invariants (e.g., engine cannot import from cli; contracts cannot import from runtime). Violations fail CI immediately.

## **8\. Generated Index Patterns**

### **When to Generate vs. Manually Maintain**

> * **Manual:** High-level narrative, motivation, architecture rationale, project mission.  
> * **Auto-Generated:**  
  1. **File / Subsystem Manifests:** Map of all packages, modules, and their purpose lines.  
  2. **Skill Catalog (SKILLS.md / manifest.json):** List of available agent skills, inputs, and descriptions extracted from SKILL.md frontmatter.  
  3. **ADR Index Table:** ID, Title, Status, and Date parsed from ADR YAML frontmatter.  
  4. **Contract Schema Docs:** Markdown tables generated directly from Pydantic/Zod schemas.

### **Generation Workflow**

`Source Files (Code Docstrings / YAML Frontmatter / Schemas)`  
                         `│`  
                         `▼`  
        `Build Hook / Pre-commit Tool (Script)`  
                         `│`  
                         `▼`  
`Generated Output (docs/INDEX.md, .agents/manifest.json)`  
                         `│`  
                         `▼`  
  `CI Check (git diff --exit-code ensures generated files are committed)`

> * **Evidence:** [ansible-community/ai-forge](https://techbeatly.com/installing-ansible-ai-skills-with-lola-and-ai-forge/) uses an automated SKILLS.md index built from individual skill definitions to give assistants an accurate inventory without manual bookkeeping.

## **9\. Best Prior-Art Repositories**

| Repository | Strongest Idea | Weakness | StudyLab Relevance |
| :---- | :---- | :---- | :---- |
| **AGENTS.md Ecosystem** ([agentsmd/agents.md](https://github.com/agentsmd/agents.md)) | A tool-agnostic root file recognized across modern coding agents; sets universal repo etiquette and build commands. \[DOCUMENTED\] | Lacks built-in modularity for deep subsystem context; can become bloated if not disciplined. | **High:** Serves as StudyLab's primary root entry point for Antigravity. |
| **Anthropic Skills** ([anthropics/skills](https://github.com/anthropics/skills)) | Progressive context loading via standalone SKILL.md bundles with YAML frontmatter; procedural instructions on demand. \[DOCUMENTED\] | Does not solve domain invariant validation by itself; purely procedural. | **High:** Pattern for StudyLab's operational tasks (e.g., package builds, card verification). |
| **obra/superpowers** ([obra/superpowers](https://github.com/obra/superpowers)) | Directly integrated as an Antigravity (agy) plugin; provides agentic skills framework and tooling. \[IMPLEMENTED\] | Focuses on runtime agent capabilities rather than repository governance and static documentation drift. | **Medium-High:** Demonstrates direct compatibility with Google Antigravity. |
| **eai-org/agent-toolkit** ([eai-org/agent-toolkit](https://github.com/eai-org/agent-toolkit)) | Explicit separation of **Rules** (invariants) vs **Skills** (procedures); strict compaction rules (compact-governing-docs). \[DOCUMENTED\] | Heavy reliance on specific daily routines (RPA workflow) that may be overkill for smaller repos. | **High:** Establishes the exact architectural boundary between static rules and procedural skills. |
| **nexus-substrate/nexus-agents** ([nexus-substrate/nexus-agents](https://github.com/nexus-substrate/nexus-agents)) | Governance substrate featuring drift-detected rules, adversarial reviews, and immutable audits. \[IMPLEMENTED\] | Substantial infrastructure overhead; requires dedicated telemetry and orchestration machinery. | **Medium:** Inspires the drift-detection and audit-trail philosophy for StudyLab's APKG contract. |
| **ansible-community/ai-forge** ([ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)) | Standardized skill catalogs (SKILLS.md) and automated SDLC skills for linting, releases, and PR generation. \[IMPLEMENTED\] | Specific to Ansible and the Lola package manager ecosystem. | **Medium:** Proves the viability of generated skill indexes and SDLC automation for agents. |
| **GregorBiswanger/featherspec** ([GregorBiswanger/copilot-spec-driven-template](https://github.com/GregorBiswanger/copilot-spec-driven-template)) | Spec-Driven Development (SDD): clear separation of PRD, technical specification, and execution steps. \[DOCUMENTED\] | Can generate excessive markdown artifacts for tiny tasks if not carefully scoped. | **Medium:** Useful model for defining new StudyLab feature specs before agents write code. |
| **borghei/Claude-Skills (doc-drift-detector)** ([borghei/Claude-Skills](https://github.com/borghei/Claude-Skills/blob/main/engineering/doc-drift-detector/SKILL.md)) | Multi-dimensional drift scoring via AST signature extraction, git history diffs, and link validation. \[IMPLEMENTED\] | Relies on Python standard library AST; requires maintenance if language tooling evolves. | **High:** Practical blueprint for automating documentation drift checks in CI. |

## **10\. ADOPT / ADAPT / EXPERIMENT / REJECT**

`┌──────────────────────────────────────────────┐`  
`│                    ADOPT                     │`  
`│  - AGENTS.md root standard                   │`  
`│  - SKILL.md progressive disclosure          │`  
`│  - Executable invariant tests (in CI)        │`  
`│  - Automated link & path checkers            │`  
`└──────────────────────┬───────────────────────┘`  
                       `│`  
`┌──────────────────────▼───────────────────────┐`  
`│                    ADAPT                     │`  
`│  - eai-org Rules vs Skills model             │`  
`│  - AST drift detection (tailor to StudyLab)  │`  
`│  - Automated skill & ADR manifest generation │`  
`└──────────────────────┬───────────────────────┘`  
                       `│`  
`┌──────────────────────▼───────────────────────┐`  
`│                  EXPERIMENT                  │`  
`│  - CI git-diff doc-staleness warning gates   │`  
`│  - Agent PR self-audit doc checklist         │`  
`│  - Markdown executable codeblock testing     │`  
`└──────────────────────┬───────────────────────┘`  
                       `│`  
`┌──────────────────────▼───────────────────────┐`  
`│                    REJECT                    │`  
`│  - Monolithic context files (>500 lines)     │`  
`│  - Purely prose domain contracts             │`  
`│  - External wikis (Notion/Confluence) for AI │`  
`│  - Manual duplicate indexes                  │`  
`└──────────────────────────────────────────────┘`

> * **ADOPT (Immediate Best Practices):**  
  * Root AGENTS.md strictly capped at \<150 lines for turn-zero orientation.  
  * SKILL.md format with YAML frontmatter for progressive procedural context.  
  * Executable invariant tests in the test suite (pytest tests/contracts/) as the unbreachable source of truth.  
> * **ADAPT (Modify for StudyLab):**  
  * eai-org Rules vs. Skills architecture: Keep rules co-located with schemas and enforcement scripts, exposing skills only for multi-step mutations.  
  * Automated index generator: A lightweight Python build script that scans docs/adr/ and .agents/skills/ to output a consolidated docs/INDEX.md.  
> * **EXPERIMENT (Trial in Audit):**  
  * CI rule checking git diffs between src/contracts/ and docs/contracts/ to prompt documentation updates on contract changes.  
  * PR template asking the agent to declare which documentation files were inspected or modified.  
> * **REJECT (Anti-Patterns):**  
  * **Monolithic AGENTS.md / .cursorrules:** Dumping 1,000 lines of codebase explanation into root instructions causes context drift and degraded reasoning.  
  * **Prose-Only Domain Contracts:** Trusting an agent to adhere to a written markdown contract without schema-level runtime validation guarantees failure over time.  
  * **External Wiki Documentation:** Keeping architectural docs in Notion or Confluence outside the Git repository ensures rapid documentation drift.

## **11\. StudyLab-Specific Layering Around the Source → APKG Contract**

StudyLab already has an established domain contract governing **Source \\to APKG** (source fidelity, provenance, canonical semantics, validation, audit, runtime/package boundaries).  
The documentation and governance architecture must wrap around this contract without modifying or duplicating it:  
`┌────────────────────────────────────────────────────────────────────────┐`  
`│                        AGENT INTERACTION LAYER                         │`  
`│  - AGENTS.md (Root): Declares APKG Contract as inviolable invariant    │`  
`│  - .agents/skills/ (Procedural workflows: compile, validate, test)    │`  
`└───────────────────────────────────┬────────────────────────────────────┘`  
                                    `│ References & Executes`  
                                    `▼`  
`┌────────────────────────────────────────────────────────────────────────┐`  
`│                     CANONICAL DOMAIN CONTRACT (CORE)                   │`  
`│  - Schemas / Types (e.g. Card, Deck, Provenance, PackageMetadata)      │`  
`│  - Invariant Test Suite (tests/contracts/test_apkg_invariants.py)      │`  
`│  - Validation & Audit CLI (bin/validate-apkg, bin/audit-provenance)    │`  
`└───────────────────────────────────▲────────────────────────────────────┘`  
                                    `│ Documented By`  
                                    `│ (Pointers only)`  
`┌───────────────────────────────────┴────────────────────────────────────┘`  
`│                     SUPPORTING DOCUMENTATION LAYER                     │`  
`│  - docs/contracts/apkg_contract.md (Rationale, architecture boundaries)│`  
`│  - docs/adr/ (Historical records of rejected/accepted design choices)  │`  
`└────────────────────────────────────────────────────────────────────────┘`

### **Layering Rules:**

> 1. **Contract Inviolability:** AGENTS.md explicitly lists the contract as a read-only boundary:*"The Source \\to APKG contract in src/contracts/ is canonical. Agents must never alter provenance rules, card hash generation, or runtime boundaries without an accepted ADR and human approval."*  
> 2. **Execution over Explanation:** Instead of attempting to teach the agent the nuance of APKG binary packaging through prose, provide a skill .agents/skills/validate-apkg/SKILL.md that executes the existing validator CLI:*"Run python \-m studylab.cli validate \--source \<src\> \--output \<apkg\>. Inspect the JSON output for errors."*  
> 3. **Docs as Rationale, Code as Law:** docs/contracts/apkg\_contract.md documents the architectural rationale behind provenance and package boundaries, but explicitly points to src/contracts/ for type signatures.

## **12\. Proposed Documentation Principles for StudyLab**

*(Architectural principles, not a rigid folder hierarchy)*

> 1. **Principle of Progressive Disclosure:** Context must be loaded just in time. The root instruction file must contain only global invariants and pointers; subsystem and procedural details must live in modular skills loaded on demand.  
> 2. **Principle of Executable Authority:** When code and documentation diverge, the test suite and schema definitions are authoritative. Invariants that matter must be backed by CI tests or linter rules, not polite prose requests.  
> 3. **Principle of Single Canonical Truth (SPOT):** Every concept, rule, or contract must have exactly one authoritative home. All other files must link or point to that home rather than paraphrasing or duplicating its contents.  
> 4. **Principle of Immutable Decision History:** Architecture Decision Records (ADRs) document why a decision was made at a specific point in time and are append-only. Current architecture documentation describes the system in its active state and cites accepted ADRs.  
> 5. **Principle of Automated Indexing:** Navigation structures, skill catalogs, and schema documentation must be generated from code and frontmatter metadata by automated scripts, preventing manual index rot.  
> 6. **Principle of Change Co-location:** Documentation describing a component should live as close to that component as possible (e.g., package READMEs alongside code, inline type hints and schemas), and documentation changes must be committed in the same pull request as the code changes.  
> 7. **Principle of Lean Attention:** Maximize the signal-to-token ratio in every agent-facing document. Avoid filler language, generic advice, and repetitive formatting. Every line must inform an agent action or constrain an error.

## **13\. Open Questions for Hands-on Audit**

> 1. **Contract Execution Interface:** Does StudyLab's existing Source \\to APKG contract currently provide a clean CLI or Python entry point that an agent can invoke in a single line to verify compliance?  
> 2. **Schema Introspection:** Are the canonical domain types defined in a format that easily auto-generates documentation (e.g., Pydantic v2 / TypeScript types / JSONSchema), or are they implicit in transformation functions?  
> 3. **Linter & Pre-Commit Hook Latency:** How fast does the existing validation and invariant test suite run? (If contract tests take \>30 seconds, running them on every agent turn will cause timeout or execution friction).  
> 4. **Agent Skill Discovery Mechanism:** How does Google Antigravity in the StudyLab environment discover and load skills? Does it use the .agents/skills/ directory convention, an agy plugin format, or direct prompt injection?  
> 5. **AST Drift Feasibility:** What languages exist in StudyLab's codebase (Python, TypeScript, Rust), and can a lightweight AST/link-validation script run in \<2 seconds in CI?

## **14\. Final Answer: The Smallest Viable Documentation System**

**What is the smallest documentation system that gives an AI agent enough reliable project context without creating a giant, duplicated, constantly-stale documentation bureaucracy?**  
The smallest viable system consists of exactly **three functional tiers and four file types**:  
`1. ROOT ANCHOR (Loaded every session)`  
   `└── AGENTS.md (≤ 100 lines)`  
       `├── Mission & non-negotiable invariants (3-5 bullet points)`  
       `├── Environment & verification commands (build, test, lint)`  
       `└── Pointers to active skills and docs index`

`2. PROCEDURAL RUNBOOKS (Loaded on demand)`  
   `└── .agents/skills/<task>/SKILL.md (10-30 lines each)`  
       `└── Step-by-step recipe for specific tasks (e.g., compile-deck, add-parser)`

`3. EXECUTABLE CONTRACTS & INVARIANTS (Enforced automatically)`  
   `├── Code Schemas (src/contracts/*.py or *.ts)`  
   `└── Invariant Test Suite (tests/contracts/test_*_invariants.py)`

`4. GENERATED NAVIGATION (Auto-built on commit/CI)`  
   `└── docs/INDEX.md (Auto-generated map of files, skills, and accepted ADRs)`

### **Why this satisfies all constraints:**

> * **Clarity:** The agent knows immediately where to look (AGENTS.md \\to specific Skill or Schema).  
> * **Discoverability:** AGENTS.md and INDEX.md provide deterministic pathways without directory guessing.  
> * **Canonical Truth:** Invariants are enforced by tests, not prose.  
> * **Low Maintenance:** There are zero duplicate rule files; indexes are auto-generated; procedural skills are short and isolated.  
> * **Agent Usability:** Root context is protected from token bloat, ensuring maximum reasoning capacity and zero hallucinations during code generation.