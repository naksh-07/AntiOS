# Antigravity ↔ AntiOS Ownership Boundaries

**Specification**: `docs/architecture/antigravity/BOUNDARIES.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 2  

---

## 1. The Principle of Platform Sovereignty (`INV-01`)

The foundational constitutional invariant of AntiOS is **Platform Sovereignty**:
> *"If Google Antigravity natively provides an orchestration, execution, scheduling, or logging primitive $\to$ **USE THE PLATFORM**."* (`ANTIOS_CONSTITUTION.md:L40`).

AntiOS must never build proprietary layers that compete with, wrap, or emulate Antigravity capabilities.

---

## 2. Exhaustive Ownership Boundary Matrix

| Capability / Subsystem | Google Antigravity | AntiOS | Target Project |
| :--- | :--- | :--- | :--- |
| **Agent Execution Loop** | **Sole Owner**: Prompt tokenization, LLM sampling, tool dispatching, streaming. | **None**: AntiOS provides zero agent loops or inference wrappers. | Provides developer prompt intent and feedback. |
| **Subagent Management** | **Sole Owner**: `invoke_subagent`, `manage_subagents`, lifecycle tracking, thread termination. | **Policy & Limits**: Defines workforce sizing rules, nesting depth limit ($\le 2$), and launch budgets ($\le 10$). | None. |
| **Tool Transport** | **Sole Owner**: Sandboxed execution of `run_command`, `view_file`, `replace_file_content`, MCP. | **Pre-Tool Interception**: Evaluates write paths for containment and security via `pre_tool_guard.py`. | Provides target scripts, application CLI binaries, and compilers. |
| **Workspace Isolation** | **Sole Owner**: `Workspace='branch'` filesystem isolation and worktree git synchronization. | **Diff & Write Policy**: Mandates Single Writer default and reconciles branch diffs upon task completion. | Source repository git history and commit graph. |
| **Verification & Ratchets**| Executes test processes via `run_command`. | **Sole Owner of Policy**: Evaluates test exit codes, conflict markers, and Maker-Checker audits on `Stop`. | **Sole Owner of Test Logic**: Test cases, assertions, mock fixtures, and domain validation. |
| **Scheduling & Timers** | **Sole Owner**: `schedule` tool (one-shot timers, cron schedules). | **Audit Policy**: Defines when periodic health audits and drift checks should be scheduled. | None. |
| **Context Window** | **Sole Owner**: Context window compaction, truncation, and message delivery. | **Discipline & Memory**: Enforces prompt brevity ($\le 40$ lines) and file-backed memory (`ACTIVE_CONTEXT.md`). | Codebase files inspected into context. |
| **Telemetry & Analytics** | Emits raw session events and `transcript.jsonl`. | **Sole Owner**: Ingests, sanitizes, scrubs credentials, and writes metrics into external `experience.db`. | Application logs and business metrics. |

---

## 3. Boundary Violations: What AntiOS Rejects

To enforce these boundaries, AntiOS has rejected the following patterns (`REJECTED_ARCHITECTURE.md`):
- **Rejected**: Building an Antigravity API client inside AntiOS to poll for subagent status.
- **Rejected**: Implementing a custom tool execution sandbox when `run_command` is available.
- **Rejected**: Creating custom background scheduling threads instead of native `schedule`.
- **Rejected**: Re-implementing git worktree cloning instead of using `Workspace='branch'`.
- **Rejected**: Adding a custom prompt templating engine when native markdown rules suffice.
