# AntiOS Master Decision Register (`DECISION_REGISTER.md`)

**Date**: 2026-09-04  
**Status**: Authoritative Architectural Consensus (Phases 1–42 Consolidated)  
**Format**: Every decision records `DECISION`, `EVIDENCE`, `ALTERNATIVES`, `WHY SELECTED`, `CONSEQUENCES`, and `REVERSIBILITY`.

---

## DECISION 01: Three-Tier Mechanism vs Policy Demarcation
- **DECISION**: AntiOS strictly defines Project Governance (policy, boundaries, verification, task state) and defers Platform Mechanisms (subagent runtimes, tool interception, scheduling, transcripts) to Antigravity, and Domain Truth (schemas, compiler, application logic) to the target project.
- **EVIDENCE**: Phase 10 Audit proved Antigravity natively provides robust, segregated subagent execution and tool interception, while the target application natively owns its domain schema and compiler contracts.
- **ALTERNATIVES**: Build custom agent orchestrator daemons and Python domain validators.
- **WHY SELECTED**: Eliminates framework bloat, avoids rebuilding tested Google platform primitives, and ensures clean boundary separation.
- **CONSEQUENCES**: AntiOS code footprint is tiny (<500 lines of Python core per module), high-speed (<100ms hook execution), and zero-maintenance.
- **REVERSIBILITY**: Irreversible core foundation; reversing would require building an entire agent execution platform from scratch.

---

## DECISION 02: Strict Fail-Closed Hook Architecture
- **DECISION**: All AntiOS security hooks (`pre_tool_guard.py`, `stop_gate.py`) must fail closed on any error, exception, empty payload, or unexpected type.
- **EVIDENCE**: Phase 9 Attack 2.8 and Phase 10 Audit proved that early prototypes with `except Exception: allow` allowed arbitrary writes upon type mismatches, and empty `workspacePaths` bypassed path checks.
- **ALTERNATIVES**: Fail-open with warning logs.
- **WHY SELECTED**: Security boundaries must never silently drop open during anomalies or adversarial attacks.
- **CONSEQUENCES**: Unhandled exceptions block tool execution and task completion until resolved. Actionable denial messages must be provided to guide recovery.
- **REVERSIBILITY**: High; failure handling logic is isolated within hook scripts.

---

