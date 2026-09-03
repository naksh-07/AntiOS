# PHASE 6 SYNTHESIS: ANTIOS ARCHITECTURE

This synthesis report concludes Phase 6 by answering the ten core architectural questions derived from the forensic research corpus.

## 1. What is AntiOS?
AntiOS is the *engineering operating layer* residing within the StudyLab repository. It is a curated collection of progressive skills, deterministic policy hooks, bounded memory bank files, and behavioral rules. It provides the structure that allows autonomous agents to safely and reliably interact with the StudyLab codebase.

## 2. What problem does it solve?
Agents operating in bare repositories suffer from context amnesia, confirmation bias during self-review, and a tendency to rationalize away prompt-based safety instructions, leading to corrupted domain contracts (like StudyLab's 20-field source schema) or broken builds. AntiOS solves this by externalizing memory, enforcing hard code-level boundaries, and mandating independent verification.

## 3. What does Antigravity already provide?
Antigravity (the Platform) natively provides the execution mechanisms:
- Segregated subagent execution (`invoke_subagent`).
- Tool interception engine (`PreToolUse`, `Stop` hooks).
- Artifact storage and UI rendering.
- MCP client transport.
- Immutable transcript logging (`transcript.jsonl`).
- Background scheduling.

## 4. What must AntiOS provide?
AntiOS (the Project Policy) must provide the domain-specific constraints:
- The actual Python hook scripts that evaluate safety and test success.
- The `AGENTS.md` constitution and Bounded Memory Bank structures.
- The progressive domain skills (e.g., `studylab-task-runner`).
- The workforce coordination policy (when to spawn an independent verifier).

## 5. What architecture is currently recommended?
A composite architecture consisting of **Skills + Rules + Hooks + MCP + Project Documentation**.
We explicitly reject building a single monolithic "AntiOS Skill" because true domain safety requires hard deterministic hooks, and true context management requires persistent file-backed documentation.

## 6. Why this architecture?
It aligns perfectly with the proven "Mechanism vs. Policy Demarcation". It leverages Google Antigravity's highly optimized platform primitives without rebuilding them, while utilizing the four consensus pillars of robust agent engineering: Externalized State, Progressive Disclosure, Independent Verification, and Hard Guardrails.

## 7. What enters Prototype v0.1?
The absolute minimum viable system to prove the architecture:
- A Bounded Memory Bank (`AGENTS.md`, `ACTIVE_CONTEXT.md`).
- A `PreToolUse` hook blocking writes to upstream Anki core.
- A `Stop` hook blocking termination if tests fail.
- Integration of the `studysource-core` MCP server.
- One orchestrator skill utilizing a fresh-eyes verifier subagent.

## 8. What is deliberately excluded?
- Heavyweight cryptographic execution receipts (W3C verifiable credentials).
- Pure LLM-based documentation drift checkers.
- Regex-based AST dependency parsers.
- Any custom agent runners or background IPC daemons.
- Large swarms (>2 agents).

## 9. What remains unknown?
- The optimal format and density for the Bounded Memory Bank (YAML vs. bullet points).
- The exact friction and recovery rate when an agent hits a hard `PreToolUse` hook block.
- The token overhead of dispatching independent verifier subagents on smaller tasks.

## 10. How will Prototype v0.1 prove or disprove the architecture?
Phase 7 will execute a controlled A/B experiment in a disposable Git sandbox. An agent will be tasked with fixing a seeded bug and updating documentation under two conditions: CONTROL (raw Antigravity) and TREATMENT (Antigravity + AntiOS v0.1). By measuring task success, blast-radius containment, and verification quality, we will empirically prove if AntiOS makes agents genuinely more reliable, verifiable, and maintainable.
