# Antigravity Subagent Context & Delegation Architecture
**Document**: `ANTIGRAVITY_SUBAGENT_CONTEXT.md`  
**Status**: Foundational Research Dossier (Research 1)  
**Classification**: Rigorous Evidence-Backed Specification  
**Authority**: Official SDK Specifications, Subagent Runtime Audits & Empirical Experiments  

---

## 1. Executive Summary

Subagents in Google Antigravity provide bounded, task-isolated parallel execution. Invoked via `invoke_subagent`, subagents operate in dedicated cognitive sessions managed independently by the Language Server.

This research establishes the exact boundary of what subagents inherit from their parent agents. The fundamental finding is that **Antigravity enforces strict Zero Context Inheritance**: a subagent inherits configuration, tools, and repository paths, but receives **zero conversation history, zero intermediate tool results, and zero internal thoughts from its parent**.

This architectural property has profound implications for multi-agent engineering: it eliminates context pollution and cognitive bias, making patterns like Maker-Checker independent verification exceptionally effective. However, it also requires parent agents to pass explicit, self-contained task contracts rather than assuming shared conversational memory.

---

## 2. The Zero-Inheritance Context Boundary

When a parent agent executes `invoke_subagent`, the runtime initializes a completely new conversation session with its own SQLite trajectory database (`<subagent-id>.db`).

```text
       PARENT CONVERSATION SESSION                    SUBAGENT SESSION
   ┌─────────────────────────────────┐        ┌─────────────────────────────────┐
   │ Turn 0: User Request            │        │ Turn 0: User Prompt             │
   │ Turn 1: Planning Thoughts       │        │  (= Prompt argument passed to   │
   │ Turn 2: list_dir tool outputs   │        │     invoke_subagent)            │
   │ Turn 3: 40KB of code inspected  │        │                                 │
   │ Turn 4: Bug diagnosed           │        │ [ZERO PARENT HISTORY]           │
   │ Turn 5: invoke_subagent(...)    │───┐    │ [ZERO PARENT THOUGHTS]          │
   └─────────────────────────────────┘   │    │ [ZERO PARENT SCRATCHPAD]        │
                                         ▼    └────────────────┬────────────────┘
                                  Dispatch Contract            │
                                  passed via prompt            ▼
                                                       Subagent executes tools
                                                       independently & emits
                                                       structured HANDOFF REPORT
                                                               │
   ┌─────────────────────────────────┐                         │
   │ Turn 6: Reactive Wakeup         │◄────────────────────────┘
   │ Receives Subagent Message       │
   └─────────────────────────────────┘
```

---

## 3. What Subagents Inherit vs. What They Do Not

### 3.1 What Subagents Inherit
1. `[OFFICIAL]` **Workspace Path Binding (`Workspace='inherit'`)**: Subagents default to executing within the parent's current workspace directory, with access to repository files. If `Workspace='branch'` is passed, a fresh git worktree is created.
2. `[OFFICIAL]` **Tool Declarations (By Subagent Type)**:
   * `TypeName='self'`: Inherits the full parent toolset, including write tools (`replace_file_content`, `write_to_file`) and execution tools (`run_command`).
   * `TypeName='research'`: Inherits only read tools (`view_file`, `list_dir`, `grep_search`, `read_url_content`, `search_web`). Write tools are omitted from its system prompt.
3. `[OFFICIAL]` **Skill Metadata Catalog**: Inherits the Tier 1 `<skills>` catalog (name, description, path) in its system prompt.
4. `[OFFICIAL]` **Directory & Workspace Rules**: Inherits rules discovered by the Language Server for the directory paths the subagent accesses (`AGENTS.md`).
5. `[OFFICIAL]` **Platform Lifecycle Hooks**: Operations performed by subagents trigger `.agents/hooks.json` (`PreToolUse`, `PostToolUse`, `Stop`) identically to the parent.

