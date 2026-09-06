# AntiOS Master Constitution (`ANTIOS_CONSTITUTION.md`)

**Date**: 2026-09-05  
**Status**: Master Engineering Invariants (Universal Baseline & AntiOS 2.0 Foundation)  
**Objective**: Establish the canonical project constitution, defining the engineering invariants, boundary placement laws, orchestration bounds, and immutable rules governing all autonomous agent operations within AntiOS repositories.

---

## 1. The Rule-to-Enforcement Mapping Principle

> *"Prompt rules without code-level enforcement are soft guidelines that LLMs routinely rationalize away during complex multi-step reasoning.*  
> *Conversely, hooks cannot perform fuzzy semantic evaluations requiring human or LLM judgment."*

Therefore, AntiOS establishes a strict **Enforcement Placement Law**:

```text
┌─────────────────────────┬──────────────────────────────────────────────────┐
│ LAYER                   │ APPROPRIATE GOVERNANCE RESPONSIBILITY            │
├─────────────────────────┼──────────────────────────────────────────────────┤
│ DETERMINISTIC HOOKS     │ Hard boundaries, path immutability, test exit 0, │
│ (Python Process Code)   │ hook self-protection. Zero tolerance for bypass. │
├─────────────────────────┼──────────────────────────────────────────────────┤
│ CONSTITUTION (AGENTS.md)│ High-level architectural orientation, risk       │
│ (Prompt Directives)     │ tiering awareness, cognitive rules, boundaries.  │
├─────────────────────────┼──────────────────────────────────────────────────┤
│ SKILLS (SKILL.md)       │ Step-by-step engineering procedures, delegation  │
│ (Progressive Workflows) │ templates, tool command idioms.                  │
├─────────────────────────┼──────────────────────────────────────────────────┤
│ DOCUMENTATION           │ In-depth rationale, architecture diagrams,       │
│ (Reference Docs)        │ historical evidence, design alternatives.        │
└─────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 2. The Ten Constitutional Invariants

Every agent operating in an AntiOS repository is bound by ten immutable invariants:

1. **Platform Sovereignty**: If Google Antigravity natively provides an orchestration, execution, scheduling, or logging primitive -> **USE THE PLATFORM**. Never reimplement native mechanisms.
2. **Protected Zones Immutability**: Governance zones (`.agents/`, `framework/`, `antios.config.json`) and configured upstream protected domain paths are strictly immutable. Mutating actions are blocked fail-closed.
3. **Toolchain Ground Truth**: If a native compiler, type checker, or test framework provides verification -> **USE THE NATIVE TOOLCHAIN**. Never forge test results or replace compilers with brittle regex parsers.
4. **Physical Stop Gate Ratchet**: An agent **cannot conclude** a task turn unless all physical test processes exit with returncode 0. Conversational self-certification ("Looks Good to Me") is rejected.
5. **Same Change Set Policy**: Source code modifications and corresponding documentation/test updates must be delivered in the same change set. Code without tests or docs is rejected.
6. **Shallow Depth Law**: Subagent nesting depth is strictly bounded to <= 2 (Parent -> Child). Recursive agent swarms are strictly prohibited.
7. **Wave Budget & Resource Bounds**: Concurrent active subagents are bounded to <= 10 per wave; total lifetime subagent launches are bounded to <= 20 per mission.
8. **Mandatory Wave Collapse**: Every dispatched wave must be consolidated and collapsed to 0 active subagents before launching a subsequent wave (`WAVE -> CONSOLIDATE -> COLLAPSE -> NEXT WAVE`).
9. **Bounded Working Context**: Operational task state in `docs/ACTIVE_CONTEXT.md` is strictly bounded to <= 60 lines to eliminate context saturation and amnesia.
10. **4-Boundary Demarcation**: AntiOS compiler and lifecycle engines must preserve boundary separation: `SOURCE ≠ INSTANCE`, `INSTANCE ≠ PROJECT`, `PROJECT ≠ ANTIGRAVITY`. Target application code and user-owned skills are sovereign and immutable.

---

## 3. What Belongs in `docs/AGENTS.md` (Global Constitution Entrypoint)

- **Token Budget**: Strictly <= 40 lines. Bounded, pointer-oriented orientation.
- **Content**: Directs the agent to:
  - The 4 Architectural Axioms (Platform vs Core vs Adapter vs Target).
  - The 10 Constitutional Invariants (Protected zones, test exit 0, Same Change Set, bounded context, orchestration bounds).
  - Pointers to canonical architecture (`ANTIOS_ARCHITECTURE.md`, `ANTIOS_OPERATING_MODEL.md`, `ANTIOS_V1.md`) and operational state (`docs/ACTIVE_CONTEXT.md`).
