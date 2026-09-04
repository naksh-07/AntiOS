# AntiOS Phase 27 — Architecture Specification: Agent-Native Engineering Environment
**Document ID**: `PHASE27_ARCHITECTURE`  
**Date**: 2026-09-04  
**Author**: AntiOS System Architect  
**Status**: APPROVED ARCHITECTURAL BLUEPRINT  
**Baseline Certified**: Phase 26 Certified (234/234 tests passing in 10.83s, Release Ready with Limitations)  

---

## 1. ARCHITECTURAL FOUNDATION & BOUNDARY PRESERVATION

### 1.1 Four-Tier Architecture Model
AntiOS Phase 27 strictly preserves the unidirectional four-tier architecture model established and proven through Phases 1–26:

```text
===================================================================================
                       TIER 1: GOOGLE ANTIGRAVITY PLATFORM
                               (Platform Mechanism)
  - Agent & Subagent Execution Lifecycle (invoke_subagent, manage_subagents, send_message)
  - Tool Runtimes (run_command via PowerShell/Bash, write_to_file, replace_file_content)
  - Hook Transport IPC (Stdio JSON-RPC for PreToolUse and Stop events)
  - Interactive Planning Mode (<planning_mode>, implementation_plan.md)
  - Immutable Logging (transcript.jsonl & transcript_full.jsonl)
  - Ambient Platform Capabilities (Native MCP Client, schedule timer/cron)
===================================================================================
                                        │
                                        ▼
===================================================================================
                             TIER 2: ANTIOS CORE
                            (Universal Governance)
  - Fail-Closed Path Guard Engine (framework/core/guard.py)
  - Physical Stop Gate Ratchet with OS Exit Code 0 (framework/core/gate.py)
  - Maker-Checker Protocol & Structured JSON Verdict (framework/core/verdict.py)
  - 10-Stage Task Lifecycle FSM (framework/core/lifecycle.py)
  - Persistent Memory & Token Distillation (framework/core/memory.py)
  - Deterministic Session Recovery & Contradiction Resolution (framework/core/recovery.py)
  - Working Tree Cleanliness & Merge Conflict Defense (framework/core/worktree.py)
  - Same Change Set Atomic Sync Policy (framework/core/changeset.py)
  - [NEW] Component Wayfinding & Locality Engine (framework/core/wayfinding.py)
  - [NEW] Agent-Oriented Subsystem Manifest Model (framework/core/subsystem.py)
  - [NEW] Syntactic Documentation Reference Auditor (framework/core/docaudit.py)
  - Universal Skills & Constitution (.agents/skills/, docs/AGENTS.md)
===================================================================================
                                        │
                                        ▼
===================================================================================
                           TIER 3: PROJECT ADAPTER
                            (Declarative Binding)
  - Configuration Manifest (antios.config.json)
  - Automated Discovery & Profiling (framework/core/discovery.py, profile.py)
  - [EXTENDED] Declarative Component & Subsystem Maps (components registry)
  - Protected Domain Paths (e.g. core/engine, migrations, rslib)
  - Concrete Test Runner Specifications (e.g. pytest, npm test, cargo test)
  - Workspace Monorepo Topology & Member Mappings (framework/core/topology.py)
  - Manifest Fingerprints (SHA256 tracking dependency drift)
===================================================================================
                                        │
                                        ▼
===================================================================================
                           TIER 4: TARGET PROJECT
                                (Domain Truth)
  - Application Source Code (TypeScript, Python, Rust, Go, C++, etc.)
  - Domain Semantics, Business Logic, and Schema Invariants
  - Native Compilers & Toolchains (tsc, cargo, vite, pyright)
  - Application Test Suites (Unit, Integration, E2E)
===================================================================================
```

### 1.2 Invariants of the Four-Tier Boundary
1. **Zero Domain Knowledge in Core**: AntiOS Core contains no application-specific keywords, paths, or rules. It remains 100% universal across any codebase.
2. **Zero Platform Mechanism Duplication**: AntiOS Core never spawns background daemons, implements custom process schedulers, or intercepts IPC directly; it defers mechanism to Antigravity.
3. **Fail-Closed by Construction**: Every security boundary, path check, and verification gate fails closed on error, missing configuration, or unexpected data types.
4. **Declarative Extension**: Project-specific behavior is governed strictly via Tier 3 (`antios.config.json`), proposed through automated discovery, and verified before adoption.

