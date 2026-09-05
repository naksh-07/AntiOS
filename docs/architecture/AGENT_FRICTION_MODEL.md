# Agent Friction Taxonomy & Resolution (`docs/architecture/AGENT_FRICTION_MODEL.md`)

## 1. Overview
Agent friction consists of observable repository impediments that force agents into repeated search loops, excessive context consumption, dead-end tool executions, or verification failures.

AntiOS 2.0 deterministically detects, classifies, and resolves agent friction via `framework/core/agent_friction.py` and `framework/core/agent_improvement.py`.

---

## 2. Friction Categories & Impact

| Category | Primary Symptom | Severity | Resolution Proposal Type |
|---|---|---|---|
| `DEAD_PROJECT_REFERENCES` | Broken file links or dead symbols in docs | HIGH/MEDIUM | `DOCUMENTATION_IMPROVEMENT` |
| `ORPHANED_DOCUMENTATION` | Unindexed markdown files outside wayfinding | LOW | `WAYFINDING_IMPROVEMENT` |
| `EXCESSIVE_CONTEXT_TRAVERSAL` | Bloated context files (>60 lines) or huge skills | MEDIUM | `DOCUMENTATION_IMPROVEMENT` |
| `DUPLICATE_SKILLS` | Multiple skills with overlapping trigger words | MEDIUM | `SKILL_DEDUPLICATION` |
| `AMBIGUOUS_OWNERSHIP` | Missing `.antios/manifest.json` | HIGH | `RECOMPILE_INTELLIGENCE` |
| `MISSING_VERIFICATION_SURFACE` | No automated test runner configured | HIGH/CRITICAL | `TEST_MAPPING_IMPROVEMENT` |
| `UNNECESSARY_MCP_ESCALATION` | Escalating to Tier 6 MCP when Tier 4 CLI exists | MEDIUM | `MCP_ESCALATION_REDUCTION` |
| `CONFLICTING_INSTRUCTIONS` | Legacy `.agents/workflows/` coexistence | CRITICAL | `ORCHESTRATION_IMPROVEMENT` |
| `REPEATED_VERIFICATION_FAILURE` | Persistent failures in learning observations | HIGH | `KNOWLEDGE_REFRESH` |

---

## 3. Epistemic Classification
Findings are segregated into 4 epistemic classifications:
1. `OBSERVED_FRICTION`: Physically confirmed on disk (e.g. broken path, missing manifest, active workflow folder).
2. `INFERRED_FRICTION`: Derived through static analysis (e.g. 75%+ description word overlap between skills).
3. `POSSIBLE_FRICTION`: Heuristic warning without conclusive confirmation.
4. `UNKNOWN`: Insufficient evidence to establish friction.

---

## 4. Improvement Pipeline & NO_ACTION Contract
Friction is resolved through the canonical improvement pipeline:
$$\text{FRICTION} \longrightarrow \text{EVIDENCE} \longrightarrow \text{ROOT CAUSE} \longrightarrow \text{ALTERNATIVES} \longrightarrow \text{EXPECTED BENEFIT} \longrightarrow \text{RISK} \longrightarrow \text{BLAST RADIUS} \longrightarrow \text{PROPOSAL}$$

### The NO_ACTION Guarantee
The Improvement Proposal Engine emits `StructuredProposalType.NO_ACTION` when:
- Friction confidence is below $0.6$.
- The friction finding is classified as `UNKNOWN` or low-confidence `POSSIBLE_FRICTION`.
- Friction severity is `LOW` and proposed mutation carries `HIGH` or `CRITICAL` risk.
- Structural churn would cost more tokens/cognitive effort than the friction itself.
