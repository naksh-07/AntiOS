"""End-to-End Integration Suite for AntiOS Phase 27: Agent-Native Engineering Environment."""

import json
import os
import shutil
import subprocess
import tempfile

from framework.core.adapter import (
    analyze_adaptation,
    generate_adapter_config,
    verify_adapter,
)
from framework.core.changeset import ChangesetPolicy, evaluate_changeset
from framework.core.config import AntiOSConfig, PoliciesConfig
from framework.core.discovery import discover_project
from framework.core.gate import evaluate_stop_gate
from framework.core.subsystem import SubsystemDeclaration
from framework.core.wayfinding import WayfindingEngine


def _setup_integration_repo(tmpdir: str):
    src_dir = os.path.join(tmpdir, "src", "billing")
    tests_dir = os.path.join(tmpdir, "tests")
    docs_dir = os.path.join(tmpdir, "docs")
    agents_dir = os.path.join(tmpdir, ".agents")
    framework_dir = os.path.join(tmpdir, "framework")

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(agents_dir, exist_ok=True)
    os.makedirs(framework_dir, exist_ok=True)

    with open(os.path.join(src_dir, "service.py"), "w") as f:
        f.write("# Billing service\nclass BillingService:\n    pass\n")
    with open(os.path.join(tests_dir, "test_billing.py"), "w") as f:
        f.write("def test_billing():\n    assert True\n")
    with open(os.path.join(docs_dir, "billing.md"), "w") as f:
        f.write(
            "# Billing Documentation\n"
            "The core service is at `src/billing/service.py`.\n"
            "Covered by `pytest tests/test_billing.py`.\n"
        )
    with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
        f.write("[project]\nname = 'integration-app'\nversion = '0.1.0'\n")

    subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@antios.org"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "AntiOS Test"], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmpdir, capture_output=True)


def test_phase27_e2e_01_discovery_to_components_adaptation():
    """Zero-code discovery infers billing subsystem and adapts into antios.config.json components."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_integration_repo(tmpdir)
        profile = discover_project(tmpdir)
        assert "billing" in profile.subsystems
        billing_sub = profile.subsystems["billing"]
        assert billing_sub["subsystem_id"] == "billing"
        assert "src/billing" in billing_sub["root_paths"]
        assert "src/billing/service.py" in billing_sub["entrypoints"]
        assert "tests/test_billing.py" in billing_sub["covering_tests"]

        proposal = analyze_adaptation(profile)
        component_items = [i for i in proposal.items if i.component == "components"]
        assert len(component_items) == 1
        assert component_items[0].risk.value == "LOW"
        assert component_items[0].is_automated_safe is True

        cfg = generate_adapter_config(profile, proposal)
        assert "billing" in cfg.components

        verif_res = verify_adapter(tmpdir, config=cfg)
        assert verif_res.is_valid is True


def test_phase27_e2e_02_wayfinding_resolution_from_adapted_config():
    """WayfindingEngine loaded from config resolves intent queries accurately."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_integration_repo(tmpdir)
        profile = discover_project(tmpdir)
        proposal = analyze_adaptation(profile)
        cfg = generate_adapter_config(profile, proposal)

        engine = WayfindingEngine(workspace_root=tmpdir)
        for sub_id, data in cfg.components.items():
            decl = SubsystemDeclaration.from_dict(data)
            engine.register_subsystem(decl)

        res = engine.locate("billing service invoice")
        assert res is not None
        assert res.matched_subsystem_id == "billing"
        assert "src/billing/service.py" in res.entrypoints
        assert "tests/test_billing.py" in res.covering_tests

        card = engine.format_locator_card(res)
        assert "Subsystem:   billing" in card
        assert "Entrypoints: src/billing/service.py" in card


def test_phase27_e2e_03_changeset_doc_audit_integration_clean():
    """Modifying code, test, and clean doc passes Same Change Set with doc reference verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_integration_repo(tmpdir)
        policy = ChangesetPolicy(
            require_tests_on_code_change=True,
            require_docs_on_code_change=True,
            audit_documentation_references=True,
        )

        files = [
            "src/billing/service.py",
            "tests/test_billing.py",
            "docs/billing.md",
        ]
        cs_eval = evaluate_changeset(tmpdir, policy=policy, changed_files=files)
        assert cs_eval.is_valid is True
        assert cs_eval.violations == []


def test_phase27_e2e_04_changeset_doc_audit_catches_dead_references():
    """Modifying documentation with dead links fails Same Change Set evaluation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_integration_repo(tmpdir)
        docs_dir = os.path.join(tmpdir, "docs")
        broken_doc = os.path.join(docs_dir, "broken.md")
        with open(broken_doc, "w") as f:
            f.write("# Dead Link Doc\nRefers to non-existent `src/billing/ghost.py`.\n")

        policy = ChangesetPolicy(
            require_tests_on_code_change=True,
            require_docs_on_code_change=True,
            audit_documentation_references=True,
        )

        files = [
            "src/billing/service.py",
            "tests/test_billing.py",
            "docs/broken.md",
        ]
        cs_eval = evaluate_changeset(tmpdir, policy=policy, changed_files=files)
        assert cs_eval.is_valid is False
        assert any("Documentation Reference Drift" in v for v in cs_eval.violations)


def test_phase27_e2e_05_stop_gate_blocks_on_doc_drift():
    """Stop Gate ratchet rejects task completion if working tree has documentation drift."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _setup_integration_repo(tmpdir)
        docs_dir = os.path.join(tmpdir, "docs")
        broken_doc = os.path.join(docs_dir, "broken_ref.md")
        with open(broken_doc, "w") as f:
            f.write("Broken reference: `src/nonexistent/fake_file.py`\n")

        config = AntiOSConfig(
            policies=PoliciesConfig(
                fail_closed=True,
                enforce_working_tree_cleanliness=False,
                enforce_same_change_set=True,
            ),
            changeset=ChangesetPolicy(
                require_tests_on_code_change=False,
                require_docs_on_code_change=False,
                audit_documentation_references=True,
            ),
        )

        hook_input = {
            "workspacePaths": [tmpdir],
            "touched_files": ["docs/broken_ref.md"],
        }
        decision, reason = evaluate_stop_gate(hook_input, config=config)
        assert decision == "continue"
        assert "Documentation Reference Drift" in reason
