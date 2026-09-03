# AntiOS v1 MCP Policy (`ANTIOS_MCP_POLICY.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Audit and establish a disciplined, evidence-based policy for Model Context Protocol (MCP) server usage within AntiOS, classifying candidates into strict operational tiers and eliminating architectural bloat.

---

## 1. Governance Axiom for MCP Integrations

> *"Do not add or call MCP servers simply because they are configured in the platform environment.*  
> *If a native CLI or standard tool executes faster, offline, and with zero token overhead $\to$ PREFER NATIVE TOOLING.*  
> *An MCP server earns a place in the AntiOS workflow only when it provides unique, irreplaceable capabilities that materially improve engineering quality or safety."*

---

## 2. MCP Candidate Classification Matrix

| MCP Server Name | Primary Capabilities | Classification | AntiOS v1 Operational Policy |
| :--- | :--- | :---: | :--- |
| **`chrome-devtools-mcp`** | Deep browser DOM inspection, accessibility trees, console errors, visual snapshots. | **`USEFUL`** | Permitted for StudyLab Svelte frontend layout inspection, webview debugging, and visual regression auditing. |
| **`playwright` / `playwright-mcp-server`** | End-to-end headless browser automation, UI flow testing, click/fill interaction. | **`USEFUL`** | Permitted for automated verification of StudyLab interactive review flows and e2e test execution. |
| **`gemini-api-docs`** | Official upstream Gemini SDK and API documentation search and chunk retrieval. | **`USEFUL`** | Permitted for validating model integration APIs, SDK schemas, and preventing API hallucinations. |
| **`github-mcp-server`** | Remote repository operations: PR creation, remote branch listing, issue tracking. | **`OPTIONAL`** | **STRICT BOUNDARY**: Local repository operations (commit, diff, status, checkout, branch) MUST use local `git` CLI via `run_command`. GitHub MCP is restricted strictly to remote PR workflows if requested by the user. |
| **`docker-mcp`** | Container lifecycle management, isolated environments. | **`OPTIONAL`** | Permitted only for isolated Linux containerized builds or reproduction of environment-specific bugs. |
| **`studysource-core`** | StudySourceCore domain tools (`validate_artifact`, `export_anki_package`). | **`REJECTED`** | **STRICTLY OUT OF SCOPE**. Formally rejected in Phase 8 (`DECISION_REGISTER.md:L60`) and reinforced by User Directive. Zero integration permitted. |
| **`notion-mcp-server`** | Notion page and database manipulation. | **`REDUNDANT`** | **NOT PERMITTED**. AntiOS strictly maintains project state and documentation in version-controlled local markdown files. |
| **`postman-mcp-server`** | REST API testing and collection management. | **`REDUNDANT`** | **NOT PERMITTED**. StudyLab is a native desktop application with SQLite storage, not a distributed HTTP REST microservice. |
| **`posthog`** | Product analytics queries and tracking. | **`REDUNDANT`** | **NOT PERMITTED**. Telemetry and analytics inspection are out of scope for AntiOS engineering governance. |

---

## 3. The Local Git vs GitHub MCP Rule

A critical lesson from Phases 8 and 10:
```text
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ LOCAL GIT CLI (Native run_command)   │ GITHUB MCP SERVER (Remote Transport) │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Speed: < 50ms                      │ • Speed: 500ms - 2000ms              │
│ • Token Cost: 0 tokens (CLI output)  │ • Token Cost: High JSON-RPC payload  │
│ • Offline Capability: 100% Offline   │ • Offline Capability: Requires WAN   │
│ • Target: Local working tree/sandbox │ • Target: Remote GitHub API endpoints│
│ • State: Directly reads disk index   │ • State: Only reads pushed commits   │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ VERDICT: AUTHORITATIVE FOR LOCAL WORK│ VERDICT: REMOTE PR MANAGEMENT ONLY   │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

AntiOS v1 mandates that all local repository inspections (`git status`, `git diff`, `git log`, `git checkout`) execute via local git CLI. Agents must never call GitHub MCP to inspect uncommitted local working trees.

---

## 4. MCP Operational Hygiene Rules

1. **Lazy Loading**: All permitted MCP servers must remain lazily loaded. Tools are queried only when the active task explicitly demands browser automation or documentation lookup.
2. **Payload Restraint**: When querying `gemini-api-docs`, agents must request single chunks without unnecessary context expansion to conserve context window budgets.
3. **Zero Contamination**: Sandboxes and production code must contain zero import statements, wrapper classes, or dependencies tying application logic to MCP servers.

---

## 5. Phase 16–18 MCP Integration Decision

**Decision**: **DEFER** (with partial REJECT for anti-patterns)

### Reasoning

| Criterion | Assessment |
| :--- | :--- |
| **Does AntiOS Core need a custom MCP server?** | **No.** All governance, enforcement, and tool interfaces in Phase 16–18 are fully served by deterministic Python scripts invoked via `run_command`. Zero MCP gap exists. |
| **Would wrapping existing scripts in MCP add value?** | **No.** It would add JSON-RPC overhead, runtime complexity, and a dependency on MCP transport for operations that execute in < 50ms locally. |
| **Is there a future MCP integration surface?** | **Yes — DEFERRED.** The `ToolTier.MCP` tier in `framework/core/tool.py` reserves the extensibility surface. When a genuine need arises (e.g., remote CI integration, cross-repo verification), MCP can be adopted through the existing `ToolSelectionPolicy` without architectural changes. |
| **What is explicitly REJECTED?** | Building a custom MCP server merely to wrap `inspect_repo.py`, `check_changeset.py`, or `check_worktree.py`. Building MCP wrappers for git CLI operations. Adding MCP dependencies to any core module. |

### Formal Policy Statement

> AntiOS Phase 16–18 does NOT build, register, or depend on any new MCP server.
> The `ToolTier` enum reserves `MCP` as a third tier for future needs.
> The `ToolSelectionPolicy.select_tool_tier()` method ensures MCP is only selected
> when both native and script tiers are unavailable.
> This decision can be revisited in a future phase if a concrete, irreplaceable
> MCP capability is identified.