---

## 2. THE AUGMENTED AGENT-NATIVE ENGINEERING LIFECYCLE

In Phase 27, AntiOS elevates the engineering lifecycle from simple reactive task progression to a comprehensive 8-stage cognitive pipeline:

```text
  [ 1. UNDERSTAND ]  ──>  [ 2. LOCATE ]  ──>  [ 3. PLAN ]  ──>  [ 4. ACT ]
         │                       │                  │                │
         ▼                       ▼                  ▼                ▼
   Read Context &        Deterministic Wayfinding   Scoped Diff     Controlled
   Adapter Directives    Resolve Subsystem & Tests   Strategy      Single-Writer
                                                                         │
                                                                         ▼
  [ 8. RECOVER ]  <──  [ 7. REMEMBER ]  <──  [ 6. VERIFY ]  <──  [ 5. TEST ]
         ▲                       ▲                  ▲                │
         │                       │                  │                ▼
   Contradiction &       Distill Lessons &     Maker-Checker    Physical Runner
   Staleness Recovery    Durable Decisions     Fresh Eyes Audit   Exit Code 0
```

### 2.1 The Critical "LOCATE" Gate
Prior to Phase 27, agents jumped from `UNDERSTAND` directly to `PLAN`, forcing them to guess where files lived. Phase 27 introduces the mandatory **`LOCATE`** stage:
- **Input**: User prompt intent, bug description, or requested feature area.
- **Mechanism**: Deterministic lookup via `WayfindingEngine` (`navigate_repo.py`).
- **Output**: Bounded `LocalityResolution` block ($\le 20$ lines) injected into working context:
  * Responsible Subsystem & Component ID
  * Primary Entrypoints & Key Authoritative Files
  * Governing Invariants (What must NOT be touched)
  * Applicable Skills & Workflows
  * Covering Test Suites & Exact Runner Commands
  * Upstream Dependencies & Downstream Consumers (Blast Radius)
  * Required Documentation Files for Atomic Sync

---

## 3. SUBSYSTEM 1: COMPONENT WAYFINDING & LOCALITY ENGINE (`wayfinding.py`)

### 3.1 Design Principles
1. **Deterministic Resolution**: Zero vector databases, zero fuzzy embeddings, zero non-deterministic LLM lookups. Uses exact keyword indexing, prefix mapping, directory boundaries, and inverted file maps.
2. **Bounded Token Footprint**: Returns a compact resolution card ($\le 20$ lines) containing actionable paths and commands, preventing context bloat.
3. **Multi-Key Lookup**: Supports resolution by:
   - File Path (e.g. `src/auth/token.ts` $\to$ `auth` subsystem)
   - Component / Subsystem ID (e.g. `auth` or `billing`)
   - Natural Language Keyword / Intent Tokens (e.g. `"login"`, `"button"`, `"token"`)
   - Monorepo Member Name (e.g. `frontend-client`)

### 3.2 Data Models

```python
@dataclass(frozen=True)
class SubsystemDeclaration:
    """Declarative specification of a project subsystem."""
    subsystem_id: str
    name: str
    description: str
    area: str                                # e.g. "ui", "core", "api", "infra"
    root_paths: List[str]                   # e.g. ["src/auth", "lib/auth"]
    entrypoints: List[str]                  # e.g. ["src/auth/index.ts"]
    authoritative_files: List[str]          # Core files defining interface
    covering_tests: List[str]               # e.g. ["tests/test_auth.py"]
    test_commands: List[str]                # e.g. ["pytest tests/test_auth.py"]
    applicable_skills: List[str]            # e.g. ["antios-engineer"]
    applicable_workflows: List[str]         # e.g. ["FEATURE", "BUG"]
    governing_rules: List[str]              # e.g. ["Never bypass token expiration"]
    protected_invariants: List[str]         # Paths/symbols that must not be altered
    dependencies: List[str]                 # Subsystems this relies upon
    consumers: List[str]                    # Subsystems relying on this
    documentation_paths: List[str]          # e.g. ["docs/subsystems/auth.md"]
    keywords: List[str]                     # Search keywords for intent matching

@dataclass(frozen=True)
class LocalityResolution:
    """The actionable wayfinding response delivered to an agent."""
    query: str
    matched_subsystem_id: str
    confidence: float                       # 1.0 = exact path/id; 0.5-0.9 = keyword
    area: str
    entrypoints: List[str]
    authoritative_files: List[str]
    covering_tests: List[str]
    test_commands: List[str]
    applicable_skills: List[str]
    applicable_workflows: List[str]
    governing_rules: List[str]
    protected_invariants: List[str]
    dependencies: List[str]
    consumers: List[str]
    documentation_paths: List[str]
    blast_radius_summary: str
```

