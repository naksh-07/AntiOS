# SINGLE IDEA CATALOG — PHASE 5 PRIOR-ART RESEARCH

## Overview & Executive Ledger
This catalog consolidates the forensic findings across all investigated architectural ideas in **Phase 5: Single-Idea Forensic Inspection**. Each candidate idea was extracted from original implementations, reverse-engineered at the source level, verified against exact commit SHAs, and evaluated against the specific domain constraints of **StudyLab** (an agent-native engineering framework for a mathematics-focused Anki learning platform).

### Evaluation Legend
- 🟢 **Adopt Candidate**: High value, low accidental complexity, directly solves verified StudyLab failure modes.
- 🧪 **Requires Experiment**: High conceptual promise, but requires an isolated empirical spike before adoption.
- ⚠️ **Adapt Candidate**: Valuable core idea, but original implementation is encumbered by excessive complexity or requires domain translation.
- ❌ **Reject**: Brittle implementation, high maintenance burden, low agent value, or creates dangerous false confidence.

---

## 1. Master Architectural Primitives Catalog

| ID | Architectural Primitive | Source Repository & Commit | Why Interesting | Complexity | StudyLab Fit | Test? | Adoption Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **IDEA-01** | **Deterministic Repository Governance** | `artreimus/software-factory-starter`<br/>(`73caae5`) | Strict 4-way artifact partitioning (`specs/`, `plans/`, `docs/`, `.agents/skills/`) enforced by a deterministic CI Python oracle (`validate_factory.py`) and a canonical contract (`AGENTS.md`). Eliminates agent folder ambiguity and configuration rot. | LOW | HIGH | 🟢 | **ADOPT CANDIDATE** (Artifact Boundaries & CI Oracle) |
| **IDEA-02** | **RPAC Lifecycle & Maker-Checker Verifier** | `affectionatec/agentic-engineering`<br/>(`b44562c`) | Independent verifier sub-agent running with fresh context without seeing maker's internal reasoning; frozen acceptance criteria; non-negotiable test ratchet ("suite count only goes up"). Crushes maker-checker collusion. | MEDIUM | HIGH | 🧪 | **ADAPT CANDIDATE** (Streamline 10 skills into 4 core phases) |
| **IDEA-03** | **Static Blast-Radius & Dependency Reachability** | `RavByte-AI/agent-memory-system`<br/>(`1f72872`) | Answers *"Can an agent know what else might break before modifying a file?"* via reverse-index BFS reachability. **Implementation Warning:** Uses brittle regexes, leaves symbol tracking empty, and fails on path aliases. | MEDIUM | MEDIUM | 🧪 | **REJECT Implementation** / **ADAPT Concept** (Curriculum Prereq Graph) |
| **IDEA-04** | **Cryptographically Chained Execution Receipts** | `agent-receipts/obsigna`<br/>(`a53ffae`)<br/>*(Comp: `realalonw/agent-receipts`)* | Externalized observation via tool-boundary hooks (`PostToolUse`); records pre/post filesystem hashes, canonical JSON parameter hashes, and Ed25519 hash-chaining. Transforms agent claims ("I finished") into verifiable proof. | MEDIUM | HIGH | 🧪 | **ADAPT CANDIDATE** (Adopt hash-chain + state hashes; reject VC daemon) |
| **IDEA-05** | **Bounded Memory Bank & Spec Lifecycle** | `GregorBiswanger/featherspec`<br/>(`a978e23`) | Zero-dependency 3-tier memory bank (`.memory-bank/`, `.specs/`); strict line budgets (~200 lines for constitution, ~60 lines for active context); frozen immutable plan archive (`plan-archive/`); "Same Change Set" rule. | LOW | HIGH | 🟢 | **ADOPT CANDIDATE** (Direct adoption of bounded memory & change set law) |
| **IDEA-06** | **Tool-Boundary Policy Gating (Hard Gates)** | `fangkangmi/agent-harness`<br/>(`b6ff1a7`) | Intercepts tool calls *before* execution (`PreToolUse` exit code 2 / deny) with structural AST diffs; physically blocks forbidden edits; one-shot cross-agent plan validation. Distinguishes hard gates from advisory nudges. | LOW | HIGH | 🟢 | **ADOPT CANDIDATE** (Adopt PreToolUse exit 2 gates & one-shot plan review) |
| **IDEA-07** | **Multi-Layer Documentation Drift Detection** | `Arthur920/Staleguard`<br/>(`c055748`)<br/>*(Comp: `driftee-ai/drift`)* | Detects documentation-reality drift across 3 layers: Layer 1 (deterministic file path, CLI target, symbol resolution, and Mermaid import checks in ~1.2s with 0 false positives); Layer 2/3 (advisory semantic NLI). | LOW-MED | HIGH | 🟢 | **ADOPT CANDIDATE** (Adopt Layer 1 deterministic core; reject heavy ML in CI) |

