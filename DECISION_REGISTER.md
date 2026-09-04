# AntiOS Master Decision Register (`DECISION_REGISTER.md`)

**Date**: 2026-09-04  
**Status**: Authoritative Architectural Consensus  
**Format**: Every decision records `DECISION`, `EVIDENCE`, `ALTERNATIVES`, `WHY SELECTED`, `CONSEQUENCES`, and `REVERSIBILITY`.

---

## DECISION 01: Three-Tier Mechanism vs Policy Demarcation
- **DECISION**: AntiOS v1 strictly defines Project Governance (policy, boundaries, verification, task state) and defers Platform Mechanisms (subagent runtimes, tool interception, scheduling, transcripts) to Antigravity, and Domain Truth (schemas, compiler, application logic) to StudyLab.
- **EVIDENCE**: Phase 10 Audit (`ANTIOS_FINAL_CAPABILITY_MAP.md`) proved Antigravity natively provides robust, segregated subagent execution and tool interception, while StudyLab already owns the 20-field schema and compiler contracts.
- **ALTERNATIVES**: Build custom agent orchestrator daemons and Python domain validators.
- **WHY SELECTED**: Eliminates framework bloat, avoids rebuilding tested Google platform primitives, and ensures clean boundary separation.
- **CONSEQUENCES**: AntiOS code footprint is tiny (<500 lines of Python), high-speed (<100ms hook execution), and zero-maintenance.
- **REVERSIBILITY**: Irreversible core foundation; reversing would require building an entire agent execution platform from scratch.

---

## DECISION 02: Strict Fail-Closed Hook Architecture
- **DECISION**: All AntiOS security hooks (`pre_tool_guard.py`, `stop_gate.py`) must fail closed on any error, exception, empty payload, or unexpected type.
- **EVIDENCE**: Phase 9 Attack 2.8 and Phase 10 Audit Q9 proved that the prototype's `except Exception: allow` allowed arbitrary writes upon type mismatches, and empty `workspacePaths` bypassed path checks.
- **ALTERNATIVES**: Fail-open with warning logs (the Phase 8 prototype).
- **WHY SELECTED**: Security boundaries must never silently drop open during anomalies or adversarial attacks.
- **CONSEQUENCES**: Unhandled exceptions block tool execution and task completion until resolved. Actionable denial messages must be provided to guide recovery.
- **REVERSIBILITY**: High; failure handling logic is isolated within hook scripts.

---

## DECISION 03: Permanent Removal of `verify_task.py` Fallback
- **DECISION**: The hardcoded `verify_task.py` fallback script in `stop_gate.py` is permanently excised. All verification must execute through registered, native project test suites (`package.json`, `pyproject.toml`).
- **EVIDENCE**: Phase 9 Attack 4.3 and Phase 10 Finding F-06 proved that agents could forge test passes by creating a dummy `verify_task.py` with `sys.exit(0)`.
- **ALTERNATIVES**: Cryptographic signing of test scripts; AST validation of test scripts.
- **WHY SELECTED**: Native project test runners (`vitest`, `pytest`) are established ground truth. Arbitrary agent-authored root scripts cannot be trusted as verification evidence.
- **CONSEQUENCES**: Projects without registered test configurations cannot complete tasks with fake test scripts.
- **REVERSIBILITY**: Reversible if a project specifically registers a dedicated test harness in its configuration files.

---

## DECISION 04: Risk-Tiered Maker-Checker Verification
- **DECISION**: Independent verification via a freshly spawned subagent (`invoke_subagent`) is mandatory for High-Risk tasks (Reviewer FSM, double SQLite, APKG packaging, security hooks), but optional/solo for Low-Risk tasks (typos, formatting, docs). Verifier must use `TypeName='self'`.
- **EVIDENCE**: Phase 7 and 9 trials proved independent verification eliminates 100% of LLM confirmation bias, but Phase 10 Q19 demonstrated it adds 30–60s latency and token overhead on trivial 1-line typo fixes. Phase 10 Q3 proved `TypeName='research'` has no execution tools.
- **ALTERNATIVES**: Mandatory 100% Maker-Checker on all tasks; or 0% Maker-Checker (relying on self-review).
- **WHY SELECTED**: Balances rigorous verification on complex domain changes with speed and efficiency on trivial tasks.
- **CONSEQUENCES**: High-risk changes are audited by clean-context checkers; trivial documentation changes proceed without latency.
- **REVERSIBILITY**: High; governed by `ANTIOS_VERIFICATION_MODEL.md` and `antios-engineer` skill.

---

