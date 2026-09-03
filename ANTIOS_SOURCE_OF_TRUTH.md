# AntiOS v1 Master Source of Truth (`ANTIOS_SOURCE_OF_TRUTH.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish the single canonical authority for every architectural, operational, and domain dimension of AntiOS, eliminating dual-truth risks, documentation drift, and authority fragmentation.

---

## 1. Single Authority Governance Law

> *"Every architectural fact, operational rule, or system boundary MUST have exactly one authoritative source of truth.*  
> *If two documents disagree, the higher authority level prevails unconditionally.*  
> *No secondary document may redefine or contradict a primary canonical authority."*

---

## 2. Canonical Authority Map

| Architectural Domain | Canonical Source of Truth | Location / File Path | Authority Level | Precedence When Conflicting |
| :--- | :--- | :--- | :---: | :--- |
| **System Architecture** | AntiOS v1 Architecture Specification | `ANTIOS_V1_ARCHITECTURE.md` | **PRIMARY SPEC** | Overrides all historical proposals, synthesis files, and scratch notes. |
| **Architectural Consensus & History** | AntiOS v1 Decision Register | `DECISION_REGISTER.md` | **DECISION RECORD** | Authoritative record of why choices were made and alternatives rejected. |
| **Safety Boundaries & Path Protection** | Pre-Tool Guard Hook Implementation | `framework/scripts/hooks/pre_tool_guard.py` | **CODE / RUNTIME** | The physical Python script is authoritative over any prompt or documentation text. |
| **Task Completion & Verification Gate** | Stop Gate Hook Implementation | `framework/scripts/hooks/stop_gate.py` | **CODE / RUNTIME** | Physical subprocess exit code overrides conversational claims and subagent reports. |
| **Active Task State & Working Set** | Bounded Working Context | `docs/ACTIVE_CONTEXT.md` | **ACTIVE MEMORY** | Authoritative for the current session's immediate tasks, blockers, and next action. |
| **Global Agent Constitution** | Project Constitution | `docs/AGENTS.md` | **CONSTITUTION** | Authoritative for behavioral rules, immutability directives, and Same Change Set policy. |
| **Engineering Procedures & Workflows** | AntiOS Engineering Skill | `.agents/skills/antios-engineer/SKILL.md` | **WORKFLOW SPEC** | Authoritative for Maker-Checker risk tiering and dispatch mechanics. |
| **Hook Registration & Mounts** | Platform Hook Manifest | `.agents/hooks.json` | **PLATFORM BINDING** | Connects Antigravity tool events to AntiOS hook scripts. |
| **StudyLab Domain Truth** | StudyLab Codebase & Contracts | `sandbox/StudyLab/` (Source & Tests) | **DOMAIN CONTRACT** | 20-field schema, reviewer FSM, and double SQLite logic reside exclusively in StudyLab. |
| **Package Generation Truth** | StudyLab Compiler Script | `sandbox/StudyLab/scripts/generate_apkg.py` | **COMPILER CONTRACT**| Authoritative for APKG format compliance. StudySourceCore is 100% out of scope. |
| **Historical Evidence & Research** | Reports & Archive Directories | `reports/` and `reports/archive/` | **HISTORICAL ARCHIVE**| Read-only evidence ledger. Never used as active task state or current specification. |

---

## 3. Strict Precedence Hierarchy

When an agent encounters conflicting signals across tools, files, or prompts, it MUST resolve precedence in this exact, immutable order:

```text
Rank 1: Deterministic Hook Process Execution (pre_tool_guard.py, stop_gate.py)
        └── Physical OS process exit code. Cannot be overridden by any prompt or file.

Rank 2: Explicit Human User Prompt / Directive
        └── Active conversational mandate. Overrides passive documentation.

Rank 3: Git Commit Log & Working Tree Status (git status, git diff)
        └── Physical filesystem reality on disk. Overrides markdown memory.

Rank 4: Master Architecture Specification (ANTIOS_V1_ARCHITECTURE.md)
        └── Canonical system blueprint. Overrides older proposals.

Rank 5: Decision Register (DECISION_REGISTER.md)
        └── Recorded consensus. Overrides speculative or informal proposals.

Rank 6: Active Engineering Skill (.agents/skills/antios-engineer/SKILL.md)
        └── Progressive procedural workflow. Overrides generic prompting.

Rank 7: Active Working Memory (docs/ACTIVE_CONTEXT.md)
        └── Ephemeral task tracking. Must yield to all higher layers if out of sync.
```
