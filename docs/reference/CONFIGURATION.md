# AntiOS Configuration Reference (`docs/reference/CONFIGURATION.md`)

This document provides the formal specification for **`antios.config.json`**, the root declarative adapter configuration for projects governed by AntiOS.

---

## 1. Schema Definition & Field Specifications

### Root Object
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `schema_version` | `string` | **Yes** | Configuration schema version (must be `"1.0.0"`). |
| `project_metadata` | `object` | **Yes** | Metadata describing the target repository. |
| `protected_zones` | `array[string]` | No | Glob patterns of paths strictly shielded from tool modification. |
| `protected_domain_cores` | `array[string]` | No | Application domain files protected from unauthorized changes. |
| `runners` | `object` | No | Test and verification commands executed by Stop Gate. |
| `skills` | `object` | No | Skill definitions enabled for this workspace. |
| `tool_routing` | `object` | No | Tool selection preferences, provider mappings, and MCP policies. |
| `audit_policies` | `object` | No | Operational policy flags and threshold limits. |
| `data_dir` | `string` | No | Path to central AntiOS Data Directory (`experience.db`). |

---

### `project_metadata` Object
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | `""` | Human-readable project name. |
| `version` | `string` | `"0.1.0"` | Current project version. |
| `primary_language` | `string` | `"python"` | Primary programming language (`python`, `typescript`, `rust`, etc.). |
| `root_directory` | `string` | `"."` | Path to project root relative to configuration file. |

---

### `runners` Object
A map of runner identifier strings (e.g. `"test"`, `"lint"`, `"typecheck"`) to runner configuration objects:

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `command` | `string` | (Required) | Physical command string executed via shell subprocess. |
| `timeout_seconds` | `integer` | `60` | Execution timeout in seconds before aborting. |
| `required` | `boolean` | `true` | When `true`, exit code 0 is mandatory for Stop Gate pass. |
| `env` | `object` | `{}` | Optional environment variables injected during execution. |

---

### `tool_routing` Object
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `allowed_tiers` | `array[string]` | `["NATIVE", "SCRIPT", "PROJECT", "EXTERNAL"]` | Permitted tool tiers in preference order. |
| `excluded_tools` | `array[string]` | `[]` | Explicit tool names banned from selection. |
| `mcp_enabled` | `boolean` | `false` | Whether Model Context Protocol servers are permitted. |

---

### `audit_policies` Object
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `same_change_set` | `boolean` | `true` | Enforce code + doc + test co-modification in git diff. |
| `doc_reference_audit` | `boolean` | `true` | Enforce zero broken references in documentation. |
| `max_active_context_lines` | `integer` | `60` | Maximum allowed line count for `docs/ACTIVE_CONTEXT.md`. |
| `max_delegation_depth` | `integer` | `2` | Maximum subagent hierarchy depth. |

---

## 2. Validation & Fail-Closed Behavior

1. **Missing Config**: If `antios.config.json` is missing, AntiOS operates in fail-safe fallback mode (protecting `.agents/` and `framework/` by default).
2. **Schema Invalidation**: Syntax errors in `antios.config.json` will cause `config.py` to raise a validation exception and block Stop Gate transitions.
3. **Runner Failure**: If any runner marked `required: true` exits with a non-zero exit code, `stop_gate.py` rejects the Stop request and returns exit code 1.
