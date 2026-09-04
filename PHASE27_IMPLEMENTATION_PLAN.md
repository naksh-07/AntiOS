# AntiOS Phase 27 — Implementation Plan: Agent-Native Engineering Environment

**Document ID**: `PHASE27_IMPLEMENTATION_PLAN`  
**Date**: 2026-09-04  
**Author**: AntiOS System Architect  
**Status**: APPROVED IMPLEMENTATION ROADMAP  
**Baseline Test Suite**: 234/234 passing tests in 10.83s  

---

## 1. OBJECTIVE & PHASING OVERVIEW

Transform AntiOS from a strict enforcement/guardrail operating system into a complete **Agent-Native Engineering Environment** that answers **"Where should I look?"** before **"What should I change?"**.

Implementation executes across 5 staged modules with non-negotiable verification gates between stages:
- **Module A**: Subsystem Manifest & Core Wayfinding Engine (`subsystem.py`, `wayfinding.py`, `navigate_repo.py`)
- **Module B**: Staleguard Layer 1 Syntactic Documentation Reference Auditor (`docaudit.py`, `audit_docs.py`)
- **Module C**: Project Discovery & Declarative Adapter Extension (`discovery.py`, `profile.py`, `adapter.py`)
- **Module D**: Lifecycle, Memory, Governance & Skill Integration (`lifecycle.py`, `memory.py`, `changeset.py`, `gate.py`, `.agents/skills/`)
- **Module E**: Comprehensive Zero-Dependency Test Suite & Adversarial Validation (Target: 270+ passing tests)

---

## 2. DETAILED IMPLEMENTATION MODULES

### Module A: Subsystem Manifest & Core Wayfinding Engine
1. **`framework/core/subsystem.py`**:
   - `SubsystemDeclaration` immutable dataclass: ID, name, area, root paths, entrypoints, authoritative files, covering tests, test commands, applicable skills, workflows, governing rules, protected invariants, dependencies, consumers, documentation paths, keywords.
   - Serialization to/from dictionary and JSON.
   - Validation logic ensuring all required fields are present and paths are well-formed.
2. **`framework/core/wayfinding.py`**:
   - `WayfindingEngine` class maintaining indexed subsystem declarations.
   - Multi-key index: by subsystem ID, by exact file path, by path prefix, and by keyword tokens.
   - `locate(query: str) -> Optional[LocalityResolution]`: Tokenizes query, matches against subsystem IDs, keywords, and path prefixes, returning ranked `LocalityResolution` with confidence score.
   - `resolve_file(file_path: str) -> Optional[LocalityResolution]`: Locates owning subsystem from file path using longest prefix matching.
   - `format_locator_card(resolution: LocalityResolution) -> str`: Renders compact, high-density $\le 20$-line summary for agent context injection.
   - Fail-safe default: Falls back to root project runners and universal skills if no specific subsystem matches.
3. **`framework/scripts/tools/navigate_repo.py`**:
   - CLI entrypoint: `python navigate_repo.py --query "auth"` or `--file "src/auth/token.py"`.
   - Emits human/agent-readable locator card and JSON output.

### Module B: Staleguard Layer 1 Syntactic Documentation Reference Auditor
1. **`framework/core/docaudit.py`**:
   - `DocAuditResult` dataclass: file path, valid references, broken references, status (`PASS`/`FAIL`).
   - `extract_references(content: str) -> List[DocReference]`: Deterministic regex extraction of:
     * Backticked paths: `` `path/to/file.ext` ``
     * Markdown links: `[label](relative/path/to/file)`
     * Test runner command strings: `` `pytest tests/test_*.py` `` or `` `npm test ...` ``
   - `audit_documentation_references(doc_path: str, workspace_root: str) -> DocAuditResult`:
     * Checks existence of referenced paths on physical disk using `os.path.exists` with canonicalization.
     * Extracts files mentioned in test commands and verifies test files exist.
     * Millisecond execution speed ($<1.5$s across repository), 0% false positives.
   - `audit_all_documentation(workspace_root: str) -> Dict[str, DocAuditResult]`: Scans all markdown and manifest files.
2. **`framework/scripts/tools/audit_docs.py`**:
   - CLI entrypoint: `python audit_docs.py [--path docs/]` reporting clean references and dead links.

