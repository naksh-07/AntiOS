# AntiOS 2.0 Project Agent OS Architecture Specification (`docs/architecture/PROJECT_AGENT_OS.md`)

**Date**: 2026-09-05  
**Status**: Canonical Specification (AntiOS 2.0 Foundation)  
**Scope**: Project Agent OS Compilation, Lifecycle, Provenance & Orchestration  

---

## 1. Executive Summary & The 4-Boundary Demarcation

AntiOS 2.0 transitions AntiOS from a repository-internal development governance system into a universal **Project Boundary Compiler and Lifecycle Manager**. It compiles and adapts a self-contained, project-local Agent OS instance into any target repository without altering target application code or polluting the target repository with internal framework development assets.

To guarantee safety, determinism, and immutability, AntiOS 2.0 formalizes the **4-Boundary Demarcation**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM BOUNDARY                               │
│  Google Antigravity (IDE, Native Tools, Process Execution, Hooks)      │
└────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ (PROJECT ≠ ANTIGRAVITY)
                                    ▼
┌────────────────────────────┐              ┌────────────────────────────┐
│      SOURCE BOUNDARY       │              │     INSTANCE BOUNDARY      │
│  Canonical AntiOS Source   │              │ Target Repository Instance │
│  (framework/, tests/,      │              │ (.antios/, manifest.json,  │
│   docs/, blueprints)       │              │  knowledge, topology, skill│
└────────────────────────────┘              └────────────────────────────┘
              │                                            │
              │ (SOURCE ≠ INSTANCE)                        │ (INSTANCE ≠ PROJECT)
              ▼                                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        PROJECT BOUNDARY                                │
│  Target Project Codebase (App code, package manifests, user configs)   │
└────────────────────────────────────────────────────────────────────────┘
```

### The Four Boundary Laws:
1. **`SOURCE ≠ INSTANCE`**: Canonical AntiOS source (framework core, tests, development blueprints) is the compiler and authority; it is **never** copied wholesale or shipped into target project repositories.
2. **`INSTANCE ≠ PROJECT`**: The installed AntiOS instance (`.antios/` metadata and `.agents/skills/antios/`) is distinct from the target project source code. Application code remains sovereign.
3. **`PROJECT ≠ ANTIGRAVITY`**: Project-local skills and hooks bind to Google Antigravity primitives natively; they do not construct custom external daemons, sidecars, or background runtimes.
4. **`CANONICAL CORE ≠ LOCAL ADAPTER`**: The framework core enforces zero third-party dependencies, fail-closed security gates, and LF-normalized provenance, while the local adapter (`antios.config.json`) configures runners, domain paths, and boundaries.

---

## 2. The Five Artifact Tiers

AntiOS 2.0 classifies all filesystem artifacts into five distinct ownership tiers:

| Tier | Name | Description | Provenance & Mutation Policy |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Canonical Source** | Canonical framework core (`framework/`), test suites (`tests/`), and reference documentation. | Resides solely in canonical source repository. Never shipped to targets. |
| **Tier 2** | **Managed Config & Hooks** | `antios.config.json`, `.agents/hooks.json`. | Managed by AntiOS. User edits are strictly preserved; updates surface conflicts rather than overwriting. |
| **Tier 3** | **Generated Intelligence** | `.antios/manifest.json`, `project_profile.json`, `knowledge.json`, `agent_topology.json`, `tool_policy.json`. | Deterministically compiled from project traits. Safely regenerated during `adapt` when project manifests change. |
| **Tier 4** | **Operating Interface** | `.agents/skills/antios/SKILL.md`. | Primary user-facing `/antios` skill interface. Self-contained; guides agents through standard lifecycle. |
| **Tier 5** | **Target Project Source** | Application source code, existing `.agents/` skills, user instructions, build manifests. | Sovereign project property. AntiOS never clobbers, renames, or mutates user files without explicit consent. |

---

## 3. The Project Manifest (`.antios/manifest.json`)

The Project Manifest is the cryptographic and provenance foundation of an installed AntiOS instance. It tracks every managed and generated file with LF-normalized SHA-256 hashes, source revision, schema version, and project fingerprint.

### Schema:
```json
{
  "antios_version": "2.0.0",
  "schema_version": "1.0.0",
  "project_fingerprint": "a3f8...",
  "source_revision": "v2.0.0",
  "generated_at": "2026-09-05T00:00:00Z",
  "adaptation_state": "ADAPTED",
  "installation_state": "INSTALLED",
  "managed_paths": {
    "antios.config.json": {
      "path": "antios.config.json",
      "ownership": "MANAGED",
      "sha256": "e2b1...",
      "source_revision": "v2.0.0",
      "generated_at": "2026-09-05T00:00:00Z"
    }
  },
  "generated_paths": {
    ".antios/knowledge.json": { ... },
    ".antios/project_profile.json": { ... },
    ".antios/agent_topology.json": { ... },
    ".antios/tool_policy.json": { ... },
    ".agents/skills/antios/SKILL.md": { ... }
  },
  "user_owned_paths": [
    ".agents/skills/my-custom-skill/SKILL.md"
  ],
  "protected_paths": [
    ".agents",
    "framework",
    "antios.config.json",
    ".antios"
  ],
  "stale_paths": []
}
```

---

## 4. The Six Installation Lifecycle Phases

AntiOS 2.0 establishes a deterministic, ownership-aware lifecycle engine (`InstallationLifecycleManager`):

1. **INSTALL**: Discovers project traits, derives adapter configuration, compiles instance assets, verifies existing assets (preserving user files), writes artifacts, and records `.antios/manifest.json`. Subsequent installs are strictly idempotent no-ops.
2. **ADAPT**: Re-runs discovery against target project manifests (e.g., package.json, pyproject.toml), detects dependency or topology changes, recomputes project fingerprint, and updates generated project intelligence.
3. **UPDATE**: Advances the AntiOS source revision (e.g., v2.0.0 to v2.1.0), audits managed and generated files, detects user modifications (which are preserved and flagged as conflicts), and migrates instance assets safely.
4. **REPAIR**: Diagnoses broken or missing managed/generated artifacts, validates existing files against manifest SHA-256 records, restores missing files, and resynchronizes the manifest without disturbing user files.
5. **REMOVE**: Surgically uninstalls the AntiOS instance, removing only manifest-tracked managed and generated files and the `.antios/` directory, while strictly preserving user-owned files and target project code.
6. **VERIFY**: Audits manifest schema validity, verifies physical file checksums against manifest records, checks for manifest fingerprint drift, and returns structured `LifecycleResult`.

---

## 5. Antigravity-Native Orchestration Constitution

AntiOS 2.0 incorporates the proven orchestration principles of the Adaptive Orchestrator, codifying strict, resource-aware bounds for multi-agent workflows:

### Constitutional Bounds:
- **Maximum Active Subagents Per Wave**: Strictly $\le 10$ concurrent agents. Prevents resource exhaustion and context thrashing.
- **Maximum Total Spawned Agents Per Mission**: Strictly $\le 20$ total subagent launches across all waves. Enforces decisive execution over runaway swarms.
- **Shallow Delegation Depth Law**: Subagent nesting depth is strictly bounded to $\le 2$ (Parent $\to$ Child). Subagents are prohibited from spawning further child subagents.
- **Wave-Based Lifecycle**:
  ```text
  WAVE DISPATCH ──► WORKER DISCOVERY ──► CONSOLIDATE ──► COLLAPSE (Active=0) ──► NEXT WAVE
  ```
  Every wave must consolidate structured handoffs and completely collapse active subagents before the parent agent dispatches the next wave.
- **Dead-End Memory**: Subagents must report dead ends, blockers, and rejected paths to prevent subsequent waves from repeating failed trajectories.
- **Maker-Checker Invariant**: Verification must be executed by an independent verifier subagent with fresh context, evaluating physical test outputs and diffs rather than conversational attestations.
