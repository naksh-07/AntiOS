# AntiOS Phase 31–33 Decision Register (`docs/PHASE31_33_DECISION_REGISTER.md`)

**Date**: 2026-09-04  
**Status**: CANONICAL ARCHITECTURAL DECISIONS  
**Phase**: Phase 31–33 (Project Capability Layer)  

---

## Decision 1: Canonical Capability Source of Truth
- **Decision**: The source of truth for capabilities is derived dynamically by `CapabilityRegistry.build_default_registry()` from physical manifests (`.agents/skills/`, `.agents/workflows/`, `antios.config.json`, `SubsystemDeclaration`).
- **Rationale**: Eliminates duplicate static registries. Ensures that changes to skills or adapter configurations immediately reflect in routing.

## Decision 2: Zero Vector Database / Zero Embeddings Invariant
- **Decision**: Vector databases, embeddings, and external search daemons are permanently rejected.
- **Rationale**: AntiOS remains 100% standard library Python. Sub-millisecond deterministic routing (< 2ms) beats opaque, heavy embedding models.

## Decision 3: Explicit Negative Applicability
- **Decision**: Skills and rules declare conditions where they must NOT apply (`negative_applicability`).
- **Rationale**: Prevents debugging skills from polluting documentation tasks and verifier skills from bloating implementation turns.

## Decision 4: Rule Precedence & Conflict Surfacing
- **Decision**: Rules carry a 5-tier precedence hierarchy (Platform Hook > Core Invariant > Adapter Policy > Subsystem Invariant > Project Guidance).
- **Rationale**: Core safety invariants (Stop Gate, Guard) cannot be silently overridden by target project documentation. Any conflict is surfaced explicitly with its winning rule.

## Decision 5: Tool vs Skill Decoupling
- **Decision**: A Tool represents an executable mechanism (CLI script, test runner). A Skill represents procedural guidance on how to use it.
- **Rationale**: Preserves architectural purity and prevents monolithic skill bloat.

## Decision 6: Bounded Capability Pack Card Budget
- **Decision**: Capability packs rendered to text enforce a strict $\le 25$ lines budget.
- **Rationale**: Protects agent working memory from context saturation during planning and intake.

## Decision 7: Scope Boundary — Phase 34–36 Deferral
- **Decision**: Autonomous runtime skill synthesis and automated large-scale project mutation are explicitly deferred to Phase 34–36.
- **Rationale**: Phase 31–33 establishes deterministic capability routing. Runtime generation belongs to later adaptation tiers.
