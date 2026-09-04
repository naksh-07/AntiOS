# Capability Gap & Tool Escalation Model (`docs/architecture/CAPABILITY_GAP_MODEL.md`)

## 1. Overview
AntiOS 2.0 establishes a deterministic capability gap triage and tool escalation engine. When task execution encounters friction or failure, the system rigorously distinguishes genuine capability gaps from ordinary code defects, false positives, and missing knowledge.

---

## 2. Multi-Failure Classification Taxonomy
To prevent spurious OS mutations, deficits are categorized into nine distinct classes:

| Classification | Root Cause | System Response |
|---|---|---|
| `ORDINARY_IMPLEMENTATION_FAILURE` | Agent code syntax/runtime bug | Standard debugging; no OS mutation (`NO_ACTION`) |
| `VERIFICATION_FAILURE` | Regression caught by test suite | Code fix in application; ratchet working as intended |
| `UNAVAILABLE_TOOL` | Configured binary missing in host PATH | Environment setup or container runner guidance |
| `UNAUTHORIZED_TOOL` | Invocation blocked by security policy | Policy enforcement; request human approval |
| `STALE_INTELLIGENCE` | `.antios/` out of sync with disk | Trigger intelligence re-adaptation (`inspect_repo.py`) |
| `MISSING_KNOWLEDGE` | Relevant files unindexed | Update wayfinding index and knowledge graph |
| `WRONG_ROUTING` | Task routed to mismatched role | Re-route to compatible specialist or generic engineer |
| `INSUFFICIENT_EVIDENCE` | Unsubstantiated agent assertion | Reject deficit; require reproducible physical witness |
| `MISSING_CAPABILITY` | Genuine lack of skill/tool/verifier | Emit formal capability evolution proposal |

---

## 3. Gap Lifecycle State Machine
Genuine capability gaps transition through formal, auditable states:
$$\text{DETECTED} \longrightarrow \text{VALIDATING} \longrightarrow \text{CONFIRMED} \longrightarrow \text{PROPOSED} \longrightarrow \text{RESOLVED}$$

- **Terminal States**: `RESOLVED` and `REJECTED` are strictly terminal (re-entrancy cycles rejected).
- **Stale State**: Inactive gaps transition to `STALE` if the repository context shifts, but can be re-validated if context re-emerges.
- **Recurrence Tracking**: Duplicate task signatures increment recurrence counts and monotonically increase confidence.

---

## 4. 6-Tier Tool Escalation Hierarchy
AntiOS strictly prefers local and native primitives over remote services or MCP providers:
1. **Tier 1: NATIVE** — Antigravity runtime primitives (`view_file`, `grep_search`, `write_to_file`).
2. **Tier 2: LOCAL SCRIPT** — Deterministic framework tools (`navigate_repo.py`, `audit_docs.py`, `inspect_repo.py`).
3. **Tier 3: PROJECT TOOL** — Project-native binaries discovered in manifest (`pytest`, `vitest`, `cargo`).
4. **Tier 4: STANDARD CLI** — Host environment tools (`git`, `python`, `curl`). Local `git` CLI strictly outranks GitHub MCP.
5. **Tier 5: EXTERNAL SERVICE** — Background local daemons or database services.
6. **Tier 6: MCP PROVIDER** — Model Context Protocol remote tools (Strict escalation only via `MCPJustificationEngine`).

> [!WARNING]
> MCP is never a default tool provider. Prohibited MCP providers (Notion, Postman, PostHog) are rejected fail-closed.
