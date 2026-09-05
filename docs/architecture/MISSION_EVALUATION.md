# AntiOS 2.0 Mission Evaluation Engine (Phase 91)

## 1. Deterministic Multi-Dimensional Evaluation
AntiOS 2.0 evaluates completed missions against explicit acceptance criteria and physical evidence across 11 canonical engineering dimensions:

1. **`FUNCTIONAL_CORRECTNESS`**: Physical tests exit 0, outputs match expectations.
2. **`ACCEPTANCE_CRITERIA_SATISFACTION`**: Every acceptance criterion mapped to verified evidence.
3. **`TEST_VERIFICATION`**: Physical tests executed on final unmodified working tree.
4. **`INVARIANT_COMPLIANCE`**: Constitutional limits, security invariants, single-writer respected.
5. **`REPOSITORY_INTEGRITY`**: Clean git status or expected changes only, zero conflict markers.
6. **`CHANGE_SET_INTEGRITY`**: Same Change Set satisfied (code + docs/tests co-committed, zero forbidden mutations).
7. **`WORKFORCE_GOVERNANCE`**: $\le 10$ active/wave, $\le 20$ lifetime launches, depth $\le 2$, mandatory wave collapse.
8. **`CONTEXT_GOVERNANCE`**: Token budget respected, safety invariants loaded, safe compaction intact.
9. **`EVIDENCE_COMPLETENESS`**: Zero missing or conflicting critical evidence; complete provenance on all items.
10. **`FRESHNESS_REALITY_ALIGNMENT`**: Zero stale or invalid context sources accepted without refresh.
11. **`RECOVERY_INTEGRITY`**: Recovery decisions grounded in physical reality; lifetime budget preserved across crashes.

---

## 2. The 4 Evaluation Statuses
- **`PASS`**: All acceptance criteria verified, physical tests exit 0, invariants hold, verifier approved.
- **`FAIL`**: Criteria unmet, test error, verifier rejected, or invariants violated.
- **`BLOCKED`**: Preconditions missing, toolchain missing, or gate rejection prevented execution.
- **`INCONCLUSIVE`**: Evidence is missing, contradictory, or invalidated by drift.

---

## 3. Maker-Checker Separation Contract
Under `IndependentVerifierContract`:
- The worker performing a code modification cannot be the sole authority verifying it.
- Independent verifiers receive bounded mission context, required criteria, changed artifacts, and test results — never the entire conversational history.
- HIGH and CRITICAL risk missions strictly fail closed if maker equals checker or if checker lacks independent context.

---

## 4. Token-Bounded MissionEvaluationCard
Every evaluation emits a compact card strictly bounded to $\le 25$ lines:
```text
=== ANTIOS MISSION EVALUATION ===
Mission:          <mission_id>
Acceptance:       N/M criteria verified
Physical Changes: N files modified
Tests:            N commands, M tests run (all 0)
Invariants:       N/N invariants held
Evidence:         N verified, 0 conflicting
Governance:       Workforce & Context compliant
Freshness:        FRESH (0 stale items)
Uncertainty:      None
Verdict:          PASS
==============================
```
