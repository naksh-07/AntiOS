# Antigravity Invocation Injection: Dynamic Context Steering & Ephemeral Mechanics

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity Customization Docs (`hooks.md:L238-278`), `[OBSERVED]` Empirical AntiOS Test Harness (`test_lifecycle_primitives.py`), `[INFERRED]` LLM Context Compaction Dynamics

---

## 1. Executive Summary

Research 1 demonstrated that Antigravity agents possess zero passive memory across sessions and rely on active context assembly during each turn. While instructions can be statically placed into root markdown files (`GEMINI.md`, `AGENTS.md`) or system prompts via skills, static rules suffer from context dilution, token bloat, and attentional decay over extended conversations.

The `PreInvocation` and `PostInvocation` hooks introduce an active, programmatic context injection primitive via `injectSteps`. This monograph analyzes the exact behavioral mechanics of `injectSteps`, contrasts the lifecycle of `ephemeralMessage`, `userMessage`, and `toolCall`, evaluates their token and compaction dynamics, and defines the optimal context steering strategy for AntiOS.

---

## 2. The `injectSteps` Protocol

When `PreInvocation` fires (immediately prior to LLM inference) or `PostInvocation` fires (immediately post-turn resolution), the hook script can return a JSON object containing an `injectSteps` array:

```json
{
  "injectSteps": [
    {
      "ephemeralMessage": "CRITICAL ADVISORY: Target file src/core.py is protected. Plan required before edits."
    },
    {
      "userMessage": "Automated pipeline notification: staging deployment succeeded."
    },
    {
      "toolCall": {
        "name": "view_file",
        "args": {
          "AbsolutePath": "c:\\Users\\Suraj\\Documents\\Antigravity\\AntiOs\\spec.md"
        }
      }
    }
  ]
}
```

Antigravity parses these steps and injects them directly into the agent's turn trajectory before the inference call is dispatched.

---

## 3. Comparative Analysis of Injection Step Types

The three step types exhibit fundamentally different persistence, token consumption, and UI visibility profiles:

| Property | `ephemeralMessage` `[OFFICIAL]` | `userMessage` `[OFFICIAL]` | `toolCall` `[OFFICIAL]` |
|---|---|---|---|
| **Trajectory Location** | Prepended to active prompt buffer | Appended as synthetic user turn | Injected as synthetic tool execution |
| **UI Rendering** | **Invisible** (hidden from user) | Visible in UI as user utterance | Visible in UI as tool call block |
| **Transcript Persistence (`transcript.jsonl`)** | **Zero Persistence** (never written) | **Durable** (written to disk) | **Durable** (written to disk) |
| **Database Persistence (SQLite DB)** | **Zero Persistence** (discarded) | **Durable** (stored in message table) | **Durable** (stored in step table) |
| **Token Impact Duration** | **Single Turn Only** | **Permanent** (all future turns) | **Permanent** (all future turns) |
| **Compaction Vulnerability** | N/A (cleared before compaction) | Subject to summarization/truncation | Subject to summarization/truncation |
| **Dialogue Semantic Impact** | Steers model reasoning cleanly | Simulates user speech; can confuse dialogue | Simulates tool execution flow |

---

## 4. Deep-Dive: `ephemeralMessage` Mechanics

### 4.1 Ephemeral Lifecycle & Attentional Hygiene `[OFFICIAL]` `[OBSERVED]`
The `ephemeralMessage` is the most powerful steering primitive in the Antigravity runtime:
1. **Zero Attentional Pollution**: Traditional prompt injections append user or system messages that permanently remain in the conversation history. Over a 50-turn engineering task, repeated reminder messages consume tens of thousands of tokens and cause severe attention drift. An `ephemeralMessage` exists only for the exact inference request in which it is dispatched.
2. **Transient System Prompts**: When the model finishes generating its response or tool call for that turn, the `ephemeralMessage` is discarded from active memory and is never written to `transcript.jsonl`.
3. **Turn-Targeted Steering**: Because `PreInvocation` receives `invocationNum` and `initialNumSteps`, an external script can dynamically assess the state of the workspace (e.g., git status, modified files, test failures) and inject precisely targeted guardrails only when necessary.

### 4.2 Compaction Dynamics `[INFERRED]`
When a long conversation approaches the LLM context window limit (e.g., 1M+ tokens), Antigravity triggers context compaction:
- Compaction algorithms inspect persisted messages in `transcript.jsonl`, generating high-level summaries and truncating older tool calls.
- Because `ephemeralMessage` is never persisted to disk, it **never participates in compaction**. It leaves zero residual baggage, zero truncated text, and zero synthetic user turns in the compacted summary.

---

## 5. Comparative Analysis: `userMessage` vs `toolCall`

### 5.1 When to Use `userMessage` `[OFFICIAL]`
- **Real User Asynchronous Signals**: Used when an external background process (such as a CI/CD build completion, webhook, or human operator comment) needs to be communicated to the agent as genuine external user feedback.
- **Permanent Dialogue Constraints**: Constraints that must remain part of the audited user transcript across all subsequent turns.

### 5.2 When to Use `toolCall` `[OFFICIAL]`
- **Synthetic Observation Pre-fetching**: If an external hook knows the agent will need to inspect a specific status file or test log, it can inject a synthetic `toolCall` to avoid a round-trip model reasoning cycle.
- **Caution**: Injecting synthetic `toolCall` steps without corresponding valid tool execution results will trigger schema validation faults in the agent loop.

---

## 6. Context Injection vs Root Rule Walk

In Research 1, we established that Antigravity performs an Upward Rule Walk on session startup, reading `GEMINI.md` and `AGENTS.md`. How does `PreInvocation` injection compare to static root instructions?

```
┌───────────────────────────────────────────────┐
│        STATIC INSTRUCTIONS (GEMINI.md)        │
│  - Loaded once at startup                     │
│  - Fixed across all turns                     │
│  - Static token cost on EVERY turn            │
│  - Attentional decay over long trajectories   │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│     DYNAMIC EPHEMERAL STEERING (PreInvocation)│
│  - Evaluated just-in-time per turn            │
│  - Injected only when specific conditions met │
│  - Zero token cost when not triggered         │
│  - Discarded immediately after turn           │
│  - Maximum attentional sharpness              │
└───────────────────────────────────────────────┘
```

---

## 7. AntiOS Strategic Architectural Blueprint

To leverage Antigravity's injection primitives without degrading performance, AntiOS must adopt a **Three-Tier Context Architecture**:

1. **Tier 1: Minimal Static Core (`AGENTS.md`)**
   - High-level role framing and pointer to AntiOS commands.
   - Kept under 50 lines (<500 tokens) to ensure zero context bloat.
2. **Tier 2: On-Demand Skill Activation (`SKILL.md`)**
   - Detailed domain workflows loaded only when invoked via tool or user trigger.
3. **Tier 3: Dynamic Ephemeral Governance (`PreInvocation`)**
   - Configured in `.agents/hooks.json`.
   - Before each turn, an AntiOS hook inspects the working tree:
     - If uncommitted changes exist in critical files, inject an `ephemeralMessage` reminding the agent of Stop Gate invariants.
     - If previous tool execution produced an error, inject targeted diagnostic hints.
     - If all files are clean, inject nothing (0 token overhead).
