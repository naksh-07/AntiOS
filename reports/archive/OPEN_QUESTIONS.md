# ANTIOS OPEN QUESTIONS

The following questions remain unresolved after the Phase 6 Architectural Synthesis and must be answered through experimental validation during Prototype v0.1 testing or later phases.

## 1. Persistent Memory & Task State Formatting
- **Question:** What is the optimal format and density for the Bounded Memory Bank (e.g., `ACTIVE_CONTEXT.md`)?
- **Context:** We know we need file-backed memory, but we do not know if agents handle YAML, concise bullet points, or structured paragraphs better when rapidly updating context.
- **Validation Plan:** Experiment with different memory formats during Prototype v0.1 tasks and measure context retention and token consumption.

## 2. Blast-Radius Analysis Efficacy
- **Question:** Can a deterministic script reliably calculate the pedagogical or code-level "blast radius" of a change in StudyLab without relying on fragile regex-based AST parsers?
- **Context:** Prior art (IDEA-03) showed regex-based dependency graphs create false confidence.
- **Validation Plan:** Prototype a Curriculum Prerequisite Graph using strict metadata/imports and test if an agent can use it to correctly identify all downstream affected cards.

## 3. Hook Enforcement Friction
- **Question:** Do strict `PreToolUse` hooks cause agent "death loops" (where the agent repeatedly tries the same blocked command and fails), or do they successfully force in-turn self-correction?
- **Context:** Hard gating is necessary, but we must ensure it doesn't break the agent's ability to recover.
- **Validation Plan:** Intentionally trigger the safety hook during a prototype task and observe the agent's retry logic and escalation paths.

## 4. Multi-Agent Coordination Overhead
- **Question:** At what task complexity does the overhead of dispatching a subagent outweigh the benefits of independent verification or parallel work?
- **Context:** Dispatching subagents consumes launches and token budgets. Shallow hierarchies (Depth $\le 2$) are mandated, but the exact threshold for "when to split" is fuzzy.
- **Validation Plan:** Run identical StudyLab tasks in `SOLO` mode vs. `MAKER-CHECKER` mode and compare token costs, wall-clock time, and final output quality.

## 5. Execution Receipts & Evidence Depth
- **Question:** Should execution receipts (e.g., SHA-256 hashes of pre/post states) be stored as transient artifacts, committed directly to Git, or discarded after the `Stop` hook validates them?
- **Context:** IDEA-04 proved cryptographic state hashing works, but storing full W3C verifiable credentials is too heavy.
- **Validation Plan:** Implement a simple transient receipt system during v0.1 and evaluate if it actually aids the Verifier agent in its audit.

## 6. MCP Protocol Limits
- **Question:** Are there payload size limitations or latency bottlenecks when passing large StudyLab procedural database schemas or batch artifact validations over the local stdio MCP transport?
- **Context:** `studysource-core` uses MCP for deterministic validation. Large payloads might stress the stdio bridge.
- **Validation Plan:** Benchmark `validate_artifact` over MCP with a massive Anki deck (1000+ cards) during prototype testing.
