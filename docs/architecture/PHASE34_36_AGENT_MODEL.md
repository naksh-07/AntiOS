# AntiOS Phase 34–36 Agent Role Model & Boundary Contracts

### 1. Canonical Agent Role Schema
The `AgentRole` domain model defines the canonical behavioral contract for agents in AntiOS:

| Field | Type | Description |
| :--- | :--- | :--- |
| `role_id` | `str` | Unique canonical identifier (e.g. `role:primary-engineer`) |
| `name` | `str` | Human-readable role name |
| `role_type` | `AgentRoleType` | `PRIMARY`, `SPECIALIST`, `CHECKER`, `CANDIDATE` |
| `responsibility` | `str` | Bounded functional mandate |
| `scope` | `CapabilityScope` | `CORE`, `ADAPTER`, `PROJECT_LOCAL`, `SUBSYSTEM` |
| `applies_to_task_types` | `List[str]` | Applicable `TaskClass` values or wildcard `*` |
| `applies_to_subsystems` | `List[str]` | Applicable subsystem IDs or wildcard `*` |
| `boundary` | `AgentCapabilityBoundary` | Explicit capability authorization boundaries |
| `required_verifier` | `str` | Mandatory verification ratchet (`verifier:maker-checker`, etc.) |
| `escalation_policy` | `EscalationPolicyType` | `RETURN_TO_PRIMARY`, `FAIL_CLOSED`, `REQUIRE_CHECKER` |
| `max_depth` | `int` | Strictly $\le 2$ under Shallow Depth Law |
| `can_delegate` | `bool` | `True` for PRIMARY only; strictly `False` for specialists/checkers |
| `enabled` | `bool` | Registry activation status |
| `confidence` | `float` | 0.0 to 1.0 confidence score |
| `evidence` | `str` | Grounding evidence for role definition |
| `epistemic_state` | `str` | `OBSERVED`, `INFERRED`, `CANDIDATE`, `DURABLE` |

---

### 2. Capability Boundaries: The 4 Zones
Authority is **never** inferred from role name alone. Access is evaluated via `AgentCapabilityBoundary`:
1. **`FORBIDDEN` (Absolute Precedence)**: Explicitly forbidden capabilities (e.g. `rule:core-immutable:override`, `tool:write_to_file` for verifiers). If matched, access is unconditionally denied.
2. **`ALLOWED`**: Explicitly permitted capabilities (e.g. `skill:antios-engineer`, `tool:test-*`).
3. **`INHERITED`**: Core rules and invariants inherited from platform governance (`rule:core-immutable`, `rule:stop-gate-ratchet`).
4. **`REQUIRED`**: Mandatory capabilities the role must exercise (e.g. `skill:antios-verifier` for Checkers).

---

### 3. Shallow Depth Law Invariant
AntiOS enforces:
$$\text{Max Agent Depth} \le 2$$
$$\text{Primary} \longrightarrow \text{Specialist / Checker}$$

- **Primary Agent**: Coordinates execution, may delegate to bounded specialists.
- **Specialist Agent**: Executes bounded subtask, strictly forbidden from spawning child subagents (`can_delegate = False`).
- **Checker Agent**: Independently audits diffs and tests, strictly forbidden from delegating or writing code.
