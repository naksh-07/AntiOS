"""Tests for framework.core.memory."""

import os
import tempfile

from framework.core.memory import (
    MemoryCategory,
    MEMORY_CATEGORY_DOCS,
    KnowledgeAuthority,
    AUTHORITY_WEIGHTS,
    MemoryRecord,
    ProjectKnowledgeFact,
    DecisionRecord,
    LessonRecord,
    HistoricalRecord,
    MemoryWritePolicy,
    format_project_knowledge,
    parse_project_knowledge,
    sync_project_knowledge,
    format_lessons,
    parse_lessons,
    sync_lessons,
    format_historical_record,
    parse_historical_record,
    sync_historical_record,
    format_decision_register,
    parse_decision_register,
    sync_decision_register,
)


def test_memory_categories_and_docs():
    expected_categories = {
        "ACTIVE_STATE",
        "PROJECT_KNOWLEDGE",
        "DECISIONS",
        "LESSONS",
        "HISTORICAL_RECORD",
    }
    actual_categories = {c.value for c in MemoryCategory}
    assert actual_categories == expected_categories

    assert MEMORY_CATEGORY_DOCS[MemoryCategory.ACTIVE_STATE] == "docs/ACTIVE_CONTEXT.md"
    assert MEMORY_CATEGORY_DOCS[MemoryCategory.PROJECT_KNOWLEDGE] == "docs/PROJECT_KNOWLEDGE.md"
    assert MEMORY_CATEGORY_DOCS[MemoryCategory.DECISIONS] == "DECISION_REGISTER.md"
    assert MEMORY_CATEGORY_DOCS[MemoryCategory.LESSONS] == "docs/LESSONS.md"
    assert MEMORY_CATEGORY_DOCS[MemoryCategory.HISTORICAL_RECORD] == "docs/HISTORICAL_RECORD.md"


def test_knowledge_authority_and_weights():
    expected_authorities = {"OBSERVED", "CANDIDATE", "VALIDATED", "DURABLE"}
    actual_authorities = {a.value for a in KnowledgeAuthority}
    assert actual_authorities == expected_authorities

    assert AUTHORITY_WEIGHTS[KnowledgeAuthority.OBSERVED] == 1.0
    assert AUTHORITY_WEIGHTS[KnowledgeAuthority.CANDIDATE] == 0.3
    assert AUTHORITY_WEIGHTS[KnowledgeAuthority.VALIDATED] == 0.8
    assert AUTHORITY_WEIGHTS[KnowledgeAuthority.DURABLE] == 1.0


def test_write_policy_ephemeral_rejection():
    # Ephemeral observations MUST be rejected from durable categories
    durable_cats = [
        MemoryCategory.PROJECT_KNOWLEDGE,
        MemoryCategory.DECISIONS,
        MemoryCategory.LESSONS,
        MemoryCategory.HISTORICAL_RECORD,
    ]
    for cat in durable_cats:
        ok, msg = MemoryWritePolicy.can_write(cat, KnowledgeAuthority.VALIDATED, is_ephemeral=True)
        assert ok is False
        assert "Ephemeral" in msg

    # Ephemeral observations ARE allowed in ACTIVE_STATE
    ok, msg = MemoryWritePolicy.can_write(MemoryCategory.ACTIVE_STATE, KnowledgeAuthority.CANDIDATE, is_ephemeral=True)
    assert ok is True


