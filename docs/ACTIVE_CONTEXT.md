# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Current Mission**: Phase 12–13 Architecture Re-baseline & Universal Core Design  
**Date**: 2026-09-04  
**Active State**: Canonical universal architecture baselined (5 core specs authored)  

## 1. Objective
Establish AntiOS as a universal, reusable Agent-Native Engineering OS for Antigravity:
- Demarcate Antigravity Platform vs AntiOS Core vs Project Adapter vs Target Project.
- Decouple generic governance from StudyLab proving ground assumptions.
- Author 5 canonical architectural specifications.

## 2. Active Tasks
- [x] Phase 12–13: Comprehensive codebase & research forensic inspection
- [x] Phase 12–13: Author `ANTIOS_SYSTEM_ARCHITECTURE.md` (4-tier model & shell gap)
- [x] Phase 12–13: Author `ANTIOS_COMPONENT_MODEL.md` (components, contracts, lifecycles)
- [x] Phase 12–13: Author `ANTIOS_CORE_VS_ADAPTER.md` (adapter schema & decoupling plan)
- [x] Phase 12–13: Author `ANTIOS_CAPABILITY_MATRIX.md` (16 layers & capability audit)
- [x] Phase 12–13: Author `ANTIOS_PHASE12_13_REPORT.md` (ADRs, roadmap, risk analysis)
- [x] Phase 12–13: Framework self-test verification (18/18 tests passing in <1.0s)
- [ ] Phase 14: Core Decoupling & Dynamic Manifest Discovery (`framework/core/config.py`)

## 3. Blockers & Constraints
- StudySourceCore is 100% OUT OF SCOPE.
- Production StudyLab code remains completely untouched.
- Subagent Shallow Depth Law: Depth <= 2 strictly enforced.
- Token Budget: Skills <= 60 lines, ACTIVE_CONTEXT <= 60 lines.

## 4. Dead Ends (Do Not Repeat)
- Do NOT build custom AST parsers, schema validators, or vector databases.
- Do NOT use static cryptographic receipts (`evidence/` - Ratchet Expiry).
- Do NOT place skills inside `framework/.agents` (causes discoverability black hole).
- Do NOT fracture skills into 7 micro-skills (causes prompt thrashing).
- Do NOT hardcode domain paths into Core fallback dataclasses.

## 5. Next Immediate Action
Execute Phase 14: Purge residual StudyLab defaults from `framework/core/config.py` and implement dynamic manifest scanning in `framework/core/gate.py`.
