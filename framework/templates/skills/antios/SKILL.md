---
name: antios
description: >-
  Universal project operating interface under AntiOS 2.0 governance.
  Use when planning, navigating, implementing, debugging, verifying,
  or maintaining tasks in this repository.
---

# AntiOS Project Operating Interface

You are operating inside a repository governed by **AntiOS 2.0 (Project Agent OS)**.
This skill is your primary interface. You do not need to manually invoke dozens
of individual subsystems.

## 1. Operating Rules & Governance
- **Platform Native**: Google Antigravity provides execution, tool interception, planning mode, and subagents.
- **Fail-Closed Boundaries**: Modifying protected zones (`.agents/`, `framework/`, `antios.config.json`, or declared domain cores) is strictly blocked.
- **Physical Verification**: Task conclusion requires physical test runners to exit with code 0.
- **Same Change Set**: Code, tests, and documentation must be committed together.

## 2. Standard Task Lifecycle
Execute tasks following the 8-stage lifecycle:
`UNDERSTAND -> LOCATE -> PLAN -> ACT -> TEST -> VERIFY -> REMEMBER -> RECOVER`.

1. **Wayfinding**: Inspect `.antios/knowledge.json` and `.antios/project_profile.json` for component boundaries, entrypoints, and test runners.
2. **Planning**: Create implementation plans with `<planning_mode>` when tasks require non-trivial architectural changes.
3. **Execution**: Controlled writing. Never allow multiple agents to modify the same file concurrently.
4. **Verification**: Execute the project test command configured in `antios.config.json` via `run_command`.
5. **State**: Maintain operational state in `docs/ACTIVE_CONTEXT.md` (bounded <= 60 lines).

## 3. Instance Health & Maintenance
- To inspect instance state: view `.antios/manifest.json`.
- To re-adapt following manifest changes: run `python framework/scripts/tools/adapt_project.py .`.
- To verify installation integrity: run `python framework/scripts/tools/install_project.py . --verify`.
