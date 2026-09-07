# Antigravity Persistence Scope: Information Lifetimes & Storage Realities

**Status:** Canonical Platform Research Monograph  
**Research Phase:** AntiOS Research 3 — Project, Workspace, Repository & Scope Reality  
**Author:** Antigravity Pairing Agent  
**Repository:** `naksh-07/AntiOS`  
**Evidence Standard:** `[OFFICIAL]` Upstream Docs/SDK, `[OBSERVED]` Empirical Runtime Experiments (Part 8), `[EXTERNAL_REPORT]` Verified Public GitHub Issues/Forums, `[INFERRED]` Deductive Architectural Analysis, `[HYPOTHESIS]` Proposed Theoretical Models

---

## 1. Executive Summary

A critical engineering failure in AI agent frameworks is data placement mismatch: storing ephemeral data in persistent stores, or relying on ephemeral memory for persistent project facts.

In Antigravity, information is strictly tiered into five persistence classifications:
1. **Ephemeral**: Lives only for a single turn or sub-invocation step; wiped completely from active memory upon turn completion.
2. **Session Persistent**: Bound to a specific conversation lifecycle; persists on disk in SQLite and JSONL logs, but resets when a new conversation begins.
3. **Project Persistent**: Bound to an Antigravity Project container; survives across conversations, IDE restarts, and reboots.
4. **Repository Persistent**: Version-controlled in Git; tracked across commits and branches.
5. **User / Global Persistent**: Machine-wide configuration; applies to all projects for the host user.

This monograph documents the exact persistence boundaries across nine operational transitions and specifies where AntiOS state must reside.

---

## 2. The Nine Operational Persistence Transitions

To understand information lifetimes, we analyze what survives across nine distinct execution boundaries:
1. **Turn**: A single prompt/response cycle within an ongoing agent invocation.
2. **Invocation**: The complete sequence of tool calls and inferences fulfilling a single user prompt.
3. **Conversation**: Multi-turn dialogue thread between user and agent.
4. **Fresh Conversation**: Launching a new conversation thread within the same project.
5. **Fresh Agent**: Restarting the Language Server agent process.
6. **Subagent**: Launching a child worker process via `invoke_subagent`.
7. **Worktree**: Switching between isolated Git worktrees.
8. **Project Restart**: Closing and reopening an Antigravity Project.
9. **Machine Restart**: Full operating system reboot.

---

## 3. The Comprehensive Persistence Matrix

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CANONICAL PERSISTENCE LIFETIME MATRIX                                      │
├───────────────────────┬────────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────────────┤
│ Information Entity    │ Class      │ 1.   │ 2.   │ 3.   │ 4.   │ 5.   │ 6.   │ 7.   │ 8.   │ 9.   │ Physical On-Disk│
│                       │            │ Turn │ Invoc│ Conv │ F.C. │ F.Ag │ Sub  │ WkTr │ P.Rs │ M.Rs │ Storage Location│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ In-Memory Tokens      │ Ephemeral  │ YES  │ YES  │ YES  │ NO   │ NO   │ NO   │ NO   │ NO   │ NO   │ RAM Only        │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Ephemeral Injections  │ Ephemeral  │ NO   │ NO   │ NO   │ NO   │ NO   │ NO   │ NO   │ NO   │ NO   │ None (PreInvoc) │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Step Logs (JSONL)     │ Session    │ YES  │ YES  │ YES  │ DORM │ DORM │ NO   │ YES  │ DORM │ DORM │ brain/<id>/tr.  │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Conversation SQLite   │ Session    │ YES  │ YES  │ YES  │ DORM │ DORM │ NO   │ YES  │ DORM │ DORM │ conv/<id>.db    │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Brain Artifacts       │ Session    │ YES  │ YES  │ YES  │ DORM │ DORM │ NO   │ YES  │ DORM │ DORM │ brain/<id>/*.md │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Project Settings      │ Project    │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ config/proj/<id>│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Permission Grants     │ Project    │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ config/proj/<id>│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Project Mapping       │ User/Global│ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ ~/.gem/proj.json│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Global Settings/MCP   │ User/Global│ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ config/conf.json│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Tracked Files (Git)   │ Repository │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ .git/objects/   │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Rules / AGENTS.md     │ Repository │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ <repo>/AGENTS.md│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Hooks / hooks.json    │ Repository │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ .agents/hooks.js│
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Untracked Files       │ Worktree   │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ NO   │ YES  │ YES  │ Working Tree    │
│ (.venv, node_modules) │ Local      │      │      │      │      │      │      │ (Gap)│      │      │                 │
├───────────────────────┼────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────┤
│ Central Experience DB │ User/Global│ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ YES  │ experience.db   │
└───────────────────────┴────────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────────────┘
```
*Legend: YES = Active & Available; NO = Destroyed / Reset; DORM = Persists on disk but dormant unless resumed.*

---

## 4. Physical Storage Architecture on Disk

Antigravity segregates storage across three distinct local filesystem zones `[OBSERVED]`:

```
1. USER GLOBAL APP DATA (~/.gemini/)
   ├── projects.json                      <-- Mappings: local paths -> project IDs
   ├── config/
   │   ├── config.json                    <-- Global user settings, plugins, global grants
   │   └── projects/
   │       ├── 70a4eea3-...json           <-- Project settings, resources, permissions
   │       └── outside-of-project.json
   └── antigravity/
       ├── conversations/
       │   └── <conv-id>.db               <-- SQLite database of conversation turns
       └── brain/
           └── <conv-id>/
               ├── .system_generated/
               │   ├── logs/transcript.jsonl <-- Complete turn/tool stream
               │   └── tasks/task-*.log      <-- Async task outputs
               ├── implementation_plan.md    <-- Planning artifacts
               ├── walkthrough.md
               └── scratch/                  <-- Ephemeral script workspace

2. WORKING TREE / REPOSITORY (<workspace_root>/)
   ├── .git/                              <-- Canonical object store & refs
   ├── .agents/
   │   ├── rules/                         <-- Tracked modular rules
   │   ├── skills/                        <-- Tracked skills
   │   └── hooks.json                     <-- Tracked hook policies
   ├── docs/                              <-- Epistemic project state (System A)
   └── (Application source code)

3. EXTERNAL DATA DIRECTORY (<ANTIOS_DATA_DIR>/)
   └── experience.db                      <-- Cross-project SQLite WAL telemetry (System B)
```

---

## 5. Epistemic Architecture for AntiOS 3.0

The persistence realities confirm the AntiOS Bi-Cameral Memory Architecture (`ANTIOS_ARCHITECTURE.md`):

1. **System A (Project Epistemic Memory)**:
   - Must be strictly **Repository Persistent** (committed to Git).
   - Stored in bounded markdown/JSON files: `docs/ACTIVE_CONTEXT.md` ($\le 60$ lines), `docs/LESSONS.md` ($\le 50$ entries), and `.antios/manifest.json`.
   - Survives fresh conversations, fresh agents, and team-wide Git cloning.
2. **System B (Cross-Project Experience Intelligence)**:
   - Must be strictly **User / Global Persistent** (external to the repository).
   - Stored in `experience.db` (SQLite WAL mode).
   - Survives repository deletions and project switches; accumulates telemetry across all projects on the machine.
3. **Never Pollute the Working Tree with Ephemeral State**:
   - Coordination files, dead-end logs, and temporary scripts must reside strictly in `brain/<conv-id>/scratch/`, never in the user's codebase.