### 3.2 What Subagents DO NOT Inherit
1. `[OBSERVED]` **Conversation History**: Zero turns of prior chat dialogue are transferred.
2. `[OBSERVED]` **Parent Internal Thoughts**: The subagent never sees `response.thoughts` or intermediate planning chains.
3. `[OBSERVED]` **Intermediate Tool Outputs**: File contents read by the parent, grep outputs, or command logs are not present in the subagent context.
4. `[OBSERVED]` **In-Memory Python State**: No runtime objects from `framework/core/` are accessible in the subagent's execution process.
5. `[OBSERVED]` **Artifact Directory State**: Artifacts authored in `<appDataDir>\brain\<parent-id>\` are not visible to the subagent unless explicit absolute file paths are passed in the prompt.

---

## 4. Communication & Synchronization Protocols

### 4.1 Asynchronous Messaging & Reactive Wakeup
* `[OFFICIAL]` **No Busy Polling**: The platform messaging system automatically manages turn progression. When a parent calls `invoke_subagent`, it does **not** poll `manage_subagents(Action='status')`.
* `[OFFICIAL]` **Event Wakeup**: When a subagent emits output or terminates, the runtime delivers the payload directly into the parent context as a high-priority system message, waking up the parent agent automatically.

### 4.2 Structured Handoff Reports
`[OFFICIAL]` To bridge the zero-inheritance boundary cleanly, subagents must return standardized, high-density structured handoff blocks:

```text
### HANDOFF REPORT
- OBJECTIVE:           [Assigned mandate]
- OBSERVATIONS:        [Key factual findings with file paths and line numbers]
- LOGIC_CHAIN:         [Technical reasoning and causal analysis]
- EVIDENCE:            [Exact command outputs, diffs, or citations]
- CAVEATS:             [Assumptions, risks, edge cases, or unverified items]
- CONCLUSION:          [Actionable recommendation or deliverable]
- VERIFICATION_METHOD: [Exact command/check next owner can run to verify]
- NEXT_OWNER:          [Recommended role: Implementer / Reviewer / Root]
```

---

## 5. Hierarchical Depth & Resource Bounds

### 5.1 The Shallow Depth Law
* `[OFFICIAL]` The Antigravity SDK supports nested subagent hierarchies via `max_subagent_depth` and `allowed_subagents` (`SubagentCapabilities`).
* `[OFFICIAL]` AntiOS and Adaptive Orchestrator enforce the **Shallow Depth Law**:
  $$\text{Maximum Depth} \le 2 \quad (\text{Root} \to \text{Child})$$
  * Exceptional complex enterprise tasks permit depth $\le 3$ ($\text{Root} \to \text{Coordinator} \to \text{Child}$).
  * Unbounded recursive subagent trees are strictly prohibited to prevent token explosion and credit exhaustion.

### 5.2 Hard Resource Ceilings
* `[OFFICIAL]` **Concurrency Ceiling**: Strictly $\le 4$ active concurrent subagents across the entire mission tree.
* `[OFFICIAL]` **Launch Ceiling**: Strictly $\le 10$ total lifetime subagent launches per mission. Terminated or failed subagents consume their launch slot.
* `[OFFICIAL]` **Mandatory Wave Collapse**: Workforces must be collapsed to zero active workers before initiating subsequent execution waves (`WAVE -> CONSOLIDATE -> COLLAPSE -> NEXT WAVE`).

---

## 6. The Maker-Checker Pattern (`antios-verifier`)

The Zero Context Inheritance model is the mathematical foundation of the Maker-Checker verification pattern:

```text
[ MAKER AGENT (Parent or Implementer) ]
├── Implements source changes in working tree
├── Runs preliminary tests
└── Dispatches Independent Checker:
    invoke_subagent(TypeName='self', Role='Independent Verifier')
                         │
                         ▼
[ CHECKER AGENT (Fresh-Context Verifier) ]
├── Completely unbiased by Maker's chain of thought
├── Inspects physical disk reality via `git diff`
├── Runs physical test suite via `run_command`
├── Audits boundary compliance against invariants
└── Emits structured JSON verdict:
    {
      "status": "APPROVED" | "REJECTED",
      "tests_passed": true,
      "clean_diff": true,
      "protected_zones_untouched": true,
      "rationale": "Verified exit code 0 across all test suites."
    }
```

> **Why Maker-Checker Works in Antigravity:**  
> If subagents inherited parent conversation context, the checker would inherit the implementer's biases, rationalizations, and blind spots. Because Antigravity enforces **zero context inheritance**, the verifier is forced to construct its understanding purely from physical disk artifacts (`git diff`, test runner exit codes), providing true independent auditability.

---

## 7. How Subagents Access Project Knowledge

Given zero context inheritance, how can a subagent access project intelligence without dumping the parent history?

1. **Self-Contained Dispatch Contracts**: The parent prompt must provide exact file paths, interfaces, and expected diff constraints.
2. **Deterministic File Pointers**: Pass pointers to on-disk configuration files (`antios.config.json`) or relevant docs (`README.md`, `specs/`).
3. **Progressive Skill Loading**: The subagent independently calls `view_file` on specialized skills (e.g. `antios-verifier`).
4. **Physical Disk Inspection**: The subagent uses `git status` and `git diff` to inspect filesystem truth directly.
