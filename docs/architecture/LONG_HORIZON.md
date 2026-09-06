# AntiOS 2.0 Long-Horizon Adaptive Engineering Evaluation (Phase 98)

## 1. Architectural Purpose

The Long-Horizon Adaptive Engineering Evaluation (`framework/core/long_horizon.py`) empirically measures whether an agent operating under AntiOS governance compounds intelligence over multi-step engineering campaigns (sequences RUN-01 through RUN-05).

## 2. The Canonical Evaluation Sequences (RUN-01 to RUN-05)

1. **RUN-01 (`EXPLORATION_BASELINE`)**: Initial project discovery, baseline test execution, and architecture wayfinding.
2. **RUN-02 (`INCREMENTAL_FEATURE`)**: Implementation of incremental feature building upon discovered architecture.
3. **RUN-03 (`COMPLEX_REFACTOR`)**: Multi-component refactoring requiring blast radius analysis and updated tests.
4. **RUN-04 (`REGRESSION_TRIAGE`)**: Targeted diagnostic isolation and minimal fix for a regression introduced in upstream changes.
5. **RUN-05 (`RELEASE_AUDIT`)**: End-to-end drift audit, durable proof distillation, and release certification verification.

## 3. Knowledge Feedback Loop & Adaptive Proofs

AntiOS enforces a closed knowledge feedback loop:
- In RUN-01, initial wayfinding records discovered test runners, entry points, and component ownership.
- Passing runs distill verified facts into `ProjectProofStore`.
- Subsequent runs (RUN-02 to RUN-05) query cached durable proofs to skip redundant exploration, reducing tool call counts and token expenditure.
- The evaluation engine tracks performance deltas across runs, classifying outcomes into `OBSERVED_IMPROVEMENT`, `NO_MEASURABLE_CHANGE`, or `REGRESSION_DETECTED`.

## 4. Bounded Sequence Execution & Invariant Protections

- **Step Bounds**: Maximum 10 steps per sequence; maximum 30 cumulative tool calls per sequence.
- **Summary Bounding**: Multi-run history summaries are strictly bounded; raw logs are collapsed into cryptographic digests.
- **Token-Bounded Output**: Emits a `LongHorizonSequenceCard` strictly bounded to $\le 25$ lines.
