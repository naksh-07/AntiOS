# AntiOS v1 Directory Structure Map (`ANTIOS_V1_DIRECTORY_MAP.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Define the clean, final repository structure for AntiOS v1, aligning strictly with Antigravity platform discovery conventions, separating active governance from historical research, and eliminating redundant directories.

---

## 1. Master Repository Directory Topology

```text
c:\Users\Suraj\Documents\Antigravity\AntiOs\
│
├── .agents/                                     <── [Active Platform Discovery]
│   ├── hooks.json                               <── Platform hook manifest (PreToolUse & Stop)
│   └── skills/
│       └── antios-engineer/
│           └── SKILL.md                         <── Canonical AntiOS engineering workflow skill
│
├── docs/                                        <── [Active Project Governance & Context]
│   ├── AGENTS.md                                <── Canonical AntiOS v1 Global Constitution
│   └── ACTIVE_CONTEXT.md                        <── Bounded working set memory (≤ 60 lines)
│
├── framework/                                   <── [AntiOS Core Implementation]
│   └── scripts/
│       └── hooks/
│           ├── pre_tool_guard.py                <── Hardened fail-closed PreToolUse guard
│           └── stop_gate.py                     <── Hardened fail-closed Stop verification gate
│
├── reports/                                     <── [Historical Research & Forensic Archives]
│   ├── archive/                                 <── Binary archives (PHASE_10_REPORTS.zip)
│   ├── prototype/                               <── Historical Phase 7 scratch & trial logs
│   ├── AGENT_VS_AGENT_ADVERSARIAL_RESULTS.md   <── Phase 9/10 Adversarial trial results
│   ├── AGENT_VS_AGENT_RESULTS.md                <── Phase 8 Trial results
│   ├── ANTIOS_FAILURE_TAXONOMY.md               <── Phase 9 Failure categorization
│   ├── BEST_IN_BREED_GAP_ANALYSIS.md            <── Phase 8 Prior art benchmark
│   ├── COMPLEXITY_AUDIT.md                      <── Phase 8 Complexity audit
│   ├── MCP_REEVALUATION_REPORT.md               <── Phase 8 MCP audit
│   ├── MEMORY_AND_RECOVERY_REPORT.md            <── Phase 8 Memory audit
│   ├── PHASE_8_REPORT.md                        <── Phase 8 Milestone report
│   ├── PHASE_9_ATTACK_MATRIX.md                 <── Phase 9 Attack vectors (22 vectors)
│   ├── PHASE_9_REPORT.md                        <── Phase 9 Milestone report
│   ├── RECOVERY_TEST_REPORT.md                  <── Phase 9 Recovery trials
│   ├── SECURITY_ADVERSARIAL_REPORT.md           <── Phase 9 Security findings
│   ├── SECURITY_HARDENING_REPORT.md             <── Phase 8 Hardening report
│   ├── VERIFICATION_ADVERSARIAL_REPORT.md       <── Phase 9 Verification audit
│   └── VERIFICATION_HARDENING_REPORT.md         <── Phase 8 Verification report
│
├── sandbox/                                     <── [Isolated Target Workspaces]
│   ├── StudyLab/                                <── Active StudyLab development sandbox
│   ├── StudyLab_Control/                        <── Bare Antigravity benchmark sandbox
│   └── StudyLab_Treatment/                      <── Hardened AntiOS experimental sandbox
│
└── [Core Architecture & Specification Documents]
    ├── ANTIOS_V1.md                             <── Canonical Master Architecture Specification
    ├── ANTIOS_V1_ARCHITECTURE.md                <── Architectural model & boundary specification
    ├── ANTIOS_RESPONSIBILITY_BOUNDARY.md        <── Tripartite responsibility matrix
    ├── ANTIOS_CONSTITUTION.md                   <── Constitutional governance model
    ├── ANTIOS_HOOK_SECURITY_MODEL.md            <── Hook security & fail-closed specifications
    ├── ANTIOS_V1_SECURITY_MODEL.md              <── Comprehensive security & threat model
    ├── ANTIOS_VERIFICATION_MODEL.md             <── Verification hierarchy & test ratchet
    ├── ANTIOS_STATE_MODEL.md                    <── Task state & 3-tier memory model
    ├── ANTIOS_SKILL_ARCHITECTURE.md             <── Skill design & non-redundant scope
    ├── ANTIOS_MCP_POLICY.md                     <── MCP candidate evaluation & Git CLI rules
    ├── ANTIOS_SOURCE_OF_TRUTH.md                <── Master single-source-of-truth matrix
    ├── ANTIOS_REJECTED_ARCHITECTURE.md          <── Ledger of permanently excised components
    ├── ANTIOS_V1_CAPABILITY_DISPOSITION.md      <── 34-capability empirical disposition
    ├── ANTIOS_PROTOTYPE_PRUNING_PLAN.md         <── Inventory of pruned prototype assets
    ├── ANTIOS_V1_FREEZE_REVIEW.md               <── Architecture freeze scorecard & audit
    ├── ANTIOS_V1_IMPLEMENTATION_PLAN.md         <── Implementation roadmap for production
    ├── ANTIOS_V1_DIRECTORY_MAP.md               <── This file
    └── DECISION_REGISTER.md                     <── Authoritative architectural decision record
```

---

## 2. Structural Principles Observed

1. **Native Discovery Compliance**: `.agents/` is positioned at the workspace root so Antigravity natively indexes `hooks.json` and `skills/` upon workspace opening.
2. **Strict Separation of Active vs Historical**: All experimental logs, past phase summaries, and adversarial test data reside in `reports/`, preventing historical reports from contaminating active agent memory.
3. **Zero Redundant Duplication**: Exactly 1 canonical copy of every report and document exists on disk.
4. **No Artificial Directory Bloat**: No empty `evidence/`, no unneeded vector databases, and no speculative multi-agent coordinator folders.
