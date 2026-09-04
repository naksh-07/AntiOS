# AntiOS Phase 31–33 Capability Matrix (`docs/PHASE31_33_CAPABILITY_MATRIX.md`)

**Version**: 3.0.0  
**Status**: CANONICAL CAPABILITY DISPOSITION  
**Phase**: Phase 31–33 (Project Capability Layer)  

---

## 1. Capability Layer Matrix

| Capability / Pillar | Physical Location | Scope | Verification Status |
| :--- | :--- | :---: | :--- |
| **Capability Domain Models** | `framework/core/capability.py` | Universal Core | 100% Verified (7 unit tests) |
| **Canonical Capability Registry** | `framework/core/capability_registry.py` | Universal Core | 100% Verified (5 unit tests) |
| **Task-to-Capability Router** | `framework/core/capability_router.py` | Universal Core | 100% Verified (11 unit tests) |
| **Capability Pack Model & Formatter** | `framework/core/capability_pack.py` | Universal Core | 100% Verified (5 unit tests) |
| **Progressive Capability Disclosure** | `framework/core/knowledge.py` | Universal Core | 100% Verified (L0–L5) |
| **Wayfinding Engine Integration** | `framework/core/wayfinding.py` | Universal Core | 100% Verified |
| **Adapter Capabilities Policy** | `framework/core/config.py`, `adapter.py` | Project Adapter | 100% Verified |
| **Wayfinding CLI (`--task`, `--json`)** | `framework/scripts/tools/navigate_repo.py` | Universal CLI | 100% Verified |
| **Golden Task Test Suite** | `tests/test_golden_tasks.py` | Test Harness | 100% Verified (6 golden scenarios) |
| **Adversarial & Failure Matrix** | `tests/test_capability_adversarial.py` | Test Harness | 100% Verified (7 attack vectors) |
| **Performance Benchmarks** | `tests/test_capability_benchmark.py` | Test Harness | 100% Verified (< 15ms target) |

---

## 2. Capability Disposition Summary

- **IMPLEMENTED (Phase 31–33)**:
  - 8-tier canonical capability model (`SKILL`, `RULE`, `WORKFLOW`, `TOOL`, `VERIFIER`, `SPECIALIST`, `EXTERNAL_PROVIDER`, `MCP_PROVIDER`).
  - 5-rank rule precedence hierarchy with conflict detection.
  - Deterministic task intent classifier with keyword & verb analysis.
  - Multi-tier progressive capability disclosure (L0–L5).
  - Negative applicability filtering.
  - MCP 3-tier selection policy evaluation.
  - 6 golden tasks proving relevance and context filtering.
- **DEFERRED (Phase 34–36)**:
  - Autonomous dynamic skill synthesis.
  - Automatic specialist agent swarm orchestration.
  - Continuous runtime self-mutation.
