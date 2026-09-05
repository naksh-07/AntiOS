# AntiOS 2.0 Evidence Architecture (Phase 90)

## 1. Epistemic Separation Law
AntiOS 2.0 establishes a foundational epistemic separation in multi-agent engineering workflows:
$$\text{OBSERVATION} \ne \text{EVIDENCE} \ne \text{VERDICT} \ne \text{INFERENCE} \ne \text{DECISION}$$

- **`OBSERVATION`**: Raw, descriptive perception of system state (process output, tool read, exit code emitted). Unverified.
- **`EVIDENCE`**: Corroborated physical ground-truth artifact directly tied to an acceptance criterion (before/after SHA-256 diff, test run exit code 0).
- **`VERDICT`**: Formal evaluation emitted by an independent evaluator or gate.
- **`INFERENCE`**: Deductive or inductive hypothesis synthesized by an agent. Must never be treated as ground truth without proof.
- **`DECISION`**: Explicit operational commitment to an action, architecture, or policy.

> [!IMPORTANT]
> **Anti-Hallucination Invariant**: An agent's self-assertion that a task succeeded can NEVER be classified as `EVIDENCE`. Unbacked claims fail closed immediately.

---

## 2. Canonical Evidence States
Evidence progresses through 6 deterministic lifecycle states:
1. `OBSERVED`: Raw proof recorded, pending criteria evaluation.
2. `VERIFIED`: Proven valid, meeting criteria on the final unmodified working tree.
3. `INVALIDATED`: Falsified by test failure, regression, or working tree drift.
4. `SUPERSEDED`: Replaced by more authoritative evidence from a subsequent wave.
5. `MISSING`: Required by an acceptance criterion or invariant, but physical proof is absent.
6. `CONFLICTING`: Contradictory evidence exists between tools, verifiers, or runs.

---

## 3. Cryptographic Artifact Fingerprinting
Every modified file is tracked via `ArtifactFingerprint`:
- `path`: Normalized path relative to repository root.
- `sha256_before`: SHA-256 hash prior to modification.
- `sha256_after`: SHA-256 hash after modification.
- `byte_size`: Final size in bytes.
- `ownership_tier`: Security classification (`PROJECT_LOCAL`, `PROTECTED_CORE`, `IMMUTABLE`).
- `is_substantive`: Boolean indicator of content alteration.

---

## 4. Deterministic Evidence Packaging
Completed missions produce an auditable, bounded `EvidencePackage`:
- Bounded to $\le 50$ changed artifacts, $\le 100$ evidence items, $\le 30$ invariants, and $\le 10$ unresolved uncertainties.
- Integrated with `ToolOutputClassifier` to compact large command outputs ($> 2000$ characters) to 20 head/tail lines while computing the full 64-character SHA-256 digest.
- Emits a cryptographic `compute_evidence_hash()` digest over all verified items.
- Persisted to `.antios/missions/<mission_id>/evidence.json` or maintained in-memory for ephemeral tasks.
