# AntiOS 2.0 Real Antigravity Proving Ground Architecture (Phase 96)

## 1. Architectural Purpose

The Real Antigravity Proving Ground (`framework/core/proving_ground.py`) provides an empirical, realistic execution harness for evaluating autonomous engineering workflows under real-world development conditions, edge cases, and failure vectors.

## 2. Epistemic Execution Demarcation

AntiOS strictly separates physical native execution from mock or synthetic replay:

- **`NATIVE_EXECUTION`**: Tool calls execute directly against real local runtime environments and physical subagent primitives. Every action produces authoritative on-disk artifacts and physical exit codes.
- **`SIMULATED_TRACE`**: Replayed or modeled execution traces used for regression, unit testing, and edge-case modeling without external side effects.

Simulated traces are never represented as native execution in evidence packages or certification ledgers.

## 3. The 8 Canonical Engineering Scenarios

1. **Scenario A: `SINGLE_FILE_BUG_FIX`**  
   Targeted single-file bug fix with clear deterministic reproduction and passing unit test.
2. **Scenario B: `MULTI_FILE_REFACTOR_BREAKING_INTERFACE`**  
   Interface signature update across multiple files requiring synchronized consumer updates and blast radius containment.
3. **Scenario C: `INCOMPLETE_SPECIFICATION`**  
   Underspecified acceptance criteria requiring epistemic discovery and explicit assumption surfacing before edits.
4. **Scenario D: `CONTRADICTORY_REQUIREMENTS`**  
   Conflicting requirement constraints requiring stop-and-clarify halts rather than silent assumptions.
5. **Scenario E: `UPSTREAM_DEPENDENCY_BREAKING_CHANGE`**  
   External or upstream interface change causing compilation or runtime test breakage.
6. **Scenario F: `TRANSIENT_TEST_FLAKINESS`**  
   Intermittent test failures requiring deterministic retry classification, flake isolation, and corroboration.
7. **Scenario G: `OUT_OF_BAND_PHYSICAL_DRIFT`**  
   External file mutation or git branch change occurring during mission lifecycle, triggering Stage 2 drift alerts.
8. **Scenario H: `MULTI_AGENT_CONCURRENT_EDIT_COLLISION`**  
   Simultaneous edits by parallel workers to the same target file, requiring Single-Writer Lock arbitration.

## 4. Bounded Mission Trace & Safety Guardrails

- **Hard History Bounds**: Maximum 20 lifecycle stages, 30 tool calls, 30 inspected files, and 30 modified files per trace.
- **Strict Isolation**: Proving ground executions run strictly inside isolated synthetic scratch sandboxes. Production workspaces and core framework codebases are completely forbidden.
- **Token-Bounded Output**: Emits a `ProvingGroundExecutionCard` strictly bounded to $\le 25$ lines.
