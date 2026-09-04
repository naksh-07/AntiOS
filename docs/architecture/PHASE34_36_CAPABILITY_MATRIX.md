# AntiOS Phase 34–36 Agent Topology Capability Matrix

### 1. Canonical Agent Roles

| Role ID | Role Type | Scope | Primary Responsibility | Allowed Capabilities | Forbidden Capabilities | Required Verifier | Can Delegate | Max Depth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| `role:primary-engineer` | `PRIMARY` | `CORE` | Owns overall task completion & execution coordination | `*` | *(None)* | `verifier:maker-checker` | **Yes** | 2 |
| `role:root-cause-debugger` | `SPECIALIST` | `CORE` | Systematic bug diagnosis & minimal fix isolation | `skill:antios-debug`, `tool:navigate-repo`, `tool:test-*`, `rule:*` | `workflow:release`, `rule:core-immutable:override` | `verifier:maker-checker` | **No** | 2 |
| `role:independent-verifier` | `CHECKER` | `CORE` | Fresh-context verification of diffs, tests & invariants | `skill:antios-verifier`, `tool:navigate-repo`, `tool:audit-docs`, `tool:test-*` | `tool:write_to_file`, `tool:replace_file_content`, `workflow:*` | `verifier:maker-checker` | **No** | 2 |
| `role:investigation-specialist` | `SPECIALIST` | `CORE` | Read-only reconnaissance & codebase exploration | `tool:navigate-repo`, `tool:audit-docs`, `tool:view_file`, `tool:grep_search`, `rule:*` | `tool:write_to_file`, `tool:replace_file_content` | `verifier:solo` | **No** | 2 |
| `role:security-reviewer` | `SPECIALIST` | `CORE` | Audits security hooks, Stop Gate & protected zones | `skill:antios-verifier`, `tool:audit-docs`, `tool:navigate-repo`, `rule:*` | `rule:core-immutable:override`, `rule:platform-hook:override` | `verifier:independent-auditor` | **No** | 2 |

---

### 2. Adapter-Configurable Project Specialists

Projects declare custom domain specialists in `antios.config.json` under `agent_topology.specialists`:

```json
{
  "agent_topology": {
    "allow_delegation": true,
    "specialists": {
      "role:frontend-specialist": {
        "name": "Frontend Specialist",
        "role_type": "SPECIALIST",
        "responsibility": "Frontend UI component authoring and styling",
        "applies_to_subsystems": ["ui", "frontend"],
        "applies_to_task_types": ["FEATURE", "BUG"],
        "allowed_capabilities": ["skill:antios-*", "tool:test-*", "rule:*"],
        "forbidden_capabilities": ["rule:core-immutable:override"],
        "max_depth": 2,
        "can_delegate": false
      },
      "role:database-specialist": {
        "name": "Database Specialist",
        "role_type": "SPECIALIST",
        "responsibility": "Database migrations, schemas, and storage optimization",
        "applies_to_subsystems": ["database", "db"],
        "applies_to_task_types": ["FEATURE", "BUG", "REFACTOR"],
        "allowed_capabilities": ["skill:antios-*", "tool:test-*", "rule:*"],
        "forbidden_capabilities": ["rule:core-immutable:override"],
        "max_depth": 2,
        "can_delegate": false
      }
    }
  }
}
```

---

### 3. Capability Boundary Gating
Every access request by an agent evaluates:
$$\text{Authorized} \iff (\text{Cap} \notin \text{Forbidden}) \land (\text{Cap} \in \text{Allowed} \lor \text{Cap} \in \text{Inherited})$$
- Wildcards are supported (`"skill:*"`, `"tool:test-*"`, `"*"`).
- `Forbidden` takes absolute precedence over `Allowed`.
