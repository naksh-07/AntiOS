# AntiOS Master Constitution (`ANTIOS_CONSTITUTION.md`)

**Date**: 2026-09-04  
**Status**: Master Engineering Invariants (Universal GA Baseline)  
**Objective**: Establish the canonical project constitution, defining the engineering invariants, boundary placement laws, and immutable rules governing all autonomous agent operations within AntiOS repositories.

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

## 2. The Seven Constitutional Invariants

Every agent operating in an AntiOS repository is bound by seven immutable invariants:

1. **Platform Sovereignty**: If Google Antigravity natively provides an orchestration, execution, scheduling, or logging primitive $	o$ **USE THE PLATFORM**. Never reimplement native mechanisms.
2. **Protected Zones Immutability**: Governance zones (`.agents/`, `framework/`, `antios.config.json`) and configured upstream protected domain paths are strictly immutable. Mutating actions are blocked fail-closed.
3. **Toolchain Ground Truth**: If a native compiler, type checker, or test framework provides verification $	o$ **USE THE NATIVE TOOLCHAIN**. Never forge test results or replace compilers with brittle regex parsers.
4. **Physical Stop Gate Ratchet**: An agent **cannot conclude** a task turn unless all physical test processes exit with returncode 0. Conversational self-certification ("Looks Good to Me") is rejected.
5. **Same Change Set Policy**: Source code modifications and corresponding documentation/test updates must be delivered in the same change set. Code without tests or docs is rejected.
6. **Shallow Depth Law**: Subagent nesting depth is strictly bounded to $\le 2$ ($	ext{Parent} 	o 	ext{Child}$). Recursive agent swarms are strictly prohibited.
7. **Bounded Working Context**: Operational task state in `docs/ACTIVE_CONTEXT.md` is strictly bounded to $\le 60$ lines to eliminate context saturation and amnesia.

---

## 3. What Belongs in `docs/AGENTS.md` (Global Constitution Entrypoint)

- **Token Budget**: Strictly $\le 40$ lines. Bounded, pointer-oriented orientation.
- **Content**: Directs the agent to:
  - The 4 Architectural Axioms (Platform vs Core vs Adapter vs Target).
  - The 7 Directives (Protected zones, test exit 0, Same Change Set, bounded context).
  - Pointers to canonical architecture (`ANTIOS_V1.md`) and operational state (`docs/ACTIVE_CONTEXT.md`).
