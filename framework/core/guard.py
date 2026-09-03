"""AntiOS PreToolUse Guard Engine.

Enforces deterministic boundary protection, framework self-protection,
path canonicalization, and workspace boundary confinement with strict fail-closed semantics.
"""

from __future__ import annotations
import fnmatch
import os
from typing import Any, Dict, List, Optional, Tuple

from framework.core.config import AntiOSConfig, load_config


# Immutable Core Zones that CANNOT be disabled or modified via adapter configs
IMMUTABLE_CORE_ZONES: List[str] = [
    ".agents",
    "framework",
    "antios.config.json",
    ".git",
]


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

        first_workspace = workspace_paths[0]
        if not isinstance(first_workspace, str) or not first_workspace.strip():
            return "deny", "AntiOS Security Guard: workspacePaths contains invalid entry. Failing closed."

        repo_root = os.path.normcase(os.path.abspath(os.path.realpath(first_workspace)))

        # 4. Load config if not provided
        if config is None:
            config = load_config(repo_root)

        # 5. Canonicalize TargetFile path anchored strictly to workspace root
        if not os.path.isabs(target_file):
            target_abs = os.path.abspath(os.path.join(repo_root, target_file))
        else:
            target_abs = os.path.abspath(target_file)
        target_resolved = os.path.normcase(os.path.realpath(target_abs))

        # 6. Confinement Check: TargetFile must reside within repo_root
        is_inside_repo = False
        try:
            if os.path.commonpath([target_resolved, repo_root]) == repo_root:
                is_inside_repo = True
        except ValueError:
            # Different Windows drive letters cannot share commonpath
            is_inside_repo = False

        if not is_inside_repo:
            return (
                "deny",
                f"AntiOS Boundary Policy: Modifying files outside the workspace repository ({repo_root}) "
                f"is strictly forbidden. Target: '{target_file}' -> '{target_resolved}'. Failing closed."
            )

        # 7. Framework Self-Protection (Immutable Core + Configured Zones)
        all_protected_zones = list(dict.fromkeys(IMMUTABLE_CORE_ZONES + (config.protected_zones if config else [])))
        protected_self_zones = [
            (zone, os.path.normcase(os.path.abspath(os.path.join(repo_root, zone))))
            for zone in all_protected_zones
        ]

        for zone_name, zone_path in protected_self_zones:
            try:
                if os.path.commonpath([target_resolved, zone_path]) == zone_path:
                    return (
                        "deny",
                        f"AntiOS Self-Protection Policy: Modifying AntiOS framework governance files, "
                        f"hooks, or configurations ({zone_name}) is strictly forbidden. "
                        f"DO NOT RETRY THIS ACTION. Re-evaluate your plan."
                    )
            except ValueError:
                pass

        # 8. Decompose relative path for domain boundary and alias checks
        rel_path = os.path.relpath(target_resolved, repo_root)
        rel_norm = rel_path.replace("\\", "/").lower().strip("/")
        parts = rel_path.split(os.sep)

        # 8.3 alias defense on self-protection zones
        for part in parts:
            part_lower = part.lower()
            if "~" in part_lower:
                if any(fnmatch.fnmatch(part_lower, f"{z[:6].lower()}~*") for z in ["framework", "agents", "antios"]):
                    return (
                        "deny",
                        f"AntiOS Self-Protection Policy: 8.3 alias '{part}' targeting protected governance files "
                        f"is strictly forbidden. Failing closed."
                    )

        # 9. Check Upstream Domain Boundaries (Multi-segment and segment-level)
        domain_targets = [p.replace("\\", "/").lower().strip("/") for p in config.protected_domain_paths]
        patterns = [p.lower() for p in config.forbidden_patterns]

        # Multi-segment prefix check (e.g. "src/core" or "vendor/upstream")
        for dom in domain_targets:
            if dom and (rel_norm == dom or rel_norm.startswith(dom + "/")):
                return (
                    "deny",
                    f"AntiOS Boundary Policy: Modifying '{dom}' (upstream domain core) is strictly forbidden. "
                    f"Protected by {config.name}. Direct implementation to application layers."
                )

        # Individual segment checks & pattern matching (including 8.3 aliases)
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

        # 10. All checks passed
        return "allow", None

    except Exception as e:
        # STRICT FAIL-CLOSED ON ANY UNHANDLED EXCEPTION
        return "deny", f"AntiOS Security Guard Fatal Exception: {str(e)}. Failing closed."
