# AntiOS 2.0 Mission Continuity & State Persistence Specification
**Phase 89: Mission State Continuity & Output Bounding**
**Status**: Authoritative Architectural Specification | **Version**: 2.0.0

---

## 1. Overview & Architecture

Multi-wave engineering missions require bounded persistence that survives context wipes, crash restarts, and tool interruptions without generating runaway state or manual user intervention.

AntiOS 2.0 establishes the fundamental doctrine:
> **"Reality > Stale State. Do not persist trivial tasks; maintain bounded state only when justified."**

---

## 2. Persistence Threshold

The `MissionStateStore` evaluates mission complexity to determine persistence mode:
- **`EPHEMERAL` (In-Memory)**:
  - Scope: 1 file, 1 wave, LOW risk tier, SOLO mode.
  - Storage: In-memory working ledger; zero filesystem directory churn.
- **`PERSISTENT` (Disk-Backed)**:
  - Scope: Multi-file, multi-wave ($\ge 2$ waves), HIGH risk tier, or parallel subagents.
  - Storage: Bounded files under `.antios/missions/<mission-id>/`.

---

## 3. Persistent Mission State Structure

A persistent mission contains exactly 4 canonical files:
```text
.antios/
    missions/
        <mission-id>/
            mission.json     # Intent, acceptance criteria, risk tier, fingerprint
            progress.json    # Lifecycle state, active wave, workstreams, worker quotas
            evidence.json    # Decisions, verified artifact hashes, test outputs, learning refs
            handoffs.json    # Structured evidence handoffs from completed workers
```

### Canonical Mission Lifecycle:
```text
CREATED -> PLANNED -> ACTIVE -> BLOCKED / RECOVERING -> VERIFYING -> COMPLETED -> ARCHIVED
```

---

## 4. Evidence-Grounded Crash Recovery

The `MissionRecoveryEngine` (`framework/core/mission_state.py`) audits disk state upon session resumption or restart:
1. **Interrupted Waves**: Detects active worker remnants from an uncollapsed wave and prompts wave consolidation (`RESUME`).
2. **Fingerprint Drift**: Detects changes in manifests or project adapter during interruption and triggers context refresh (`REFRESH`).
3. **State Contradictions**: Detects unresolvable conflicts between physical git status and progress records (`REPLAN`).
4. **Partial Writes**: Detects dirty uncommitted working tree state from crashed workers (`ROLLBACK`).
5. **Tampering / Corruption**: Detects forged verdicts or corrupted JSON files (`ABORT`).

---

## 5. Tool Output Bounding

Large command outputs (e.g. build logs, large test traces) can rapidly exhaust model context. The `ToolOutputClassifier` categorizes outputs:
- `RAW`: In-memory output during immediate turn.
- `RELEVANT`: Outputs $\le 2,000$ characters needed for immediate reasoning.
- `SUMMARIZED`: Outputs $> 2,000$ characters compacted to 20 bounded lines (head + tail) with a full cryptographic SHA-256 digest to ensure 100% reproducible verification.
- `DISCARDED`: Empty or trivial outputs.
