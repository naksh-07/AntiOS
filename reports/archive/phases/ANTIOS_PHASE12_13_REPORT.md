# AntiOS Phase 12–13 Report: Architecture Re-baseline & Universal Core Design (`ANTIOS_PHASE12_13_REPORT.md`)

**Milestone**: Phases 12–13 (Architecture Re-baseline & Core Design)  
**Date**: 2026-09-04  
**Project**: AntiOS Universal  
**Status**: COMPLETE & CANONICALLY BASELINED  

---

## 1. Executive Summary & Current-State Assessment

Phase 12–13 establishes the formal architectural re-baseline of AntiOS, defining its identity as a **UNIVERSAL, reusable Agent-Native Engineering OS for Google Antigravity**.

AntiOS is structured as a 4-tier system:
$$\text{Antigravity Platform} \;\longrightarrow\; \text{AntiOS Core} \;\longrightarrow\; \text{Project Adapter} \;\longrightarrow\; \text{Target Project}$$

### Current-State Assessment:
1. **Foundation Maturity**: AntiOS possesses a hardened, fail-closed governance core (`framework/core/`) and platform hook bridges (`framework/scripts/hooks/`) with 100% test pass rate (18/18 unit tests, <1.0s runtime) and zero third-party dependencies.
2. **Proving Ground Demarcation**: StudyLab served as the critical testing proving ground that exposed edge cases (Windows 8.3 alias bypasses, fail-open lockups, test forgery vectors). However, StudyLab is **NOT AntiOS's permanent domain boundary**.
3. **Coupling Status**: Phase 12 successfully introduced declarative configuration (`antios.config.json`). The re-baseline identified 4 residual domain couplings (hardcoded `rslib` and `vitest:once` defaults in `framework/core/config.py`, StudyLab preambles in `docs/AGENTS.md`, and skill examples), and established the formal remediation plan in `ANTIOS_CORE_VS_ADAPTER.md`.
4. **Boundary Compliance**: StudySourceCore remains 100% out of scope (0 files accessed, 0 tools integrated). Production StudyLab code remains completely untouched.

---

## 2. Missing Capabilities vs Speculative Bloat

An essential insight from Phase 6–11 research is that **adding features merely because another agent framework has them is catastrophic to reliability and token efficiency**.

| Capability Proposed in Past Research | Actual Necessity | Architectural Disposition |
| :--- | :---: | :--- |
| **Declarative Project Adapter Schema** | **CRITICAL** | **JUSTIFIED (BUILT)**: Necessary to decouple Core governance from repository-specific paths, test runners, and file types. |
| **Adversarial Regression Test Harness** | **HIGH** | **JUSTIFIED (ROADMAP)**: Automated CI regression suite validating the 22 Phase 9 attack vectors against hooks. |
| **Automated Same Change Set Diff Check** | **HIGH** | **JUSTIFIED (ROADMAP)**: Git diff inspection in Stop Gate to ensure documentation changes accompany code modifications. |
| **Vector Memory Databases (Chroma/Pinecone)** | **ZERO** | **SPECULATIVE BLOAT (PERMANENTLY REJECTED)**: Opaque retrieval, dependency bloat, context saturation. Replaced by bounded `ACTIVE_CONTEXT.md` ($\le 60$ lines). |
| **Custom AST Regex Blast-Radius Parsers** | **ZERO** | **FRAGILE (PERMANENTLY REJECTED)**: Misses dynamic imports and complex syntax. Replaced by native compilers (`tsc`, `pyright`, `cargo`). |
| **Duplicate Schema Validators** | **ZERO** | **REDUNDANT (PERMANENTLY REJECTED)**: Duplicates domain logic and violates Bounded Context. Native compilers (`generate_apkg.py`) validate schemas. |
| **Cryptographic Hash Receipts (`evidence/`)** | **ZERO** | **FLAWED (PERMANENTLY REJECTED)**: Suffers from **Ratchet Expiry**; subsequent edits invalidate hashes. Real-time OS process execution (`gate.py`) provides superior proof. |
| **Arbitrary `verify_task.py` Fallback** | **NEGATIVE** | **SECURITY VULNERABILITY (PERMANENTLY EXCISED)**: Primary vector for test forgery (`sys.exit(0)`). |
| **Large Hierarchical Agent Swarms (>2-3 agents)**| **NEGATIVE** | **INEFFICIENT (PERMANENTLY REJECTED)**: 120s+ latency, runaway token costs. Shallow Depth Law ($\le 2$) strictly enforced. |

---

## 3. Master Architectural Decision Records (ADRs 01–12)

