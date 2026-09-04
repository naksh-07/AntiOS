# AntiOS Phase 28–30 — Decision Register (`PHASE28_30_DECISION_REGISTER.md`)

**Date**: 2026-09-04  
**Author**: AntiOS System Architecture Team  
**Status**: RATIFIED ADR LEDGER  

---

## ADR-14: In-Memory Multi-Index Graph vs. External Graph Database
- **Context**: Phase 28 requires representing relationships between subsystems, dependencies, consumers, tests, rules, and skills.
- **Alternatives Considered**:
  1. *External Graph Database (Neo4j, Memgraph, Dgraph)*: Rich Cypher querying, but introduces background service daemons, network latency, setup friction, and fragile port binding.
  2. *SQLite/DuckDB Relational Graph Tables*: Lightweight file-backed SQL, but adds disk I/O, table migrations, and query overhead for small graphs.
  3. *Pure Python In-Memory Indexed Adjacency Map (`KnowledgeGraph`)*: Standard library dictionary indices by entity ID and relationship type.
- **Decision**: **ADOPT Option 3 (Pure Python In-Memory Indexed Adjacency Map)**.
- **Rationale**: Real repository graphs contain dozens to hundreds of components, not millions. Graph construction takes $< 5\text{ms}$ and BFS reachability takes $< 2\text{ms}$. Zero background processes, zero installation requirements, 100% deterministic and diffable.

---

## ADR-15: Progressive Context Disclosure Levels (L0 to L5)
- **Context**: Dumping full repository metadata or complete dependency trees into an agent's prompt causes prompt bloat, dilution of instructions, and catastrophic context compaction loss.
- **Decision**: Establish a strict 6-tier Progressive Disclosure retrieval protocol:
  - `L0` (Project Identity): $\le 5$ lines (bootstrapping / session start)
  - `L1` (Subsystem Locator): $\le 15$ lines (locating target area)
  - `L2` (Component Knowledge): $\le 20$ lines (understanding interfaces and covering tests)
  - `L3` (Relationships & Blast Radius): $\le 25$ lines (evaluating upstream/downstream impact)
  - `L4` (Capabilities & Governance): $\le 20$ lines (identifying required skills, workflows, and rules)
  - `L5` (Detailed Evidence): Full JSON specification with physical manifest provenance
- **Rationale**: Bounded cognitive overhead. Agents request only the degree of fidelity demanded by their active lifecycle stage (`UNDERSTAND` $\to$ `LOCATE` $\to$ `PLAN` $\to$ `ACT`).

---

## ADR-16: Deterministic Ownership Derivation vs. Invented Certainty
- **Context**: Agents need to know who owns a component or module when planning architectural changes.
- **Decision**: Derive ownership deterministically from disk evidence:
  1. `.github/CODEOWNERS`, `CODEOWNERS`, `docs/CODEOWNERS` (confidence = 0.95)
  2. Package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`) (confidence = 0.80)
  3. Maintainer documents (`MAINTAINERS.md`, `AUTHORS`) (confidence = 0.50)
  4. If no physical evidence exists, return `owner = None`, `source = "UNKNOWN"`, `confidence = 0.0`.
- **Rationale**: Never hallucinate code ownership. An agent must never claim certainty without physical file proof.

---

## ADR-17: Transitive Blast Radius & Downstream Test Aggregation
- **Context**: Changing a core utility or interface risks breaking downstream consumers. An agent modifying a component must know what downstream consumers will be impacted.
- **Decision**: Implement reverse-index BFS reachability (`target -> Set<consumers>`) in `KnowledgeGraph` and automatically aggregate covering tests across all transitive consumers into `ChangeIntent.covering_tests` and `ChangeIntent.test_commands`.
- **Rationale**: Eliminates hidden breakages. When an agent edits `auth`, the change intent card automatically informs it that `billing` and `reports` consumers are affected and provides the exact `pytest` commands covering those consumers.
