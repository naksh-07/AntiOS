# AntiOS Phase 31–33 Routing Model Specification (`docs/PHASE31_33_ROUTING_MODEL.md`)

**Version**: 1.0.0  
**Status**: CANONICAL SPECIFICATION  
**Module**: `framework/core/capability_router.py`  

---

## 1. The Resolution Pipeline

The Task-to-Capability Router executes a 9-stage deterministic resolution pipeline:

```text
┌─────────────────────────┐
│ 1. TASK INTENT INPUT    │  e.g. "Change the login button" / target files
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 2. TASK CLASSIFICATION  │  Determines TaskClass (FEATURE, BUG, REFACTOR, etc.)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 3. LOCALITY RESOLUTION  │  WayfindingEngine maps to Subsystem, Component, Blast Radius
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 4. WORKFLOW ROUTING     │  Maps TaskClass to canonical/adapter WorkflowSpec
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 5. SKILL SELECTION      │  Filters by Subsystem & Task; evaluates negative applicability
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 6. RULE RESOLUTION      │  Applies Precedence (Rank 1-5) and surfaces conflicts
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 7. TOOL RESOLUTION      │  Binds test runners, linters, and deterministic scripts
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 8. VERIFIER SELECTION   │  Derives Solo vs Maker-Checker vs Auditor by Risk Tier
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 9. MCP EVALUATION       │  Applies 3-Tier Policy (Native > Script > Project > MCP)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ EMIT CAPABILITY PACK    │  Token-bounded card (<= 25 lines) or complete JSON
└─────────────────────────┘
```

---

## 2. Negative Applicability Filtering

AntiOS enforces negative applicability rules so that irrelevant skills do not pollute agent context:
- `antios-debug`: Prohibited for `DOCUMENTATION`, `INVESTIGATION`, and `RELEASE` tasks.
- `antios-verifier`: Prohibited for `INVESTIGATION` tasks or agents executing in the `MAKER` role during `IMPLEMENT` stage.
- `antios-adapt-project`: Prohibited for standard application feature development.

---

## 3. MCP Justification Decision Tree

Under `ANTIOS_MCP_POLICY.md`, MCP servers are evaluated only when native mechanisms cannot fulfill the requirement:

```text
Can native Antigravity tools fulfill the task?
  ├──► YES: Use NATIVE (MCP Decision: NOT_NEEDED)
  └──► NO:
       Can a deterministic local script fulfill the task?
         ├──► YES: Use SCRIPT (MCP Decision: NOT_NEEDED)
         └──► NO:
              Can a project-local compiler/test runner fulfill the task?
                ├──► YES: Use PROJECT_TOOL (MCP Decision: NOT_NEEDED)
                └──► NO:
                     Does task require live browser DOM or accessibility inspection?
                       ├──► YES: Permit chrome-devtools-mcp (USEFUL)
                       └──► NO:
                            Does task require headless browser automation?
                              ├──► YES: Permit playwright (USEFUL)
                              └──► NO:
                                   Does task require upstream Gemini SDK documentation?
                                     ├──► YES: Permit gemini-api-docs (USEFUL)
                                     └──► NO:
                                          Does task require remote GitHub PR creation?
                                            ├──► YES: Permit github-mcp-server (OPTIONAL)
                                            └──► NO:
                                                 Is candidate rejected (notion, postman, posthog)?
                                                   ├──► YES: REJECT (MCP Decision: REJECTED)
                                                   └──► NO: NOT_NEEDED
```
