# AntiOS Phase 34–36 Architecture Specification
## Agent Topology & Project-Specific Specialist Layer

### 1. Executive Summary
Phase 34–36 elevates AntiOS from capability identification (*"Which capabilities are relevant?"*) to deterministic agent governance (*"Which agent role should perform which capability, under what scope, with what constraints, and when delegation is justified?"*).

AntiOS establishes this layer as a lightweight, zero-daemon orchestration policy over Google Antigravity. It does **not** duplicate Antigravity's native agent runtime, model invocation, or scheduling engines.

```text
TASK
  │
  ▼
TASK CLASS & INTENT
  │
  ▼
SUBSYSTEM & COMPONENT WAYFINDING
  │
  ▼
CAPABILITY PACK (Phase 31–33)
  │
  ▼
AGENT ROUTER (Phase 34–36)
  ├── Primary Role Selection (AntiOS Engineer)
  ├── Delegation Policy Evaluation (NO_DELEGATION vs DELEGATE_SPECIALIST)
  ├── Capability Boundary Enforcement (Allowed vs Forbidden)
  └── Handoff Contract Synthesis
  │
  ▼
EXECUTION & VERIFICATION
  ├── Single Controlled Writer / Scoped Specialist
  └── Independent Checker (Maker-Checker / Stop Gate Ratchet)
```

---

### 2. The Separation of Authority
- **Antigravity Owns**:
  - Actual agent execution and subagent lifecycle (`invoke_subagent`, `manage_subagents`)
  - LLM model invocation, token generation, and context isolation
  - Tool execution and native scheduling (`schedule`)
- **AntiOS Owns**:
  - Role policy, scope, and capability authorization boundaries
  - Deterministic delegation decisions
  - Specialist constraints and Shallow Depth Law enforcement
  - Independent verification expectations and Stop Gate ratchets
  - Project-specific adapter topology configuration

---

### 3. Core Architecture Components
1. **Canonical Agent Role Model (`framework/core/agent_role.py`)**:
   - `AgentRole`: Canonical domain model for agent roles.
   - `AgentCapabilityBoundary`: Explicit gating of allowed, forbidden, required, and inherited capabilities.
   - `AgentHandoffContract`: Token-bounded context handoff contract.
   - `SpecialistResultReport`: Structured return report with evidence.
2. **Agent Topology Engine (`framework/core/agent_topology.py`)**:
   - `AgentTopologyRegistry`: Multi-key index (by role type, subsystem, task type).
   - Canonical core roles (`primary-engineer`, `root-cause-debugger`, `independent-verifier`, `investigation-specialist`, `security-reviewer`).
   - `SpecialistDiscoveryEngine`: Candidate discovery without auto-activation (`DISCOVER` $\to$ `PROPOSE` $\to$ `VALIDATE` $\to$ `ENABLE`).
3. **Deterministic Agent Router (`framework/core/agent_router.py`)**:
   - Evaluates delegation signals (subsystem specialization, task complexity, risk tier, cross-subsystem scope, adapter policies).
   - Enforces `NO_DELEGATION` (SOLO) as the efficient default.
   - Generates compact `AgentRoutingPack` cards ($\le 25$ lines) with *why selected* and *why not others* rationales.
4. **Project Adapter Extensions (`framework/core/config.py`, `adapter.py`)**:
   - Project-local specialist declarations in `antios.config.json`.
   - `verify_adapter` constitutional audit rejecting depth $> 2$, specialist delegation authority, or core invariant overrides.
