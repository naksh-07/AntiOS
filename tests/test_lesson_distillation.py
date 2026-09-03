"""Tests for Cross-Session Lesson Distillation, Deterministic Matching, and Conflict Detection."""

import os
import tempfile

from framework.core.memory import (
    KnowledgeAuthority,
    LessonRecord,
    DeterministicLessonMatcher,
    LessonDistillationEngine,
    format_lessons,
    parse_lessons,
)


def test_normalize_signature_strips_volatile_tokens():
    """Verify volatile addresses, timestamps, file paths, UUIDs, and lines are normalized."""
    raw = (
        "Fatal error at 0x7fff5fbff8a0 in C:\\Users\\Dev\\AntiOs\\src\\auth.py:L142 "
        "uuid=123e4567-e89b-12d3-a456-426614174000 at 2026-09-04T04:00:00Z: connection reset"
    )
    norm = DeterministicLessonMatcher.normalize_signature(raw)
    assert "0x7fff5fbff8a0" not in norm
    assert "<addr>" in norm
    assert "123e4567-e89b-12d3-a456-426614174000" not in norm
    assert "<uuid>" in norm
    assert "<timestamp>" in norm
    assert "<path>" in norm
    assert "connection reset" in norm


def test_semantic_equivalence_matching():
    """Two failure logs with the same root cause and error signature match."""
    err1 = "ModuleNotFoundError: No module named 'yaml' in /home/user/repo/app.py:L20"
    err2 = "ModuleNotFoundError: No module named 'yaml' in C:\\Users\\Worker\\app.py:L45"
    err3 = "SyntaxError: invalid syntax in /home/user/repo/parser.py:L10"

    assert DeterministicLessonMatcher.are_semantically_equivalent(err1, err2) is True
    assert DeterministicLessonMatcher.are_semantically_equivalent(err1, err3) is False


def test_conflict_detection_opposing_rules():
    """Detects conflicting rules for the same problem pattern."""
    lesson_a = LessonRecord(
        lesson_id="L-01",
        title="Subprocess shell flag",
        trigger_or_failure="Subprocess fails on Windows due to shell execution semantics",
        rule_or_action="Always enable shell=True on Windows for subprocess commands",
        authority=KnowledgeAuthority.CANDIDATE,
    )
    lesson_b = LessonRecord(
        lesson_id="L-02",
        title="Subprocess security",
        trigger_or_failure="Subprocess fails on Windows due to shell execution semantics",
        rule_or_action="Always disable shell=True to prevent injection vulnerabilities",
        authority=KnowledgeAuthority.CANDIDATE,
    )

    conflict = DeterministicLessonMatcher.check_conflict(lesson_a, lesson_b)
    assert conflict is not None
    assert "Contradictory directives detected" in conflict


def test_distillation_promotes_recurring_candidate_lessons():
    """Candidate lessons with >= 2 verified recurrences are promoted to VALIDATED/DURABLE."""
    cand = LessonRecord(
        lesson_id="L-10",
        title="Flaky network in CI runner",
        trigger_or_failure="Network socket timeout in test runner",
        rule_or_action="Inject retry wrapper with exponential backoff",
        authority=KnowledgeAuthority.CANDIDATE,
    )

    task_evidence = [
        {
            "task_id": "TASK-101",
            "failure_pattern": "Network socket timeout in test runner at <ADDR>",
            "verdict": "PASS",
            "resolution": "Applied exponential backoff wrapper",
            "category": "",
        },
        {
            "task_id": "TASK-102",
            "failure_pattern": "Network socket timeout in test runner at <ADDR>",
            "verdict": "PASS",
            "resolution": "Applied exponential backoff wrapper",
            "category": "",
        }
    ]

    updated, result = LessonDistillationEngine.distill(
        lessons=[cand],
        task_evidence=task_evidence,
        min_recurrences=2
    )

    assert len(result.promoted_lessons) == 1
    promoted = result.promoted_lessons[0]
    assert promoted.lesson_id == "L-10"
    assert promoted.authority in (KnowledgeAuthority.VALIDATED, KnowledgeAuthority.DURABLE)
    assert promoted.recurrence_count == 2
    assert "TASK-101" in promoted.task_ids
    assert "TASK-102" in promoted.task_ids
    assert promoted.scope != ""
    assert promoted.when_applies != ""
    assert promoted.when_not_applies != ""


def test_distillation_retains_unverified_single_occurrence_candidate():
    """Single occurrence candidates remain in CANDIDATE tier and are not promoted."""
    cand = LessonRecord(
        lesson_id="L-11",
        title="Rare compiler bug",
        trigger_or_failure="Internal compiler error in rustc version 1.70",
        rule_or_action="Pin rust-toolchain to 1.72",
        authority=KnowledgeAuthority.CANDIDATE,
        recurrence_count=1,
    )

    updated, result = LessonDistillationEngine.distill(
        lessons=[cand],
        task_evidence=[],
        min_recurrences=2
    )

    assert len(result.promoted_lessons) == 0
    assert len(result.retained_candidates) == 1
    assert result.retained_candidates[0].authority == KnowledgeAuthority.CANDIDATE


def test_distillation_blocks_conflicting_lesson_promotion():
    """Candidate with conflicting counterpart is quarantined and refused promotion."""
    cand_a = LessonRecord(
        lesson_id="L-20",
        title="Cache behavior A",
        trigger_or_failure="Memory leak in local build cache directory",
        rule_or_action="Always enable local caching",
        authority=KnowledgeAuthority.CANDIDATE,
        recurrence_count=3,
        verified_resolution="Verified resolution",
    )
    cand_b = LessonRecord(
        lesson_id="L-21",
        title="Cache behavior B",
        trigger_or_failure="Memory leak in local build cache directory",
        rule_or_action="Always disable local caching",
        authority=KnowledgeAuthority.CANDIDATE,
        recurrence_count=3,
        verified_resolution="Verified resolution",
    )

    updated, result = LessonDistillationEngine.distill(
        lessons=[cand_a, cand_b],
        min_recurrences=2
    )

    assert len(result.conflicts_detected) > 0
    assert len(result.promoted_lessons) == 0
    assert any("conflict" in r.lower() for r in result.rejected_promotions)


def test_lessons_markdown_roundtrip_with_practical_fields():
    """format_lessons and parse_lessons preserve all utility fields."""
    original = [
        LessonRecord(
            lesson_id="L-30",
            title="Database pool starvation",
            trigger_or_failure="ConnectionPoolTimeoutError under high concurrency",
            rule_or_action="Increase connection pool size to 20",
            authority=KnowledgeAuthority.VALIDATED,
            evidence="Benchmarked in load tests",
            problem_pattern="High concurrency connection exhaustion",
            verified_resolution="Increased pool capacity to 20",
            scope="Database Access Layer",
            when_applies="When concurrency exceeds 50 req/sec",
            when_not_applies="When running in local single-thread test mode",
            recurrence_count=3,
            task_ids=["TASK-01", "TASK-02", "TASK-03"],
        )
    ]

    md = format_lessons(original)
    parsed = parse_lessons(md)

    assert len(parsed) == 1
    p = parsed[0]
    assert p.lesson_id == "L-30"
    assert p.authority == KnowledgeAuthority.VALIDATED
    assert p.problem_pattern == "High concurrency connection exhaustion"
    assert p.scope == "Database Access Layer"
    assert p.when_applies == "When concurrency exceeds 50 req/sec"
    assert p.when_not_applies == "When running in local single-thread test mode"
    assert p.recurrence_count == 3
    assert "TASK-01" in p.task_ids
