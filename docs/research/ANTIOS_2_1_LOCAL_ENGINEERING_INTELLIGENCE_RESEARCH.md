# AntiOS 2.1 — Local Engineering Intelligence
## Phase 1: Deep Research & Architecture Dossier

**Status**: RESEARCH ONLY — ARCHITECTURAL DOSSIER RATIFIED  
**Date**: 2026-09-06  
**Target Repository**: `c:\Users\Suraj\Documents\Antigravity\AntiOs`  
**Governance Authority**: Level 1 Architecture Governance / AntiOS 2.0 Architecture Freeze Charter  
**Version Alignment**: AntiOS 2.0.0-GA (Frozen Baseline) $\to$ AntiOS 2.1 (Engineering Intelligence Proposal)  

---

## Executive Summary

This dossier investigates the architectural feasibility, boundaries, data models, storage mechanics, privacy safeguards, and governance integration for **AntiOS 2.1: Local Engineering Intelligence**.

AntiOS 2.0 is officially architecturally frozen under Phase 101 (`ARCHITECTURE_FREEZE.md`) and ratified under ADR 85 / ADR 86. It enforces 20 constitutional invariants (`INVARIANT_REGISTRY.md`), including zero background daemons (INV-15), zero vector databases/embeddings (INV-09, Freeze Sec 3), zero custom multi-agent execution runtimes (INV-16), physical stop-gate enforcement (INV-04), and strict epistemic separation (`OBSERVATION ≠ EVIDENCE ≠ VERDICT ≠ INFERENCE ≠ DECISION`, INV-11).

The core mandate of AntiOS 2.1 is:
> *Local-first persistent Engineering Intelligence that records structured engineering experience across projects, sessions, missions, agents, tools, failures, recoveries, verification, and successful strategies, then feeds validated knowledge back into the existing AntiOS learning/evidence/proof architecture.*

This research establishes that AntiOS 2.1 is **fully architecturally viable without mutating, weakening, or violating AntiOS 2.0 freeze invariants**. It achieves this through a **Dual-Plane Architecture**:
1. **Control & Governance Plane**: Preserved 100% in AntiOS 2.0 Core via deterministic `hooks.json` (`PreToolUse`, `Stop`), physical test runners, and fail-closed guards.
2. **Telemetry & Experience Ingestion Plane**: A lightweight, non-invasive, event-driven observer that ingests platform transcripts (`transcript.jsonl`) and hook metadata, normalizes events, applies strict zero-PII/secret filters, and writes to an external, user-configured **Central AntiOS Data Directory** (e.g. `D:\AntiOSData\experience.db`) using standard library SQLite (WAL mode).

The existing AntiOS learning, evidence, and proof engines remain the sovereign epistemic judges: **Experience is raw telemetry; learning remains evidence accumulation; project proofs remain grounded in physical disk byte SHA-256 hashes.**

---

# R1 — Antigravity Platform Integration Research

## 1.1 Surfaces Topology & Agent Lifecycle

Google Antigravity operates on a unified, high-performance C++/Go core engine (`language_server.exe` / `localharness` / `agentapi`) exposed across four primary surfaces:

```
                      ┌─────────────────────────────────────────┐
                      │    Google Antigravity Core Engine       │
                      │ (language_server.exe / localharness)    │
                      └────┬──────────────┬───────────────┬─────┘
                           │              │               │
            ┌──────────────▼───┐   ┌──────▼────────┐   ┌──▼────────────────┐
            │ Antigravity 2.0  │   │  Antigravity  │   │    agy CLI        │
            │ Desktop Electron │   │   IDE (VSCode)│   │ (Headless/Stream) │
            └──────────────┬───┘   └──────┬────────┘   └──┬────────────────┘
                           │              │               │
                           └──────────────┼───────────────┘
                                          │
                           ┌──────────────▼────────────────┐
                           │    Python SDK Engine Binding   │
                           │  (google-antigravity / PyPI)   │
                           └───────────────────────────────┘
```

1. **Antigravity 2.0 (Electron Desktop App)**:
   - Primary multi-turn conversational desktop environment.
   - Manages projects, workspace bindings, auxiliary tabs (Terminals, Artifacts, Subagents, Changes), and permission policies.
   - Manages agent lifecycles via async turn loops; maintains active process pools for bash/powershell terminals and webviews.
2. **Antigravity IDE (VS Code-based)**:
   - In-editor environment with three operational modalities: Passive (Antigravity Tab autocomplete), Instructive (Inline `Ctrl+I` / `Cmd+I`), and Collaborative (Sidebar Chat & Planning Mode).
   - Shares runtime configuration and workspace customization discovery (`.agents/`).
3. **Antigravity CLI (`agy`)**:
   - Terminal-based TUI and headless automation engine.
   - Supports headless execution via `agy --output-format stream-json --input-format stream-json`. Emits streaming NDJSON events (`ACTIVE` with `text_delta`, `result` with token counts, `DONE`).
4. **Antigravity Python SDK (`google-antigravity`)**:
   - Programmatic async interface (`async with Agent(config) as agent:`).
   - Exposes strongly typed `ToolCall`, `UsageMetadata` (`prompt_token_count`, `candidates_token_count`, `thoughts_token_count`, `total_token_count`), and in-process Python lifecycle hooks.

---

## 1.2 Lifecycle Hook Specifications & Semantics (`hooks.json`)

Antigravity provides a declarative, subprocess-based lifecycle hook system configured via `.agents/hooks.json` (project-scoped) or `~/.gemini/config/hooks.json` (machine-global).

### Common Input Payload (Delivered on `stdin`)
Every hook execution receives a camelCase JSON payload containing host metadata:
```json
{
  "conversationId": "d794456c-b363-4b9d-a16a-c1ea27e6b2c4",
  "workspacePaths": ["c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs"],
  "transcriptPath": "C:\\Users\\Suraj\\.gemini\\antigravity\\brain\\d794456c...\\.system_generated\\logs\\transcript.jsonl",
  "artifactDirectoryPath": "C:\\Users\\Suraj\\.gemini\\antigravity\\brain\\d794456c...",
  "modelName": "auto"
}
```

### Supported Hook Events & Execution Contracts

| Hook Event | Trigger Point | Matcher Target | Input Payload (`stdin`) | Output Contract (`stdout`) | Capability / Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PreToolUse`** | Before tool executes | Tool name regex (e.g. `run_command`, `write_to_file\|replace_file_content`, `.*`) | Common fields + `toolCall: {name, args}`, `stepIdx: int` | `{"decision": "allow"\|"deny"\|"ask"\|"force_ask", "reason": "...", "overwrite": {...}}` | **Inspect / Decide / Transform**: Can hard-block, prompt user, or rewrite tool arguments via shallow top-level `overwrite` merge before execution. |
| **`PostToolUse`** | After tool completes | Tool name regex | Common fields + `stepIdx: int`, `error: string` (present if tool failed) | `{}` (empty JSON object) | **Inspect**: Post-execution auditing, telemetry logging, and auto-fix trigger. |
| **`PreInvocation`** | Before model is called | N/A (ignored) | Common fields + `invocationNum: int`, `initialNumSteps: int` | `{"injectSteps": [{"ephemeralMessage": "..."}, {"userMessage": "..."}, {"toolCall": {...}}]}` | **Transform**: Dynamic context injection without modifying conversation history. |
| **`PostInvocation`** | After tool steps finish | N/A (ignored) | Common fields + `invocationNum: int`, `initialNumSteps: int` | `{"injectSteps": [...], "terminationBehavior": "force_continue"\|"terminate"}` | **Transform / Decide**: Inspect model completions; force continuation or loop termination. |
| **`Stop`** | When execution loop attempts to conclude | N/A (ignored) | Common fields + `executionNum: int`, `terminationReason: string` (`model_stop`, `max_steps_exceeded`, `error`), `error: string`, `fullyIdle: bool` | `{"decision": "continue"\|"allow", "reason": "..."}` | **Physical Stop Gate**: Setting `decision: "continue"` rejects task conclusion, injects `reason` as a system prompt, and forces model back into execution. |

*Crucial Engineering Fact*: Hook commands run synchronously, blocking the agent execution loop until the process exits. They execute via `cmd /c` on Windows and `sh -c` on Unix with a configurable timeout (default 30s).

---

## 1.3 Local Filesystem Artifacts & Persistence Layout

Antigravity stores all runtime state locally on the filesystem under the user profile:
```text
C:\Users\Suraj\.gemini\antigravity\
├── brain\
│   └── <conversation-id>\
│       ├── .system_generated\
│       │   ├── logs\
│       │   │   ├── transcript.jsonl      <-- Streamed step log (truncated content)
│       │   │   ├── transcript_full.jsonl <-- Complete un-truncated step log
│       │   │   └── chunks\               <-- Streamed token chunks
│       │   └── steps\<stepIdx>\
│       │       └── output.txt            <-- Raw stdout/stderr of tool step
│       ├── scratch\                      <-- Scripts & temporary scratch files
│       └── *.md                          <-- User-facing artifacts
├── conversations\
│   └── <conversation-id>.db              <-- Local SQLite database (WAL mode)
└── config\
    ├── config.json                       <-- Global settings & execution policies
    └── mcp_config.json                   <-- Configured Model Context Protocol servers
