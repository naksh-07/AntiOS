# AntiOS v1 Master Architecture Specification (`ANTIOS_V1.md`)

**Version**: 1.0.0  
**Date**: 2026-09-04  
**Status**: Canonical Master Architecture Specification  
**Governing Axiom**:
> *"If Antigravity already provides the mechanism $\to$ USE THE PLATFORM.*  
> *If the language/compiler/test framework provides verification $\to$ USE THE NATIVE TOOLCHAIN.*  
> *If StudyLab already owns a domain contract $\to$ DEFER TO STUDYLAB.*  
> *AntiOS owns: PROJECT POLICY, SAFETY BOUNDARIES, ENGINEERING WORKFLOW, VERIFICATION POLICY, TASK STATE, AGENT GOVERNANCE."*  
> *"Prototype ko bachana nahi hai. AntiOS ko bachana hai."*

---

## 1. What is AntiOS?

**AntiOS** is a lean, deterministic, project-governance operating layer residing within a software repository. It provides the behavioral rules, safety boundaries, task-state conventions, and verification gates that allow autonomous AI agents (powered by Google Antigravity) to safely plan, implement, test, document, and maintain complex codebases over long-running sessions without human micromanagement.

AntiOS is **not** an operating system, an agent runtime, a database, or an application framework. It is the minimal set of project policies and deterministic hooks required to prevent agent hallucination, confirmation blindness, and blast-radius destruction.

---

## 2. What Problem Does It Solve?

When autonomous AI agents operate in bare repositories without governance, they suffer from four systematic failure modes:
1. **Upstream Blast-Radius Contamination**: Agents hallucinate fixes directly inside upstream core libraries (e.g. `rslib/`), corrupting stable engines.
2. **Conversational Self-Certification ("Looks Good to Me")**: Agents declare victory by writing reassuring text in chat without physically executing test suites.
3. **Context Amnesia & Stale-State Deception**: When conversation context windows fill and wipe, agents lose track of active tasks or read stale notes, repeating completed work or re-introducing bugs.
4. **Prompt Rule Decay**: As conversations grow long, LLMs rationalize away negative prompt constraints ("do not touch X") unless enforced by hard process code.

AntiOS eliminates these failure modes by enforcing **Code Over Prompt**, **Physical Process Verification**, **Bounded Working Sets**, and **Independent Maker-Checker Review**.

---

## 3. The Tripartite Responsibility Division

```text
                     =========================================
                               TIER 1: ANTIGRAVITY
                              (Platform Mechanism)
                     =========================================
                     • Subagent execution & context isolation
                     • Tool interception & JSON stdio transport
                     • Interactive Planning UI (<planning_mode>)
                     • Persistent transcript logging (transcript.jsonl)
                     • Background scheduling & timers (schedule)
                     • Shell terminal execution (run_command)
                                         │
                                         ▼
                     =========================================
                                 TIER 2: AntiOS v1
                               (Project Governance)
                     =========================================
                     • Safety boundaries & canonical path guards
                     • Fail-closed hook scripts (pre_tool_guard, stop_gate)
                     • Global Project Constitution (docs/AGENTS.md)
                     • Bounded active task state (docs/ACTIVE_CONTEXT.md)
                     • Engineering workflow skill (.agents/skills/antios-engineer/)
                     • Risk-tiered Maker-Checker verification policy
                     • Single canonical source-of-truth governance
                                         │
                                         ▼
                     =========================================
                                TIER 3: STUDYLAB
                                  (Domain Truth)
                     =========================================
                     • 20-field source question schema & validation
                     • Reviewer FSM & double SQLite architecture
                     • Upstream Anki core engine (rslib/ - immutable)
                     • Native compiler & test runners (tsc, vitest, pytest)
                     • Application features & UI components
```

---

## 4. What Does Antigravity Provide? (Platform)
- Subagent runtime lifecycle (`invoke_subagent`, `manage_subagents`).
- Interception engine for `PreToolUse` and `Stop` hooks.
- Raw shell execution (`run_command`) and file manipulation tools.
- Native interactive planning UI (`<planning_mode>`, `implementation_plan.md`, `walkthrough.md`).
- Immutable chronological transcript streaming (`transcript.jsonl`).
- Asynchronous timers and cron triggers (`schedule`).
- MCP client connection and protocol handling.

---

## 5. What Does AntiOS Provide? (Project Governance)
- **Hard Boundaries**: Deterministic Python hook scripts enforcing fail-closed protection on `rslib/` and `.agents/`.
- **Engineering Constitution**: `docs/AGENTS.md` specifying core engineering directives ($\le 40$ lines).
- **Active Working Memory**: `docs/ACTIVE_CONTEXT.md` tracking active tasks, blockers, and dead ends ($\le 60$ lines).
- **Engineering Skill**: `.agents/skills/antios-engineer/SKILL.md` guiding risk tiering and verifier dispatch.
- **Physical Verification Ratchet**: `stop_gate.py` executing registered OS test processes before permitting completion.
- **Maker-Checker Protocol**: Policy defining when and how to spawn isolated subagents.