- **ADR 01: The 4-Tier Hierarchy**: Platform $\to$ Core $\to$ Adapter $\to$ Project. Clear demarcation of responsibilities.
- **ADR 02: Fail-Closed Standard**: Invariant that any missing parameter, exception, or parse failure must deny mutating actions and block completion.
- **ADR 03: Platform Hook Limitation Law & Shell Gap Defense**: Hooks intercept IDE tool calls, not raw shell syscalls. Safety is guaranteed via 3-layer defense-in-depth (Constitution $\to$ PreToolUse Guard $\to$ Stop Gate Ratchet).
- **ADR 04: Process-Level Verification Ratchet**: No task completion without physical OS test process execution (exit code 0) against the exact working tree.
- **ADR 05: Risk-Tiered Maker-Checker Model**: Low Risk = solo; Medium Risk = self-verify; High Risk = mandatory fresh-context Checker (`TypeName='self'`).
- **ADR 06: Shallow Depth Law**: Subagent nesting depth is strictly $\le 2$ (Parent $\to$ Child). Subagents are strictly forbidden from spawning child agents.
- **ADR 07: Token Efficiency Budget**: All skills must adhere to a strict $\le 60$-line limit. Active context files must adhere to $\le 60$ lines.
- **ADR 08: Universal Adapter Abstraction**: Core governance operates on abstract strings and command arrays. Project-specific paths (`rslib`) and runners are declared in `antios.config.json`.
- **ADR 09: Native Toolchain Ground Truth**: AntiOS never replaces or mocks native compilers (`tsc`, `cargo`, `pytest`).
- **ADR 10: Pure Standard-Library Core**: AntiOS Core runs entirely on standard Python 3.8+ with zero third-party dependencies.
- **ADR 11: Permanent Exclusion of StudySourceCore**: StudySourceCore is 100% out of scope.
- **ADR 12: Bounded Markdown State Over Databases**: Rejection of vector databases and JSON journals in favor of transparent, version-controlled markdown state.

---

## 4. Antigravity vs AntiOS Boundaries

```text
===================================================================================
                       ANTIGRAVITY PLATFORM PRIMITIVES
===================================================================================
  1. Agent Lifecycle & Context: invoke_subagent, manage_subagents, send_message.
  2. Hook Transport: Stdio JSON-RPC IPC marshaling PreToolUse and Stop payloads.
  3. Tool Execution: run_command, write_to_file, replace_file_content.
  4. Planning Mode UI: Native <planning_mode> rendering and approval flow.
  5. Session Logging: Immutable transcript.jsonl turn-by-turn capture.
  6. Scheduling: schedule tool for background timers and cron events.
                                        │
                                        ▼ (Stdio JSON-RPC IPC)
===================================================================================
                            ANTIOS GOVERNANCE CORE
===================================================================================
  1. Fail-Closed Path Guards: Canonical path resolution & ancestor isolation.
  2. Stop Gate Ratchet: OS subprocess test execution & git conflict detection.
  3. Maker-Checker Protocol: Structured JSON verdict parsing and reporting.
  4. Engineering Skills: Operational governance and 5-step root-cause debugging.
  5. Bounded State Discipline: docs/ACTIVE_CONTEXT.md rolling operational ledger.
  6. Self-Test Harness: Pure Python standard library verification test suite.
                                        │
                                        ▼ (Declarative Manifest)
===================================================================================
                            PROJECT ADAPTER BINDING
===================================================================================
  1. antios.config.json: Declarative schema binding domain paths & test runners.
  2. Manifest Auto-Detection: Dynamic detection of package.json, pyproject.toml, etc.
  3. Linters & Change Set Rules: Code quality and doc-code co-modification rules.
===================================================================================
```

---

## 5. Core vs Adapter Boundary

- **AntiOS Core (`framework/core/`)**:
  - Contains zero domain terms (`rslib`, `vitest:once`, `APKG`).
  - Implements universal path canonicalization, prefix matching, 8.3 alias blocking, and subprocess test orchestration.
  - Fallback defaults protect `.agents/`, `framework/`, and `antios.config.json`, and rely on dynamic manifest detection.
- **Project Adapter (`antios.config.json`)**:
  - Declarative configuration file in the target workspace root.
  - Maps concrete immutable paths (`protected_domain_paths`), wildcard expressions (`forbidden_patterns`), test commands (`test_runners`), and linters (`linters`).

---

## 6. Proposed `.agents/` Architecture

Every component in `.agents/` has an empirical, functional justification. No directories exist merely for aesthetics:

```text
.agents/
├── hooks.json                      # [PLATFORM CONFIG] Registers PreToolUse & Stop hooks
└── skills/                         # [PLATFORM DISCOVERY] Native Antigravity skill directory
    ├── antios-engineer/
    │   └── SKILL.md                # [CORE SKILL] Workflow, risk tiers, shallow depth (35 lines)
    ├── antios-verifier/
    │   └── SKILL.md                # [CORE SKILL] Fresh-context Checker contract (49 lines)
    └── antios-debug/
        └── SKILL.md                # [CORE SKILL] Systematic 5-step debugging procedure (36 lines)
```

### Placement Principles:
1. **Platform Hook Config**: `.agents/hooks.json` must reside directly in `<workspace_root>/.agents/` for Antigravity engine discovery.
2. **Skill Discovery**: Skills must reside in `<workspace_root>/.agents/skills/` to be indexed by Antigravity.
3. **No Redundant Files**:
   - `docs/AGENTS.md` resides in `docs/` as the project constitution (human-authored).
   - `docs/ACTIVE_CONTEXT.md` resides in `docs/` as the bounded task state (agent-maintained).
   - `tests/` resides in repository root as the framework verification harness.
   - `framework/core/` resides in `framework/` as the modular governance engine.