## DECISION 03: Permanent Removal of `verify_task.py` Fallback
- **DECISION**: The hardcoded `verify_task.py` fallback script in `stop_gate.py` is permanently excised. All verification must execute through registered, native project test suites (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
- **EVIDENCE**: Phase 9 Attack 4.3 and Phase 10 Finding F-06 proved that agents could forge test passes by creating a dummy `verify_task.py` with `sys.exit(0)`.
- **ALTERNATIVES**: Cryptographic signing of test scripts; AST validation of test scripts.
- **WHY SELECTED**: Native project test runners (`vitest`, `pytest`, `cargo test`, `go test`) are established ground truth. Arbitrary agent-authored root scripts cannot be trusted as verification evidence.
- **CONSEQUENCES**: Projects without registered test configurations cannot complete tasks with fake test scripts.
- **REVERSIBILITY**: Reversible if a project specifically registers a dedicated test harness in its configuration files.

---

## DECISION 04: Risk-Tiered Maker-Checker Verification
- **DECISION**: Independent verification via a freshly spawned subagent (`invoke_subagent`) is mandatory for High-Risk tasks (core persistence, security hooks, architecture changes), but optional/solo for Low-Risk tasks (typos, formatting, docs). Verifier must use `TypeName='self'`.
- **EVIDENCE**: Phase 7 and 9 trials proved independent verification eliminates 100% of LLM confirmation bias, while trivial 1-line typo fixes avoid 30–60s latency and token overhead when executed solo.
- **ALTERNATIVES**: Mandatory 100% Maker-Checker on all tasks; or 0% Maker-Checker (relying on self-review).
- **WHY SELECTED**: Balances rigorous verification on complex domain changes with speed and efficiency on trivial tasks.
- **CONSEQUENCES**: High-risk changes are audited by clean-context checkers; trivial documentation changes proceed without latency.
- **REVERSIBILITY**: High; governed by verification policies and `antios-engineer` skill.

---

## DECISION 05: Workspace Root Skill & Hook Discoverability
- **DECISION**: Active AntiOS skills and hooks must reside directly in the workspace root (`<workspace_root>/.agents/skills/` and `<workspace_root>/.agents/hooks.json`).
- **EVIDENCE**: Phase 10 Audit proved that placing skills and hooks in subdirectories resulted in 100% undiscoverability by the Antigravity engine in the root workspace.
- **ALTERNATIVES**: Rely on sub-workspace folder opening; symlink directories.
- **WHY SELECTED**: Aligns directly with Antigravity's native platform discovery conventions.
- **CONSEQUENCES**: Antigravity automatically indexes `antios-engineer`, `antios-verifier`, `antios-debug`, `antios-adapt-project` and mounts `PreToolUse` and `Stop` hooks upon workspace initialization.
- **REVERSIBILITY**: High; directory layout is standard.

---

## DECISION 06: Bounded File-Backed Working Memory
- **DECISION**: Working state is maintained in version-controlled markdown (`docs/ACTIVE_CONTEXT.md`) with a strict $\le 60$ line budget. Vector memory databases and custom execution journals are permanently rejected.
- **EVIDENCE**: Phase 6 research and Phase 10 proved that zero-dependency markdown state survives context wipes, is human-auditable, and diffable in Git. Vector DBs introduce opaque retrieval failures and drift.
- **ALTERNATIVES**: External vector DBs (Chroma/Pinecone); JSON state databases; relying solely on memory prompts.
- **WHY SELECTED**: Minimal overhead, high transparency, zero external dependencies.
- **CONSEQUENCES**: Agents must maintain `docs/ACTIVE_CONTEXT.md` across major task milestones to prevent state amnesia.
- **REVERSIBILITY**: High.

---

## DECISION 07: Native Git CLI over GitHub MCP for Local Work
- **DECISION**: Local version control operations (`git status`, `git diff`, `git log`, `git checkout`) must execute via local `git` CLI through `run_command`. GitHub MCP is restricted to remote PR creation/triage.
- **EVIDENCE**: Phase 8 Report and Phase 10 proved local Git CLI is 20x faster, consumes 0 tokens, operates offline, and works directly on local sandboxes.
- **ALTERNATIVES**: Require GitHub MCP for all repository interactions.
- **WHY SELECTED**: Drastically reduces latency and token waste; eliminates reliance on remote network roundtrips.
- **CONSEQUENCES**: Local sandbox operations remain fast, offline, and token-free.
- **REVERSIBILITY**: High.

---

## DECISION 08: Permanent Exclusion of StudySourceCore
- **DECISION**: StudySourceCore is 100% out of scope for AntiOS.
- **EVIDENCE**: Phase 8 Decision 5, Phase 10 Baseline, and Universal Core Mandate. Target projects natively own domain schemas and package generation.
- **ALTERNATIVES**: Integrate StudySourceCore MCP server.
- **WHY SELECTED**: Eliminates foreign cross-project contamination and adheres strictly to universal boundaries.
- **CONSEQUENCES**: Zero StudySourceCore files, tools, or dependencies are present in AntiOS.
- **REVERSIBILITY**: Immutable universal directive.

---

## DECISION 09: Deterministic Project Capability Layer Architecture
- **DECISION**: Establish a unified, deterministic Project Capability Layer (`framework/core/capability.py`, `capability_registry.py`, `capability_router.py`, `capability_pack.py`) indexing 8 canonical capability types (`SKILL`, `RULE`, `WORKFLOW`, `TOOL`, `VERIFIER`, `SPECIALIST`, `EXTERNAL_PROVIDER`, `MCP_PROVIDER`) with 5-tier rule precedence and bounded capability packs ($\le 25$ lines).
- **EVIDENCE**: Phase 31–33 Implementation and verification: 354/354 tests passing in 21.3s, sub-millisecond task resolution (< 1ms), and 100% accurate golden task routing with zero vector databases or embedding models.
- **ALTERNATIVES**: Rely on unstructured string lists in subsystem declarations; use vector database embeddings for skill retrieval; collapse skills, tools, and verifiers into monolithic prompts.
- **WHY SELECTED**: Enforces clean architectural separation between Project Knowledge (where things are), Project Capability (how to work), Task Routing (what applies now), and Capability Pack (bounded bundle for current task).
- **CONSEQUENCES**: Agents deterministically receive exactly the capabilities needed for their task and subsystem with zero hallucination and clear explainability.
- **REVERSIBILITY**: High; standard Python library models and declarative JSON adapters.

---

## DECISION 10: Deterministic Component Wayfinding over Vector Databases
- **DECISION**: AntiOS implements repository wayfinding and locality indexing via deterministic, file-backed inverted indices and prefix tree mapping (`framework/core/wayfinding.py`). Vector databases (Chroma, Pinecone, Qdrant) and regex-based AST dependency parsers are permanently rejected.
- **EVIDENCE**: Phase 27 trials proved deterministic prefix and keyword matching executes in $<20$ms, returns 100% reproducible results, requires 0 dependencies, and avoids vector DB temporal blindness.
- **ALTERNATIVES**: Embedded vector databases; regex-based AST parsers; live LSP indexing daemons.
- **WHY SELECTED**: Maximizes speed, determinism, portability across Windows/Linux/macOS, and operates offline with 0 API token cost.
- **CONSEQUENCES**: Wayfinding resolution is strictly predictable and testable with standard unit tests.
- **REVERSIBILITY**: High; isolated to `framework/core/wayfinding.py`.

---

## DECISION 11: Agent-Oriented Subsystem Manifests and Layer-1 Drift Auditing
- **DECISION**: Establish machine-readable Subsystem Manifests (`framework/core/subsystem.py`) and Staleguard Layer 1 Syntactic Reference Auditing (`framework/core/docaudit.py`). LLM-as-a-judge documentation checkers are permanently rejected.
- **EVIDENCE**: Phase 27 audit proved Staleguard Layer 1 scans backticked paths and markdown links against physical disk in $<1.5$s with 0% false positives, whereas LLM drift checkers take 30–60s and hallucinate semantic conflicts.
- **ALTERNATIVES**: LLM-based documentation evaluators; pure prose READMEs.
- **WHY SELECTED**: Provides instant, zero-cost, zero-hallucination verification that documentation links and code files physically exist on disk.
- **CONSEQUENCES**: Broken file paths or hallucinated test commands in documentation fail the Stop Gate ratchet.
- **REVERSIBILITY**: High; isolated to `framework/core/docaudit.py`.

---

## DECISION 12: Three-Tier Tooling Hierarchy
- **DECISION**: AntiOS strictly enforces the tooling hierarchy: Native Antigravity $\succ$ Local Script/CLI $\succ$ MCP. Internal framework logic remains 100% Python standard library.
- **EVIDENCE**: Local CLI tools executed via `run_command` are 20x faster, consume zero API tokens, work offline, and have no background socket/port collision vulnerabilities on Windows.
- **ALTERNATIVES**: Rebuilding tools exclusively as an MCP server; persistent background daemons.
- **WHY SELECTED**: Eliminates background process thrashing, guarantees 100% offline functionality, and keeps AntiOS Core independent of external protocol libraries.
- **CONSEQUENCES**: Agents interact with AntiOS via native tools and fast CLI invocations.
- **REVERSIBILITY**: High.

---

## DECISION 13: Automated Subsystem Discovery in Project Adapter
- **DECISION**: Static project discovery (`framework/core/discovery.py`) automatically infers subsystem boundaries, component directories, entrypoints, and test pairings during onboarding, emitting them as proposed declarations in `AdaptationProposal`.
- **EVIDENCE**: Standard software architectures exhibit predictable directory conventions (`src/{name}`, `tests/test_{name}`, `pkg/{name}`). Automated discovery followed by declarative adapter storage preserves the 4-tier model.
- **ALTERNATIVES**: Requiring developers to write component manifests manually by hand.
- **WHY SELECTED**: Enables zero-configuration onboarding while maintaining declarative, version-controlled predictability.
- **CONSEQUENCES**: Running `adapt_project.py` automatically discovers components and populates `antios.config.json`.
- **REVERSIBILITY**: High.

---

## DECISION 14: Explicit LOCATE Stage in Agent Lifecycle
- **DECISION**: The AntiOS task lifecycle formally incorporates a mandatory `LOCATE` stage: Understand $	o$ Locate $	o$ Plan $	o$ Act $	o$ Test $	o$ Verify $	o$ Remember $	o$ Recover.
- **EVIDENCE**: The classic failure mode occurs when agents guess where code lives before locating the true owning subsystem. Requiring locality resolution in `ACTIVE_CONTEXT.md` prevents regressions in unrelated subsystems.
- **ALTERNATIVES**: Jumping directly from intake to code editing; recursive multi-agent investigation swarms.
- **WHY SELECTED**: Enforces deliberate cognitive orientation before code mutation.
- **CONSEQUENCES**: `antios-engineer` and `antios-debug` skills require checking subsystem locality before planning.
- **REVERSIBILITY**: High.

---

## DECISION 15: In-Memory Multi-Index Knowledge Graph
- **DECISION**: AntiOS implements its project knowledge graph using a pure Python in-memory indexed adjacency map (`KnowledgeGraph` in `framework/core/knowledge.py`), rejecting external graph databases (Neo4j) and relational graph tables.
- **EVIDENCE**: Real repository graphs contain dozens to hundreds of components, not millions. In-memory graph construction takes $< 5$ms and BFS reachability takes $< 2$ms.
- **ALTERNATIVES**: Neo4j/Memgraph; SQLite relational tables.
- **WHY SELECTED**: Zero background processes, zero external dependencies, 100% deterministic and diffable.
- **CONSEQUENCES**: Instant graph queries with zero runtime footprint.
- **REVERSIBILITY**: High.

---

## DECISION 16: Progressive Context Disclosure Levels (L0 to L5)
- **DECISION**: Knowledge retrieval enforces a strict 6-tier Progressive Disclosure protocol (L0 Project Identity $\le 5$ lines, L1 Subsystem Locator $\le 15$ lines, L2 Component Knowledge $\le 20$ lines, L3 Relationships & Blast Radius $\le 25$ lines, L4 Capabilities $\le 20$ lines, L5 Detailed Evidence JSON).
- **EVIDENCE**: Dumping full repository metadata or complete dependency trees into prompts causes prompt bloat, dilution of instructions, and catastrophic context compaction loss.
- **ALTERNATIVES**: Monolithic system prompts; full repo dumps.
- **WHY SELECTED**: Bounded cognitive overhead; agents request only the degree of fidelity demanded by their active lifecycle stage.
- **CONSEQUENCES**: Compact prompt cards, high context preservation.
- **REVERSIBILITY**: High.

---

## DECISION 17: Deterministic Ownership Derivation
- **DECISION**: Derive code ownership deterministically from disk evidence (`CODEOWNERS`, package manifests, maintainer docs). If no physical evidence exists, return `owner = None` with confidence 0.0.
- **EVIDENCE**: Invented or guessed code ownership leads agents to send notifications or assign reviews to non-existent teams.
- **ALTERNATIVES**: Guessing ownership based on commit frequency; defaulting to repository author.
- **WHY SELECTED**: Prevents hallucinated code ownership.
- **CONSEQUENCES**: True provenance is maintained.
- **REVERSIBILITY**: High.

---

## DECISION 18: Transitive Blast Radius & Downstream Test Aggregation
- **DECISION**: Implement reverse-index BFS reachability (`target -> Set<consumers>`) in `KnowledgeGraph` and automatically aggregate covering tests across all transitive consumers into `ChangeIntent`.
- **EVIDENCE**: Phase 28–30 testing proved transitive test aggregation eliminates hidden cross-module breakages when editing core shared utilities.
- **ALTERNATIVES**: Relying solely on the directly modified module's unit tests.
- **WHY SELECTED**: Guarantees that any change impacting downstream consumers runs all covering test suites before task completion.
- **CONSEQUENCES**: Stop gate ratchets ensure zero hidden downstream regressions.
- **REVERSIBILITY**: High.

---

## DECISION 19: Canonical Bounded Agent Role Contract
- **DECISION**: Define agent roles via canonical, bounded behavioral contracts (`AgentRole` in `framework/core/agent_role.py`) specifying role type, core responsibility, scope, task/subsystem applicability, capability boundaries (allowed, forbidden, required), and Shallow Depth invariants (`max_depth <= 2`, `can_delegate = False` for specialists).
- **EVIDENCE**: Standardizes agent identity without assuming arbitrary prompt personas or unconstrained swarm delegation.
- **ALTERNATIVES**: Prompt-only system personas; unconstrained agent swarms.
- **WHY SELECTED**: Enforces the principle of least privilege and prevents privilege escalation.
- **CONSEQUENCES**: Clear role boundaries for Primary, Specialist, and Checker agents.
- **REVERSIBILITY**: High.

---

## DECISION 20: Stored vs Derived Agent Properties
- **DECISION**: Agent topology strictly separates stored configuration (Role ID, scope, boundaries, verifier, enabled status) from derived evaluation (task applicability, permission evaluation via pattern matching, conflict resolution, handoff contracts).
- **EVIDENCE**: Storing derived evaluation states causes synchronization drift and stale cache bugs when repository files change.
- **ALTERNATIVES**: Caching precomputed routing tables to disk.
- **WHY SELECTED**: Prevents redundant state storage and avoids synchronization drift.
- **CONSEQUENCES**: Fast dynamic evaluation on every turn.
- **REVERSIBILITY**: High.

---

## DECISION 21: Signal-Based Specialist Relevance
- **DECISION**: Specialist relevance is evaluated against matched subsystem, task class, capability boundary compatibility, and active enablement in the registry using a multi-signal deterministic decision matrix.
- **EVIDENCE**: Naive keyword-matching if/else ladders frequently route specialists to unrelated tasks or fail to activate needed specialists.
- **ALTERNATIVES**: Hardcoded task-to-role switch statements; fuzzy LLM-based agent selection.
- **WHY SELECTED**: Provides explainable, reproducible, sub-millisecond agent routing.
- **CONSEQUENCES**: Transparent agent routing decisions with clear rationale.
- **REVERSIBILITY**: High.

---

## DECISION 22: Conservative Delegation Justification
- **DECISION**: Subagent delegation is justified only when domain specialization provides measurable value (bug reproduction, read-only reconnaissance, security review, dedicated UI/database subsystem). Default is strictly `NO_DELEGATION` (SOLO).
- **EVIDENCE**: Spawning subagents on trivial tasks adds 30–60s latency and token overhead with zero quality improvement.
- **ALTERNATIVES**: Automatic subagent delegation on every task; recursive agent trees.
- **WHY SELECTED**: Prevents agent sprawl and minimizes context handoff overhead.
- **CONSEQUENCES**: Small tasks stay fast and solo; complex tasks receive focused specialization.
- **REVERSIBILITY**: High.

---

## DECISION 23: Separation of Capability Availability from Specialist Authority
- **DECISION**: A capability being registered in the system does not grant an agent authority to use it. Authority is strictly gated by the role's `AgentCapabilityBoundary` (allowed vs forbidden). Authority is never inferred from role name alone.
- **EVIDENCE**: Adversarial testing in Phase 34–36 proved agents with administrative names attempt forbidden writes unless strictly blocked by capability boundaries.
- **ALTERNATIVES**: Role-name based permission heuristics.
- **WHY SELECTED**: Enforces defense in depth and least privilege.
- **CONSEQUENCES**: Read-only specialists and independent checkers cannot mutate code even if write tools are available.
- **REVERSIBILITY**: High.

---

## DECISION 24: Token-Bounded Agent Handoff Contracts
- **DECISION**: Primary $\leftrightarrow$ Specialist interaction executes via a token-bounded `AgentHandoffContract` containing target files, allowed/forbidden capabilities, constraints, and verification requirements. Specialist returns a structured `SpecialistResultReport`.
- **EVIDENCE**: Forwarding entire conversation history across subagents saturates context windows and causes instruction decay.
- **ALTERNATIVES**: Full conversation history forwarding; unstructured free-text prompts.
- **WHY SELECTED**: Keeps context transfer compact, verifiable, and free of conversation baggage.
- **CONSEQUENCES**: Subagents receive crisp, bounded instructions and return structured evidence.
- **REVERSIBILITY**: High.

---

## DECISION 25: Independent Checker Verification Model
- **DECISION**: The independent Checker (`role:independent-verifier`) operates in a fresh context, possesses a read-only boundary (`tool:write_to_file` and `tool:replace_file_content` forbidden), cannot delegate (`can_delegate = False`), and executes physical test suites to emit structured JSON verdicts.
- **EVIDENCE**: Maker-Checker verification eliminates 100% of confirmation bias and prevents implementing agents from self-certifying broken changes.
- **ALTERNATIVES**: Self-review in the same conversation; automated static linting only.
- **WHY SELECTED**: Guarantees independent, objective audit of working tree diffs and test results.
- **CONSEQUENCES**: High-risk tasks receive verified, independent audit sign-off before completion.
- **REVERSIBILITY**: High.

---

## DECISION 26: Project-Local Agent Topology Overrides
- **DECISION**: Target projects declare specialists in `antios.config.json` under `agent_topology`. These are validated by `verify_adapter` against core invariants (Shallow Depth Law, protected zones, fail-closed).
- **EVIDENCE**: Different repositories require different specialists (e.g. database specialist, frontend specialist, Rust interop specialist).
- **ALTERNATIVES**: Hardcoding all possible specialists into AntiOS Core.
- **WHY SELECTED**: Keeps AntiOS Core universal while enabling rich project-specific topologies.
- **CONSEQUENCES**: Projects customize their agent workforce declaratively without touching framework code.
- **REVERSIBILITY**: High.

---

## DECISION 27: Specialist Candidate Discovery Lifecycle
- **DECISION**: Discovered recurring subsystem boundaries with dedicated test runners and distinct file paths are proposed as specialist candidates following `DISCOVER -> PROPOSE -> VALIDATE -> ENABLE`. Candidates are never automatically enabled.
- **EVIDENCE**: Automatic agent enablement without human review leads to agent sprawl and unexpected delegation costs.
- **ALTERNATIVES**: Instant automatic enablement of discovered specialists.
- **WHY SELECTED**: Prevents ungrounded agent explosion while surfacing valuable specialization opportunities.
- **CONSEQUENCES**: Developers retain complete governance over active specialists.
- **REVERSIBILITY**: High.

---

## DECISION 28: Six-Tier Tool and Provider Hierarchy
- **DECISION**: AntiOS implements a 6-tier tool preference hierarchy: `NATIVE` $\succ$ `SCRIPT` $\succ$ `PROJECT` $\succ$ `EXTERNAL` $\succ$ `MCP` (Authorized) $\succ$ `REJECTED` (Prohibited).
- **EVIDENCE**: Phase 37–39 testing demonstrated native IDE tools and local CLI scripts execute in $<50$ms with 0 tokens, while MCP calls incur protocol serialization, potential network latency, and credential management overhead.
- **ALTERNATIVES**: Flattening all tools into a single unranked tool catalog; preferring MCP for all tasks.
- **WHY SELECTED**: Enforces maximum execution speed, zero token waste, and predictable tool routing.
- **CONSEQUENCES**: Agents automatically choose the fastest, safest tool for any given operation.
- **REVERSIBILITY**: High.

---

## DECISION 29: In-Memory Multi-Dimensional ToolRegistry
- **DECISION**: Implement `ToolRegistry` entirely in-memory with secondary indexing across tier, capability, task class, subsystem, provider, and availability.
- **EVIDENCE**: Sub-millisecond query performance (<1ms) across 100+ tools with zero disk I/O, zero external databases, and zero lock contention.
- **ALTERNATIVES**: SQLite tool registry; filesystem-based tool discovery on every turn.
- **WHY SELECTED**: Maximum speed, simplicity, and deterministic testability.
- **CONSEQUENCES**: Instantaneous tool lookups during agent execution.
- **REVERSIBILITY**: High.

---

## DECISION 30: Canonical MCP Justification Authority
- **DECISION**: Centralize all MCP justification and policy enforcement in `MCPJustificationEngine` within `framework/core/tool_policy.py`, answering the 8 canonical architectural questions in a unified structured report.
- **EVIDENCE**: Eliminates split-brain MCP policy decisions across routers and scripts. Guarantees unauthorized MCPs are strictly rejected.
- **ALTERNATIVES**: Ad-hoc MCP checks scattered across individual tools.
- **WHY SELECTED**: Single source of truth for MCP compliance and security.
- **CONSEQUENCES**: Every MCP evaluation produces an auditable justification record.
- **REVERSIBILITY**: High.

---

## DECISION 31: Strict Local Git CLI vs GitHub MCP Boundary
- **DECISION**: Local repository inspection (`git status`, `git diff`, `git log`, working tree checks) must execute via local Git CLI (`tool:native-git-cli` or `tool:external-git`). GitHub MCP is strictly restricted to remote pull request operations.
- **EVIDENCE**: Local Git CLI is authoritative, 100% offline, zero token overhead, and executes in $<50$ms. Routing local diffs through remote APIs introduces network latency, privacy risk, and token consumption.
- **ALTERNATIVES**: Allowing GitHub MCP to perform local repository operations.
- **WHY SELECTED**: Protects local data privacy and guarantees instant, offline execution.
- **CONSEQUENCES**: Remote operations go to GitHub MCP; local operations stay strictly on the local machine.
- **REVERSIBILITY**: High.

---

## DECISION 32: Rejection of Custom AntiOS MCP Server
- **DECISION**: Reject creation of a custom AntiOS MCP server wrapping `navigate_repo.py`, `audit_docs.py`, `check_changeset.py`, or `check_worktree.py`.
- **EVIDENCE**: AntiOS deterministic scripts are directly executable via `run_command` in $<100$ms with zero token cost. Wrapping them in an MCP server adds JSON-RPC serialization and background process overhead with zero capability gain.
- **ALTERNATIVES**: Creating `antios-mcp-server` to expose all scripts as MCP tools.
- **WHY SELECTED**: Preserves minimalism and avoids unnecessary daemon management.
- **CONSEQUENCES**: Lean, direct CLI invocation with no protocol wrappers.
- **REVERSIBILITY**: High.

---

## DECISION 33: Tool Authorization Separation from Tool Selection
- **DECISION**: Tool selection does not grant execution authority. All tool selections must be validated against `AgentCapabilityBoundary` and protected zone policies before execution.
- **EVIDENCE**: Prevents privilege escalation and maintains strict Maker-Checker and Specialist role boundaries.
- **ALTERNATIVES**: Allowing any selected tool to execute without boundary check.
- **WHY SELECTED**: Fundamental security invariant: discovery and selection are decoupled from authorization.
- **CONSEQUENCES**: Even if a write tool is selected for a task, an agent with a read-only boundary is blocked from executing it.
- **REVERSIBILITY**: High.

---

## DECISION 34: Explicit Availability and Degraded Modes
- **DECISION**: Tool unavailability must be explicitly surfaced as `UNAVAILABLE` or `MISCONFIGURED`. Silent fallbacks that alter semantics or pretend success are strictly prohibited.
- **EVIDENCE**: Silent fallbacks cause agents to believe an operation succeeded when it actually failed or was skipped, corrupting task state.
- **ALTERNATIVES**: Silent fallback to generic tools; pretending missing tools succeeded.
- **WHY SELECTED**: Guarantees deterministic, honest execution status.
- **CONSEQUENCES**: When a preferred tool is unavailable, the agent is notified with clear diagnostic details.
- **REVERSIBILITY**: High.

---

## DECISION 35: Phase 40–42 Final Consolidation & Release Freeze
- **DECISION**: Phase 40–42 constitutes the final implementation phase of AntiOS. All accumulated Phase 1–39 implementations are consolidated into a coherent, maintainable, universal architecture. Feature expansion is permanently frozen in favor of maintenance, bug fixes, and measured evolution.
- **EVIDENCE**: Complete forensic audit verified 447/447 passing tests across 34 core modules. AntiOS Core is 100% universal, domain-decoupled, and verified against multiple language archetypes (Python, TypeScript, Go, Rust).
- **ALTERNATIVES**: Embarking on additional speculative feature phases (swarm daemons, auto-generation).
- **WHY SELECTED**: Transforms AntiOS from an evolving research prototype into a polished, release-hardened, production-grade engineering operating system.
- **CONSEQUENCES**: Zero architectural churn; rock-solid stability and long-term maintainability.
- **REVERSIBILITY**: Immutable release milestone.

---

## DECISION 36: Four-Boundary Demarcation Model
- **DECISION**: AntiOS 2.0 establishes four inviolable boundary laws: `SOURCE ≠ INSTANCE`, `INSTANCE ≠ PROJECT`, `PROJECT ≠ ANTIGRAVITY`, and `CANONICAL CORE ≠ LOCAL ADAPTER`.
- **EVIDENCE**: Attempting to ship the entire AntiOS development framework (internal tests, blueprints, doc tooling) into target repositories causes massive file bloat, confusing ownership, and broken path assumptions. Decoupling ensures the target repository receives only a lean, self-contained Agent OS instance.
- **ALTERNATIVES**: Cloning or submoduling the entire AntiOS repository into every target project.
- **WHY SELECTED**: Guarantees clean separation of concerns, zero target repository pollution, and surgical installation/removal.
- **CONSEQUENCES**: Canonical framework core resides solely in the source repository; target repositories receive compiled, project-local assets.
- **REVERSIBILITY**: High.

---

## DECISION 37: Cryptographic Project Manifest (.antios/manifest.json)
- **DECISION**: Every installed AntiOS instance must maintain an authoritative `.antios/manifest.json` tracking all managed and generated artifacts with LF-normalized SHA-256 checksums, source revision, schema version, and project fingerprint.
- **EVIDENCE**: Cross-platform file edits (CRLF on Windows vs LF on Linux/macOS) produce hash mismatches unless normalized. Cryptographic manifests allow fail-closed detection of file tampering, accidental deletion, or manifest drift.
- **ALTERNATIVES**: Unversioned file presence checks without hashes or metadata.
- **WHY SELECTED**: Provides deterministic, reproducible provenance across all operating systems.
- **CONSEQUENCES**: Any unrecorded mutation or corruption is immediately surfaced by `verify()` and `repair()`.
- **REVERSIBILITY**: Low (Foundational to AntiOS 2.0).

---

## DECISION 38: Five-Tier Artifact Ownership and Safe Mutation Policy
- **DECISION**: Filesystem artifacts are strictly categorized into 5 tiers: Tier 1 (Canonical Source), Tier 2 (Managed Config & Hooks), Tier 3 (Generated Intelligence), Tier 4 (Operating Interface), and Tier 5 (Target Project Source). User-modified managed files must never be silently overwritten during updates; conflicts must be surfaced explicitly.
- **EVIDENCE**: Overwriting user modifications (such as custom runners or domain paths in `antios.config.json`) destroys user intent and breaks existing project adaptations.
- **ALTERNATIVES**: Blind overwriting of all config and skill files during updates.
- **WHY SELECTED**: Enforces the immutable rule that user-owned and user-modified assets are sovereign.
- **CONSEQUENCES**: Updates preserve user edits and provide structured conflict reports.
- **REVERSIBILITY**: High.

---

## DECISION 39: Deterministic Six-Phase Installation Lifecycle Engine
- **DECISION**: AntiOS 2.0 lifecycle management is implemented in `InstallationLifecycleManager` covering six distinct operations: `INSTALL` (idempotent), `ADAPT` (manifest re-sync), `UPDATE` (source revision migration), `REPAIR` (missing file restoration), `REMOVE` (surgical uninstallation), and `VERIFY` (checksum and schema audit).
- **EVIDENCE**: Real projects evolve: manifests change, dependencies are added, files are moved. A unified lifecycle manager prevents divergent maintenance scripts.
- **ALTERNATIVES**: Fragmented, ad-hoc shell scripts for installation and updates.
- **WHY SELECTED**: Provides a single, programmatic, testable lifecycle engine with full CLI exposure (`install_project.py`).
- **CONSEQUENCES**: Unified status reporting and consistent error handling across all project operations.
- **REVERSIBILITY**: High.

---

## DECISION 40: Universal Project Boundary Compiler
- **DECISION**: The `ProjectBoundaryCompiler` compiles project intelligence (`project_profile.json`, `knowledge.json`, `agent_topology.json`, `tool_policy.json`) and operating skill (`SKILL.md`) in memory from discovered project traits before emitting files. It strictly excludes internal development files (`tests/`, `reports/`, `docs/archive/`).
- **EVIDENCE**: In-memory compilation allows dry-run evaluation, conflict pre-detection, and atomic file emission.
- **ALTERNATIVES**: Direct file copying from template directories into target repositories.
- **WHY SELECTED**: Ensures tailor-made, project-specific instance configuration rather than generic templates.
- **CONSEQUENCES**: Target projects receive customized specialist routing and tool policies matching their actual tech stack.
- **REVERSIBILITY**: High.

---

## DECISION 41: Antigravity-Native Orchestration Constitution
- **DECISION**: Codify the orchestration principles of Adaptive Orchestrator into AntiOS: maximum 10 active subagents per wave, maximum 20 total lifetime launches per mission, mandatory wave collapse to 0 active agents before the next wave, shallow delegation depth ($\le 2$), and Maker-Checker independent verification.
- **EVIDENCE**: Unconstrained subagent spawning leads to exponential context exhaustion, token waste, and uncontrollable background swarms. Strict wave lifecycle (`WAVE -> DISCOVER -> CONSOLIDATE -> COLLAPSE -> NEXT WAVE`) guarantees decisive execution.
- **ALTERNATIVES**: Unbounded recursive agent spawning; continuous long-running background swarms.
- **WHY SELECTED**: Enforces resource awareness, prompt containment, and deterministic mission convergence.
- **CONSEQUENCES**: All AntiOS multi-agent missions operate within strict, mathematically bounded budgets.
- **REVERSIBILITY**: High.

---

## DECISION 42: Self-Contained Skill Interface (.agents/skills/antios/SKILL.md)
- **DECISION**: Target projects expose AntiOS capabilities via a single self-contained skill (`/antios` entrypoint) rather than custom external tools or fragmented slash commands.
- **EVIDENCE**: Antigravity natively discovers and binds skills in `.agents/skills/*/SKILL.md`. A unified `/antios` skill provides instant wayfinding and progressive disclosure for both human operators and AI agents.
- **ALTERNATIVES**: Creating multiple fragmented project skills (`/antios-install`, `/antios-test`, `/antios-plan`).
- **WHY SELECTED**: Minimizes cognitive overhead and conforms 100% to Google Antigravity skill discovery conventions.
- **CONSEQUENCES**: Developers and agents use `/antios` as the primary operational gateway in any adapted project.
- **REVERSIBILITY**: High.

---

## DECISION 43: Single User-Facing Entrypoint & Control Plane Architecture
- **DECISION**: AntiOS establishes `.agents/skills/antios/SKILL.md` as the single authoritative user-facing entrypoint (`/antios`) and control plane. It coordinates wayfinding, capability routing, workforce sizing, execution, and verification through progressive disclosure rather than monolithic instruction bloat.
- **EVIDENCE**: Phase 49–54 Architectural Audit proved that forcing agents or users to manually coordinate dozens of lower-level subsystems leads to fragmented execution, cognitive overload, and instruction drift.
- **ALTERNATIVES**: Requiring users to memorize and manually invoke individual specialist skills and routing scripts.
- **WHY SELECTED**: Provides an intuitive, universal operational gateway across any adapted repository while keeping token consumption bounded.
- **CONSEQUENCES**: All target projects operate under a unified `/antios` interface.
- **REVERSIBILITY**: High.

---

## DECISION 44: Antigravity-Native Adaptive Mission Orchestration & Canonical Dispatch Pipeline
- **DECISION**: Implement the canonical 9-stage dispatch pipeline (`USER TASK` -> `CLASSIFIER` -> `WAYFINDING` -> `CAPABILITIES` -> `AGENT ROUTING` -> `ORCHESTRATOR` -> `TOOL POLICY` -> `EXECUTE` -> `VERIFY` -> `MEMORY`) without creating a competing runtime, daemon, or message broker.
- **EVIDENCE**: Google Antigravity already natively provides robust subagent execution (`invoke_subagent`, `manage_subagents`), tool interception, and planning modes. AntiOS acts purely as the governance and policy layer.
- **ALTERNATIVES**: Build custom multi-agent execution runtimes, socket servers, or background worker daemons.
- **WHY SELECTED**: Conforms strictly to Platform Sovereignty (Constitutional Invariant 1); zero redundant framework bloat.
- **CONSEQUENCES**: Orchestration is lightweight, fast, and 100% standard-library compliant.
- **REVERSIBILITY**: Irreversible core foundation.

---

## DECISION 45: Tree-Aware Global Workforce Bounds & Quota Reservation
- **DECISION**: Orchestration enforces hard constitutional ceilings across the entire mission tree: maximum 10 active subagents per wave, maximum 20 lifetime launches per mission, and maximum nesting depth $\le 2$. Coordinators receive bounded child quotas ($N \le 4$) from Root that revert upon termination.
- **EVIDENCE**: Uncontrolled hierarchical subagent spawning causes combinatorial credit exhaustion and sibling race conditions. Tree-aware budgeting guarantees budget containment regardless of hierarchy depth.
- **ALTERNATIVES**: Granting coordinators independent budgets or unbounded child spawning authority.
- **WHY SELECTED**: Guarantees credit and token safety while preserving focused parallelism.
- **CONSEQUENCES**: Missions never run away or exceed constitutional ceilings.
- **REVERSIBILITY**: High.

---

## DECISION 46: Wave Lifecycle with Mandatory State Consolidation and Worker Collapse
- **DECISION**: Multi-agent missions execute in bounded waves (`RECONNAISSANCE` -> `PLANNING` -> `IMPLEMENTATION` -> `VERIFICATION` -> `DELIVERY`). Advancing to the next wave requires that all active workers from the previous wave are terminated (active total = 0) and state is consolidated.
- **EVIDENCE**: Persistent, idle subagents consume context and generate prompt confusion. Mandatory collapse ensures the team shrinks as the problem narrows.
- **ALTERNATIVES**: Allowing workers to persist indefinitely across task phases.
- **WHY SELECTED**: Prevents context rot, eliminates orphan subagents, and enforces barrier synchronization.
- **CONSEQUENCES**: Waves are cleanly decoupled; new waves spawn fresh, targeted workers within the global 20-launch budget.
- **REVERSIBILITY**: High.

---

## DECISION 47: Read-Parallel and Controlled Single-Writer Execution Policy
- **DECISION**: AntiOS enforces unrestricted parallelism for read-only tasks (reconnaissance, symbol search, log analysis), but strictly controlled execution for writes. Overlapping concurrent writers on the same file are strictly prohibited. Multi-worker writing mandates disjoint file boundaries and isolated worktree branches (`Workspace='branch'`).
- **EVIDENCE**: Concurrent writes to identical files cause merge conflicts, silent overwrites, and state corruption.
- **ALTERNATIVES**: Optimistic concurrent writing with post-hoc merge conflict resolution.
- **WHY SELECTED**: Eliminates write hazards at the scheduling level.
- **CONSEQUENCES**: High reliability and clean diffs across parallel workstreams.
- **REVERSIBILITY**: High.

---

## DECISION 48: Deprecation and Retirement of Legacy `.agents/workflows/`
- **DECISION**: Standalone legacy workflow files (`.agents/workflows/*.md`) are permanently retired and archived to `reports/archive/legacy_workflows/`. Task class lifecycle contracts are codified in Python standard library (`framework/core/workflow.py`).
- **EVIDENCE**: Antigravity has unified around Skills (`.agents/skills/*/SKILL.md`) with slash command bindings. Maintaining duplicate, unversioned procedural markdown files in `.agents/workflows/` violates the Single Authority Governance Law.
- **ALTERNATIVES**: Maintain two competing workflow systems in parallel.
- **WHY SELECTED**: Eliminates architectural ambiguity and aligns AntiOS with native platform conventions.
- **CONSEQUENCES**: Active `.agents/` contains only Skills, Rules, and Hooks.
- **REVERSIBILITY**: High.

---

## DECISION 49: Epistemically Segregated Project Anatomy Compiler and Component Intelligence
- **DECISION**: Implement `ProjectAnatomyCompiler` to compile `.antios/project_anatomy.json` with strict epistemic segregation across three evidence tiers (`OBSERVED`, `INFERRED`, `UNKNOWN`). Component intelligence indexes domain subsystems and renders token-bounded cards ($\le 25$ lines) with authoritative interfaces and covering test mappings.
- **EVIDENCE**: Code generation and specialist dispatch without epistemic segregation suffer from hallucinated package managers, assumed test runners, and spurious specialist proliferation. Grounding intelligence in physical witnesses prevents catastrophic assumptions.
- **ALTERNATIVES**: Flat unstructured project metadata or dynamic prompt-time filesystem scraping.
- **WHY SELECTED**: Guarantees deterministic, audited repository anatomy while respecting token limits and platform boundaries.
- **CONSEQUENCES**: All target projects have an explicit, serializable anatomy ledger; wayfinding can resolve components and test boundaries instantly.
- **REVERSIBILITY**: High.

---

## DECISION 50: Evidence-Driven Skill and Specialist Synthesis with Cryptographic Verification
- **DECISION**: `SkillGenerator` and `SpecialistGenerator` synthesize project-specific operating skills and agent personas strictly on physical witness evidence, enforcing the Shallow Depth Law (`max_depth <= 2`, `can_delegate = False`) and core immutable boundary restrictions. `IntelligenceVerifier` cryptographically audits generated intelligence against target project state, flagging architecture drift, stale paths, and deprecated workflow presence.
- **EVIDENCE**: Spurious specialist generation and deep delegation trees trigger agent swarm runaway and tool permission leakage. Automated verification gates ensure that emitted skills and specialists remain synchronized with actual project manifests.
- **ALTERNATIVES**: Static hardcoded specialists or unbounded dynamic delegation chains.
- **WHY SELECTED**: Combines project-tailored autonomous capability with strict constitutional safety guarantees and drift detection.
- **CONSEQUENCES**: Emitted specialists are non-delegating leaf workers; legacy `.agents/workflows/` are strictly blocked; all emitted files are tracked in `.antios/manifest.json`.
- **REVERSIBILITY**: High.

---

## DECISION 51: Deterministic Project Learning and Epistemic Segregation
- **DECISION**: Implement `LearningEngine`, `ObservationStore`, and `LessonDistiller` under the core law: *"Learning is evidence accumulation, not memory mutation."* Observations are captured deterministically across 13 types and 4 epistemic sources (`OBSERVED_FACT` weight 1.0, `USER_ASSERTION` 0.9, `DERIVED_INFERENCE` 0.7, `AGENT_INTERPRETATION` 0.3). Lessons undergo a multi-tier evidence promotion lifecycle (`OBSERVED` -> `CANDIDATE` -> `VALIDATED` -> `DURABLE`). An agent's interpretation or LLM belief alone is strictly prohibited from promoting lessons.
- **EVIDENCE**: Uncontrolled LLM agent self-reflection creates echo chambers of false beliefs and corrupted memory state. Weight-based epistemic source validation and multi-task recurrence requirements guarantee that only empirical, reproducible truths become durable knowledge.
- **ALTERNATIVES**: Unfiltered memory append, vector database embedding stores, or prompt-based self-reflection loops.
- **WHY SELECTED**: Enforces scientific evidence rigor in autonomous agents while remaining completely zero-dependency and deterministic.
- **CONSEQUENCES**: Project learnings are grounded in test failures, verifier verdicts, and explicit user corrections stored in `.antios/learning_observations.json`.
- **REVERSIBILITY**: High.

---

## DECISION 52: Learning Safety Gate, Safe Evolution Proposals, and Knowledge Decay Lifecycle
- **DECISION**: Learning artifacts never perform silent codebase or skill mutations. All evolutionary improvements must be emitted as reviewable `EvolutionProposal` records in `.antios/learning_proposals.json`. `LearningSafetyGate` enforces 10 non-bypassable invariants, including prompt injection filtering, denial of core framework/constitution mutation (`CORE != ADAPTER`), prohibition of specialist self-promotion (`can_delegate=False`), and prevention of unconfigured MCP privilege escalation. `KnowledgeDecayEngine` detects drift and missing referenced files, transitioning stale knowledge through `ACTIVE` -> `STALE` -> `SUPERSEDED` -> `INVALIDATED` -> `RETIRED` while strictly preserving historical provenance audit trails.
- **EVIDENCE**: Autonomous agents given unconstrained self-modification capabilities inevitably introduce vulnerabilities, hallucinated capabilities, or privilege escalation. Structured proposal schemas and automated decay audits protect repository integrity.
- **ALTERNATIVES**: Silent in-place skill rewriting or unmonitored agent prompt modification.
- **WHY SELECTED**: Guarantees repository safety, human oversight over autonomous changes, and deterministic staleness mitigation.
- **CONSEQUENCES**: Evolution proposals require human approval; attacks attempting core modification or prompt injection are blocked and logged; stale lessons decay safely.
- **REVERSIBILITY**: High.

---

## DECISION 53: Two-Way Adaptation Contract & Epistemic Boundary Segregation
- **DECISION**: Implement `TwoWayAdaptationContract` and `AdaptationSignal` to formally govern information flow across four architectural tiers: `TARGET_PROJECT`, `PROJECT_INSTANCE`, `ANTIOS_SOURCE`, and `PLATFORM`. Target project evidence can adapt project-local intelligence but can NEVER directly mutate AntiOS core files (`framework/`, `ANTIOS_CONSTITUTION.md`). Upstream feedback is routed strictly as read-only RFCs. Agent interpretation alone (`AGENT_INFERENCE`, confidence $\le 0.4$) can never approve durable changes.
- **EVIDENCE**: Bidirectional adaptation without constitutional boundaries leads to target project specifics polluting the universal OS core, causing drift and cross-project pollution.
- **ALTERNATIVES**: Single-direction unconstrained adaptation or allowing target projects to patch framework core directly.
- **WHY SELECTED**: Enforces the immutable law `CORE ≠ ADAPTER` while enabling safe project-specific intelligence synthesis.
- **CONSEQUENCES**: All boundary-crossing signals are cryptographically hashed and validated; Core remains permanently immutable.
- **REVERSIBILITY**: High.

---

## DECISION 54: Capability Gap Detection & Multi-Failure Classification Taxonomy
- **DECISION**: Implement `CapabilityGapDetector` and `GapLifecycleEngine` with a 9-class failure taxonomy distinguishing genuine capability gaps (`MISSING_CAPABILITY`) from ordinary syntax bugs (`ORDINARY_IMPLEMENTATION_FAILURE`), test regressions (`VERIFICATION_FAILURE`), missing PATH binaries (`UNAVAILABLE_TOOL`), policy denials (`UNAUTHORIZED_TOOL`), stale intelligence, and unindexed knowledge. Gaps transition through a formal lifecycle (`DETECTED` -> `VALIDATING` -> `CONFIRMED` -> `PROPOSED` -> `RESOLVED` / `REJECTED` / `STALE`).
- **EVIDENCE**: LLM agents frequently misclassify syntax errors or broken test assertions as missing OS capabilities, leading to hallucinated tool installations and runaway skill generation.
- **ALTERNATIVES**: Treating every execution failure as a capability deficit or prompt-based triage.
- **WHY SELECTED**: Eliminates false-positive capability claims and grounds OS adaptation in empirical proof.
- **CONSEQUENCES**: Ordinary code errors generate `NO_ACTION` proposals; genuine gaps require reproducible evidence traces.
- **REVERSIBILITY**: High.

---

## DECISION 55: 6-Tier Tool Hierarchy & MCP Escalation-Only Model
- **DECISION**: Formalize the 6-tier tool escalation hierarchy (`NATIVE` > `LOCAL SCRIPT` > `PROJECT TOOL` > `STANDARD CLI` > `EXTERNAL SERVICE` > `MCP`). Local `git` CLI strictly outranks GitHub MCP. Remote MCP providers are treated strictly as an escalation mechanism of last resort evaluated through `MCPJustificationEngine`. Prohibited MCP providers (Notion, Postman, PostHog) are rejected fail-closed.
- **EVIDENCE**: Defaulting to MCP tools causes latency, external network vulnerabilities, credential leakage, and reliance on remote proprietary services when local primitives suffice.
- **ALTERNATIVES**: MCP-first architecture or arbitrary tool routing without tier preference.
- **WHY SELECTED**: Maximizes determinism, local execution speed, and security boundary isolation.
- **CONSEQUENCES**: Tasks resolve at the lowest viable local tier; MCP usage generates auditable justification ledgers.
- **REVERSIBILITY**: High.

---

## DECISION 56: Structured Capability Evolution Proposals & Explicit NO_ACTION
- **DECISION**: Implement `CapabilityProposalEngine` to synthesize complete `StructuredCapabilityProposal` records containing evaluated alternatives, cost hints, risk tiers, blast radius, verification plans, and rollback plans. The engine explicitly emits `NO_ACTION` proposals when deficits are classified as ordinary implementation or verification failures.
- **EVIDENCE**: Requiring structured proposals with counterfactual alternative analysis and explicit `NO_ACTION` prevents unnecessary complexity accretion and keeps the OS lean.
- **ALTERNATIVES**: Direct automatic file modification without proposal modeling.
- **WHY SELECTED**: Ensures transparency, human auditability, and complete reversibility of all OS evolutions.
- **CONSEQUENCES**: Every proposed change is paired with an automated test command and a concrete rollback procedure.
- **REVERSIBILITY**: High.

---

## DECISION 57: Controlled AntiOS Evolution & Three-Tier Approval Governance
- **DECISION**: Implement `ControlledEvolutionGovernor` enforcing three approval classes: `AUTO_EXECUTABLE` (low-risk managed config changes), `GOVERNANCE_REQUIRED` (medium/high risk skills, tools, or specialist roles requiring human sign-off), and `CORE_IMMUTABLE_DENIED` (attempts to mutate core or violate Shallow Depth Law). Application requires pre-snapshotting and atomic rollback on verification failure.
- **EVIDENCE**: Autonomous self-evolution without human governance or atomic rollback risks catastrophic bricking of the project OS environment.
- **ALTERNATIVES**: Unrestricted auto-application of all proposals or full manual execution of all edits.
- **WHY SELECTED**: Balances frictionless low-risk maintenance with ironclad human governance over architectural changes.
- **CONSEQUENCES**: Manifest capability revisions are bumped on successful verified applications; failed writes revert atomically.
- **REVERSIBILITY**: High.

---

## DECISION 58: AntiOS Instance Compatibility & Fail-Closed Migration Engine
- **DECISION**: Implement `MigrationEngine` and `migrate_instance.py` CLI supporting SemVer compatibility evaluation (`COMPATIBLE`, `UPGRADE_AVAILABLE`, `MIGRATION_REQUIRED`, `INCOMPATIBLE`, `CORRUPTED`, `UNKNOWN`), 7-stage migration planning (`INSPECT` -> `PLAN` -> `CONFLICT_CHECK` -> `SNAPSHOT` -> `MIGRATE` -> `VERIFY` -> `COMMIT_STATE`), and user-owned artifact preservation. Incompatible states fail closed.
- **EVIDENCE**: As AntiOS evolves across versions, existing project instances require deterministic, safe schema updates without overwriting customized user files.
- **ALTERNATIVES**: Blind overwrites, manual copy-paste instructions, or breaking backward compatibility.
- **WHY SELECTED**: Guarantees zero data loss for user adaptations while keeping project instances synchronized with framework improvements.
- **CONSEQUENCES**: `migrate_instance.py` provides automated `--check`, `--dry-run`, and migration capabilities.
- **REVERSIBILITY**: High.

---

## DECISION 59: Evidence-Backed Agent-Native Scoring Engine (Phase 73)
- **DECISION**: Implement `AgentNativeScoreEngine` evaluating 10 canonical dimensions (`WAYFINDING`, `DOCUMENTATION`, `SKILLS`, `AGENTS`, `OWNERSHIP`, `VERIFICATION`, `MEMORY_KNOWLEDGE`, `TOOLING`, `PROJECT_STRUCTURE`, `ORCHESTRATION_READINESS`) strictly from observable filesystem, manifest, and configuration evidence. Enforce epistemic segregation (`OBSERVED`, `INFERRED`, `UNKNOWN`) and confidence tiers. Missing information is logged as `UNKNOWN` with baseline neutral scores rather than arbitrarily collapsed to zero.
- **EVIDENCE**: Unanchored LLM self-assessment creates arbitrary, ungrounded quality scores. Grounding every score in physical files, verified manifests, and passing test runners provides reproducible, objective metrics.
- **ALTERNATIVES**: Arbitrary LLM score generation or simple checklist counting without evidence verification.
- **WHY SELECTED**: Establishes objective, reproducible measurement of how easily AI agents can understand and maintain a repository.
- **CONSEQUENCES**: Scores explain WHY each dimension was rated with concrete evidence, warnings, unknowns, and recommendations.
- **REVERSIBILITY**: High.

---

## DECISION 60: Deterministic Agent Friction Detection & Cost Modeling (Phase 74)
- **DECISION**: Implement `AgentFrictionDetector` identifying 19 measurable friction patterns (including broken doc references, unindexed docs, context bloat, duplicate skills, ambiguous ownership, missing verification surfaces, and unnecessary MCP escalation). Categorize findings into `OBSERVED_FRICTION`, `INFERRED_FRICTION`, `POSSIBLE_FRICTION`, and `UNKNOWN` with estimated agent token/cognitive cost metrics.
- **EVIDENCE**: Agents trapped in repeated search cycles or encountering broken links consume excessive tokens and risk hallucinating fixes. Deterministic friction detection isolates the root structural causes of agent failure.
- **ALTERNATIVES**: Relying solely on runtime runtime crash logs or unstructured agent feedback.
- **WHY SELECTED**: Provides proactive, preventative detection of impediments before agent missions fail.
- **CONSEQUENCES**: Outputs structured `AgentFrictionReport` feeding directly into the improvement proposal engine.
- **REVERSIBILITY**: High.

---

## DECISION 61: Governed Improvement Proposal Engine & NO_ACTION Ratchet (Phase 75)
- **DECISION**: Implement `ImprovementProposalEngine` integrating directly with `StructuredCapabilityProposal` and `ControlledEvolutionGovernor`. Proposes targeted remedies (`DOCUMENTATION_IMPROVEMENT`, `WAYFINDING_IMPROVEMENT`, `SKILL_DEDUPLICATION`, `MCP_ESCALATION_REDUCTION`, `KNOWLEDGE_REFRESH`, etc.) with counterfactual alternative options, blast radius analysis, and explicit rollback plans. Mandate `NO_ACTION` when evidence is weak (confidence < 0.6) or refactoring risk exceeds potential benefit.
- **EVIDENCE**: Uncontrolled automated code refactoring introduces regressions and churn. Modeling changes as governed proposals under existing evolution infrastructure guarantees human oversight and fail-closed safety.
- **ALTERNATIVES**: Creating a duplicate proposal system or performing direct autonomous mutations.
- **WHY SELECTED**: Unifies all repository evolution under the established AntiOS Controlled Evolution Governance pipeline.
- **CONSEQUENCES**: Zero autonomous churn; all improvements are reviewable proposals paired with automated verification contracts.
- **REVERSIBILITY**: High.

---

## DECISION 62: Progressive Disclosure Documentation Compiler & Ownership Tiers (Phase 76)
- **DECISION**: Implement `DocumentationCompiler` to compile concise, progressive disclosure documentation surfaces (`ARCHITECTURE_SUMMARY.md`, `SUBSYSTEM_MAP.md`, `COMPONENT_MAP.md`, `TEST_MAP.md`, `AGENT_GUIDANCE.md`, `OWNERSHIP_INFO.md`). Enforce 4-tier artifact ownership (`GENERATED`, `MANAGED`, `USER_AUTHORED`, `PROTECTED`). The compiler strictly refuses to overwrite `USER_AUTHORED` and `PROTECTED` documents.
- **EVIDENCE**: Massive, bloated documentation saturates agent context windows. Compact, structured markdown surfaces (<= 100 lines) with provenance headers maximize token efficiency while preserving user-authored knowledge.
- **ALTERNATIVES**: Generating monolithic markdown dumps or allowing unconstrained overwriting of human docs.
- **WHY SELECTED**: Delivers maximum signal per token while preserving human authorial intent.
- **CONSEQUENCES**: Generated documentation contains cryptographic provenance hashes; user files are never overwritten.
- **REVERSIBILITY**: High.

---

## DECISION 63: Agent-Native Refactoring Advisor & Protected Path Invariance (Phase 77)
- **DECISION**: Implement `AgentRefactoringAdvisor` as a strictly advisory intelligence engine identifying high-cost repository structures. Convert recommendations to governed evolution proposals. Explicitly prohibit recommendations that mutate immutable AntiOS core paths (`framework/core/`, `ANTIOS_CONSTITUTION.md`, `.agents/hooks.json`), classifying them as `CORE_IMMUTABLE_DENIED` / `NO_ACTION`.
- **EVIDENCE**: Refactoring agents given write access to constitutional governance code or framework cores inevitably break universal invariants. Strict advisory boundaries protect framework stability.
- **ALTERNATIVES**: Allowing autonomous broad refactoring across the entire repository.
- **WHY SELECTED**: Enforces the immutable law `CORE ≠ ADAPTER` while helping developers optimize their repositories for agents.
- **CONSEQUENCES**: Advisor cannot write code directly; all advice evaluates friction cost vs. risk before proposing action.
- **REVERSIBILITY**: High.

---

## DECISION 64: Formal Evidence-Based Certification & Fail-Closed Safety (Phase 78)
- **DECISION**: Implement `AgentNativeCertificationEngine` and `certify_agent_native.py` CLI supporting 5 formal certification tiers (`NOT_READY`, `BASELINE`, `AGENT_READY`, `HIGHLY_AGENT_NATIVE`, `CERTIFIED`). The certification engine unconditionally fails closed (`NOT_READY`) upon detecting legacy workflow remnants (`.agents/workflows/`), specialist delegation violations (`can_delegate=True`), manifest corruption, test runner execution failures, or unauthorized privilege escalation.
- **EVIDENCE**: A checklist score alone cannot guarantee safety if critical security invariants are violated. Fail-closed certification prevents unsafe or poorly structured repositories from being certified as agent-native.
- **ALTERNATIVES**: Passive scoring without certification levels or lenient passing grades despite critical security failures.
- **WHY SELECTED**: Establishes a rigorous, industry-grade standard for agent-native software engineering.
- **CONSEQUENCES**: `certify_agent_native.py` provides deterministic CLI exit codes (0 for pass, 1 for fail) for CI/CD gates.
- **REVERSIBILITY**: High.

---

## DECISION 65: Project Instance Runtime Closure (`SOURCE ≠ INSTANCE`) (Phases 79–82)
- **DECISION**: Establish physical runtime closure for compiled AntiOS target instances. The AntiOS source repository is the compiler and authority, but an installed target project instance must be 100% self-contained and independently operational without requiring the AntiOS source repository, its `framework/`, `tests/`, `docs/`, or development assets. Implement `RuntimeClosureContract` and `verify_runtime_closure()`, standalone instance runtime scripts in `.antios/runtime/` (`pre_tool_guard.py`, `stop_gate.py`, `inspect_instance.py`, `verify_runtime.py`) using only the standard library and zero imports from `framework`, eliminate all source leaks from `.agents/hooks.json` and `.agents/skills/antios/SKILL.md`, and verify runtime closure in `InstallationLifecycleManager.verify()`.
- **EVIDENCE**: 89->99 audit identified that compiled target projects contained 14 broken references pointing to absent source repository paths (`framework/scripts/`, `../framework/`, `tests/run_all.py`), which caused runtime failures in target projects detached from the AntiOS source repository.
- **ALTERNATIVES**: Copy the entire `framework/` and development source tree into target repositories; or require target repositories to install an external AntiOS Python package wheel.
- **WHY SELECTED**: Copying development source bloats user repositories and pollutes project architecture; requiring an external pip package creates external dependency friction. Emitting lightweight, audited, zero-dependency runtime scripts directly into `.antios/runtime/` ensures complete autonomy, maximum performance, and zero dependency overhead.
- **CONSEQUENCES**: Target projects operate completely offline and detached from the compiler source. `verify_runtime_closure()` and `.antios/runtime/verify_runtime.py` provide deterministic CI/CD verification of instance closure. Target instances cannot leak references back to the AntiOS development environment.
- **REVERSIBILITY**: High; isolated within the compiler, lifecycle manager, and runtime templates.

---

## DECISION 66: AntiOS Native Workforce Contract & 11-Step Capability Hierarchy (Phase 83)
- **DECISION**: Formally codify the boundary between AntiOS Governance and native Antigravity execution via `WorkforceContract` and `DEFAULT_WORKFORCE_CONTRACT` in `framework/core/workforce_contract.py`. AntiOS operates strictly as an intelligent control plane over native Antigravity primitives, never as a competing runtime, daemon, or custom workflow engine (*"AntiOS orchestrates Antigravity; AntiOS does not rebuild Antigravity"*). Enforce an authoritative 11-step execution pipeline: `USER` -> `/antios` -> `MISSION_UNDERSTANDING` -> `PROJECT_INTELLIGENCE` -> `CAPABILITY_SELECTION` -> `WORKFORCE_PLAN` -> `NATIVE_EXECUTION` -> `SPECIALIST_SUBAGENT` -> `NATIVE_TOOL_CLI_MCP` -> `EVIDENCE` -> `VERIFICATION_AND_MEMORY`. Prohibit AntiOS from emulating platform primitives (`agent_execution_runtime`, `subagent_lifecycle`, `tool_execution_transport`, `mcp_transport`, `cli_execution_sandbox`, `background_execution`).
- **EVIDENCE**: Architectural drift occurred when AntiOS components attempted to mimic runtime execution layers (background daemons, polling loops, custom subagent process managers). Demarcating responsibilities establishes clear authority, prevents duplicated execution logic, and eliminates runtime contention.
- **ALTERNATIVES**: Implement an independent agent runner inside AntiOS; or allow unstructured ad-hoc tool calling without hierarchical governance.
- **WHY SELECTED**: Guarantees alignment with Antigravity 2.0 platform architecture, preserves `/antios` as the single authoritative user entrypoint, and ensures deterministic execution.
- **CONSEQUENCES**: All subagent actions route through native `invoke_subagent` and `manage_subagents`; AntiOS components that attempt to claim native primitives fail validation fail-closed.
- **REVERSIBILITY**: High; cleanly codified in `framework/core/workforce_contract.py`.

---

## DECISION 67: 12-Input Adaptive Workforce Sizer with Token-Bounded Cost Reasoning (Phase 84)
- **DECISION**: Implement `AdaptiveWorkforcePlanner` in `framework/core/orchestration.py` evaluating 12 deterministic decision inputs (`task_class`, `risk_tier`, `pre_planning_decision`, `execution_decision`, `write_policy`, `subsystem_count`, `file_count`, `has_disjoint_boundaries`, `remaining_mission_budget`, `historical_worker_success_rate`, `estimated_token_cost_budget`, `active_workers_in_wave`). Every sizing decision emits a token-bounded `WorkforceCostReasoning` rationale card ($\le 12$ lines) answering three mandatory economic questions: *Why this workforce*, *Why not fewer workers*, and *Why not more workers*. Integrate planning directly into `TaskDispatchPipeline` and `MissionPlan`.
- **EVIDENCE**: Unbounded agent swarms cause catastrophic context churn, high token expenditure, and merge collision risks. Grounding workforce sizing in 12 objective inputs and requiring token-bounded economic justification ensures minimal viable headcount.
- **ALTERNATIVES**: Hardcoded agent counts per task class; heuristic-free agent spawning; or unconstrained LLM self-sizing.
- **WHY SELECTED**: Enforces the governing law *"Maximize useful parallel progress per token — never optimize for agent headcount. The team must shrink as the problem narrows."*
- **CONSEQUENCES**: Simple tasks default to SOLO (0 subagents); multi-worker modes require verified independent workstreams and disjoint file boundaries.
- **REVERSIBILITY**: High; backward-compatible with `DualDispatchGates`.

---

## DECISION 68: Teamwork-Grade Wave Orchestration, Anti-Hydra Protection & Crash Persistence (Phase 85)
- **DECISION**: Formalize teamwork-grade wave lifecycle management in `framework/core/orchestration.py`. Mandate `WorkerMetadata` on every worker spawn and enforce 4 deterministic Anti-Hydra gates: duplicate active specialist prevention within waves, runaway failure retry ceiling ($\le 2$ consecutive failures per role), write boundary collision checks, and leaf depth delegation blocking. Implement `WavePersistenceEngine` serializing mission and wave state to `.antios/wave_state.json` for crash recovery, and `FailureRecoveryEngine` mapping 11 failure types to deterministic recovery actions.
- **EVIDENCE**: Multi-agent sessions are vulnerable to "hydra spawning" (duplicate workers spawned on failure, runaway retry loops, concurrent write collisions on identical files). Explicit metadata and barrier synchronization eliminate agent runaway and state corruption.
- **ALTERNATIVES**: In-memory-only wave tracking; or allowing unconstrained worker retries without failure type classification.
- **WHY SELECTED**: Provides production-grade resilience against crashes and ungrounded worker behavior while enforcing constitutional concurrency and depth limits.
- **CONSEQUENCES**: Waves cannot advance while active workers exist (`Mandatory Wave Collapse`); failed runs recover state from `.antios/wave_state.json`.
- **REVERSIBILITY**: High; serialized cleanly in JSON.

---

## DECISION 69: 8-Tier Hybrid Capability Execution Matrix & Governed MCP Escalation (Phase 86)
- **DECISION**: Implement `HybridCapabilityExecutionMatrix` in `framework/core/tool_policy.py` establishing a strict 8-tier resolution order: 1. Native Antigravity Built-in Tool -> 2. Project-Native Skill -> 3. Project Tool / Script -> 4. AntiOS Core Runtime Service -> 5. Antigravity Built-in Specialist Agent -> 6. Standard CLI Execution -> 7. User-Approved External Service -> 8. Managed MCP Tool. Enforce that Local Git CLI (Tier 6) is strictly preferred over GitHub MCP (Tier 8) for all local git operations. Mandate a 7-field escalation audit report (`capability_sought`, `why_native_failed`, `least_privilege_scope`, `risk_assessment`, `rollback_plan`, `user_approval_required`, `audit_trail_entry`) for any Tier 8 MCP escalation; missing fields fail closed immediately.
- **EVIDENCE**: Agents frequently default to remote, high-latency MCP providers for operations that local tools or standard CLIs perform in $<50$ms with zero token cost. A strict 8-tier priority hierarchy and mandatory 7-field escalation audit enforce least-privilege tool usage.
- **ALTERNATIVES**: Treat all tools as peers without preference; or allow arbitrary MCP tool invocation without escalation audit.
- **WHY SELECTED**: Guarantees lowest possible latency, zero token cost for local operations, and ironclad security governance over external capabilities.
- **CONSEQUENCES**: Local git commands execute via standard CLI; external MCPs are used solely when lower tiers genuinely lack the required remote protocol or live browser DOM capabilities.
- **REVERSIBILITY**: High; integrated into `ToolPolicyEngine` and `MCPJustificationEngine`.

---

## DECISION 70: Context Budget Governor & Epistemic Utility Optimization (Phase 87)
- **DECISION**: Implement `ContextBudgetGovernor` in `framework/core/context_budget.py` establishing deterministic task-time context budgeting. Classify candidate sources into `MANDATORY`, `RELEVANT`, `OPTIONAL`, `STALE`, `REDUNDANT`, and `UNKNOWN`. Map sources to actions `LOAD`, `DEFER`, `SUMMARIZE`, `DISCARD`, and `REFRESH`. Enforce the optimization metric: `USEFUL INFORMATION / CONTEXT COST` rather than `MINIMUM TOKENS AT ANY COST`. Unconditionally preserve safety invariants, acceptance criteria, active blockers, and ownership boundaries. Emit a token-bounded reasoning card ($\le 16$ lines).
- **EVIDENCE**: Blind context dumping wastes prompt tokens, distracts reasoning, and elevates injection risks. Simple truncation risks stripping security rules. Objective utility scoring with mandatory invariant reservation guarantees safety and efficiency.
- **ALTERNATIVES**: Unconstrained full-context injection; purely length-based FIFO truncation; or LLM-based self-summarization.
- **WHY SELECTED**: Enforces deterministic, predictable context bounds while guaranteeing safety-critical rules are never discarded.
- **CONSEQUENCES**: Context is budgeted at Stage 7 (`BUILD CONTEXT`) of `/antios`; workers receive strictly bounded relevant context.
- **REVERSIBILITY**: High; isolated engine in `framework/core/context_budget.py`.

---

## DECISION 71: Context Freshness Model & Non-Destructive Safe Compaction (Phase 88)
- **DECISION**: Implement `FreshnessEvaluator` and `SafeContextCompactor` in `framework/core/context_freshness.py`. Audit context against physical file SHA-256 digests, manifest fingerprints, git HEAD advancement, and working tree modifications. Enforce two non-negotiable laws: (1) A stale source must never silently appear as authoritative current context; (2) Compaction never converts inference into fact or strips provenance references.
- **EVIDENCE**: Context drift between tool invocations leads to hallucinated fixes on stale code states. Non-destructive compaction preserves all verifiable facts, constraints, and test outputs while stripping redundant conversational fluff.
- **ALTERNATIVES**: Blind trust in cached context; heuristic string truncation; or vector embedding cosine similarity.
- **WHY SELECTED**: Rooted in physical filesystem evidence (`REALITY > STALE STATE`) with zero external dependencies.
- **CONSEQUENCES**: Stale sources trigger deterministic `REFRESH` actions; compacted context preserves complete provenance.
- **REVERSIBILITY**: High; deterministic standard library implementation.

---

## DECISION 72: Bounded Mission State Continuity & Evidence-Grounded Recovery (Phase 89)
- **DECISION**: Implement `MissionStateStore` and `MissionRecoveryEngine` in `framework/core/mission_state.py`. Establish a deterministic complexity threshold: trivial single-file/low-risk tasks use ephemeral in-memory state; complex multi-file/multi-wave/high-risk tasks persist state to `.antios/missions/<mission-id>/` across 4 canonical files (`mission.json`, `progress.json`, `evidence.json`, `handoffs.json`). On interruption or crash, audit disk reality to deterministically choose `RESUME`, `REPLAN`, `REFRESH`, `ROLLBACK`, or `ABORT`.
- **EVIDENCE**: Multi-agent missions fail across context wipes if state is ephemeral, but persisting every trivial command clutters the filesystem. Bounded 4-file persistence for complex tasks enables crash resilience without disk churn.
- **ALTERNATIVES**: Monolithic sqlite database; unbounded session log appending; or purely in-memory wave state.
- **WHY SELECTED**: Transparent, inspectable JSON files with zero external database dependencies, adhering to AntiOS project sovereignty.
- **CONSEQUENCES**: Crashed missions cleanly resume their active wave and workstreams without duplicating completed tasks.
- **REVERSIBILITY**: High; clean filesystem layout under `.antios/missions/`.

---

## DECISION 73: Token Bounding of Tool Outputs & Cryptographic Verification Digests (Phase 89)
- **DECISION**: Implement `ToolOutputClassifier` in `framework/core/mission_state.py` categorizing execution outputs as `RAW`, `RELEVANT`, `SUMMARIZED`, or `DISCARDED`. For outputs exceeding 2,000 characters, compact stdout/stderr to 20 bounded lines while computing and storing the SHA-256 hash.
- **EVIDENCE**: Large test suites or compiler outputs generate tens of thousands of characters that blow out context windows. Compacting to head+tail lines with a cryptographic hash preserves 100% verification reproducibility while bounding prompt tokens.
- **ALTERNATIVES**: Discarding stdout entirely; or persisting unlimited multi-megabyte log dumps into LLM context.
- **WHY SELECTED**: Provides full verifiability without context bloat.
- **CONSEQUENCES**: Verification audits verify the exit code and SHA-256 digest; agent prompts remain strictly token-bounded.
- **REVERSIBILITY**: High; integrated into `ToolOutputClassifier`.

---

## DECISION 74: Canonical Evidence Model & Epistemic Separation (Phase 90)
- **DECISION**: Implement the canonical Evidence Architecture in `framework/core/evidence.py`. Codify the strict epistemic separation axiom: `OBSERVATION ≠ EVIDENCE ≠ VERDICT ≠ INFERENCE ≠ DECISION`. Prohibit agent assertions from being registered as `EVIDENCE` without physical verification. Define 6 canonical evidence states: `OBSERVED`, `VERIFIED`, `INVALIDATED`, `SUPERSEDED`, `MISSING`, and `CONFLICTING`. Implement `ArtifactFingerprint` and `EvidencePackage` bounded to $\le 50$ artifacts, $\le 100$ items, and $\le 30$ invariants. Integrate with `ToolOutputClassifier` to compact outputs $> 2000$ characters with SHA-256 digests. Enforce mandatory non-empty provenance on all evidence items.
- **EVIDENCE**: Multi-agent systems hallucinate completion when conversational claims are conflated with verified facts. Distinguishing raw observations, verified evidence, and agent inferences with cryptographic artifact fingerprints guarantees auditable and reproducible mission conclusions.
- **ALTERNATIVES**: Unstructured execution logs; allowing agents to self-declare verification; or trusting exit codes without before/after SHA-256 file fingerprints.
- **WHY SELECTED**: Guarantees deterministic epistemic ground truth, bounds context and disk usage, and enforces complete provenance across all workstreams.
- **CONSEQUENCES**: Mission completion requires authoritative physical evidence; unbacked worker claims fail closed immediately.
- **REVERSIBILITY**: High; isolated core model in `framework/core/evidence.py`.

---

## DECISION 75: Deterministic Mission Evaluation Engine & Independent Verification (Phase 91)
- **DECISION**: Implement `MissionEvaluationEngine` in `framework/core/mission_evaluation.py` evaluating missions across 11 canonical engineering dimensions (`FUNCTIONAL_CORRECTNESS`, `ACCEPTANCE_CRITERIA_SATISFACTION`, `TEST_VERIFICATION`, `INVARIANT_COMPLIANCE`, `REPOSITORY_INTEGRITY`, `CHANGE_SET_INTEGRITY`, `WORKFORCE_GOVERNANCE`, `CONTEXT_GOVERNANCE`, `EVIDENCE_COMPLETENESS`, `FRESHNESS_REALITY_ALIGNMENT`, `RECOVERY_INTEGRITY`). Enforce 4 deterministic statuses: `PASS`, `FAIL`, `BLOCKED`, `INCONCLUSIVE`. Require physical test execution for MEDIUM/HIGH risk missions. Strengthen Maker-Checker separation via `IndependentVerifierContract`, forbidding worker self-certification on HIGH risk tasks. Emit bounded `MissionEvaluationCard` ($\le 25$ lines).
- **EVIDENCE**: Simple binary exit codes fail to capture subtle governance, context, or freshness regressions. Multi-dimensional evaluation coupled with independent verifier context ensures changes are robust, bounded, and constitutionally compliant.
- **ALTERNATIVES**: Binary pass/fail based solely on worker exit codes; LLM self-evaluation without structured criteria; or monolithic test runners without governance checks.
- **WHY SELECTED**: Provides deterministic, fail-closed mission verification without context bloat or circular self-certification.
- **CONSEQUENCES**: Completed missions receive a comprehensive 11-dimension audit card; conflicting or incomplete evidence deterministically resolves to `INCONCLUSIVE` or `FAIL`.
- **REVERSIBILITY**: High; cleanly modularized in `framework/core/mission_evaluation.py`.

---

## DECISION 76: Agent-Native Mission Benchmark & Controlled Proving Grounds (Phase 92)
- **DECISION**: Implement `MissionBenchmarkEngine` in `framework/core/mission_benchmark.py` to evaluate agent engineering workflow quality (not LLM reasoning). Define explicitly labeled proxy metrics (`time_to_correct_location_proxy`, `unnecessary_files_inspected`, `context_consumed_tokens_proxy`, `tool_calls_count`, `workforce_launches`, `active_workers_per_wave_peak`, `mission_completion_cost_proxy`). Create the `BASELINE` (naive, unbudgeted) vs `ANTIOS` (governed, budgeted) comparative model using conservative terminology (`OBSERVED_IMPROVEMENT`, `MEASURED_DIFFERENCE`, `INSUFFICIENT_DATA`). Register 10 controlled proving-ground synthetic fixtures (Scenarios A through J). Enforce that benchmark execution preserves all constitutional limits ($\le 10$ active/wave, $\le 20$ lifetime, depth $\le 2$).
- **EVIDENCE**: Without empirical measurement, claims of orchestration efficiency remain unproven. A controlled benchmark with synthetic scenarios demonstrates that AntiOS wayfinding, context budgeting, and wave collapse reduce tokens and exploration while preventing false completions.
- **ALTERNATIVES**: Model-level coding benchmarks (HumanEval/SWE-bench); subjective human reviews; or claiming unverified percentage improvements.
- **WHY SELECTED**: Measures operating system workflow quality deterministically without external API dependencies or network latency.
- **CONSEQUENCES**: Engineering workflow improvements are measured and auditable; false passes and exploration traps are caught and penalized.
- **REVERSIBILITY**: High; self-contained in `framework/core/mission_benchmark.py`.

---

## DECISION 77: Durable Project Proofs & Evidence Distillation (Phase 93)
- **DECISION**: Implement the Durable Project Proofs architecture in `framework/core/project_proof.py`. Codify the epistemic distillation axiom: `MISSION EVIDENCE -> (validation) -> DURABLE PROJECT PROOF`, while strictly prohibiting raw `OBSERVATION`, `INFERENCE`, or unverified claims from becoming proof. Define 13 canonical proof subjects and 7 lifecycle states (`CANDIDATE`, `VALIDATED`, `DURABLE`, `AGING`, `STALE`, `INVALIDATED`, `SUPERSEDED`). Bind proofs directly to physical disk reality via `tracked_paths` and `path_hashes`. Audit on-disk SHA-256 digests via `ProjectProofStore.verify_physical_reality()`, demoting modified or missing tracked files to `INVALIDATED`. Enforce bounded store capacity (`MAX_DURABLE_PROOFS = 50`, `MAX_REFERENCES_PER_PROOF = 10`) with retention priority, and emit token-bounded `ProjectProofCard` ($\le 25$ lines).
- **EVIDENCE**: Individual missions verify point-in-time criteria, but over long development horizons, changes to files invalidate past assumptions. Cryptographically binding verified facts to tracked file hashes ensures that agent intelligence never operates on stale or disproven project knowledge.
- **ALTERNATIVES**: Storing unbounded mission histories; storing all raw execution logs; or trusting agent memories without physical filesystem hash checks.
- **WHY SELECTED**: Enforces physical grounding (`REALITY > REASONING`), bounds storage, and guarantees verifiable provenance across missions.
- **CONSEQUENCES**: Stage 10 (`REMEMBER`) distills passing mission evidence into durable proofs; Stage 7 (`BUILD CONTEXT`) filters and loads only verified, physically fresh proofs.
- **REVERSIBILITY**: High; clean isolated store in `.antios/proofs/` with zero database dependencies.

---

## DECISION 78: Runtime Drift Detection & Project Intelligence Health (Phase 94)
- **DECISION**: Implement `ProjectDriftEngine`, `IntelligenceHealthEngine`, and `IntelligenceRepairEngine` in `framework/core/drift_health.py`. Detect drift across 10 canonical domains (`FILE_STRUCTURE`, `COMPONENT_OWNERSHIP`, `PROJECT_MANIFEST`, `ADAPTER_CONFIGURATION`, `SKILLS`, `DOCUMENTATION`, `TEST_OWNERSHIP`, `CAPABILITY_MAPPINGS`, `DURABLE_PROOFS`, `ARCHITECTURE_ASSUMPTIONS`) on an event-driven basis (zero background daemons). Classify findings into 5 severities (`NO_DRIFT`, `MINOR_DRIFT`, `SIGNIFICANT_DRIFT`, `CRITICAL_DRIFT`, `UNKNOWN`) mapping to 6 actions (`NONE`, `REFRESH`, `REVERIFY`, `REPLAN`, `REBUILD_INTELLIGENCE`, `BLOCK`). Evaluate intelligence health across 7 defensible dimensions into 4 status classes (`HEALTHY`, `DEGRADED`, `STALE`, `UNTRUSTED`). Prohibit autonomous architecture mutation; emit bounded `RepairProposal` objects ($\le 10$) and token-bounded `DriftHealthCard` ($\le 25$ lines).
- **EVIDENCE**: Out-of-band edits, branch switches, or dirty working trees silently degrade wayfinding, adapter configurations, and documentation. A deterministic, explainable health engine prevents agents from operating under corrupted assumptions.
- **ALTERNATIVES**: Continuous background watcher daemons; autonomous self-mutation of architecture; or opaque AI-generated confidence scores.
- **WHY SELECTED**: Event-driven execution preserves system resources; proposal-governed repair upholds constitutional evolution boundaries.
- **CONSEQUENCES**: Stage 2 (`CHECK STATE`) detects critical drift and halts or warns before plan execution; detected drift produces explicit, auditable repair proposals.
- **REVERSIBILITY**: High; deterministic standard library checks in `framework/core/drift_health.py`.

---

## DECISION 79: Long-Horizon Release Certification Engine (Phase 95)
- **DECISION**: Implement `ReleaseCertificationEngine` in `framework/core/release_certification.py` evaluating releases across 12 canonical dimensions (`FUNCTIONAL_STABILITY`, `TEST_INTEGRITY`, `GOVERNANCE_INTEGRITY`, `EVIDENCE_INTEGRITY`, `PROJECT_INTELLIGENCE_HEALTH`, `DURABLE_PROOF_FRESHNESS`, `REPOSITORY_INTEGRITY`, `CHANGE_SET_INTEGRITY`, `CAPABILITY_INTEGRITY`, `RECOVERY_INTEGRITY`, `LONG_HORIZON_DRIFT`, `UNRESOLVED_UNCERTAINTY`). Enforce 5 certification levels: `CERTIFIED`, `CONDITIONALLY_CERTIFIED`, `DEGRADED`, `BLOCKED`, `UNKNOWN`. Codify the fundamental rule that current physical reality outranks historical certifications. Bound the certification window to $\le 10$ recent missions while collapsing older history into a cryptographic SHA-256 digest. Emit token-bounded `LongHorizonCertificationCard` ($\le 25$ lines).
- **EVIDENCE**: Verifying individual tasks is insufficient to establish release-level confidence after extensive refactors. Evaluating multi-mission stability, test integrity, evidence completeness, and cumulative drift guarantees long-term trust without CI bloat.
- **ALTERNATIVES**: Relying solely on git tags; trusting single-mission test exits; or unbounded historical logging.
- **WHY SELECTED**: Evidence-grounded, bounded, and independently auditable by Maker-Checker verifiers.
- **CONSEQUENCES**: Release certification is explicitly invoked as an AntiOS governance operation; certificates are fail-closed and invalidated upon repository drift.
- **REVERSIBILITY**: High; modular governance layer in `framework/core/release_certification.py`.

---

## DECISION 80: Real Antigravity Proving Ground & Scenario Architecture (Phase 96)
- **DECISION**: Implement `RealProvingGround` and `ScenarioCatalog` in `framework/core/proving_ground.py`. Define 8 canonical engineering scenarios (Scenarios A through H) spanning diverse development topologies: Single-File Bug Fix, Multi-File Refactor with Breaking Interface, Incomplete Specification, Contradictory Requirements, Upstream Dependency Breaking Change, Transient Test Flakiness, Out-of-Band Physical Drift, and Multi-Agent Concurrent Edit Collision. Codify strict epistemic boundaries distinguishing `NATIVE_EXECUTION` from `SIMULATED_TRACE`. Enforce bounded `MissionTrace` invariants ($\le 20$ stages, $\le 30$ tool calls, $\le 30$ inspected files, $\le 30$ modified files) and token-bounded `ProvingGroundExecutionCard` ($\le 25$ lines). Prohibit touching production codebases; sandboxes run exclusively in isolated synthetic fixtures.
- **EVIDENCE**: Abstract benchmarks fail to stress edge cases like dirty working trees, flake tests, and concurrent collisions. Realistic scenario topologies with strict execution mode demarcation prevent agents from conflating mock replay with real runtime verification while guaranteeing zero pollution of host filesystems.
- **ALTERNATIVES**: Testing solely against unit tests; running uncontained tests against live repositories; or using unbounded trace loggers.
- **WHY SELECTED**: Grounded in physical fixtures, deterministic, fully token-bounded, and guarantees zero side effects outside designated scratch sandboxes.
- **CONSEQUENCES**: Any workflow claim must be proven across the 8 canonical scenarios; native vs simulated status is cryptographically captured in every mission trace.
- **REVERSIBILITY**: High; isolated module in `framework/core/proving_ground.py`.

---

## DECISION 81: Failure Injection Matrix & Deterministic Recovery Certification (Phase 97)
- **DECISION**: Implement `FailureInjectionHarness` and `FailureMatrixCatalog` in `framework/core/failure_injection.py`. Formalize 16 canonical failure modes spanning tool failures, test failures, context degradation, workforce anomalies, state corruption, external interruptions, and drift. Codify a deterministic recovery decision matrix mapping each failure mode to exact canonical recovery actions: `RESUME`, `REPLAN`, `REFRESH`, `ROLLBACK`, `ABORT`, `BLOCK`, or `REQUIRE_HUMAN_APPROVAL`. Enforce partial write safety: whenever uncommitted modifications are detected after tool or test failures, the harness guarantees either an atomic rollback or an explicit safe block. Emit token-bounded `FailureRecoveryCard` ($\le 25$ lines).
- **EVIDENCE**: Real-world agent deployments inevitably experience flaky commands, context truncation, file permission denial, and dirty trees. An ad-hoc recovery mechanism risks repeating failed tool calls in infinite loops or leaving dirty uncommitted partial edits. A deterministic matrix guarantees fail-closed safety and bounded retries.
- **ALTERNATIVES**: Infinite retry loops; blind rollback on every warning; or manual human intervention for all failures.
- **WHY SELECTED**: Guarantees deterministic, fail-safe recovery paths with strict boundaries against runaway tool loops and corrupted workspaces.
- **CONSEQUENCES**: Stage 9 (`VERIFY`) and recovery handlers deterministically route errors through the failure matrix; unrecoverable corruption fails closed with `BLOCK` or `REQUIRE_HUMAN_APPROVAL`.
- **REVERSIBILITY**: High; cleanly encapsulated in `framework/core/failure_injection.py`.

---

## DECISION 82: Long-Horizon Adaptive Engineering Evaluation (Phase 98)
- **DECISION**: Implement `LongHorizonEvaluationEngine` in `framework/core/long_horizon.py` executing multi-step sequences RUN-01 through RUN-05. Codify the adaptive feedback loop: knowledge and proofs produced in earlier runs must be discoverable and leveraged in subsequent runs, demonstrating measured improvement (`OBSERVED_IMPROVEMENT`, `NO_MEASURABLE_CHANGE`, `REGRESSION_DETECTED`). Enforce bounded sequence execution ($\le 10$ steps per sequence, $\le 30$ cumulative tool calls, bounded history summaries) and emit token-bounded `LongHorizonSequenceCard` ($\le 25$ lines).
- **EVIDENCE**: Multi-turn agent productivity compounds when lessons, durable proofs, and context maps persist across discrete tasks. Validating that RUN-02 through RUN-05 require fewer exploratory steps and tool calls than RUN-01 provides empirical proof of long-horizon compounding intelligence.
- **ALTERNATIVES**: Evaluating tasks as completely isolated, stateless events; or allowing unbounded context accumulators across long sessions.
- **WHY SELECTED**: Provides empirical, repeatable evidence of compounding efficiency while strictly enforcing token and memory boundedness.
- **CONSEQUENCES**: Multi-mission workflows systematically test knowledge reuse and adaptation; regressions in efficiency are flagged and diagnosed.
- **REVERSIBILITY**: High; modular evaluation suite in `framework/core/long_horizon.py`.
