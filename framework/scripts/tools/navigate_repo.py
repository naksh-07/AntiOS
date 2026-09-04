"""AntiOS Deterministic Repository Wayfinding & Navigation Tool.

Resolves a task intent, natural language query, or file path to its owning
subsystem, entrypoints, covering test suites, invariants, and blast radius.

Usage:
    python framework/scripts/tools/navigate_repo.py --query "auth"
    python framework/scripts/tools/navigate_repo.py --file "src/auth/service.py"
    python framework/scripts/tools/navigate_repo.py --list
    python framework/scripts/tools/navigate_repo.py --query "auth" --json

Outputs locator card to stdout. Exits 0 on successful resolution.
"""

from __future__ import annotations
import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normcase(os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..")))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from framework.core.config import load_config
from framework.core.discovery import discover_project
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine, LocalityResolution


def build_engine(repo_root: str) -> WayfindingEngine:
    """Builds a WayfindingEngine populated from config or automated discovery."""
    engine = WayfindingEngine(workspace_root=repo_root)
    config = load_config(repo_root)

    # 1. Load components from config if present
    registered = False
    if hasattr(config, "components") and config.components:
        for sub_id, data in config.components.items():
            if isinstance(data, dict):
                data["subsystem_id"] = sub_id
                decl = SubsystemDeclaration.from_dict(data)
                engine.register_subsystem(decl)
                registered = True

    # 2. If no components in config, run discovery to populate
    if not registered:
        try:
            profile = discover_project(repo_root)
            if hasattr(profile, "subsystems") and profile.subsystems:
                for sub_id, data in profile.subsystems.items():
                    if isinstance(data, dict):
                        data["subsystem_id"] = sub_id
                        decl = SubsystemDeclaration.from_dict(data)
                        engine.register_subsystem(decl)
        except Exception:
            pass

    return engine


def main() -> None:
    parser = argparse.ArgumentParser(description="AntiOS Repository Wayfinding & Navigation")
    parser.add_argument("--query", "-q", help="Task query, intent, or keyword")
    parser.add_argument("--file", "-f", help="Target file path to locate subsystem for")
    parser.add_argument("--list", "-l", action="store_true", help="List all registered subsystems")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--repo-root", default=REPO_ROOT, help="Repository root directory")

    args = parser.parse_args()
    repo_root = os.path.normcase(os.path.abspath(args.repo_root))
    engine = build_engine(repo_root)

    if args.list:
        subsystems = engine.list_subsystems()
        if args.json:
            print(json.dumps([s.to_dict() for s in subsystems], indent=2))
        else:
            print(f"=== ANTIOS REGISTERED SUBSYSTEMS ({len(subsystems)}) ===")
            for s in subsystems:
                print(f"- {s.subsystem_id} [{s.area}]: {s.name} ({s.description})")
                print(f"  Entrypoints: {', '.join(s.entrypoints)}")
                print(f"  Tests:       {', '.join(s.covering_tests)}")
            print("==============================================")
        sys.exit(0)

    resolution: Optional[LocalityResolution] = None

    if args.file:
        resolution = engine.resolve_file(args.file)
    elif args.query:
        resolution = engine.locate(args.query)
    else:
        parser.print_help()
        sys.exit(1)

    if not resolution:
        if args.json:
            print(json.dumps({"error": "No subsystem matched", "query": args.file or args.query}))
        else:
            print(f"AntiOS Wayfinding: No specific subsystem found for query '{args.file or args.query}'.")
            print("Fallback: Use root test runners and antios-engineer skill.")
        sys.exit(1)

    if args.json:
        print(json.dumps(resolution.to_dict(), indent=2))
    else:
        print(engine.format_locator_card(resolution))

    sys.exit(0)


if __name__ == "__main__":
    main()
