# AntiOS Core vs Project Adapter Specification (`ANTIOS_CORE_VS_ADAPTER.md`)

**Version**: 2.0.0-draft (Universal Re-baseline)  
**Date**: 2026-09-04  
**Status**: Canonical Core vs Adapter Specification  

---

## 1. Principles of Universal Design

To function as a **UNIVERSAL, reusable Agent-Native Engineering OS**, AntiOS must strictly decouple its generic governance engines from the specific architecture of any target codebase.

```text
=============================================================================
                    ANTIOS CORE (100% Domain-Agnostic)
  - Canonical path resolution, prefix ancestor containment
  - Windows 8.3 alias prevention, self-protection of framework files
  - Subprocess execution with timeouts, git merge conflict detection
  - Structured Maker-Checker verdict parsing and data models
  - Universal engineering lifecycle, shallow depth laws, bounded state
=============================================================================
                                     ▲
                                     │  Clean JSON / Dataclass Contract
                                     ▼
=============================================================================
                  PROJECT ADAPTER (Declarative Manifest)
  - antios.config.json (Schema-validated configuration)
  - Concrete protected paths (e.g. "rslib", "vendor/upstream", "legacy/core")
  - Concrete wildcard patterns (e.g. "rslib~*")
  - Concrete test commands (e.g. ["npm", "run", "vitest:once"], ["cargo", "test"])
  - Concrete typecheck & lint commands (e.g. ["tsc", "--noEmit"], ["ruff", "check"])
  - Concrete documentation sync rules (Same Change Set)
=============================================================================
                                     ▲
                                     │  File System / Subprocess Invocation
                                     ▼
=============================================================================
                   TARGET PROJECT (Any Language & Stack)
  - TypeScript / Svelte (StudyLab) | Python / FastAPI | Go / Microservices | Rust
=============================================================================
```

### 1.1 The Invariant Separation Principle
- **AntiOS Core NEVER imports, hardcodes, or references domain terms**:
  - No file paths like `rslib`, `src/routes`, `app/models`.
  - No tool names like `vitest:once`, `pytest`, `cargo`.
  - No domain concepts like `anki21`, `APKG`, `SourceQuestion`.
- **AntiOS Core operates purely on generalized abstractions**:
  - `protected_domain_paths`: An arbitrary list of filesystem strings.
  - `test_runners`: An arbitrary list of executable command specifications.
  - `forbidden_patterns`: An arbitrary list of glob expressions.

---

## 2. AntiOS Core Specification

The Core is implemented entirely within `framework/core/` and uses standard library Python.

### 2.1 Universal Invariants
1. **Self-Protection**: The framework unconditionally protects its own governance files:
   - Workspace root `.agents/` and all descendants (`hooks.json`, `skills/`).
   - Workspace root `framework/` and all descendants (`core/`, `scripts/`).
   - Workspace root adapter manifest `antios.config.json`.
2. **Fail-Closed Execution**: If any hook fails, crashes, or receives malformed data, it denies tool execution or task completion.
3. **Subprocess Isolation**: Tests are executed via standard OS subprocesses with strict timeout boundaries.
4. **Clean Working Tree**: Before completion, `git diff --check` verifies that no merge conflict markers exist.

### 2.2 Core Default Fallback Contract
When `antios.config.json` is missing or unparseable, `framework/core/config.py` MUST fallback to safe universal defaults rather than StudyLab defaults:
```python
# Universal Fallback (Decoupled from StudyLab)
DEFAULT_CONFIG = AntiOSConfig(
    name="AntiOS-Universal-Core",
    version="1.0.0",
    protected_zones=[".agents", "framework", "antios.config.json"],
    protected_domain_paths=[],  # Empty! Domain paths belong to the adapter
    forbidden_patterns=[],       # Empty!
    test_runners=[],             # Empty! Dynamically auto-detected from manifests
    fail_closed=True
)
```

---

## 3. Project Adapter Specification (`antios.config.json`)

The Project Adapter is declared in a root configuration file: `antios.config.json`.

