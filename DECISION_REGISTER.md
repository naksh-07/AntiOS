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