---

## 7. What from Phase 11 Survives vs What Gets Deprecated

### What Survives (The Hardened Core):
1. **Fail-Closed Hook Architecture**: Intercepts `write_to_file` and `replace_file_content`.
2. **Canonical Path Guard**: `os.path.commonpath` prefix matching, `os.path.realpath`, and 8.3 alias prevention.
3. **Physical Process Test Ratchet**: Required OS process exit code 0 on tests before task completion.
4. **Three Canonical Skills**: `antios-engineer`, `antios-verifier`, and `antios-debug` adhering strictly to $\le 60$ lines.
5. **Bounded Task State Model**: `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines) with anti-decay conventions.
6. **Maker-Checker Verdict Protocol**: Structured JSON reporting with fallback heuristics.
7. **18-Test Unit Suite**: Standard library verification harness in `tests/`.

### What Gets Deprecated / Decoupled:
1. **Hardcoded Fallback Defaults in `config.py`**: Removing hardcoded `"rslib"` and `"vitest:once"` from dataclass defaults; replacing with generic fallbacks and dynamic manifest scanning.
2. **StudyLab Preamble in `docs/AGENTS.md`**: Modularizing the constitution into universal laws and adapter-injected domain sections.
3. **Root Report Duplicates**: Archiving historical milestone reports out of root into structured documentation.

---

## 8. What New Components Are Justified

1. **Formal Project Adapter Schema (`antios.config.json`)**: Formally specified in `ANTIOS_CORE_VS_ADAPTER.md` to support multi-language ecosystems (TypeScript, Python, Rust, Go).
2. **Dynamic Manifest Scanner**: Auto-detects `package.json`, `pyproject.toml`, `Cargo.toml`, and `go.mod` when explicit runner config is absent.
3. **Automated Adversarial Regression Test Suite (Roadmap Phase 18)**: Converts Phase 9's 22-vector attack matrix into automated unit tests.
4. **Dynamic Same Change Set Checker (Roadmap Phase 17)**: Stop Gate git diff inspection ensuring documentation updates accompany code changes.

---

## 9. Open Questions & Risk Analysis

### Open Questions:
1. **Platform Hook Expansion for Shell Commands**: Will future Google Antigravity platform releases support `PreToolUse` interception for `run_command`?  
   *Current Mitigation*: 3-layer defense-in-depth (Constitution $\to$ Tool Guard $\to$ Stop Gate diff inspection).
2. **Cross-Repository Deployment Model**: How will AntiOS be distributed to external repositories?  
   *Recommendation*: Distribute AntiOS as a lightweight template or Git submodule containing `.agents/` and `framework/core/`, initialized via `antios init`.

### Risks & Mitigations:
| Risk | Severity | Mitigation |
| :--- | :---: | :--- |
| **Shell Command File Write Bypass** | Medium | Stop Gate inspects `git diff` against protected paths before approving completion. |
| **Missing Host Runtimes** | Low | Stop Gate traps `FileNotFoundError` and reports `ENVIRONMENT_UNAVAILABLE` rather than false test failures. |
| **Context Degradation from Large Skills** | High | Enforced strict $\le 60$-line token budget across all skills in `.agents/skills/`. |
| **Agent Confirmation Bias** | High | Maker-Checker protocol mandates fresh-context Checker (`TypeName='self'`) on high-risk modifications. |

---

## 10. Recommended Implementation Order (Phases 14–20)

```text
Phase 12-13 (CURRENT): Architecture Re-baseline & Core Design (COMPLETE)
       │
       ▼
Phase 14: Core Decoupling & Adapter Engine Hardening
       - Purge hardcoded rslib / vitest defaults from framework/core/config.py
       - Implement dynamic manifest scanner in framework/core/gate.py
       - Update tests/ to verify zero-config and multi-language adapter loading
       │
       ▼
Phase 15: Skill & Constitution Generalization
       - Modularize docs/AGENTS.md into Universal Laws + Adapter Domain Section
       - Parameterize skill prompt examples (.agents/skills/) to reference adapter terms
       │
       ▼
Phase 16: Multi-Language Adapter Validation & Proving Ground Binding
       - Validate adapters on StudyLab (TS/Svelte/Rust), Python (FastAPI), and Go
       - Hook StudyLab's Rust test runner (cargo test in rslib) into antios.config.json
       │
       ▼
Phase 17: Automated Same Change Set Git Diff Enforcement
       - Implement git diff inspection in stop_gate.py verifying doc sync
       │
       ▼
Phase 18: Adversarial Regression Pipeline
       - Package Phase 9 attack matrix (22 vectors) into automated test suite in tests/
       │
       ▼
Phase 19: Sandboxed Snapshot Debugging Extension
       - Connect antios-debug to automated environment snapshot captures
       │
       ▼
Phase 20: Production Benchmarking & Release 2.0
       - End-to-end task benchmarking comparing AntiOS vs unconstrained agents
```