```

- **`transcript.jsonl` vs `transcript_full.jsonl`**: Every step is logged as an NDJSON object containing `step_index`, `source` (`USER_EXPLICIT`, `MODEL`, `SYSTEM`), `type` (`USER_INPUT`, `PLANNER_RESPONSE`, `GENERIC`), `status` (`DONE`, `ERROR`), `created_at`, `tool_calls` (name and arguments), `content` (output), and `thinking` (raw reasoning). In `transcript.jsonl`, massive text blocks are truncated with field markers (`truncated_fields: ["content"]`); in `transcript_full.jsonl`, all fields are 100% complete.

---

## 1.4 Subagents Lifecycle, Isolation & Context Hygiene

Antigravity provides first-class native subagent primitives:
1. **Invocation**: Launched via `BuiltinTools.START_SUBAGENT` / `invoke_subagent` with parameters `TypeName`, `Role`, `Prompt`, `Model`, `Workspace` (`inherit` vs `branch` vs `share`).
2. **Context Hygiene (Strict Isolation)**: Subagents do **not** inherit parent prompt history. Each subagent is provisioned with a fresh conversation ID, an independent SQLite state file, and an isolated `transcript.jsonl`.
3. **Inter-Agent Messaging**: Parent and child communicate strictly via structured messaging tools (`send_message(Recipient, Message)`). The runtime awakens listening agents reactively upon message receipt without polling.
4. **Lifecycle States**: `running` $\to$ `idle` / `waiting_for_message` $\to$ `done` / `killed`.

---

## 1.5 Observability Surfaces & Epistemic Classification

Telemetry data obtainable from Antigravity is classified under four epistemic truth grades:

| Classification | Telemetry Data Items | Extraction Surface | Reliability & Invariants |
| :--- | :--- | :--- | :--- |
| **[FACT]** | - Exact tool names & argument payloads<br>- Process exit codes (0 vs non-zero)<br>- Command execution timestamps & durations<br>- `conversationId`, `stepIdx`, `modelName`<br>- Hook input payloads on `stdin`<br>- Token usage (`prompt`, `candidate`, `thinking`) in SDK/CLI stream | `transcript.jsonl`<br>`output.txt`<br>Hook `stdin`<br>`stream-json` events | **100% Deterministic & Structured**.<br>Hardware/filesystem reality. Zero heuristic parsing needed. |
| **[INFERENCE]** | - Touched file sets derived from tool arguments<br>- Test verification pass/fail status derived from runner exit code<br>- Worker specialization and hierarchy depth derived from parent IDs<br>- Tool failure categorization (syntax vs missing dependency) | Parsed from tool arguments and stdout | **High Confidence Derived**.<br>Validated against `git status` and test process return codes. |
| **[ASSUMPTION]** | - Cross-environment tool name normalization (e.g. `write_to_file` vs `edit_file`)<br>- SQLite concurrency behavior during active Electron `-wal` write locks<br>- Model capability inference from prompt responses | Normalization heuristics | **Plausible but Variable**.<br>Requires fail-closed defensive defaults. |
| **[UNKNOWN]** | - Real-time token inter-arrival intervals inside cloud Gemini inference<br>- Passive autocomplete keystrokes in VS Code editor canvas<br>- Proprietary internal protobuf structures (`agyhub_summaries_proto.pb`) | Closed IDE internals | **Unobservable**.<br>Must NEVER be relied upon. |

---

## 1.6 Recommended Integration: The Dual-Plane Architecture

```
                      GOOGLE ANTIGRAVITY ENGINE
                 (Desktop 2.0 / IDE / agy CLI / SDK)
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
(A) Lifecycle Hooks                               (B) Append-Only Transcripts
 (.agents/hooks.json)                              (.system_generated/logs/)
         │                                                 │
         ▼                                                 ▼
