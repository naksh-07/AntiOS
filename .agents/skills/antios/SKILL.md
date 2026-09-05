---
name: antios
description: >-
  Universal project-native control plane under AntiOS 2.0 governance.
  Use when planning, navigating, implementing, debugging, verifying,
  or orchestrating any engineering task in this repository.
---

# AntiOS Project Operating Interface (`/antios`)

You are operating under **AntiOS 2.0 (Project Agent OS)** governance.
This skill is your **single authoritative control plane** (`/antios`). AntiOS coordinates native Antigravity primitives without reimplementing the platform. Helper CLI: `dispatch_task.py`.

## 1. Responsibility Demarcation (Phase 83 Workforce Contract)
- **Platform (Antigravity)**: Owns execution primitives (`invoke_subagent`, `manage_subagents`), tool transport, and workspace branching.
- **AntiOS Core**: Owns governance, boundaries, task dispatch, adaptive planning, anti-hydra validation, and verification gates.
- **Project Adapter (`antios.config.json` / `.antios/`)**: Owns project topology, protected paths, and test runners.
- **Target Project**: Owns application logic, domain schemas, and native test suites.

## 2. Canonical Capability Pipeline Stages
1. `UNDERSTAND`: Parse user intent, acceptance criteria, and non-goals.
2. `CHECK STATE`: Read `.antios/knowledge.json` and `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines).
3. `LOCATE`: Deterministically locate code via project intelligence.
4. `CLASSIFY`: Determine `TaskClass` and `RiskTier`.
5. `SELECT CAPABILITIES`: Resolve 8-tier matrix (Native -> Skill -> Tool -> Runtime -> Specialist -> CLI -> Service -> MCP).
6. `SELECT WORKFORCE`: 12-input `AdaptiveWorkforcePlanner` emitting cost reasoning card.
7. `EXECUTE`: Dispatch native tools or specialists (`antios-engineer`, `antios-debug`, `antios-adapt-project`).
8. `VERIFY`: Independent Maker-Checker audit (`antios-verifier`) and test suite (exit code 0).
9. `REMEMBER`: Distill durable lessons and refresh active context.

## 3. Adaptive Workforce Sizing & Cost Reasoning (Phase 84)
Evaluates 12 inputs to select mode with token-bounded cost card (**Why this**, **Why not fewer**, **Why not more**):
- Modes: `SOLO` (0 subagents), `FOCUSED` (1 specialist), `SMALL` (2 specialists), `PARALLEL` (2–4 specialists), `STAGED` (sequential waves), `HIERARCHICAL` (coordinator + 1–2 children), `MAX` (constitutional ceiling).

## 4. Teamwork-Grade Waves & Anti-Hydra Protection (Phase 85)
- **Constitutional Limits**:
  - Max Active Subagents Per Wave: 10.
  - Max Lifetime Launches Per Mission: 20.
  - Shallow Depth Law: Depth bounded $\le 2$ (`Root=0 -> Child=1 -> Grandchild=2`). Leaf specialists cannot delegate.
  - Mandatory Wave Collapse: `NEXT_WAVE` strictly blocked while `ACTIVE_TOTAL != 0`.
- **Anti-Hydra Specialist Protection**:
  - Valid `WorkerMetadata` required (no anonymous workers).
  - Duplicate specialist roles with identical goals or overlapping write boundaries rejected.
  - Runaway retry limit: Max 2 consecutive failures per role before fail-closed.
  - Wave persistence: `.antios/wave_state.json` saved at each transition for crash recovery.
- **Read-Parallel, Write-Controlled**: Single writer default. Parallel writes require disjoint boundaries (`Workspace='branch'`).

## 5. 8-Tier Capability Matrix & Governed MCP Escalation (Phase 86)
Priority: 1. Native -> 2. Project Skill -> 3. Script -> 4. Runtime -> 5. Specialist -> 6. CLI -> 7. Service -> 8. MCP.
- *Local Git Invariant*: Local Git CLI (Tier 6) is strictly preferred over GitHub MCP (Tier 8) for local operations.
- *MCP Escalation*: Mandatory 7-field report (`capability_sought`, `why_native_failed`, `least_privilege_scope`, `risk_assessment`, `rollback_plan`, `user_approval_required`, `audit_trail_entry`).

## 6. Stop Gate & Task Completion
1. Collapse all active workers: `manage_subagents(Action='kill', ...)`.
2. Execute configured test runner (from `antios.config.json`, must exit code 0).
3. Ensure `docs/ACTIVE_CONTEXT.md` is updated and strictly $\le 60$ lines.
