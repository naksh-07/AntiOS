# AntiOS Phase 37–39 Architecture: Tool, Provider & MCP Layer

## 1. Architectural Mandate
AntiOS Phase 37–39 establishes the deterministic execution mechanism selection layer. It evolves AntiOS from:

> **"AntiOS knows which capability is needed and who should use it"** (Phases 31–36)

to:

> **"AntiOS can deterministically select the safest, smallest, and most appropriate execution mechanism for that capability without unnecessary MCPs or agent proliferation."**

Target resolution pipeline:
```
TASK
 ↓
PROJECT KNOWLEDGE (Subsystem & Wayfinding - Phases 28–30)
 ↓
CAPABILITY (CapabilityPack - Phases 31–33)
 ↓
AGENT ROLE (AgentRoutingPack - Phases 34–36)
 ↓
TOOL / PROVIDER SELECTION (ToolRoutingPack - Phases 37–39)
 ↓
EXECUTION (Native runtime / Deterministic script / Project tool)
 ↓
VERIFICATION (Maker-Checker / Independent Auditor / Stop Gate)
```

---

## 2. Core Tool Preference Hierarchy
AntiOS enforces a strict 6-tier preference ordering. Lower-tier mechanisms are selected only when higher-tier mechanisms are demonstrably insufficient:

```text
1. ANTIGRAVITY NATIVE TOOL        (Highest priority; zero token cost, <50ms, direct runtime execution)
2. LOCAL DETERMINISTIC SCRIPT     (Python scripts under framework/scripts/tools/; 100% offline, deterministic)
3. PROJECT-LOCAL TOOL             (Target repo test runners, linters, package build scripts)
4. STANDARD EXTERNAL CLI / SDK    (System binaries installed on PATH e.g. local git, python)
5. EXTERNAL SERVICE               (Network APIs when strictly necessary)
6. MCP PROVIDER                   (Model Context Protocol external servers; lowest priority, selective)
```

---

## 3. Critical Separations of Concerns

| Concept | Definition | AntiOS Core Representation |
| :--- | :--- | :--- |
| **Capability** | What needs to be accomplished | `Capability` (`framework/core/capability.py`) |
| **Tool** | Mechanism that performs the operation | `ToolDefinition` (`framework/core/tool.py`) |
| **Provider** | Source/interface exposing a capability | `ProviderDefinition` (`framework/core/provider.py`) |
| **MCP Provider** | One possible external transport | `ProviderDefinition(provider_type=MCP)` |
| **Skill** | Procedural guidance for using capability | Markdown skill instructions (`.agents/skills/`) |
| **Agent Role** | Persona responsible for the work | `AgentRole` (`framework/core/agent_role.py`) |

---

## 4. Canonical Governance Invariants
1. **Tool Selection Does Not Grant Authority**:
   - A selected tool is merely an execution mechanism.
   - It is executable only within the executing agent's `AgentCapabilityBoundary`, AntiOS Stop Gate ratchets, and protected zone policies.
   - Specialists attempting to execute tools on protected files (`framework/`, `.agents/`, `antios.config.json`) are blocked (`BLOCKED`).
2. **Local Git CLI Authority**:
   - Local Git status, diff, log, branch, and commit operations **strictly use local Git CLI** (`NATIVE` or `EXTERNAL`).
   - GitHub MCP is strictly forbidden for local repository inspection.
3. **No Custom AntiOS MCP Server**:
   - AntiOS deterministic scripts (`navigate_repo.py`, `audit_docs.py`, `check_changeset.py`, `check_worktree.py`) remain local scripts.
   - No custom MCP server is introduced to wrap local utilities.
4. **Canonical MCP Justification Authority**:
   - Single source of truth (`MCPJustificationEngine`) answering the 8 canonical questions.
   - MCP is never selected merely because it is configured in the environment.
