# AntiOS Project Environment Compiler Contract

**Specification**: `docs/architecture/ambient/COMPILER.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 4  

---

## 1. Overview & Architectural Role

The **Project Environment Compiler** (`framework/core/compiler.py`) is the deterministic build system that compiles an AntiOS source repository into an isolated, self-contained project instance within a target repository.

The compiler guarantees that:
1. Target projects receive complete, standalone engineering governance without depending on the upstream AntiOS source tree at runtime.
2. The Four-Boundary Demarcation (`INV-10`) is mathematically enforced.
3. Every generated artifact is cryptographically accounted for in an LF-normalized manifest ledger.

---

## 2. The Four-Boundary Demarcation (`INV-10`)

The compiler strictly maintains the four sovereign boundaries:

$$\text{SOURCE} \ne \text{INSTANCE} \ne \text{PROJECT} \ne \text{ANTIGRAVITY}$$

```
┌─────────────────────────┐         ┌─────────────────────────┐
│     ANTI-OS SOURCE      │         │   ANTIGRAVITY PLATFORM  │
│       (`SOURCE`)        │         │     (`ANTIGRAVITY`)     │
│ Canonical engine code:  │         │ Host IDE & extensions:  │
│ - framework/            │         │ - .agents/              │
│ - tests/                │         │ - .agents/hooks.json    │
└────────────┬────────────┘         └────────────┬────────────┘
             │                                   │
             ▼ Compiles into                     ▼ Mounts hooks
┌─────────────────────────┐         ┌─────────────────────────┐
│     ANTI-OS INSTANCE    │         │      TARGET PROJECT     │
│      (`INSTANCE`)       │         │       (`PROJECT`)       │
│ Generated runtime:      │         │ Application domain:     │
│ - .antios/manifest.json │         │ - src/, app/, lib/      │
│ - .antios/runtime/*.py  │         │ - package.json, Cargo   │
│ - .antios/proofs/       │         │ - antios.config.json    │
└─────────────────────────┘         └─────────────────────────┘
```

---

## 3. The Five Artifact Tiers

Artifacts within an adapted workspace belong to exactly one of five ownership tiers:

| Tier | Name | Managed By | Mutation Policy | Examples |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Canonical Source** | Upstream AntiOS | Read-only in target projects | `framework/core/*.py` |
| **2** | **Managed Config & Hooks** | Declarative Config | User & Adapter managed | `antios.config.json`, `.agents/hooks.json` |
| **3** | **Generated Intelligence** | Project Compiler | 100% Machine generated | `.antios/runtime/*.py`, `.antios/manifest.json` |
| **4** | **Operating Interface** | AntiOS Skill System | Managed by AntiOS | `.agents/skills/antios/SKILL.md` |
| **5** | **Target Project Source** | Project Authors | 100% Sovereign & untouched | Application code, domain tests, migrations |

---

## 4. Runtime Closure Specification

Runtime scripts generated into `.antios/runtime/` (`pre_tool_guard.py`, `stop_gate.py`, `inspect_instance.py`, `verify_runtime.py`) must satisfy the **Runtime Closure Axiom**:

1. **Zero Framework Imports**: AST parsing verifies that no script in `.antios/runtime/` imports from `framework` or any submodule.
2. **Zero Third-Party Dependencies**: All scripts execute using Python's standard library alone (`sys`, `os`, `json`, `subprocess`, `hashlib`, `pathlib`).
3. **Self-Contained Execution**: Scripts operate as standalone binaries directly invocable by Antigravity platform hooks via standard subprocess execution.
4. **Deterministic Exit Codes**:
   - `0`: Permitted / Passed.
   - `1`: Denied / Failed / Policy Violation.
   - `2`: Syntax Error / Hook Execution Anomaly (fails closed).

---

## 5. Cryptographic Provenance Manifest (`.antios/manifest.json`)

Every compilation emits an authoritative cryptographic manifest ledger:

```json
{
  "antios_version": "2.1.0-contract",
  "compiled_at": "2026-09-07T02:00:00Z",
  "project_id": "proj_target_app",
  "artifacts": {
    ".antios/runtime/pre_tool_guard.py": {
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 1842,
      "tier": 3
    },
    ".antios/runtime/stop_gate.py": {
      "sha256": "5f4dcc3b5aa765d61d8327deb882cf992b95bc680917e335f60b0d36cae59714",
      "size_bytes": 4510,
      "tier": 3
    }
  }
}
```

- **LF Line Ending Normalization**: Hashes are computed after normalizing `\r\n` to `\n` to ensure identical checksums across Windows, macOS, and Linux.
- **Drift Detection**: During `antios doctor`, the engine compares disk hashes against `manifest.json`. Any untracked modification flags a `RUNTIME_TAMPERED` warning.
