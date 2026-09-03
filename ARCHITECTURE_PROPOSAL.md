# ANTIOS ARCHITECTURE PROPOSAL

## 1. Mission
To provide the engineering operating layer that enables Antigravity agents to develop, test, debug, document, audit, maintain, and safely evolve StudyLab. AntiOS defines the policy, structure, and knowledge necessary for agentic reliability, without rebuilding the mechanisms already provided by the Antigravity platform.

## 2. Goals & Non-Goals
**Goals:**
- Guarantee safety and immutability of the StudyLab domain contracts (e.g., Source → APKG contract).
- Eliminate confirmation bias through independent multi-agent verification.
- Provide progressive disclosure of context to prevent context window saturation and amnesia.
- Establish hard deterministic guardrails (code over prompt) to enforce architectural boundaries.
- Maintain durable, file-backed project state (Bounded Memory Bank).

**Non-Goals:**
- Do not rebuild Antigravity primitives (e.g., subagent lifecycle, background scheduling, MCP transport, UI artifact rendering).
- Do not bypass or dynamically dilute StudyLab domain truth or the 20-field source question schema.
- Do not create a monolithic, bloated framework; optimize for a Minimum Viable System.

## 3. System Model & Boundaries

The architecture operates on a strict **Mechanism vs. Policy Demarcation**:

### Antigravity (PLATFORM)
Provides universal execution mechanisms: subagent execution with segregated context, `PreToolUse` and `Stop` hook interception, MCP client transport, persistent JSONL transcripts, and asynchronous background scheduling.

### AntiOS (PROJECT POLICY)
Defines the engineering framework: Hook validation scripts, progressive agent skills, behavioral rules, verification test ratchets, workforce coordination policy, and bounded memory bank structures.

### StudyLab (DOMAIN TRUTH)
Owns mathematical semantics, pedagogical invariants, the double SQLite architecture, telemetry firewall, reviewer FSM, and canonical question contracts.

## 4. Core Components

Based on prior-art consensus and the capability audit, AntiOS is composed of:

1.  **[VALIDATED] The Bounded Memory Bank (Documentation Governance)**:
    - Zero-dependency, markdown-based working memory with strict line budgets.
    - Examples: `AGENTS.md` (Tier 1 Global Rules), `PROJECT_BRIEF.md`, `ACTIVE_CONTEXT.md` (Tier 2 Working Set).
    - Ensures that context is externalized on disk, preventing agent amnesia.

2.  **[VALIDATED] Hard Policy Hooks (Deterministic Enforcement)**:
    - Uses Antigravity's `.agents/hooks.json` to mount `PreToolUse` and `Stop` scripts.
    - Intercepts invalid operations (e.g., malformed LaTeX, editing upstream Anki core, failing tests) *before* execution or task completion. (Path traversal hardened in Phase 8).

3.  **[VALIDATED] Progressive Domain Skills**:
    - Focused skills (`.agents/skills/`) for discrete procedures (e.g., `studylab-test-runner`, `apkg-packager`).
    - Uses Antigravity's native progressive disclosure to inject minimal tokens until activated.

4.  **[PARTIALLY_VALIDATED] Independent Multi-Agent Verification (Maker-Checker)**:
    - Uses native `invoke_subagent` with `TypeName='research'` or `self` to spawn fresh-context verifiers.
    - Eliminates self-grading confirmation bias, but adds latency/token cost. Future tuning required for task sizing.

5.  **[DISPROVED] StudyLab Domain MCP Server (`studysource-core`)**:
    - Exposes strict deterministic tooling for validating artifacts and resolving policies natively over local IPC, bypassing error-prone shell scripting.
    - *Phase 8 Update*: Schema validation was determined to be a redundant abstraction. StudyLab's native domain tools (`generate_apkg.py`) provide self-validation via execution. External GitHub MCP was also rejected in favor of native Git CLI.

## 5. Architecture Selection: Skills + Rules + Hooks + MCP + Documentation

**Decision:** Option C (Skills + Rules + Hooks + MCP + project documentation) is selected over a single monolithic AntiOS Skill.
**Reasoning:**
- A single skill conflates *prompt-level cognitive constraints* with *hard enforcement*. Research proves that LLMs can rationalize away prompt rules.
- True enforcement requires Hooks. True domain tooling requires MCP. True persistent memory requires Documentation. True procedural logic requires Skills. True global constraints require Rules (`AGENTS.md`).
- This composition maps perfectly to the Antigravity capability audit boundaries.

## 6. Task Lifecycle (RPAC-Inspired)
1. **Refine & Plan**: Agent consults Memory Bank, explores codebase, and authors `implementation_plan.md`.
2. **Execute (Act)**: Agent modifies code, governed strictly by `PreToolUse` hooks preventing invariant violations.
3. **Verify**: Parent agent dispatches a fresh-eyes `verifier` subagent to audit changes and run tests.
4. **Consolidate (Stop Gate)**: The `Stop` hook validates that all tests pass and documentation is synchronized (Same Change Set rule) before allowing completion.

## 7. Prototype v0.1 Boundary
Prototype v0.1 will implement a **Minimum Viable System** focusing on:
- A basic Bounded Memory Bank (`AGENTS.md`, `ACTIVE_CONTEXT.md`).
- One `PreToolUse` safety hook to protect the StudyLab domain.
- One `Stop` hook for test verification.
- Integration of the `studysource-core` MCP server.
- One or two focused skills.
- The use of Antigravity's native Planning Mode (`implementation_plan.md`) + fresh-eyes verification.

**Deliberately Excluded from v0.1:**
- Advanced cryptographic state hashing (Receipts).
- Semantic NLI-based documentation drift detection (only Layer 1 syntactic checking will be explored later).
- Massive hierarchical agent swarms (workforce will be capped at 2-3 agents max).
