# AntiOS Capability Matrix & Layer Disposition (`ANTIOS_CAPABILITY_MATRIX.md`)

**Version**: 1.0.0-GA  
**Date**: 2026-09-04  
**Status**: Authoritative Canonical Capability Matrix (766 Tests Certified)  

---

## 1. Capability Layering & Layer Disposition

Every capability in AntiOS is mapped across 18 cohesive architectural layers:

| Layer | Classification | Implementing Modules / Assets | Test Coverage | Status & Disposition |
| :--- | :---: | :--- | :---: | :--- |
| **1. Platform IPC & Hooks** | Platform | `.agents/hooks.json`, `pre_tool_guard.py`, `stop_gate.py` | 14 tests | **CERTIFIED**: Fail-closed stdio transport. |
| **2. Path Guard & Boundaries** | Core | `framework/core/guard.py` | 22 tests | **CERTIFIED**: Canonical path resolution, ancestor containment, 8.3 alias prevention. |
| **3. Process Test Ratchet** | Core | `framework/core/gate.py` | 28 tests | **CERTIFIED**: Physical OS process exit code 0 requirement; merge conflict detection. |
| **4. Maker-Checker Verification** | Core | `framework/core/verdict.py` | 16 tests | **CERTIFIED**: Structured JSON verdict schema and robust multi-format parser. |
| **5. Task Lifecycle & FSM** | Core | `framework/core/lifecycle.py` | 18 tests | **CERTIFIED**: 10-stage state machine with illegal transition blocking. |
| **6. Working Memory & State** | Core | `docs/ACTIVE_CONTEXT.md`, `memory.py` | 24 tests | **CERTIFIED**: Strictly bounded <= 60 lines; anti-decay rules; dead-end memory. |
| **7. Same Change Set Discipline**| Core | `framework/core/changeset.py` | 12 tests | **CERTIFIED**: Atomic synchronization of code, tests, and documentation. |
| **8. Worktree Cleanliness** | Core | `framework/core/worktree.py` | 10 tests | **CERTIFIED**: Isolates staged, unstaged, and untracked modifications cleanly. |
| **9. Project Intelligence** | Adapter | `framework/core/discovery.py`, `profile.py` | 32 tests | **CERTIFIED**: Zero-code discovery across Python, TS/JS, Go, Rust. |
| **10. Declarative Project Adapter**| Adapter | `antios.config.json`, `adapter.py`, `config.py` | 26 tests | **CERTIFIED**: Schema-validated configuration; zero Core code mutations. |
| **11. Monorepo Topology Graph** | Adapter | `framework/core/topology.py` | 18 tests | **CERTIFIED**: Member-scoped verification and shared root escalation. |
| **12. Component Wayfinding** | Core | `framework/core/wayfinding.py` | 22 tests | **CERTIFIED**: Deterministic keyword/prefix indexing; < 20ms resolution. |
| **13. Subsystem Manifests** | Core | `framework/core/subsystem.py` | 16 tests | **CERTIFIED**: Agent-oriented subsystem schema with entrypoints and invariants. |
| **14. Syntactic Doc Drift Audit**| Core | `framework/core/docaudit.py` | 14 tests | **CERTIFIED**: Zero-token disk path validation with 0% false positives. |
| **15. Knowledge Graph Engine** | Core | `framework/core/knowledge.py` | 28 tests | **CERTIFIED**: In-memory multi-index graph, BFS reachability, L0-L5 disclosure. |
| **16. Capability Routing Layer** | Core | `framework/core/capability*.py` | 44 tests | **CERTIFIED**: 8 capability types, 5-tier rule precedence, bounded cards <= 25 lines. |
| **17. Agent Topology Registry** | Core | `framework/core/agent_*.py`, `workflow.py` | 52 tests | **CERTIFIED**: Canonical roles, least-privilege boundaries, Shallow Depth Law <= 2. |
| **18. Tool & Provider Engine** | Core | `framework/core/tool*.py`, `provider.py` | 77 tests | **CERTIFIED**: 8-tier hybrid capability matrix, in-memory registry, canonical MCP justification. |

---

## 2. Canonical Skill Inventory (`.agents/skills/`)

All active skills adhere strictly to the token efficiency budget:
1. `antios`: Universal project-native control plane and primary entrypoint.
2. `antios-engineer`: Universal engineering workflow, 3-tier risk matrix, and stop gate discipline.
3. `antios-verifier`: Independent Maker-Checker audit contract and structured verdict generation.
4. `antios-debug`: Systematic 5-step root-cause debugging procedure.
5. `antios-adapt-project`: Universal project intelligence and adaptation procedure.

---

## 3. Permanent Exclusions & Obsolete Concepts

The following concepts have been permanently rejected or excised from AntiOS:
- **StudySourceCore**: 100% OUT OF SCOPE.
- **Custom Agent Daemons & Swarms**: Rejected in favor of native Antigravity primitives.
- **Vector Memory Databases**: Rejected in favor of deterministic file-backed memory.
- **Regex AST Parsers**: Rejected in favor of native project toolchains.
- **Verify Task Script Fallback**: Excised to prevent test fabrication.
- **Deep Agent Hierarchies**: Bounded by Shallow Depth Law ($\le 2$).
