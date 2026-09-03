# AntiOS Universal Engineering Workflows

This directory defines the canonical engineering workflows in AntiOS.
AntiOS strictly separates **HOW** from **WHEN + SEQUENCE**:
- **Skills (`.agents/skills/`)**: HOW (Operational policies, contracts, and safety invariants).
- **Workflows (`.agents/workflows/`)**: WHEN + SEQUENCE (10-step lifecycle progression for distinct task classes).

## Workflow Catalog

| Task Class | Workflow File | Primary Composed Skills | Risk Tier Default |
| :--- | :--- | :--- | :---: |
| **FEATURE** | [`FEATURE.md`](FEATURE.md) | `antios-engineer`, `antios-verifier` | Medium / High |
| **BUG** | [`BUG.md`](BUG.md) | `antios-debug`, `antios-engineer`, `antios-verifier` | Medium |
| **REFACTOR** | [`REFACTOR.md`](REFACTOR.md) | `antios-engineer`, `antios-verifier`, `antios-debug` | High |
| **INVESTIGATION**| [`INVESTIGATION.md`](INVESTIGATION.md) | `antios-engineer` (Read-Only) | Low |
| **DOCUMENTATION**| [`DOCUMENTATION.md`](DOCUMENTATION.md) | `antios-engineer` | Low |
| **RELEASE** | [`RELEASE_MAINTENANCE.md`](RELEASE_MAINTENANCE.md) | `antios-engineer`, `antios-verifier` | High |

## The 10-Step Universal Lifecycle Progression
```text
INTAKE -> UNDERSTAND -> INVESTIGATE -> PLAN -> IMPLEMENT -> TEST -> VERIFY -> REVIEW -> CONSOLIDATE -> COMPLETE
```
