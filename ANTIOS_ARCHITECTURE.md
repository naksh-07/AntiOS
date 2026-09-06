# AntiOS Master Architecture Contract: Ambient Project OS

**Version**: `2.1.0-contract`  
**Status**: `RATIFIED ARCHITECTURAL CONTRACT` (Phase 108)  
**Authority**: Rank 5 in Precedence (`ANTIOS_SOURCE_OF_TRUTH.md`)  
**Scope**: Project-Local Operating Layer under Google Antigravity Execution Substrate  

---

## 1. Executive Summary & The Conceptual Lock

AntiOS evolves from a command-invoked task framework into an **Ambient Project OS** — a persistent, low-overhead, event-driven operating layer that lives inside software repositories, continuously governing engineering safety, project wayfinding, deterministic verification, and cumulative learning without developer ceremony.

### The Canonical Three-Tier Conceptual Lock
The target architecture is locked conceptually across three sovereign domains:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      GOOGLE ANTIGRAVITY                                │
│                     (Execution Substrate)                              │
│  - LLM Cognitive Loop & Context Window Management                     │
│  - Native Agent Runtimes & Subagent Spawning (invoke_subagent)         │
│  - Platform Lifecycle Hooks (.agents/hooks.json)                       │
│  - Tool Transport & Process Sandboxing (run_command, view_file)       │
│  - Isolated Workspace Branching (Workspace='branch')                   │
│  - Scheduling Primitives (schedule, cron, timer)                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Augments without micromanagement
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           ANTIOS                                       │
│          (Ambient, Project-Local Engineering Operating Layer)          │
│  - Sovereign Boundary Enforcement (INV-10: SOURCE ≠ INSTANCE ≠ PROJ)   │
│  - Deterministic Pre-Tool Path Protection (pre_tool_guard.py)          │
│  - Physical Toolchain Stop Gate Ratchet (exit code 0 verification)     │
│  - Locality Wayfinding & Prefix Indexing (wayfinding.py)               │
│  - Capability Selection & Routing (capability_router.py)               │
│  - Task Continuity & Bounded Active Context (docs/ACTIVE_CONTEXT.md)   │
│  - System A: Evidence-Grounded Project Memory (learning.py, proofs)    │
│  - System B: Continuous, Non-Blocking Telemetry Ingestion (experience) │
│  - Deep Operations Interface (/antios explicit skill)                  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Governs and protects
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        TARGET PROJECT                                  │
│                      (Source of Truth)                                 │
│  - Application Business Logic, Schemas & API Contracts                 │
│  - Native Compilers, Linters & Test Suites (Cargo, Pytest, Vitest, Go) │
│  - Git Version Control History & Working Tree Status                   │
│  - Project Declarative Configuration (antios.config.json)              │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Operating Axioms
1. **Augmentation, Not Replacement**: AntiOS augments Antigravity; it never replaces, wraps, emulates, or micromanages it.
2. **Frictionless Normal Engineering**: Zero mandatory `/antios` invocation for normal tasks; zero mandatory 10-stage ceremony on simple edits.
3. **Strict Context Boundedness**: No giant monolithic prompt injections. Global orientation (`docs/AGENTS.md`) is bounded to $\le 40$ lines; operational memory (`docs/ACTIVE_CONTEXT.md`) is bounded to $\le 60$ lines; capability cards are bounded to $\le 25$ lines.
4. **Zero Custom Runtime & Zero Daemons**: AntiOS executes purely on an event-driven basis via platform hooks and standard Python scripts. No background watcher processes, polling daemons, vector databases, or custom agent loop wrappers are permitted (`INV-15`, `INV-16`).
5. **Native Platform Preference**: Native Antigravity rules, hooks, skills, agents, and subagents are always preferred over custom framework mechanisms (`INV-01`).
6. **Epistemic & Operational Firewall**: Project-specific learning (System A) and framework-wide experience intelligence (System B) remain strictly and permanently decoupled (`INV-10`, `INV-11`).
7. **Passive, Continuous Telemetry**: Experience data is ingested continuously from real Antigravity lifecycle events without manual user commands or blocking developer progress.

---

## 2. Antigravity ↔ AntiOS ↔ Target Project Ownership Boundaries

