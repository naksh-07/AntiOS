# Antigravity Subagent Scope: Zero Context Inheritance & Epistemic Boundaries

**Status:** Canonical Platform Research Monograph  
**Research Phase:** AntiOS Research 3 — Project, Workspace, Repository & Scope Reality  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Subagent Lifecycle Logging, `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Summary

A pervasive misconception in autonomous agent architecture is that subagents inherit the working memory, thought history, and conversational turns of their parent orchestrator. 

In Google Antigravity, the exact opposite is true `[OFFICIAL]`:
> **Antigravity subagents operate under a strict Law of Zero Context Inheritance.**

When a parent agent dispatches a subagent via `invoke_subagent`, the platform launches an entirely distinct, headless conversation session with a pristine token window. The subagent has **zero visibility** into parent turns, parent tool invocations, or parent thoughts.

This monograph documents the architectural relationship between Project, Parent Agent, Subagent, and Worktree, answers the fundamental question regarding minimal subagent context, and establishes why Zero Context Inheritance is the bedrock of objective verification in AntiOS.

---

## 2. The Structural Relationship: Project $\to$ Parent $\to$ Subagent $\to$ Worktree

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ANTIGRAVITY PROJECT CONTAINER                     │
│  Owns: Global Identity, Settings, Permission Grants, Project Resources  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        PRIMARY (PARENT) AGENT                          │
│  Owns: User Interaction, Multi-turn History, Lazy MCP Tools, Planning  │
│  Storage: SQLite DB (<conv-1>.db) & brain/<conv-1>/transcript.jsonl    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ invoke_subagent(Role, Prompt, Workspace)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          SUBAGENT (WORKER)                             │
│  Owns: Headless execution of assigned Prompt, Zero Parent Memory       │
│  Storage: Isolated SQLite (<conv-2>.db) & brain/<conv-2>/              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Workspace Mode Selection
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│      Workspace = 'inherit'      │         │       Workspace = 'branch'       │
│  Shares parent working tree     │         │  Provisions isolated Git worktree│
│  Ideal for: Audits, Verifiers   │         │  Ideal for: Parallel Writers     │
└─────────────────────────────────┘         └──────────────────────────────────┘
```

---

## 3. Subagent Visibility Audit Across Environment Entities

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            SUBAGENT VISIBILITY AUDIT                                   │
├──────────────────────────┬───────────┬─────────────────────────────────────────────────┤
│ Environment Entity       │ Visible?  │ Architectural Mechanism                         │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Active Workspace FS      │ YES       │ Mounted into subagent working directory         │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Root AGENTS.md           │ YES       │ Injected at Turn 0 as constitutional grounding  │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ .agents/rules/*.md       │ YES       │ Evaluated dynamically based on trigger patterns │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ .agents/skills/          │ YES       │ Frontmatter registered in <skills> tool prompt  │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ .agents/hooks.json       │ YES       │ Workspace hooks intercept subagent tool calls   │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Git Repository           │ YES       │ Full access to git CLI in assigned worktree     │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Parent Turns / History   │ NO (0%)   │ ZERO CONTEXT INHERITANCE: Pristine token window │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Parent Internal Thoughts │ NO (0%)   │ Hidden from child conversation completely       │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Parent Brain Artifacts   │ NO (0%)   │ Subagent writes to its own brain/<child-id>/    │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Lazy MCP Tools           │ NO (0%)   │ Broken in subagents via Issue #569              │
├──────────────────────────┼───────────┼─────────────────────────────────────────────────┤
│ Sibling Repositories     │ PARTIAL   │ Reachable via relative paths, but ungrounded   │
└──────────────────────────┴───────────┴─────────────────────────────────────────────────┘
```

---

## 4. The Fundamental Question Answered

> **"What is the smallest context a subagent receives from the project environment by default?"**

Under official Antigravity platform specifications `[OFFICIAL]`, the minimal default context of a subagent at Turn 0 consists strictly of:

1. **The System Prompt Scaffold**: Standard Antigravity agent role instructions and behavioral constraints (~1,500 tokens).
2. **The Active Workspace Declaration**: The `[URI] -> [CorpusName]` header defining mounted roots.
3. **The Root Constitutional Document**: `AGENTS.md` discovered at the repository root.
4. **The Eager Native Tool Definitions**: Tool schemas for `run_command`, `view_file`, `write_to_file`, `replace_file_content`, `grep_search`, `find_by_name`, `list_dir`.
5. **The Skills Index**: Name and description headers of declared skills (~50 tokens each).
6. **The Explicit Subagent Prompt**: The literal string passed via `invoke_subagent(Prompt="...")`.

**Everything else is absent.** If the parent agent discovered crucial context during its reasoning turns, that context is **completely lost to the subagent** unless the parent explicitly serializes it into the `Prompt` argument or writes it to an on-disk project document (`docs/ACTIVE_CONTEXT.md`).

---

## 5. Known Platform Edge Cases & Tool Deficits

### 5.1 The Subagent Lazy MCP Deficit (GitHub Issue #569)
`[EXTERNAL_REPORT]` `[OBSERVED]`
- In the primary agent, lazily-loaded Model Context Protocol (MCP) tools are dispatched via a native runtime wrapper tool named `call_mcp_tool`.
- When a subagent is spawned, the Antigravity subagent initialization routine registers eager native tools, but **fails to bind the `call_mcp_tool` wrapper into the subagent's tool registry**.
- **Consequence**: Subagents cannot dispatch tools from lazy MCP servers (such as `chrome-devtools-mcp`, `github-mcp-server`, `notion-mcp-server`, or `playwright`). Any subagent attempt to invoke lazy MCP tools fails.
- **Rule for AntiOS**: All deep MCP interactions must be executed directly by the Primary Agent or wrapped in CLI scripts executable via `run_command`.

---

## 6. Why Zero Context Inheritance is an Architectural Superpower

While naive agent frameworks view context inheritance as desirable, in safety-critical systems it is an anti-pattern. Context inheritance causes **Confirmation Bias Cascades**:
- If a Maker agent adopts a flawed hypothesis, every child subagent inheriting that context adopts the same rationalizations and fails to identify the bug.

Antigravity's Zero Context Inheritance guarantees that when AntiOS dispatches `antios-verifier` as an independent Checker:
1. The Checker begins with a **100% pristine token window**.
2. The Checker cannot read the Maker's chain-of-thought or cognitive excuses.
3. The Checker is forced to audit the physical working tree diff and run automated test suites against cold reality.
4. The resulting verdict (`VERIFIED` vs `REJECTED`) is mathematically objective.
