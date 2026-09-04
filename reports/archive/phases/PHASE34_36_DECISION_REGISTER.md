# AntiOS Phase 34–36 Architecture Decision Register

### 1. Canonical Decisions

| # | Architecture Question | Decision | Rationale |
| :-: | :--- | :--- | :--- |
| **1** | **What defines an Agent Role?** | A canonical, bounded behavioral contract (`AgentRole`) defining role type, core responsibility, scope, task/subsystem applicability, explicit capability boundaries (allowed, forbidden, required, inherited), required verifier, escalation policy, and Shallow Depth Law invariants (`max_depth <= 2`, `can_delegate = False` for specialists). | Standardizes agent identity without assuming arbitrary prompt personas. |
| **2** | **What is stored versus derived?** | **Stored**: Role ID, name, role type, scope, responsibility, boundary patterns, required verifier, escalation policy, enabled status.<br>**Derived**: Task applicability, capability permission evaluation via pattern matching, conflict resolution, handoff contract payloads. | Prevents redundant state storage and avoids synchronization drift. |
| **3** | **How is specialist relevance determined?** | Evaluated against matched subsystem, task class, capability boundary compatibility, and active enablement in the registry. | Replaces naive if/else ladders with a multi-signal deterministic decision matrix. |
| **4** | **When is delegation justified?** | Delegated **only** when domain specialization provides measurable value (bug reproduction, read-only reconnaissance, security review, dedicated UI/database subsystem). Default is strictly `NO_DELEGATION` (SOLO). | Prevents agent sprawl and minimizes context handoff overhead. |
| **5** | **How does specialist authority differ from capability availability?** | A capability being registered in the system does **not** grant an agent authority to use it. Authority is strictly gated by the role's `AgentCapabilityBoundary` (allowed vs forbidden). Authority is never inferred from role name alone. | Enforces principle of least privilege and prevents privilege escalation. |
| **6** | **How does Primary $\leftrightarrow$ Specialist handoff work?** | Via a token-bounded `AgentHandoffContract` containing target files, allowed/forbidden capabilities, constraints, and verification requirements. Specialist returns a structured `SpecialistResultReport` containing work performed, touched files, decisions, evidence, and test results. | Keeps context transfer compact and verifiable without forwarding conversation history. |
| **7** | **How is Checker independence preserved?** | The independent Checker (`role:independent-verifier`) operates in a fresh context, possesses a read-only boundary (`tool:write_to_file` and `tool:replace_file_content` forbidden), cannot delegate (`can_delegate = False`), and executes physical test suites to emit structured JSON verdicts. | Maintains the integrity of the Maker-Checker verification model. |
| **8** | **How does project-local agent configuration override defaults?** | Target projects declare specialists in `antios.config.json` under `agent_topology`. These are validated by `verify_adapter` against core invariants (Shallow Depth Law, protected zones, fail-closed). | Keeps AntiOS Core universal while enabling rich project-specific topologies. |
| **9** | **What constitutes a specialist candidate?** | Discovered recurring subsystem boundaries with dedicated test runners, entrypoints, and distinct file paths. Candidates follow `DISCOVER -> PROPOSE -> VALIDATE -> ENABLE` and are **never** automatically enabled. | Prevents ungrounded agent explosion while surfacing valuable specialization opportunities. |
| **10** | **What remains deferred to Phase 37–39?** | Phase 37–39 Tool/MCP Architecture (advanced MCP lifecycle, tool virtualization, sandboxed execution providers). | Preserves clean modular boundaries and avoids premature runtime complexity. |

---

### 2. Research Reconciliation Matrix

| Concept | Disposition | Detail / Rationale |
| :--- | :---: | :--- |
| **Shallow Depth Law ($\text{depth} \le 2$)** | **KEEP** | Core constitutional invariant; prevents runaway nested execution trees. |
| **Maker-Checker Verification** | **KEEP** | Independent Checker subagent validates working tree diffs and executes physical test suites. |
| **PreToolUse & Stop Gate Hooks** | **KEEP** | Out-of-context deterministic guards enforcing immutable zones and verification ratchets. |
| **Token-Bounded Cards ($\le 25$ lines)** | **KEEP** | Strict context efficiency for agent prompting and tool outputs. |
| **Specialist Capabilities** | **ADAPT** | Evolved from raw capability dictionaries into full `AgentRole` contracts with capability boundaries. |
| **Project Adapter Topology** | **ADAPT** | Extended `antios.config.json` with declarative `agent_topology` validated against core invariants. |
| **Agent Topology Registry** | **BUILD** | Deterministic multi-key index for Primary, Specialist, and Checker roles. |
| **Deterministic Agent Router** | **BUILD** | Signal-based routing engine evaluating specialization value vs delegation cost. |
| **Agent Capability Boundary** | **BUILD** | Explicit allowed, forbidden, required, and inherited capability gating. |
| **Agent Handoff Contract** | **BUILD** | Bounded context transfer schema for Primary $\leftrightarrow$ Specialist interaction. |
| **Specialist Candidate Discovery** | **BUILD** | Safe discovery engine following `DISCOVER -> PROPOSE -> VALIDATE -> ENABLE`. |
| **Dynamic Tool Virtualization** | **DEFER** | Deferred to Phase 37–39 Tool/MCP Architecture. |
| **Sandboxed MCP Providers** | **DEFER** | Deferred to Phase 37–39 Tool/MCP Architecture. |
| **Peer-to-Peer Agent Swarms** | **REJECT** | Unbounded swarms cause coordination failure, race conditions, and context dilution. |
| **Recursive Agent Hierarchies** | **REJECT** | Deep trees violate the Shallow Depth Law and degrade predictability. |
| **Background Agent Daemons** | **REJECT** | AntiOS is an agent-native OS policy, not an agent runtime; Antigravity owns execution. |
