# AntiOS v1 Capability Disposition (`ANTIOS_V1_CAPABILITY_DISPOSITION.md`)

**Date**: 2026-09-04  
**Author**: Antigravity & AntiOS Architecture Team  
**Governing Axiom**:
> *"If Antigravity provides the mechanism $\to$ USE THE PLATFORM.*  
> *If the language/compiler/test framework provides verification $\to$ USE THE NATIVE TOOLCHAIN.*  
> *If StudyLab already owns a domain contract $\to$ DEFER TO STUDYLAB.*  
> *AntiOS owns: PROJECT POLICY, SAFETY BOUNDARIES, ENGINEERING WORKFLOW, VERIFICATION POLICY, TASK STATE, AGENT GOVERNANCE."*  
> *"Prototype ko bachana nahi hai. AntiOS ko bachana hai."*

---

## 1. Disposition Taxonomy

Every capability discovered and tested across Phases 6–10 is classified under one authoritative decision:
- **`PLATFORM`**: Native mechanism provided by the Antigravity engine. AntiOS must never rebuild it.
- **`STUDYLAB`**: Domain truth, schema, or test harness owned by the StudyLab project. AntiOS must not absorb or duplicate it.
- **`KEEP`**: Survived empirical testing without significant change. Retained in v1 core.
- **`ADAPT`**: Conceptually sound and empirically proven, but prototype implementation failed or contained vulnerabilities; must be redesigned for v1.
- **`REMOVE`**: Failed empirical testing, added unacceptable friction, created severe security vulnerabilities, or proved to be architectural bloat.
- **`ADD`**: Essential new mechanism required by empirical evidence from Phases 9 and 10 to close security or operational holes.
- **`DEFER`**: Theoretically attractive idea that is not currently required for immediate StudyLab safety and lacks conclusive empirical justification.

---

## 2. Master Capability Disposition Matrix

