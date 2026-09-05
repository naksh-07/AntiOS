# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 83–86 Native Antigravity Orchestration & Workforce Architecture
**Class**: NATIVE_ORCHESTRATION | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED_AND_VERIFIED
**Version**: 2.0.0-TEAMWORK-GRADE | **Mode**: OPERATIONAL
**Active Subsystem**: Workforce Contract, Adaptive Planner, Wave Orchestrator, Hybrid Matrix

## 1. Active Checklist
- [x] Phase 83: Native Workforce Contract (`workforce_contract.py`, 11-step pipeline, anti-emulation)
- [x] Phase 84: Adaptive Workforce Planner (`orchestration.py`, 12 inputs, token-bounded cost card)
- [x] Phase 85: Teamwork Waves & Anti-Hydra (`orchestration.py`, persistence & recovery engines)
- [x] Phase 86: 8-Tier Hybrid Capability Matrix (`tool_policy.py`, 7-field MCP escalation protocol)
- [x] Comprehensive Test Suites: 6 test modules, 49 new tests, 10 adversarial vectors, 9 proving scenarios
- [x] Full Regression Suite Pass (733/733 tests pass in 25.3s on `tests/run_all.py`, 0 failures)
- [x] Architecture Docs & ADRs 66–69 Synchronized (`WORKFORCE_CONTRACT.md`, `ORCHESTRATION_MODEL.md`)
- [x] Wave 4: Independent Maker-Checker Audit (`antios-verifier` PASS)

## 2. Blockers & Invariants
- Invariant: `AntiOS orchestrates Antigravity, not AntiOS rebuilds Antigravity`.
- Invariant: Constitutional Limits: Max 10 active/wave, Max 20 lifetime launches, Shallow Depth $\le 2$.
- Invariant: Mandatory Wave Collapse: `NEXT_WAVE` blocked while active total $\ne 0$.
- Invariant: Local Git CLI strictly preferred over GitHub MCP for local status/diff/log.
- Invariant: Active Context strictly bounded $\le 60$ lines.

## 3. Changed Files & Verification State
- Core: `workforce_contract.py`, `orchestration.py`, `tool.py`, `tool_policy.py`, `dispatch.py`, `__init__.py`
- Skills: `.agents/skills/antios/SKILL.md`, `framework/templates/skills/antios/SKILL.md`
- Tests: `test_workforce_contract.py`, `test_workforce_planner.py`, `test_teamwork_wave_orchestration.py`, `test_hybrid_capability_matrix.py`, `test_orchestration_phase83_86_adversarial.py`, `test_proving_ground_scenarios.py`, `run_all.py` (733/733 passing)
- Docs: `WORKFORCE_CONTRACT.md`, `ORCHESTRATION_MODEL.md`, `DECISION_REGISTER.md` (ADRs 66–69), `README.md`
- Verdict: PASS (All 733 tests pass cleanly with 0 failures)

## 4. Dead-End Memory & Validated Lessons
- `WorkerMetadata.goal` and `purpose` must be synchronized in both directions for legacy test compatibility.
- In `AdaptiveWorkforcePlanner`, `DELEGATION_MANDATORY` in `execution_decision` routes to `FOCUSED` when non-parallel.
- In `HybridCapabilityExecutionMatrix`, `available_skills` must sort by length descending to prevent substring collisions (`antios` vs `antios-engineer`).

## 5. Next Immediate Action
Phases 83–86 fully complete and verified. Ready for next 89→99 milestone.
