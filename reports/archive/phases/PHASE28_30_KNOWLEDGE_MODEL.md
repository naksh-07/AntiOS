# AntiOS Phase 28–30 — Agent-Native Project Knowledge Model (`PHASE28_30_KNOWLEDGE_MODEL.md`)

**Document ID**: `PHASE28_30_KNOWLEDGE_MODEL`  
**Date**: 2026-09-04  
**Author**: AntiOS System Architecture Team  
**Status**: CANONICAL SPECIFICATION  

---

## 1. Canonical Subsystem & Component Schema

AntiOS extends `SubsystemDeclaration` as the single canonical data structure for project subsystems, maintaining full backward compatibility:

```python
@dataclass(frozen=True)
class SubsystemDeclaration:
    # --- Phase 27 Baseline Fields ---
    subsystem_id: str                      # Unique kebab-case identifier (e.g., "auth")
    name: str                              # Human-readable title
    description: str                       # High-level overview
    area: str                              # Architectural tier (core, ui, api, infra)
    root_paths: List[str]                  # Root directory prefixes (e.g., ["src/auth"])
    entrypoints: List[str]                 # Primary execution entrypoints
    authoritative_files: List[str]         # Files defining authoritative interface/types
    covering_tests: List[str]              # Test files covering this subsystem
    test_commands: List[str]               # Shell commands to execute tests
    applicable_skills: List[str]           # Agent skills governing this domain
    applicable_workflows: List[str]        # Task workflows (FEATURE, BUG, REFACTOR)
    governing_rules: List[str]             # Invariants and boundary policies
    protected_invariants: List[str]        # Paths/files that must remain unmodified
    dependencies: List[str]                # Subsystem IDs this subsystem relies upon
    consumers: List[str]                   # Subsystem IDs that rely upon this subsystem
    documentation_paths: List[str]         # Documentation files describing this subsystem
    keywords: List[str]                    # Natural language search keywords

    # --- Phase 28-30 Knowledge Extensions ---
    purpose: str = ""                      # Specific functional purpose statement
    authoritative_interfaces: List[str] = field(default_factory=list) # Interface files/contracts
    risk_tier: str = "MEDIUM"              # LOW, MEDIUM, HIGH, CRITICAL
    owner: Optional[str] = None            # Derived code owner (e.g. "@team-security")
    owner_source: str = "UNKNOWN"          # CODEOWNERS, MANIFEST, MAINTAINER_FILE, UNKNOWN
    owner_confidence: float = 0.0          # Confidence score (0.0 to 1.0)
    epistemic_state: str = "INFERRED"      # OBSERVED, INFERRED, UNKNOWN
    documentation_categories: Dict[str, List[str]] = field(default_factory=dict)
```

---

## 2. Epistemic Certainty Tiers

AntiOS enforces strict epistemic honesty. Every fact and relationship is categorized:

| Tier | Definition | Example | Confidence Weight |
| :--- | :--- | :--- | :---: |
| **`OBSERVED`** | Directly witnessed on physical disk, AST, or authoritative manifest | Path exists on disk; CODEOWNERS rule; declared dependency in `pyproject.toml` | **1.0** |
| **`INFERRED`** | Derived deterministically through heuristics or multi-key ranking | Inverted keyword match; inferred test command; directory owner from package author | **0.40 – 0.95** |
| **`UNKNOWN`** | Fact cannot be verified from physical evidence | Component without declared owner; untracked file outside known subsystems | **0.0** |

---

## 3. The 8 Canonical Directed Relationship Types

Relationships between repository entities are represented as directed `KnowledgeEdge` records in the in-memory `KnowledgeGraph`:

```text
       ┌───────────────┐
       │   COMPONENT   │
       └───────┬───────┘
               │
               ├──[ DEPENDS_ON ]─────────────► Component (Upstream Dependency)
               │
               ├──[ CONSUMED_BY ]────────────► Component (Downstream Consumer)
               │
               ├──[ TESTED_BY ]──────────────► Test Suite / Test File
               │
               ├──[ GOVERNED_BY ]────────────► Architectural Invariant / Rule
               │
               ├──[ REQUIRES_SKILL ]─────────► Agent Skill (.agents/skills/*)
               │
               ├──[ IMPLEMENTED_THROUGH ]────► Workflow (.agents/workflows/*)
               │
               ├──[ OWNED_BY ]───────────────► Person / Team Handle
               │
               └──[ DOCUMENTED_BY ]──────────► Documentation File
```

---

## 4. Stored vs. Derived vs. Ephemeral Decisions

| Property / Artifact | State | Storage / Derivation Mechanism |
| :--- | :---: | :--- |
| **Subsystem Identity & Paths** | **Stored** | Declared in `antios.config.json.components` or discovered by `ProjectDiscoveryEngine` |
| **Canonical Purpose & Invariants** | **Stored** | Maintained in subsystem declaration |
| **Direct Dependencies** | **Stored** | Declared in subsystem manifests or package topology |
| **Transitive Blast Radius** | **Derived** | Computed on-demand via cycle-safe BFS in `KnowledgeGraph` |
| **Ownership & Confidence** | **Derived** | Computed by `OwnershipDeriver` from `CODEOWNERS` and manifests |
| **Risk Tier** | **Derived / Stored** | Explicitly declared or computed from transitive consumer count |
| **Change Intent Card** | **Ephemeral** | Generated in-memory for active task by `ChangeIntentAnalyzer` |
| **Progressive Disclosure Cards** | **Ephemeral** | Rendered on-demand by `ProgressiveDisclosureEngine` (L0–L5) |
| **Validated Lessons** | **Durable** | Distilled and persisted to `docs/LESSONS.md` via `LessonDistillationEngine` |
