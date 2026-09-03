# AntiOS v1 Implementation Plan (`ANTIOS_V1_IMPLEMENTATION_PLAN.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish the sequential, dependency-ordered roadmap for implementing, verifying, and freezing AntiOS v1, minimizing risk and ensuring verifiable engineering progression.

---

## 1. Implementation Phasing by Dependency & Risk

To prevent cascading regressions and maintain rigorous control, implementation is ordered strictly by dependency:

```text
Phase 1: Repository Hygiene & Dead Code Pruning
    │  (Eliminate duplicates, excise insecure fallbacks, clean contamination)
    ▼
Phase 2: Core Hook Security & Fail-Closed Hardening
    │  (Canonicalization, 8.3 alias protection, self-protection, fail-closed)
    ▼
Phase 3: Platform Discovery & Manifest Registration
    │  (Root .agents/hooks.json, python launcher alias bridge)
    ▼
Phase 4: Skill Architecture & Progressive Disclosure
    │  (Discoverable antios-engineer skill in root .agents/skills/)
    ▼
Phase 5: Constitutional & State Layer
    │  (Compact AGENTS.md, synchronized ACTIVE_CONTEXT.md)
    ▼
Phase 6: Verification Model & Ratchet Hardening
    │  (Native test auto-discovery, timeout bounds, environment diagnosis)
    ▼
Phase 7: Governance Documentation & Single Source of Truth
    │  (Master Architecture, Responsibility Boundary, Decision Register)
    ▼
Phase 8: Empirical Verification & Freeze Audit
    │  (Live attack regression testing, freeze review, master ANTIOS_V1.md)
```

---

## 2. Detailed Work Package Breakdown

### Work Package 1: Repository Hygiene & Pruning (COMPLETED)
- **Actions**:
  1. Deleted 7 byte-identical duplicate reports from root workspace (retained canonical copies in `reports/`).
  2. Moved historical Phase 7 scratch files to `reports/prototype/`.
  3. Archived binary zip files to `reports/archive/`.
  4. Removed empty `evidence/` directory.
  5. Purged foreign project contamination (`Anki-maths` references in `sandbox/StudyLab_Treatment/.agents/sentinel/`).
- **Verification**: `list_dir` confirmed zero duplicate report files in root; all historical reports intact in `reports/`.

### Work Package 2: Core Hook Security Hardening (COMPLETED)
- **Actions**:
  1. Rewrote `framework/scripts/hooks/pre_tool_guard.py` to be strictly **Fail-Closed**.
  2. Implemented `os.path.commonpath` prefix matching for `.agents` and `framework/` self-protection, eliminating the `framework` ancestor false-positive lockup.
  3. Added lexical checks blocking Windows 8.3 short names (`rslib~1`, `RSLIB~1`).
  4. Added strict fail-closed handling on empty payloads, missing `workspacePaths`, and malformed types.
- **Verification**: Executed live Python test harness verifying `rslib/` $\to$ deny, `.agents/` $\to$ deny, `framework/` $\to$ deny, `ts/app.ts` $\to$ allow, empty payload $\to$ deny, malformed types $\to$ deny.

### Work Package 3: Platform Discovery & Manifest Registration (COMPLETED)
- **Actions**:
  1. Authored `.agents/hooks.json` in workspace root.
  2. Synchronized `framework/.agents/hooks.json`.
  3. Verified cross-platform launcher bridge for Windows environment (`python` alias to `python3.11`).
- **Verification**: `python --version` confirmed `Python 3.11.16`.

### Work Package 4: Skill Architecture & Progressive Disclosure (COMPLETED)
- **Actions**:
  1. Authored lean, discoverable `antios-engineer` skill at `.agents/skills/antios-engineer/SKILL.md`.
  2. Eliminated duplication with Antigravity native Planning Mode.
  3. Codified risk tiers (Low, Medium, High) and mandated `TypeName='self'` for Maker-Checker verifiers.
- **Verification**: Skill verified for valid YAML frontmatter and concise (<40 lines) token footprint.

### Work Package 5: Constitutional & State Layer (COMPLETED)
- **Actions**:
  1. Updated `docs/AGENTS.md` to canonical AntiOS v1 constitution format ($\le 40$ lines).
  2. Updated `docs/ACTIVE_CONTEXT.md` to reflect active Phase 11 state and tasks ($\le 50$ lines).
- **Verification**: Verified zero contradictory phase claims.

### Work Package 6: Verification Model & Ratchet Hardening (COMPLETED)
- **Actions**:
  1. Rewrote `framework/scripts/hooks/stop_gate.py` with fail-closed semantics and process timeouts (`timeout=60`).
  2. Permanently excised insecure `verify_task.py` fallback.
  3. Added `ENVIRONMENT_UNAVAILABLE` differentiation for missing runner binaries.
- **Verification**: Syntax verified; unit test logic validated.

### Work Package 7: Master Governance Specifications (COMPLETED)
- **Actions**:
  1. Authored `ANTIOS_V1_CAPABILITY_DISPOSITION.md` (34 capabilities classified).
  2. Authored `ANTIOS_PROTOTYPE_PRUNING_PLAN.md`.
  3. Authored `ANTIOS_V1_ARCHITECTURE.md`.
  4. Authored `ANTIOS_RESPONSIBILITY_BOUNDARY.md`.
  5. Authored `ANTIOS_SKILL_ARCHITECTURE.md`.
  6. Authored `ANTIOS_CONSTITUTION.md`.
  7. Authored `ANTIOS_HOOK_SECURITY_MODEL.md`.
  8. Authored `ANTIOS_V1_SECURITY_MODEL.md`.
  9. Authored `ANTIOS_VERIFICATION_MODEL.md`.
  10. Authored `ANTIOS_STATE_MODEL.md`.
  11. Authored `ANTIOS_MCP_POLICY.md`.
  12. Authored `ANTIOS_SOURCE_OF_TRUTH.md`.
  13. Authored `ANTIOS_REJECTED_ARCHITECTURE.md`.
  14. Updated `DECISION_REGISTER.md`.
  15. Authored `ANTIOS_V1_DIRECTORY_MAP.md`.

### Work Package 8: Architecture Freeze & Final V1 Document (PENDING NEXT)
- **Actions**:
  1. Author `ANTIOS_V1_FREEZE_REVIEW.md` (Part 22 & 23: Architecture Self-Review and Freeze Review).
  2. Author canonical master specification `ANTIOS_V1.md` (Part 24).
  3. Execute final verification and author `walkthrough.md`.
  4. Freeze repository; halt without modifying production StudyLab.
