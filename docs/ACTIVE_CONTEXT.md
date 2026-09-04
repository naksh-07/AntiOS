# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 67–72 Two-Way Adaptation, Capability Gap & Evolution
**Class**: FEATURE_ARCHITECTURE | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED_PASS
**Version**: 2.0.0-PROPOSAL | **Mode**: OPERATIONAL
**Active Subsystem**: Two-Way Adaptation, Capability Gap, Tool Gap, Evolution & Migration

## 1. Active Checklist
- [x] Phase 67: Two-Way Adaptation Contract (`TwoWayAdaptationContract`, `AdaptationSignal`)
- [x] Phase 68: Capability Gap Detection & Lifecycle (`CapabilityGapDetector`, `GapLifecycleEngine`)
- [x] Phase 69: Tool/MCP Gap Analysis (`ToolGapAnalyzer`, 6-tier preference, local git over MCP)
- [x] Phase 70: Structured Capability Proposal Engine (`CapabilityProposalEngine`, `NO_ACTION`)
- [x] Phase 71: Controlled AntiOS Evolution (`ControlledEvolutionGovernor`, snapshot & rollback)
- [x] Phase 72: Compatibility & Migration Contract (`MigrationEngine`, `migrate_instance.py`)
- [x] Full Regression Suite Pass (632/632 tests pass in 30.19s, 0 failures, 0 regressions)
- [x] Architecture Documentation & ADRs 53–58 Synchronized

## 2. Blockers & Invariants
- Invariant: `CORE ≠ ADAPTER` — AntiOS Core (`framework/core/`, constitution) is strictly immutable.
- Invariant: Epistemic Segregation — `AGENT_INFERENCE` alone cannot approve durable changes.
- Invariant: 6-Tier Tool Preference — `NATIVE` > `SCRIPT` > `PROJECT` > `CLI` > `SERVICE` > `MCP`.
- Invariant: Shallow Depth Law (depth <= 2; specialist `can_delegate = False`).
- Invariant: Active Context strictly bounded <= 60 lines.

## 3. Changed Files & Verification State
- Core: `two_way_contract.py`, `capability_gap.py`, `tool_gap.py`, `evolution_proposal.py`, `evolution_governance.py`, `migration.py`, `__init__.py`
- CLI: `framework/scripts/tools/migrate_instance.py`
- Tests: 7 new test modules (61 new tests, 632/632 tests passing on `tests/run_all.py`)
- Docs: `TWO_WAY_ADAPTATION.md`, `CAPABILITY_GAP_MODEL.md`, `EVOLUTION_GOVERNANCE.md`, `COMPATIBILITY_MODEL.md`, `INDEX.md`, `DECISION_REGISTER.md` (ADR 53–58)

## 4. Dead-End Memory & Validated Lessons
- `compute_file_sha256` lives in `framework.core.provenance`, not `manifest`.
- Tier 1 native tool matching must not shadow AntiOS-specific script domain tasks.
- `ProjectManifest` revision properties must be safely bumped without non-existent methods.

## 5. Next Immediate Action
Phases 67–72 fully verified and certified (632/632 passing). Ready for production use.
