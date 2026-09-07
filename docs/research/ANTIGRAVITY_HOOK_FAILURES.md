# Antigravity Hook Failure Modes & Degraded Operation

**Status:** Canonical Architectural Monograph  
**Research Phase:** AntiOS Research 2 — Execution Primitives & Lifecycle Reality  
**Evidence Baseline:** `[OFFICIAL]` Upstream Antigravity SDK & Customization Docs (`hooks.md`), `[OBSERVED]` Empirical Windows Runtime Harness (`test_lifecycle_primitives.py`), `[EXTERNAL_REPORT]` Upstream Issue Tracker (#5358, #301)

---

## 1. Executive Summary

When external software acts as an inline interceptor in an AI agent's execution loop, hook failure semantics determine whether the system remains operational, degrades safely, or grinds to an abrupt halt. An unhandled exception, syntax error, or slow network call inside a hook script can either paralyze the agent (**Fail-Closed**) or completely bypass security policies (**Fail-Open**).

This monograph provides a rigorous forensic analysis of hook failure modes across Antigravity runtime environments. It dissects the infamous GitHub Issue #5358 (`invalid_args` default-deny failure), audits timeout behaviors, analyzes Windows-specific process wrappers (`cmd /c`), and defines the canonical AntiOS defensive pattern for 100% resilient hook scripts.

---

## 2. Platform Failure Semantics Matrix

The table below delineates the native behavior of the Antigravity host runtime when a hook script encounters fatal execution anomalies:

| Hook Type | Script Crash / Unhandled Traceback | Empty Output `{}` Emitted | Timeout Exceeded (>30s) | Native System Failure Posture |
|---|---|---|---|---|
| **`PreInvocation`** | Logs warning to stderr; proceeds with turn | No injection performed; proceeds | Terminates script; proceeds without injection | **Fail-Open** (Agent continues unsteered) |
| **`PreToolUse`** | **Denies tool call (`invalid_args`)** | **Denies tool call (`invalid_args`)** | Terminates script; **denies tool call** | **FAIL-CLOSED** (All tools blocked) |
| **`PostToolUse`** | Logs warning to stderr; proceeds | **Expected Contract** (Passes) | Terminates script; proceeds | **Fail-Open** (Telemetry dropped) |
| **`PostInvocation`**| Logs warning to stderr; proceeds | Default lifecycle continuation | Terminates script; proceeds | **Fail-Open** (Steering dropped) |
| **`Stop`** | Terminates; permits agent exit | Permits agent exit | Terminates; permits agent exit | **Fail-Open** (Session exits unverified) |

---

## 3. Case Study: GitHub Issue #5358 (`invalid_args` Deny-All)

### 3.1 The Incident `[EXTERNAL_REPORT]`
In multiple community extensions and early hook implementations, developers registered a `PreToolUse` hook with the intention of passively logging tool calls. When no modification or block was required, the hook script simply emitted an empty JSON object:
```python
# Flawed implementation
print(json.dumps({}))
sys.exit(0)
```
Upon running the agent, **every single tool call was instantly rejected** with an `invalid_args` error returned to the model. The agent repeatedly apologized, retried other tools, and became completely trapped in a paralyzed loop.

### 3.2 Root Cause Analysis `[OBSERVED]` `[OFFICIAL]`
The upstream Antigravity schema validator strictly treats `decision` as a mandatory enumerated field in `PreToolUse`:
- Allowed enum values: `["allow", "deny", "ask", "force_ask"]`.
- When the hook outputs `{}`, schema validation fails immediately on the host side.
- To protect system integrity against broken or malicious hooks, Antigravity's security engine treats any schema validation failure in `PreToolUse` as an untrusted state and enforces **FAIL-CLOSED (deny all)**.

### 3.3 The Fix
Any `PreToolUse` hook that wishes to permit tool execution **must explicitly emit**:
```json
{
  "decision": "allow"
}
```

---

## 4. Timeout Semantics & Process Termination

- **Default Timeout**: Standard timeout across all hooks is **30 seconds** unless overridden in `hooks.json`:
  ```json
  { "command": "python ../scripts/stop_gate.py", "timeout": 60 }
  ```
- **Process Killing**:
  - When the timeout expires, the Antigravity host process sends a `SIGTERM` / `SIGKILL` sequence to the child process tree.
  - On Windows, child processes spawned by `cmd /c` may occasionally survive as orphaned processes if they do not listen to standard termination signals.
- **Stop Gate Timeout Hazard**:
  - If a `Stop` hook runs an extensive test suite (e.g. `pytest tests/`) that takes 45 seconds while `timeout` is left at default 30s, the hook is killed, and the Stop Gate **fails open**, allowing an unverified session to terminate!
  - **Rule**: All test execution inside `Stop` hooks must specify an explicit timeout larger than the test suite execution ceiling, or delegate heavy test runs to asynchronous subagents.

---

## 5. Windows-Specific Failure Modes

### 5.1 Process Wrapper Escaping (`cmd /c`) `[OFFICIAL]` `[OBSERVED]`
On Windows, Antigravity executes hooks via `cmd /c "<command>"`. This creates several hazards:
1. **Quoting Hell**:
   - `python -c "import json; print('{\"decision\":\"allow\"}')"` will fail or mangle JSON inside `cmd /c` due to quote stripping.
   - **Rule**: Never use inline script commands in `hooks.json`. Always target physical Python scripts via file paths.
2. **Backslash Path Mangling**:
   - Passing Windows file paths (`C:\Users\Suraj\...`) on the command line can result in stripped backslashes.

### 5.2 The Working Directory (`cwd = .agents/`) Failure `[OBSERVED]`
- If `hooks.json` declares `"command": "python scripts/guard.py"`, the execution will crash with `FileNotFoundError: [Errno 2] No such file or directory: 'scripts/guard.py'`.
- This occurs because the working directory of the hook process is `.agents/`, not the repository root!
- **Rule**: All commands must resolve relative to `.agents/` (`python ../scripts/guard.py`) or use absolute path resolution inside the script via `Path(__file__).resolve().parent.parent`.

### 5.3 Console Window Flashing (Issue #301) `[EXTERNAL_REPORT]`
- On Windows 11, Antigravity IDE spawns hook processes without the Win32 `CREATE_NO_WINDOW` (0x08000000) process flag.
- On every hook trigger, a black console window flashes on screen for 50–100ms.
- **Rule**: Keep hook execution scripts lightning fast (<50ms) to minimize UI interruption.

---

## 6. The Canonical AntiOS Resilient Hook Template

To guarantee absolute resilience against crashes, malformed JSON, and unexpected exceptions, all AntiOS hook scripts must adhere to the following defensive template:

```python
#!/usr/bin/env python3
"""
AntiOS Defensive Hook Template
Guarantees deterministic JSON output, error containment, and safe exit codes.
"""
import sys
import json
import traceback
from pathlib import Path

# Resolve workspace root dynamically regardless of cwd
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def main() -> None:
    # 1. Read input with safe fallbacks
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
    except Exception as e:
        sys.stderr.write(f"[AntiOS Hook] Failed to parse stdin JSON: {e}\n")
        payload = {}

    # 2. Execute business logic with top-level error trapping
    try:
        # Business logic goes here
        decision = "allow"
        reason = "Operation approved by AntiOS governance."
        
        output = {
            "decision": decision,
            "reason": reason
        }
    except Exception as e:
        # 3. Defensive Fallback Strategy
        sys.stderr.write(f"[AntiOS Hook Critical Error] Unhandled exception:\n")
        traceback.print_exc(file=sys.stderr)
        
        # In PreToolUse, explicitly decide fallback posture:
        # Fail-closed is recommended for security-critical guards
        output = {
            "decision": "deny",
            "reason": f"AntiOS internal error in security hook: {str(e)}"
        }

    # 4. Atomic stdout emission
    sys.stdout.write(json.dumps(output) + "\n")
    sys.stdout.flush()
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Key Defensive Properties:
1. **Dynamic Path Anchoring**: Computes `WORKSPACE_ROOT` from `__file__`, ignoring `cwd`.
2. **Top-Level `try...except`**: Prevents Python tracebacks from spilling into `stdout` (which corrupts JSON deserialization).
3. **Explicit Exit 0**: Always exits with code 0 to prevent platform panic, encoding decisions cleanly within the JSON payload.
4. **Explicit `decision: "deny"` Fallback**: Guarantees that internal errors fail closed safely rather than crashing the agent loop.