### 3.1 JSON Schema Specification
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AntiOSProjectAdapterConfig",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Human-readable name of the project adapter"
    },
    "version": {
      "type": "string",
      "description": "Schema version of this configuration"
    },
    "protected_zones": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Framework internal directories protected from agent mutation"
    },
    "protected_domain_paths": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Target project paths that agents are strictly forbidden from modifying"
    },
    "forbidden_patterns": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Glob patterns for Windows 8.3 alias blocking or forbidden file types"
    },
    "test_runners": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "manifest": { "type": "string", "description": "Manifest file whose existence activates this runner" },
          "command": { "type": "array", "items": { "type": "string" } },
          "cwd": { "type": "string", "description": "Relative directory from workspace root" },
          "timeout_seconds": { "type": "integer", "default": 120 },
          "required": { "type": "boolean", "default": true }
        },
        "required": ["name", "command"]
      }
    },
    "linters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "command": { "type": "array", "items": { "type": "string" } },
          "manifest": { "type": "string" }
        },
        "required": ["name", "command"]
      }
    },
    "change_set_rules": {
      "type": "object",
      "properties": {
        "enforce_same_change_set": { "type": "boolean", "default": true },
        "code_extensions": { "type": "array", "items": { "type": "string" } },
        "doc_directories": { "type": "array", "items": { "type": "string" } }
      }
    },
    "fail_closed": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["name", "version", "protected_zones", "fail_closed"]
}
```

### 3.2 Manifest Auto-Detection Heuristics
If `test_runners` is empty or omitted, AntiOS Core dynamically detects the project stack via root manifests:
1. **Node.js / TypeScript**: If `package.json` exists $\to$ scans scripts for `vitest:once`, `test`, or runs `npm test`.
2. **Python**: If `pyproject.toml` or `pytest.ini` exists $\to$ runs `pytest` (or `python -m unittest`).
3. **Rust**: If `Cargo.toml` exists $\to$ runs `cargo test`.
4. **Go**: If `go.mod` exists $\to$ runs `go test ./...`.

---

## 4. Coupling Audit & Remediation Plan

An empirical audit of the repository reveals **4 residual StudyLab couplings** that must be decoupled in the Universal Core:

| Location | Hardcoded Coupling | Universal Remediation Plan |
| :--- | :--- | :--- |
| **`framework/core/config.py`** | `AntiOSConfig` dataclass defaults fallback to `protected_domain_paths=["rslib"]` and `vitest:once`. | Change defaults to empty lists. Add dynamic manifest detection fallback when `antios.config.json` is absent. |
| **`antios.config.json`** | Hardcoded to `"name": "AntiOS-StudyLab-Adapter"`. | Retain this file as the **StudyLab Reference Proving Ground Adapter**, but document it as an instance of the universal schema. |
| **`docs/AGENTS.md`** | Opens with "You are an autonomous engineering agent operating within the StudyLab repository...". | Refactor into a modular Constitution: Universal Section (Core Laws) + Adapter-Injected Section (Domain Invariants). |
| **`.agents/skills/*.md`** | Skill instructions use `rslib/` and `npm run vitest:once` as concrete examples. | Generalize examples to cite `<protected_domain_paths>` and `<configured_test_runner>`. |

---

## 5. Reference Adapter Implementations

### 5.1 Proving Ground: StudyLab (TypeScript / Svelte / Rust)
```json
{
  "name": "AntiOS-StudyLab-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": ["rslib"],
  "forbidden_patterns": ["rslib~*"],
  "test_runners": [
    {
      "name": "vitest-frontend",
      "manifest": "package.json",
      "command": ["npm", "run", "vitest:once"],
      "timeout_seconds": 90,
      "required": true
    },
    {
      "name": "rust-anki-core",
      "manifest": "rslib/Cargo.toml",
      "command": ["cargo", "test"],
      "cwd": "rslib",
      "timeout_seconds": 180,
      "required": true
    }
  ],
  "fail_closed": true
}
```

### 5.2 Case Study 2: Python / FastAPI Backend
```json
{
  "name": "AntiOS-FastAPI-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": ["migrations", "deploy/secrets"],
  "forbidden_patterns": ["*.pem", "*.key"],
  "test_runners": [
    {
      "name": "pytest-suite",
      "manifest": "pyproject.toml",
      "command": ["pytest", "tests/", "-v"],
      "timeout_seconds": 60,
      "required": true
    }
  ],
  "linters": [
    {
      "name": "ruff-check",
      "manifest": "pyproject.toml",
      "command": ["ruff", "check", "."]
    }
  ],
  "fail_closed": true
}
```

### 5.3 Case Study 3: Go Microservice
```json
{
  "name": "AntiOS-Go-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": ["vendor/upstream", "api/proto/gen"],
  "forbidden_patterns": ["vendor~*"],
  "test_runners": [
    {
      "name": "go-test",
      "manifest": "go.mod",
      "command": ["go", "test", "-race", "./..."],
      "timeout_seconds": 45,
      "required": true
    }
  ],
  "fail_closed": true
}
```

### 5.4 Case Study 4: Rust Systems Crate
```json
{
  "name": "AntiOS-Rust-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": ["c_bindings/vendored"],
  "forbidden_patterns": [],
  "test_runners": [
    {
      "name": "cargo-test",
      "manifest": "Cargo.toml",
      "command": ["cargo", "test", "--all-targets"],
      "timeout_seconds": 120,
      "required": true
    }
  ],
  "linters": [
    {
      "name": "cargo-clippy",
      "manifest": "Cargo.toml",
      "command": ["cargo", "clippy", "--", "-D", "warnings"]
    }
  ],
  "fail_closed": true
}
```