| System Dimension | Google Antigravity Owns | AntiOS Owns | Target Project Owns |
| :--- | :--- | :--- | :--- |
| **Cognitive Execution** | Model inference, reasoning, token streams, turn orchestration | Policy-based prompt orientation, task bounds, failure escalations | Domain intent, user requests, issue specifications |
| **Subagent Management** | Subagent creation (`invoke_subagent`), state tracking, killing, workspace branching | Workforce sizing policy (`SOLO` to `MAX`), delegation depth ($\le 2$), Maker-Checker audit rules | Task deliverables, feature code, domain tests |
| **Tool Execution** | Tool sandboxing, stdin/stdout transport, MCP client connections | Pre-execution safety evaluation (`PreToolUse`), path guards, command sanitization | Application CLI tools, build commands, test runners |
| **Workspace & Storage** | Ephemeral context window, workspace worktree branching | Bounded working memory (`ACTIVE_CONTEXT.md`), persistent proofs, `.antios/` metadata | Application files, schema migrations, documentation |
| **Verification** | Execution of command processes via `run_command` | Enforcement of physical verification ratchet (exit code 0 on `Stop`), conflict marker checks | Test implementation, assertion logic, domain invariants |
| **Scheduling** | Cron and timer infrastructure (`schedule`) | Specification of periodic audit policies and health checks | CI/CD pipeline triggers, release schedules |
| **Telemetry & State** | Session logs (`transcript.jsonl`), trace metadata | Checkpoint ingestion, privacy scrubbing, metric aggregation (`experience.db`) | Project telemetry, application monitoring |

---

## 3. Responsibility Matrix: Rule vs Hook vs Skill vs Agent vs Project State

AntiOS structures its operating presence across 5 distinct architectural mechanisms:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. RULES (Orientation & Invariants)                                    │
│    Location: docs/AGENTS.md (≤ 40 lines)                               │
│    Role: Universal prompt directives read automatically by agents.     │
│    Contains: Epistemic axioms, protected zone laws, verification rules.│
├────────────────────────────────────────────────────────────────────────┤
│ 2. HOOKS (Deterministic Hard Invariants)                               │
│    Location: .agents/hooks.json → .antios/runtime/*.py                 │
│    Role: Non-bypassable platform interceptors executing out-of-band.   │
│    Contains: PreToolUse path guard, Stop Gate physical test ratchet.   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. SKILLS (Procedural Capabilities & Deep Operations)                  │
│    Location: .agents/skills/*/SKILL.md (≤ 80 lines each)               │
│    Role: Step-by-step procedures invoked on-demand by agents.          │
│    Contains: /antios (control plane), antios-engineer, antios-verifier│
├────────────────────────────────────────────────────────────────────────┤
│ 4. AGENTS (Role-Specialized Cognitive Workers)                         │
│    Location: Native Antigravity subagents (TypeName='self' | 'research')│
│    Role: Discrete contexts with specific technical mandates.          │
│    Contains: Primary lead, Maker-Checker verifier, Explorer specialist│
├────────────────────────────────────────────────────────────────────────┤
│ 5. PROJECT STATE (Persistent Ground Truth & Memory)                    │
│    Location: .antios/ (configuration), docs/ACTIVE_CONTEXT.md (memory) │
│    Role: Durable, human-auditable files surviving context wipes.       │
│    Contains: Anatomy, capabilities, proofs, active blockers.          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Project Environment Compiler Contract

The Project Environment Compiler (`framework/core/compiler.py`) is the deterministic engine that transforms an AntiOS installation into a fully adapted, self-contained project instance:

### 4.1 Four-Boundary Demarcation (`INV-10`)
The compiler strictly enforces the Four-Boundary Demarcation:
$$\text{SOURCE} \ne \text{INSTANCE} \ne \text{PROJECT} \ne \text{ANTIGRAVITY}$$
- **AntiOS Source (`SOURCE`)**: Canonical operating system repository (`framework/`, `tests/`).
- **AntiOS Instance (`INSTANCE`)**: Compiled project metadata and standalone scripts (`.antios/`).
- **Target Project (`PROJECT`)**: Sovereign application files, domain source, and native configs.
- **Antigravity Platform (`ANTIGRAVITY`)**: Host platform configuration and IDE hooks (`.agents/`).

### 4.2 Five Artifact Tiers
1. **Tier 1: Canonical Source**: Upstream AntiOS engine. Read-only during project operation.
2. **Tier 2: Managed Config & Hooks**: `antios.config.json` and `.agents/hooks.json`. Managed declaratively.
3. **Tier 3: Generated Intelligence & Runtime**: `.antios/manifest.json`, `.antios/runtime/*.py`, `.antios/knowledge.json`. Fully generated by compiler; zero manual edits.
4. **Tier 4: Operating Interface**: `.agents/skills/antios/SKILL.md` and specialized skill definitions.
5. **Tier 5: Target Project Source**: User application files. Sovereign and immutable by AntiOS governance.

