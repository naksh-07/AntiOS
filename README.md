# AntiOS: Autonomous Engineering Governance & Verification Framework

[![Tests](https://img.shields.io/badge/tests-18%2F18%20passing-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)
[![Antigravity: Native](https://img.shields.io/badge/Antigravity-v4%20Native-purple.svg)](#)

> **AntiOS** is a universal, production-grade engineering governance, safety boundary, and deterministic verification framework for autonomous AI coding agents (Google Antigravity, Gemini CLI, Claude Code).
>
> It turns unconstrained AI coding assistants into disciplined, verifiable engineering systems with **zero hallucinated test passes**, **fail-closed boundary protection**, and **risk-tiered Maker-Checker verification**.

---

## 🌟 Why AntiOS?

AI coding agents often:
- Hallucinate test passes without executing real OS processes.
- Speculatively patch core libraries, causing architectural drift.
- Suffer from context degradation when instruction files are thousands of lines long.
- Spawn unconstrained swarms of subagents, causing latency and cost explosion.

**AntiOS solves this deterministically at the OS and tool layer.**

```
+--------------------------------------------------------------------------+
| 1. AI Coding Platform (Antigravity / Gemini CLI)                         |
|    - Subagent lifecycles, interactive planning UI, tool execution, logs  |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| 2. AntiOS Governance Layer (This Repository)                             |
|    - Fail-Closed PreToolUse Guard: Protects immutable cores & governance |
|    - Physical Stop Gate Ratchet: Enforces OS Exit Code 0 test execution  |
|    - Maker-Checker Protocol: Dispatches fresh-context verifiers on risk  |
|    - Lean Skill Architecture: All skills strictly <= 60 lines            |
|    - Bounded Working Context: ACTIVE_CONTEXT.md strictly <= 60 lines     |
|    - Declarative Domain Adapter: antios.config.json (Node, Py, Rust, Go) |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| 3. Target Application (Your Repository)                                  |
|    - Your application code, schemas, domain models, and test suites      |
+--------------------------------------------------------------------------+
```

---

## 🚀 Key Capabilities

### 1. Fail-Closed Boundary Protection (`framework/core/guard.py`)
Intercepts IDE tool calls (`write_to_file`, `replace_file_content`).
- **Self-Protection**: Strictly prevents agents from tampering with governance files (`.agents/`, `framework/`).
- **Domain Protection**: Protects configured upstream core libraries (e.g. `rslib`, `engine/core`) from direct edits.
- **8.3 Short Name & Canonicalization**: Uses `os.path.commonpath` and resolves Windows 8.3 aliases (`rslib~1`) to block path traversal bypasses.
- **Fail-Closed**: Any unhandled exception or malformed payload returns `decision: deny`.

### 2. Physical Stop Gate Ratchet (`framework/core/gate.py`)
Intercepts agent task conclusion (`Stop` event).
- Automatically discovers and executes project test runners (`vitest:once`, `pytest`, `cargo test`, `go test`).
- **Exit Code 0 Requirement**: The agent **cannot conclude** the turn unless all physical test processes exit with 0.
- Captures compiler errors, stderr, and test assertion logs, returning them directly to the agent to force deterministic fixes.

### 3. Maker-Checker Verification Protocol (`framework/core/verdict.py`)
Eliminates self-rationalization on high-risk modifications:
- **Low Risk** (docs, formatting, typos): Primary agent works solo.
- **Medium Risk** (UI fixes, non-critical features): Primary agent self-verifies via native tests.
- **High Risk** (state machines, persistence/schema, security hooks, packaging): **Mandatory Checker**.
  - Primary agent spawns an independent verifier in a fresh context with `TypeName='self'`.
  - The verifier audits `git diff`, executes physical tests, and returns a structured JSON verdict (`PASS`, `FAIL`, `BLOCK`).
- **Shallow Depth Law**: Subagent nesting depth is strictly $\le 2$ (Parent $\to$ Child). Subagents never spawn grandchildren.

### 4. Lean, High-Value Skills (`.agents/skills/`)
Avoids context saturation by enforcing a strict $\le 60$-line budget per skill:
- **`antios-engineer`** (34 lines): Core engineering lifecycle, safety boundaries, risk tiering, and Stop Gate ratchet.
- **`antios-verifier`** (48 lines): Independent Checker verification contract and structured verdict emission.
- **`antios-debug`** (35 lines): Deterministic root-cause debugging protocol (minimal reproducing test first).

---

## 📦 How to Use AntiOS on ANY Project

AntiOS is domain-agnostic. You can drop it into any TypeScript, Python, Rust, Go, or mixed project:

### Step 1: Copy Governance Assets
Copy `.agents/` and `framework/` into your repository root:
```text
your-repo/
├── .agents/
│   ├── hooks.json
│   └── skills/
│       ├── antios-engineer/SKILL.md
│       ├── antios-verifier/SKILL.md
│       └── antios-debug/SKILL.md
├── framework/
│   ├── core/
│   └── scripts/hooks/
├── antios.config.json
└── docs/
    ├── AGENTS.md
    └── ACTIVE_CONTEXT.md
```

### Step 2: Configure `antios.config.json`
Define your project's protected paths and test runners:

```json
{
  "version": "1.0",
  "name": "MyProject-Adapter",
  "protected_zones": [
    ".agents",
    "framework"
  ],
  "protected_domain_paths": [
    "core/engine",
    "shared_kernel"
  ],
  "forbidden_patterns": [
    "core~*"
  ],
  "test_runners": [
    {
      "name": "typescript",
      "manifest": "package.json",
      "scripts": ["test:unit", "test"],
      "default_command": ["npm", "test"],
      "timeout_seconds": 60
    },
    {
      "name": "python",
      "manifest": "pyproject.toml",
      "default_command": ["pytest"],
      "timeout_seconds": 60
    }
  ],
  "policies": {
    "fail_closed": true,
    "enforce_working_tree_cleanliness": true,
    "enforce_same_change_set": true
  }
}
```

---

## 🧪 Testing

AntiOS includes a comprehensive 18-test suite with **zero third-party dependencies**:

```bash
# Run using standard library Python
python tests/run_all.py

# Or run using pytest
pytest tests/ -v
```

All 18 tests execute in $\le 1.2$ seconds, validating configuration loading, security guards, stop gate ratchets, verdict parsing, and skill token budgets.

---

## 📂 Repository Topology

- **`.agents/`**: Platform discovery layer (`hooks.json`, skills).
- **`framework/`**: Core governance implementation (`framework/core/`, `framework/scripts/hooks/`).
- **`docs/`**: Active governance (`AGENTS.md`, `ACTIVE_CONTEXT.md`, `CAPABILITY_ARCHITECTURE.md`).
- **`tests/`**: Automated test suite (`run_all.py`, `test_*.py`).
- **`specs/` & Root**: Master specification documents and decision registers.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.