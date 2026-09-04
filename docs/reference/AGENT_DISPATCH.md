# AntiOS Task Dispatch & Routing Reference (`docs/reference/AGENT_DISPATCH.md`)

**Date**: 2026-09-05  
**Status**: Authoritative Reference Manual (Phases 49–54 Consolidated)  
**Objective**: Comprehensive developer and agent reference for the AntiOS Canonical Dispatch Pipeline.

---

## 1. The Canonical Dispatch Pipeline

The AntiOS dispatch pipeline connects user intent to physical execution through 8 deterministic stages:

```text
[ USER TASK / PROMPT ]
          │
          ▼
┌─────────────────────────┐
│ 1. TASK CLASSIFIER      │ -> Classifies TaskClass (FEATURE, BUG, REFACTOR, etc.) & RiskTier
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 2. WAYFINDING & KG      │ -> Locates subsystem, entrypoints, and blast radius via WayfindingEngine
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 3. CAPABILITY RESOLUTION│ -> Resolves skills, rules, and test runners via CapabilityRouter
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 4. AGENT ROUTING        │ -> Assigns Primary role and candidate specialists via AgentRouter
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 5. DUAL DISPATCH GATES  │ -> Evaluates Gate A (Pre-Planning) and Gate B (Execution Dispatch)
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 6. WORKFORCE SIZING     │ -> Sizes workforce: SOLO, FOCUSED, SMALL, PARALLEL, STAGED, HIERARCHICAL
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 7. WRITE SAFETY CHECK   │ -> Enforces Controlled Single Writer or Disjoint Workspace Branches
└──────────┬──────────────┘
          │
          ▼
┌─────────────────────────┐
│ 8. VERIFICATION WIRING  │ -> Binds Maker-Checker verifier and physical Stop Gate test runner
└─────────────────────────┘
```

---

## 2. Programmatic Python API

To resolve dispatch programmatically:

```python
from framework.core.dispatch import TaskDispatchPipeline

pipeline = TaskDispatchPipeline(workspace_root=".")
plan = pipeline.dispatch(
    task_query="Fix NullPointerException in payment service",
    target_files=["src/payment/processor.py"],
    independent_streams=1,
)

# Access resolved attributes
print(plan.workforce_mode)         # WorkforceMode.FOCUSED
print(plan.primary_role)           # "AntiOS Engineer"
print(plan.configured_test_command)# "python tests/run_all.py"
print(plan.verification_method)    # "Maker-Checker (verifier:maker-checker) + Stop Gate"

# Output token-bounded card (<= 25 lines)
print(plan.format_card())
```

---

## 3. Command Line Interface

AntiOS provides a deterministic CLI tool for task dispatch inspection:

```bash
# Basic natural language dispatch
python framework/scripts/tools/dispatch_task.py "Fix null pointer in payment service"

# Multi-stream refactoring task
python framework/scripts/tools/dispatch_task.py "Refactor database and auth subsystems" --streams 3

# JSON format for tool integrations
python framework/scripts/tools/dispatch_task.py "Add Button padding" --json
```

### CLI Output Format

```text
=== ANTIOS MISSION DISPATCH CARD ===
Mission ID:   mission-3196
Task Class:   BUG [Risk: HIGH]
Subsystem:    general
Workforce:    SOLO (Coordination: L2)
Gate A Recon: SOLO_AUTHORIZED (0 rec)
Gate B Exec:  SOLO_AUTHORIZED (0 rec)
Primary:      AntiOS Engineer
Specialists:  None (Solo Primary)
Write Safety: READ_ONLY
Test Runner:  python tests/run_all.py
Verification: Maker-Checker (verifier:maker-checker) + Stop Gate (exit code 0)
Waves:        PLANNING -> IMPLEMENTATION -> VERIFICATION
Rationale:    Task is focused and narrow; solo reconnaissance authorized;
-------------------------------------
```
