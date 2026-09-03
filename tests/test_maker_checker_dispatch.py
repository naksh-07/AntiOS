"""Tests for Maker-Checker dispatch, context construction, and verdict evaluation."""

from framework.core.verdict import (
    ResultItem,
    VerificationVerdict,
    prepare_checker_context,
    evaluate_checker_verdict,
    parse_verdict,
)
from framework.core.lifecycle import RiskTier


def test_prepare_checker_context_minimal_and_bounded():
    """Verify context construction is noise-free, minimal, and enforces shallow depth law."""
    ctx = prepare_checker_context(
        task_id="TASK-42",
        objective="Fix memory leak in parser",
        risk_tier="HIGH",
        changed_files=["src/parser.py"],
        test_commands=["python -m pytest tests/test_parser.py"],
        target_member="core",
        affected_dependents=["cli"],
        protected_zones=[".agents", "framework"],
    )

    assert ctx["task_id"] == "TASK-42"
    assert ctx["role"] == "INDEPENDENT_VERIFIER"
    assert ctx["risk_tier"] == "HIGH"
    assert ctx["target_member"] == "core"
    assert "cli" in ctx["affected_dependents"]
    assert "src/parser.py" in ctx["changed_files"]
    assert "shallow_depth_law" in ctx["invariants"]
    assert "physical_execution" in ctx["invariants"]
    assert "boundary_defense" in ctx["invariants"]
    assert "same_change_set" in ctx["invariants"]


def test_evaluate_checker_verdict_pass():
    """Valid PASS verdict with executed tests passes evaluation."""
    v = VerificationVerdict(
        status="PASS",
        risk_tier="HIGH",
        files_audited=["src/parser.py"],
        tests=[ResultItem(command="pytest", exit_code=0, passed=True, details="OK")],
        same_change_set_verified=True,
        summary="Verified cleanly",
    )
    ok, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert ok is True
    assert "approved" in reason.lower()


def test_evaluate_checker_verdict_fail():
    """FAIL verdict is rejected with actionable issue details."""
    v = VerificationVerdict(
        status="FAIL",
        risk_tier="HIGH",
        files_audited=["src/parser.py"],
        tests=[ResultItem(command="pytest", exit_code=1, passed=False, details="AssertionError")],
        same_change_set_verified=True,
        summary="Tests failed",
        issues=["AssertionError in test_parser_bounds"],
    )
    ok, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert ok is False
    assert "rejected" in reason.lower()
    assert "AssertionError" in reason


def test_evaluate_checker_verdict_block():
    """BLOCK verdict fails closed."""
    v = VerificationVerdict(
        status="BLOCK",
        risk_tier="HIGH",
        files_audited=[],
        tests=[],
        issues=["Protected zone .agents/ was modified by Maker"],
    )
    ok, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert ok is False
    assert "blocked" in reason.lower()


def test_evaluate_checker_verdict_same_change_set_violation():
    """Passing tests but failing same change set rejects verification."""
    v = VerificationVerdict(
        status="PASS",
        risk_tier="MEDIUM",
        files_audited=["src/app.py"],
        tests=[ResultItem(command="pytest", exit_code=0, passed=True)],
        same_change_set_verified=False,
        issues=["docs/ACTIVE_CONTEXT.md was not updated"],
    )
    ok, reason = evaluate_checker_verdict(v, required_risk_tier="MEDIUM")
    assert ok is False
    assert "same change set" in reason.lower()


def test_evaluate_checker_verdict_missing_tests_for_high_risk():
    """HIGH risk tasks cannot pass with zero physical test results."""
    v = VerificationVerdict(
        status="PASS",
        risk_tier="HIGH",
        files_audited=["src/security.py"],
        tests=[],  # Zero tests run
        same_change_set_verified=True,
    )
    ok, reason = evaluate_checker_verdict(v, required_risk_tier="HIGH")
    assert ok is False
    assert "requires at least one executed physical test" in reason


def test_verdict_is_current_validates_clean_repo():
    """is_current returns True when working tree is clean and fingerprints match."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        v = VerificationVerdict(
            status="PASS",
            risk_tier="LOW",
            git_head="abcdef123456",
            manifest_fingerprint="sha256_mock_hash",
        )
        is_cur, reasons = v.is_current(
            repo_root=tmpdir,
            current_manifest_fingerprint="sha256_mock_hash",
            current_git_head="abcdef123456"
        )
        assert is_cur is True
        assert len(reasons) == 0


def test_verdict_is_current_invalidated_by_drift():
    """is_current returns False when manifest fingerprint drifts or HEAD moves."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        v = VerificationVerdict(
            status="PASS",
            risk_tier="LOW",
            git_head="commit_1",
            manifest_fingerprint="fingerprint_1",
        )
        # Fingerprint drift
        is_cur, reasons = v.is_current(
            repo_root=tmpdir,
            current_manifest_fingerprint="fingerprint_2",
            current_git_head="commit_1"
        )
        assert is_cur is False
        assert any("manifest" in r.lower() for r in reasons)

        # HEAD advancement
        is_cur, reasons = v.is_current(
            repo_root=tmpdir,
            current_manifest_fingerprint="fingerprint_1",
            current_git_head="commit_2"
        )
        assert is_cur is False
        assert any("git head" in r.lower() for r in reasons)
