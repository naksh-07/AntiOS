# AntiOS Pre-Architecture Research Dossier
## Executive Synthesis: The Antigravity Operating Model & Agent Engineering Reality

**Status**: RATIFIED PRE-ARCHITECTURE RESEARCH DOSSIER  
**Classification**: Foundational Architectural Synthesis  
**Authority**: AntiOS Pre-Architecture Discovery Mandate  
**Target Repository**: `c:\Users\Suraj\Documents\Antigravity\AntiOs`  
**Date**: September 7, 2026  

---

## 1. Executive Conclusion

Google Antigravity is an exceptionally fast, highly capable AI development platform built on a compiled Language Server (`language_server.exe`), remote Gemini foundation models, and an Electron/IDE desktop environment.

However, **it is a general-purpose agent runtime, not an engineering operating system for large codebases**.

When placed into an enterprise monorepo with hundreds of thousands of lines of code, native Antigravity exhibits predictable failure patterns:
- It suffers from **session amnesia** (100% context loss across session boundaries).
- It wastes tokens and turns on **brute-force rediscovery** (because the system prompt contains zero file tree information).
- It lacks **subsystem boundary awareness** (risking inadvertent corruption of upstream core code).
- It suffers from **verification bias** (agents assuming fixes work without rigorous empirical proof).

AntiOS was conceived to solve these exact problems. However, our forensic audit of the `Anki-maths` adaptation reveals that **current AntiOS 2.0/2.1 failed to realize this vision**:
- It created an architectural contradiction between **Runtime Isolation** (zero framework imports in target projects) and **Framework-Centric Telemetry** (telemetry requiring the monolithic `framework.core` package).
- Consequently, target instances had all telemetry code stripped; `.agents/hooks.json` omitted `PostToolUse`; the Central Experience Store received 1 project registration row and **zero ongoing telemetry rows**.
- 80% of AntiOS's 84 framework modules sat as dead code on disk, never participating in live agent turns.
- AntiOS functioned as **"many useful files beside the agent"** rather than an integrated operating layer.

**The Foundational Breakthrough**: AntiOS must stop trying to be an external software runtime or background daemon. AntiOS is fundamentally a **Project-Native Compiler and Governance Layer** that compiles an ordinary repository into an **Agent-Native Project Environment** using Antigravity's native extension surfaces (`.agents/skills/`, `.agents/hooks.json`, `AGENTS.md`, and `antios.config.json`).

---

## 2. Antigravity Operating Model (Summary)
*Full Analysis: [ANTIGRAVITY_OPERATING_MODEL.md](./ANTIGRAVITY_OPERATING_MODEL.md)*

Antigravity operates on a 3-tier architecture:
1. **Core Language Server (`language_server.exe` / `cortex`)**: Manages process lifecycles, MCP servers, filesystem monitors, tool execution policies, and token counting.
2. **Surfaces**: Antigravity 2.0 (Desktop), Antigravity IDE (VS Code), Antigravity CLI (`agy`), and Python SDK (`google-antigravity`). All surfaces share the same core engine and customization discovery.
3. **Native Extension Engine**: Discovers customizations in `.agents/` at repository root.
   - **Skills** (`.agents/skills/`): Modular procedural runbooks loaded via progressive disclosure.
   - **Rules** (`AGENTS.md`, `.agents/rules/`): Hierarchical markdown rules mounted into `<user_rules>`.
   - **Hooks** (`.agents/hooks.json`): Synchronous shell commands intercepting the loop at `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, and `Stop`.
   - **MCP Servers** (`mcp_config.json`): Local stdio and remote SSE tool providers.

**The Immutable Platform Law**: The ONLY mechanism in Antigravity with hard, unbypassable enforcement authority is **Lifecycle Hooks (`hooks.json`)**. All prompt rules, skills, and documentation are advisory.

---

## 3. Agent Lifecycle Model (Summary)
*Full Analysis: [ANTIGRAVITY_AGENT_LIFECYCLE.md](./ANTIGRAVITY_AGENT_LIFECYCLE.md)*

The real agent engineering lifecycle is an empirical 12-state recursive loop:
```
[Understand] ──> [Locate] ──> [Inspect] ──> [Reason] ──> [Plan] ──> [Change]
      ▲                                                                 │
      │                                                                 ▼