### 3.3 Progressive Context Rendering
When an agent or tool invokes wayfinding, the engine emits a formatted, high-density block:
```text
=== ANTIOS WAYFINDING LOCATOR ===
Subsystem:   auth (Identity & Session Management) [Area: backend]
Entrypoints: src/auth/service.py, src/auth/middleware.py
Tests:       pytest tests/auth/ (2 files: test_token.py, test_session.py)
Workflows:   BUG, FEATURE | Skills: antios-engineer, antios-debug
Invariants:  Immutable: src/auth/crypto.py (Never edit crypto primitives directly)
Consumers:   api_gateway, user_profile (Blast radius: Medium)
Docs:        docs/subsystems/auth.md (Must update on interface change)
=================================
```

---

## 4. SUBSYSTEM 2: AGENT-ORIENTED SUBSYSTEM MANIFEST MODEL (`subsystem.py`)

### 4.1 The Dual-Audience Documentation Paradigm
Project documentation typically suffers from one of two extremes:
1. Written solely for humans (rambling prose, outdated tutorials, missing exact file paths).
2. Written solely as raw code comments (invisible during high-level planning).

AntiOS establishes the **Agent-Oriented Subsystem Manifest Standard**:
- Resides as either a declarative JSON specification (`subsystem.json` / `antios.components.json`) or a structured Markdown header (`README.md` with YAML frontmatter).
- Answers the 10 canonical agent engineering questions deterministically.

### 4.2 Standard Subsystem Manifest Schema
```json
{
  "subsystem_id": "auth-engine",
  "name": "Authentication & Authorization Engine",
  "area": "security",
  "owner": "Security Team / Core Backend",
  "description": "Handles JWT issuance, OAuth2 flows, and role-based access control.",
  "root_paths": ["src/security/auth", "src/middleware/auth"],
  "entrypoints": ["src/security/auth/index.ts"],
  "authoritative_files": [
    "src/security/auth/token_service.ts",
    "src/security/auth/types.ts"
  ],
  "covering_tests": [
    "tests/security/auth_test.ts"
  ],
  "test_commands": [
    "npm test -- tests/security/auth_test.ts"
  ],
  "applicable_skills": ["antios-engineer", "antios-debug"],
  "applicable_workflows": ["BUG", "FEATURE", "REFACTOR"],
  "governing_rules": [
    "JWT secret must never be logged or serialized",
    "Token expiration must be explicitly tested"
  ],
  "protected_invariants": [
    "src/security/auth/crypto_primitives.ts"
  ],
  "dependencies": ["database", "redis-cache"],
  "consumers": ["api-gateway", "billing", "user-service"],
  "documentation_paths": [
    "docs/architecture/auth.md"
  ],
  "keywords": ["auth", "login", "jwt", "oauth", "token", "session", "permission"]
}
```

---

## 5. SUBSYSTEM 3: SYNTACTIC DOCUMENTATION REFERENCE AUDITOR (`docaudit.py`)

### 5.1 The Staleguard Layer 1 Principle
Documentation drift has historically been tackled via expensive, non-deterministic LLM-as-a-judge approaches (e.g. `driftee-ai/drift`), which introduce 30–60s latency, high API token costs, and 15–30% false positives.

