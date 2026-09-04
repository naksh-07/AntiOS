# AntiOS Phase 31–33 Capability Model Specification (`docs/PHASE31_33_CAPABILITY_MODEL.md`)

**Version**: 1.0.0  
**Status**: CANONICAL SPECIFICATION  
**Module**: `framework/core/capability.py`  

---

## 1. Capability Taxonomy

The Project Capability Layer defines eight canonical capability types:

```text
┌─────────────────┬────────────────────────────────────────────────────────┐
│ Capability Type │ Purpose & Operational Semantics                        │
├─────────────────┼────────────────────────────────────────────────────────┤
│ SKILL           │ Procedural engineering policy on HOW to do work        │
│ RULE            │ Governing constraint, boundary, or invariant           │
│ WORKFLOW        │ 10-stage lifecycle sequence governing WHEN work happens│
│ TOOL            │ Deterministic execution mechanism (script, binary)     │
│ VERIFIER        │ Verification contract (Solo, Maker-Checker, Auditor)   │
│ SPECIALIST      │ Bounded agent role adhering to Shallow Depth Law (<=2) │
│ EXTERNAL_PROVIDER│ External service, data repository, or remote resource │
│ MCP_PROVIDER    │ Model Context Protocol server under strict governance  │
└─────────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Canonical Data Contract (`Capability`)

```python
@dataclass
class Capability:
    capability_id: str                         # e.g. "skill:antios-engineer"
    type: CapabilityType                       # SKILL, RULE, WORKFLOW, etc.
    name: str                                  # Human-readable title
    purpose: str                               # Concise functional mandate
    scope: CapabilityScope = CapabilityScope.CORE
    applies_to_subsystems: List[str] = ["*"]
    applies_to_task_types: List[str] = ["*"]
    prerequisites: List[str] = []
    related_rules: List[str] = []
    related_workflows: List[str] = []
    related_tools: List[str] = []
    verifier: Optional[str] = None
    enabled: bool = True
    risk: str = "LOW"
    evidence: str = ""
    confidence: float = 1.0
    epistemic_state: str = "OBSERVED"
    source: str = ""
    negative_applicability: List[str] = []
    metadata: Dict[str, Any] = {}
```

---

## 3. Rule Precedence Hierarchy

When multiple rules govern a task, precedence is strictly ordered by constitutional authority:

1. **Rank 1 (`PLATFORM_HOOK`)**: Host stdio hook IPC interception (`PreToolUse`, `Stop`).
2. **Rank 2 (`CORE_INVARIANT`)**: Universal Core self-protection, Stop Gate physical test ratchet, Same Change Set rule, Shallow Depth Law ($\text{depth} \le 2$).
3. **Rank 3 (`ADAPTER_POLICY`)**: Project configuration declared in `antios.config.json`.
4. **Rank 4 (`SUBSYSTEM_INVARIANT`)**: Subsystem-specific protected invariants and boundary rules.
5. **Rank 5 (`PROJECT_GUIDANCE`)**: Discovered documentation conventions and repository practices.

### Conflict Handling Policy
- Conflicting rules are **never silently suppressed**.
- Both rules are recorded in `CapabilityPack.conflicts` with `status: CONFLICT_DETECTED`.
- The higher-ranking rule prevails by numeric precedence (`winning_precedence <= losing_precedence`).

---

## 4. Specialist Agent Model & Shallow Depth Law

Specialist agents represent bounded execution roles, **not autonomous swarm daemons**:
- Nesting depth is strictly capped at $\text{depth} \le 2$ (Root $\to$ Leaf/Coordinator).
- Subagents are permanently prohibited from spawning recursive swarms.
- Specialists inherit explicit scopes, allowed capabilities, required verifiers, and escalation paths.