┌───────────────────────────────────┐    ┌───────────────────────────────────┐
│     AntiOS CONTROL PLANE (2.0)    │    │    AntiOS TELEMETRY PLANE (2.1)   │
│  - PreToolUse: Path Guard (INV-02)│    │  - Transcript Tail Reader         │
│  - PreToolUse: Arg Overwrite      │    │  - Normalizer & Redaction Filter  │
│  - Stop: Stop Gate Test (INV-04)  │    │  - Event Ingestion to SQLite      │
│  - Stop: Change Set Ratchet       │    │  - Zero Runtime Blocking Latency  │
└───────────────────────────────────┘    └───────────────────────────────────┘
```

1. **Control Plane (AntiOS 2.0 Baseline)**:
   - Uses `PreToolUse` to block writes to `.agents/`, `framework/`, and `antios.config.json` (INV-02).
   - Uses `Stop` to execute native test runners (`pytest`, `npm test`, `cargo test`) and enforce exit code 0 before task conclusion (INV-04).
2. **Telemetry Plane (AntiOS 2.1 Capability)**:
   - Non-blocking, passive ingestion of `transcript.jsonl` and hook metadata.
   - Extracts structured execution events, strips sensitive PII/secrets/CoT, and records to the Central Experience Store.

---

# R2 — Comprehensive Audit of AntiOS 2.0

## 2.1 Mapping Existing Implementations (16 Subsystems)

| Subsystem File | Physical Size | Primary Architectural Responsibility | Persistence Form |
| :--- | :---: | :--- | :--- |
| `framework/core/memory.py` | 1,005 lines | 5 memory categories (`ACTIVE_STATE`, `PROJECT_KNOWLEDGE`, `DECISIONS`, `LESSONS`, `HISTORICAL_RECORD`), epistemic authority progression (`CANDIDATE` $\to$ `VALIDATED` $\to$ `DURABLE`), transparent Markdown serialization. | Markdown documents (`docs/`) |
| `framework/core/learning.py` | 1,195 lines | Epistemic classification (`OBSERVED_FACT`, `USER_ASSERTION`, `DERIVED_INFERENCE`, `AGENT_INTERPRETATION`), 13 canonical observation types, bounded observation store ($\le 100$ items), evolution proposals ($\le 20$), knowledge decay, safety gate. | JSON (`.antios/learning_observations.json`, `learning_proposals.json`) |
| `framework/core/mission_state.py` | 467 lines | Multi-wave mission continuity, ephemeral vs persistent threshold, crash recovery engine, tool output classifier ($\le 2,000$ chars, SHA-256 bounding). | JSON (`.antios/missions/<id>/`) |
| `framework/core/evidence.py` | 506 lines | Strict epistemic separation (`OBSERVATION ≠ EVIDENCE ≠ VERDICT ≠ INFERENCE ≠ DECISION`), 6 evidence states, cryptographic `ArtifactFingerprint`, bounded `EvidencePackage` ($\le 50$ artifacts, $\le 100$ items). | JSON / In-memory package |
| `framework/core/project_proof.py` | 451 lines | Durable project proofs distillation (`MISSION EVIDENCE -> PROOF`), 13 proof subjects, 7 lifecycle states, physical disk byte SHA-256 hash grounding, bounded store ($\le 50$ proofs). | JSON (`.antios/proofs/proofs.json`) |
| `framework/core/mission_evaluation.py` | 522 lines | Deterministic 11-dimension evaluation (`FUNCTIONAL_CORRECTNESS`, `TEST_VERIFICATION`, etc.), 4 statuses (`PASS`, `FAIL`, `BLOCKED`, `INCONCLUSIVE`), Maker-Checker contract, bounded card ($\le 25$ lines). | In-memory evaluation / Card |
| `framework/core/mission_benchmark.py` | 533 lines | Benchmarking workflow quality (not LLM reasoning), 13 proxy metrics, baseline vs governed comparison, 10 synthetic proving scenarios (A through J), report card ($\le 25$ lines). | In-memory / JSON |
| `framework/core/drift_health.py` | 582 lines | Event-driven runtime drift detection (INV-15 compliant; zero daemons), 10 drift domains, 5 severities, 7 health dimensions, proposal-governed repair ($\le 10$ repair proposals), card ($\le 25$ lines). | In-memory / Card |
| `framework/core/release_certification.py` | 410 lines | Multi-mission release certification, 12 dimensions, physical reality outranking past claims, bounded window ($\le 10$ missions, older collapsed to SHA-256 digest), card ($\le 25$ lines). | JSON / Card |
| `framework/core/context_budget.py` | 384 lines | Task-time context budgeting, "Optimize useful info / context cost", 6 source classifications, 5 governor actions (`LOAD`, `DEFER`, `SUMMARIZE`, `DISCARD`, `REFRESH`), budget card ($\le 16$ lines). | In-memory / Card |
| `framework/core/context_freshness.py` | 267 lines | Physical disk SHA-256 auditing, git HEAD tracking, 5 freshness states (`FRESH`, `AGING`, `STALE`, `INVALID`, `UNKNOWN`), non-destructive safe compaction. | In-memory / Disk audit |
| `framework/core/runtime_contract.py` | 267 lines | Runtime closure contract (`SOURCE ≠ INSTANCE`), AST inspection prohibiting imports from `framework` in target instances, zero source leaks. | Target `.antios/runtime/` |
| `framework/core/workforce_contract.py` | 320 lines | Responsibility demarcation between AntiOS (brain/governance) and Antigravity (execution), 11-step pipeline, resource ceilings (depth $\le 2$, active $\le 10$, lifetime $\le 20$). | Code contract / Invariants |
| `framework/core/dispatch.py` | 685 lines | End-to-end task dispatch pipeline wiring classifier $\to$ wayfinding $\to$ capabilities $\to$ agents $\to$ adaptive planner $\to$ verification $\to$ memory. | In-memory pipeline |
| `framework/core/orchestration.py` | 1,548 lines | `AdaptiveWorkforcePlanner` (12 inputs), `WaveOrchestrator` (mandatory collapse before next wave), `WavePersistenceEngine`, `WriteSafetyEvaluator` (single-writer default). | JSON (`.antios/wave_state.json`) |
| `framework/cli.py` & `scripts/` | 464 lines | Unified `antios` CLI (`version`, `status`, `doctor`, `install`, `update`, `rollback`, `repair`, `remove`, `adapt`, `verify`, `issue`, `release`), root shell wrappers. | CLI console scripts |

---

## 2.2 Scope & Persistence Matrix

| Artifact / Entity | Lifecycle Scope | Persistence Medium | Authority Tier | Retention / Bounds |
| :--- | :--- | :--- | :--- | :--- |
| `docs/ACTIVE_CONTEXT.md` | Active Mission / Session | Version-controlled Markdown | Operational Working State | Hard bounded $\le 60$ lines; overwritten across missions |
| `docs/PROJECT_KNOWLEDGE.md` | Project-Scoped | Version-controlled Markdown | `VALIDATED` / `DURABLE` | Bounded human doc; updated on verified facts |
| `docs/LESSONS.md` | Project-Scoped | Version-controlled Markdown | `CANDIDATE` vs `DURABLE` | Partitioned; candidate section pruned on promotion |
| `DECISION_REGISTER.md` | Project-Scoped | Version-controlled Markdown | `DURABLE` Consensus | Append-only architectural consensus records |
| `.antios/learning_observations.json` | Project-Scoped | Bounded JSON (Schema 2.0.0) | `OBSERVED_FACT` (1.0) to `AGENT_INT` (0.3) | Hard bound $\le 100$ items, $\le 200\text{ KB}$; state-priority eviction |
| `.antios/learning_proposals.json` | Project-Scoped | Bounded JSON (Schema 2.0.0) | Staged for Human Review | Hard bound $\le 20$ proposals; pruned on resolution |
| `.antios/proofs/proofs.json` | Project-Scoped | Bounded JSON (Version 1.0) | Grounded in File SHA-256 | Hard bound $\le 50$ proofs; invalidated on hash divergence |
| `.antios/missions/<id>/` | Mission-Scoped | Bounded JSON | Intermediate Multi-Wave State | Created for complex tasks; archived upon completion |
| `ToolOutputEvidence` buffers | Ephemeral / Turn | In-Memory Buffer | Temporary Percept | Compacted to 20 lines if $>2,000$ chars; raw SHA-256 kept |
| Framework Core Code (`framework/core/`) | Global / Universal | Static Python Modules | Universal Invariant Baseline | Immutable across projects; zero project-specific mutations |

---

## 2.3 The Markdown vs Bounded JSON Demarcation

AntiOS 2.0 establishes a strict functional demarcation between Markdown and JSON:

1. **What MUST Remain Markdown**:
   - Everything intended for human audit, code review, Git versioning, and direct operator editing.
   - `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines): Injected directly into agent working contexts; must be lightweight and readable.
   - `docs/AGENTS.md` ($\le 40$ lines): Universal platform orientation.
   - `docs/LESSONS.md`, `docs/PROJECT_KNOWLEDGE.md`, `DECISION_REGISTER.md`: Living engineering knowledge reviewed by developers during PRs.
   - `.agents/skills/*/SKILL.md`: Platform-native skill instructions parsed by Antigravity.
2. **What MUST Remain Bounded Runtime JSON**:
   - Structured registries requiring machine parsing, hashing, signature deduplication, and atomic operations.
   - Observations (`learning_observations.json`), proposals (`learning_proposals.json`), durable proofs (`proofs.json`), wave states (`wave_state.json`), and project manifests (`manifest.json`).
3. **What Belongs in a Future Experience Store (AntiOS 2.1)**:
   - High-volume, granular, cross-session telemetry: individual tool call parameters, command execution runtimes, exit codes, subagent tree structures, multi-step navigation paths, and raw error snippets.
   - This data is too voluminous for Git-tracked Markdown or bounded `.antios/*.json` files. Storing it in an external SQLite database prevents repository bloat while enabling cross-mission historical analysis.

---

## 2.4 Overlap vs Complementarity

```
Existing AntiOS 2.0 Memory & Proofs             Future AntiOS 2.1 Experience Store
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│  - Bounded to 50 proofs, 100 obs     │       │  - Bounded to 500 missions, 50,000 ev│
│  - Point-in-time verified facts      │       │  - Full procedural trajectories      │
│  - Git-tracked in target repo        │       │  - Central database (D:\AntiOSData\) │
│  - Sovereign Epistemic Judge         │       │  - Telemetry Ingestion Engine        │
└──────────────────▲───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   └──────── Pattern Mining & Promotion ──────────┘
```

- **Where It Would Overlap (And Must Be Constrained)**:
  - If AntiOS 2.1 attempts to store "authoritative project rules", it would collide directly with `docs/LESSONS.md` and `docs/PROJECT_KNOWLEDGE.md`.
  - If AntiOS 2.1 attempts to create a separate proof store, it would collide with `project_proof.py`.
  - *Resolution*: The Experience Store MUST NOT be an authority. It is purely a **telemetry ledger**. It records what happened; existing AntiOS 2.0 modules decide what it means.
- **Where It Complements AntiOS 2.0**:
  - **Trajectory Provenance**: AntiOS 2.0 knows that a file was modified and passed tests; AntiOS 2.1 records the 14 exploratory tool calls, failed grep searches, and navigation missteps that preceded the fix.
  - **Empirical Navigation Priors**: AntiOS 2.0 wayfinding uses static lexical indexes; AntiOS 2.1 can provide empirical probabilities ("When modifying auth handlers, developers inspect token validator 85% of the time").
  - **Empirical Tool Policy**: Identifies flaky CLI tools or environmental mismatches across multiple sessions before the tool is invoked.
  - **Automated Recurrence Feeding**: Feeds multi-session recurrence counts directly into `learning.py:LessonDistillationEngine` without requiring manual entry.

---

# R3 — Experience Data Model Research

## 3.1 Proposed Conceptual Entity Model