def test_write_policy_candidate_rejection_in_project_knowledge_and_decisions():
    # CANDIDATE facts cannot be written directly to PROJECT_KNOWLEDGE
    ok, msg = MemoryWritePolicy.can_write(MemoryCategory.PROJECT_KNOWLEDGE, KnowledgeAuthority.CANDIDATE, is_ephemeral=False)
    assert ok is False
    assert "CANDIDATE" in msg

    # VALIDATED / DURABLE / OBSERVED facts can be written to PROJECT_KNOWLEDGE
    for auth in [KnowledgeAuthority.VALIDATED, KnowledgeAuthority.DURABLE, KnowledgeAuthority.OBSERVED]:
        ok, _ = MemoryWritePolicy.can_write(MemoryCategory.PROJECT_KNOWLEDGE, auth, is_ephemeral=False)
        assert ok is True

    # CANDIDATE facts cannot be written directly to DECISIONS
    ok, msg = MemoryWritePolicy.can_write(MemoryCategory.DECISIONS, KnowledgeAuthority.CANDIDATE, is_ephemeral=False)
    assert ok is False
    assert "CANDIDATE" in msg

    # VALIDATED / DURABLE can be written to DECISIONS
    ok, _ = MemoryWritePolicy.can_write(MemoryCategory.DECISIONS, KnowledgeAuthority.DURABLE, is_ephemeral=False)
    assert ok is True

    # CANDIDATE facts cannot be written directly to HISTORICAL_RECORD
    ok, msg = MemoryWritePolicy.can_write(MemoryCategory.HISTORICAL_RECORD, KnowledgeAuthority.CANDIDATE, is_ephemeral=False)
    assert ok is False
    assert "CANDIDATE" in msg


def test_write_policy_lessons_candidate_vs_durable_sections():
    # CANDIDATE allowed in Candidate Improvements section
    ok, _ = MemoryWritePolicy.can_write(
        MemoryCategory.LESSONS,
        KnowledgeAuthority.CANDIDATE,
        is_ephemeral=False,
        target_section="Candidate Improvements",
    )
    assert ok is True

    # CANDIDATE rejected from Durable Lessons section
    ok, msg = MemoryWritePolicy.can_write(
        MemoryCategory.LESSONS,
        KnowledgeAuthority.CANDIDATE,
        is_ephemeral=False,
        target_section="Durable Lessons",
    )
    assert ok is False
    assert "VALIDATED or DURABLE" in msg

    # VALIDATED allowed in Durable Lessons section
    ok, _ = MemoryWritePolicy.can_write(
        MemoryCategory.LESSONS,
        KnowledgeAuthority.VALIDATED,
        is_ephemeral=False,
        target_section="Durable Lessons",
    )
    assert ok is True


def test_lesson_record_promotion():
    lesson = LessonRecord(
        lesson_id="L-01",
        title="Path case sensitivity on Windows",
        trigger_or_failure="test_adapter assertion failed on drive letter casing",
        rule_or_action="Normalize with Path.resolve() before comparison",
        authority=KnowledgeAuthority.CANDIDATE,
    )
    assert lesson.authority == KnowledgeAuthority.CANDIDATE

    # Promotion to VALIDATED
    lesson.promote_to_durable("Verified on Windows CI run #42", KnowledgeAuthority.VALIDATED)
    assert lesson.authority == KnowledgeAuthority.VALIDATED
    assert "Verified on Windows CI run #42" in lesson.evidence

    # Invalid promotion to CANDIDATE raises ValueError
    raised = False
    try:
        lesson.promote_to_durable("attempt downgrade", KnowledgeAuthority.CANDIDATE)
    except ValueError:
        raised = True
    assert raised is True


def test_authority_progression():
    ok, _ = MemoryWritePolicy.can_promote(KnowledgeAuthority.CANDIDATE, KnowledgeAuthority.VALIDATED)
    assert ok is True

    ok, _ = MemoryWritePolicy.can_promote(KnowledgeAuthority.VALIDATED, KnowledgeAuthority.DURABLE)
    assert ok is True

    # Demotion or same level rejected
    ok, msg = MemoryWritePolicy.can_promote(KnowledgeAuthority.DURABLE, KnowledgeAuthority.CANDIDATE)
    assert ok is False
    assert "must be higher" in msg


