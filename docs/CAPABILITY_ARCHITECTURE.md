# AntiOS Capability Architecture & Governance Specification
**Phases 12–15 Foundation** | **AntiOS v1 Frozen Baseline**  
**Status**: ACTIVE | **Demarcation**: Platform $\leftrightarrow$ Governance $\leftrightarrow$ Domain

---

## 1. Tripartite Capability Demarcation

AntiOS strictly separates responsibilities into three distinct architectural tiers:

```
+-----------------------------------------------------------------------+
| 1. Antigravity Platform (Native Mechanisms)                           |
|    - Subagent execution & lifecycle (invoke_subagent)                 |
|    - Tool interception engine (PreToolUse & Stop hook framing)        |
|    - Interactive Planning Mode UI (implementation_plan.md)            |
|    - Immutable audit logs (transcript.jsonl) & Background scheduler   |
|    - Raw OS process execution primitive (run_command)                 |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
| 2. AntiOS v1 Framework (Project Governance & Safety Layer)            |
|    - Fail-closed tool guards (pre_tool_guard.py / framework.core.guard)|
|    - Framework self-protection (.agents/ & framework/ immutable)      |
|    - Physical process test ratchets (stop_gate.py / gate.py)          |
|    - Bounded task state (docs/ACTIVE_CONTEXT.md <= 60 lines)          |
|    - Global project constitution (docs/AGENTS.md <= 80 lines)         |
|    - Core engineering skills (antios-engineer, verifier, debug)       |
|    - Maker-Checker verification protocol & structured verdicts        |
|    - Declarative domain adapter configuration (antios.config.json)    |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
| 3. Target Domain Application (e.g. StudyLab)                          |
|    - Application schemas, invariants, and state machines               |
|    - Domain-specific compilers & packaging (generate_apkg.py)        |
|    - Application test suites (vitest:once, pytest)                    |
|    - Domain data models and storage (SQLite / TypeScript)             |
+-----------------------------------------------------------------------+
```

---

## 2. Directory Layout & Discovery Contracts

- **`.agents/` (Platform Discovery Layer)**:
  - Exclusively houses assets indexed by Antigravity at workspace root:
    - `.agents/hooks.json`: Interception declarations for `PreToolUse` and `Stop`.
    - `.agents/skills/<skill>/SKILL.md`: Discoverable skill definitions.
  - *Invariant*: Protected by `pre_tool_guard.py` from tool edits. Total skill count kept lean.
- **`framework/` (Governance Implementation Layer)**:
  - `framework/core/`: Reusable Python modules (`config.py`, `guard.py`, `gate.py`, `verdict.py`).
  - `framework/scripts/hooks/`: Hook CLI bridges (`pre_tool_guard.py`, `stop_gate.py`).
  - *Invariant*: Zero external dependencies, pure standard library Python, protected from tool edits.
- **`docs/` (Active Governance & Working State)**:
  - `docs/AGENTS.md`: Global constitution ($\le 80$ lines).
  - `docs/ACTIVE_CONTEXT.md`: Bounded working set memory ($\le 60$ lines).
  - `docs/CAPABILITY_ARCHITECTURE.md`: This capability specification.
- **`tests/` (Deterministic Test Harness)**:
  - Unit and adversarial test suites validating AntiOS framework code, hook security, and skill contracts.
- **`antios.config.json` (Root Domain Adapter)**:
  - Declarative configuration specifying protected zones, protected domain cores, and dynamic test runners.

---

## 3. Core Workflows (Composed Engineering Sequences)

### A. Feature Implementation Workflow
1. **Ingest & Orient**:
   - Inspect `docs/AGENTS.md` and `docs/ACTIVE_CONTEXT.md`.
   - Determine Risk Tier (Low, Medium, High).
2. **Platform Native Planning**:
   - Enter Antigravity `<planning_mode>` and draft `implementation_plan.md`.
   - Await explicit user approval before modifying code.
3. **Guarded Implementation**:
   - Execute edits using IDE tools (`replace_file_content`).
   - `pre_tool_guard.py` verifies all targets against self-protection and domain immutability boundaries.
   - Respect Same Change Set rule: documentation updated in the same changeset as code.