AntiOS 2.1 models engineering experience as an immutable, append-only directed acyclic graph (DAG) grounded in the physical reality of tool executions and test verifications:

```
┌─────────────┐
│   PROJECT   │ (Unique repository identity grounded in root manifest hash)
└──────┬──────┘
       │ 1:N
┌──────▼──────┐
│   SESSION   │ (Single Antigravity desktop or CLI conversation)
└──────┬──────┘
       │ 1:N
┌──────▼──────┐
│   MISSION   │ (Bounded engineering objective under AntiOS governance)
└──────┬──────┘
       │ 1:N
┌──────▼──────┐
│    TURN     │ (Single agent invocation cycle: prompt -> thoughts -> tool calls)
└──────┬──────┘
       │ 1:N
┌──────▼──────┐
│  TOOL_CALL  │ (Deterministic tool invocation: name, sanitized args, duration)
└──────┬──────┘
       │ 1:1
┌──────▼──────┐
│ EVENT_RECORD│ (Normalized engineering event typed according to taxonomy)
└─────────────┘
```

---

## 3.2 Relational Entity Schema

### 1. `projects`
- `project_id` (TEXT, PK): Deterministic SHA-256 derived from initial project root path + initial manifest hash.
- `project_name` (TEXT): Normalized directory name.
- `canonical_path` (TEXT): Absolute path on local machine.
- `ecosystem` (TEXT): Primary language/framework (e.g. `python`, `typescript`, `rust`).
- `first_observed_at` (TEXT): ISO 8601 UTC timestamp.
- `last_active_at` (TEXT): ISO 8601 UTC timestamp.

### 2. `sessions`
- `session_id` (TEXT, PK): Antigravity `conversationId` (UUIDv4).
- `project_id` (TEXT, FK): Foreign key referencing `projects.project_id`.
- `surface` (TEXT): `DESKTOP`, `IDE`, `CLI_HEADLESS`, `CLI_INTERACTIVE`, `SDK`.
- `started_at` (TEXT): ISO 8601 UTC timestamp.
- `ended_at` (TEXT, Nullable): ISO 8601 UTC timestamp.
- `total_turns` (INTEGER): Cumulative turns executed.
- `token_usage_json` (TEXT): Serialized `{prompt, candidates, thoughts, total}`.

### 3. `missions`
- `mission_id` (TEXT, PK): AntiOS mission identifier (e.g. `M-20260906-001`).
- `session_id` (TEXT, FK): Foreign key referencing `sessions.session_id`.
- `project_id` (TEXT, FK): Foreign key referencing `projects.project_id`.
- `intent_query` (TEXT): Normalized task prompt (secrets redacted).
- `task_class` (TEXT): AntiOS TaskClass (e.g. `BUG_FIX`, `FEATURE_IMPLEMENTATION`).
- `risk_tier` (TEXT): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- `workforce_mode` (TEXT): `SOLO`, `FOCUSED`, `PARALLEL`, `HIERARCHICAL`.
- `status` (TEXT): `ACTIVE`, `COMPLETED`, `FAILED`, `ABORTED`.
- `stop_gate_exit_code` (INTEGER, Nullable): Final returncode from stop gate.
- `created_at` (TEXT): ISO 8601 UTC timestamp.
- `completed_at` (TEXT, Nullable): ISO 8601 UTC timestamp.

### 4. `turns`
- `turn_id` (TEXT, PK): Deterministic `turn_{session_id}_{step_idx}`.
- `mission_id` (TEXT, FK): Foreign key referencing `missions.mission_id`.
- `step_idx` (INTEGER): Monotonic sequence number in conversation.
- `agent_role` (TEXT): e.g. `PrimaryEngineer`, `Maker`, `Checker`, `Researcher`.
- `agent_conversation_id` (TEXT): Subagent conversation ID if executed in child context.
- `duration_ms` (INTEGER): Execution duration of step in milliseconds.
- `created_at` (TEXT): ISO 8601 UTC timestamp.

### 5. `tool_calls`
- `call_id` (TEXT, PK): Deterministic `call_{turn_id}_{call_idx}`.
- `turn_id` (TEXT, FK): Foreign key referencing `turns.turn_id`.
- `tool_name` (TEXT): Normalized tool name (`run_command`, `view_file`, etc.).
- `sanitized_args_json` (TEXT): JSON arguments scrubbed of secrets, absolute paths relativized.
- `exit_code` (INTEGER, Nullable): Subprocess returncode if shell command.
- `status` (TEXT): `SUCCESS`, `ERROR`, `DENIED_BY_GUARD`, `TIMED_OUT`.
- `output_sha256` (TEXT): SHA-256 of raw stdout/stderr.
- `output_summary` (TEXT): Compacted representation ($\le 500$ chars).
- `duration_ms` (INTEGER): Execution latency.

### 6. `engineering_events`
- `event_id` (TEXT, PK): `evt_{SHA-256(type|project_id|timestamp|signature)[:16]}`.
- `mission_id` (TEXT, FK): Foreign key referencing `missions.mission_id`.
- `project_id` (TEXT, FK): Foreign key referencing `projects.project_id`.
- `event_type` (TEXT): Mapped to canonical taxonomy (see 3.3).
- `epistemic_grade` (TEXT): `FACT`, `INFERENCE`, `ASSUMPTION`.
- `affected_file` (TEXT, Nullable): Relative workspace path.
- `event_signature` (TEXT): Deterministic deduplication hash.
- `payload_json` (TEXT): Bounded event details ($\le 1,000$ chars).
- `created_at` (TEXT): ISO 8601 UTC timestamp.

---

## 3.3 Engineering Event Taxonomy

AntiOS 2.1 aligns directly with the 13 canonical observation types from `learning.py`, extended with physical telemetry signals:

```
                                ENGINEERING EVENT TAXONOMY
                                             │
      ┌──────────────────────────────────────┼──────────────────────────────────────┐
      │                                      │                                      │
[EXECUTION OUTCOMES]                   [VERIFICATION & TESTS]                 [NAVIGATION & TOOLS]
- TASK_OUTCOME                         - TEST_FAILURE                         - REPEATED_NAVIGATION_PATH
- SUCCESSFUL_FIX                       - VERIFICATION_RESULT                  - TOOL_FAILURE
- RECOVERY_EVENT                       - PROOF_INVALIDATED                    - CAPABILITY_GAP
- REJECTED_APPROACH                    - RECURRING_FAILURE_SIGNATURE          - UNNECESSARY_EXPLORATION_TRAP
      │                                      │
      └──────────────────┬───────────────────┘
                         │
              [DISCOVERY & CONVENTIONS]
              - USER_CORRECTION
              - PROJECT_CONVENTION
              - ARCHITECTURAL_DISCOVERY
              - SPECIALIST_FINDING
```

| Event Type | Epistemic Grade | Trigger Condition | Persistence Policy |
| :--- | :---: | :--- | :--- |
| **`TASK_OUTCOME`** | FACT | Stop Gate passes or fails mission turn | **DURABLE**: Retained across sessions |
| **`TEST_FAILURE`** | FACT | Physical test runner emits non-zero returncode | **DURABLE**: Retained for failure analysis |
| **`SUCCESSFUL_FIX`** | FACT | Passing test execution following previous `TEST_FAILURE` | **DURABLE**: Promotes to candidate lesson |
| **`USER_CORRECTION`** | FACT | User prompt following agent error or turn rejection | **DURABLE**: High epistemic weight (0.9) |
| **`PROJECT_CONVENTION`** | INFERENCE | Discovered pattern verified across multiple files | **DURABLE**: Feeds `PROJECT_KNOWLEDGE.md` |
| **`ARCHITECTURAL_DISCOVERY`** | INFERENCE | New component/subsystem mapping discovered | **DURABLE**: Feeds `project_anatomy.json` |
| **`REPEATED_NAVIGATION_PATH`** | FACT | Consecutive file opens in identical order $\ge 2$ times | **TRANSIENT / COMPACTED**: Retained as weight |
| **`TOOL_FAILURE`** | FACT | Tool execution returns `ERROR` or non-zero exit | **DURABLE**: Feeds `tool_policy.py` reliability |
| **`SPECIALIST_FINDING`** | INFERENCE | Maker/Checker/Researcher emits structured handoff | **MISSION-SCOPED**: Compacted on mission end |
| **`VERIFICATION_RESULT`** | FACT | Independent Maker-Checker audit verdict emitted | **DURABLE**: Feeds release certification |
| **`RECOVERY_EVENT`** | FACT | Resumption of interrupted mission via recovery engine | **DURABLE**: Tracks robustness |
| **`CAPABILITY_GAP`** | FACT | Agent requires tool/binary missing from environment | **DURABLE**: Surfaces tooling debt |
| **`REJECTED_APPROACH`** | INFERENCE | Working tree reverted following failed test run | **DURABLE**: Feeds dead-end memory |