AntiOS implements **Staleguard Layer 1 Syntactic Reference Auditing** (`framework/core/docaudit.py`):
1. **Deterministic Regex Extraction**: Extracts all backticked file paths (`` `path/to/file.ext` ``), markdown link targets (`[label](path/to/file)`), and command references from documentation files and subsystem manifests.
2. **Physical Disk Verification**: Validates every extracted path against physical disk using normalized path canonicalization and existence checks.
3. **Zero Token Cost & Sub-Second Speed**: Audits hundreds of documentation references across the entire repository in $<1.5$ seconds with **0% false positives**.
4. **Integration with Same Change Set & Stop Gate**:
   - `changeset.py` invokes `audit_documentation_references()` on modified documentation files.
   - If a modified documentation file introduces dead links, stale path references, or hallucinated file locations, the Stop Gate fails closed.

---

## 6. SUBSYSTEM 4: PROJECT DISCOVERY & ADAPTER EXTENSION

### 6.1 Automated Subsystem Discovery
`framework/core/discovery.py` is extended with `discover_subsystems()`:
- Scans repository directory structure across standard conventions:
  * `src/*`, `lib/*`, `packages/*`, `apps/*`, `services/*`, `modules/*`, `pkg/*`, `internal/*`.
- Heuristically pairs source directories with corresponding test directories:
  * `src/{name}/` $\longleftrightarrow$ `tests/test_{name}.py` or `tests/{name}/` or `{name}/**/*.test.ts`.
- Extracts keywords from directory basenames, README headers, and package manifests.
- Emits proposed `SubsystemDeclaration` entries in `AdaptationProposal`.

### 6.2 Declarative Adapter Schema Enhancement
`antios.config.json` is updated to include an optional `components` dictionary:
```json
{
  "version": "1.0",
  "project_name": "MyProject",
  "protected_zones": [".agents", "framework"],
  "test_runners": [...],
  "components": {
    "auth": {
      "name": "Auth Subsystem",
      "area": "core",
      "root_paths": ["src/auth"],
      "entrypoints": ["src/auth/service.py"],
      "covering_tests": ["tests/test_auth.py"],
      "test_commands": ["pytest tests/test_auth.py"],
      "applicable_skills": ["antios-engineer"],
      "governing_rules": ["Zero token leakage"],
      "dependencies": ["db"],
      "consumers": ["api"],
      "keywords": ["auth", "token", "jwt", "login"]
    }
  }
}
```

---

## 7. SUBSYSTEM 5: TOOLING ARCHITECTURE & MCP EVALUATION

### 7.1 The Tooling Tier Hierarchy
AntiOS strictly enforces the three-tier tooling hierarchy:

$$\text{NATIVE ANTIGRAVITY} \;\succ\; \text{ANTI OS SCRIPT / CLI} \;\succ\; \text{MCP}$$

