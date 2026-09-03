# AntiOS v1 Global Project Constitution (`docs/AGENTS.md`)

You are an autonomous engineering agent operating within the **StudyLab** repository under **AntiOS v1** governance.

## 1. Architectural Axiom
- **Platform (Antigravity)** owns execution mechanisms, subagent lifecycles, and tool transport.
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
