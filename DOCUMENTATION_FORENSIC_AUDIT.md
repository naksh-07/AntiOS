# AntiOS Documentation Forensic Audit (`DOCUMENTATION_FORENSIC_AUDIT.md`)

**Date**: 2026-09-03  
**Auditor**: AntiOS Forensic Audit Team  
**Scope**: All architecture documents, decision records, constitution files, task-state files, skill instructions, and reports across `AntiOs/`.  
**Objective**: Uncover contradictions, stale references, nonexistent paths, duplicate truth, and unclear authority across the documentation corpus.

---

## 1. Executive Summary

AntiOS documentation is severely degraded by **documentation drift, redundant file duplication, dead directory paths, and contradictory specifications**. While early documents established clear architectural concepts, subsequent phases added ad-hoc reports without pruning obsolete requirements or keeping working-set memory synchronized.

```text
DOCUMENTATION CORPUS HEALTH
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ Metric                               │ Observed Value                       │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ Total Markdown Documents in Root     │ 19 files                             │
│ Total Reports in reports/            │ 15 files                             │
│ Identical Duplicate Files            │ 7 exact duplicates (54,582 bytes)    │
│ Stale / Obsolete Requirements        │ 4 major architectural conflicts      │
│ Dead File / Path References          │ 5 broken paths in hooks/skills       │
│ Missing Core Files                   │ README.md missing, rules/ missing    │
│ Active Context Health                │ 100% STALE (Frozen at Phase 6)       │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. The Duplicate Truth Register

Seven major Phase 9 forensic reports exist simultaneously in **both the repository root and `reports/`**. SHA-256 digests prove they are byte-for-byte identical duplicates:

| File Name | Root Size | `reports/` Size | SHA-256 Digest Match | Recommendation |
| :--- | :---: | :---: | :---: | :--- |
| `AGENT_VS_AGENT_ADVERSARIAL_RESULTS.md` | 5,455 B | 5,455 B | **MATCH** | Delete from root; retain in `reports/` |
| `ANTIOS_FAILURE_TAXONOMY.md` | 8,108 B | 8,108 B | **MATCH** | Retain in root as active framework reference; delete from `reports/` |
| `PHASE_9_ATTACK_MATRIX.md` | 8,986 B | 8,986 B | **MATCH** | Delete from root; retain in `reports/` |
| `PHASE_9_REPORT.md` | 16,774 B | 16,774 B | **MATCH** | Delete from root; retain in `reports/` |
| `RECOVERY_TEST_REPORT.md` | 5,963 B | 5,963 B | **MATCH** | Delete from root; retain in `reports/` |
| `SECURITY_ADVERSARIAL_REPORT.md` | 6,924 B | 6,924 B | **MATCH** | Delete from root; retain in `reports/` |
| `VERIFICATION_ADVERSARIAL_REPORT.md` | 6,350 B | 6,350 B | **MATCH** | Delete from root; retain in `reports/` |
| `PHASE_9_REPORTS.zip` | 28,044 B | N/A | **REDUNDANT** | Delete archive from root |

**Impact**: Causes confusion about which directory is authoritative. Agents performing grep searches receive double matches on every query, saturating context tokens.

---

## 3. Major Architectural Contradictions

### A. The StudySourceCore MCP Contradiction
- **Source A (`FRAMEWORK_REQUIREMENTS.md:L8`)**:
  > *"FR3: MCP Integration: AntiOS must define configurations to connect Antigravity agents to the `studysource-core` MCP server for deterministic execution of domain tasks..."*
- **Source B (`DECISION_REGISTER.md:L60` & `ARCHITECTURE_PROPOSAL.md:L53`)**:
  > *"AntiOS Schema Validators: [DISPROVED]. Validation of domain artifacts is the responsibility of StudyLab's native tooling. AntiOS only orchestrates execution."*
- **Source C (Active User Instruction)**:
  > *"STUDYSOURCECORE: Completely OUT OF SCOPE. Do not inspect, clone, modify, integrate, investigate, reuse, redesign StudySourceCore."*
- **Forensic Finding**: `FRAMEWORK_REQUIREMENTS.md` was never updated to reflect Decision 5/Phase 8 update. It still mandates integration of a server that is strictly out of scope and architecturally disproved.

### B. The `verify_task.py` Test Fallback Contradiction
- **Source A (`studylab-task-runner/SKILL.md:L30-31`)**:
  > *"Instruction: Ask the subagent to independently run the test suite or `verify_task.py`..."*
- **Source B (`PHASE_8_REPORT.md:L22` & `DECISION_REGISTER.md:L58`)**:
  > *"What was removed? Hardcoded `verify_task.py` dependency."*
- **Source C (`stop_gate.py:L58-69`)**:
  > The code still contains lines 58–69 executing `verify_task.py` as a fallback!
- **Forensic Finding**: While Phase 8 and Phase 9 reports claimed `verify_task.py` was removed due to test fabrication risks, the skill instruction still promotes it, and `stop_gate.py` still executes it.

### C. The Hook Shell Enforcement Contradiction
- **Source A (`DECISION_REGISTER.md:L41`)**:
  > *"If an agent tries to execute a dangerous shell command, the hook exits with non-zero status, the platform blocks the tool, and the agent must correct its approach."*
- **Source B (`framework/.agents/hooks.json:L5`)**:
  > `"matcher": "write_to_file|replace_file_content"`
- **Source C (`SECURITY_ADVERSARIAL_REPORT.md:L80-92`)**:
  > Proves `run_command` shell execution completely bypasses hooks and mutates files without resistance.
- **Forensic Finding**: `DECISION_REGISTER.md` asserts an impossible capability. Antigravity IDE hooks intercept tool calls, not raw shell command strings.

### D. The Active Phase Contradiction
- **Source A (`docs/ACTIVE_CONTEXT.md:L6`)**:
  > *"Phase: Framework Setup"* (with `- [ ] Implement safety hooks`).
- **Source B (`PHASE_9_REPORT.md:L244`)**:
  > *"Phase 9 complete. Phase 10: Controlled StudyLab Production Pilot."*
- **Forensic Finding**: The working memory file is completely disconnected from project reality.

---

## 4. Stale References & Dead Paths

1. **`studylab-task-runner/SKILL.md:L15` $\to$ Dead Context Files**:
   - Skill instructs: *"Consult the `docs/AGENTS.md` and `docs/ACTIVE_CONTEXT.md` files to understand current constraints..."*
   - Reality: When the agent works inside `sandbox/StudyLab/`, neither file exists.
2. **`sandbox/StudyLab/.agents/hooks.json` $\to$ Nonexistent Hook Script**:
   - `hooks.json` specifies: `"command": "python ./scripts/hooks/pre_tool_guard.py"`
   - Reality: `sandbox/StudyLab/scripts/hooks/` does NOT exist! The hook runner crashes with path not found.
3. **`framework/.agents/hooks.json` $\to$ Relative Path CWD Mismatch**:
   - Specifies `"command": "python ./scripts/hooks/pre_tool_guard.py"`.
   - Reality: In the root workspace, the path is `./framework/scripts/hooks/`.
4. **`sandbox/StudyLab_Treatment/.agents/sentinel/BRIEFING.md` $\to$ Foreign Path Contamination**:
   - Contains hardcoded references to `c:\Users\Suraj\Documents\Antigravity\Anki-maths\...`.
   - Reality: `Anki-maths` is an external repository that does not exist in this environment.

---

## 5. Missing Core Documentation

1. **Root `README.md`**:
   - The workspace root has no `README.md`. A newcomer or fresh agent has no entry point explaining how to initialize or run AntiOS.
2. **Platform Rules (`.agents/rules/`)**:
   - Zero directory-based rules exist. All behavioral rules are buried in `docs/AGENTS.md`.
3. **Environment & Tooling Prerequisites**:
   - No documentation specifies that Python 3.11, Node/Vitest, and PowerShell are required.

---

## 6. Authority & Governance Recommendations

1. **Prune Duplicates**: Delete all 7 duplicate report files from the root workspace; retain them exclusively in `reports/`.
2. **Archive Stale Specifications**: Update `FRAMEWORK_REQUIREMENTS.md` to prune disproved MCP requirements and mark them as historical.
3. **Synchronize `docs/ACTIVE_CONTEXT.md`**: Overwrite with current Phase 10 status.
4. **Author Root `README.md`**: Create an authoritative entry point linking directly to `ARCHITECTURE_PROPOSAL.md`, `DECISION_REGISTER.md`, and `reports/`.
