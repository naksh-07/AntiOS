"""AntiOS Stop Gate Hook Entrypoint.

Intercepts task conclusion attempt (Stop event).
Delegates evaluation to framework.core.gate with dynamic test execution.
"""

from __future__ import annotations
import json
import os
import sys

# Ensure repository root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from framework.core.gate import evaluate_stop_gate


def output_decision(decision: str, reason: str = None) -> None:
    payload = {"decision": decision}
    if reason:
        payload["reason"] = reason
    print(json.dumps(payload))
    sys.exit(0)


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            input_data = {}
        else:
            input_data = json.loads(raw_input)

        decision, reason = evaluate_stop_gate(input_data)
        output_decision(decision, reason)

    except Exception as e:
        # STRICT FAIL-CLOSED ON ANY EXCEPTION
        output_decision("continue", f"AntiOS Stop Gate internal error: {str(e)}. Failing closed.")


if __name__ == "__main__":
    main()