4. **Risk-Based Verification**:
   - If Low Risk: Local verification.
   - If Medium Risk: Self-verify by executing native test suite.
   - If High Risk: Dispatch Independent Verifier subagent (`TypeName='self'`).
5. **Stop Gate Ratchet**:
   - Attempt task conclusion; `stop_gate.py` dynamically runs test runners and checks working tree cleanliness.
6. **State Reconciliation**:
   - Update `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines) and author `walkthrough.md`.

### B. Bug-Fix & Root-Cause Workflow (`antios-debug`)
1. **Deterministic Reproduction**:
   - Execute native test command to observe failure or author minimal reproducing test case first.
2. **Hypothesis & Isolation**:
   - Formulate explicit root-cause hypothesis; trace logic without touching protected cores.
3. **Surgical Patch**:
   - Apply minimal fix in application layer.
4. **Regression Verification**:
   - Run reproduction test and full test suite (`npm run vitest:once` or `pytest`).
5. **Stop Gate Ratchet**:
   - Physical exit code 0 required.

### C. Independent Verification Workflow (`antios-verifier`)
1. **Dispatch (High Risk)**:
   - Primary agent calls `invoke_subagent(TypeName='self', Role='Independent Verifier', ...)`.
2. **Clean Audit**:
   - Verifier checks `git status` and `git diff`.
   - Verifies protected boundaries and Same Change Set.
3. **Physical Execution**:
   - Verifier runs native test commands via `run_command`.
4. **Structured Verdict**:
   - Verifier emits JSON verdict (`PASS`, `FAIL`, or `BLOCK`).
   - Primary agent acts on verdict.

---

## 4. Agent Roles & Delegation Model

```
+---------------------------------------------------------------+
| Primary Agent (Maker)                                         |
| - Owns planning, execution, and state synchronization         |
| - Low Risk: works solo                                        |
| - Medium Risk: self-verifies                                  |
| - High Risk: dispatches Independent Verifier                  |
+---------------------------------------------------------------+
                               |
                               | (High-Risk tasks only)
                               v
+---------------------------------------------------------------+
| Independent Verifier (Checker)                                |
| - Fresh context (unbiased by Maker's rationale)               |
| - TypeName='self' (mandated to run test commands)             |
| - Audits git diff, checks boundaries & Same Change Set        |
| - Executes physical tests, emits structured JSON verdict      |
| - SHALLOW DEPTH LAW: Depth <= 2 (NEVER spawns subagents)      |
+---------------------------------------------------------------+
```

### Risk-Based Delegation Matrix

| Risk Tier | Scope / Characteristics | Delegation Rule | Verifier Required? |
| :--- | :--- | :--- | :--- |
| **LOW** | Typos, documentation edits, formatting, comments | Solo execution | NO (Zero subagents) |
| **MEDIUM** | Isolated UI components, standard non-critical features | Primary agent + self test | NO (Parent runs tests) |
| **HIGH** | State machines, persistence/schema, security hooks, packaging | **MANDATORY MAKER-CHECKER** | **YES** (`TypeName='self'`) |

### Shallow Depth Law
- Nesting depth must NEVER exceed 2: $\text{Parent} \to \text{Child}$.
- Subagents are strictly forbidden from calling `invoke_subagent`.
- Swarms (>2 concurrent agents) are permanently rejected. Maximum 1 active verifier per task wave.

---

## 5. Structured Verdict Protocol

Independent verifiers emit machine-readable verdicts parsed by `framework.core.verdict`:

```json
{
  "status": "PASS",
  "risk_tier": "HIGH",
  "files_audited": ["sandbox/StudyLab/ts/state.ts"],
  "tests": [
    {
      "command": "npm run vitest:once",
      "exit_code": 0,
      "passed": true,
      "details": "14 tests passed"
    }
  ],
  "same_change_set_verified": true,
  "summary": "Verified state machine fix without regressions.",
  "issues": []
}
```
