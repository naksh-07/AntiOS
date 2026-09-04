"""Unit tests for AntiOS Phase 28-30 Ownership Derivation Model."""

import os
import tempfile
import unittest

from framework.core.knowledge import OwnershipDeriver, OwnershipResolution


def test_ownership_derivation_from_codeowners_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        gh_dir = os.path.join(tmpdir, ".github")
        os.makedirs(gh_dir, exist_ok=True)
        codeowners_path = os.path.join(gh_dir, "CODEOWNERS")

        with open(codeowners_path, "w", encoding="utf-8") as f:
            f.write(
                "# Global fallback\n"
                "* @core-maintainers\n"
                "\n"
                "# Domain specific\n"
                "src/auth/* @security-team\n"
                "src/billing/* @finance-team\n"
            )

        deriver = OwnershipDeriver(workspace_root=tmpdir)
        deriver.scan()

        auth_owner = deriver.resolve_path("src/auth/service.py")
        assert auth_owner.owner == "@security-team"
        assert auth_owner.source == "CODEOWNERS"
        assert auth_owner.confidence == 0.95

        billing_owner = deriver.resolve_path("src/billing/checkout.py")
        assert billing_owner.owner == "@finance-team"
        assert billing_owner.source == "CODEOWNERS"

        fallback_owner = deriver.resolve_path("misc/helper.py")
        assert fallback_owner.owner == "@core-maintainers"
        assert fallback_owner.source == "CODEOWNERS"


def test_ownership_derivation_from_package_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "packages", "ui")
        os.makedirs(pkg_dir, exist_ok=True)

        with open(os.path.join(pkg_dir, "package.json"), "w", encoding="utf-8") as f:
            f.write('{"name": "@app/ui", "author": "Frontend Team <ui@app.com>"}\n')

        deriver = OwnershipDeriver(workspace_root=tmpdir)
        deriver.scan()

        res = deriver.resolve_path("packages/ui/src/Button.tsx")
        assert res.owner == "Frontend Team <ui@app.com>"
        assert res.source == "MANIFEST"
        assert res.confidence == 0.80


def test_ownership_derivation_from_pyproject_toml():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "pyproject.toml"), "w", encoding="utf-8") as f:
            f.write(
                '[project]\n'
                'name = "my-tool"\n'
                'authors = [{ name = "Python Lead" }]\n'
            )

        deriver = OwnershipDeriver(workspace_root=tmpdir)
        deriver.scan()

        res = deriver.resolve_path("my_tool/cli.py")
        assert res.owner == "Python Lead"
        assert res.source == "MANIFEST"
        assert res.confidence == 0.80


def test_ownership_derivation_from_maintainers_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "MAINTAINERS.md"), "w", encoding="utf-8") as f:
            f.write(
                "# Maintainers\n"
                "- Alice Smith (@alice)\n"
                "- Bob Jones (@bob)\n"
            )

        deriver = OwnershipDeriver(workspace_root=tmpdir)
        deriver.scan()

        res = deriver.resolve_path("src/core/main.py")
        assert res.owner == "Alice Smith"
        assert res.source == "MAINTAINER_FILE"
        assert res.confidence == 0.50


def test_ownership_derivation_unknown_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty repository with no ownership files
        deriver = OwnershipDeriver(workspace_root=tmpdir)
        deriver.scan()

        res = deriver.resolve_path("src/something.py")
        assert res.owner is None
        assert res.source == "UNKNOWN"
        assert res.confidence == 0.0