---

# R4 — Privacy, Security & Boundary Protection

## 4.1 The Ironclad Collection Redline

AntiOS 2.1 operates under an absolute privacy boundary. The following items are **strictly prohibited from ever entering the experience database, logs, or telemetry**:

```
                               PROHIBITED FROM COLLECTION
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ [X] Passwords, API Keys, Personal Access Tokens, Private Keys, SSH Keys, Certificates   │
│ [X] HTTP Authorization Headers, Cookies, Bearer Tokens, OAuth Refresh Tokens           │
│ [X] .env files, credentials.json, secrets.yaml, id_rsa, .npmrc, .pypirc                 │
│ [X] System Clipboard Buffers & Keystroke Logs                                           │
│ [X] Arbitrary personal user files outside workspace root (~/Documents, ~/Downloads)     │
│ [X] Complete raw source code files (Only diffs, structural symbols, and bounded ranges) │
│ [X] Screenshots & UI pixel captures unless explicitly authorized by user               │
│ [X] Raw internal model Chain-of-Thought ("thinking" field from Gemini 2.0 / Flash)     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

> **Why Raw Chain-of-Thought (CoT) Is Strictly Prohibited**:  
> Ingesting model `thinking` deltas violates user privacy, creates severe IP contamination liabilities, and bloats databases with non-deterministic probabilistic tokens. AntiOS records what the agent **did** (tool calls, diffs, commands) and what the environment **witnessed** (exit codes, test results), never raw internal reasoning tokens.

---

## 4.2 Deterministic Secret Redaction & Path Sanitization

Before any payload is written to SQLite, it passes through the `TelemetrySanitizer`:

1. **Secret Pattern Redaction**:
   - Matches known API key formats: `AIza[0-9A-Za-z-_]{35}` (Google), `ghp_[0-9A-Za-z]{36}` (GitHub PAT), `gho_[0-9A-Za-z]{36}` (GitHub OAuth), `sk-[0-9A-Za-z]{48}` (OpenAI), `AKIA[0-9A-Z]{16}` (AWS Access Key).
   - Matches generic key/value assignments: `(?i)(password|secret|token|api_key|auth_token|bearer)\s*[:=]\s*['"][^'"]+['"]` $\to$ replaced with `[REDACTED_SECRET]`.
2. **Path Relativization & Normalization**:
   - All absolute filesystem paths matching `workspacePaths` are stripped of machine prefixes (e.g. `c:\Users\Suraj\Documents\Antigravity\AntiOs\framework\core\gate.py` $\to$ `framework/core/gate.py`).
   - Forward slashes are enforced universally to ensure cross-platform reproducibility.
3. **Out-of-Workspace Path Rejection**:
   - Any tool call attempting to inspect or edit paths outside registered project roots is recorded with path `[OUT_OF_WORKSPACE_PATH]` and payload omitted.

---

## 4.3 Adversarial Defense & Anti-Poisoning Architecture

LLM agents are susceptible to prompt injection, hallucination loops, and adversarial repository files (e.g. malicious `README.md` or crafted test outputs attempting to poison agent memory).

AntiOS 2.1 defends against memory poisoning through four lines of defense:

```
[Untrusted Agent Input] ──> [1. Regex Injection Filter] ──> [2. Epistemic Source Tagging]
                                                                      │
