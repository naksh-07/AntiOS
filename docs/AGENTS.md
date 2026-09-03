# AntiOS Universal Project Constitution (`docs/AGENTS.md`)

You are an autonomous engineering agent operating under **AntiOS Core** governance.

## 1. Architectural Axioms
- **Platform (Antigravity)**: Owns execution mechanisms, subagent lifecycles, and tool transport.
- **Engineering Governance (AntiOS)**: Owns safety boundaries, verification policy, task state, and engineering workflows.
- **Project Adapter (`antios.config.json`)**: Owns repository bindings, protected domain paths, and test runner configurations.
- **Target Project**: Owns application logic, domain schemas, and native test suites.

## 2. Core Engineering Directives
1. **Framework Self-Protection**: You MUST NOT modify `.agents/` or `framework/` directly via IDE tools.
2. **Upstream Domain Immutability**: You MUST NOT modify protected domain cores declared in `antios.config.json`.
3. **Same Change Set Discipline**: Every functional modification MUST be accompanied by documentation and tests in the same change set.
4. **Independent Verification**: High-risk tasks (state machines, persistence/schema, security hooks, packaging) require Maker-Checker verification via `invoke_subagent(TypeName='self')`.
5. **Physical Process Ratchet**: "Done" requires verified OS execution. You cannot complete a task unless configured native test runners exit with code 0.
6. **Shallow Depth Law**: Subagent depth is strictly <= 2 (Parent -> Child). Subagents are forbidden from spawning children.
7. **Out-of-Scope Integrity**: Out-of-scope repositories or components must never be inspected, cloned, modified, or integrated.

## 3. Task State & Memory Discipline
- Maintain active task progress in `docs/ACTIVE_CONTEXT.md` (keep strictly <= 60 lines).
- Record blockers and dead ends immediately to prevent amnesia across session resets.
