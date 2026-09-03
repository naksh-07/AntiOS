# ANTIOS FRAMEWORK REQUIREMENTS

This document outlines the concrete requirements AntiOS must satisfy to function as a reliable engineering operating layer on top of Google Antigravity for the StudyLab project.

## 1. FUNCTIONAL REQUIREMENTS
- **FR1: Bounded Memory Bank:** AntiOS must provide a standardized set of markdown files (e.g., `AGENTS.md`, `ACTIVE_CONTEXT.md`) that serve as the persistent, externalized memory for agents, bypassing the limitations of in-turn context windows.
- **FR2: Progressive Skill Disclosure:** AntiOS must package complex workflows (e.g., `studylab-test-runner`, `apkg-packager`) as discrete Antigravity Skills to leverage the platform's lazy-loading prompt architecture.
- **FR3: MCP Integration:** AntiOS must define configurations to connect Antigravity agents to the `studysource-core` MCP server for deterministic execution of domain tasks (e.g., `validate_artifact`, `export_anki_package`).
- **FR4: Documentation Synchronization:** AntiOS must require that documentation updates occur within the same change set as code modifications (The "Same Change Set" rule).

## 2. NON-FUNCTIONAL REQUIREMENTS
- **NFR1: Minimalism (No Reinvention):** AntiOS must not duplicate any mechanism natively provided by Antigravity (e.g., subagent spawning, timer daemons, artifact rendering).
- **NFR2: Performance (Token Efficiency):** AntiOS rules and memory banks must adhere to strict line/token budgets (e.g., Global Constitution $\le 200$ lines, Active Context $\le 60$ lines) to prevent context saturation.
- **NFR3: Transparency:** AntiOS execution state and verification results must be fully visible to human operators via standard markdown files and artifacts.

## 3. SAFETY REQUIREMENTS
- **SR1: Hard Policy Gating:** AntiOS must implement deterministic `PreToolUse` hooks (via `hooks.json`) to physically intercept and block unauthorized file modifications or unsafe commands before execution.
- **SR2: Domain Invariant Protection:** AntiOS hooks and rules must strictly protect the StudyLab Source → APKG contract (e.g., preventing modification of the 20-field schema by LLM hallucination).
- **SR3: Upstream Protection:** AntiOS must forbid and block agents from modifying upstream Anki core files (`rslib/src/collection/`, etc.) without explicit, structured human authorization.

## 4. VERIFICATION REQUIREMENTS
- **VR1: Independent Verification (Maker-Checker):** Critical implementation tasks must be verified by a freshly spawned subagent (the checker) that shares no context with the implementing agent (the maker).
- **VR2: Test Ratcheting:** Agents must not bypass, skip, or delete existing automated tests. Test coverage must remain stable or increase.
- **VR3: Stop Gating (Completion Oracle):** AntiOS must implement a `Stop` hook that executes critical test suites and blocks the agent from declaring victory if any tests fail.

## 5. RECOVERY REQUIREMENTS
- **RR1: Dead-End Logging:** Failed hypotheses and approaches must be documented in a persistent log (e.g., `dead-ends.md` or equivalent artifact) to prevent subsequent agents or retries from repeating the same mistakes.
- **RR2: Granular Resumption:** Task state must be tracked at a granular level (e.g., in a checklist artifact) so that if an agent crashes or context is lost, a new agent can resume exactly where the previous one left off.

## 6. MAINTAINABILITY & PORTABILITY REQUIREMENTS
- **MR1: Single Unified Runtime:** Core orchestrator tools and hooks must be built in a unified, cross-platform runtime (e.g., Python) rather than maintaining dual-stack Bash/PowerShell scripts.
- **MR2: Deterministic Reference Auditing (Layer 1):** Documentation references to files and symbols must be auditable via fast, deterministic Layer-1 scripts to detect syntactic drift without relying on slow, expensive LLMs.