### 4.3 Runtime Closure Contract
Compiled runtime scripts in `.antios/runtime/` (`pre_tool_guard.py`, `stop_gate.py`, `inspect_instance.py`, `verify_runtime.py`) must satisfy **100% Runtime Closure**:
- **Zero Framework Imports**: Scripts must never import from `framework.*`.
- **Zero Third-Party Dependencies**: Scripts execute exclusively using Python standard library (`sys`, `os`, `json`, `subprocess`, `hashlib`, `pathlib`).
- **Fail-Closed Execution**: Any syntax error, missing config, or unexpected exception causes immediate non-zero exit or tool denial.

---

## 5. Ambient Context & Bootstrap Model

### 5.1 Zero-Cost Session Priming
In an Ambient Project OS, agents do not read massive documentation dumps. When a new session initializes in an adapted workspace:
1. **Platform Orientation**: Antigravity automatically indexes `docs/AGENTS.md`. At $\le 40$ lines, it consumes $< 250$ tokens and establishes core axioms:
   - Toolchain ground truth over conversational claims.
   - Verification required before concluding.
   - Protected governance zones fail-closed.
2. **Active Context Priming**: If the agent requires immediate operational awareness, it inspects `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines), which contains:
   - Current goal and active milestone.
   - Immediate blockers and completed milestones.
   - Verified next step.
3. **Wayfinding on Demand**: The agent does not scan the entire filesystem. When working in a subsystem, it consults the deterministic prefix map (`.antios/anatomy.json` or `framework/core/wayfinding.py`), retrieving exact paths in $< 1$ms without vector databases.

---

## 6. Project Routing & Progressive-Disclosure Model

AntiOS organizes capabilities and skills through a **progressive-disclosure hierarchy** matching the task complexity:

```text
TASK ARRIVES
     │
     ├─► LOW-RISK / FOCUSED (Typo, docs, single-file bug)
     │   │
     │   └─► AMBIENT EXECUTION (SOLO Mode)
     │       - Direct planning & code modification
     │       - PreToolUse guards active in background
     │       - Stop Gate physical test ratchet verifies completion
     │       - Zero multi-stage ceremony; zero subagent overhead
     │
     └─► HIGH-RISK / COMPLEX (Refactor, schema change, multi-wave)
         │
         └─► EXPLICIT CONTROL PLANE (/antios)
             - Formal task classification & risk analysis
             - Workforce sizing (SMALL, PARALLEL, STAGED, HIERARCHICAL)
             - Maker-Checker verification via independent subagent
             - Evidence distillation into System A (ACTIVE_CONTEXT / LESSONS)
