# Project Adapter Guide (`docs/guides/PROJECT_ADAPTER.md`)

The **Project Adapter** is the declarative bridge that binds AntiOS Core governance to a specific software project without modifying AntiOS framework code.

The adapter is defined in a single root configuration file: **`antios.config.json`**.

---

## 1. Anatomy of `antios.config.json`

A canonical `antios.config.json` file contains eight top-level sections:

```json
{
  "schema_version": "1.0.0",
  "project_metadata": {
    "name": "my-project",
    "version": "0.1.0",
    "primary_language": "python",
    "root_directory": "."
  },
  "protected_zones": [
    ".git/**",
    ".env*",
    "dist/**",
    "node_modules/**",
    ".venv/**"
  ],
  "protected_domain_cores": [
    "src/core/schema.py",
    "src/database/models.py"
  ],
  "runners": {
    "test": {
      "command": "python -m pytest tests/",
      "timeout_seconds": 60,
      "required": true
    },
    "lint": {
      "command": "ruff check .",
      "timeout_seconds": 30,
      "required": false
    }
  },
  "skills": {
    "enabled": [
      "antios-engineer",
      "antios-verifier",
      "antios-debug",
      "antios-adapt-project"
    ]
  },
  "tool_routing": {
    "allowed_tiers": ["NATIVE", "SCRIPT", "PROJECT", "EXTERNAL"],
    "excluded_tools": [],
    "mcp_enabled": false
  },
  "audit_policies": {
    "same_change_set": true,
    "doc_reference_audit": true,
    "max_active_context_lines": 60
  }
}
```

---

## 2. Key Sections Explained

### A. Protected Zones (`protected_zones`)
Paths in this list are completely shielded from agent file modification tools (`replace_file_content`, `write_to_file`). AntiOS `pre_tool_guard.py` intercepts any attempt to write to these paths and denies the action with `PERMISSION_DENIED`.

### B. Protected Domain Cores (`protected_domain_cores`)
Critical domain models, security protocols, or upstream libraries that an agent must not mutate without explicit approval. Unlike framework self-protection (which is permanent), domain cores represent project-specific immutability boundaries.

### C. Test Runners (`runners`)
Configures the physical commands executed by `stop_gate.py` before any task can complete.
- `command`: Physical shell command executed by Python `subprocess.run`.
- `timeout_seconds`: Execution timeout before aborting.
- `required`: When `true`, exit code 0 is mandatory for Stop Gate to pass.

### D. Tool Routing & MCP Policy (`tool_routing`)
Defines authorized tool tiers and providers. AntiOS enforces a strict 6-tier preference:
1. `NATIVE` — IDE / Platform primitives (highest preference).
2. `SCRIPT` — Deterministic local Python scripts.
3. `PROJECT` — Project CLI tools (`git`, `pytest`, `npm`).
4. `EXTERNAL` — Host OS binaries.
5. `SERVICE` — Local HTTP or RPC services.
6. `MCP` — Model Context Protocol servers (strictly gated).

---

## 3. Adapting Monorepos and Polyglot Workspaces

For repositories containing multiple packages or languages:
1. **Topology Detection**: AntiOS automatically identifies monorepos via `topology.py`.
2. **Multiple Test Runners**: You can define multiple test runners in `runners` (e.g., `test_frontend` and `test_backend`). `stop_gate.py` executes all required runners sequentially.
3. **Relative Path Anchoring**: All paths in `antios.config.json` are evaluated relative to the repository root.
