# AntiOS Phase 16–18 Report: Governance, Enforcement & Tooling Layer

**Date**: 2026-09-04
**Author**: AntiOS Architecture Team
**Status**: ✅ COMPLETE
**Test Suite**: 93/93 passing (31 baseline + 62 new)

---

## 1. Executive Summary

Phase 16–18 delivers the Governance, Enforcement & Tooling layer for AntiOS v1. This phase formalizes the governance model taxonomy, hardens the security posture of the Guard and Gate engines against 5 identified vulnerabilities, introduces the Same Change Set integrity engine, the Working Tree State inspector, the Tool Abstraction layer, and three deterministic CLI tools.

All work adheres to the LOCKED ARCHITECTURE constraint: `Antigravity Platform → AntiOS Core → Project Adapter → Target Project`. Zero external dependencies. Zero StudyLab coupling. Zero StudySourceCore references.

---

## 2. Deliverables

### 2.1 Core Framework Modules

| Module | Status | Description |
| :--- | :---: | :--- |
| `framework/core/governance.py` | ✅ NEW | Governance model primitives: 6 types (RULE, SKILL, WORKFLOW, HOOK, TOOL, ADAPTER) with frozen dataclass definitions, physical locations, invariants, anti-patterns, and boundary validation. |
| `framework/core/tool.py` | ✅ NEW | Minimal tool abstraction: `ToolTier` (NATIVE/SCRIPT/MCP), `ToolStatus`, `FailureClass` (7 categories), `ToolIdentity`, `ToolResult` with factory methods, `ToolSelectionPolicy` with 3-tier selection. |
| `framework/core/changeset.py` | ✅ NEW | Same Change Set engine: `ChangesetPolicy` (configurable patterns), `evaluate_changeset()` with code/test/doc classification and violation detection. |
| `framework/core/worktree.py` | ✅ NEW | Working tree inspector: `WorktreeDisposition` (5-level), `WorktreeSnapshot`, `capture_worktree_snapshot()`, `inspect_all_conflicts()`, `find_conflict_markers_in_untracked()`, `audit_worktree()`. |
| `framework/core/guard.py` | ✅ HARDENED | Immutable self-protection zones, path anchoring to workspace root, out-of-workspace boundary enforcement, multi-segment domain matching, 8.3 alias bypass defense. |
| `framework/core/gate.py` | ✅ HARDENED | Fail-closed on missing/invalid workspace, required runner binary enforcement, Same Change Set integration, deep conflict detection, Windows binary detection fix. |
| `framework/core/config.py` | ✅ UPDATED | ChangesetPolicy integration, `same_change_set` config loading from `antios.config.json`. |
| `framework/core/__init__.py` | ✅ UPDATED | Exports all Phase 16-18 public symbols. |
| `framework/scripts/hooks/stop_gate.py` | ✅ HARDENED | Empty stdin now fails closed instead of treating as empty dict. |

### 2.2 Deterministic CLI Tools

| Tool | Path | Description |
| :--- | :--- | :--- |
| `inspect_repo.py` | `framework/scripts/tools/inspect_repo.py` | Inspects repo for framework integrity, manifests, runners, git status. JSON output. |
| `check_changeset.py` | `framework/scripts/tools/check_changeset.py` | Evaluates Same Change Set policy against current git working tree. JSON output. |
| `check_worktree.py` | `framework/scripts/tools/check_worktree.py` | Captures worktree snapshot, detects conflicts, audits disposition. JSON output. |

### 2.3 Test Suite

| Test Module | Tests | Coverage |
| :--- | :---: | :--- |
| `test_guard_hardened.py` | 14 | Immutable zones, 8.3 bypass, out-of-workspace, multi-segment domains, invalid inputs |
| `test_gate_hardened.py` | 9 | Fail-closed workspace, required/optional runners, changeset disabled, valid workspace |
| `test_changeset.py` | 11 | Pattern matching, code/test/doc classification, violations, disabled policy, serialization |
| `test_tool.py` | 13 | Factory methods, selection policy, failure classes, identity, defaults |
| `test_worktree.py` | 9 | Snapshots, conflict detection, dispositions, non-git handling, forbidden dirty |
| `test_governance.py` | 9 | Taxonomy completeness, boundary validation, frozen dataclass, invariant checks |
| **Baseline (7 modules)** | **31** | Guard, gate, config, verdict, skills, lifecycle, workflows |
| **TOTAL** | **93** | **All passing** |

