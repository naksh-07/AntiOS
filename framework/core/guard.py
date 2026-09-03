"""AntiOS PreToolUse Guard Engine.

Enforces deterministic boundary protection and framework self-protection
with strict fail-closed semantics.
"""

from __future__ import annotations
import fnmatch
import os
from typing import Any, Dict, Optional, Tuple

from framework.core.config import AntiOSConfig, load_config


def evaluate_tool_call(
    input_data: Any,
    config: Optional[AntiOSConfig] = None
) -> Tuple[str, Optional[str]]:
    """Evaluates a PreToolUse hook payload against security boundaries.

    Returns:
        (decision, reason) where decision is either "allow" or "deny".
    """
    try:
        # 1. Validate JSON root type
        if not isinstance(input_data, dict):
            return "deny", "AntiOS Security Guard: Invalid JSON root type (must be object). Failing closed."

        # 2. Extract and validate toolCall
        tool_call = input_data.get("toolCall")
        if not isinstance(tool_call, dict):
            return "deny", "AntiOS Security Guard: Missing or malformed toolCall object. Failing closed."

        args = tool_call.get("args")
        if not isinstance(args, dict):
            return "deny", "AntiOS Security Guard: Missing or malformed tool args. Failing closed."

        target_file = args.get("TargetFile")
        if not target_file or not isinstance(target_file, str):
            return "deny", "AntiOS Security Guard: TargetFile must be a non-empty string. Failing closed."

        # 3. Extract and validate workspacePaths
        workspace_paths = input_data.get("workspacePaths")
        if not workspace_paths or not isinstance(workspace_paths, list) or len(workspace_paths) == 0:
            return "deny", "AntiOS Security Guard: workspacePaths must be a non-empty list. Failing closed."

        repo_root = os.path.normcase(os.path.abspath(os.path.realpath(workspace_paths[0])))

        # 4. Load config if not provided
        if config is None:
            config = load_config(repo_root)

        # 5. Canonicalize TargetFile path
        target_abs = os.path.abspath(target_file)
        target_resolved = os.path.normcase(os.path.realpath(target_abs))

        # 6. Check Framework Self-Protection zones
        protected_self_zones = [
            os.path.normcase(os.path.abspath(os.path.join(repo_root, zone)))
            for zone in config.protected_zones
        ]

        for zone in protected_self_zones:
            try:
                if os.path.commonpath([target_resolved, zone]) == zone:
                    return (
                        "deny",
                        f"AntiOS Self-Protection Policy: Modifying AntiOS framework governance files, "
                        f"hooks, or configurations ({zone}) is strictly forbidden. "
                        f"DO NOT RETRY THIS ACTION. Re-evaluate your plan."
                    )
            except ValueError:
                # Different Windows drive letters cannot share commonpath
                pass

        # 7. Check Upstream Domain Boundaries
        is_inside_repo = False
        try:
            if os.path.commonpath([target_resolved, repo_root]) == repo_root:
                is_inside_repo = True
        except ValueError:
            is_inside_repo = False

        if is_inside_repo:
            rel_path = os.path.relpath(target_resolved, repo_root)
            parts = rel_path.split(os.sep)
        else:
            parts = target_resolved.split(os.sep)

        domain_targets = [p.lower() for p in config.protected_domain_paths]
        patterns = [p.lower() for p in config.forbidden_patterns]

        for part in parts:
            part_lower = part.lower()
            if part_lower in domain_targets:
                return (
                    "deny",
                    f"AntiOS Boundary Policy: Modifying '{part}' (upstream domain core) is strictly forbidden. "
                    f"Protected by {config.name}. Direct implementation to application layers."
                )

            for pat in patterns:
                if fnmatch.fnmatch(part_lower, pat):
                    return (
                        "deny",
                        f"AntiOS Boundary Policy: Modifying path matching '{pat}' ({part}) is strictly forbidden. "
                        f"Protected by {config.name}."
                    )

        # 8. All checks passed
        return "allow", None

    except Exception as e:
        # STRICT FAIL-CLOSED ON ANY UNHANDLED EXCEPTION
        return "deny", f"AntiOS Security Guard Fatal Exception: {str(e)}. Failing closed."
