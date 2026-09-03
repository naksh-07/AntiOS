# AntiOS Capability Matrix & Layer Disposition (`ANTIOS_CAPABILITY_MATRIX.md`)

**Version**: 2.0.0-draft (Universal Re-baseline)  
**Date**: 2026-09-04  
**Status**: Canonical Capability Matrix & Layer Disposition  

---

## 1. Existing Capability Classification

Every capability identified across AntiOS Phase 1–11 outputs, Phase 12–15 foundation scripts, research reports, and codebase assets is classified below:

| # | Capability / Mechanism | Classification | Physical File / Location | Status & Evidence |
| :-: | :--- | :---: | :--- | :--- |
| **1** | Subagent Lifecycle & Isolation | **PLATFORM** | Antigravity Engine (`invoke_subagent`, `manage_subagents`) | Native Antigravity platform primitive. Fully verified. |
| **2** | Tool Execution Runtime | **PLATFORM** | Antigravity Engine (`run_command`, `write_to_file`, `replace_file_content`) | Platform primitive executing file mutations and host shell processes. |
| **3** | Hook Transport Mechanism | **PLATFORM** | Antigravity Stdio Hook IPC | Marshals `PreToolUse` and `Stop` JSON payloads over stdio to configured processes. |
| **4** | Interactive Planning Mode UI | **PLATFORM** | Antigravity Engine (`<planning_mode>`, `implementation_plan.md`) | Platform primitive rendering plan approvals and walkthrough artifacts. |
| **5** | Persistent Session Transcripts | **PLATFORM** | Antigravity Engine (`transcript.jsonl`, `transcript_full.jsonl`) | Platform primitive capturing chronological turns, tool calls, and model reasoning. |
| **6** | Background Timers & Schedulers | **PLATFORM** | Antigravity Engine (`schedule`) | Platform primitive managing one-shot timers and cron jobs. |
| **7** | Fail-Closed Path Guard Engine | **CORE** | `framework/core/guard.py` | Universal path canonicalization, ancestor isolation, self-protection, and 8.3 alias blocking. 234/234 tests passing. |
| **8** | Physical Stop Gate Verification | **CORE** | `framework/core/gate.py` | Universal subprocess execution requiring OS process exit code 0 and git merge conflict detection. |
| **9** | Maker-Checker Verdict Protocol | **CORE** | `framework/core/verdict.py` | Standardized data model and robust parser (raw JSON, codeblock, text fallback) for independent verifiers. |
| **10** | Universal Engineering Skill | **CORE** | `.agents/skills/antios-engineer/SKILL.md` | Injects universal engineering lifecycle, 3-tier risk matrix, shallow depth law, and stop gate discipline ($\le 60$ lines). |
| **11** | Independent Verifier Skill | **CORE** | `.agents/skills/antios-verifier/SKILL.md` | Injects fresh-context Checker contract, physical diff audit, and structured verdict reporting ($\le 60$ lines). |
| **12** | Root-Cause Debugging Skill | **CORE** | `.agents/skills/antios-debug/SKILL.md` | Injects deterministic 5-step debugging procedure ($\le 60$ lines). |
| **13** | Bounded Working Context State | **CORE** | `docs/ACTIVE_CONTEXT.md` | Bounded file-backed working set ($\le 60$ lines) preventing context amnesia. |
| **14** | Zero-Dependency Self-Test Harness| **CORE** | `tests/` (`run_all.py`, `test_guard.py`, etc.) | Pure standard-library test suite verifying AntiOS core and skill constraints. |
| **15** | Declarative Adapter Schema | **PROJECT-ADAPTER** | `antios.config.json` & `framework/core/config.py` | Decouples project-specific paths, patterns, and runners from core logic. |
| **16** | Test Runner Manifest Discovery | **PROJECT-ADAPTER** | `framework/core/gate.py` | Dynamic detection of `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`. |
| **17** | Protected Domain Paths & Patterns | **PROJECT-ADAPTER** | Declared in `antios.config.json` | Configurable array of repository-specific immutable paths and wildcard expressions. |
| **18** | `rslib/` Immutability Guard | **PROJECT-SPECIFIC** | Hardcoded entry in `antios.config.json` | StudyLab-specific Anki Rust core boundary. |
| **19** | `vitest:once` Runner Binding | **PROJECT-SPECIFIC** | Hardcoded entry in `antios.config.json` | StudyLab-specific frontend test command. |
| **20** | StudyLab Proving Ground Sandboxes | **PROJECT-SPECIFIC** | `sandbox/StudyLab/`, `_Control`, `_Treatment` | Isolated repository clones for empirical verification. |
| **21** | Automated Same Change Set Diff | **EXPERIMENTAL** | Proposed in `CAPABILITY_ARCHITECTURE.md` | Git diff inspection in Stop Gate to verify doc changes whenever code is touched. |
| **22** | Sandboxed Snapshot Captures | **EXPERIMENTAL** | Proposed in Phase 19 roadmap | Automated UI and database state snapshots during debugging. |
| **23** | Legacy `studylab-task-runner` | **OBSOLETE** | Formerly `framework/.agents/skills/` | Undiscoverable prototype skill. Pruned in Phase 12. |
| **24** | Cryptographic Receipts (`evidence/`) | **OBSOLETE** | Formerly `evidence/` | Suffer from **Ratchet Expiry**; replaced by real-time test execution. |
| **25** | Custom AST Regex Parsers | **OBSOLETE** | Prototype proposals | Brittle and inaccurate; replaced by native compilers (`tsc`, `pytest`). |
| **26** | Duplicate Schema Validators | **OBSOLETE** | Prototype proposals | Violates Bounded Context; replaced by native application compilers (`generate_apkg.py`). |
| **27** | `verify_task.py` Fallback Script | **OBSOLETE** | Formerly in `stop_gate.py` | Primary vector for test fabrication (`sys.exit(0)`). Excised in Phase 11. |
| **28** | Deep Hierarchical Agent Swarms | **OBSOLETE** | Prototype multi-tier proposals | Caused latency and context fragmentation. Excised by Shallow Depth Law ($\le 2$). |
| **29** | External GitHub MCP for Local Work | **OBSOLETE** | MCP catalog evaluation | Slower than native `git` CLI via `run_command`. Excised by `ANTIOS_MCP_POLICY.md`. |
| **30** | StudySourceCore Integration | **OBSOLETE** | Candidate MCP evaluation | **100% OUT OF SCOPE**. Permanently rejected. |
| **31** | Vector Memory Databases | **OBSOLETE** | Chroma/Pinecone proposals | Saturated context, non-deterministic retrieval. Excised in favor of markdown state. |
| **32** | Custom Agent Orchestrator Daemons | **OBSOLETE** | Autonomous agent runner proposals | Duplicates native Antigravity platform primitives. |

