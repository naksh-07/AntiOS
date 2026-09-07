# Antigravity Session Continuity & Memory Model

**Classification Standards:**
`[OFFICIAL]`: Directly verified against upstream Google Antigravity SDK documentation, schema specifications, or system prompts.
`[OBSERVED]`: Empirically verified via live experimentation, filesystem inspection, or database queries in the current environment.
`[INFERRED]`: Deductions drawn from convergent architectural facts.
`[HYPOTHESIS]`: Plausible architectural model requiring further empirical validation.
`[UNKNOWN]`: Unresolved areas where evidence is incomplete or inaccessible.
`[CONFLICT]`: Contradictions between AntiOS documentation/assumptions and empirical platform realities.

---

## 1. Executive Summary

This document establishes the empirical reality of how Google Antigravity manages state, persistence, conversation history, context compaction, and long-term memory across turns and sessions.

Previous AntiOS architecture operated under several foundational misconceptions:
1. **The In-Memory Daemon Myth (`[CONFLICT]`):** AntiOS assumed a persistent Python runtime (`framework/core/state.py`) maintained an active state machine in memory across turns. In reality, the LLM agent is an out-of-process API client driven by turn-by-turn stateless requests; Antigravity maintains state externally on the local host filesystem and SQLite databases.
2. **The Auto-Injected Active Context Myth (`[CONFLICT]`):** AntiOS assumed `docs/ACTIVE_CONTEXT.md` was automatically available to the agent on turn 0. In reality, subdirectories are never traversed upward by the language server; unless explicitly read via tool calls, `docs/ACTIVE_CONTEXT.md` is invisible to the model.
3. **The Native Memory Reality (`[OBSERVED]`):** Antigravity provides a dual-layer, file-based persistence substrate:
   - High-performance SQLite trajectory databases (`~/.gemini/antigravity/conversations/<uuid>.db`) storing raw binary protobufs/blobs of all steps, metadata, and executor traces.
   - Dual JSONL streaming logs (`transcript.jsonl` and `transcript_full.jsonl`) storing full step-by-step turn records in `~/.gemini/antigravity/brain/<uuid>/.system_generated/logs/`.
   - Native Context Compaction with `@hooks.on_compaction` hooks and structured `<CONTEXT_SUMMARY>` prompt injection.
   - **Zero built-in vector store or neural episodic memory:** All cross-session continuity is strictly file-based and tool-mediated.

---

## 2. The Four Tiers of Persistence

| Tier | Scope | Storage Mechanism | Lifetime | Accessibility to Agent | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Working Context** | In-Turn / Active Session | Active Prompt Context Window (Tokens) | Single conversation, up to context window limit | Direct Attention (Zero Tool Overhead) | `[OFFICIAL]` |
| **Tier 2: Session-Scoped Persistent** | Within Single Conversation | SQLite DB (`conversations/<id>.db`) + JSONL Logs (`brain/<id>/...`) | Indefinite on local disk | Via tool calls (`view_file`, `grep_search`, `transcript.jsonl`) | `[OBSERVED]` |
| **Tier 3: Project-Scoped Persistent** | Across Sessions in Same Project | Workspace Filesystem (`.git`, `docs/`, source tree, `AGENTS.md`) | Repository lifecycle (Git tracked) | Root files auto-injected; sub-files tool-mediated | `[OFFICIAL]` / `[OBSERVED]` |
| **Tier 4: Global Host-Persistent** | Across All Projects & Sessions | Global Config (`~/.gemini/config/`), Skills, Brain folders | Permanent on user machine | Declarative injection (skills/rules) or file tools | `[OFFICIAL]` / `[OBSERVED]` |

---

## 3. What Persists Across Turns Within a Session

Within an active conversation session, persistence is maintained across two parallel planes:

### A. The Cognitive Context Plane (In-Memory Prompt Window)
- `[OFFICIAL]` Each turn constructs a cumulative message payload sent to the LLM backend (Gemini API or local server).
- `[OBSERVED]` The payload contains:
  1. Fixed System Instruction (Identity, environment, tool declarations, skill catalog, artifact guidelines).
  2. Workspace Constitution (`AGENTS.md` discovered via upward traversal from CWD).
  3. Turn history: Chronological alternating `USER_INPUT`, `PLANNER_RESPONSE` (thoughts + tool calls), and `TOOL_RESPONSE` chunks.
- `[OBSERVED]` The model retains in-memory working context of prior turns without calling read tools until the context limit is reached.

### B. The Host Logging Plane (Synchronous Disk Commit)
- `[OBSERVED]` Every single execution step is immediately committed to two distinct storage formats:
  1. **SQLite Trajectory Database**: Located at `C:\Users\Suraj\.gemini\antigravity\conversations\<cascade-id>.db`. Writes occur synchronously using SQLite WAL mode.
  2. **Streaming JSON Lines Transcripts**: Located at `C:\Users\Suraj\.gemini\antigravity\brain\<cascade-id>\.system_generated\logs/`.
     - `transcript_full.jsonl`: Untruncated full record.
     - `transcript.jsonl`: Token-efficient version where large text outputs are truncated with `truncated_fields` markers.