1. **Native Antigravity Tools (Tier 1 - Highest Priority)**:
   - `view_file`, `replace_file_content`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`.
   - Native tools run with zero network overhead, direct IDE integration, and optimal latency.
2. **AntiOS CLI Scripts (Tier 2 - Deterministic Local Utilities)**:
   - Executed via `run_command` (e.g. `python framework/scripts/tools/navigate_repo.py --query "auth"`).
   - Zero external daemon dependencies, 100% offline, cross-platform Python standard library, instant execution.
3. **MCP Tooling (Tier 3 - Protocol Boundary)**:
   - Used when communicating with external protocol servers or providing an ambient MCP tool palette for IDEs that require it.

### 7.2 Rigorous MCP Protocol Evaluation
- **Why Python for Core Framework Logic**:
  Python standard library provides zero-dependency, robust cross-platform filesystem primitives, sub-second execution, deterministic testing via `unittest`, and zero build step.
- **When Node.js/TypeScript MCP Server is Justified**:
  An MCP server (`antios-mcp-server`) built in Node.js/TypeScript is useful strictly as a **decoupled protocol bridge** for external IDEs or environments that interact with AntiOS purely via JSON-RPC stdio.
  *Tools exposed*:
  * `antios_locate`: Query wayfinding engine for component locality.
  * `antios_inspect_subsystem`: Get full manifest and invariants for a subsystem.
  * `antios_audit_docs`: Execute Staleguard Layer 1 reference check.
  * `antios_get_state`: Read bounded `ACTIVE_CONTEXT.md`.
  * `antios_query_memory`: Retrieve past lessons tagged with a subsystem ID.
- **Architectural Boundary Invariant**:
  The MCP server must remain a **pure, decoupled read-only view layer**. AntiOS Core never depends on the MCP server. If the MCP server is absent, all capabilities remain 100% accessible via CLI scripts and native Python imports.

---

## 8. SUBSYSTEM 6: AGENT COORDINATION & SCOPED INVESTIGATION

### 8.1 Shallow Depth Law Preservation (Depth $\le 2$)
AntiOS strictly forbids deep recursive agent swarms. The hierarchy is capped at:
$$\text{Parent (Maker)} \;\longrightarrow\; \text{Child (Checker or Investigation Specialist)}$$

### 8.2 Investigation Specialist Delegation Pattern
For complex tasks touching unfamiliar multi-module areas:
1. **Delegation**: Parent dispatches an Investigation Specialist via `invoke_subagent`:
   * `TypeName='research'` (read-only tools) or `TypeName='self'` with read mandate.
   * Scoped prompt: *"Locate and inspect the subsystem owning auth. Run navigate_repo.py, view the entrypoint and test files, verify invariants, and return a Locality Handoff Report."*
2. **Handoff**: Subagent returns standard `Locality Handoff Report` containing file paths, line numbers, test commands, and invariants.
3. **Parent Synthesis**: Parent ingests the locality card, updates `ACTIVE_CONTEXT.md`, collapses the investigator, and proceeds to `PLAN`.

---

## 9. VERIFICATION CONTINUITY & STOP GATE INTEGRATION

All new Phase 27 capabilities are integrated directly with AntiOS's fail-closed verification gates:
1. **Stop Gate Ratchet (`gate.py`)**:
   - Executes dynamic test runners identified via subsystem wayfinding.
   - Verifies that modified subsystems pass their covering tests with OS exit code 0.
2. **Documentation Reference Gate (`docaudit.py` $\to$ `changeset.py`)**:
   - Verifies that any documentation added or modified during the task contains 0 dead file paths or broken references.
3. **Maker-Checker Context Stripping (`verdict.py`)**:
   - `prepare_checker_context()` includes the verified `LocalityResolution` so the Checker knows exact authoritative files, covering tests, and invariants to audit.

---

## 10. SUMMARY OF DELIVERABLES & INTERFACES

| Module / Artifact | Layer | Primary Responsibility | Interface / Entrypoint |
| :--- | :--- | :--- | :--- |
| `framework/core/wayfinding.py` | AntiOS Core | Component indexing, keyword search, locality resolution | `WayfindingEngine.locate()`, `resolve_file()` |
| `framework/core/subsystem.py` | AntiOS Core | Subsystem manifest schemas and validators | `SubsystemDeclaration`, `validate_manifest()` |
| `framework/core/docaudit.py` | AntiOS Core | Staleguard Layer 1 syntactic reference auditing | `audit_documentation_references()` |
| `framework/scripts/tools/navigate_repo.py` | AntiOS Script | CLI for agent wayfinding and locality queries | `python framework/scripts/tools/navigate_repo.py` |
| `framework/scripts/tools/audit_docs.py` | AntiOS Script | CLI for syntactic documentation reference auditing | `python framework/scripts/tools/audit_docs.py` |
| `framework/core/discovery.py` | Core Adapter | Extended static discovery for subsystems | `discover_subsystems()` in discovery pipeline |
| `antios-engineer` / `debug` | Core Skills | Updated with 8-stage lifecycle & wayfinding directive | `.agents/skills/antios-engineer/SKILL.md` |
| `tests/test_wayfinding.py` | Test Suite | Unit & integration tests for wayfinding engine | `python tests/run_all.py` |
| `tests/test_docaudit.py` | Test Suite | Unit & adversarial tests for doc reference auditor | `python tests/run_all.py` |
| `tests/test_phase27_integration.py` | Test Suite | End-to-end integration of wayfinding with Stop Gate | `python tests/run_all.py` |
