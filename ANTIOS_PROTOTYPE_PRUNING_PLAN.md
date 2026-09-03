# AntiOS Prototype Pruning Plan (`ANTIOS_PROTOTYPE_PRUNING_PLAN.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Cleanse the repository of dead files, redundant documentation, foreign project contamination, and fake verification paths, establishing a disciplined baseline for AntiOS v1.

---

## 1. Pruning Policy & Principles

1. **Never Delete Research Evidence**: Research reports, test results, and empirical logs from Phases 6–10 must be preserved in dedicated historical archives (`reports/` or `research/phases/`).
2. **Eliminate Dual Truth**: No document should exist simultaneously in multiple active directories.
3. **Excise Insecure Mechanisms**: Any mechanism that allows test fabrication (e.g., `verify_task.py`) or silent bypass must be completely deleted from active scripts.
4. **Remove Foreign Contamination**: References to external projects (e.g., `Anki-maths`) must be removed from sandbox configurations.
5. **Establish Platform Discovery**: Skills and hooks must be located where Antigravity actually discovers them (`<workspace_root>/.agents/`).

---

## 2. Item-by-Item Pruning Disposition

| Target File / Path | Current Status | Disposition | Target Location / Action | Rationale |
| :--- | :--- | :---: | :--- | :--- |
| **`AGENT_VS_AGENT_ADVERSARIAL_RESULTS.md`** (Root) | Exact duplicate (5,455 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Eliminates dual-truth token waste and grep confusion. |
| **`ANTIOS_FAILURE_TAXONOMY.md`** (Root) | Exact duplicate (8,108 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/` as Phase 9 reference. |
| **`PHASE_9_ATTACK_MATRIX.md`** (Root) | Exact duplicate (8,986 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/`. |
| **`PHASE_9_REPORT.md`** (Root) | Exact duplicate (16,774 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/`. |
| **`RECOVERY_TEST_REPORT.md`** (Root) | Exact duplicate (5,963 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/`. |
| **`SECURITY_ADVERSARIAL_REPORT.md`** (Root) | Exact duplicate (6,924 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/`. |
| **`VERIFICATION_ADVERSARIAL_REPORT.md`** (Root) | Exact duplicate (6,350 B) | **`DELETE`** | Delete from root; canonical copy in `reports/` | Preserved in `reports/`. |
| **`PHASE_10_REPORTS.zip`** (Root) | Binary ZIP archive (38,379 B) | **`ARCHIVE`** | Move to `reports/archive/` or delete redundant zip | Working tree should contain clean source files, not redundant zips. |
| **`PROTOTYPE_IMPLEMENTATION.md`** (Root) | Phase 7 scratch notes | **`ARCHIVE`** | Move to `reports/prototype/` | Historical artifact from Phase 7. |
| **`PROTOTYPE_OPEN_ISSUES.md`** (Root) | Phase 7 issue notes | **`ARCHIVE`** | Move to `reports/prototype/` | Historical artifact from Phase 7. |
| **`PROTOTYPE_TEST_RESULTS.md`** (Root) | Phase 7 trial log | **`ARCHIVE`** | Move to `reports/prototype/` | Historical artifact from Phase 7. |
| **`EXPERIMENT_BASELINE.md`** (Root) | Phase 7 scratch notes | **`ARCHIVE`** | Move to `reports/prototype/` | Historical artifact from Phase 7. |
| **`evidence/`** (Root directory) | Empty directory (0 bytes) | **`DELETE`** | Remove directory | Cryptographic receipts rejected; empty folder creates confusion. |
| **`sandbox/StudyLab_Treatment/.agents/sentinel/`** | Dead foreign artifacts | **`DELETE`** | Delete entire sentinel directory | Contains foreign references to `Anki-maths`. |
| **`verify_task.py` fallback in `stop_gate.py`** | Insecure script execution | **`DELETE`** | Excise lines 58–69 from `stop_gate.py` | Eliminates test forgery vulnerability (`sys.exit(0)`). |
| **`studylab-task-runner` Skill** | Undiscoverable in `framework/` | **`REWRITE`** | Author new `antios-engineer` in `.agents/skills/` | Relocates to workspace root for Antigravity discovery; fixes `research` subagent bug. |
| **`framework/.agents/hooks.json`** | Undiscoverable in `framework/` | **`REWRITE`** | Author canonical `.agents/hooks.json` in root | Connects root workspace to hardened AntiOS hooks. |
| **`docs/ACTIVE_CONTEXT.md`** | Stale context frozen at v0.1 | **`REWRITE`** | Synchronize with active Phase 11 state | Eliminates stale-state amnesia for resuming agents. |
| **`docs/AGENTS.md`** | Passive constitution | **`REWRITE`** | Restructure into canonical AntiOS v1 constitution | Clear, enforceable directives within token budget. |

---

## 3. Pruning Execution Steps

1. Delete the 7 byte-identical duplicate reports from root workspace (verify `reports/` holds intact copies first).
2. Remove `evidence/` directory.
3. Clean foreign contamination from `sandbox/StudyLab_Treatment/.agents/sentinel/`.
4. Relocate historical prototype logs (`PROTOTYPE_*.md`, `EXPERIMENT_BASELINE.md`) into `reports/prototype/`.
5. Excise `verify_task.py` lines from `stop_gate.py`.
6. Establish root `.agents/skills/` and `.agents/hooks.json`.
