# AntiOS v1 Security Model (`ANTIOS_V1_SECURITY_MODEL.md`)

**Date**: 2026-09-04  
**Author**: AntiOS Architecture Team  
**Objective**: Establish the complete, authoritative security architecture for AntiOS v1, distinguishing IDE tool security from operating system filesystem security, and documenting boundary protections, failure semantics, and escalation paths.

---

## 1. The Fundamental Security Demarcation

An essential principle of AntiOS v1 is intellectual honesty regarding security boundaries:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 IDE TOOL SECURITY vs OS FILESYSTEM SECURITY                 │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ IDE TOOL SECURITY (AntiOS Domain)    │ OS FILESYSTEM SECURITY (Platform)    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Intercepts Antigravity tool calls: │ • Kernel-level system calls:         │
│   write_to_file, replace_file_content│   CreateFile, open(), unlink(), write│
│ • Validates file arguments via JSON  │ • Raw terminal processes:            │
│ • Enforces project boundaries        │   powershell.exe, bash, git, python  │
│ • Deterministic, synchronous gating  │ • Bypasses IDE tool runner completely│
│ • 100% Effective against IDE tools   │ • Requires OS container/ACL guards   │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

> **Security Axiom**:  
> AntiOS IDE hooks protect against accidental or agent-driven mutations originating from Antigravity's file-editing tools.  
> AntiOS **DOES NOT** and **CANNOT** claim to provide kernel-level OS filesystem security against unrestricted shell processes executed via `run_command`. Any claim that an IDE hook intercepts arbitrary PowerShell command strings is architecturally false.

---

## 2. Protected Paths & Boundaries

AntiOS v1 enforces strict immutability on two core filesystem zones:

### Zone 1: Framework Self-Protection (`.agents/` & `framework/`)
- **Paths**:
  - `<workspace_root>/.agents/` (including `hooks.json` and skills)
  - `<workspace_root>/framework/` (hook scripts and core assets)
- **Invariant**: Autonomous agents must NEVER alter the rules, hooks, or skills that govern them.
- **Enforcement**: Any `write_to_file` or `replace_file_content` targeting files within these directories is unconditionally denied.

### Zone 2: Upstream Domain Immutability (`rslib/`)
- **Paths**:
  - `<workspace_root>/sandbox/StudyLab/rslib/`
  - `<workspace_root>/rslib/`
  - Any directory segment named `rslib` or matching `rslib*` / `rslib~*`
- **Invariant**: The upstream Rust core of Anki is strictly immutable. StudyLab interacts with Anki core through stable interfaces; agents must not perform surgical mutations in upstream code.
- **Enforcement**: Denied by `pre_tool_guard.py` with actionable redirection to the TypeScript layer (`ts/`).

---

## 3. Threat Model & Adversarial Mitigations

| Threat / Attack Vector | Attack Mechanism | AntiOS v1 Mitigation | Result |
| :--- | :--- | :--- | :---: |
| **Direct Mutation** | Targeting `rslib/src/lib.rs` | Canonical path check blocks `rslib` segment | **BLOCKED** |
| **Directory Traversal** | `ts/../rslib/card.rs` | `os.path.realpath` resolves lexical `..` before comparison | **BLOCKED** |
| **Case Obfuscation** | `RSLIB/card.rs`, `RsLib/` | `os.path.normcase` lowers casing on Windows | **BLOCKED** |
| **Separator Obfuscation** | Mixed `/` and `\` slashes | `os.path.normpath` unifies separators | **BLOCKED** |
| **Windows 8.3 Aliasing** | Targeting `RSLIB~1/card.rs` | Regex checks for `~` aliases on protected roots | **BLOCKED** |
| **Hook Config Tampering** | Deleting `.agents/hooks.json` | Explicit protection of `.agents` zone | **BLOCKED** |
| **Hook Script Poisoning** | Editing `pre_tool_guard.py` | Script self-path resolution denies writes | **BLOCKED** |
| **Ancestor False Positive** | Path inside `C:\...\framework\` | `os.path.commonpath` checks prefix relative to workspace root | **PERMITTED** |
| **Malformed Injected Type** | Passing `TargetFile: 12345` | Type-check fails $\to$ enters exception $\to$ fails closed | **BLOCKED** |
| **Empty Workspace Payload** | Passing `workspacePaths: []` | Verification checks `if not workspacePaths: deny` | **BLOCKED** |
| **Test Pass Forgery** | Authoring fake `verify_task.py` | `verify_task.py` fallback permanently excised | **NEUTRALIZED** |
| **Test Config Tampering** | Changing `package.json` test script | Maker-Checker review + git diff inspection | **DETECTED** |
| **Shell Redirection Bypass** | `powershell Set-Content ...` | Platform limitation; prohibited by Constitution Directive 1 | **PLATFORM GAP** |

---

## 4. Fail-Closed Mechanics

All AntiOS security hooks adhere to strict **Fail-Closed Semantics**:

```python
try:
    # 1. Parse JSON from stdin
    # 2. Validate types and required arguments
    # 3. Canonicalize paths
    # 4. Check boundaries
except Exception as e:
    # FAIL CLOSED UNCONDITIONALLY
    output_json({
        "decision": "deny",
        "reason": f"AntiOS Security Guard encountered an internal error: {e}. Operation denied for safety."
    })
    sys.exit(0)
```

There is **zero code path** that defaults to `{"decision": "allow"}` upon an error.

---

## 5. Trusted Verification Commands & Ratchet Security

Task completion gating (`stop_gate.py`) permits only registered, trusted project test commands:
1. **Node / TypeScript**:
   - Discovered strictly from `package.json` (`scripts["vitest:once"]` or `scripts["test"]`).
   - Invoked via `npm test` or `yarn test`.
2. **Python**:
   - Discovered strictly from `pyproject.toml` (`tool.pytest`).
   - Invoked via `uv run pytest`.
3. **Hard Timeout**:
   - Subprocess invocations are bounded by `timeout=60` seconds to prevent hangs from interactive prompts.
4. **Environment Failure vs Test Failure**:
   - If the runner executable (`yarn`, `node`, `uv`) cannot be found or crashes before testing, the Stop gate reports `ENVIRONMENT_UNAVAILABLE`, distinguishing system infrastructure issues from broken application code.

---

## 6. Human Escalation Protocol

When an agent encounters a security block or environment failure that it cannot resolve autonomously:
1. **Hook Block Escalation**:
   - If an agent genuinely believes an upstream file or protected configuration needs modification, it MUST NOT attempt shell bypasses.
   - It must halt, explain the technical necessity in its response, and request human intervention.
2. **Environment Failure Escalation**:
   - If ambient runtimes (Node, Python, compiler) are broken, the agent must document the exact missing dependency and pause for human assistance.
3. **Emergency Bypass**:
   - In development environments where a human developer intentionally requires modifying `.agents/`, the human operator directly edits the file or disables hooks via the OS terminal. Autonomous agents are never granted bypass keys.
