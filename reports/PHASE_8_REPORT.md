# Phase 8 Report: AntiOS Hardening + Validation

## 1. Did AntiOS survive adversarial testing?
Mostly yes, but it required critical path-traversal hardening in `PreToolUse` and "fail closed" hardening in the `Stop` gate.

## 2. What vulnerabilities were found?
- Path traversal bypass (`RSLIB/` vs `rslib/` due to OS case-insensitivity, and `../rslib`).
- False positives blocking valid paths (e.g., `sandbox/rslib`).
- Hook Self-Modification (the agent could edit the hooks).
- Fail-open exception handling in `stop_gate.py` allowed test bypass.

## 3. What was hardened?
- Path canonicalization (`os.path.realpath`, `os.path.normcase`) in `pre_tool_guard.py`.
- Meta-guards preventing edits to the `framework/` directory.
- `stop_gate.py` rewritten to dynamically discover test frameworks (`package.json`, `pyproject.toml`) and strictly fail closed on exceptions.

## 4. What failed?
- Relying on external MCP servers for local operations (GitHub MCP) added unnecessary failure points compared to standard Git CLI in a bounded sandbox.
- Schema validation via an AntiOS abstraction layer failed the Bounded Context principle.

## 5. What was removed?
- Hardcoded `verify_task.py` dependency.
- Proposed AntiOS Schema Validators.
- Heavy cryptographic receipt tracking.

## 6. What became unnecessary?
- Complex blast-radius/AST parsers. Native compiler toolchains (`tsc`, `vitest`) are universally superior.

## 7. What remains unknown?
- Optimal token/latency tuning for Maker-Checker verification on trivially simple tasks.

## 8. Did AntiOS outperform normal Antigravity on real StudyLab tasks?
**Yes.** In the Agent-vs-Agent failure injection test, naked Antigravity permanently corrupted upstream core code, whereas AntiOS safely intercepted the action and guided the agent to a recovery path.

## 9. On which tasks?
- Tasks where the agent hallucinated a false completion without running tests.
- Tasks that involved dangerous boundaries (`rslib/`).

## 10. Where did AntiOS provide no benefit?
- Documentation drift detection. Semantic matching of docs to code is better handled by an LLM subagent review rather than deterministic AntiOS rules.

## 11. Where did AntiOS make things worse?
- If dependencies were missing (e.g., `yarn` not installed), AntiOS blocked the agent from completing the task, demanding tests pass. While technically correct (Fail Closed), this causes friction.

## 12. What was the cost of AntiOS?
- Negligible latency for Python hooks (<200ms).
- Subagent verification costs additional API tokens.

## 13. Which mechanisms provided the highest value?
- The hardened `Stop` gate (test ratchet) and `PreToolUse` domain boundary guard.

## 14. Which prior-art ideas should be adopted?
- Lightweight markdown state over heavy vector memories.
- Native toolchain reliance over custom AI AST parsers.

## 15. What should AntiOS v1 contain?
- Bounded Memory Bank.
- Hardened Path Guards & Stop Gates.
- Progressive Skills.
- Maker-Checker 1:1 Subagent pattern.

## 16. What should AntiOS explicitly NOT contain?
- Schema validators.
- Cryptographic receipts.
- Dependency graph parsers.
- Bloated multi-agent swarms.

## 17. Is AntiOS ready for a controlled StudyLab pilot?
**Yes.** The system is hardened against adversarial path traversals, enforces real tests, and prevents "fail-open" completions.

## 18. What exactly should Phase 9 do?
**A. Controlled StudyLab Pilot.** AntiOS has survived its adversarial trial by fire. It is time to release it onto live, non-critical StudyLab issues in a production environment.
