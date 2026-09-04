# AntiOS Phase 37–39 Tool Model Specification

## 1. Overview
The Canonical Tool Model defines the smallest sufficient representation for executable mechanisms in AntiOS without wrapping Antigravity native tools or duplicating agent runtime state.

---

## 2. Tool Tiering (`ToolTier`)

```python
class ToolTier(str, Enum):
    NATIVE = "NATIVE"      # Antigravity native tool (highest priority)
    SCRIPT = "SCRIPT"      # Deterministic local script (framework/scripts/tools/)
    PROJECT = "PROJECT"    # Project-local tool (project test runners, linters, scripts)
    EXTERNAL = "EXTERNAL"  # Standard external CLI / SDK (git CLI, python binary)
    MCP = "MCP"            # Model Context Protocol external server (selective)
```

---

## 3. Operational Enums

* **`ExecutionMode`**: `SYNCHRONOUS`, `ASYNC`, `DAEMON`
* **`Locality`**: `LOCAL`, `REMOTE`
* **`ProviderAvailability`**: `AVAILABLE`, `UNAVAILABLE`, `UNKNOWN`, `POLICY_BLOCKED`, `MISCONFIGURED`
* **`CostHint`**: `ZERO`, `LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`
* **`LatencyHint`**: `SUB_SECOND`, `SECONDS`, `MINUTES`, `UNKNOWN`
* **`ToolPolicyStatus`**: `PERMITTED`, `RESTRICTED`, `FORBIDDEN`

---

## 4. `ToolDefinition` Data Model

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `tool_id` | `str` | *required* | Unique tool identifier (e.g. `tool:native-run-command`) |
| `name` | `str` | *required* | Human-readable tool name |
| `purpose` | `str` | `""` | Operational mandate of the tool |
| `tier` | `ToolTier` | *required* | Execution tier in preference hierarchy |
| `provider_id` | `str` | *required* | ID of the providing provider |
| `capability_ids` | `List[str]` | `[]` | Capabilities exposed by this tool |
| `supported_task_types` | `List[str]` | `["*"]` | Task classes where tool is applicable |
| `supported_subsystems` | `List[str]` | `["*"]` | Subsystems where tool can be used |
| `execution_mode` | `ExecutionMode` | `SYNCHRONOUS` | Synchronous or asynchronous execution |
| `locality` | `Locality` | `LOCAL` | Local on disk or remote network service |
| `availability` | `ProviderAvailability` | `AVAILABLE` | Real-time availability status |
| `prerequisites` | `List[str]` | `[]` | Dependencies or tools needed beforehand |
| `risk` | `str` | `"LOW"` | Inherent risk tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `cost_hint` | `CostHint` | `LOW` | Relative token and compute cost hint |
| `latency_hint` | `LatencyHint` | `SUB_SECOND` | Estimated execution turnaround |
| `offline_capable` | `bool` | `True` | Whether tool functions without WAN access |
| `evidence` | `str` | `""` | Justification or provenance evidence |
| `source` | `str` | `""` | Physical source path or platform registration |
| `enabled` | `bool` | `True` | Administrative enabled toggle |
| `policy_status` | `ToolPolicyStatus` | `PERMITTED` | Constitutional policy standing |
| `metadata` | `Dict[str, Any]` | `{}` | Extensible attributes without schema pollution |

---

## 5. In-Memory Registry (`ToolRegistry`)
Indexed across 6 secondary dimensions:
- `_tools_by_tier`: Fast tier-priority lookup
- `_tools_by_capability`: O(1) matching against capability requests
- `_tools_by_task_type`: Task class scoping
- `_tools_by_subsystem`: Subsystem restriction
- `_tools_by_provider`: Provider lineage
- `_tools_by_availability`: Active filtering of offline/broken tools
