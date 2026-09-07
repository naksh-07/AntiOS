# Antigravity Instruction & Rule Architecture
**Document**: `ANTIGRAVITY_INSTRUCTION_MODEL.md`  
**Status**: Foundational Research Dossier (Research 1)  
**Classification**: Rigorous Evidence-Backed Specification  
**Authority**: Official Customization Guides & Forensic Codebase Audit  

---

## 1. Executive Summary

This document establishes how persistent instructions enter and influence an Antigravity agent's behavior. It audits the two native instruction mechanisms provided by the platform:
1. **Directory-Based Rules (`GEMINI.md` / `AGENTS.md`)**: Hierarchical markdown files discovered by walking up from the current working directory to the repository root.
2. **Modular Rules (`.agents/rules/*.md`)**: Targeted markdown guidelines supporting trigger modes (`always_on`, `model_decision`) and glob pattern matching.

This research answers the pivotal architectural question:  
> **Are prompt instructions and rules merely cognitive guidance, or do they establish actual behavioral guarantees?**

The evidence proves that all prompt instructions—regardless of whether they are titled "Constitution", "Invariant", or "Master Rule"—operate strictly as **cognitive model steering**. They alter token generation probabilities, but provide **zero operating-system-level isolation or deterministic execution guarantees**. True enforcement requires physical process interceptors (`hooks.json`) and automated test exit codes.

---

## 2. Directory-Based Rules (`AGENTS.md` / `GEMINI.md`)

### 2.1 Discovery & Hierarchical Traversal
`[OFFICIAL]` Directory-based rules are placed directly in project directories. The Language Server discovers them through an automated upward traversal:
* When an agent starts a session or operates in a directory, the system walks **UP** from the current working directory (CWD) to the repository root (e.g. folder containing `.git`).
* All `GEMINI.md` and `AGENTS.md` files encountered along that upward path are loaded into the prompt context.
* **Scope of Application**: A rule file applies to the directory it resides in and **all its recursive subdirectories**.

```text
Repository Root/
├── AGENTS.md                  <-- [Loaded for EVERYTHING in repo]
├── backend/
│   ├── AGENTS.md              <-- [Loaded for backend/ and backend/api/]
│   └── api/
│       └── routes.py          <-- CWD: loads root/AGENTS.md + backend/AGENTS.md
└── docs/
    └── AGENTS.md              <-- [Loaded ONLY when operating inside docs/!]
```

### 2.2 Format & Frontmatter Restrictions
* `[OFFICIAL]` **No Frontmatter in Standalone Files**: Standalone `AGENTS.md` and `GEMINI.md` files **do not support YAML frontmatter**.
* `[OFFICIAL]` **Unconditional Activation**: If an `AGENTS.md` file is in the upward directory path, its entire text is loaded unconditionally. There is no progressive disclosure or triggering for standalone directory rules.
* `[OFFICIAL]` **Token Budget Invariant**: Because directory rules are injected into prompt context on every relevant turn, they must remain concise ($\le 40$ to $120$ lines) to avoid context bloat.

### 2.3 The Critical Subdirectory Flaw in AntiOS
* `[CONFLICT]` & `[OBSERVED]` **The `docs/AGENTS.md` Blindspot**:
  * AntiOS designed `docs/AGENTS.md` as its "Global Project Constitution" (`ANTIOS_CONSTITUTION.md:Sec 3`).
  * AntiOS assumed that Antigravity automatically indexes `docs/AGENTS.md` repository-wide (`ANTIOS_ARCHITECTURE.md:L146`).
  * **Empirical Reality**: Antigravity walks **UP** from CWD to the repository root. When an agent works at the repository root or in source directories (`framework/`, `tests/`), `docs/` is a sibling or child directory—it is **never** in the ancestor chain!
  * **Consequence**: In an AntiOS repository, **the constitution is never loaded into context on Turn 1**. The agent begins completely unoriented.

---

## 3. Modular Rules (`.agents/rules/*.md`)

### 3.1 Structure & Configuration
`[OFFICIAL]` Modular rules reside in `.agents/rules/` (or `.agent/rules/`, `_agents/rules/`). Unlike standalone `AGENTS.md` files, modular rules support YAML frontmatter:

```markdown
---
trigger: always_on | model_decision
glob: "**/*.ts"
description: "Enforce strict TypeScript interface and type safety conventions"
---

# TypeScript Guidelines
- Always declare explicit return types on public functions.
- Never use `any`; use `unknown` with type narrowing.
```

### 3.2 Activation Modes
1. `[OFFICIAL]` **Always-On (`trigger: always_on`)**: Loaded unconditionally into prompt context on Turn 0 of every session.
2. `[OFFICIAL]` **Glob-Matched (`glob: "<pattern>"`):** Loaded dynamically into context only when the agent views, opens, or edits a file whose path matches the specified glob pattern.
3. `[OFFICIAL]` **Model-Decision (`trigger: model_decision`)**: Implements progressive disclosure. Only the frontmatter description is visible initially; the full rule body is injected only if the model decides it is relevant to the current user prompt.

