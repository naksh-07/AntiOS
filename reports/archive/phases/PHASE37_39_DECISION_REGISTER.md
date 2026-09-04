# AntiOS Phase 37–39 Architecture Decision Register (ADR)

## Decision 1: Extension of Existing ToolTier vs Replacement
* **Decision**: Extend `ToolTier` enum in `framework/core/tool.py` to include `PROJECT` and `EXTERNAL`, preserving `NATIVE`, `SCRIPT`, and `MCP`.
* **Rationale**: Maintains 100% backward compatibility with all baseline tests while cleanly accommodating project-local and standard system CLI tools.
* **Status**: ACCEPTED.

## Decision 2: In-Memory Multi-Dimensional ToolRegistry
* **Decision**: Implement `ToolRegistry` entirely in-memory with secondary indexing across tier, capability, task class, subsystem, provider, and availability.
* **Rationale**: Zero external runtime dependencies, zero disk database overhead, and sub-millisecond query performance (<1ms).
* **Status**: ACCEPTED.

## Decision 3: Canonical MCP Justification Authority
* **Decision**: Centralize all MCP justification and policy enforcement in `MCPJustificationEngine` within `framework/core/tool_policy.py`.
* **Rationale**: Eliminates split-brain MCP policy decisions across capability router, agent router, and scripts. Answers the 8 canonical questions in a unified structured report.
* **Status**: ACCEPTED.

## Decision 4: Local Git CLI vs GitHub MCP Boundary
* **Decision**: Strictly mandate that local repository inspection (git status, diff, log, branch, working tree) uses local Git CLI (`tool:native-git-cli` or `tool:external-git`). GitHub MCP is strictly restricted to remote pull request operations.
* **Rationale**: Local Git CLI is authoritative, 100% offline, zero token overhead, and executes in <50ms. Using remote GitHub MCP for local state violates AntiOS speed and locality invariants.
* **Status**: ACCEPTED.

## Decision 5: No Custom AntiOS MCP Server
* **Decision**: Reject creation of an AntiOS MCP server wrapping `navigate_repo.py`, `audit_docs.py`, `check_changeset.py`, or `check_worktree.py`.
* **Rationale**: AntiOS deterministic scripts are directly executable, zero-token, and 100% deterministic. Wrapping them in an MCP server adds unnecessary JSON-RPC and process latency with zero capability gain.
* **Status**: ACCEPTED.

## Decision 6: Tool Authorization Separation
* **Decision**: Tool selection does NOT grant execution authority. All tool selections must be validated against `AgentCapabilityBoundary` and protected zone policies before execution.
* **Rationale**: Prevents privilege escalation and maintains strict Maker-Checker / Specialist role boundaries.
* **Status**: ACCEPTED.

## Decision 7: Explicit Availability and Degraded Modes
* **Decision**: Unavailability must be explicitly surfaced as `UNAVAILABLE` or `MISCONFIGURED`. Silent fallbacks that alter semantics or pretend success are strictly prohibited.
* **Rationale**: Protects against false-positive task completion and silent execution drift.
* **Status**: ACCEPTED.

## Decision 8: Deferral of Phase 40–42
* **Decision**: Defer automated mass skill generation, automatic project self-mutation, and autonomous agent generation to Phase 40–42.
* **Rationale**: Preserves architectural purity of Phase 37–39 as purely Tool, Provider, and MCP selection governance.
* **Status**: ACCEPTED.
