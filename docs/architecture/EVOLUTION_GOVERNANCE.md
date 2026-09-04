# Controlled Evolution Governance (`docs/architecture/EVOLUTION_GOVERNANCE.md`)

## 1. Overview
AntiOS 2.0 governs how Project Agent OS capabilities evolve over time. While the framework encourages continuous, evidence-grounded improvement, all mutations to skills, tools, and specialist roles are strictly governed by formal proposals, approval classes, pre-application snapshotting, and atomic rollback.

---

## 2. Structured Capability Proposals
Every evolution recommendation is captured in a `StructuredCapabilityProposal` containing:
- **Proposal Type**: `ADD_PROJECT_SKILL`, `UPDATE_PROJECT_SKILL`, `ADD_SPECIALIST`, `UPDATE_SPECIALIST`, `ADD_TOOL_ADAPTER`, `UPDATE_TOOL_POLICY`, `RECOMPILE_INTELLIGENCE`, `MIGRATE_INSTANCE`, `REPAIR_INSTANCE`, or `NO_ACTION`.
- **Evidence & Rationale**: Concrete physical observations motivating the proposal.
- **Evaluated Alternatives**: Comparison of alternative paths, trade-offs, estimated costs, and risks.
- **Risk Tier & Blast Radius**: Rigorous classification of affected subsystems and filesystem paths.
- **Verification & Rollback Contracts**: Explicit automated commands to verify the change and exact actions to revert if verification fails.

---

## 3. Three-Tier Approval Classes

| Approval Class | Scope & Authority | Execution Protocol |
|---|---|---|
| `AUTO_EXECUTABLE` | Low-risk, project-local changes targeting pre-authorized managed files (`antios.config.json`, generated topology) | Executed automatically by compiler/lifecycle engine |
| `GOVERNANCE_REQUIRED` | Medium/High risk changes, project skill creations, or specialist modifications | Requires explicit human operator authorization |
| `CORE_IMMUTABLE_DENIED` | Any proposal touching `framework/core/`, `ANTIOS_CONSTITUTION.md`, or hooks | Unconditionally rejected; zero execution |

---

## 4. Mandatory Lifecycle & Atomic Rollback
Proposals follow a strict non-bypassable lifecycle:
$$\text{PROPOSED} \longrightarrow \text{REVIEWED} \longrightarrow \text{APPROVED} \longrightarrow \text{APPLIED} \longrightarrow \text{VERIFIED}$$

- **No Shortcuts**: Skipping `REVIEWED` or `APPROVED` directly to `APPLIED` is structurally impossible.
- **Pre-Application Snapshot**: Before any file write, the governor takes an in-memory snapshot of target files and manifest state.
- **Atomic Rollback**: If disk write fails or post-application verification checks fail, the previous state is restored immediately, marking the proposal `REJECTED`.
- **Manifest Revision Bump**: Successful applications increment instance capability revisions in `.antios/manifest.json`.