---

## 2. Definitive Idea Ranking

The 7 investigated architectural primitives are ranked below according to an objective multi-variable scoring model:
- **StudyLab Relevance**: Alignment with math card authoring, curriculum graphs, LaTeX rendering, and Anki SQLite/apkg generation.
- **Agent Reliability Improvement**: Measurable reduction in agent hallucinations, boundary violations, and silent breakages.
- **Evidence Strength**: Depth of inspected source code, test pass rates, and empirical verification.
- **Simplicity**: Low line-count, minimal dependencies, and clear mental model.
- **Testability**: Feasibility of automated, deterministic offline verification in CI.
- **Maintenance Cost**: Ongoing operational overhead imposed on human developers.

### Comprehensive Ranking Matrix

| Rank | Idea ID | Architectural Primitive | Relevance (1-5) | Reliability Δ (1-5) | Evidence (1-5) | Simplicity (1-5) | Testability (1-5) | Maint. Cost (Inv 1-5) | Composite Score | Tier |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **IDEA-01** | Deterministic Repository Governance | 5 | 5 | 5 | 5 | 5 | 5 | **30 / 30** | Top Candidate |
| **2** | **IDEA-06** | Tool-Boundary Policy Gating (Hard Gates) | 5 | 5 | 5 | 5 | 5 | 5 | **30 / 30** | Top Candidate |
| **3** | **IDEA-05** | Bounded Memory Bank & Spec Lifecycle | 5 | 4 | 5 | 5 | 4 | 5 | **28 / 30** | Top Candidate |
| **4** | **IDEA-02** | RPAC Lifecycle & Independent Verifier | 5 | 5 | 5 | 3 | 4 | 4 | **26 / 30** | Experiment Spike |
| **5** | **IDEA-07** | Multi-Layer Documentation Drift (Layer 1) | 4 | 4 | 5 | 4 | 5 | 4 | **26 / 30** | Experiment Spike |
| **6** | **IDEA-04** | Execution Receipts (Externalized State Hash) | 4 | 5 | 4 | 3 | 4 | 3 | **23 / 30** | Experiment Spike |
| **7** | **IDEA-03** | Static Blast Radius & Dependency Graph | 3 | 2 | 2 | 2 | 2 | 2 | **13 / 30** | Reject Impl / Adapt |

---

## 3. Top Ideas Worth Experimenting With

### 1. `IDEA-01` + `IDEA-05`: The Bounded Governance & Spec Memory Foundation
- **Why It Matters**: Autonomous agents flounder when context windows are flooded with arbitrary documentation or ambiguous task folders. Combining `software-factory-starter`'s 4-way boundary (`specs/`, `plans/`, `docs/`, `.agents/skills/`) and CI validation oracle with `featherspec`'s strict line budgets (~200 lines for constitution, ~60 lines for `activeContext.md`) and immutable plan archives provides a bulletproof operational container with zero external dependencies.
- **Experiment Scope**: Define a minimal `scripts/validate_workspace.py` and test whether agent sessions can maintain context across 5 consecutive card-generation tasks without context corruption or directory clutter.

### 2. `IDEA-06`: Tool-Boundary Policy Gating (`PreToolUse` Hard Interception)
- **Why It Matters**: Prompt-based behavioral rules fail under reasoning stress. `fangkangmi/agent-harness` proves that returning exit code `2` from a pre-tool hook physically cancels tool execution, preserves disk state, and forces self-correction via stderr.
- **Experiment Scope**: Implement a lightweight Python pre-tool script that checks modified Markdown/TS files for StudyLab-specific invariants (e.g. valid LaTeX math delimiters `$...$` / `$$...$$`, valid cloze formatting `{{c1::...}}`, forbidden raw SQLite writes). Test if agent recovers in-place.