### 3.3 Rule Absence in AntiOS Repository
* `[OBSERVED]` A physical audit of the AntiOS repository reveals that **`.agents/rules/` does not exist**.
* AntiOS authored complex documentation regarding rule models, but failed to create the actual `.agents/rules/` directory or compile rule files in `framework/core/compiler.py`.
* As a result, AntiOS possesses **zero native modular rules** in its current distribution.

---

## 4. Rule Precedence, Merging & Deduplication

### 4.1 Precedence Hierarchy
`[OFFICIAL]` When multiple rules, instructions, or user directives interact, precedence resolves in this order:

```text
Rank 1: Deepest Nested Directory Rule (e.g. `packages/ui/AGENTS.md` - most specific)
        │
Rank 2: Parent Directory Rules up to Repository Root (`AGENTS.md` at root)
        │
Rank 3: Workspace Modular Rules (`.agents/rules/*.md` matching glob or trigger)
        │
Rank 4: Plugin Rules (`plugins/<name>/rules/AGENTS.md`)
        │
Rank 5: Global User Rules (`~/.gemini/config/`)
```

### 4.2 Deduplication Law
`[OFFICIAL]` Rules are deduplicated strictly by their **resolved canonical file path**. Even if a rule file is discovered via multiple paths or matches multiple triggers, it is injected **at most once per conversation turn**.

---

## 5. Cognitive Guidance vs. Deterministic Enforcement

### 5.1 The Prompt Sandboxing Myth
`[OFFICIAL]` A persistent misconception in AI framework design is that instructing an LLM not to perform an action provides a security guarantee.

```text
PROMPT DIRECTIVE:
"You MUST NOT modify files in framework/core/."

COGNITIVE REALITY:
The model processes this string as token attention weights.
Under complex reasoning, ambiguous instructions, or prompt injection:
- The model can hallucinate an exception.
- The model can prioritize user commands over system instructions.
- The model can issue a `replace_file_content` call to `framework/core/guard.py`.
```

Prompt directives provide **guidance, not enforcement**.

### 5.2 Deterministic Security Boundaries
`[OFFICIAL]` Deterministic enforcement in Antigravity occurs exclusively outside the model's cognitive space:
1. **Lifecycle Hook Gates (`PreToolUse` in `hooks.json`)**: Executes an external process before the tool runs. If the process outputs `{"decision": "deny"}`, the tool is aborted by the runtime before it touches the OS.
2. **Tool Execution Policies**: Platform-level whitelist/blacklist checks evaluated in compiled Go/C++ (`confirm_run_command`).
3. **Physical Process Ratchets (`Stop` hook in `hooks.json`)**: When the agent attempts to stop, the hook executes native test commands (`pytest`, `npm test`). If the exit code is non-zero, the completion is vetoed regardless of how confident the LLM claims to be.

---

## 6. Audit of Current AntiOS Instruction Assumptions

| AntiOS Assumption | Documented Location | Empirical Reality | Flaw Severity |
| :--- | :--- | :--- | :---: |
| **`docs/AGENTS.md` is auto-loaded** | `ANTIOS_ARCHITECTURE.md:L146` | Antigravity only walks root/CWD ancestors. `docs/AGENTS.md` is ignored. | **CRITICAL** |
| **`.agents/rules/` provides modular policy** | `docs/research/ANTIGRAVITY_OPERATING_MODEL.md` | `.agents/rules/` directory does not exist in the repository. | **HIGH** |
| **Constitution outranks user prompts** | `ANTIOS_CONSTITUTION.md:Sec 1` | `ANTIOS_SOURCE_OF_TRUTH.md` places Human Directives (Rank 2) above Constitution (Rank 4). | **HIGH** |
| **Context budget is enforced by gate** | `INVARIANT_REGISTRY.md:INV-09` | `gate.py` contains zero checks for `ACTIVE_CONTEXT.md` line limits. | **MEDIUM** |
| **84 Python modules govern the agent** | `framework/core/*.py` | LLM does not execute Python in-process. 82 of 84 modules never run in live turns. | **ARCHITECTURAL** |

---

## 7. Strategic Recommendations for Research 2

1. **Relocate Constitution to Root**: Place a token-bounded ($\le 40$ lines) `AGENTS.md` at the repository root.
2. **Adopt Native Modular Rules**: Create `.agents/rules/` with `always_on` and `glob` triggers for domain-specific engineering rules.
3. **Align Source of Truth Precedence**: Place constitutional invariants and deterministic hook gates strictly above human user directives to eliminate the prompt bypass loophole.
4. **Delegate Safety to Hooks Exclusively**: Never rely on markdown prompts to protect critical assets; enforce all boundary rules in `PreToolUse` hooks.