## DECISION 05: Workspace Root Skill & Hook Discoverability
- **DECISION**: Active AntiOS skills and hooks must reside directly in the workspace root (`<workspace_root>/.agents/skills/` and `<workspace_root>/.agents/hooks.json`).
- **EVIDENCE**: Phase 10 Audit Q1 proved that placing skills and hooks in `framework/.agents/` resulted in 100% undiscoverability by the Antigravity engine in the root workspace.
- **ALTERNATIVES**: Rely on sub-workspace folder opening; symlink directories.
- **WHY SELECTED**: Aligns directly with Antigravity's native platform discovery conventions.
- **CONSEQUENCES**: Antigravity automatically indexes `antios-engineer` and mounts `PreToolUse` and `Stop` hooks upon workspace initialization.
- **REVERSIBILITY**: High; directory layout is standard.

---

## DECISION 06: Bounded File-Backed Working Memory
- **DECISION**: Working state is maintained in version-controlled markdown (`docs/ACTIVE_CONTEXT.md`) with a strict $\le 60$ line budget. Vector memory databases and custom execution journals are permanently rejected.
- **EVIDENCE**: Phase 6 research (IDEA-05) and Phase 10 Q14 proved that zero-dependency markdown state survives context wipes, is human-auditable, and diffable in Git. Vector DBs introduce opaque retrieval failures.
- **ALTERNATIVES**: External vector DBs (Chroma/Pinecone); JSON state databases; relying solely on memory prompts.
- **WHY SELECTED**: Minimal overhead, high transparency, zero external dependencies.
- **CONSEQUENCES**: Agents must maintain `docs/ACTIVE_CONTEXT.md` across major task milestones to prevent state amnesia.
- **REVERSIBILITY**: High.

---

## DECISION 07: Native Git CLI over GitHub MCP for Local Work
- **DECISION**: Local version control operations (`git status`, `git diff`, `git log`, `git checkout`) must execute via local `git` CLI through `run_command`. GitHub MCP is restricted to remote PR creation/triage.
- **EVIDENCE**: Phase 8 Report and Phase 10 Q22 proved local Git CLI is 20x faster, consumes 0 tokens, operates offline, and works directly on local sandboxes.
- **ALTERNATIVES**: Require GitHub MCP for all repository interactions.
- **WHY SELECTED**: Drastically reduces latency and token waste; eliminates reliance on remote network roundtrips.
- **CONSEQUENCES**: Local sandbox operations remain fast, offline, and token-free.
- **REVERSIBILITY**: High.

---

## DECISION 08: Permanent Exclusion of StudySourceCore
- **DECISION**: StudySourceCore is 100% out of scope for AntiOS and StudyLab engineering tasks.
- **EVIDENCE**: Phase 8 Decision 5, Phase 10 Baseline, and User Directives. StudyLab's native compiler (`generate_apkg.py`) natively owns domain schema and package generation.
- **ALTERNATIVES**: Integrate StudySourceCore MCP server.
- **WHY SELECTED**: Eliminates foreign cross-project contamination and adheres strictly to project boundaries.
- **CONSEQUENCES**: Zero StudySourceCore files, tools, or dependencies are present in AntiOS.
- **REVERSIBILITY**: Immutable user and project directive.

---

## DECISION 09: Deterministic Project Capability Layer Architecture
- **DECISION**: Establish a unified, deterministic Project Capability Layer (`framework/core/capability.py`, `capability_registry.py`, `capability_router.py`, `capability_pack.py`) indexing 8 canonical capability types (`SKILL`, `RULE`, `WORKFLOW`, `TOOL`, `VERIFIER`, `SPECIALIST`, `EXTERNAL_PROVIDER`, `MCP_PROVIDER`) with 5-tier rule precedence and bounded capability packs ($\le 25$ lines).
- **EVIDENCE**: Phase 31–33 Implementation and verification: 354/354 tests passing in 21.3s, sub-millisecond task resolution (< 1ms), and 100% accurate golden task routing with zero vector databases or embedding models.
- **ALTERNATIVES**: Rely on unstructured string lists in subsystem declarations; use vector database embeddings for skill retrieval; collapse skills, tools, and verifiers into monolithic prompts.
- **WHY SELECTED**: Enforces clean architectural separation between Project Knowledge (where things are), Project Capability (how to work), Task Routing (what applies now), and Capability Pack (bounded bundle for current task).
- **CONSEQUENCES**: Agents deterministically receive exactly the capabilities needed for their task and subsystem with zero hallucination and clear explainability.
- **REVERSIBILITY**: High; standard Python library models and declarative JSON adapters.

