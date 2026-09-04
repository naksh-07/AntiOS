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
from framework.core.knowledge import (
    ProgressiveDisclosureLevel,
    ProgressiveDisclosureEngine,
)
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
    parser.add_argument("--task", "-t", help="Task description / intent to resolve engineering capabilities for")
    parser.add_argument("--query", "-q", help="Task query, intent, or keyword")
    parser.add_argument("--file", "-f", help="Target file path to locate subsystem for")
    parser.add_argument("--component", "-c", help="Component or subsystem ID to inspect")
    parser.add_argument("--subsystem", "-s", help="Subsystem ID to inspect (alias for --component)")
    parser.add_argument("--impact", "-i", nargs="+", help="File path(s) to analyze change intent and systemic blast radius")
    parser.add_argument("--capabilities", help="Target subsystem or file to inspect governing capabilities")
    parser.add_argument("--level", "-L", type=int, choices=[0, 1, 2, 3, 4, 5], default=None, help="Progressive context disclosure level (0 to 5)")
    parser.add_argument("--list", "-l", action="store_true", help="List all registered subsystems")
    parser.add_argument("--agent-routing", action="store_true", help="Resolve agent role, delegation decision, boundaries, and handoff for task")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--repo-root", default=REPO_ROOT, help="Repository root directory")

    args = parser.parse_args()
    repo_root = os.path.normcase(os.path.abspath(args.repo_root))
    engine = build_engine(repo_root)

    # 1. Level 0: Project Identity (can run without specific query)
    if args.level == 0:
        config = load_config(repo_root)
        subsystems = engine.list_subsystems()
        proj_info = {
            "name": getattr(config, "name", os.path.basename(repo_root)),
            "archetype": "monorepo" if len(subsystems) > 3 else "standalone",
            "total_subsystems": len(subsystems),
            "primary_tech": "Python / Multi-Language",
        }
        if args.json:
            print(json.dumps(proj_info, indent=2))
        else:
            print(ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L0_PROJECT_IDENTITY, proj_info))
        sys.exit(0)

    # 2. List all subsystems
    if args.list:
        subsystems = engine.list_subsystems()
        if args.json:
            print(json.dumps([s.to_dict() for s in subsystems], indent=2))
        else:
            print(f"=== ANTIOS REGISTERED SUBSYSTEMS ({len(subsystems)}) ===")
            for s in subsystems:
                owner_info = f" [Owner: {s.owner} ({s.owner_source})]" if s.owner else ""
                print(f"- {s.subsystem_id} [{s.area}]: {s.name} ({s.description}){owner_info}")
                print(f"  Entrypoints: {', '.join(s.entrypoints)}")
                print(f"  Tests:       {', '.join(s.covering_tests)}")
            print("==============================================")
        sys.exit(0)

    # 3. Change Intent / Impact Analysis
    if args.impact and not args.task:
        intent = engine.analyze_change(args.impact)
        if args.json:
            print(json.dumps(intent.to_dict(), indent=2))
        else:
            print(engine.change_analyzer.format_change_intent_card(intent))
        sys.exit(0)

    # 4. Task-to-Capability Routing
    if args.task:
        from framework.core.capability_router import CapabilityRouter
        target_files = args.impact or ([args.file] if args.file else [])
        router = CapabilityRouter(wayfinding_engine=engine, workspace_root=repo_root)
        if args.agent_routing:
            routing_pack = router.resolve_agent_routing(args.task, target_files=target_files)
            if args.json:
                print(routing_pack.to_json())
            else:
                print(routing_pack.format_card())
            sys.exit(0)

        pack = router.resolve_capabilities(args.task, target_files=target_files)
        if args.json:
            print(pack.to_json())
        elif args.level == 4:
            print(ProgressiveDisclosureEngine.render(ProgressiveDisclosureLevel.L4_CAPABILITIES, pack))
        else:
            print(pack.format_card())
        sys.exit(0)

    # 5. Capabilities Inspection
    if args.capabilities:
        caps = engine.get_capabilities(args.capabilities)
        if args.json:
            print(json.dumps(caps, indent=2))
        else:
            print("=== ANTIOS GOVERNING CAPABILITIES ===")
            print(f"Target:    {caps['target']} (Subsystem: {caps.get('subsystem_id', 'Unknown')})")
            print(f"Skills:    {', '.join(caps['skills'])}")
            print(f"Workflows: {', '.join(caps['workflows'])}")
            print(f"Rules:     {'; '.join(caps['rules']) if caps['rules'] else 'Standard project rules'}")
            print(f"Tests:     {', '.join(caps['covering_tests']) if caps['covering_tests'] else 'Default runner'}")
            print(f"Runners:   {'; '.join(caps['test_commands']) if caps['test_commands'] else 'tests/run_all.py'}")
            print("=====================================")
        sys.exit(0)

    # 5. Component / File / Query Resolution
    resolution: Optional[LocalityResolution] = None
    target_param = args.component or args.subsystem or args.file or args.query

    if args.component or args.subsystem:
        resolution = engine.resolve_component(args.component or args.subsystem)
    elif args.file:
        resolution = engine.resolve_file(args.file)
    elif args.query:
        resolution = engine.locate(args.query)
    else:
        parser.print_help()
        sys.exit(1)

    if not resolution:
        if args.json:
            print(json.dumps({"error": "No subsystem matched", "query": target_param}))
        else:
            print(f"AntiOS Wayfinding: No specific subsystem found for query '{target_param}'.")
            print("Fallback: Use root test runners and antios-engineer skill.")
        sys.exit(1)

    # Format output according to requested level
    if args.json:
        if args.level is not None:
            # Render specific level JSON
            level_enum = ProgressiveDisclosureLevel(args.level)
            if level_enum == ProgressiveDisclosureLevel.L5_DETAILED_EVIDENCE:
                decl = engine.get_subsystem(resolution.matched_subsystem_id)
                print(json.dumps(decl.to_dict() if decl else resolution.to_dict(), indent=2))
            else:
                print(json.dumps(resolution.to_dict(), indent=2))
        else:
            print(json.dumps(resolution.to_dict(), indent=2))
    else:
        if args.level is not None:
            level_enum = ProgressiveDisclosureLevel(args.level)
            decl = engine.get_subsystem(resolution.matched_subsystem_id)
            target_obj = decl if level_enum == ProgressiveDisclosureLevel.L5_DETAILED_EVIDENCE and decl else resolution
            print(ProgressiveDisclosureEngine.render(level_enum, target_obj, engine.knowledge_graph))
        else:
            print(engine.format_locator_card(resolution))

    sys.exit(0)


if __name__ == "__main__":
    main()
