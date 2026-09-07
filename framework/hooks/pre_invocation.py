"""AntiOS 3.0 PreInvocation Hook.

Fires immediately prior to LLM inference turn.
Establishes lightweight turn context and non-blocking telemetry logging.

Runtime Invariants:
- INV-10: 4-Zone ownership boundary.
- INV-11: Zero framework imports (pure stdlib + local hook helpers).
- INV-12: Sanitized telemetry emission.
- Bounded execution (< 10ms).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional

# Sibling import bootstrap (zero framework imports)
HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
if HOOK_DIR not in sys.path:
    sys.path.insert(0, HOOK_DIR)

import path_resolver
import emitter


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input.strip() else {}

        workspace_paths = input_data.get("workspacePaths", [])
        project_root = path_resolver.discover_project_root(
            cwd=os.getcwd(),
            script_file=__file__,
            workspace_paths=workspace_paths if isinstance(workspace_paths, list) else None,
        )

        # Non-blocking telemetry
        try:
            emitter.emit_event(
                project_root=project_root,
                event_type="pre_invocation",
                payload={"invocationNum": input_data.get("invocationNum", 0)},
            )
        except Exception:
            pass

        # Return standard empty injection (Turn-0 Constitution in AGENTS.md handles static steering)
        print(json.dumps({}))
        sys.exit(0)

    except Exception:
        # PreInvocation fails open by platform contract
        print(json.dumps({}))
        sys.exit(0)


if __name__ == "__main__":
    main()
