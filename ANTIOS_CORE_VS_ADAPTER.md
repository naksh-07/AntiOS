# AntiOS Core vs Project Adapter Specification (`ANTIOS_CORE_VS_ADAPTER.md`)

**Version**: 1.0.0-GA  
**Date**: 2026-09-04  
**Status**: Canonical Core vs Adapter Specification (Universal GA Baseline)  

---

## 1. Principles of Universal Design

To function as a **universal, reusable Agent-Native Engineering OS**, AntiOS strictly decouples its generic governance engines from the specific architecture of any target codebase.

```text
=============================================================================
                    ANTIOS CORE (100% Domain-Agnostic)
  - Canonical path resolution, prefix ancestor containment
  - Windows 8.3 alias prevention, self-protection of framework files
  - Subprocess execution with timeouts, git merge conflict detection
  - Structured Maker-Checker verdict parsing and data models
  - Universal engineering lifecycle, shallow depth laws, bounded state
  - 8-type capability registry, agent topology, 6-tier tool policy
=============================================================================
                                     ▲
                                     │  Clean JSON / Dataclass Contract
                                     ▼
=============================================================================
                  PROJECT ADAPTER (Declarative Manifest)
  - antios.config.json (Schema-validated configuration)
  - Concrete protected paths (e.g. "core/engine", "vendor/upstream")
  - Concrete wildcard patterns (e.g. "core~*")
  - Concrete test commands (e.g. ["pytest", "-v"], ["npm", "test"])
  - Concrete typecheck & lint commands (e.g. ["mypy"], ["ruff", "check"])
  - Project specialist topology overrides
=============================================================================
                                     ▲
                                     │  File System / Subprocess Invocation
                                     ▼
=============================================================================
                   TARGET PROJECT (Any Language & Stack)
  - Python / FastAPI | TypeScript / Node / React | Go | Rust | Polyglot
=============================================================================
```

---

## 2. AntiOS Core Invariants

1. **Zero Domain Couplings**: AntiOS Core contains zero hardcoded references to domain terms, schemas, or third-party project paths.
2. **Universal Primitives**: Core operates exclusively on generalized abstractions (`protected_domain_paths`, `test_runners`, `forbidden_patterns`, `agent_topology`).
3. **Zero Core Mutation**: The project adaptation process (`adapt_project.py`) modifies only `antios.config.json` and project-local files. Any proposal attempting to modify `framework/core/` is rejected fail-closed.

---

## 3. Reference Adapter Implementations

### 3.1 Self-Adapter (Python): `AntiOS-Universal-Self-Adapter`
```json
{
  "name": "AntiOS-Universal-Self-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": [],
  "forbidden_patterns": [],
  "test_runners": [
    {
      "name": "python-self-tests",
      "manifest": "pyproject.toml",
      "command": ["python", "tests/run_all.py"],
      "timeout_seconds": 120,
      "working_directory": "."
    }
  ]
}
```

### 3.2 Reference Proving Ground: StudyLab (TypeScript / Svelte / Rust)
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
      "working_directory": "."
    }
  ]
}
```

### 3.3 Reference Proving Ground: Pallets/Click (Python / Pytest)
```json
{
  "name": "AntiOS-Click-Adapter",
  "version": "1.0.0",
  "protected_zones": [".agents", "framework", "antios.config.json"],
  "protected_domain_paths": [],
  "forbidden_patterns": [],
  "test_runners": [
    {
      "name": "pytest-click",
      "manifest": "pyproject.toml",
      "command": ["pytest", "tests/"],
      "timeout_seconds": 60,
      "working_directory": "."
    }
  ]
}
```
