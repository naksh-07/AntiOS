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
7. `BUILD CONTEXT`: Internal `ContextBudgetGovernor` & `FreshnessEvaluator` emitting bounded context card.
8. `EXECUTE`: Dispatch native tools or specialists (`antios-engineer`, `antios-debug`, `antios-adapt-project`).
9. `VERIFY`: Independent Maker-Checker audit (`antios-verifier`) and test suite (exit code 0).
10. `REMEMBER`: Distill durable lessons and refresh active context.

## 3. Adaptive Workforce Sizing & Anti-Hydra Waves (Phases 84–85)
- **Modes**: `SOLO` (0 subagents), `FOCUSED` (1 specialist), `SMALL` (2 specialists), `PARALLEL` (2–4 specialists), `STAGED` (sequential waves), `HIERARCHICAL` (coordinator + 1–2 children), `MAX` (constitutional ceiling).
- **Constitutional Limits**: Max Active Subagents Per Wave: 10. Max Lifetime Launches Per Mission: 20. Shallow Depth Law: $\le 2$. Mandatory Wave Collapse. Read-Parallel, Write-Controlled: Single writer default.

## 4. Capability Matrix & Context Budget Governor (Phases 86–88)
- **Matrix**: 1. Native -> 2. Skill -> 3. Script -> 4. Runtime -> 5. Specialist -> 6. CLI -> 7. Service -> 8. MCP. Local Git CLI over MCP.
- **Context & Freshness**: Classify (`MANDATORY` to `REDUNDANT`), govern (`LOAD` to `REFRESH`), and ground against physical file SHAs.

## 5. Mission State & Evidence Architecture (Phases 89–92)
- **Continuity**: Crash recovery (`RESUME` to `ABORT`) and bounded tool outputs (`RAW`, `RELEVANT`, `SUMMARIZED`, `DISCARDED`).
- **Epistemic Law**: `OBSERVATION ≠ EVIDENCE ≠ VERDICT ≠ INFERENCE ≠ DECISION`. 6 states (`OBSERVED` to `CONFLICTING`).
- **Evaluation & Benchmark**: 11-dimension evaluator (`PASS` to `INCONCLUSIVE`) and agent-native benchmark grounds (Scenarios A–J).

## 6. Durable Proofs, Runtime Drift & Release Certification (Phases 93–95)
- **Durable Proofs (93)**: Epistemic distillation into `ProjectProof` across 13 subjects, 7 states, bounded store ($\le 50$).
- **Runtime Drift & Health (94)**: 10 domains, 7 dimensions, proposal-governed repair. Zero daemons.
- **Release Certification (95)**: 12 dimensions, 5 levels (`CERTIFIED_RELEASE` to `UNKNOWN`), bounded card ($\le 25$ lines).

## 7. Stop Gate & Task Completion
1. Collapse all active workers: `manage_subagents(Action='kill', ...)`.
2. Execute configured test runner (from `antios.config.json`, must exit code 0).
3. Ensure `docs/ACTIVE_CONTEXT.md` is updated and strictly $\le 60$ lines.


