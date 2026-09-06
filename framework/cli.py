"""AntiOS 2.0 Unified CLI Entrypoint.

The canonical control surface for AntiOS Project Agent OS:
  antios version [--json]
  antios status [--json]
  antios doctor [--json]
  antios install [--version <V>] [--force-downgrade] [--dry-run]
  antios update [--check] [--version <V>] [--dry-run]
  antios rollback [--version <V>] [--dry-run]
  antios repair [--check] [--plan] [--apply] [--dry-run]
  antios remove / antios uninstall [--dry-run]
  antios adapt [--dry-run]
  antios verify [--json]
  antios issue {discover,classify,create,triage}
  antios release {check,notes} [--json]
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from framework.core.adapter import analyze_adaptation, apply_project_adaptation, verify_adapter
from framework.core.discovery import discover_project
from framework.core.doctor import DoctorEngine
from framework.core.git_capability import GitCapabilityEngine
from framework.core.github_capability import GitHubCapabilityEngine, IssueClass, IssueEvidence
from framework.core.installation import InstallationLifecycleManager
from framework.core.release_engine import ReleaseEngine
from framework.core.version import (
    ANTIOS_VERSION,
    compare_versions,
    get_version_info,
)


def _resolve_target(args: argparse.Namespace) -> Path:
    """Resolves target directory from CLI arguments or cwd."""
    p = getattr(args, "path", None)
    if p:
        return Path(p).resolve()
    return Path.cwd().resolve()


def _resolve_source() -> Path:
    """Resolves the root directory of the AntiOS framework."""
    # framework/cli.py -> framework/ -> repository root
    return Path(__file__).resolve().parent.parent


# ==========================================
# Command Handlers
# ==========================================

def cmd_version(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    info = get_version_info(target)
    if getattr(args, "json", False):
        print(json.dumps(info.to_dict(), indent=2))
    else:
        print(info.format_human())
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    doc_eng = DoctorEngine(target)
    stat = doc_eng.get_status()
    if getattr(args, "json", False):
        print(json.dumps(stat.to_dict(), indent=2))
    else:
        print(stat.format_human())
    return 0 if stat.is_healthy else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    doc_eng = DoctorEngine(target)
    rep = doc_eng.run_doctor()
    if getattr(args, "json", False):
        print(json.dumps(rep.to_dict(), indent=2))
    else:
        print(rep.format_human())
    return 0 if rep.is_healthy else 1


def cmd_install(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    res = mgr.install(
        dry_run=getattr(args, "dry_run", False),
        force=getattr(args, "force", False),
        target_version=getattr(args, "version", None),
        force_downgrade=getattr(args, "force_downgrade", False),
    )

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.issues:
            for issue in res.issues:
                print(f"  - Issue: {issue}")
    return 0 if res.status in ("SUCCESS", "IDEMPOTENT") else 1


def cmd_update(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    target_ver = getattr(args, "version", None)
    if getattr(args, "check", False):
        # Read-only update check
        doc_eng = DoctorEngine(target)
        stat = doc_eng.get_status()
        ver_info = get_version_info(target)
        if getattr(args, "json", False):
            print(json.dumps({
                "updates_available": stat.updates_available,
                "current_instance_version": stat.version,
                "framework_version": ver_info.version,
            }, indent=2))
        else:
            if stat.updates_available:
                print(f"Update available: {stat.version} -> {ver_info.version}. Run 'antios update'.")
            else:
                print(f"AntiOS is already up to date ({ver_info.version}).")
        return 0

    rev = f"v{target_ver}" if target_ver else None
    res = mgr.update(new_revision=rev, dry_run=getattr(args, "dry_run", False))

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.issues:
            for issue in res.issues:
                print(f"  - {issue}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_rollback(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    res = mgr.rollback(
        target_version=getattr(args, "version", None),
        dry_run=getattr(args, "dry_run", False),
    )

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.issues:
            for issue in res.issues:
                print(f"  - {issue}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_repair(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    plan_only = getattr(args, "plan", False) or getattr(args, "check", False)
    dry_run = getattr(args, "dry_run", False) or plan_only

    res = mgr.repair(dry_run=dry_run, plan_only=plan_only)

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.written_files:
            print(f"Files affected: {len(res.written_files)}")
            for f in res.written_files[:10]:
                print(f"  - {f}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_remove(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    res = mgr.remove(dry_run=getattr(args, "dry_run", False))

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.issues:
            for issue in res.issues:
                print(f"  - Warning: {issue}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_adapt(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    res = mgr.adapt(dry_run=getattr(args, "dry_run", False))

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_verify(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    source = _resolve_source()
    mgr = InstallationLifecycleManager(source_root=source, target_root=target)

    res = mgr.verify()

    if getattr(args, "json", False):
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"[{res.status}] {res.summary}")
        if res.issues:
            for issue in res.issues:
                print(f"  - {issue}")
    return 0 if res.status == "SUCCESS" else 1


def cmd_issue(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    gh_eng = GitHubCapabilityEngine(target)
    sub = getattr(args, "issue_action", None)

    if sub == "triage":
        desc = getattr(args, "description", "")
        verdict = gh_eng.triage_feature_request(desc)
        if getattr(args, "json", False):
            print(json.dumps(verdict, indent=2))
        else:
            print(f"Feature Triage Verdict: {verdict['verdict']}")
            print(f"Permitted in 2.x:      {'Yes' if verdict['is_permitted_in_2_x'] else 'No'}")
            print(f"Reason:                {verdict['reason']}")
            print(f"Guidance:              {verdict['guidance']}")
        return 0

    if sub == "discover":
        query = getattr(args, "query", "")
        dups = gh_eng.search_duplicate_issues(query)
        if getattr(args, "json", False):
            print(json.dumps(dups, indent=2))
        else:
            if dups:
                print(f"Found {len(dups)} matching issue(s):")
                for d in dups:
                    print(f"  - #{d.get('number')}: {d.get('title')} ({d.get('state')})")
            else:
                print("No duplicate issues discovered.")
        return 0

    if sub == "create":
        title = getattr(args, "title", "Issue")
        iclass = getattr(args, "issue_class", "BUG").upper()
        try:
            ic = IssueClass(iclass)
        except ValueError:
            ic = IssueClass.BUG

        evidence = IssueEvidence(
            title=title,
            issue_class=ic,
            observed_behavior=getattr(args, "observed", "Observed failure."),
            expected_behavior=getattr(args, "expected", "Expected pass."),
            reproduction_steps=[getattr(args, "reproduce", "Run antios verify")],
            evidence_traces=[getattr(args, "trace", "Exit code 1")],
            affected_files=getattr(args, "files", []),
            anti_os_version=ANTIOS_VERSION,
        )
        print(evidence.to_markdown())
        return 0

    print("Usage: antios issue {discover,triage,create} ...")
    return 1


def cmd_release(args: argparse.Namespace) -> int:
    target = _resolve_target(args)
    rel_eng = ReleaseEngine(target)
    sub = getattr(args, "release_action", "check")

    if sub == "check":
        skip_tests = getattr(args, "skip_tests", False)
        rep = rel_eng.run_release_checks(skip_slow_tests=skip_tests)
        if getattr(args, "json", False):
            print(json.dumps(rep.to_dict(), indent=2))
        else:
            print(rep.format_human())
        return 0 if rep.is_ready_for_release else 1

    if sub == "notes":
        notes = rel_eng.generate_release_notes(getattr(args, "version", None))
        print(notes)
        return 0

    print("Usage: antios release {check,notes} ...")
    return 1


# ==========================================
# CLI Parser Setup
# ==========================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="antios",
        description="AntiOS 2.0 — Project Agent OS for Universal Engineering Governance & Autonomous Development",
    )
    subparsers = parser.add_subparsers(dest="command", help="AntiOS commands")

    # version
    p_ver = subparsers.add_parser("version", help="Print AntiOS version, channel, and environment facts")
    p_ver.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_ver.add_argument("--path", help="Target project root directory")
    p_ver.set_defaults(func=cmd_version)

    # status
    p_stat = subparsers.add_parser("status", help="Print concise operational status")
    p_stat.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_stat.add_argument("--path", help="Target project root directory")
    p_stat.set_defaults(func=cmd_status)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Run comprehensive system and project diagnostics")
    p_doc.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_doc.add_argument("--path", help="Target project root directory")
    p_doc.set_defaults(func=cmd_doctor)

    # install
    p_inst = subparsers.add_parser("install", help="Install AntiOS into the target project")
    p_inst.add_argument("--version", help="Target AntiOS version to install")
    p_inst.add_argument("--force", action="store_true", help="Force overwrite of managed files")
    p_inst.add_argument("--force-downgrade", action="store_true", help="Explicitly allow downgrade to an older version")
    p_inst.add_argument("--dry-run", action="store_true", help="Preview installation without writing files")
    p_inst.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_inst.add_argument("--path", help="Target project root directory")
    p_inst.set_defaults(func=cmd_install)

    # update
    p_upd = subparsers.add_parser("update", help="Update AntiOS instance to a newer revision")
    p_upd.add_argument("--check", action="store_true", help="Check for available updates without applying")
    p_upd.add_argument("--version", help="Specific version to update to")
    p_upd.add_argument("--dry-run", action="store_true", help="Preview update without writing files")
    p_upd.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_upd.add_argument("--path", help="Target project root directory")
    p_upd.set_defaults(func=cmd_update)

    # rollback
    p_roll = subparsers.add_parser("rollback", help="Roll back AntiOS instance to a previous snapshot")
    p_roll.add_argument("--version", help="Specific snapshot version to restore")
    p_roll.add_argument("--dry-run", action="store_true", help="Preview rollback without writing files")
    p_roll.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_roll.add_argument("--path", help="Target project root directory")
    p_roll.set_defaults(func=cmd_rollback)

    # repair
    p_rep = subparsers.add_parser("repair", help="Repair damaged, missing, or drifted instance files")
    p_rep.add_argument("--check", action="store_true", help="Check for drift without repairing")
    p_rep.add_argument("--plan", action="store_true", help="Generate and display repair plan")
    p_rep.add_argument("--apply", action="store_true", help="Apply repair plan (default)")
    p_rep.add_argument("--dry-run", action="store_true", help="Simulate repair without modifying files")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rep.add_argument("--path", help="Target project root directory")
    p_rep.set_defaults(func=cmd_repair)

    # remove / uninstall
    p_rem = subparsers.add_parser("remove", help="Safely remove AntiOS instance files")
    p_rem.add_argument("--dry-run", action="store_true", help="Preview removal without unlinking files")
    p_rem.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rem.add_argument("--path", help="Target project root directory")
    p_rem.set_defaults(func=cmd_remove)

    p_uninst = subparsers.add_parser("uninstall", help="Alias for remove")
    p_uninst.add_argument("--dry-run", action="store_true", help="Preview removal without unlinking files")
    p_uninst.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_uninst.add_argument("--path", help="Target project root directory")
    p_uninst.set_defaults(func=cmd_remove)

    # adapt
    p_adp = subparsers.add_parser("adapt", help="Re-discover and adapt target project")
    p_adp.add_argument("--dry-run", action="store_true", help="Simulate adaptation")
    p_adp.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_adp.add_argument("--path", help="Target project root directory")
    p_adp.set_defaults(func=cmd_adapt)

    # verify
    p_verf = subparsers.add_parser("verify", help="Verify instance integrity and runtime closure")
    p_verf.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_verf.add_argument("--path", help="Target project root directory")
    p_verf.set_defaults(func=cmd_verify)

    # issue
    p_iss = subparsers.add_parser("issue", help="Issue and bug management workflow")
    p_iss_sub = p_iss.add_subparsers(dest="issue_action", help="Issue action")

    p_iss_triage = p_iss_sub.add_parser("triage", help="Triage a feature request against Architecture Freeze")
    p_iss_triage.add_argument("description", help="Feature request description")
    p_iss_triage.add_argument("--json", action="store_true")

    p_iss_disc = p_iss_sub.add_parser("discover", help="Search duplicate issues")
    p_iss_disc.add_argument("query", help="Search query")
    p_iss_disc.add_argument("--json", action="store_true")

    p_iss_create = p_iss_sub.add_parser("create", help="Generate structured issue evidence card")
    p_iss_create.add_argument("--title", required=True, help="Issue title")
    p_iss_create.add_argument("--class", dest="issue_class", default="BUG", help="Issue class (BUG/FEATURE/etc)")
    p_iss_create.add_argument("--observed", default="", help="Observed behavior")
    p_iss_create.add_argument("--expected", default="", help="Expected behavior")
    p_iss_create.add_argument("--reproduce", default="", help="Steps to reproduce")
    p_iss_create.add_argument("--trace", default="", help="Command output or error trace")
    p_iss_create.add_argument("--files", nargs="*", default=[], help="Affected files")

    p_iss.set_defaults(func=cmd_issue)

    # release
    p_rel = subparsers.add_parser("release", help="Release engineering and validation")
    p_rel_sub = p_rel.add_subparsers(dest="release_action", help="Release action")

    p_rel_chk = p_rel_sub.add_parser("check", help="Run pre-flight release validation checks")
    p_rel_chk.add_argument("--skip-tests", action="store_true", help="Skip slow test suite execution")
    p_rel_chk.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rel_chk.add_argument("--path", help="Target project root directory")

    p_rel_not = p_rel_sub.add_parser("notes", help="Generate release notes")
    p_rel_not.add_argument("--version", help="Version override")

    p_rel.set_defaults(func=cmd_release)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