### Module C: Project Discovery & Declarative Adapter Extension
1. **`framework/core/discovery.py`**:
   - Add `discover_subsystems(root_path: str) -> Dict[str, SubsystemDeclaration]`:
     * Scans standard project directories: `src/*`, `lib/*`, `packages/*`, `services/*`, `apps/*`, `modules/*`.
     * Pairs source directories with matching tests: `tests/test_{name}.py`, `tests/{name}/`, `{name}/**/*.test.*`.
     * Detects keywords from directory basenames and READMEs.
     * Generates proposed `SubsystemDeclaration` entries.
2. **`framework/core/profile.py`**:
   - Add `subsystems: Dict[str, Dict[str, Any]]` field to `ProjectProfile`.
3. **`framework/core/adapter.py`**:
   - Update `antios.config.json` schema to accept optional `components` dictionary.
   - Update `analyze_adaptation()` to include discovered components in the proposal.
   - Update `apply_project_adaptation()` and `verify_adapter()` to validate component entries against disk.

### Module D: Lifecycle, Memory, Governance & Skill Integration
1. **`framework/core/lifecycle.py`**:
   - Add `active_subsystem: Optional[str]` to `TaskLifecycleState`.
   - Update `ACTIVE_CONTEXT.md` serialization to include `Subsystem: <id>` in mission header when scoped.
2. **`framework/core/memory.py`**:
   - Add `subsystem_id: Optional[str]` to `Lesson` and `Decision` records.
   - Enable filtering lessons and decisions by subsystem for scoped retrieval.
3. **`framework/core/changeset.py` & `gate.py`**:
   - Wire `audit_documentation_references()` into `evaluate_changeset()`: modified documentation with dead links fails changeset validation.
   - In Stop Gate: If task touched a known subsystem, prioritize and verify that subsystem's covering tests.
4. **`.agents/skills/` Updates**:
   - Update `antios-engineer/SKILL.md` and `antios-debug/SKILL.md` to incorporate the `LOCATE` step:
     `UNDERSTAND -> LOCATE -> PLAN -> ACT -> TEST -> VERIFY -> REMEMBER -> RECOVER`.
     Directs agents to run `navigate_repo.py` before exploring files.

### Module E: Comprehensive Zero-Dependency Test Suite
1. **`tests/test_wayfinding.py`**: Unit tests for `WayfindingEngine`, path resolution, keyword matching, locator card formatting, multi-component monorepos.
2. **`tests/test_subsystem.py`**: Unit tests for `SubsystemDeclaration`, validation, serialization, invariant checks.
3. **`tests/test_docaudit.py`**: Unit tests for `DocReferenceAuditor`, valid links, dead links, test command extraction, zero false positives.
4. **`tests/test_wayfinding_adversarial.py`**: Adversarial attacks:
   - Path traversal in queries (`../../etc/passwd`)
   - Empty or whitespace-only queries
   - Circular subsystem dependencies
   - Unmapped random file queries (graceful fallback)
   - Corrupt component manifests
   - Extremely long token attacks
5. **`tests/test_phase27_integration.py`**: End-to-end integration:
   - Full flow: Discovery $\to$ Adapter $\to$ Wayfinding $\to$ Lifecycle $\to$ Changeset $\to$ Stop Gate.
   - Documentation with dead link triggers Stop Gate rejection.
   - Component-scoped test runner execution in Stop Gate.
6. **`tests/run_all.py`**: Registered new test modules; full test suite execution (270+ passing tests).

---

## 3. STEP-BY-STEP EXECUTION ORDER

1. **Step 1: Planning Approval Gate**: Output plan and register approval.
2. **Step 2: Core Primitives**: Implement `subsystem.py` and `wayfinding.py`.
3. **Step 3: Doc Auditor**: Implement `docaudit.py` and `audit_docs.py`.
4. **Step 4: Discovery & Adapter Extension**: Extend `discovery.py`, `profile.py`, and `adapter.py`.
5. **Step 5: CLI Tools**: Implement `navigate_repo.py`.
6. **Step 6: Integration**: Integrate with `lifecycle.py`, `memory.py`, `changeset.py`, `gate.py`, and `.agents/skills/`.
7. **Step 7: Test Suite Implementation**: Author unit, integration, and adversarial tests.
8. **Step 8: Baseline & Adversarial Verification**: Run `python tests/run_all.py` to confirm 100% pass rate.
9. **Step 9: Independent Verification**: Dispatch fresh-context Checker subagent (`antios-verifier`).
10. **Step 10: Final Deliverables**: Publish `PHASE27_REPORT.md`, `PHASE27_CAPABILITY_MATRIX.md`, `PHASE27_AGENT_WORKFLOW_MAP.md`, and update root documentation.
