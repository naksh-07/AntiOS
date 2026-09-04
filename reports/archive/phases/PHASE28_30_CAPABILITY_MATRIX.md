# AntiOS Phase 28–30 — Capability Matrix (`PHASE28_30_CAPABILITY_MATRIX.md`)

**Date**: 2026-09-04  
**Author**: AntiOS System Architecture Team  
**Evaluation Status**: CERTIFIED PRODUCTION-GRADE  
**Test Baseline**: 308 / 308 tests passing (100.0%) in 18.5s  

---

## 1. Primary Capability Breakdown

| Capability Domain | Subsystem / Module | Operational Mechanism | Latency / Bounds | Verification Suite |
| :--- | :--- | :--- | :--- | :--- |
| **In-Memory Knowledge Graph** | `framework/core/knowledge.py` | Typed forward & reverse adjacency maps (`KnowledgeGraph`) with 8 canonical directed relationship types | $< 5\text{ms}$ construction, $< 1\text{ms}$ query | `tests/test_project_knowledge.py` |
| **Transitive Blast Radius Engine** | `framework/core/knowledge.py` | Cycle-safe reverse-index BFS traversal (`calculate_blast_radius`) with downstream test aggregation | $< 5\text{ms}$ across 50 nodes | `tests/test_project_knowledge.py` |
| **Change-Intent Analyzer** | `framework/core/knowledge.py` | Deterministic impact analyzer mapping files to subsystems, risk tiers, consumers, tests, and verifier gates | $< 10\text{ms}$ per change set | `tests/test_change_intent.py` |
| **Progressive Disclosure** | `framework/core/knowledge.py` | 6-tier layered retrieval engine (L0 to L5) enforcing strict line and token budget limits | L0: $\le 5$ lines<br>L1: $\le 15$ lines<br>L2: $\le 20$ lines<br>L3: $\le 25$ lines<br>L4: $\le 20$ lines | `tests/test_progressive_disclosure.py` |
| **Deterministic Ownership Derivation** | `framework/core/knowledge.py` | Multi-source scanner (`OwnershipDeriver`) parsing CODEOWNERS, manifests, and maintainer files | $< 30\text{ms}$ repo scan | `tests/test_ownership_derivation.py` |
| **Documentation Infrastructure** | `framework/core/knowledge.py` | Functional taxonomy classifier (`DocKnowledgeClassifier`) integrated with Staleguard Layer 1 (`docaudit.py`) | $< 15\text{ms}$ doc classification | `tests/test_doc_infrastructure.py` |
| **Integrated Wayfinding CLI** | `framework/scripts/tools/navigate_repo.py` | Deterministic CLI supporting `--query`, `--file`, `--component`, `--impact`, `--capabilities`, `--level`, `--json` | Instant exit code 0/1 | `tests/test_knowledge_wayfinding.py`, `tests/test_phase28_30_integration.py` |

---

## 2. Research Corpus Disposition (KEEP / ADAPT / BUILD / DEFER / REJECT)

```text
===================================================================================
[KEEP - Preserved from Prior Architecture & Phases]
  1. SubsystemDeclaration & LocalityResolution schemas from Phase 27.
  2. Bounded Context Tokens (cards <= 20-25 lines, active context <= 60 lines).
  3. Four-Tier Unidirectional Architecture (Platform -> Core -> Adapter -> Project).
  4. Epistemic Lifecycle Progression (OBSERVED -> CANDIDATE -> VALIDATED -> DURABLE).
  5. Staleguard Layer 1 Reference Auditor (docaudit.py).

[ADAPT - Refined & Generalized in Phase 28-30]
  1. SubsystemDeclaration: added canonical purpose, interfaces, risk, ownership, and doc categories.
  2. WayfindingEngine: upgraded to query progressive disclosure levels and change intent.
  3. Transitive Blast Radius: generalized from monorepo member scope to subsystem and component level.
  4. navigate_repo.py: expanded with --impact, --capabilities, --level, and --component flags.

[BUILD - Newly Implemented Primitives]
  1. KnowledgeGraph in-memory indexed graph with 8 canonical directed relationship types.
  2. OwnershipDeriver for deterministic, zero-hallucination code owner resolution.
  3. ChangeIntentAnalyzer for comprehensive downstream impact and required verification mapping.
  4. ProgressiveDisclosureEngine implementing L0 through L5 token-bounded retrieval.
  5. DocKnowledgeClassifier categorizing docs into functional agent infrastructure.

[DEFER - Postponed to Future Phases]
  1. Project Capability Generation Layer (Phase 31-33: auto-generating brand new skills/workflows).
  2. Interactive Multi-Turn Disambiguation Dialogs.
  3. Sandboxed DOM/UI Snapshot Regression Capture.

[REJECT - Permanently Excluded Anti-Patterns]
  1. External Graph Databases (Neo4j, Memgraph) -> Fragile daemons, port dependencies.
  2. Vector Memory Stores (Chroma, Pinecone) -> Non-deterministic, opaque embeddings.
  3. Regex AST Parsers for Source Code -> Fragile, false confidence, path alias blindness.
  4. LLM-as-a-Judge for Blocking CI -> Non-deterministic, expensive, prompt-injectable.
  5. Fabricated Ownership or Inferred Facts as Durable Truth.
===================================================================================
```