### 3. `IDEA-02` + `IDEA-04`: Streamlined RPAC Lifecycle with State-Hashed Evidence Receipts
- **Why It Matters**: The maker-checker pattern (`affectionatec/agentic-engineering`) prevents agents from approving their own flawed work. Pairing this with `agent-receipts`' state commitments (`before_hash` and `after_hash` over output Anki packages or test files) gives human maintainers and automated CI oracles mathematically verifiable proof of completion without re-running long generation jobs.
- **Experiment Scope**: Run a dual-agent trial (Generator Agent + Fresh-Context Verifier Subagent). Measure if the verifier catches deliberately injected math inaccuracies or malformed cloze tags that the generator overlooked.

### 4. `IDEA-07`: Deterministic Layer 1 Documentation Drift Detection
- **Why It Matters**: Complex LLM-based documentation reviewers (`driftee-ai/drift`) are expensive, slow, and hallucinate false negatives. `Arthur920/Staleguard` proves that a simple deterministic scanner checking quoted file paths, config command targets, and symbol existence executes in milliseconds with zero false alarms.
- **Experiment Scope**: Build a ~150-line deterministic documentation auditor that verifies all paths cited in `AGENTS.md`, `specs/`, and `docs/` exist on disk, failing CI if an agent deletes or renames a referenced asset without updating documentation.

---

## 4. Ideas We Should Probably NOT Build

### 1. The Regular-Expression "AST" Graph Engine (`RavByte-AI/agent-memory-system`)
- **Reason to Reject**:
  - The implementation advertises AST analysis but relies on heuristic regexes that fail on multi-line imports, dynamic imports, and path aliases (`@/components`).
  - Symbol tracking is hollow (`symbols: []`), causing breaking-change detection to report 0 affected files in real code.
  - The function call graph is completely unpopulated (`calledBy` is dead code).
  - An inaccurate dependency graph creates **false confidence**, which is far more dangerous to an agent than having no graph at all.
- **What to do instead**: If code dependency analysis is needed in StudyLab, use the official TypeScript Compiler API or Python `ast` module. For curriculum and learning science, model relationships as an explicit **Curriculum & Theorem Prerequisite DAG** in YAML/JSON.

### 2. Out-of-Process Background Daemons & W3C Verifiable Credentials (`obsigna-daemon`)
- **Reason to Reject**:
  - `obsigna` requires a persistent background daemon, Unix domain socket / named pipe IPC, OS peer credential resolution, and full W3C Verifiable Credential v2.0 envelope packaging.
  - This architecture is designed for enterprise compliance and multi-tenant security gateways. For StudyLab, running an external daemon adds significant installation friction, platform-specific IPC bugs on Windows, and massive maintenance overhead.
- **What to do instead**: Keep the **cryptographic state hash and hash-chain concept**, but implement it as a zero-dependency in-process script called by CI or git pre-commit hooks.

### 3. Pure LLM-Centric Documentation Reviewers (`driftee-ai/drift`)
- **Reason to Reject**:
  - Concatenating documentation and source code into an LLM context on every PR costs $0.10–$0.50 per commit, takes 30–60 seconds, and suffers from non-deterministic evaluations.
  - It generates false-positive alerts on stylistic changes, causing developers to disable the gate.
- **What to do instead**: Use deterministic Layer 1 syntactic checks (validating cited paths, commands, and code symbols) in CI. Restrict LLM semantic verification strictly to high-value diff audits when architectural specs change.

### 4. Sprawling 10-Skill Operational Splintering (`affectionatec/agentic-engineering`)
- **Reason to Reject**:
  - Decomposing the dev loop into 10 separate markdown skills (`refine`, `plan`, `act`, `consolidate`, `status`, `adr`, `verify`, etc.) creates high cognitive load, burns tokens reloading skill files, and results in context thrashing for simple tasks.
- **What to do instead**: Condense the lifecycle into **four concise, cohesive phases** (Refine, Plan, Act, Consolidate) integrated into the core framework.

---

## 5. Conceptual Complexity Tax Analysis

For each candidate idea, the table below balances raw conceptual value against implementation complexity, ongoing maintenance, and failure risk:

$$\text{Net Utility} = \frac{\text{Value to Agent Reliability} \times \text{Human Maintainability}}{\text{Implementation Complexity} \times \text{Failure / Hallucination Risk}}$$

| Idea | Value | Implementation Complexity | Ongoing Maintenance | Failure / Flakiness Risk | Net Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **01 — Repository Governance** | VERY HIGH | LOW (Simple folder rules + Python check) | VERY LOW | NONE (Deterministic) | **Massive positive return. Essential foundation.** |
| **02 — RPAC Lifecycle** | HIGH | MEDIUM (Subagent orchestration + prompt design) | LOW-MED | LOW (Controlled by test ratchet) | **High positive return. Solves self-review bias.** |
| **03 — Regex Blast Radius** | LOW | HIGH (Parsing ASTs, maintaining graph cache) | HIGH (Breaks on new syntax) | CRITICAL (False confidence & unpopulated symbols) | **Negative net utility. Accidental complexity.** |
| **04 — Execution Receipts** | HIGH | MEDIUM (Hashing + canonical JSON) | LOW (Deterministic scripts) | LOW (Deterministic math) | **Positive return if daemon/VC bloat is stripped.** |
| **05 — Spec Memory Bank** | VERY HIGH | VERY LOW (Zero-dep Markdown conventions) | LOW (Hard line limits prevent bloat) | VERY LOW (Easy to inspect and roll back) | **Massive positive return. Solves amnesia cleanly.** |
| **06 — Hard Policy Hooks** | VERY HIGH | LOW (Shell/Python scripts with exit code 2) | LOW (Directly scriptable) | VERY LOW (Fails closed on error) | **Massive positive return. True enforcement.** |
| **07 — Doc Drift Layer 1** | HIGH | LOW-MED (Regex/AST path & target checker) | LOW (Only updates on doc schema changes) | VERY LOW (Zero false alarms on exact paths) | **High positive return. Keeps documentation trustworthy.** |

---

## 6. Cross-Idea Synergies & Reinforcement Loops

The investigated ideas do not operate in isolation. When combined thoughtfully, they form powerful self-reinforcing loops that amplify agent reliability:

```text
               ┌────────────────────────────────────────────────────────┐
               │    01: Deterministic Governance + 05: Memory Bank      │
               │ (Strict folder boundaries, line budgets, active spec)   │
               └───────────────────────────┬────────────────────────────┘
                                           │ Dispatches scoped task
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │            02: RPAC (Refine → Plan → Act)              │
               │  (Atomic plan slice, frozen acceptance tests)          │
               └───────────────────────────┬────────────────────────────┘
                                           │ Executes mutations
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │           06: Hard Tool-Boundary Policy Hooks          │
               │ (PreToolUse exit 2 physically blocks invalid math/SQL) │
               └───────────────────────────┬────────────────────────────┘
                                           │ Captures state changes
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │         04: Cryptographic Execution Receipts           │
               │    (before_hash, after_hash, parameter commitments)    │
               └───────────────────────────┬────────────────────────────┘
                                           │ Handoff to fresh-context
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │       02: Independent Verifier + 07: Drift Check       │
               │  (Fresh-eyes subagent runs test ratchet + doc checks)  │
               └───────────────────────────┬────────────────────────────┘
                                           │ Consolidates into git commit
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │         05: "Same Change Set" Documentation Law        │
               │ (Code + Anki Decks + Memory Bank updated in one commit)│
               └────────────────────────────────────────────────────────┘
```

### Verified Synergistic Multipliers:
1. **Governance (01) + Memory Bank (05)**: Eliminates "where do I put this?" confusion. `AGENTS.md` acts as the constitution, while `.memory-bank/activeContext.md` bounds session RAM.
2. **Policy Hooks (06) + RPAC Execution (02)**: Prevents the agent from writing invalid code *during* the Act phase, so the Verifier during Consolidation evaluates clean candidates rather than debugging syntax crashes.
3. **Receipts (04) + Independent Verifier (02)**: The Verifier subagent does not need to re-execute long generation scripts; it inspects the cryptographic receipt slip and verifies the output hashes in $O(1)$ time.
4. **"Same Change Set" Law (05) + Layer 1 Drift Check (07)**: Featherspec's rule that documentation must move in the same commit as code is mechanically enforced by Staleguard's Layer 1 CI check, guaranteeing that documentation never rots.
