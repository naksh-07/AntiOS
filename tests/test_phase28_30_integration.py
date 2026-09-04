"""End-to-End Integration Suite for AntiOS Phase 28-30: Agent-Native Project Knowledge."""

import json
import os
import subprocess
import tempfile
import unittest

from framework.core.adapter import analyze_adaptation, generate_adapter_config, verify_adapter
from framework.core.changeset import ChangesetPolicy, evaluate_changeset
from framework.core.config import load_config
from framework.core.discovery import discover_project
from framework.core.gate import evaluate_stop_gate
from framework.core.knowledge import (
    ProgressiveDisclosureLevel,
    ProgressiveDisclosureEngine,
)
from framework.core.wayfinding import WayfindingEngine


def _setup_phase28_repo(tmpdir: str):
    """Sets up a realistic multi-component repository for testing."""
    src_auth = os.path.join(tmpdir, "src", "auth")
    src_billing = os.path.join(tmpdir, "src", "billing")
    tests_dir = os.path.join(tmpdir, "tests")
    docs_dir = os.path.join(tmpdir, "docs")
    agents_dir = os.path.join(tmpdir, ".agents")
    framework_dir = os.path.join(tmpdir, "framework")
    gh_dir = os.path.join(tmpdir, ".github")

    os.makedirs(src_auth, exist_ok=True)
    os.makedirs(src_billing, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(agents_dir, exist_ok=True)
    os.makedirs(framework_dir, exist_ok=True)
    os.makedirs(gh_dir, exist_ok=True)

    # Auth files
    with open(os.path.join(src_auth, "__init__.py"), "w") as f:
        f.write("# Auth package\n")
    with open(os.path.join(src_auth, "service.py"), "w") as f:
        f.write("def authenticate(token: str): return True\n")
    with open(os.path.join(tests_dir, "test_auth.py"), "w") as f:
        f.write("def test_auth(): assert True\n")

    # Billing files
    with open(os.path.join(src_billing, "__init__.py"), "w") as f:
        f.write("# Billing package\n")
    with open(os.path.join(src_billing, "service.py"), "w") as f:
        f.write("from src.auth.service import authenticate\ndef charge(): return authenticate('t')\n")
    with open(os.path.join(tests_dir, "test_billing.py"), "w") as f:
        f.write("def test_billing(): assert True\n")

    # Documentation
    with open(os.path.join(docs_dir, "architecture.md"), "w") as f:
        f.write(
            "# System Architecture\n"
            "Auth lives in `src/auth/service.py` tested by `pytest tests/test_auth.py`.\n"
            "Billing lives in `src/billing/service.py` tested by `pytest tests/test_billing.py`.\n"
        )
    with open(os.path.join(tmpdir, "AGENTS.md"), "w") as f:
        f.write("# Agent Constitution\nInvariants: Zero secret leaks.\n")

    # CODEOWNERS
    with open(os.path.join(gh_dir, "CODEOWNERS"), "w") as f:
        f.write("* @platform-core\nsrc/auth/* @security-team\nsrc/billing/* @finance-team\n")

    # pyproject.toml
    with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
        f.write("[project]\nname = 'integrated-saas'\nversion = '1.0.0'\ndependencies = ['pytest']\n")

    # Git init
    subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@antios.org"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "AntiOS CI"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmpdir, capture_output=True)


def test_phase28_e2e_discovery_and_knowledge_population():
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_phase28_repo(tmpdir)

        # 1. Discover project
        profile = discover_project(tmpdir)
        assert "auth" in profile.subsystems
        assert "billing" in profile.subsystems

        # Verify derived ownership
        auth_data = profile.subsystems["auth"]
        assert auth_data["owner"] == "@security-team"
        assert auth_data["owner_source"] == "CODEOWNERS"

        billing_data = profile.subsystems["billing"]
        assert billing_data["owner"] == "@finance-team"


def test_phase28_e2e_wayfinding_and_progressive_disclosure():
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_phase28_repo(tmpdir)
        engine = WayfindingEngine(workspace_root=tmpdir)

        # Populate engine from discovery
        profile = discover_project(tmpdir)
        from framework.core.subsystem import SubsystemDeclaration
        for sub_id, data in profile.subsystems.items():
            data["subsystem_id"] = sub_id
            engine.register_subsystem(SubsystemDeclaration.from_dict(data))

        # Query progressive disclosure levels
        res_l0 = ProgressiveDisclosureEngine.render(
            ProgressiveDisclosureLevel.L0_PROJECT_IDENTITY,
            {"name": "integrated-saas", "archetype": "standalone", "total_subsystems": 2, "primary_tech": "Python"},
        )
        assert "[AntiOS L0 Project]" in res_l0

        res_l1, card_l1 = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L1)
        assert res_l1 is not None
        assert "=== ANTIOS L1 LOCATOR ===" in card_l1

        res_l2, card_l2 = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L2)
        assert "=== ANTIOS L2 COMPONENT KNOWLEDGE ===" in card_l2

        res_l3, card_l3 = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L3)
        assert "=== ANTIOS L3 RELATIONSHIPS & BLAST RADIUS ===" in card_l3

        res_l4, card_l4 = engine.locate_progressive("auth", level=ProgressiveDisclosureLevel.L4)
        assert "=== ANTIOS L4 CAPABILITIES & GOVERNANCE ===" in card_l4