| # | Capability | Empirical Evidence (Phases 7–10) | Decision | Architectural Rationale |
| :-: | :--- | :--- | :---: | :--- |
| **1** | **Subagent Runtime Lifecycle** | Phase 10 Audit Q31 (`ANTIOS_FINAL_CAPABILITY_MAP.md`): Antigravity natively creates, isolates, monitors, and terminates subagents with segregated context windows. | **`PLATFORM`** | Building custom agent daemons, background IPC runners, or process trees duplicates Google Antigravity core primitives. AntiOS governs *when* and *why* to delegate, not *how* agents run. |
| **2** | **Tool Interception Engine** | Phase 10 Audit Q32: Platform engine intercepts tool calls (`PreToolUse`) and completion attempts (`Stop`), piping structured JSON over stdio. | **`PLATFORM`** | Tool interception is a native platform mechanism. AntiOS provides the validation scripts and denial reasons. |
| **3** | **Immutable Audit Logging** | Phase 10 Audit Q33: Persistent chronological JSONL logging (`transcript.jsonl`) is tamper-proof and maintained by the platform. | **`PLATFORM`** | Custom execution journals or logging databases duplicate Antigravity's native transcript stream. |
| **4** | **Background Scheduling & Daemons** | Phase 10 Audit Q34: `schedule` tool provides one-shot timers and recurring cron jobs natively. | **`PLATFORM`** | AntiOS does not require custom background cron workers or persistent daemon processes. |
| **5** | **Interactive Planning Mode** | Phase 10 Audit Q4 & Q35: Native `<planning_mode>` provides research $\to$ plan $\to$ user approval $\to$ execute $\to$ verify workflow natively. | **`PLATFORM`** | AntiOS skills must not duplicate Antigravity's native planning lifecycle; skills must strictly provide non-native project policies. |
| **6** | **Shell Command Execution** | Phase 9 Attack 3.3 (`SECURITY_ADVERSARIAL_REPORT.md`): `run_command` bypasses `write_to_file` hooks completely because Antigravity executes raw shell strings. | **`PLATFORM`** | Shell execution is an execution primitive with an inherent platform boundary limitation. IDE tool hooks cannot deterministically parse arbitrary shell strings. Document this boundary explicitly. |
| **7** | **MCP Client Transport** | Phase 10 Audit Q37: Stdio protocol framing, JSON-RPC transport, and tool schema registration are natively handled by Antigravity. | **`PLATFORM`** | AntiOS consumes MCP servers via standard configuration; it does not build custom client transport libraries. |
| **8** | **StudyLab Domain Schemas & Invariants** | Phase 8 Decision 5 (`DECISION_REGISTER.md:L60`): 20-field source question schema, double SQLite logic, and reviewer FSM reside in StudyLab. | **`STUDYLAB`** | AntiOS must not duplicate domain schemas in separate Python validators. Domain correctness is governed by StudyLab's native compiler and test suites. |
| **9** | **Source $\to$ APKG Generation & Validation** | Phase 8 Report (`PHASE_8_REPORT.md:L23`): `generate_apkg.py` natively validates cards and compiles packages with exact domain semantics. | **`STUDYLAB`** | AntiOS must defer package generation and domain validation to StudyLab's existing toolchain. |
| **10** | **Application Unit & E2E Test Suites** | Phase 9 & 10 Audit: TypeScript Vitest/Playwright tests (`ts/tests/`) and Rust tests provide native ground truth. | **`STUDYLAB`** | AntiOS provides the verification gate policy; the actual assertions and domain coverage belong entirely to StudyLab. |
| **11** | **Upstream Core Boundary Guard (`rslib/`)** | Phase 9 Attack 2.1 & Phase 10 Audit: `pre_tool_guard.py` achieved 100% interception of direct and path traversal mutations to `rslib/` via IDE tools. | **`KEEP`** | Absolute necessity for StudyLab safety. Prevents LLM hallucinations from corrupting upstream Anki core engine. |
| **12** | **Physical Process Test Ratchet** | Phase 9 Attack 4.1 & Phase 10 Audit: `stop_gate.py` executing actual OS test processes eliminated 100% of conversational LLM self-certification ("Looks good to me"). | **`KEEP`** | Core pillar of AntiOS verification. The completion gate must physically execute tests and demand exit code 0. |
| **13** | **Global Project Constitution (`AGENTS.md`)** | Phase 7 & 9 Trials: Concise ($\le 120$ lines) prompt rules orient resuming agents and bound attention to valid directories. | **`KEEP`** | Essential high-level governance layer. Must be kept compact and backed by deterministic code hooks for critical boundaries. |
| **14** | **Bounded Memory Bank (`ACTIVE_CONTEXT.md`)** | Phase 7 Trial: File-backed working set enabled recovery after context wipes. (Phase 10 proved decay occurs if unmaintained). | **`ADAPT`** | Retained, but redesigned with strict line budget ($\le 60$ lines) and clear conventions to prevent stale-state deception. |
| **15** | **Dynamic Native Test Discovery** | Phase 8 & 9: Auto-discovering `package.json` (`vitest:once`) and `pyproject.toml` (`pytest`) succeeded on standard repos. | **`ADAPT`** | Redesign in `stop_gate.py` to add process timeouts (`timeout=60`), shell escaping safety, and explicit multi-runner support. |
| **16** | **PreToolUse Hook Security Logic** | Phase 9 & 10 Audit: Injected type errors caused `pre_tool_guard.py` to fail open (`decision: allow`); empty workspace caused bypass; `framework` segment caused 100% false positives. | **`ADAPT`** | Must be rewritten from scratch to be strictly **FAIL-CLOSED**, use `os.path.commonpath` for prefix matching, and resolve Windows 8.3 aliases. |
| **17** | **Hook Self-Protection** | Phase 9 Attack 3.2: Edits to `.agents/hooks.json` were allowed, allowing agents to silently disable hooks. | **`ADAPT`** | Expand `pre_tool_guard.py` to protect `.agents/hooks.json` and hook scripts unconditionally against IDE tool modification. |
| **18** | **AntiOS Engineering Skill** | Phase 10 Audit Q1 & Q3: `studylab-task-runner` was buried in `framework/` (100% undiscoverable by Antigravity), recommended read-only `research` subagent, and duplicated native planning mode. | **`ADAPT`** | Replace with lean, discoverable `.agents/skills/antios-engineer/` in workspace root. Focus strictly on non-native workflow: Maker-Checker trigger, boundary safety, and test ratchet. |
| **19** | **Maker-Checker Verification Pattern** | Phase 7 & 9 Trials: Fresh-eyes subagent eliminated 100% confirmation bias, but incurred token/latency penalties on trivial tasks. | **`ADAPT`** | Implement risk-tiered Maker-Checker: Mandatory for High-Risk domain changes; optional/self-check for Low-Risk trivial changes (typos/docs). Verifier must use `TypeName='self'`. |
| **20** | **Environment Error Diagnosis** | Phase 9 Attack 1.3: Missing ambient binaries (`yarn`, `node`) caused `stop_gate.py` to report "TypeScript tests did not pass", trapping agent in retry loop. | **`ADAPT`** | Update `stop_gate.py` to catch `FileNotFoundError` or runner startup crashes and report `ENVIRONMENT_UNAVAILABLE` rather than test failure. |
| **21** | **`verify_task.py` Fallback Test Runner** | Phase 9 Attack 4.3 & Phase 10 Audit: Hardcoded script fallback allowed trivial test forgery (`sys.exit(0)`), completely bypassing verification. | **`REMOVE`** | **PERMANENTLY REMOVED**. All verification must run through registered, native project test suites. |
| **22** | **External GitHub MCP Server** | Phase 8 Report & Phase 10 Audit: Redundant with local `git` CLI via `run_command`, which is faster, token-free, offline, and works on local sandboxes. | **`REMOVE`** | **PERMANENTLY REMOVED**. Local Git CLI is the authoritative version control tool for local engineering. |
| **23** | **StudySourceCore MCP Integration** | Phase 8 Decision 5, Phase 10 Audit & User Directive: StudySourceCore is 100% out of scope. Domain schemas belong to StudyLab. | **`REMOVE`** | **PERMANENTLY REMOVED**. All configurations, documentation, and references excised. |
| **24** | **Cryptographic Evidence Receipts** | Phase 8 Decision 4 & Phase 10 Audit: `evidence/` directory was 0 bytes. Static file hashes prove state changes, not pedagogical correctness, and suffer ratchet expiry. | **`REMOVE`** | **PERMANENTLY REMOVED**. Real-time process verification at task completion replaces static cryptographic receipts. |
| **25** | **Custom AST & Dependency Parsers** | Phase 8 Decision 6: Fragile regex AST dependency parsers produce false confidence. Native TypeScript (`tsc`) and Vitest module graphs are universally superior. | **`REMOVE`** | **PERMANENTLY REMOVED**. Defer module resolution and type checking to native compilers. |
| **26** | **Custom Schema Validators** | Phase 8 Decision 5: AntiOS Python schema validators duplicated StudyLab domain compiler rules. | **`REMOVE`** | **PERMANENTLY REMOVED**. StudyLab domain tools own domain schema validation. |
| **27** | **Large Hierarchical Agent Swarms** | Phase 6 Synthesis & Phase 7 Trials: Multi-tier agent swarms (>2-3 agents) generated massive token overhead and coordination latency without improving code quality. | **`REMOVE`** | **PERMANENTLY REMOVED**. Enforce shallow hierarchy: 1 Maker, 1 Checker (Depth $\le 2$). |
| **28** | **Redundant Root Reports & ZIP Archives** | Phase 10 Baseline & Doc Audit: 7 duplicate reports (54KB) and stale ZIP archives cluttered the root workspace. | **`REMOVE`** | **PRUNED / ARCHIVED**. Consolidate into canonical historical archive (`reports/` / `research/`). |
| **29** | **Fail-Closed Hook Architecture** | Phase 9 & 10 Forensic Audit: `pre_tool_guard.py` had `except Exception: allow` and allowed empty `workspacePaths`. | **`ADD`** | Implement strict fail-closed policy across all hook scripts. Any unhandled error, type mismatch, or missing argument blocks the tool call. |
| **30** | **Prefix-Based Path Canonicalization** | Phase 10 Audit Q7: Naive `in parts` check blocked legitimate paths inside any folder named `framework`. | **`ADD`** | Use `os.path.commonpath` and resolved absolute path boundaries to eliminate false positives. |
| **31** | **Hook Configuration Protection** | Phase 10 Finding F-02: `.agents/hooks.json` was editable via IDE tools. | **`ADD`** | Explicit protection for `.agents/` and hook scripts in `pre_tool_guard.py`. |
| **32** | **Working Tree Ratchet Verification** | Phase 9 Attack 4.4 & Phase 10 Audit: Modifying files after running tests bypassed verification ("Test $\to$ Mutate $\to$ Done"). | **`ADD`** | Stop gate verifies working tree cleanliness or executes tests on the exact final working tree state before allowing stop. |
| **33** | **Layer-1 Syntactic Doc Drift Checker** | Phase 9 Attack 1.10: Code and documentation drift without detection. Proposed in Phase 6, never implemented. | **`DEFER`** | Defer standalone AST doc checker. Enforce documentation sync via Maker-Checker review and Same Change Set policy for v1. |
| **34** | **Dead-End Logging Database** | Phase 9 & 10 Audit: `evidence/` was empty. Vector or database memory for dead ends is over-engineering. | **`DEFER`** | Defer structured database. Human-readable `## Dead Ends` section in `ACTIVE_CONTEXT.md` is sufficient for v1. |

---

## 3. Summary Statistics

```text
┌────────────────────────────────────────────────────────┐
│ TOTAL CAPABILITIES EVALUATED: 34                       │
├──────────────────────────────────┬─────────────────────┤
│ Disposition                      │ Count               │
├──────────────────────────────────┼─────────────────────┤
│ PLATFORM (Antigravity Core)      │ 7 (20.6%)           │
│ STUDYLAB (Domain Authority)      │ 3 (8.8%)            │
│ KEEP (Validated v1 Core)         │ 3 (8.8%)            │
│ ADAPT (Redesigned & Hardened)    │ 7 (20.6%)           │
│ REMOVE (Excised / Proved Bad)    │ 8 (23.5%)           │
│ ADD (New Evidence-Backed Gaps)   │ 4 (11.8%)           │
│ DEFER (Speculative / Unproven)   │ 2 (5.9%)            │
└──────────────────────────────────┴─────────────────────┘
```
