# AntiOS v1 Constitution Architecture (`ANTIOS_CONSTITUTION.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish the canonical project constitution, defining exactly what belongs in prompt rules (`AGENTS.md`), what belongs in skills, what belongs in deterministic hooks, and what belongs in documentation.

---

## 1. The Rule-to-Enforcement Mapping Principle

Empirical testing across Phases 7–10 proved that:
> *Prompt rules without code-level enforcement are soft guidelines that LLMs routinely rationalize away during complex multi-step reasoning.*  
> *Conversely, hooks cannot perform fuzzy semantic evaluations requiring human or LLM judgment.*

Therefore, AntiOS v1 establishes a strict **Enforcement Placement Law**:

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

## 2. What Belongs Where?

### What Belongs in `docs/AGENTS.md` (Global Constitution)
- **Token Budget**: Strictly $\le 80$ lines (~2,500 bytes). Must fit comfortably in initial context without displacing project reasoning.
- **Core Directives**:
  1. **Axiom of AntiOS**: Platform mechanism vs Project policy vs Domain truth.
  2. **Upstream Immutability**: Absolute prohibition on modifying `rslib/`.
  3. **Framework Self-Protection**: Prohibition on editing `.agents/` or AntiOS scripts.
  4. **Working Tree Discipline**: Operate in designated sandboxes/worktrees; no destructive git commands.
  5. **Same Change Set**: Synchronize code changes and documentation in the same commit/turn.
  6. **Physical Process Ratchet**: Task completion requires OS test exit code 0.
  7. **StudySourceCore Boundary**: Strictly out of scope.

### What Belongs in Skills (`.agents/skills/`)
- Procedural workflows that are activated only when relevant.
- Risk-tiering heuristics (when to spawn Maker-Checker).
- Subagent dispatch instructions (using `TypeName='self'`).
- Test runner commands and environment diagnosis guidance.

### What Belongs in Hooks (`framework/scripts/hooks/`)
- Purely deterministic, binary checks that can be calculated in <100ms:
  - `pre_tool_guard.py`: Canonical path resolution, prefix matching, denial reasons.
  - `stop_gate.py`: Subprocess test execution, return code inspection, timeout enforcement.

### What Belongs in Reference Documentation (`docs/`)
- Full architecture specifications (`ANTIOS_V1_ARCHITECTURE.md`).
- Decision registers and forensic reports.
- Comprehensive security and verification models.

---

## 3. Canonical `docs/AGENTS.md` Specification

The authoritative content of `docs/AGENTS.md` in AntiOS v1:

```markdown
# AntiOS v1 Global Project Constitution

You are an autonomous engineering agent operating within the **StudyLab** repository, governed by **AntiOS v1**.

## 1. Architectural Axiom
- **Platform (Antigravity)** owns execution, subagent lifecycles, and tool transport.
- **Engineering Governance (AntiOS)** owns safety boundaries, verification policy, and task state.
- **Domain Truth (StudyLab)** owns schemas, APKG contracts, application logic, and native test suites.

## 2. Core Engineering Directives
1. **Upstream Immutability**: You MUST NOT modify or write to `rslib/` (Anki core). It is protected by deterministic hooks.
2. **Hook Self-Protection**: You MUST NOT modify `.agents/` or AntiOS hook scripts.
3. **Same Change Set**: Every code modification MUST be accompanied by corresponding updates to documentation and tests in the same change set.
4. **Independent Verification**: High-risk tasks (reviewer FSM, persistence, packaging, security) require Maker-Checker verification via `invoke_subagent(TypeName='self')`.
5. **Physical Process Ratchet**: "Done" requires verified OS execution. You cannot complete a task unless native tests (`vitest:once` or `pytest`) exit with code 0.
6. **StudySourceCore Boundary**: StudySourceCore is 100% OUT OF SCOPE. Do not inspect, clone, modify, or integrate it.

## 3. Task State Discipline
- Maintain active task progress in `docs/ACTIVE_CONTEXT.md` (keep $\le 60$ lines).
- Record blockers and dead ends immediately to prevent amnesia across session resets.
```
