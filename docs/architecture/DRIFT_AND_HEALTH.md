# AntiOS 2.0 Runtime Drift Detection & Intelligence Health Architecture (Phase 94)

## 1. Architectural Purpose

AntiOS project intelligence (wayfinding, manifests, component ownership, durable proofs, and adapter configuration) can become stale when changes occur out-of-band, across branches, or over time. The Drift and Intelligence Health Engine answers:

> **"Is the knowledge AntiOS is relying on still true?"**

Drift detection is strictly event-driven, mission-triggered, or explicitly invoked. AntiOS does NOT run background watcher daemons or persistent background threads.

## 2. The 10 Canonical Drift Domains

1. `FILE_STRUCTURE`: Directory hierarchy and file tree integrity.
2. `COMPONENT_OWNERSHIP`: Locality and component boundary mapping.
3. `PROJECT_MANIFEST`: `antios.config.json` checksum and configuration sanity.
4. `ADAPTER_CONFIGURATION`: `.antios/project_adapter.json` drift against repository archetype.
5. `SKILLS`: Agent skill workflows and interface declarations.
6. `DOCUMENTATION`: `docs/INDEX.md` and `docs/ACTIVE_CONTEXT.md` budget compliance ($\le 60$ lines).
7. `TEST_OWNERSHIP`: Availability of `tests/run_all.py` and test runner configuration.
8. `CAPABILITY_MAPPINGS`: Tool policy and provider bindings.
9. `DURABLE_PROOFS`: Physical on-disk SHA-256 validation of all active proofs.
10. `ARCHITECTURE_ASSUMPTIONS`: Immutability of protected core zones (`framework/`, `ANTIOS_CONSTITUTION.md`).

## 3. Drift Severity & Deterministic Governance Actions

Every detected drift is classified deterministically:

| Severity | Definition | Governed Action |
| :--- | :--- | :--- |
| `NO_DRIFT` | Physical reality completely matches recorded fingerprints. | `NONE` |
| `MINOR_DRIFT` | Non-functional drift (e.g. `ACTIVE_CONTEXT.md` exceeded line budget). | `REFRESH` |
| `SIGNIFICANT_DRIFT` | Manifest or adapter drift, or single durable proof invalidated. | `REVERIFY` / `REPLAN` |
| `CRITICAL_DRIFT` | Protected core zone modified, manifest unreadable, or test runner missing. | `BLOCK` |
| `UNKNOWN` | Uncorroborated state or unindexed changes. | `REBUILD_INTELLIGENCE` |

## 4. Defensible Intelligence Health Model

Intelligence health evaluates 7 defensible dimensions on a $[0.0, 1.0]$ scale:
1. `proof_freshness`: Ratio of valid active proofs against on-disk hashes.
2. `adapter_integrity`: Adapter configuration validity.
3. `navigation_integrity`: Locality entrypoints and authoritative file presence.
4. `documentation_integrity`: Line budget adherence ($\le 60$ lines) and index sanity.
5. `capability_mapping_integrity`: Registered tools and MCP provider bindings.
6. `test_mapping_integrity`: Master runner existence and test ownership.
7. `evidence_validity`: Integrity of architecture assumptions and evidence hashes.

Status Classes:
- `HEALTHY`: Average score $\ge 0.85$, zero significant/critical drift.
- `DEGRADED`: Average score $\ge 0.65$ or non-critical drift present.
- `STALE`: Average score $\ge 0.40$ or proof staleness detected.
- `UNTRUSTED`: Average score $< 0.40$ or any critical drift detected (fail closed).

## 5. Proposal-Governed Repair

Where drift is detected, AntiOS prohibits autonomous architecture mutation. Instead, `IntelligenceRepairEngine` generates bounded, governed `RepairProposal` objects (`REFRESH_PROJECT_MAP`, `REGENERATE_DOC_INDEX`, `REVALIDATE_PROOF`, `RUN_TARGETED_TESTS`, `REBUILD_CAPABILITY_MAP`, `REFRESH_ADAPTER_METADATA`, `INVALIDATE_STALE_HINT`, `REQUEST_HUMAN_REVIEW`) subjected to approval gates.

Bounds: Maximum 20 drift findings, maximum 10 repair proposals, summary card $\le 25$ lines.
