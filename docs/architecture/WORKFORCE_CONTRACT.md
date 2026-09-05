# WORKFORCE_CONTRACT: AntiOS 2.0 Native Workforce Contract & Responsibility Demarcation

## 1. Overview & Purpose

The **Native Workforce Contract** (AntiOS 2.0, Phase 83) establishes the formal constitutional boundary between **AntiOS Governance** and the native **Antigravity Execution Substrate**.

AntiOS operates as an intelligent control plane over the native Antigravity environment, **never** as a competing agent runtime, duplicate daemon, or bespoke workflow engine:
> *AntiOS orchestrates Antigravity; AntiOS does not rebuild Antigravity.*

---

## 2. Canonical Responsibility Demarcation

| Engineering Responsibility | Authoritative Owner | Governing Invariant | Anti-Pattern Forbidden |
| :--- | :--- | :--- | :--- |
| **User Intent Clarification** | **AntiOS** | Formalizes intent, constraints, and non-goals. | Unconstrained conversational assumptions. |
| **Task Classification** | **AntiOS** | Categorizes `TaskClass` (BUG, FEATURE, REFACTOR, etc.) and `RiskTier`. | Homogeneous feature handling. |
| **Project Intelligence** | **AntiOS** | Indexes anatomy, components, epistemic state, and boundaries. | Dynamic full-repo prompt scraping. |
| **Capability Selection** | **AntiOS** | Deterministically resolves skills, rules, and tools across 8 tiers. | Blindly enabling all tools or defaulting to MCP. |
| **Risk Analysis & Gates** | **AntiOS** | Enforces Dual Dispatch Gates, Pre-Tool Guard, and Stop Gate exit 0. | Bypassing verification via LLM assertions. |
| **Workforce Planning** | **AntiOS** | 12-input evaluation sizing workforce mode (SOLO to MAX) with cost card. | Spawning maximum agent swarms by default. |
| **Delegation Policy** | **AntiOS** | Shallow Depth Law ($\le 2$); leaf specialists cannot delegate. | Unbounded recursive agent trees. |
| **Evidence Requirements** | **AntiOS** | Grounded `StructuredHandoff` with concrete files, lines, and commands. | Conversational "Looks Good To Me" handoffs. |
| **Verification Governance** | **AntiOS** | Maker-Checker separation and independent physical verification. | Self-certification by primary author. |
| **Memory & Learning** | **AntiOS** | Distills durable lessons; maintains active context ($\le 60$ lines). | Unfiltered prompt context pollution. |
| **Agent Execution Runtime** | **Antigravity** | Platform LLM inference loop, turn management, and reasoning tokens. | AntiOS emulating custom LLM loops/agent brokers. |
| **Skill Discovery & Loading**| **Antigravity** | Native `SKILL.md` parsing, YAML frontmatter, and activation. | AntiOS maintaining custom skill daemons. |
| **Subagent Lifecycle** | **Antigravity** | Native `invoke_subagent`, `manage_subagents`, and background tasks. | AntiOS spawning raw OS processes/threads. |
| **Tool Execution Transport** | **Antigravity** | Native `view_file`, `write_to_file`, `run_command`, `grep_search`, etc. | AntiOS mutating files via raw sockets. |
| **MCP Transport** | **Antigravity** | Native JSON-RPC / MCP client protocol connections. | AntiOS implementing raw external network sockets. |
| **CLI Execution Sandbox** | **Antigravity** | Native `run_command` with paging and security boundaries. | AntiOS executing unmonitored background subprocesses. |
| **Context & Sessions** | **Antigravity** | Platform context windows, transcripts, and event serialization. | AntiOS attempting to hijack platform context. |
| **Background Execution** | **Antigravity** | Native non-blocking background tasks and reactive wakeup. | AntiOS running `while True: sleep()` polling loops. |

---

## 3. Canonical 11-Step Capability Execution Hierarchy

Execution in AntiOS follows a strictly ordered, non-inverting 11-step pipeline:

```
[01: USER REQUEST]
       │
       ▼
[02: CONTROL PLANE (/antios)]
       │
       ▼
[03: MISSION UNDERSTANDING]
       │
       ▼
[04: PROJECT INTELLIGENCE]
       │
       ▼
[05: CAPABILITY SELECTION]
       │
       ▼
[06: WORKFORCE PLAN & COST CARD]
       │
       ▼
[07: NATIVE ANTIGRAVITY EXECUTION]
       │
       ▼
[08: SPECIALIST / SUBAGENT DISPATCH]
       │
       ▼
[09: NATIVE TOOL / CLI / MCP EXECUTION]
       │
       ▼
[10: EVIDENCE COLLECTION (StructuredHandoff)]
       │
       ▼
[11: VERIFICATION & DURABLE MEMORY]
```

---

## 4. Anti-Emulation Laws

AntiOS strictly prohibits emulating native platform capabilities:
1. **No Custom Daemons**: AntiOS components never run permanent background daemons.
2. **No Custom Workflow Engines**: Workflows are governed as native Antigravity Skills.
3. **No Agent Broker / Process Substrate**: AntiOS never spawns operating system processes to simulate subagents. All subagents are dispatched exclusively via `invoke_subagent`.
4. **No Polling Loops**: AntiOS utilizes reactive wakeups and scheduled events; no sleep-polling.
5. **No Direct Socket MCP**: All MCP interactions traverse Antigravity native tool definitions.