---

## 3. Security Hardening

### 3.1 Vulnerabilities Fixed

| # | Vulnerability | Severity | Fix |
| :---: | :--- | :---: | :--- |
| 1 | Stop Gate fail-open on empty workspace | **CRITICAL** | Gate now fails closed with `"Failing closed"` when `workspacePaths` is missing, empty, None, or contains invalid entries. |
| 2 | `antios.config.json` unprotected | **HIGH** | Added to `IMMUTABLE_CORE_ZONES` hardcoded list. Cannot be disabled by adapter config. |
| 3 | Relative path CWD anchoring | **HIGH** | All relative paths now anchored to `workspacePaths[0]` via `os.path.join(repo_root, ...)`. Never falls back to `os.getcwd()`. |
| 4 | Multi-segment domain path matching | **MEDIUM** | Normalized forward-slash prefix comparison for paths like `src/core`. |
| 5 | `enforce_same_change_set` dead code | **MEDIUM** | Now backed by `changeset.evaluate_changeset()` with full pattern matching and violation detection. |

### 3.2 Additional Defenses

- **8.3 alias bypass prevention**: Detects Windows short filename patterns (e.g., `FRAMEW~1`, `AGENTS~1`) targeting self-protection zones.
- **Windows binary detection**: `run_command_safe()` now detects "is not recognized" stderr on Windows `shell=True` instead of relying solely on `FileNotFoundError`.
- **Empty stdin defense**: `stop_gate.py` hook entrypoint fails closed on empty stdin instead of parsing `{}`.

---

## 4. Governance Model

### 4.1 Formal Taxonomy

| Primitive | Physical Location | Execution Context |
| :--- | :--- | :--- |
| **RULE** | `.agents/rules/` | Cognitive — agent reads and obeys |
| **SKILL** | `.agents/skills/*/SKILL.md` | Cognitive — agent reads and follows |
| **WORKFLOW** | `.agents/workflows/` | Cognitive — multi-step sequencing |
| **HOOK** | `.agents/hooks.json` + `framework/scripts/hooks/` | Deterministic — platform-invoked |
| **TOOL** | `framework/scripts/tools/` | Deterministic — agent-invoked |
| **ADAPTER** | `antios.config.json` | Declarative — parsed by framework |

### 4.2 Tool Selection Policy

```
Native (Antigravity built-in) → Script (deterministic Python) → MCP (only if needed)
```

Implemented in `ToolSelectionPolicy.select_tool_tier()`. MCP is last resort.

---

## 5. MCP Decision

**DEFER** with partial **REJECT**. See `ANTIOS_MCP_POLICY.md §5` for full reasoning.

Summary: No custom MCP server built. `ToolTier.MCP` reserves the extensibility surface for future needs. Building MCP wrappers around existing deterministic scripts is explicitly rejected as anti-pattern.

---

## 6. Architecture Constraints Maintained

| Constraint | Status |
| :--- | :--- |
| Locked Architecture: `Platform → Core → Adapter → Project` | ✅ Maintained |
| Zero StudyLab coupling in Core | ✅ Maintained |
| Zero StudySourceCore references | ✅ Maintained |
| Zero external dependencies (stdlib only) | ✅ Maintained |
| Python 3.8+ compatibility | ✅ Maintained |
| Windows path handling (`os.path.normcase`) | ✅ Maintained |
| All 31 baseline tests preserved | ✅ Verified |

---

## 7. File Manifest

### New Files (Phase 16–18)
```
framework/core/governance.py
framework/core/tool.py
framework/core/changeset.py
framework/core/worktree.py
framework/scripts/tools/inspect_repo.py
framework/scripts/tools/check_changeset.py
framework/scripts/tools/check_worktree.py
tests/test_guard_hardened.py
tests/test_gate_hardened.py
tests/test_changeset.py
tests/test_tool.py
tests/test_worktree.py
tests/test_governance.py
```

### Modified Files
```
framework/core/guard.py         (hardened)
framework/core/gate.py          (hardened)
framework/core/config.py        (updated)
framework/core/__init__.py      (updated exports)
framework/scripts/hooks/stop_gate.py (hardened)
tests/run_all.py                (updated test discovery)
ANTIOS_MCP_POLICY.md            (§5 added)
ANTIOS_PHASE16_18_REPORT.md     (this file)
```
