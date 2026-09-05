# AntiOS Master Source of Truth (`ANTIOS_SOURCE_OF_TRUTH.md`)

**Date**: 2026-09-04  
**Status**: Canonical Master Source of Truth & Precedence Hierarchy (Phases 1–42 Consolidated)  
**Objective**: Establish the single authoritative source of truth for every architectural, operational, and governance dimension of AntiOS, eliminating dual-truth risks, documentation drift, and authority fragmentation.

---

## 1. Single Authority Governance Law

> *"Every architectural fact, operational rule, or system boundary MUST have exactly one authoritative source of truth.*  
> *If two documents disagree, the higher authority level prevails unconditionally.*  
> *No secondary document may redefine or contradict a primary canonical authority.*  
> *Physical code and passing automated tests outrank stale historical prose."*

---

## 2. Canonical Authority Map

| Architectural Domain | Canonical Source of Truth | Location / File Path | Authority Level | Precedence When Conflicting |
| :--- | :--- | :--- | :---: | :--- |
| **Engineering Invariants & Constitution** | AntiOS Master Constitution | `ANTIOS_CONSTITUTION.md` | **CONSTITUTION** | Highest architectural policy; defines invariants, boundaries, and immutable rules. |
| **System Architecture** | AntiOS Master Architecture Specification | `ANTIOS_V1.md` | **PRIMARY SPEC** | Comprehensive system specification: 4-tier model, 7 subsystems, 63 core modules. |
| **Project Agent OS Architecture** | AntiOS 2.0 Project Agent OS Specification | `docs/architecture/PROJECT_AGENT_OS.md` | **PRIMARY SPEC** | Compilation contract, 5-tier ownership, 6-phase lifecycle, and orchestration limits. |
| **Adaptive Mission Orchestration** | AntiOS Adaptive Orchestration Model | `docs/architecture/ORCHESTRATION_MODEL.md` | **PRIMARY SPEC** | Adaptive workforce sizing (SOLO to MAX), wave lifecycle, dual dispatch gates, resource ledger. |
| **Primary Skill Control Plane** | AntiOS Primary Skill Architecture | `docs/architecture/ANTIOS_SKILL_MODEL.md` | **PRIMARY SPEC** | Authoritative control plane specification for `/antios` skill and progressive disclosure. |
| **Project Agent OS Manifest** | Project Agent OS Manifest | `.antios/manifest.json` | **INSTANCE METADATA** | Cryptographic provenance, artifact ownership records, and lifecycle state. |
| **Architectural Consensus & Decisions** | AntiOS Master Decision Register | `DECISION_REGISTER.md` | **DECISION RECORD** | Authoritative consensus log (Decisions 01–76) recording why decisions were made. |
| **Evidence Architecture** | AntiOS Evidence Architecture Specification | `docs/architecture/EVIDENCE_ARCHITECTURE.md` | **PRIMARY SPEC** | Authoritative epistemic separation, 6 evidence states, and bounded packaging. |
| **Mission Evaluation Engine** | AntiOS Mission Evaluation Specification | `docs/architecture/MISSION_EVALUATION.md` | **PRIMARY SPEC** | 11-dimension deterministic evaluation, 4 statuses, and Maker-Checker enforcement. |
| **Agent-Native Mission Benchmark** | AntiOS Mission Benchmark Specification | `docs/architecture/MISSION_BENCHMARK.md` | **PRIMARY SPEC** | Workflow quality benchmark, Baseline vs AntiOS comparison, and proving grounds A–J. |
| **Capability Inventory & Layering** | AntiOS Capability Matrix | `docs/architecture/CAPABILITY_MATRIX.md` | **CAPABILITY MATRIX** | Authoritative 18-layer capability disposition across all 807 certified tests. |
| **Project Instance Runtime & Closure** | Instance Runtime & Closure Contract | `framework/core/runtime_contract.py` / `.antios/runtime/` | **RUNTIME CLOSURE** | Self-contained instance execution, PreToolUse and Stop gates, and closure contract. |
| **Formal System Certification** | AntiOS Formal Certification Matrix | `docs/architecture/CERTIFICATION_MATRIX.md` | **CERTIFICATION LEDGER** | Complete verification ledger across all 50 capability dimensions. |
| **Core vs Adapter Contract** | Core vs Project Adapter Specification | `docs/architecture/CORE_VS_ADAPTER.md` | **BOUNDARY CONTRACT** | Strict demarcation between universal Core logic and declarative project adapters. |
| **Safety Boundaries & Path Protection** | Pre-Tool Guard Hook Implementation | `framework/scripts/hooks/pre_tool_guard.py` | **CODE / RUNTIME** | Physical Python script is authoritative over any prompt or documentation text. |
| **Task Completion & Verification Gate** | Stop Gate Hook Implementation | `framework/scripts/hooks/stop_gate.py` | **CODE / RUNTIME** | Physical subprocess exit code overrides conversational claims and subagent reports. |
| **Active Task State & Working Set** | Bounded Working Context | `docs/ACTIVE_CONTEXT.md` | **ACTIVE MEMORY** | Authoritative for the current session's immediate tasks, blockers, and next action (<= 60 lines). |
| **Tool, Provider & MCP Architecture** | AntiOS Tool, Provider & MCP Policy | `docs/reference/MCP_POLICY.md` | **PRIMARY SPEC** | Authoritative for 8-tier hybrid capability matrix, provider abstractions, and MCP escalation. |
| **Hook Registration & Mounts** | Platform Hook Manifest | `.agents/hooks.json` | **PLATFORM BINDING** | Connects Antigravity tool events to AntiOS hook scripts. |
| **Declarative Project Adapter** | Project Adapter Configuration | `antios.config.json` | **PROJECT CONFIG** | Declares project test runners, linters, protected zones, and topology overrides. |
| **Historical Evidence & Research** | Reports & Archive Directories | `reports/archive/` | **HISTORICAL ARCHIVE** | Read-only evidence ledger. Never used as active task state or current specification. |

---

## 3. Strict Precedence Hierarchy

When an agent encounters conflicting signals across tools, files, or prompts, it MUST resolve precedence in this exact, immutable order:

```text
Rank 1: Deterministic Hook Process Execution (pre_tool_guard.py, stop_gate.py)
        +-- Physical OS process exit code. Cannot be overridden by any prompt or file.

Rank 2: Explicit Human User Directive
        +-- Active conversational mandate. Overrides passive documentation.

Rank 3: Git Commit Log & Working Tree Status (git status, git diff)
        +-- Physical filesystem reality on disk. Overrides markdown memory.

Rank 4: Master Engineering Constitution (ANTIOS_CONSTITUTION.md)
        +-- Foundational project invariants, protected zones, and boundary rules.

Rank 5: Master Architecture Specification (ANTIOS_V1.md)
        +-- Canonical system blueprint. Overrides older subsystem proposals.

Rank 6: Master Decision Register (DECISION_REGISTER.md)
        +-- Recorded consensus (Decisions 01–65). Overrides informal proposals.

Rank 7: Active Engineering Skills (.agents/skills/*)
        +-- Progressive procedural workflows. Overrides generic prompting.

Rank 8: Active Working Memory (docs/ACTIVE_CONTEXT.md)
        +-- Ephemeral task tracking. Must yield to all higher layers if out of sync.
```
