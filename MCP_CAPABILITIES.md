# AntiOS Model Context Protocol (MCP) Capability Policy

This document defines how AntiOS interacts with Model Context Protocol (MCP) servers and external capability providers.

---

## 1. Core Architectural Axiom

> **AntiOS treats MCP as an external CAPABILITY / INTERFACE, NOT Core Architecture.**
>
> AntiOS is a **local-first engineering operating system**. It does not require any external MCP server to operate. All local development, verification, wayfinding, and testing execute using native platform tools and standard library primitives.

---

## 2. Capability Precedence Hierarchy

AntiOS enforces an explicit capability escalation hierarchy:

```
1. Local Git CLI / Standard Tools  (Fastest, zero tokens, offline, deterministic)
               │
               ▼
2. GitHub CLI (gh)                 (Official CLI tool for remote GitHub operations)
               │
               ▼
3. GitHub MCP Server               (Restricted: remote PR/issue management only)
               │
               ▼
4. Other Managed MCP Servers       (Authorized specialized providers only)
```

**Rule**: Use the least powerful capability that safely satisfies the task. Never escalate to MCP for operations that the local Git CLI can perform offline.

---

## 3. Server Classification

| Server Name | Classification | Permitted Scope | Constraints |
| :--- | :--- | :--- | :--- |
| **`local-git`** | `NATIVE_PREFERENCE` | Local status, diffs, branches, tags | Primary choice for all local repository work |
| **`github-mcp-server`** | `RESTRICTED` | Remote PR creation, review, issue tracking | **Strictly forbidden** for local repository operations |
| **`chrome-devtools-mcp`** | `AUTHORIZED` | Live DOM inspection, a11y, performance traces | Web projects only |
| **`playwright`** | `AUTHORIZED` | Headless browser integration testing | Integration test validation |
| **`gemini-api-docs`** | `AUTHORIZED` | Official upstream SDK & API documentation lookup | Read-only |
| **`notion / postman / posthog`** | `PROHIBITED` | None in AntiOS core operations | Not permitted for core engineering workflows |
| **`studysource-core`** | `PROHIBITED` | None | Anti-StudyLab boundary (`INV-19`) |

---

## 4. CLI / MCP Parity Classification

To prevent unnecessary API duplication, AntiOS classifies operations by primary interface:

| Operation | Surface | Implementation |
| :--- | :--- | :--- |
| `antios version` | `CLI-FIRST` | Local CLI command (`framework/cli.py`) |
| `antios status` | `CLI-FIRST` | Local CLI command (`framework/cli.py`) |
| `antios doctor` | `CLI-FIRST` | Local diagnostic engine (`framework/core/doctor.py`) |
| `antios install / update / remove` | `CLI-FIRST` | Local lifecycle manager (`framework/core/installation.py`) |
| `antios verify` | `BOTH` | Local CLI + Stop Gate hook |
| `Issue Creation & Deduplication` | `BOTH` | `antios issue` CLI + `GitHubCapabilityEngine` / `github-mcp-server` |
| `Remote PR Review & Merge` | `MCP-FIRST` | `github-mcp-server` tools (`pull_request_review_write`) |
| `Pre-Tool Guard Interception` | `INTERNAL` | Native Antigravity `PreToolUse` hook |

---

## 5. Escalation Justification Protocol

Before an agent may invoke a `RESTRICTED` MCP tool (such as GitHub MCP for remote PR creation), `framework/core/tool_policy.py` requires a 7-field escalation report:
1. `capability_sought`: Specific remote action needed.
2. `why_native_failed`: Why local Git or native tools cannot perform the action.
3. `least_privilege_scope`: Minimum tool call required.
4. `risk_assessment`: Impact of remote mutation.
5. `rollback_plan`: How to revert if remote operation fails.
6. `user_approval_required`: Whether explicit user consent is mandated.
7. `audit_trail_entry`: Recorded ledger entry in mission state.
