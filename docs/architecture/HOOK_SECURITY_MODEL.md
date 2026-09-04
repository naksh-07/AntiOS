# AntiOS v1 Hook Security Architecture (`ANTIOS_HOOK_SECURITY_MODEL.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Redesign the AntiOS platform hook scripts (`PreToolUse`, `Stop`) to eliminate the critical vulnerabilities identified during Phase 9 and Phase 10 forensic audits, establishing true fail-closed determinism and rigorous path canonicalization.

---

## 1. Forensic Audit Analysis & Vulnerability Remediation

The Phase 10 forensic audit established that while the hook concept is sound, the prototype implementation suffered from 5 critical vulnerabilities:

```text
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ PROTOTYPE VULNERABILITY              │ ANTI OS v1 REMEDIATION               │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 1. Fail-Open Exception Handler       │ Catch-all exceptions immediately     │
│    (except Exception: allow)         │ output '{"decision": "deny"}'        │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 2. Missing Workspace Payload Bypass  │ If workspacePaths is empty or null,  │
│    (if not workspace_paths: allow)   │ output '{"decision": "deny"}'        │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 3. Naive 'framework' Ancestor Check  │ Use os.path.commonpath to verify if  │
│    (if "framework" in parts: deny)   │ TargetFile is inside repo's .agents  │
│    causes 100% false positives       │ or AntiOS framework path             │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 4. Hook Config Tampering Allowed     │ Explicitly protect .agents/ and      │
│    (.agents/hooks.json was editable) │ hooks.json from write_to_file        │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ 5. Windows 8.3 Alias Bypass          │ Canonicalize paths with Win32 alias  │
│    (TargetFile: RSLIB~1/dummy.rs)    │ expansion & strict normalized prefix │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 2. The 10 Mandatory Security Inquiries

### Q1: Fail-Open or Fail-Closed?
**STRICTLY FAIL-CLOSED.**
In AntiOS v1, any unexpected state, unhandled exception, syntax error, JSON decoding failure, or process abort immediately yields:
```json
{
  "decision": "deny",
  "reason": "AntiOS Security Guard: Internal hook error. FAILING CLOSED for safety: <error_details>"
}
```
Safety boundaries must never drop open when an anomaly occurs.

### Q2: What happens with malformed input?
If `sys.stdin` receives invalid JSON, a non-dictionary root, or unexpected types (e.g. `TargetFile: 12345` or `toolCall: null`), the JSON parser or type assertion fails, enters the exception block, and **fails closed** (`decision: deny`).

### Q3: What happens with missing workspace paths?
If `workspacePaths` is missing, empty (`[]`), or contains invalid strings, the hook cannot determine the trust boundary. It immediately **fails closed** (`decision: deny`), rejecting the tool call until Antigravity provides valid workspace context.

### Q4: How are canonical paths resolved?
Path resolution in `pre_tool_guard.py` follows a 4-step canonicalization pipeline:
1. **String Coercion & Stripping**: Verify `TargetFile` is a non-empty string.
2. **Absolute Resolution**: Convert relative paths to absolute using `os.path.abspath`.
3. **Symlink & Realpath Resolution**: Expand symbolic links and normalization via `os.path.realpath`.
4. **Case Normalization**: Apply `os.path.normcase` to ensure case-insensitive matching on Windows (`RSLIB/` == `rslib/`).

### Q5: How are Windows path edge cases handled?
1. **Separators**: Mixed slashes (`/` and `\`) are normalized to system standard (`os.sep`) by `os.path.normpath`.
2. **8.3 Short Names**: Paths containing `~` (e.g. `RSLIB~1`) are checked lexically; any segment matching `rslib*` or `~` within candidate directories is blocked, preventing short-name bypasses on non-existent paths.
3. **Prefix Boundary Matching**: Protected directories are evaluated using `os.path.commonpath([target, protected_dir]) == protected_dir` or exact component segment matching, never naive substring searching.

### Q6: How is `.agents/hooks.json` protected?
`pre_tool_guard.py` explicitly marks `.agents` (and any file matching `*hooks.json*` or `*.agents*`) as an immutable protected boundary. Any tool call attempting to modify, replace, or overwrite hook configurations is blocked with `decision: deny`.

### Q7: Can hooks protect themselves?
**YES, against IDE tools.**
Hooks protect their own code (`framework/scripts/hooks/`, `.agents/`) by checking target file canonical paths against the script's own directory location (`os.path.dirname(__file__)`). An agent attempting to modify `pre_tool_guard.py` or `stop_gate.py` via `write_to_file` or `replace_file_content` is unconditionally denied.

### Q8: What can hooks actually intercept?
Hooks intercept **Antigravity Tool Call Invocations**:
- `write_to_file`
- `replace_file_content`
- Future registered IDE editing tools.
- Turn/Task completion (`Stop` event).

### Q9: What remains a Platform Limitation?
**Raw Shell Execution (`run_command`).**
Antigravity's `run_command` executes raw shell strings via PowerShell or Bash. Tool interception hooks cannot reliably parse arbitrary, multi-line shell scripts, pipelines, PowerShell commands (`Set-Content`), or external Python runners. This is an inherent **Platform Boundary Limitation**. AntiOS mitigates this via Constitution Directive 1, restricted shell policy, and the Stop gate test ratchet.

### Q10: How should denial messages guide recovery?
Denial messages must never be generic "Access Denied" walls. They must provide **Actionable Redirection Guidance**:
1. What invariant was violated.
2. Why the path is protected.
3. What alternative path or tool the agent should use instead.
4. An explicit directive: `DO NOT RETRY THIS BLOCKED ACTION.`

Example:
```json
{
  "decision": "deny",
  "reason": "AntiOS Boundary Guard: Modifying rslib/ (upstream Anki core) is strictly forbidden. Upstream core components are immutable to protect domain stability. DO NOT RETRY THIS ACTION. Redirect your implementation to the application TypeScript layer (e.g., ts/src/) or author a wrapper component."
}
```
