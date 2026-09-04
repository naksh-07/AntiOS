"""Unit tests for Staleguard Layer 1 Syntactic Documentation Reference Auditor."""

import os
import shutil
import tempfile

from framework.core.docaudit import (
    DocReference,
    DocAuditResult,
    extract_references_from_text,
    audit_documentation_references,
    audit_all_documentation,
)


def test_docaudit_extract_references_from_text():
    sample_doc = (
        "# App Overview\n"
        "Entrypoint is located at `src/app.py`.\n"
        "See [Test Suite](tests/test_app.py) or external [Python Docs](https://python.org).\n"
        "Run test suite via `pytest tests/test_app.py`.\n"
    )
    refs = extract_references_from_text(sample_doc)
    paths = [r[2] for r in refs]
    assert "src/app.py" in paths
    assert "tests/test_app.py" in paths
    assert "https://python.org" not in paths


def test_docaudit_clean_documentation_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        src_dir = os.path.join(tmpdir, "src")
        tests_dir = os.path.join(tmpdir, "tests")
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(tests_dir, exist_ok=True)

        with open(os.path.join(src_dir, "app.py"), "w") as f:
            f.write("# App code\n")
        with open(os.path.join(tests_dir, "test_app.py"), "w") as f:
            f.write("# Test code\n")

        doc_path = os.path.join(docs_dir, "README.md")
        with open(doc_path, "w") as f:
            f.write(
                "# System Guide\n"
                "The core module is `src/app.py`.\n"
                "Tests are executed with `pytest tests/test_app.py`.\n"
                "Relative link: [App Code](../src/app.py)\n"
            )

        res = audit_documentation_references(doc_path, tmpdir)
        assert res.is_clean is True
        assert res.broken_count == 0
        assert res.valid_count >= 2


def test_docaudit_broken_reference_detection():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir, exist_ok=True)

        doc_path = os.path.join(docs_dir, "BROKEN.md")
        with open(doc_path, "w") as f:
            f.write(
                "# Broken Guide\n"
                "The imaginary module is `src/ghost_module.py`.\n"
                "Dead link: [Missing Guide](docs/missing_guide.md)\n"
                "Dead test: `pytest tests/test_ghost.py`\n"
            )

        res = audit_documentation_references(doc_path, tmpdir)
        assert res.is_clean is False
        assert res.broken_count == 3

        broken_targets = [r.target_path for r in res.references if not r.is_valid]
        assert "src/ghost_module.py" in broken_targets
        assert "docs/missing_guide.md" in broken_targets
        assert "tests/test_ghost.py" in broken_targets


def test_docaudit_nonexistent_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        res = audit_documentation_references("docs/nonexistent.md", tmpdir)
        assert res.is_clean is False
        assert res.broken_count == 1


def test_docaudit_all_documentation():
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_dir = os.path.join(tmpdir, "docs")
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)

        with open(os.path.join(src_dir, "app.py"), "w") as f:
            f.write("# App\n")

        doc1 = os.path.join(docs_dir, "doc1.md")
        with open(doc1, "w") as f:
            f.write("Valid ref: `src/app.py`\n")

        doc2 = os.path.join(docs_dir, "doc2.md")
        with open(doc2, "w") as f:
            f.write("Invalid ref: `src/invalid_file.ts`\n")

        all_results = audit_all_documentation(tmpdir, target_dirs=["docs"])
        assert len(all_results) == 2

        doc1_rel = os.path.relpath(doc1, tmpdir)
        doc2_rel = os.path.relpath(doc2, tmpdir)

        assert all_results[doc1_rel].is_clean is True
        assert all_results[doc2_rel].is_clean is False
