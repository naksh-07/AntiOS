"""Unit tests for AntiOS Phase 28-30 Documentation as Agent Infrastructure."""

import os
import tempfile
import unittest

from framework.core.knowledge import DocCategory, DocKnowledgeClassifier, DocArtifactFact
from framework.core.docaudit import audit_documentation_references


def test_doc_knowledge_classifier_categories():
    assert DocKnowledgeClassifier.classify_file("AGENTS.md") == DocCategory.AUTHORITATIVE
    assert DocKnowledgeClassifier.classify_file("ANTIOS_CONSTITUTION.md") == DocCategory.AUTHORITATIVE
    assert DocKnowledgeClassifier.classify_file("docs/architecture/overview.md") == DocCategory.ARCHITECTURE
    assert DocKnowledgeClassifier.classify_file("docs/adr/0001-sqlite.md") == DocCategory.ARCHITECTURE
    assert DocKnowledgeClassifier.classify_file("docs/subsystems/auth.md") == DocCategory.COMPONENT
    assert DocKnowledgeClassifier.classify_file("docs/setup/install.md") == DocCategory.SETUP
    assert DocKnowledgeClassifier.classify_file("docs/testing/harness.md") == DocCategory.TESTING
    assert DocKnowledgeClassifier.classify_file("CONTRIBUTING.md") == DocCategory.CONTRIBUTION
    assert DocKnowledgeClassifier.classify_file("docs/random_notes.md") == DocCategory.GENERAL


def test_doc_knowledge_audit_integration_clean():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = os.path.join(tmpdir, "src", "service.py")
        os.makedirs(os.path.dirname(src_file), exist_ok=True)
        with open(src_file, "w") as f:
            f.write("def run(): pass\n")

        doc_file = os.path.join(tmpdir, "docs", "arch.md")
        os.makedirs(os.path.dirname(doc_file), exist_ok=True)
        with open(doc_file, "w") as f:
            f.write("# Architecture\nCore code is in `src/service.py`.\n")

        audit_res = audit_documentation_references(doc_file, tmpdir)
        assert audit_res.is_clean
        assert audit_res.broken_count == 0
        assert audit_res.valid_count == 1

        cat = DocKnowledgeClassifier.classify_file("docs/arch.md")
        fact = DocArtifactFact(
            path="docs/arch.md",
            category=cat,
            is_authoritative=False,
            is_clean=audit_res.is_clean,
            broken_references_count=audit_res.broken_count,
            covering_subsystems=["core"],
        )
        assert fact.category == DocCategory.ARCHITECTURE
        assert fact.is_clean


def test_doc_knowledge_audit_integration_broken_stale_reference():
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_file = os.path.join(tmpdir, "docs", "stale.md")
        os.makedirs(os.path.dirname(doc_file), exist_ok=True)
        with open(doc_file, "w") as f:
            f.write("# Stale Doc\nReferences missing `src/deleted_old_file.py`.\n")

        audit_res = audit_documentation_references(doc_file, tmpdir)
        assert not audit_res.is_clean
        assert audit_res.broken_count == 1