---

## 6. What Does StudyLab Provide? (Domain Truth)
- Pedagogical invariants and mathematical flashcard rendering.
- Canonical 20-field question schema.
- Native package generation (`generate_apkg.py`).
- Application test suites (TypeScript Vitest/Playwright tests, Python tests).
- Reviewer finite state machine and database storage layers.

---

## 7. What Are the Boundaries?
1. **AntiOS never duplicates Antigravity**: No custom agent runners, background daemons, or transcript loggers.
2. **AntiOS never duplicates StudyLab**: No custom schema validators or domain AST parsers.
3. **StudySourceCore is 100% OUT OF SCOPE**: Zero inspection, zero cloning, zero modification, zero integration.
4. **Production Code Protection**: Production StudyLab branches are never directly modified during governance audits; development occurs strictly in designated branches or sandboxes.

---

## 8. Core Components of AntiOS v1

AntiOS v1 consists of exactly **five active physical components**:
1. **`.agents/hooks.json`**: Root manifest registering `PreToolUse` and `Stop` hooks.
2. **`framework/scripts/hooks/pre_tool_guard.py`**: Fail-closed canonical path guard.
3. **`framework/scripts/hooks/stop_gate.py`**: Fail-closed physical test verification ratchet.
4. **`.agents/skills/antios-engineer/SKILL.md`**: Discoverable engineering workflow skill.
5. **`docs/AGENTS.md` & `docs/ACTIVE_CONTEXT.md`**: Global Constitution and Bounded Memory Bank.

---

## 9. How Does a Task Flow Through AntiOS?

```text
1. INGESTION & ORIENTATION
   Agent reads AGENTS.md and ACTIVE_CONTEXT.md. Identifies risk tier (Low, Med, High).

2. PLANNING (Platform Native)
   Agent explores codebase using read-only tools; drafts implementation_plan.md.
   User reviews and approves via native UI.

3. EXECUTION & SAFETY INTERCEPTION
   Agent modifies code and documentation (Same Change Set).
   pre_tool_guard.py intercepts every tool write:
     - Denies writes targeting rslib/ or .agents/
     - Normalizes paths (resolves traversal and 8.3 aliases)
     - Fails closed on any anomaly.

4. INDEPENDENT VERIFICATION (If High Risk)
   Parent agent dispatches fresh subagent via invoke_subagent(TypeName='self').
   Checker audits working tree and executes native test suites.

5. STOP GATE RATCHET & COMPLETION
   Agent attempts to complete task.
   stop_gate.py intercepts Stop event:
     - Discovers native test runner (package.json / pyproject.toml)
     - Executes physical OS test process (timeout: 60s)
     - If exit code == 0: approves stop.
     - If exit code != 0: denies stop, outputs exact test stderr, forces agent to fix.

6. STATE RECONCILIATION
   Agent updates docs/ACTIVE_CONTEXT.md, records walkthrough.md, and concludes.
```

---

## 10. When Are Skills Used?
Skills are loaded lazily by Antigravity when an engineering task begins. The `antios-engineer` skill is activated to guide the agent through risk classification, Maker-Checker dispatch idioms, boundary awareness, and Stop gate compliance.

---

## 11. When Are Hooks Used?
Hooks execute deterministically on every relevant platform event:
- **`PreToolUse`**: Executes on every `write_to_file` and `replace_file_content` invocation.
- **`Stop`**: Executes whenever an agent attempts to finish its turn or conclude a task.

---

## 12. When Are Subagents Used?
Subagents are used exclusively for bounded, high-value delegation:
- **Independent Verification (Maker-Checker)**: To eliminate confirmation blindness on critical changes.
- **Read-Only Exploration**: Broad, token-heavy surveys of documentation or large directories.
- Subagents are NEVER used as sprawling multi-tier swarms (>2 agents). Max depth is strictly 2.

---

## 13. When Is Maker-Checker Required?
- **Low Risk** (typos, markdown formatting, doc tweaks): Solo execution. No fresh subagent required.
- **Medium Risk** (isolated bug fixes, standard features): Parent self-tests; checker optional.
- **High Risk** (Reviewer FSM, persistence, APKG packaging, security hooks): **MANDATORY MAKER-CHECKER**. A fresh subagent (`TypeName='self'`) must audit the working tree and run tests.

---

## 14. How Does Verification Work?
Verification adheres to the **Evidence Hierarchy**:
- Conversational claims (`CLAIMED`) carry zero evidentiary weight.
- Viewing code (`OBSERVED`) does not prove runtime correctness.
- The only acceptable completion state is **`VERIFIED`**: a physical OS process (`vitest:once` or `pytest`) executed against the final working tree with exit code 0.