[Durable Knowledge]     <── [4. Physical Test Ratchet]  <── [3. Multi-Run Recurrence Gate]
```

1. **Injection Pattern Filter (`LearningSafetyGate`)**:
   - Rejects observations containing instruction overrides: `ignore previous instructions`, `bypass stop gate`, `system prompt:`, `disregard invariants`, `elevate permissions`.
2. **Epistemic Source Tagging**:
   - Observations originating from agent text assertions are permanently tagged `AGENT_INTERPRETATION` (weight 0.3). They are mathematically incapable of self-promoting to durable knowledge without independent corroboration.
3. **Multi-Run Recurrence Gate**:
   - A pattern must recur across $\ge 2$ distinct missions with identical structural signatures before becoming a candidate lesson. Single-mission anomalies are pruned.
4. **Physical Test Ratchet Grounding**:
   - No lesson claiming a bug fix or architectural discovery can be promoted unless backed by an `EvidenceItem` with a verified native test runner exit code 0.
   - *Epistemic Law*: **"Untrusted text cannot promote itself; only physical verification creates truth."**

---

# R5 — SQLite & Storage Architecture Research

## 5.1 Architectural Topology Comparison

| Topology Option | Description | Concurrency & WAL | Privacy & Isolation | Portability & Backups | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option 1: Single Global DB (`~/.antios/all.db`)** | One giant database for all projects and sessions on the host. | High write lock contention; cross-project table locks. | High leakage risk; Project A queries could see Project B data. | Difficult to export single project; high blast radius on corruption. | **REJECTED** |
| **Option 2: Per-Project DB (`<repo>/.antios/experience.db`)** | Every repository has its own SQLite file inside the working tree. | Low contention; isolated to single project. | Perfect isolation; deleting project deletes data. | Pollutes git repos; fails on read-only checkouts; breaks cross-project learning. | **REJECTED** |
| **Option 3: Global Central Directory + Strict Project Tenant Scoping** | Central user-configured data dir (`D:\AntiOSData\experience.db`) with mandatory `project_id` tenant isolation. | Single central file; WAL mode allows concurrent readers + 1 writer. | High: queries default to `project_id = ?`; cross-project requires explicit opt-in. | One central location to backup, reset, or purge; zero repo pollution. | **RECOMMENDED (PRIMARY)** |
| **Option 4: Hybrid Dual-Layer Storage** | High-volume telemetry in central SQLite (`D:\AntiOSData\`); distilled durable proofs & lessons in repo (`docs/LESSONS.md`, `.antios/*.json`). | Optimal: heavy telemetry stays out of Git; durable facts stay with code. | Maximum: code-grounded proofs travel with git; granular trajectories remain local. | Cleanest git history; zero repository bloat; fully reproducible. | **RECOMMENDED (HYBRID ARCHITECTURE)** |

---

## 5.2 The Dedicated AntiOS Data Directory Model

AntiOS 2.1 adopts the **Hybrid Architecture (Option 4)** anchored in a user-configured **Central AntiOS Data Directory**:

```text
D:\AntiOSData\                         <-- Configured once during `antios install`
├── experience.db                      <-- Authoritative SQLite 3 database (WAL mode)
├── experience.db-wal                  <-- Write-Ahead Log journal
├── experience.db-shm                  <-- Shared memory index
├── config.toml                        <-- Global telemetry & retention settings
├── backups\                           <-- Automated daily/weekly database backups
│   └── experience_20260906.db.bak
└── exports\                           <-- User-triggered JSON/Markdown exports
    └── project_AntiOs_export.json
```

### Architectural Advantages
1. **Zero Repository Pollution**: Target projects never contain binary `.db` files that clutter `git status` or violate project policies.
2. **Read-Only Compatibility**: Operates seamlessly on read-only code checkouts, ephemeral CI environments, or network shares.
3. **Single Point of Governance**: The user can inspect total disk usage, run backups, export records, or reset all agent memory with a single CLI command (`antios data clean`).
4. **Tenant Isolation**: Every query in `experience.db` is strictly parameterized by `project_id`. Cross-project intelligence querying requires explicit, sanitized, aggregated views.

---

## 5.3 Concurrency, WAL Mode & Filesystem Reliability

SQLite 3 in the Python standard library (`import sqlite3`) provides production-grade local storage when configured with optimal PRAGMAs:

```sql
PRAGMA journal_mode = WAL;          -- Concurrent readers do not block writers; writer does not block readers
PRAGMA synchronous = NORMAL;        -- 1 fsync per checkpoint; 10x faster writes with zero corruption risk
PRAGMA busy_timeout = 5000;         -- Wait up to 5,000ms on lock contention before raising OperationalError
PRAGMA foreign_keys = ON;           -- Enforce relational integrity across sessions, missions, and events
PRAGMA auto_vacuum = INCREMENTAL;   -- Reclaim disk space incrementally upon retention pruning
```

- **Connection Management**: AntiOS 2.1 uses short-lived, transaction-scoped connections (`with closing(get_db_connection()) as conn: with conn: ...`). Connections are never held open across long-running turns.
- **Corruption Prevention**: Atomic write-ahead logging guarantees database ACID durability even if the host machine loses power or Antigravity crashes mid-turn.
- **Backup & Checkpoint**: Standard library `conn.backup(backup_conn)` performs hot, non-blocking online backups while agents are actively executing.

---

# R6 — Integration With Existing Learning, Evidence & Proof

## 6.1 The End-to-End Epistemic Pipeline

AntiOS 2.1 does **not** reinvent or replace existing AntiOS learning. It acts as the **telemetry feeder** that powers the existing epistemic hierarchy:

```
Platform Raw Telemetry (Antigravity Hooks & Transcripts)
               │
               ▼
[1] Event Normalization & Sanitizer
    - Strip absolute paths, PII, API tokens, passwords
    - Classify into Canonical Event Taxonomy
               │
               ▼
[2] Experience Store (D:\AntiOSData\experience.db)
    - Append-only event ledgering
    - Link to session, mission, turn, and tool call
               │
               ▼
[3] Deterministic Pattern Mining (Offline / Mission-End Triggered)
    - Jaccard similarity token clustering (threshold >= 0.70)
    - Detect recurring tool failures, fixes, navigation paths
               │
               ▼
[4] AntiOS Observation Store (.antios/learning_observations.json)
    - Create Observation with EpistemicSource (OBSERVED_FACT = 1.0)
    - Bounded capacity ceiling (<= 100 observations)
               │
               ▼
[5] Evidence Packaging (framework/core/evidence.py)
    - Corroborate with physical test runner exit code 0
    - Generate EvidenceItem with physical provenance
               │
               ▼
[6] Lesson Distillation & Promotion (framework/core/memory.py)
    - Multi-run recurrence check (>= 2 distinct tasks)
    - Promote: CANDIDATE -> VALIDATED -> DURABLE
               │
               ▼
[7] Durable Project Proof (.antios/proofs/proofs.json) & Markdown (docs/LESSONS.md)
    - Bind to physical file byte SHA-256 hashes
    - Commit human-auditable markdown lesson
```

---

## 6.2 Subsystem Ownership Demarcation

| Pipeline Transition | Owning Subsystem | Input Data | Output Contract | Verification Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Event Capture $\to$ Experience DB** | Telemetry Ingestion Engine (New in 2.1) | Hook payload on `stdin`, `transcript.jsonl` | Scrubbed row in `engineering_events` table | Regex secret redaction, path relativization |
| **Experience DB $\to$ Observation** | Pattern Mining Service (New in 2.1) | Aggregated event clusters ($\ge 2$ recurrences) | `Observation` object | `LearningSafetyGate` (injection scan, content bounds) |
| **Observation $\to$ Candidate Lesson** | `LessonDistillationEngine` (`learning.py`) | Recurring `Observation` records | `CandidateLesson` in `.antios/learning_observations.json` | Signature deduplication, contradictory pair check |
| **Candidate $\to$ Validated Lesson** | `EvidencePromotionEngine` (`learning.py`) | Candidate + `EvidencePackage` | `VALIDATED` lesson status | Physical test runner exit code 0 OR independent verifier |
| **Validated $\to$ Durable Proof** | `ProjectProofEngine` (`project_proof.py`) | Validated lesson + file paths | `ProjectProof` in `.antios/proofs/proofs.json` | Normalized physical file SHA-256 hash recomputation |
| **Validated $\to$ Durable Lesson** | `MemoryWritePolicy` (`memory.py`) | Multi-task validated lesson ($\ge 3$ tasks) | Formatted entry in `docs/LESSONS.md` | Human code review / Same Change Set git commit |
| **Lesson $\to$ Skill/Adapter Change** | `EvolutionProposalEngine` (`learning.py`) | Durable lesson | `EvolutionProposal` in `learning_proposals.json` | **EXPLICIT HUMAN APPROVAL MANDATORY** |

---

## 6.3 Gatekeeping & Lifecycle Authority

- **What Can Be Automatically Recorded (Zero Human Gate)**:
  - Raw telemetry events, tool call executions, command exit codes, file open sequences, test failure outputs.
- **What Requires Verification (Stop Gate / Checker Gate)**:
  - Classifying a sequence as a `SUCCESSFUL_FIX` (requires physical test runner exit code 0).
  - Promoting an observation to `VALIDATED` authority (requires passing verification).
- **What Requires Explicit Human Approval**:
  - Mutating any project skill (`.agents/skills/*`).
  - Mutating project adapter settings (`antios.config.json`).
  - Promoting evolution proposals to `APPLIED` status.
- **What Can Become Durable**:
  - Validated conventions, recurring failure signatures, verified command invocations, architecture subsystem boundaries.
- **What Must Expire / Decay**:
  - Telemetry older than retention window (default 90 days or 500 missions).
  - Proofs whose tracked file hashes have drifted (`INVALIDATED`).
  - Stale navigation hints after directory refactoring.
- **What Must NEVER Become Durable**:
  - Single-run agent inferences unsupported by physical exit codes.
  - Ephemeral tool output text buffers.
  - Conversational affirmations ("The tests passed!" without subprocess proof).

---

# R7 — Engineering Improvement Measurement

## 7.1 Defining Empirical Engineering Progress

AntiOS 2.1 explicitly rejects synthetic, gameable "LLM benchmark scores" (e.g. MMLU or conversational fluency). The system measures only **empirical, physical engineering workflow efficiency**:
> *"Over repeated missions on the same codebase, does AntiOS require fewer steps, touch fewer irrelevant files, experience fewer tool failures, avoid repeated mistakes, and reach stop-gate verification faster?"*

---

## 7.2 Metric Classification Matrix

```
                             ENGINEERING METRIC MATRIX
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
[DIRECTLY MEASURED]             [DERIVED METRICS]               [PROXY METRICS]
- Turn & Step Counts            - Navigation Efficiency Ratio   - Composite Cost Proxy
- Elapsed Wall-Clock Time       - First-Pass Stop Gate Rate     - Context Waste Ratio
- Process Exit Codes            - Unnecessary File Ratio        - Agent Friction Index
- Subagent Spawn Counts         - Redundant Tool Rate
- Native Test Return Codes      - Recovery Resolution Rate
- Staged Git Diff Lines         - Strategy Reuse Rate
```

| Metric Name | Category | Exact Mathematical Formula / Extraction Method | Engineering Significance |
| :--- | :---: | :--- | :--- |
| **Turn Count** | DIRECT | `COUNT(turns) WHERE mission_id = ?` | Measures conversational and operational verbosity. |
| **Tool Failure Rate** | DIRECT | `COUNT(tool_calls WHERE exit_code != 0) / COUNT(tool_calls)` | Measures tool invocation precision. |
| **Test Verification Passes** | DIRECT | `stop_gate.py` subprocess returncode == 0 | Absolute criterion of physical correctness. |
| **Files Touched** | DIRECT | `COUNT(DISTINCT affected_file) FROM git diff` | Scope and blast radius of change set. |
| **Navigation Efficiency** | DERIVED | `1.0 - (pre_edit_unrelated_file_reads / total_file_reads)` | Measures wayfinding accuracy; higher is better. |
| **First-Pass Stop Gate Rate** | DERIVED | `% of missions where initial test execution exits 0` | Measures implementation correctness on turn 1. |
| **Unnecessary File Ratio** | DERIVED | `files_inspected_outside_subsystem / total_files_inspected` | Measures exploration traps and lost context. |
| **Redundant Tool Rate** | DERIVED | `duplicate_identical_commands / total_commands` | Detects spinning loops and stalled agents. |
| **Strategy Reuse Rate** | DERIVED | `reused_durable_proofs / total_subsystem_tasks` | Demonstrates that learned experience is actively leveraged. |
| **Proof Invalidation Rate** | DERIVED | `proofs_invalidated_by_hash_drift / total_active_proofs` | Measures repository drift and codebase churn. |
| **Composite Cost Proxy** | PROXY | `(context_tokens * 0.001) + (tool_calls * 0.5) + (spawns * 5.0) + (unnecessary_files * 2.0)` | Single composite operational cost index. |
| **Context Waste Ratio** | PROXY | `tokens_classified_DISCARDED / total_tokens_ingested` | Measures signal-to-noise ratio in context governor. |

---

## 7.3 Demonstrating Measurable Improvement Across Sessions

AntiOS 2.1 verifies its own effectiveness by comparing telemetry across longitudinal runs on identical tasks (Proving Ground Scenarios A–J):

```text
Run 1 (Cold Start):
  - Wayfinding: Crawls 14 files across 4 directories
  - Test Runner: Attempts global `pytest` (fails: binary not in PATH)
  - Tool Calls: 18 tool calls before locating correct file
  - Result: Correct fix after 3 test retries; Cost Proxy = 42.5

Run 2 (With Experience Intelligence):
  - Wayfinding: Prior proof maps subsystem directly to `framework/core/gate.py`
  - Tool Policy: Proof specifies runner command `python -m pytest`
  - Tool Calls: 3 tool calls directly to target file
  - Result: Passes Stop Gate on Turn 1; Cost Proxy = 8.2 (80.7% Cost Reduction)
```

---

# R8 — Architecture Conflict & Governance Audit

## 8.1 Governance Conflict Audit

Every proposed capability of AntiOS 2.1 has been evaluated against AntiOS 2.0 constitutional documents:

| Proposed 2.1 Capability | Constitutional Constraint | Evaluation & Impact | Classification |
| :--- | :--- | :--- | :---: |
| **Central SQLite Experience Store** | `ARCHITECTURE_FREEZE.md` Sec 3 / INV-15 | Stored in `D:\AntiOSData\experience.db`. Zero background daemons; purely event-driven during turn lifecycle. Standard library `sqlite3` only. | **COMPATIBLE** |
| **Global Data Directory Model** | INV-10 Demarcation (`SOURCE ≠ INSTANCE ≠ PROJECT`) | Target repos configure identity via `antios.config.json`; repos remain 100% clean of binary databases. | **COMPATIBLE** |
| **Antigravity Hooks & Transcript Bridge** | INV-01 Platform Sovereignty / INV-16 Zero Custom Runtime | Uses native `hooks.json` and passive `transcript.jsonl` tailing. Zero custom schedulers. | **COMPATIBLE** |
| **Structured Telemetry Ingestion** | INV-11 Strict Epistemic Separation | Telemetry items are strictly classified as `EpistemicGrade.FACT`. Cannot pose as verified proof. | **COMPATIBLE** |
| **Raw Prompt Storage** | Privacy Boundary / AntiOS Constitution Sec 1 | Storing user prompts risks secret leakage and bloats storage envelopes. | **REJECT** |
| **Raw Chain-of-Thought Storage** | Privacy Boundary / IP Compliance | Non-deterministic, probabilistic model reasoning tokens. Severe leakage liability. | **REJECT** |
| **Vector Database / Embedding Models** | `ARCHITECTURE_FREEZE.md` Sec 3 / DECISION 06 / INV-09 | Vector databases are **permanently banned**. AntiOS uses deterministic inverted indices and SQLite relational queries. | **REJECT / BANNED** |
| **Background Sync / File Watcher Daemon** | `ARCHITECTURE_FREEZE.md` Sec 3 / INV-15 | Background daemons are **permanently banned**. Telemetry ingestion must occur strictly on hook events or session exit. | **REJECT / BANNED** |
| **Autonomous Self-Modifying Code** | `ARCHITECTURE_FREEZE.md` Sec 3 / Phase 64 / ADR 85 | Learning emits proposals (`learning_proposals.json`); never mutates code or skills without human approval. | **REJECT / BANNED** |
| **Offline Pattern Analysis Engine** | INV-15 Event-Driven Execution | Triggered deterministically at Stop Gate turn conclusion or via CLI (`antios distill`). | **COMPATIBLE** |
| **Existing Learning/Proof Integration** | INV-12 Durable Proof Hash Grounding | Experience feeds `learning.py` as evidence; proofs remain hash-grounded in physical disk reality. | **COMPATIBLE** |
| **OpenTelemetry (OTel) Exporter** | INV-01 Platform Sovereignty / Host Readiness | Antigravity engine does not yet support native in-process OTel export hooks. Custom daemons are banned. | **DEFER** |
| **MCP Experience Store Server** | INV-16 Runtime Simplicity | Exposing SQLite over MCP adds IPC hops, process management, and latency. Standard Python library is superior. | **DEFER (AntiOS 3 Candidate)** |

---

## 8.2 Scope Demarcation: AntiOS 2.1 vs AntiOS 3.0

- **AntiOS 2.1 (Scope of this Proposal)**:
  - Local SQLite Experience Store in Central Data Directory (`D:\AntiOSData\`).
  - Event-driven hook and transcript bridge.
  - Secret redaction and privacy boundary engine.
  - Trajectory ledgering and empirical pattern mining.
  - Feeds existing `learning.py`, `evidence.py`, and `project_proof.py`.
  - 100% compliant with 2.0 Freeze Charter; zero background daemons, zero vector DBs.
- **AntiOS 3.0 (Future Major Paradigm Shifts Only)**:
  - Distributed cross-repository coordination across multiple git remotes.
  - Native Host Platform In-Process IPC / WASM Hooks replacing shell subprocesses.
  - Native OpenTelemetry engine integration if provided natively by Google Antigravity.
  - Formal mathematical verification provers (Lean, Coq, TLA+) integrated into Stop Gate.

---

# R9 — Final Architecture Recommendation

## 9.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GOOGLE ANTIGRAVITY ENGINE                                     │
│                              (Desktop 2.0 / IDE / CLI / SDK)                                    │
└───────────────────────┬─────────────────────────────────────────────────┬───────────────────────┘
                        │                                                 │
            (A) Synchronous Hook IPC                          (B) Append-Only Disk
          (.agents/hooks.json stdin/stdout)                   (transcript.jsonl)
                        │                                                 │
                        ▼                                                 ▼
┌───────────────────────────────────────────────┐     ┌───────────────────────────────────────────┐
│         AntiOS 2.0 CONTROL PLANE              │     │         AntiOS 2.1 TELEMETRY PLANE        │
│  ┌─────────────────────────────────────────┐  │     │  ┌─────────────────────────────────────┐  │
│  │ pre_tool_guard.py (INV-02)              │  │     │  │ Transcript Stream Parser            │  │
│  │  - Fail-closed path boundary protection │  │     │  │  - Step timing, tool calls, args    │  │
│  │  - Shallow overwrite transform          │  │     │  └──────────────────┬──────────────────┘  │
│  └─────────────────────────────────────────┘  │     │                     │                     │
│  ┌─────────────────────────────────────────┐  │     │  ┌──────────────────▼──────────────────┐  │
│  │ stop_gate.py (INV-04)                   │  │     │  │ Telemetry Sanitizer & Privacy Guard │  │
│  │  - Native test runner subprocess exit 0 │  │     │  │  - Scrub secrets, tokens, PII       │  │
│  │  - Same Change Set verification         │  │     │  │  - Relativize paths; drop raw CoT   │  │
│  └─────────────────────────────────────────┘  │     │  └──────────────────┬──────────────────┘  │
└───────────────────────┬───────────────────────┘     └─────────────────────┼─────────────────────┘
                        │                                                   │
                        │ Pass / Fail Verdict                               │ Clean Structured Events
                        │                                                   │
                        ▼                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              CENTRAL DATA DIRECTORY (D:\AntiOSData\)                            │
│                                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                experience.db (SQLite 3 WAL)                             │   │
│   │   [projects] ──< [sessions] ──< [missions] ──< [turns] ──< [tool_calls] ──< [events]     │   │
│   └────────────────────────────────────────────┬────────────────────────────────────────────┘   │
└────────────────────────────────────────────────┼────────────────────────────────────────────────┘
                                                 │
                                                 │ Empirical Recurrence Mining
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            EXISTING AntiOS 2.0 EPISTEMIC ENGINE                                 │
│                                                                                                 │
│   ┌───────────────────────────┐      ┌───────────────────────────┐      ┌────────────────────┐  │
│   │ ObservationStore          │ ───> │ EvidencePromotionEngine   │ ───> │ ProjectProofStore  │  │
│   │ (.antios/observations.json│      │ (Physical Exit Code 0)    │      │ (.antios/proofs/)  │  │
│   └───────────────────────────┘      └─────────────┬─────────────┘      └────────────────────┘  │
│                                                    │                                            │
│                                                    ▼                                            │
│                                      ┌───────────────────────────┐                              │
│                                      │ docs/LESSONS.md (DURABLE) │                              │
│                                      └───────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9.2 Complete Decision Table

| Capability | Decision | Architectural Rationale & Constraints |
| :--- | :---: | :--- |
| **SQLite Experience Store** | **IMPLEMENT** | Standard library `sqlite3`, WAL mode, relational schema. Centralized, lightweight, dependency-free. |
| **Global Data Directory (`D:\AntiOSData\`)** | **IMPLEMENT** | Keeps git repositories clean; works on read-only checkouts; centralizes backup/reset. |
| **Antigravity Event Bridge** | **IMPLEMENT** | Ingests `transcript.jsonl` and hook metadata; zero platform reimplementation (INV-01). |
| **Structured Telemetry** | **IMPLEMENT** | Records tool calls, exit codes, durations, diff sizes as `EpistemicGrade.FACT`. |
| **Raw Prompt Storage** | **REJECT** | Privacy risk; PII/secret leakage danger. Store normalized intent only. |
| **Raw Chain-of-Thought Storage** | **REJECT** | IP risk; non-deterministic; model safety compliance liability. Token counts only. |
| **Vector Database / Embeddings** | **REJECT** | **Permanently banned** by Freeze Charter Sec 3, DECISION 06, INV-09. Deterministic index only. |
| **Background Watcher Daemon** | **REJECT** | **Permanently banned** by Freeze Charter Sec 3, INV-15. 100% event-driven execution. |
| **Autonomous Code Mutation** | **REJECT** | **Permanently banned**. Learning emits proposals; human must authorize code/skill edits. |
| **Pattern Analysis Engine** | **IMPLEMENT** | Deterministic token clustering (Jaccard $\ge 0.70$) triggered at mission end or via CLI. |
| **Existing Learning Integration** | **IMPLEMENT** | Feeds `ObservationStore` $\to$ `EvidenceItem` $\to$ `CandidateLesson` $\to$ `ProjectProof`. |
| **OpenTelemetry (OTel)** | **DEFER** | Platform does not provide native OTel hooks; building custom daemon violates INV-15. |
| **MCP Experience Server** | **DEFER** | Adds unnecessary IPC overhead. Python stdlib access is faster and more reliable. (AntiOS 3). |

---

# Executive Decision

## 1. What We Should Build (AntiOS 2.1 Scope)
1. **Central Data Directory Architecture**:
   - Support `ANTIOS_DATA_DIR` environment variable (defaulting to `~/.antios/data/` or user path e.g. `D:\AntiOSData\`).
   - Manage `experience.db`, `config.toml`, `backups/`, and `exports/`.
2. **Standard Library SQLite Experience Storage Engine**:
   - Zero external dependencies (`sqlite3` only).
   - Relational schema: `projects`, `sessions`, `missions`, `turns`, `tool_calls`, `engineering_events`.
   - WAL mode, synchronous normal, strict tenant isolation via `project_id`.
3. **Telemetry Sanitizer & Redaction Guard**:
   - High-speed regex secret scrubber for API keys, passwords, and tokens.
   - Absolute path relativizer; raw CoT stripper.
4. **Event-Driven Transcript Tail Ingestion**:
   - Reads `transcriptPath` passed via hook payload or session exit.
   - Ingests tool execution facts without blocking conversational latency.
5. **Pattern Mining & Learning Feeder**:
   - Turn-triggered distillation feeding multi-session recurrence counts into existing `framework/core/learning.py:ObservationStore`.
6. **Unified CLI Data Management Commands**:
   - `antios data status`: Display database size, mission counts, event totals.
   - `antios data export --project <id>`: Export scrubbed telemetry to JSON.
   - `antios data backup`: Execute non-blocking online hot backup.
   - `antios data purge --project <id>`: Remove project history while preserving central schema.

---

## 2. What We Should NOT Build
- **NO Background Watcher Daemons or Schedulers**: Strictly event-driven.
- **NO Vector Databases or Embeddings**: Inverted indices, relational tables, and Jaccard tokens only.
- **NO Custom Agent Execution Runtimes**: Execution belongs 100% to Google Antigravity.
- **NO Autonomous Self-Modifying Code**: Evolution proposals require human sign-off.
- **NO Raw CoT / Thinking Token Storage**: Metadata and step counts only.
- **NO In-Repo Experience Databases**: Repositories remain clean of binary database files.

---

## 3. What AntiOS 2.1 Should Contain
AntiOS 2.1 will be delivered as a non-breaking, backward-compatible extension adhering to `ARCHITECTURE_FREEZE.md` permitted category `PERFORMANCE_IMPROVEMENT` and `CORRECTNESS_IMPROVEMENT`, accompanied by a formal Architectural Decision Record (ADR 87).

Core development will introduce:
- `framework/core/experience.py`: SQLite connection manager, schema migrations, and event writer.
- `framework/core/sanitizer.py`: Secret scrubbing and path relativization.
- `framework/core/telemetry_bridge.py`: Transcript parser reading `transcript.jsonl`.
- `framework/core/pattern_miner.py`: Deterministic recurrence mining feeding `learning.py`.
- Target runtime script `.antios/runtime/log_turn.py`: Fast, non-blocking post-tool/stop telemetry logger.

---

## 4. What Would Require AntiOS 3.0
- Native OpenTelemetry engine export.
- Host platform in-process C++/WASM hooks.
- Cross-repository distributed coordination across multiple git remotes.
- Formal mathematical verification provers.

---

## 5. Recommended Implementation Phases (Phase 103+)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 103: Storage & Schema Foundation                                                 │
│ - Central Data Directory resolution (ANTIOS_DATA_DIR)                                  │
│ - SQLite relational schema initialization & WAL mode configuration                     │
│ - Zero-dependency connection manager & unit test suite                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 104: Telemetry Sanitizer & Privacy Engine                                        │
│ - High-speed regex secret scrubber                                                     │
│ - Path relativizer and out-of-workspace boundary defender                               │
│ - Comprehensive adversarial privacy test suite (synthetic API keys, tokens)            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 105: Transcript Bridge & Event Ingestion                                         │
│ - Append-only NDJSON parser for transcript.jsonl                                       │
│ - Normalization to canonical Engineering Event Taxonomy                                │
│ - Integration with .agents/hooks.json (PostToolUse and Stop triggers)                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 106: Epistemic Bridge & Learning Integration                                     │
│ - Deterministic pattern miner (recurrence clustering)                                  │
│ - Feeder to framework/core/learning.py (ObservationStore)                              │
│ - End-to-end verification: Event -> Observation -> Evidence -> Proof                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 107: CLI Data Management & Beta Hardening                                        │
│ - `antios data` CLI commands (status, export, backup, purge)                           │
│ - Proving ground validation across Scenarios A-J                                       │
│ - ADR 87 ratification & documentation update                                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Open Questions to Resolve Before Phase 103 Implementation

1. **Default Windows Directory Location**:
   - *Question*: Should the default fallback be `%LOCALAPPDATA%\AntiOS\` or `%USERPROFILE%\.antios\data\`?
   - *Recommendation*: Default to `%USERPROFILE%\.antios\data\` across all platforms (Windows, Linux, macOS) for consistency, while allowing explicit override via `ANTIOS_DATA_DIR` or `antios install --data-dir D:\AntiOSData`.
2. **Subprocess Spawn Overhead on Windows**:
   - *Question*: Running a python script on every tool call in `PostToolUse` adds ~25ms per step. Is this acceptable?
   - *Recommendation*: Yes. 25ms is imperceptible compared to LLM inference latency (1,000ms–5,000ms). Alternatively, defer transcript parsing to the `Stop` hook at turn completion to pay the spawn cost only once per mission turn.
3. **Database File Pruning Policy**:
   - *Question*: What is the hard ceiling for `experience.db` before automatic retention pruning triggers?
   - *Recommendation*: Enforce `MAX_EXPERIENCE_MISSIONS = 500` and `MAX_DATABASE_BYTES = 50,000,000` (50MB). When exceeded, prune oldest non-recurring events and run `PRAGMA incremental_vacuum`.

---
*End of Research Dossier. Prepared for Phase 103 execution.*
