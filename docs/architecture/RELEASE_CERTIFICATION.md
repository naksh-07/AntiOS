# AntiOS 2.0 Long-Horizon Release Certification Architecture (Phase 95)

## 1. Architectural Purpose

AntiOS individual missions evaluate task-level correctness. Release Certification establishes multi-mission trust across long development horizons, major refactors, and multi-wave adaptations.

Release Certification is an AntiOS governance/evidence layer, NOT a CI replacement or release automation runner.

## 2. Fundamental Certification Principles

- **Current Physical Reality Outranks Historical Certification**: A past certificate is void if working tree drift or invalidated proofs are detected.
- **Evidence-Driven**: Passing exit codes or verbal assertions alone cannot grant certification.
- **Bounded Window**: Operates over a bounded window ($\le 10$ recent missions) plus a cryptographic digest collapsing older history.

## 3. The 12 Canonical Certification Dimensions

1. `FUNCTIONAL_STABILITY`: All missions in the certification window achieved `PASS` with zero regressions.
2. `TEST_INTEGRITY`: Master test runner exited 0 on final clean working tree.
3. `GOVERNANCE_INTEGRITY`: Shallow depth ($\le 2$), wave concurrency ($\le 10$), and context limits respected across all window missions.
4. `EVIDENCE_INTEGRITY`: Zero unprovenanced, missing, or conflicting evidence items in window packages.
5. `PROJECT_INTELLIGENCE_HEALTH`: Project intelligence evaluated as `HEALTHY` or acceptable `DEGRADED`.
6. `DURABLE_PROOF_FRESHNESS`: Active durable project proofs confirmed valid against on-disk SHA-256 hashes.
7. `REPOSITORY_INTEGRITY`: Clean working tree; zero git merge conflict markers (`<<<<<<<`).
8. `CHANGE_SET_INTEGRITY`: Protected core zones (`framework/`, `ANTIOS_CONSTITUTION.md`) completely untouched.
9. `CAPABILITY_INTEGRITY`: Registered capabilities and tools cleanly resolvable.
10. `RECOVERY_INTEGRITY`: Mission state continuity files intact with zero corrupted state.
11. `LONG_HORIZON_DRIFT`: Cumulative drift is non-critical and mitigated by approved proposals.
12. `UNRESOLVED_UNCERTAINTY`: Zero unaddressed high-risk unknowns.

## 4. Certification Levels

- **`CERTIFIED`**: All 12 dimensions pass; zero critical drift; physical evidence complete.
- **`CONDITIONALLY_CERTIFIED`**: Minor non-blocking documentation/adapter drift present with pending repair proposals.
- **`DEGRADED`**: Stale proofs or untrusted intelligence health present; revalidation required.
- **`BLOCKED`**: Critical drift, failed tests, unprovenanced claims, or protected core mutation detected (fail closed).
- **`UNKNOWN`**: Zero mission evaluations present in the certification window.

## 5. Certification Receipt (`LongHorizonCertificationCard`)

A compact, token-bounded summary card ($\le 25$ lines) recording:
- Certification ID & timestamp
- Project fingerprint
- Certification status & decision
- Evaluation window (active mission count + historical digest)
- Primary dimension highlights
- Intelligence health & drift state
- Durable proof health
- Verifier identity