```

### Capability Resolution Ladder
When an agent requires specialized operational guidance, it resolves capabilities via the 8-tier hierarchy:
$$\text{Native Antigravity} \to \text{Active Skill} \to \text{Local Tool/Script} \to \text{Runtime Script} \to \text{Specialist Subagent} \to \text{Local CLI} \to \text{External Service} \to \text{Managed MCP}$$
Local Git CLI is always preferred over remote GitHub MCP for local operations (`DECISION 07`).

---

## 7. Persistent Project State Model

Persistent project state in AntiOS is version-controlled, human-auditable, and strictly file-backed:

| State Store | Location | Format | Budget Bound | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Active Context** | `docs/ACTIVE_CONTEXT.md` | Markdown | $\le 60$ lines | Immediate operational working memory across turns |
| **Project Lessons** | `docs/LESSONS.md` | Markdown | $\le 50$ entries | Validated domain insights grounded in physical evidence |
| **Project Proofs** | `.antios/proofs/*.json` | JSON | $\le 50$ proofs | Durable verification certifications with SHA-256 hash grounding |
| **Project Manifest** | `.antios/manifest.json` | JSON | LF-normalized | Cryptographic ledger of compiled runtime integrity |
| **Project Config** | `antios.config.json` | JSON | Declarative | User-configured test runners, protected zones, and lint rules |

---

## 8. Antigravity Lifecycle Integration Model

AntiOS integrates into the Antigravity execution lifecycle through standard, supported platform extension points:

```text
                       ANTIGRAVITY LIFECYCLE EVENT
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
[ PreToolUse Event ]      [ Stop / Finish Event ]    [ Subagent Dispatch ]
       │                           │                           │
       ▼                           ▼                           ▼
pre_tool_guard.py           stop_gate.py              invoke_subagent
 - Validates write paths     - Scans conflict markers  - Enforces Shallow Depth (≤ 2)
 - Blocks protected zones    - Discovers test runners  - Caps concurrency (≤ 10)
 - Blocks traversal escapes  - Executes native tests   - Caps total launches (≤ 20)
 - Fails closed on error     - Ratchets exit code 0    - Mandatory wave collapse to 0
```

---

## 9. Continuous Experience Telemetry Path (System B)

Experience telemetry tracks framework health, friction patterns, and operational efficiency without ever blocking the developer or requiring manual ingestion:

```
[ Antigravity Tool / Hook Event ]
                │
                ▼ (Hook Ingestion Trigger)
       telemetry_bridge.py
                │
                ▼ (Scrubbing Pipeline)
          sanitizer.py
   - Redacts API keys & tokens (Bearer, JWT, AWS, Google)
   - Redacts external filesystem paths
   - Strips model chain-of-thought & raw prompts
                │
                ▼ (Non-Blocking Append)
     <central_data>/experience.db (SQLite WAL Mode)
   - Sessions, turns, tool metrics, engineering events
   - Bounded retention (auto-purge / vacuum)
   - ZERO files written to Target Project repo (INV-10)
```

---

## 10. System A / System B Separation Firewall

AntiOS enforces an absolute, mathematically verified firewall between project learning and framework intelligence:

```
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│        SYSTEM A (PROJECT MEMORY)     │     │     SYSTEM B (EXPERIENCE INTEL)      │
├──────────────────────────────────────┤     ├──────────────────────────────────────┤
│ Scope: Target Project Local          │     │ Scope: Centralized Cross-Project     │
│ Storage: docs/, .antios/             │     │ Storage: <data-dir>/experience.db    │
│ Nature: Semantic, Evidence-Grounded  │     │ Nature: Statistical, Empirical       │
│ Visibility: Human-Auditable, Git     │     │ Visibility: Central Machine Ledger   │
│ Feedback: Influences current project │     │ Feedback: Offline Product Analytics  │
│ Dependencies: Zero experience.py deps│     │ Dependencies: Zero learning.py deps  │
└──────────────────┬───────────────────┘     └──────────────────┬───────────────────┘
                   │                                            │
                   └────────────── ABSOLUTE FIREWALL ───────────┘
                     - 0 cross-plane imports (enforced by AST)
                     - 0 project repository file mutations (INV-10)
                     - 0 automatic promotion from System B to A
```

---

## 11. Failure & Degradation Behavior

AntiOS guarantees deterministic, fail-safe degradation across all operating failure modes:

| Failure Scenario | Ambient Behavior | Recovery Action |
| :--- | :--- | :--- |
| **Hook Script Failure / Crash** | Hook fails closed (`PreToolUse` blocks write; `Stop` denies completion) | Outputs actionable diagnostic message; agent repairs syntax or rolls back |
| **Native Test Runner Failure** | Stop Gate denies task conclusion with non-zero exit code | Agent enters debug workflow, reproduces failure, applies fix |
| **Experience DB Locked / Corrupt** | Telemetry ingestion silently silences exception; logs warning to stderr | Engineering proceeds without disruption; experience data dropped safely |
| **Corrupted `.antios/` Instance** | Diagnostic flagged by doctor; Stop Gate denies completion | Run `python framework/cli.py repair` or re-compile instance |
| **Context Window Degradation** | Active context lost from model attention | Agent re-reads bounded `docs/ACTIVE_CONTEXT.md` to restore state |
| **Subagent Stall / Infinite Loop** | Concurrency and launch limits trigger fail-closed block | Orchestrator kills stalled workers via `manage_subagents(kill)` |

---

## 12. Installation, Update & Removal Lifecycle

The AntiOS product lifecycle is managed declaratively via the unified CLI (`framework/cli.py`):
1. **Install (`antios install`)**: Discovers project traits, generates `antios.config.json`, compiles `.antios/` runtime closure, and registers `.agents/hooks.json`. Application code is 100% untouched.
2. **Status & Doctor (`antios doctor`)**: Audits 10 drift domains across runtime closure, hook registrations, and test configurations with automated secret masking.
3. **Update (`antios update`)**: Creates pre-update snapshot in `.antios/backups/`, recompiles instance templates, and updates manifest. Application files are strictly preserved.
4. **Rollback (`antios rollback`)**: Restores from backup snapshot immediately if an update fails validation.
5. **Removal (`antios remove`)**: Cleanses `.antios/` and `.agents/` registrations; leaves zero residual artifacts.

---

## 13. Security & Project-Boundary Model

1. **Path Containment**: `pre_tool_guard.py` resolves canonical physical paths via `os.path.realpath`, blocking path traversal escapes (`../`), 8.3 short names (`PROGRA~1`), and symlink attacks.
2. **Protected Governance Zones**: Writes targeting `.agents/`, `.antios/`, `framework/`, or `antios.config.json` are denied unless explicitly authorized during controlled maintenance phases.
3. **Secret Redaction**: Telemetry sanitizer strips API credentials, passwords, private SSH keys, and tokens with fail-closed regex and Shannon entropy classifiers.
4. **Tool Ground Truth**: Unverified shell scripts (`verify_task.py`) are strictly prohibited from acting as verification proof (`DECISION 03`).

---

## 14. What AntiOS Explicitly MUST NOT Become

To protect against architectural bloat and maintain long-term production stability, AntiOS permanently prohibits:
- **A Custom Agent Runtime or Scheduler**: AntiOS must NEVER implement custom agent event loops, thread managers, or subagent message queues.
- **A Background Daemon or Poller**: AntiOS must NEVER run long-lived watcher processes, file pollers, or background services (`INV-15`).
- **A Vector Database or Embedding Store**: AntiOS must NEVER depend on Chroma, Pinecone, or neural semantic retrievers for repository navigation (`DECISION 10`).
- **A Monolithic Prompt Monster**: AntiOS must NEVER inject multi-thousand-token system prompts that deplete context windows.
- **A Micromanagement Layer**: AntiOS must NEVER intercept or second-guess valid native development workflows on trivial tasks.
- **An Unbounded Agent Swarm**: AntiOS must NEVER spawn unbounded, recursive, or peer-consensus multi-agent graphs (`INV-06`, `INV-07`).

---

## 15. Subsystem Audit Matrix: Reuse, Extend & Missing

| Subsystem | Disposition | Reusable Assets | Required Extensions (Phase 109+) | Missing Capabilities |
| :--- | :---: | :--- | :--- | :--- |
| **Adapter System** | **EXTEND** | `discovery.py`, `adapter.py`, `two_way_contract.py` | Event-driven manifest change detection; ambient config schema | Dynamic dependency fallback shims |
| **Routing & Skills** | **EXTEND** | 4-role model (`agent_role.py`), 7-mode sizing (`orchestration.py`) | Ambient skill activation based on file path focus | Pre-turn prompt middleware |
| **Compiler & Templates** | **REUSE / EXTEND** | `compiler.py`, 5-tier artifact model, runtime closure | Parameterized template interpolation | Self-instance compilation inside AntiOS repo |
| **Memory & Learning (A)** | **REUSE / EXTEND** | `learning.py`, 4-tier epistemic ladder, `project_proof.py` | Automated observation streaming from tool stdout | Ephemeral scratchpad compaction |
| **Runtime & Lifecycle** | **REUSE / EXTEND** | `pre_tool_guard.py`, `stop_gate.py`, unified CLI surface | PostToolUse and SessionStart hook bindings | In-process lightweight event bus |
| **Experience (B)** | **REUSE** | `experience.py`, `sanitizer.py`, `experience_analytics.py` | Continuous hook-embedded transcript ingestion | Ambient workflow friction notifications |
| **Test Suite** | **REUSE / EXTEND** | 142 test suites, `tests/run_all.py`, 1086+ tests | Live Antigravity host integration tests | In-memory mock platform emulator |

---

## 16. End-to-End Acceptance Criteria for Architecture Proof

To prove that the Ambient Project OS architecture functions in a real Antigravity workspace, the following criteria must be satisfied:

1. **Ambient Execution Acceptance**:
   - A standard developer prompt (e.g. "Fix typo in utils.py and run tests") executes cleanly in `SOLO` mode without `/antios` prefix.
   - `pre_tool_guard.py` actively prevents writes to protected governance zones in $< 10$ms.
   - `stop_gate.py` independently verifies native test suite exit code 0 before task conclusion.
   - Total planning and governance token overhead remains $< 350$ tokens.
2. **Explicit Control Plane Acceptance**:
   - An explicit `/antios` prompt triggers full task classification, workforce planning, and Maker-Checker verification when complexity warrants.
   - Subagent nesting depth strictly adheres to $\le 2$ (`INV-06`).
   - Wave collapse to 0 active subagents occurs before final verdict emission (`INV-08`).
3. **Continuous Telemetry Acceptance**:
   - Lifecycle events stream continuously into `<central_data>/experience.db`.
   - Zero `.db` or telemetry files are created inside the target project workspace (`INV-10`).
   - Sanitizer verifies 100% of sensitive API keys and tokens are redacted.
   - Hook failure or locked database leaves the developer experience completely unblocked.
4. **Epistemic Separation Acceptance**:
   - AST validation confirms 0 imports between System A (`learning.py`) and System B (`experience.py`).
   - `git diff` confirms 0 modifications to target project code during experience export or analysis.
