# AntiOS Tool, Provider & MCP Policy (`ANTIOS_MCP_POLICY.md`)

**Date**: 2026-09-04  
**Status**: Canonical Tool, Provider & MCP Policy (Phases 1–42 Consolidated)  
**Objective**: Establish a disciplined, evidence-based policy for tool selection, provider abstractions, and Model Context Protocol (MCP) server usage within AntiOS repositories.

---

## 1. Governance Axiom for Tools & MCP

> *"Do not add or call MCP servers simply because they are configured in the platform environment.*  
> *If a native CLI or standard tool executes faster, offline, and with zero token overhead $	o$ PREFER NATIVE TOOLING.*  
> *An MCP server earns a place in the AntiOS workflow only when it provides unique, irreplaceable capabilities that materially improve engineering quality or safety."*

---

## 2. Six-Tier Tool Preference Hierarchy

AntiOS enforces a strict 6-tier preference ordering across all tool selection decisions:

```text
┌──────────────┬────────────────────────────────────────────────────────────────┐
│ TIER         │ SELECTION PREFERENCE & RATIONALE                               │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 1. NATIVE    │ Platform primitives (run_command, view_file, write_to_file).   │
│              │ Instant execution, zero protocol overhead, platform supported. │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 2. SCRIPT    │ AntiOS deterministic CLI scripts (navigate_repo, audit_docs).  │
│              │ Fast (<100ms), offline, zero token cost, reproducible.         │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 3. PROJECT   │ Project-local build/test tools (pytest, vitest, cargo, go).   │
│              │ Ground-truth application compilers and runners.               │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 4. EXTERNAL  │ Standard system CLI utilities (git, curl, tar, grep).          │
│              │ Operating system utilities executed via run_command.           │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 5. MCP       │ Authorized, lazily-loaded MCP servers with justified need.     │
│              │ Unique capabilities (browser automation, live DOM, SDK docs).  │
├──────────────┼────────────────────────────────────────────────────────────────┤
│ 6. REJECTED  │ Formally prohibited MCP servers and duplicate external tools.   │
│              │ Redundant, ungrounded, or security-violating tools.            │
└──────────────┴────────────────────────────────────────────────────────────────┘
```

---

## 3. MCP Candidate Classification Matrix

| MCP Server Name | Primary Capabilities | Classification | AntiOS Operational Policy |
| :--- | :--- | :---: | :--- |
| **`chrome-devtools-mcp`** | Live browser DOM inspection, a11y trees, console errors, performance auditing. | **`AUTHORIZED`** | Permitted for web frontend layout inspection, webview debugging, and visual regression auditing. |
| **`playwright` / `playwright-mcp-server`** | Headless browser automation, UI flow testing, click/fill interaction. | **`AUTHORIZED`** | Permitted for automated e2e browser automation and UI verification flows. |
| **`gemini-api-docs`** | Official upstream Gemini SDK and API documentation search and chunk retrieval. | **`AUTHORIZED`** | Permitted for validating model integration APIs and SDK schemas. |
| **`github-mcp-server`** | Remote repository operations: PR creation, remote branch listing, issue tracking. | **`RESTRICTED`** | **STRICT BOUNDARY**: Local repository operations (commit, diff, status, checkout, branch) MUST use local `git` CLI via `run_command`. GitHub MCP is restricted strictly to remote PR workflows. |
| **`docker-mcp`** | Container lifecycle management, isolated environments. | **`RESTRICTED`** | Permitted only for isolated containerized builds or reproduction of environment-specific bugs. |
| **`studysource-core`** | Out-of-scope domain tools (`validate_artifact`, `export_anki_package`). | **`REJECTED`** | **100% OUT OF SCOPE**. Formally rejected; zero integration permitted. |
| **`notion-mcp-server`** | Remote page and database manipulation. | **`REJECTED`** | **PROHIBITED**. State is maintained in version-controlled local markdown files. |
| **`postman-mcp-server`** | REST API testing and collection management. | **`REJECTED`** | **PROHIBITED**. Redundant with local test runners and native curl/requests. |
| **`posthog`** | Product analytics queries and tracking. | **`REJECTED`** | **PROHIBITED**. Telemetry queries out of scope for repository engineering governance. |

---

## 4. The Local Git vs GitHub MCP Rule

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

---

## 5. Canonical MCP Justification Authority

All MCP provider evaluations execute through `MCPJustificationEngine` (`framework/core/tool_policy.py`), answering 8 canonical architectural questions:
1. Is there a native or local script alternative available?
2. Does the task require capabilities outside the local filesystem?
3. Is network connectivity required and permitted?
4. Does the MCP provider expose sensitive credentials or tokens?
5. Does the MCP provider alter local filesystem state outside git tracking?
6. Can the operation be verified by an independent local test?
7. Is the provider officially authorized in the capability matrix?
8. Does the execution benefit justify the JSON-RPC latency overhead?