def test_phase28_e2e_change_intent_to_verification_cycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_phase28_repo(tmpdir)
        engine = WayfindingEngine(workspace_root=tmpdir)

        profile = discover_project(tmpdir)
        from framework.core.subsystem import SubsystemDeclaration
        for sub_id, data in profile.subsystems.items():
            data["subsystem_id"] = sub_id
            data["test_commands"] = [f"pytest tests/test_{sub_id}.py"]
            # Set billing depends on auth
            if sub_id == "billing":
                data["dependencies"] = ["auth"]
            if sub_id == "auth":
                data["consumers"] = ["billing"]
            engine.register_subsystem(SubsystemDeclaration.from_dict(data))

        # Agent plans to touch auth
        intent = engine.analyze_change(["src/auth/service.py"])
        assert "auth" in intent.affected_subsystems
        assert "billing" in intent.transitive_consumers
        assert "pytest tests/test_auth.py" in intent.test_commands
        assert "pytest tests/test_billing.py" in intent.test_commands

        card = engine.change_analyzer.format_change_intent_card(intent)
        assert "=== ANTIOS CHANGE INTENT CARD ===" in card
        assert len(card.strip().splitlines()) <= 25


def test_phase28_e2e_cli_navigate_repo_subprocesses():
    cli_path = os.path.join(os.path.dirname(__file__), "..", "framework", "scripts", "tools", "navigate_repo.py")
    cli_path = os.path.abspath(cli_path)

    # 1. Test --level 0
    res0 = subprocess.run(["python", cli_path, "--level", "0"], capture_output=True, text=True)
    assert res0.returncode == 0
    assert "[AntiOS L0 Project]" in res0.stdout

    # 2. Test --impact
    resi = subprocess.run(["python", cli_path, "--impact", "framework/core/subsystem.py"], capture_output=True, text=True)
    assert resi.returncode == 0
    assert "=== ANTIOS CHANGE INTENT CARD ===" in resi.stdout

    # 3. Test --capabilities
    resc = subprocess.run(["python", cli_path, "--capabilities", "framework/core/subsystem.py"], capture_output=True, text=True)
    assert resc.returncode == 0
    assert "=== ANTIOS GOVERNING CAPABILITIES ===" in resc.stdout

    # 4. Test --file with --json
    resj = subprocess.run(["python", cli_path, "--file", "framework/core/subsystem.py", "--json"], capture_output=True, text=True)
    assert resj.returncode == 0
    data = json.loads(resj.stdout)
    assert "matched_subsystem_id" in data
    assert data["matched_subsystem_id"] == "core"