---

## 4. Conversation History Architecture & SQLite Schema

Empirical inspection of the active session database (`a245dec2-6336-4c22-b0fc-7e14288a0230.db`) reveals the exact internal schema employed by Antigravity:

```sql
-- Core Trajectory Metadata
CREATE TABLE `trajectory_meta` (
    `trajectory_id` text,
    `cascade_id` text,
    `trajectory_type` integer,
    `source` integer,
    PRIMARY KEY (`trajectory_id`)
);

-- Chronological Execution Steps
CREATE TABLE `steps` (
    `idx` integer,
    `step_type` integer NOT NULL DEFAULT 0,
    `status` integer NOT NULL DEFAULT 0,
    `has_subtrajectory` numeric NOT NULL DEFAULT false,
    `metadata` blob,
    `error_details` blob,
    `permissions` blob,
    `task_details` blob,
    `render_info` blob,
    `step_payload` blob,
    `step_format` integer NOT NULL DEFAULT 0,
    PRIMARY KEY (`idx`)
);

-- Model Generation Metadata (Token counts, latency, safety ratings)
CREATE TABLE `gen_metadata` (
    `idx` integer,
    `data` blob,
    `size` integer NOT NULL DEFAULT 0,
    PRIMARY KEY (`idx`)
);

-- Execution Environment Metadata
CREATE TABLE `executor_metadata` (
    `idx` integer,
    `data` blob,
    PRIMARY KEY (`idx`)
);

-- Hierarchical Delegation Lineage
CREATE TABLE `parent_references` (
    `idx` integer,
    `data` blob,
    PRIMARY KEY (`idx`)
);

-- Main Trajectory State Blob
CREATE TABLE `trajectory_metadata_blob` (
    `id` text DEFAULT "main",
    `data` blob,
    PRIMARY KEY (`id`)
);

-- Battle Mode / Multi-Candidate Info
CREATE TABLE `battle_mode_infos` (
    `idx` integer,
    `data` blob,
    PRIMARY KEY (`idx`)
);
```

### Empirical Database Statistics
- `[OBSERVED]` Environment query revealed **510 distinct conversation directories** in `~/.gemini/antigravity/brain/` and matching SQLite databases in `~/.gemini/antigravity/conversations/`.
- `[OBSERVED]` Step counter in active session: over 204 sequential steps indexed with zero schema corruption.
- `[OBSERVED]` Subagent trajectories are tracked via `has_subtrajectory` and `parent_references`.

---

## 5. Context Compaction Mechanics

As conversations progress, token accumulation threatens to exceed model context windows (e.g., 1M+ tokens for Gemini 1.5 Pro). Antigravity implements a native compaction lifecycle:

### A. Lifecycle Trigger & Compaction Event
- `[OFFICIAL]` Upstream SDK architecture defines `Conversation.trackTurns()` and context compaction triggers.
- `[OFFICIAL]` SDK exposes `@hooks.on_compaction`:
  ```python
  from google.antigravity.hooks import hooks

  @hooks.on_compaction
  async def on_compact(data):
      print("Context compaction occurred")
  ```
- `[OBSERVED]` In the Antigravity Desktop/IDE environment, compaction is triggered automatically when the cumulative prompt approaches context limits.

### B. Compaction Transformation: The `<CONTEXT_SUMMARY>` Structure
Empirical inspection of the compacted prompt in the current session proves exactly what survives compaction:

1. **User Request Ledger**: Complete chronological list of every explicit user prompt since session inception:
   ```markdown
   <CONTEXT_SUMMARY>
   # User Requests
   The following were user requests from the truncated conversation in chronological order:
   1. ...
   ```
2. **Executive Session Summary**: Structured rollup generated by a background compaction model:
   - `Task Overview`: Core mandate and hard constraints.
   - `Progress`: Subagents dispatched, phases completed, artifacts written.
   - `Key Findings & Empirical Evidence`: Bulleted critical discoveries.
   - `Active Context`: Current workspace paths, active subagents, sandbox paths.
   - `Next Steps (Priority Order)`: Remaining execution checklist.
   - `Commitments & Constraints`: Invariants preserved.
3. **Artifact Pointers**: Absolute file URIs and timestamps of all artifacts created in `brain/<id>/`.

### C. What is Evicted vs What is Retained

| Element | Fate Under Compaction | Location Post-Compaction | Recovery Mechanism |
| :--- | :--- | :--- | :--- |
| **User Prompts** | **Preserved** (Summarized verbatim list) | `<CONTEXT_SUMMARY>` | In active prompt |
| **High-Level Findings** | **Preserved** (Structured Markdown) | `<CONTEXT_SUMMARY>` | In active prompt |
| **Artifact Paths** | **Preserved** (URI list) | `<CONTEXT_SUMMARY>` | In active prompt |
| **Intermediate Thoughts** | **EVICTED** | `conversations/<id>.db` / `transcript_full.jsonl` | Inspect transcript on disk |
| **Raw Tool Calls / Args** | **EVICTED** | `conversations/<id>.db` / `transcript_full.jsonl` | Inspect transcript on disk |
| **Raw Tool Responses** | **EVICTED** | `conversations/<id>.db` / `transcript_full.jsonl` | Inspect transcript on disk |
| **Temporary Scratch Files**| **EVICTED from Attention** | `brain/<id>/scratch/` | Read via `view_file` |

