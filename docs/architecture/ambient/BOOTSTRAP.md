# AntiOS Ambient Bootstrap & Context Model

**Specification**: `docs/architecture/ambient/BOOTSTRAP.md`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Contract**: `ANTIOS_ARCHITECTURE.md` Section 5  

---

## 1. The Zero-Cost Session Bootstrap

In conventional AI agent frameworks, initialization incurs massive token overhead: thousands of lines of system instructions, JSON schemas, tool definitions, and repository dumps are injected into every turn.

AntiOS permanently rejects prompt bloating (`ARCHITECTURE_FREEZE.md:L67`). The **Ambient Bootstrap Model** guarantees instant, zero-cost session orientation through progressive, on-demand discovery.

```text
SESSION INITIALIZES
       │
       ▼
1. PLATFORM ORIENTATION (Automatic)
   - Reads docs/AGENTS.md (≤ 40 lines, < 250 tokens)
   - Grasps core laws: Toolchain ground truth, protected zones, verification
       │
       ▼
2. IMMEDIATE OPERATIONAL PRIMING (On-Demand)
   - Reads docs/ACTIVE_CONTEXT.md (≤ 60 lines, < 400 tokens)
   - Recovers current mission, active milestone, blockers, next step
       │
       ▼
3. LOCALITY WAYFINDING (On-Demand)
   - Queries .antios/anatomy.json prefix tree (< 1ms execution)
   - Locates exact files for target subsystem without repository scanning
```

---

## 2. Token Bounding & File Budget Laws

To prevent memory fragmentation and model attention drift, AntiOS enforces strict file length limits:

| File | Path | Max Lines | Enforcement Mechanism | Purpose |
| :--- | :--- | :---: | :--- | :--- |
| **Agent Directives** | `docs/AGENTS.md` | **40 lines** | `tests/test_context_bounds.py` | Platform-level axioms & operating constraints |
| **Active Context** | `docs/ACTIVE_CONTEXT.md` | **60 lines** | `framework/core/memory.py` | Working memory across task turns |
| **Capability Card** | In-memory pack | **25 lines** | `framework/core/capability_pack.py`| Bounded tool & skill metadata for active task |
| **Project Lessons** | `docs/LESSONS.md` | **50 items** | `framework/core/learning.py` | Grounded project knowledge & invariants |
| **Project Proofs** | `.antios/proofs/` | **50 files** | `framework/core/project_proof.py` | Durable physical certification tokens |

---

## 3. The `docs/AGENTS.md` Constitutional Directives

`docs/AGENTS.md` is the universal, platform-level orientation contract. It must never exceed 40 lines. Its structure is standardized:

1. **Axioms**:
   - `Target Project is ground truth.`
   - `Native toolchains define correctness.`
   - `Code and passing tests outrank conversational claims.`
2. **Protected Zones (`INV-02`)**:
   - `.agents/`, `.antios/`, `framework/`, `antios.config.json` are immutable governance zones.
3. **Verification Law (`INV-04`)**:
   - No task turn concludes without passing physical test execution (exit code 0).
4. **Shallow Depth & Resource Bounds (`INV-06`, `INV-07`)**:
   - Subagent depth $\le 2$; concurrency $\le 4$; lifetime launches $\le 10$.
5. **Memory Discipline (`INV-09`)**:
   - Update `docs/ACTIVE_CONTEXT.md` on milestone transitions; keep within 60 lines.

---

## 4. The `docs/ACTIVE_CONTEXT.md` Operational Memory

`docs/ACTIVE_CONTEXT.md` provides persistent working memory that survives context wipes, model compacting, and subagent transitions.

### Canonical Schema (60-Line Bound)
```markdown
# Active Project Context

## Current Objective
- **Goal**: [Clear, 1-sentence statement of active technical goal]
- **Active Mode**: [AMBIENT | EXPLICIT (/antios)]
- **Workforce Mode**: [SOLO | FOCUSED | SMALL | PARALLEL | STAGED | HIERARCHICAL | MAX]

## Active Milestones
- [x] Phase 107: Telemetry Sanitizer Hardening (Completed)
- [ ] Phase 108: Ambient Project OS Architecture Contract (In Progress)
- [ ] Phase 109: Ambient Integration Runtime (Planned)

## Immediate Blockers & Risks
- [None currently identified]

## Verified Next Steps
1. Reconcile DECISION_REGISTER.md with proposed ADRs 87–92.
2. Run tests/run_all.py to verify 100% pass rate.
3. Commit and push canonical architecture specifications.
```

---

## 5. Locality Wayfinding without Vector Databases

When an agent needs to locate code in an unfamiliar repository, AntiOS prohibits vector databases (`ARCHITECTURE_FREEZE.md:L63`). Instead, it uses **Deterministic Locality Wayfinding** (`framework/core/wayfinding.py`):

1. **Prefix Inverted Index**: Files and symbols are indexed into prefix trees and inverted word indices during project adaptation.
2. **Subsystem Anatomy (`.antios/anatomy.json`)**: Maps business capabilities to directory trees and risk levels.
3. **Sub-Millisecond Query**: The agent retrieves exact file paths in $< 1$ms with 100% deterministic reproducibility and 0 tokens expended on embeddings.
