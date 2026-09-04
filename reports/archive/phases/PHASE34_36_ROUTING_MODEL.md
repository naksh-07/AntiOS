# AntiOS Phase 34–36 Agent Routing Engine & Delegation Policy

### 1. The Delegation Decision Matrix
AntiOS answers: *"Should this task be handled by the primary agent or delegated?"*
Default is strictly **`NO_DELEGATION` (SOLO)** unless domain specialization provides measurable value.

| Signal | Condition | Decision | Rationale |
| :--- | :--- | :--- | :--- |
| **Adapter Policy** | `allow_delegation: false` | `NO_DELEGATION` | Project adapter policy explicitly forbids delegation |
| **Documentation** | `task_class == DOCUMENTATION` | `NO_DELEGATION` | Primary agent owns documentation directly; solo verifier suffices |
| **Cross-Subsystem Feature** | Matched subsystems $\ge 3$ | `NO_DELEGATION` | Multi-subsystem scope requires unified ownership to prevent multi-agent swarm |
| **Bug Task** | `task_class == BUG` | `DELEGATE_SPECIALIST` | Root Cause Debugger isolates and deterministically reproduces failure |
| **Investigation** | `task_class == INVESTIGATION` | `DELEGATE_INVESTIGATION` | Read-only reconnaissance specialist gathers codebase evidence |
| **Core Governance** | Subsystems `governance`, `security`, `hooks` | `DELEGATE_SPECIALIST` | Security Reviewer audits invariants with mandatory verification |
| **Domain Specialist** | Specialized subsystem with enabled adapter specialist | `DELEGATE_SPECIALIST` | Domain specialist has matching skills, boundaries, and tests |
| **Unknown Domain** | Unmapped subsystem or low confidence | `NO_DELEGATION` | Fails closed to Primary Agent to prevent hallucinated delegation |

---

### 2. Token-Bounded Card Output
The `AgentRoutingPack` renders a deterministic text card adhering to strict token budgets:
- Full card: strictly $\le 25$ lines
- Summary card: strictly $\le 15$ lines

```text
=== ANTIOS AGENT ROUTING PACK ===
Task Class:   BUG [Risk: MEDIUM]
Subsystem:    auth-service
Primary:      AntiOS Engineer
Delegation:   DELEGATE_SPECIALIST
Specialist:   Root Cause Debugger
Reason:       Bug task warrants systematic root-cause isolation by debugger specialist
Why Selected: Specialist 'Root Cause Debugger' selected for deterministic reproduction
Why Not:      Investigation Specialist: Task class 'BUG' does not match domain
Allowed Caps: skill:antios-debug, skill:antios-engineer
Forbidden:    workflow:release, rule:core-immutable:override
Verifier:     verifier:maker-checker
Escalation:   RETURN_TO_PRIMARY
Handoff:      Bounded contract [contract-04281] generated
Confidence:   0.95 (OBSERVED)
---------------------------------
```

---

### 3. Agent Handoff Contract
When delegation is justified, Primary generates an `AgentHandoffContract`:
```json
{
  "contract_id": "contract-04281",
  "task": "Fix intermittent timeout in auth token generation",
  "target_files": ["src/auth/token.py"],
  "target_subsystems": ["auth-service"],
  "allowed_capabilities": ["skill:antios-debug", "tool:test-*"],
  "forbidden_capabilities": ["rule:core-immutable:override"],
  "constraints": [
    "Preserve Shallow Depth Law (depth <= 2; do NOT spawn child subagents)",
    "Adhere strictly to assigned capability boundary",
    "Required verification ratchet: verifier:maker-checker"
  ],
  "expected_output": "Bounded deliverable with verification evidence",
  "verification_requirement": "verifier:maker-checker",
  "delegated_role_id": "role:root-cause-debugger"
}
```
