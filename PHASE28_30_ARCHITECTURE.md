# AntiOS Phase 28–30 — Architecture Specification: Agent-Native Project Knowledge & Intelligent Wayfinding
**Document ID**: `PHASE28_30_ARCHITECTURE`  
**Date**: 2026-09-04  
**Author**: AntiOS System Architecture Team  
**Status**: APPROVED FOUNDATIONAL SPECIFICATION  
**Baseline Certified**: Phase 27 Certified (266/266 tests passing in 13.2s)  
**Current State**: Certified Production-Grade (308/308 tests passing in 18.5s)  

---

## 1. Executive Summary & Objective

In software development, AI coding agents entering unfamiliar repositories suffer from severe cognitive friction:
1. **Blind Exploration**: Agents run recursive file listings, global grep searches, or unbounded AST scans, burning tokens and diluting context.
2. **Context Saturation**: Monolithic documentation dumps or full dependency graphs overwhelm the context window.
3. **Hidden Blast Radius**: Modifying a shared utility or contract breaks downstream consumers that the agent cannot see.
4. **Fabricated Certainty**: Non-deterministic LLM lookups or regex parsers emit false confidence, mistaking speculation for fact.

Phase 28–30 solves this fundamental problem by establishing a deterministic **Agent-Native Project Knowledge & Intelligent Wayfinding System**. It answers the primary cognitive question of an agent:
> *"Where should I look, what governs this area, what is affected, what capabilities should I use, and what must I verify before changing it?"*

---

## 2. Four-Tier Architecture Preservation

AntiOS maintains its strict four-tier unidirectional boundary:

```text
===================================================================================
                       TIER 1: GOOGLE ANTIGRAVITY PLATFORM
                               (Platform Mechanism)
  - Agent & Subagent Execution Lifecycle (invoke_subagent, manage_subagents, send_message)
  - Tool Runtimes (run_command via PowerShell/Bash, write_to_file, replace_file_content)
  - Hook Transport IPC (Stdio JSON-RPC for PreToolUse and Stop events)
  - Interactive Planning Mode (<planning_mode>, implementation_plan.md)
  - Immutable Logging (transcript.jsonl)
===================================================================================
                                        │
                                        ▼
===================================================================================
                             TIER 2: ANTIOS CORE
                            (Universal Governance)
  - Fail-Closed Path Guard Engine (framework/core/guard.py)
  - Physical Stop Gate Ratchet with OS Exit Code 0 (framework/core/gate.py)
  - Maker-Checker Protocol & Structured JSON Verdict (framework/core/verdict.py)
  - 10-Stage Task Lifecycle FSM (framework/core/lifecycle.py)
  - Persistent Memory & Epistemic Authority (framework/core/memory.py)
  - [PHASE 28-30] In-Memory Indexed Knowledge Graph (framework/core/knowledge.py)
  - [PHASE 28-30] Deterministic Change-Intent Analyzer (framework/core/knowledge.py)
  - [PHASE 28-30] Progressive Context Disclosure L0-L5 (framework/core/knowledge.py)
  - [PHASE 28-30] Unambiguous Ownership Deriver (framework/core/knowledge.py)
  - [PHASE 28-30] Documentation Infrastructure Classifier (framework/core/knowledge.py)
  - [EXTENDED] Intelligent Wayfinding & Locality Engine (framework/core/wayfinding.py)
  - Universal Skills & Constitution (.agents/skills/, docs/AGENTS.md)
===================================================================================
                                        │
                                        ▼
===================================================================================
                           TIER 3: PROJECT ADAPTER
                            (Declarative Binding)
  - Configuration Manifest (antios.config.json)
  - Automated Discovery & Profiling (framework/core/discovery.py, profile.py)
  - Declarative Component & Subsystem Maps (components registry)
  - Workspace Monorepo Topology & Member Mappings (framework/core/topology.py)
  - Concrete Test Runner Specifications (RunnerConfig)
===================================================================================
                                        │
                                        ▼
===================================================================================
                           TIER 4: TARGET PROJECT
                                (Domain Truth)
  - Application Source Code (TypeScript, Python, Rust, Go, C++, etc.)
  - Domain Semantics, Business Logic, and Schema Invariants
  - Native Compilers & Toolchains (tsc, cargo, vite, pytest)
  - Application Test Suites (Unit, Integration, E2E)
===================================================================================
```

### Invariants of the Boundary
1. **Zero Domain Knowledge in Core**: Core contains zero application-specific keywords, schemas, or paths.
2. **Zero StudyLab Coupling**: StudyLab and StudySourceCore remain isolated external projects; AntiOS contains zero references to them.
3. **Deterministic Standard Library Only**: Zero external database dependencies (no Neo4j, SQLite, Chroma, Pinecone). 100% Python standard library.
4. **Epistemic Honesty**: Zero invented certainty. If evidence is absent, the system explicitly returns `UNKNOWN` with confidence `0.0`.

---

## 3. Cognitive Lifecycle Integration: LOCATE FIRST

Phase 28–30 strengthens the 8-stage cognitive lifecycle by introducing **Knowledge Resolution** into the `LOCATE` gate:

```text
[ 1. INTAKE / UNDERSTAND ]
           ↓
[ 2. LOCATE & KNOWLEDGE RESOLUTION ] ──> WayfindingEngine.locate() / resolve_file()
           │                              Progressive Disclosure (L0 to L3)
           │                              Resolve governing rules, tests & skills
           ↓
[ 3. CHANGE INTENT ANALYSIS ]        ──> ChangeIntentAnalyzer.analyze_change()
           │                              Transitive blast radius & risk tier
           │                              Identify required verification suites
           ↓
[ 4. INVESTIGATE & PLAN ]            ──> Scoped diff plan (zero blind searching)
           ↓
[ 5. ACT / IMPLEMENT ]               ──> Controlled Single Writer / Worktree
           ↓
[ 6. TEST & VERIFY ]                 ──> Physical Runner Exit Code 0 + Maker-Checker
           ↓
[ 7. REMEMBER & CONSOLIDATE ]        ──> Lesson Distillation + Atomic Changeset Sync
           ↓
[ 8. COMPLETE ]                      ──> Stop Gate Ratchet Passes
```

---

## 4. Key Subsystems of the Knowledge Architecture

### 4.1 In-Memory Indexed Knowledge Graph (`KnowledgeGraph`)
- **Forward & Reverse Adjacency Maps**: Indexed by entity ID and relationship type (`(source, relation) -> edges` and `(target, relation) -> edges`).
- **Eight Directed Canonical Edges**:
  - `DEPENDS_ON`: Component $\to$ Component
  - `CONSUMED_BY`: Component $\to$ Component
  - `TESTED_BY`: Component $\to$ Test
  - `GOVERNED_BY`: Component $\to$ Rule
  - `REQUIRES_SKILL`: Component $\to$ Skill
  - `IMPLEMENTED_THROUGH`: Component $\to$ Workflow
  - `OWNED_BY`: Component $\to$ Owner
  - `DOCUMENTED_BY`: Component $\to$ Document
- **Cycle-Safe BFS Traversal**: Transitive dependency resolution and transitive consumer blast radius calculation terminate in $< 5\text{ms}$ with zero recursion limits.

### 4.2 Progressive Context Disclosure Engine (`ProgressiveDisclosureEngine`)
Ensures agents consume only the context necessary for their active cognitive phase:
- **Level 0 (Project Identity)**: Bounded $\le 5$ lines. Project name, archetype, technology, total subsystems.
- **Level 1 (Subsystem Locator)**: Bounded $\le 15$ lines. Subsystem ID, name, area, purpose, entrypoints.
- **Level 2 (Component Knowledge)**: Bounded $\le 20$ lines. Authoritative files, covering tests, test runners, invariants, risk tier.
- **Level 3 (Relationships & Blast Radius)**: Bounded $\le 25$ lines. Upstream dependencies, downstream consumers, transitive reachability.
- **Level 4 (Capabilities & Governance)**: Bounded $\le 20$ lines. Applicable skills, governing rules, standard workflows, required verifier.
- **Level 5 (Detailed Evidence)**: Exhaustive JSON specification with full provenance and doc links.

### 4.3 Deterministic Change-Intent Analyzer (`ChangeIntentAnalyzer`)
Given any planned file path modification set:
- Maps files to owning subsystems via longest-prefix matching.
- Computes aggregated risk tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Expands transitive downstream consumers and aggregates all covering test suites across consumers.
- Identifies governing rules, invariants at risk, and exact required verification procedures.
- Formats a compact Change Intent Card ($\le 25$ lines) for agent ingestion.

### 4.4 Ownership Derivation Engine (`OwnershipDeriver`)
- Scans `.github/CODEOWNERS`, `CODEOWNERS`, `docs/CODEOWNERS`.
- Extracts package manifest authors (`package.json`, `pyproject.toml`, `Cargo.toml`).
- Inspects `MAINTAINERS.md` and `AUTHORS`.
- Emits structured `OwnershipResolution(owner, source, confidence, pattern_matched)`.
- Fails safely to `(owner=None, source="UNKNOWN", confidence=0.0)` when physical proof is absent.

### 4.5 Documentation Infrastructure Classifier (`DocKnowledgeClassifier`)
- Classifies documentation into `authoritative`, `architecture`, `component`, `setup`, `testing`, `contribution`, or `general`.
- Integrates with Staleguard Layer 1 (`docaudit.py`) to verify path integrity.
- Flags undocumented subsystems and broken syntactic references.

---

## 5. Architectural Invariants
1. **Bounded Output Law**: Every locator and card must have a strict line ceiling ($\le 5$ to $\le 25$ lines) to preserve agent context windows.
2. **Zero Inferred Fact Drift**: Facts derived from heuristics are labeled `INFERRED`; only disk/manifest evidence is labeled `OBSERVED`.
3. **Fail-Closed Wayfinding**: Unmapped or invalid queries return `UNKNOWN` or `None` with fallback instructions; they never invent a nonexistent subsystem.
4. **Shallow Depth Law**: Verifiers and subagents run at depth $\le 2$ and never spawn children.