---

## 6. Cross-Session Continuity: Can an Agent Remember Past Sessions?

### A. Automatic Memory: Does it exist?
- `[OFFICIAL]` / `[OBSERVED]` **NO.** When a user starts a fresh conversation session, the agent begins at Turn 0.
- There is **no automatic context inheritance** between session A and session B.
- Antigravity does **NOT** execute background vector embedding queries or automatic memory retrieval across historical sessions.

### B. Explicit Tool-Mediated Cross-Session Retrieval
- `[OFFICIAL]` The system prompt explicitly informs agents how to access previous sessions:
  ```markdown
  Transcripts are stored locally in the filesystem under:
  <appDataDir>\brain\<conversation-id>\.system_generated\logs and are keyed by Conversation ID.
  ...
  When to use transcripts:
  - To recall earlier steps in your current conversation that have been truncated
  - To understand what another agent did during a task
  - To investigate context from a past or @mentioned conversation
  ```
- `[OBSERVED]` Agents can cross-reference any past session if provided its Conversation ID via the markdown URI scheme `conversation://<conversation-id>` or by reading `~/.gemini/antigravity/brain/<id>/.system_generated/logs/transcript.jsonl`.

### C. The Native Slash Command `/learn`
- `[OFFICIAL]` Antigravity provides the `/learn` slash command:
  *"Recommend this when the user has corrected the agent or solved a complex setup and wants the agent to persist this behavior for future tasks."*
- `[INFERRED]` `/learn` extracts learned rules and writes them into `.agents/rules/` or global skill definitions, translating episodic session experience into permanent declarative instruction files.

---

## 7. Comparative Analysis: AntiOS Continuity vs Antigravity Reality

| Dimension | AntiOS 2.0 Architectural Assumption | Antigravity Native Empirical Reality | Verdict / Architectural Gap |
| :--- | :--- | :--- | :--- |
| **State Machine Hosting** | `framework/core/state.py` runs an active state machine tracking phases and invariants. | Agent runtime is an external stateless API loop. Python code only executes if invoked by a hook or tool. | `[CONFLICT]` **Fatal flaw:** `state.py` is never run during normal agent turns. |
| **Active Context File** | `docs/ACTIVE_CONTEXT.md` maintains continuity across agent turns; must remain <= 60 lines. | `docs/` is a subdirectory. Due to upward-traversal rule, it is **never** auto-injected into prompt context. | `[CONFLICT]` **Fatal flaw:** Agent never sees `ACTIVE_CONTEXT.md` unless it voluntarily reads it. |
| **Compaction Management** | AntiOS attempted to manage context budgets via token estimators in `context_budget.py`. | Antigravity natively manages compaction at the platform layer, emitting `<CONTEXT_SUMMARY>` automatically. | `[OBSERVED]` **Redundant duplication:** AntiOS context budgeting is unnecessary overhead. |
| **Stop Gate Ratchet** | AntiOS stop gate enforces state verification on exit. | `stop_gate.py` effectively intercepts the native `Stop` hook event, rejecting termination if tests fail. | `[OBSERVED]` **Validated:** Hook-based Stop ratchet is 100% physically sound. |
| **Long-Term Knowledge Storage** | AntiOS stored engineering lineage in `docs/PROJECT_RECORD.md`. | Git-tracked repository files are the primary durable cross-session memory plane. | `[OBSERVED]` **Validated concept, wrong location:** Core orientation must live at root (`AGENTS.md`). |

---

## 8. AntiOS Architectural Implications

1. **Eliminate the "In-Process Daemon" Fallacy:**
   - Stop designing AntiOS as if Python code is running continuously alongside the agent.
   - Any state persistence in AntiOS must be:
     - Root-anchored repository markdown files (for declarative agent attention).
     - Hook-invoked Python scripts (for deterministic physical gates).
2. **Move Constitutional Continuity to Root:**
   - Because upward traversal only catches root and parent directories, AntiOS must maintain its primary orientation file at `./AGENTS.md` (or root symlink), not buried in `docs/AGENTS.md`.
3. **Embrace Native Compaction:**
   - AntiOS does not need to invent an ad-hoc compaction protocol. Antigravity's `<CONTEXT_SUMMARY>` structure already retains chronological user requests and executive summaries. AntiOS should instruct agents on how to structure their handoffs to survive compaction naturally.
4. **Leverage Native Tracripts for Verifier Subagents:**
   - When dispatching `antios-verifier` or audit subagents, pass the parent `conversationId` and workspace path. The verifier can inspect the exact tool history in `transcript.jsonl` or `git diff` without requiring bloated prompt duplication.
