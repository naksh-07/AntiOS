# AntiOS Skill Architecture Specification (`ANTIOS_SKILL_ARCHITECTURE.md`)

**Date**: 2026-09-04  
**Status**: Canonical Skill Architecture Specification (Phases 1–42 Consolidated)  
**Objective**: Define a discoverable, progressive, non-redundant skill system that injects genuine project engineering governance without duplicating native Antigravity platform mechanisms.

---

## 1. Core Architectural Principles for AntiOS Skills

1. **Root Discoverability**: All active skills reside in `<workspace_root>/.agents/skills/<skill-name>/SKILL.md`.
2. **Lean & Non-Redundant**: Skills must NEVER duplicate platform behaviors (e.g. instructing an agent how to make an implementation plan). They exclusively teach **non-native project policies**:
   - Risk classification (when to dispatch a verifier).
   - Verifier dispatch idioms (`TypeName='self'`, physical test commands).
   - Invariant boundaries (protected zones immutability, Same Change Set).
   - Stop gate awareness (how the physical test ratchet works).
3. **Token Efficiency Budget**: Every `SKILL.md` must be strictly $\le 60$ lines to eliminate context saturation upon activation.
4. **Focused Responsibilities**: 4 canonical skills provide full engineering lifecycle coverage across any software stack.

---

## 2. Canonical Skill Inventory

### 2.1 `antios-engineer` (Universal Engineering Workflow)
- **Path**: `.agents/skills/antios-engineer/SKILL.md` (39 lines)
- **Role**: Primary engineering workflow policy for projects under AntiOS governance.
- **Capabilities**: Injects the 10-stage lifecycle, 3-tier risk matrix (Low, Med, High), Maker-Checker dispatch rules, boundary immutability, and Same Change Set discipline.

### 2.2 `antios-verifier` (Independent Audit Contract)
- **Path**: `.agents/skills/antios-verifier/SKILL.md` (52 lines)
- **Role**: Independent verification and audit contract for Maker-Checker subagents.
- **Capabilities**: Injects the fresh-context Checker contract, working tree diff inspection, physical test execution, boundary compliance auditing, and structured JSON verdict reporting.

### 2.3 `antios-debug` (Root-Cause Debugging)
- **Path**: `.agents/skills/antios-debug/SKILL.md` (37 lines)
- **Role**: Systematic root-cause debugging procedure.
- **Capabilities**: Injects deterministic 5-step debugging (Reproduce -> Isolate -> Hypothesize -> Fix -> Prevent), dead-end logging, and regression test ratification.

### 2.4 `antios-adapt-project` (Universal Project Adaptation)
- **Path**: `.agents/skills/antios-adapt-project/SKILL.md` (38 lines)
- **Role**: Universal project intelligence and adaptation procedure.
- **Capabilities**: Guides discovery of unfamiliar repositories, audits existing guidance, generates declarative `AdaptationProposal` schemas, and populates `antios.config.json` with zero Core code mutation.