---

## 15. How Does Task State Work?
Task state is externalized on disk in `docs/ACTIVE_CONTEXT.md` with a strict $\le 60$ line budget. It tracks the current mission, active checklist, blockers, and dead ends. It contains zero historical logs (historical logs belong in `reports/`).

---

## 16. What Happens on Failure?
- **Hook Denial**: The hook outputs an actionable denial message explaining what boundary was hit and providing immediate redirection advice.
- **Test Failure**: The Stop gate halts termination, captures process stdout/stderr, and returns it to the agent with instructions to fix the root cause.
- **Environment Failure**: The Stop gate detects missing executables (`node`, `yarn`, `uv`) and reports `ENVIRONMENT_UNAVAILABLE`, preventing infinite loops on broken host environments.

---

## 17. What Happens on Context Reset?
When a session wipes:
1. Agent reads `docs/AGENTS.md` (re-establishes rules and boundaries).
2. Agent reads `docs/ACTIVE_CONTEXT.md` (recovers active task, checklist, and next action).
3. Agent runs `git status` (reconciles documented state with physical disk reality).
4. Resumes execution seamlessly without hallucinating completed tasks as pending.

---

## 18. What Is Protected?
- `rslib/` (upstream Anki Rust core) — 100% immutable against IDE tools.
- `.agents/` (hook configurations, skills) — 100% self-protected against IDE tools.
- `framework/` (AntiOS security scripts) — 100% self-protected against IDE tools.

---

## 19. What Is NOT Protected? (Platform Boundary Limitation)
- **Raw Shell Execution (`run_command`)**: Antigravity executes raw shell strings via PowerShell/Bash. Tool hooks cannot intercept kernel-level syscalls or arbitrary shell pipelines.
- **Semantic Documentation Drift**: AntiOS verifies compilation and tests; validating whether prose accurately describes domain nuances requires human or Maker-Checker review.

---

## 20. What MCPs Are Allowed?
- **`USEFUL` (Permitted)**: `chrome-devtools-mcp` and `playwright` (for Svelte UI / webview E2E testing); `gemini-api-docs` (for upstream SDK API verification).
- **`OPTIONAL` (Restricted)**: `github-mcp-server` (remote PR creation only; local git work must use local CLI).
- **`REJECTED / EXCISED`**: `studysource-core` (100% out of scope); `notion-mcp-server`, `postman-mcp-server`, `posthog` (unnecessary bloat).

---

## 21. What Architecture Was Explicitly Rejected?
- Cryptographic state receipts (`evidence/`).
- Custom AST / regex dependency graph parsers.
- AntiOS duplicate schema validators.
- Arbitrary `verify_task.py` fallback test scripts.
- Multi-tier hierarchical agent swarms (>2 agents).
- Vector memory databases (Chroma/Pinecone).
- Custom agent orchestrator daemons.
- Fail-open exception handling.

---

## 22. How Can AntiOS Later Become Reusable?
AntiOS v1 cleanly separates **Generic Governance** from the **StudyLab Domain Adapter**:
- **Reusable Core**: The fail-closed hook runner, self-protection guards, test ratchet logic, Maker-Checker policy, and bounded markdown memory conventions are completely domain-agnostic.
- **Domain Adapter**: Protected path lists (`rslib/`), native test runner commands (`npm run vitest:once`), and domain risk classifications are isolated in modular configuration files.
- To port AntiOS to another repository, one simply clones the Core and updates the target repository's protected paths and test commands.

---

## 23. Evolution to Agent-Native Engineering Environment (Phase 27)
Phase 27 completed the transformation of AntiOS from a defensive governance harness into an active Agent-Native Engineering Environment:
- **Component Wayfinding (`framework/core/wayfinding.py`)**: Inverted multi-key indexing and sub-second locality resolution answering *"Where should I look?"* before *"What should I change?"*. Formats bounded locator cards ($\le 20$ lines) detailing entrypoints, test commands, blast radius, and invariants.
- **Subsystem Manifest Model (`framework/core/subsystem.py`)**: Declarative component schema defining boundaries, entrypoints, authoritative interface files, covering tests, test commands, applicable skills, governing rules, protected invariants, dependencies, and consumers.
- **Staleguard Layer 1 Reference Auditor (`framework/core/docaudit.py`)**: Zero-token, sub-second syntactic validation of markdown links, relative paths, and test runner targets with 0% false positives. Integrated into the Stop Gate ratchet to reject documentation drift.
- **8-Stage Agent Engineering Lifecycle**: Formalized agent workflow (`UNDERSTAND -> LOCATE -> PLAN -> ACT -> TEST -> VERIFY -> REMEMBER -> RECOVER`) with active subsystem context synchronization into `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines).
- **Certified Verification**: 266/266 tests passing in 13.2s with zero external dependencies and independent Maker-Checker certification.