[Continue] <── [Re-verify] <── [Repair] <── [Diagnose] <── [Verify] <── [Execute]
```
- **Physical Reality**: The model is a stateless prediction function. It has zero zero-shot knowledge of file contents.
- **Critical Interception Points**:
  - `PreToolUse` protects the codebase before `Change` executes.
  - `Stop` enforces physical test execution ratchets before `Continue` is authorized.
  - `handoff.md` bridges the amnesia gap between `Continue` and the next session's `Understand`.

---

## 4. Context Model & The Rediscovery Penalty (Summary)
*Full Analysis: [ANTIGRAVITY_CONTEXT_MODEL.md](./ANTIGRAVITY_CONTEXT_MODEL.md)*

Context flows across 4 tiers:
1. **Automatically Available**: System prompt, `<user_information>` (workspace roots only), `<skills>` catalog metadata, root `AGENTS.md`.
2. **Progressive Disclosure**: Full `SKILL.md` (via `view_file`), lazy MCP schemas, model-decision rules.
3. **Ephemeral Injection**: Hook `injectSteps` and Stop rejection reasons.
4. **Transient Trajectory**: Message history compacted when token limits approach.

**Why Agents Rediscover Projects**: The system prompt intentionally contains **zero file tree data** to save tokens. Without a structured navigation map, the agent must spend 5–10 turns performing exploratory grep searches and directory walks. AntiOS eliminates this via `antios.config.json` (subsystem wayfinding manifests).

---

## 5. The Large Software Project Problem (Summary)
*Full Analysis: [ANTIGRAVITY_LARGE_PROJECT_ENGINEERING.md](./ANTIGRAVITY_LARGE_PROJECT_ENGINEERING.md)*

In 100,000+ line codebases, a request like "Fix the button bug in the frontend" fails without an operating layer because the agent lacks:
1. **Wayfinding**: Resolving feature names to directory paths.
2. **Subsystem Boundaries**: Knowing what code is forbidden from mutation (e.g. upstream core).
3. **Blast Radius**: Understanding monorepo package interdependencies.
4. **Verification Discovery**: Knowing which specific test runner exercises the component.
5. **Session Continuity**: Knowing past architectural decisions.

Antigravity provides fast tools (ripgrep, view_file); AntiOS provides the **project-specific semantic intelligence** that directs those tools.

---

## 6. Current AntiOS Failure Analysis (Summary)
*Full Analysis: [ANTIOS_FAILURE_ANALYSIS.md](./ANTIOS_FAILURE_ANALYSIS.md)*

The empirical failure observed in `Anki-maths` was caused by **five compound architectural flaws**:
1. **The Import Firewall vs Telemetry Contradiction**: `RuntimeClosureContract` mandated zero framework imports in target projects; the telemetry bridge was in `framework.core`; instance templates stripped telemetry to pass AST tests.
2. **Missing `PostToolUse` Registration**: `.agents/hooks.json` only registered `PreToolUse` and `Stop`. Tool completion events were never captured.
3. **Fail-Closed Default Mode (`OFF`)**: Telemetry collection defaults to OFF; configuration was omitted from the target project.
4. **Hook CWD Reality**: Antigravity runs hooks with `cwd = .agents/`, breaking naive relative path imports.
5. **Shell Mutation Bypass**: `PreToolUse` watched only `write_to_file|replace_file_content`, allowing `run_command` shell mutations to bypass security.

---

## 7. Exact Missing Integration Points

To function as a true operating layer, AntiOS must repair these exact platform seams:
1. **`PostToolUse` Registration**: Hook must be registered in `.agents/hooks.json` to receive tool completion events.
2. **Standalone Instance Emitter**: Telemetry emission must be a zero-dependency, self-contained script (`emit_event.py`) inside `.antios/runtime/` that writes directly to SQLite or appends to a local NDJSON spool without importing `framework/`.
3. **`run_command` Safety Interception**: `PreToolUse` matcher must intercept destructive shell operations (`rm`, `git reset`, `format`) or delegate shell policy to native Antigravity permission grants.
4. **CWD-Independent Path Resolution**: All hook scripts must resolve paths relative to `__file__` using `normcase(abspath(...))`.

---

## 8. AntiOS Intervention Map & System A/B Architecture (Summary)
*Full Analysis: [ANTIOS_INTERVENTION_MAP.md](./ANTIOS_INTERVENTION_MAP.md)*

AntiOS attaches exclusively to Antigravity's native extension surfaces:
- **`PreToolUse`** $\to$ Boundary Guard (`pre_tool_guard.py`)
- **`Stop`** $\to$ Stop Gate Verification (`stop_gate.py`)
- **`PostToolUse`** $\to$ Zero-Dependency Telemetry (`emit_event.py`)
- **System Prompt** $\to$ Governance Rules (`AGENTS.md`)
- **Progressive Disclosure** $\to$ Engineering Skills (`.agents/skills/*`)
- **Filesystem** $\to$ Project Manifest (`antios.config.json`) & Memory (`handoff.md`, `dead-ends.md`)

### The System A / System B Firewall:
- **System A (Project-Native Control Plane)**: Sovereign, 100% self-contained, checked into git, zero external dependencies.
- **System B (Cross-Project Experience Store)**: Central SQLite database (`experience.db`) receiving one-way sanitized telemetry. System A **never** reads or depends on System B.

---

## 9. Proposed Fundamental Purpose of AntiOS

### What AntiOS IS:
> **AntiOS is a deterministic engineering operating layer and compiler for Google Antigravity that equips large, complex software repositories with machine-readable wayfinding, physical boundary enforcement, automated test verification gates, and cross-session memory.**

### What AntiOS IS NOT:
- AntiOS is **NOT** an agent runtime (it never replaces `language_server.exe`).
- AntiOS is **NOT** a background daemon or watcher process (`INV-15`).
- AntiOS is **NOT** a vector database or embedding store (`INV-09`).
- AntiOS is **NOT** a mandatory multi-agent ceremony for simple tasks.
- AntiOS is **NOT** a heavy framework that target projects must import.

---

## 10. Core Architectural Principles for AntiOS Next

1. **Native Platform Harmony**: Never fight Antigravity. Build strictly on `.agents/skills/`, `.agents/hooks.json`, and `AGENTS.md`.
2. **Zero-Dependency Target Runtime**: Every script installed into a target project must run on the Python standard library with zero external imports.
3. **Physical Reality Over Prompt Guidance**: Never rely on LLM voluntary compliance for safety or verification. Back critical rules with physical hooks (`hooks.json`).
4. **Declarative Wayfinding Over Brute-Force Grep**: Compact JSON manifests (`antios.config.json`) map subsystems and test runners in 0 search turns.
5. **Physical Handoff Over Context Replay**: Standardized `handoff.md` checked into git solves cross-session amnesia deterministically.
6. **Strict System A / System B Separation**: Target project execution must be completely decoupled from central telemetry databases.
7. **Adaptive Complexity**: Simple tasks execute SOLO (0 subagents); multi-agent ceremonies activate only when complexity thresholds fire.

---

## 11. Open Questions for Phase 108

1. **Shell Command Boundary Enforcement**: Should `PreToolUse` attempt to parse and sandbox raw shell strings in `run_command`, or should AntiOS delegate command allowlisting to Antigravity's native `policy.confirm_run_command()`?
2. **Telemetry Ingestion Mechanics**: Should telemetry be emitted synchronously via `PostToolUse` into SQLite, or spooled to a lightweight append-only JSON file processed during post-session CLI sync?
3. **Framework Core Pruning**: Should the 84 modules in `framework/core/` be formally repackaged into an `antios` developer CLI tool, eliminating dead code confusion in target installations?

---

## 12. Evidence Classification Standard

Every claim in this dossier is indexed against the Antigravity Forensic Ledger:
- `[FACT]`: Verified in official Antigravity documentation (`agy-customizations/docs/*.md`, `antigravity_guide/references/*.md`, `google-antigravity` SDK).
- `[OBSERVED]`: Verified in live system files, active system prompts, or physical runtime databases (`experience.db`, `conversations/*.db`).
- `[INFERENCE]`: Logically inevitable deduction from verified technical architecture.
- `[HYPOTHESIS]`: Grounded architectural proposal for the next system revision.