def test_project_knowledge_roundtrip():
    facts = [
        ProjectKnowledgeFact(
            fact_id="PK-01",
            topic="Tooling & Environment",
            fact="Python 3.11+ using uv package manager",
            authority=KnowledgeAuthority.OBSERVED,
            source="pyproject.toml",
            last_verified="2026-09-04",
        ),
        ProjectKnowledgeFact(
            fact_id="PK-02",
            topic="Architecture",
            fact="AntiOS follows Three-Tier Mechanism vs Policy separation",
            authority=KnowledgeAuthority.DURABLE,
            source="DECISION 01",
            last_verified="2026-09-04",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = sync_project_knowledge(facts, tmpdir)
        assert os.path.isfile(path)

        recovered = parse_project_knowledge(path)
        assert len(recovered) == 2

        f1 = next(f for f in recovered if f.fact_id == "PK-01")
        assert f1.topic == "Tooling & Environment"
        assert f1.fact == "Python 3.11+ using uv package manager"
        assert f1.authority == KnowledgeAuthority.OBSERVED
        assert f1.source == "pyproject.toml"
        assert f1.last_verified == "2026-09-04"

        f2 = next(f for f in recovered if f.fact_id == "PK-02")
        assert f2.authority == KnowledgeAuthority.DURABLE


def test_lessons_roundtrip():
    lessons = [
        LessonRecord(
            lesson_id="L-01",
            title="Setuptools flat layout discovery",
            trigger_or_failure="Multiple top-level packages discovered when building editable wheel",
            rule_or_action="Use uv run --no-project to execute tests without building packaging wheel",
            authority=KnowledgeAuthority.CANDIDATE,
            evidence="task-12 build failure",
            date="2026-09-04",
            category="Packaging",
        ),
        LessonRecord(
            lesson_id="L-02",
            title="PreToolGuard fail closed",
            trigger_or_failure="Unexpected JSON payload in hook",
            rule_or_action="Block tool execution and log actionable diagnostic message",
            authority=KnowledgeAuthority.DURABLE,
            evidence="Phase 9 security audit",
            date="2026-09-04",
            category="Security",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = sync_lessons(lessons, tmpdir)
        assert os.path.isfile(path)

        recovered = parse_lessons(path)
        assert len(recovered) == 2

        l1 = next(l for l in recovered if l.lesson_id == "L-01")
        assert l1.authority == KnowledgeAuthority.CANDIDATE
        assert "Setuptools" in l1.title
        assert "uv run --no-project" in l1.rule_or_action

        l2 = next(l for l in recovered if l.lesson_id == "L-02")
        assert l2.authority == KnowledgeAuthority.DURABLE
        assert "PreToolGuard" in l2.title


def test_historical_record_roundtrip():
    records = [
        HistoricalRecord(
            record_id="M-01",
            title="Phase 14 Core Decoupling",
            description="Universal core decoupled from domain assumptions",
            date="2026-09-04",
            authority=KnowledgeAuthority.DURABLE,
            artifacts=["ANTIOS_PHASE14_15_REPORT.md"],
            verification_summary="31/31 tests passing",
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = sync_historical_record(records, tmpdir)
        assert os.path.isfile(path)

        recovered = parse_historical_record(path)
        assert len(recovered) == 1
        r = recovered[0]
        assert r.record_id == "M-01"
        assert r.title == "Phase 14 Core Decoupling"
        assert r.authority == KnowledgeAuthority.DURABLE
        assert "ANTIOS_PHASE14_15_REPORT.md" in r.artifacts


def test_decision_register_roundtrip_and_real_file():
    decisions = [
        DecisionRecord(
            decision_id="DECISION 99",
            title="Test Decision",
            decision="Test decision statement",
            evidence="Test evidence",
            alternatives="Test alternatives",
            why_selected="Test why selected",
            consequences="Test consequences",
            reversibility="High",
        )
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        path = sync_decision_register(decisions, tmpdir)
        assert os.path.isfile(path)

        recovered = parse_decision_register(path)
        assert len(recovered) == 1
        d = recovered[0]
        assert d.decision_id == "DECISION 99"
        assert d.title == "Test Decision"
        assert d.decision == "Test decision statement"

    # Test against actual DECISION_REGISTER.md at repo root
    real_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DECISION_REGISTER.md")
    if os.path.isfile(real_path):
        real_decisions = parse_decision_register(real_path)
        assert len(real_decisions) >= 8
        d1 = next(d for d in real_decisions if "01" in d.decision_id)
        assert "Three-Tier Mechanism vs Policy Demarcation" in d1.title
        assert d1.authority == KnowledgeAuthority.DURABLE