---

## 2. Universal Capability Layers: 16-Layer Disposition

| Layer | Disposition | Evidence & Rationale | Action for Universal Architecture |
| :--- | :---: | :--- | :--- |
| **1. Knowledge / Documentation** | **ADAPT** | Research proved uncurated docs cause context thrashing. 54KB of stale docs were purged in Phase 11. | Formalize 4-way separation: Core Specs, Project Policy, Agent State (`ACTIVE_CONTEXT.md`), and Generated Artifacts. Archive legacy reports. |
| **2. Skills** | **ADAPT** | Empirical trials proved 3 lean skills $\le 60$ lines (`antios-engineer`, `verifier`, `debug`) outperform 7 micro-skills. | Keep the 3 canonical skills. Decouple hardcoded StudyLab references (`rslib/`) into generic adapter-injected parameters. |
| **3. Workflows** | **KEEP** | 4 composed workflows (Feature Implementation, Bug-Fix, Verification, Doc Sync) were validated in Phase 14. | Codify workflows as standard operating procedures in Core specs. |
| **4. Rules / Constitution** | **ADAPT** | Compact `docs/AGENTS.md` (21 lines) successfully orients agents but currently contains StudyLab preamble. | Separate universal constitutional invariants (boundaries, test ratchets) from adapter-injected domain directives. |
| **5. Hooks / Enforcement** | **KEEP** | Dual-path `.agents/hooks.json` driving fail-closed Python hooks (`guard.py`, `gate.py`) is proven and tested (234/234 tests pass). | Retain as the primary deterministic enforcement foundation. |
| **6. MCP / Tooling** | **KEEP** | `ANTIOS_MCP_POLICY.md` established strict classifications: permits `chrome-devtools`, `playwright`, `gemini-api-docs`; mandates local `git` CLI; rejects `studysource-core`. | Retain policy. Build zero custom MCP servers. |
| **7. Project Intelligence** | **ADAPT** | Custom AST regex parsers failed. Native compilers (`tsc`, `pyright`, `cargo`) provide 100% ground truth. | Delegate code intelligence to native project compilers invoked through adapter commands. |
| **8. Project Adaptation** | **BUILD** | Phase 12 introduced `antios.config.json`, but Core fallbacks still hardcode StudyLab paths. | Formalize the complete Project Adapter Specification (`ANTIOS_CORE_VS_ADAPTER.md`) and purge domain fallbacks from Core. |
| **9. Task State** | **KEEP** | Bounded `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines) prevents context amnesia without database bloat. | Retain bounded task state discipline with anti-decay rules. |
| **10. Memory** | **KEEP** | Vector DBs proved opaque and failure-prone. Multi-tiered markdown + git history provides full transparency. | Retain 3-tier memory model (Short: context; Mid: `ACTIVE_CONTEXT.md` + `transcript.jsonl`; Long: git). Keep vector DBs rejected. |
| **11. Verification / Evidence** | **KEEP** | Physical process execution ratchet (exit code 0 on tests) completely eliminates hallucinated test approvals. | Retain physical process ratchet and git conflict checks. Keep static receipts rejected. |
| **12. Maker-Checker / Subagents** | **KEEP** | Maker-Checker with fresh context (`TypeName='self'`) on High Risk eliminates LLM confirmation bias. Shallow Depth Law ($\le 2$) prevents swarm runaway. | Retain Risk-Tiered Maker-Checker model and Shallow Depth Law. |
| **13. Impact Analysis** | **ADAPT** | AST-based blast radius was disproved. Native git diff analysis + test suite scoping is deterministic and robust. | Enforce impact analysis via `git diff --name-only` and scoped test runners. |
| **14. Agent Testing / Regression**| **BUILD** | Phase 9 generated a 22-vector attack matrix that proved hook vulnerabilities, but attacks are not yet an automated CI test suite. | Package Phase 9 attack vectors into an automated regression suite in `tests/`. |
| **15. Recovery** | **KEEP** | Clean git checkout/restore recovery and `ENVIRONMENT_UNAVAILABLE` runtime trapping are verified. | Retain fail-closed recovery and ambient environment diagnostic checks. |
| **16. Self-Improvement** | **DEFER** | Autonomous self-modification of core governance scripts risks destabilizing loops. | Keep self-improvement human-in-the-loop: forensic audits, test matrices, and deliberate phase upgrades. |

---

## 3. The Antigravity Boundary Separation

```text
+-----------------------------------------------------------------------------------+
|                            ANTIGRAVITY PROVIDES                                   |
|  - Agent Execution Runtime (Turn execution, token budgeting, context management)  |
|  - Subagent Isolation & Communication (invoke_subagent, manage_subagents)         |
|  - Tool Interception Transport (PreToolUse and Stop stdio JSON-RPC IPC)           |
|  - Interactive Planning Mode UI (<planning_mode>, implementation_plan.md)         |
|  - Immutable Turn & Tool Logging (transcript.jsonl, transcript_full.jsonl)        |
|  - Native Tool Execution (run_command, write_to_file, replace_file_content)       |
|  - Background Scheduling (schedule tool for timers and cron jobs)                 |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+------------------------------------------+----------------------------------------+
|                               HYBRID CONTRACT                                     |
|  - Hook IPC: Antigravity provides stdio IPC <-> AntiOS provides hook logic        |
|  - Stop Gate: Antigravity intercepts Stop <-> AntiOS evaluates test subprocess    |
|  - Maker-Checker: Antigravity spawns subagent <-> AntiOS injects verifier contract|
|  - Planning Mode: Antigravity renders UI <-> AntiOS skills enforce risk-tiering   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+------------------------------------------+----------------------------------------+
|                              ANTIOS PROVIDES                                      |
|  - Fail-Closed Path Guards (framework/core/guard.py)                              |
|  - Physical Test Ratchet & Merge Conflict Check (framework/core/gate.py)          |
|  - Maker-Checker Verdict Protocol & Parser (framework/core/verdict.py)            |
|  - Universal Engineering Skills (.agents/skills/antios-engineer, verifier, debug) |
|  - Universal Project Constitution (docs/AGENTS.md)                                |
|  - Bounded Active State Ledger (docs/ACTIVE_CONTEXT.md <= 60 lines)               |
|  - Zero-Dependency Self-Test Harness (tests/run_all.py)                           |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+------------------------------------------+----------------------------------------+
|                              PROJECT PROVIDES                                     |
|  - Application Source Code & Architecture                                         |
|  - Domain Schemas, Invariants, and Business Contracts                             |
|  - Native Compilers, Linters, and Typecheckers (tsc, cargo, ruff, pyright)        |
|  - Application Test Suites (vitest, pytest, cargo test, go test)                  |
|  - Repository Documentation & Domain Specs                                        |
+-----------------------------------------------------------------------------------+
```

### 3.1 Defense-in-Depth Comparison for the Platform Shell Gap

| Action | Antigravity Platform Interception | AntiOS Defense Mechanism | Outcome |
| :--- | :---: | :---: | :---: |
| **IDE Tool Mutation** (`replace_file_content` targeting protected path) | **INTERCEPTED** via `PreToolUse` hook | `guard.py` evaluates canonical path prefix and emits `deny` | Mutation **BLOCKED** immediately; tool does not execute. |
| **Direct Shell Mutation** (`run_command` PowerShell write to protected path) | **NOT INTERCEPTED** (bypasses IDE hooks) | `gate.py` runs `git diff --name-only` at Stop Gate; blocks task completion | Task **BLOCKED** from closing; agent forced to revert unauthorized changes. |
| **Corrupted Code Mutation** (Agent introduces syntax or logical error) | **NOT INTERCEPTED** | `gate.py` executes native test runner; non-zero exit blocks completion | Task **BLOCKED** until all native tests pass cleanly. |
| **Merge Conflict Mutation** (Agent leaves conflict markers in source) | **NOT INTERCEPTED** | `gate.py` runs `git diff --check`; detects conflict markers and blocks | Task **BLOCKED** until conflict markers are resolved. |
