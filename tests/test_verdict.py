"""Tests for framework.core.verdict."""


from framework.core.verdict import TestResult, VerificationVerdict, format_verdict, parse_verdict


def test_parse_valid_json_verdict():
    raw_json = """
    {
      "status": "PASS",
      "risk_tier": "HIGH",
      "files_audited": ["app/main.ts"],
      "tests": [
        {"command": "npm run vitest:once", "exit_code": 0, "passed": true, "details": "all passed"}
      ],
      "same_change_set_verified": true,
      "summary": "Fix verified cleanly.",
      "issues": []
    }
    """
    v = parse_verdict(raw_json)
    assert v.status == "PASS"
    assert v.risk_tier == "HIGH"
    assert len(v.files_audited) == 1
    assert len(v.tests) == 1
    assert v.tests[0].exit_code == 0
    assert v.same_change_set_verified is True
    assert v.summary == "Fix verified cleanly."
    assert len(v.issues) == 0


def test_parse_fenced_markdown_verdict():
    raw_text = """
    The verifier completed its check.
    ```json
    {
      "status": "FAIL",
      "risk_tier": "MEDIUM",
      "files_audited": ["app/auth.ts"],
      "tests": [
        {"command": "pytest", "exit_code": 1, "passed": false, "details": "auth test failed"}
      ],
      "same_change_set_verified": false,
      "summary": "Auth regression detected.",
      "issues": ["Test failed with exit code 1", "docs/AGENTS.md was not updated"]
    }
    ```
    Please address these issues.
    """
    v = parse_verdict(raw_text)
    assert v.status == "FAIL"
    assert v.risk_tier == "MEDIUM"
    assert v.same_change_set_verified is False
    assert len(v.issues) == 2


def test_parse_fallback_on_unformatted_text():
    text_pass = "I inspected everything and the verdict: PASS. All tests succeeded."
    v_pass = parse_verdict(text_pass)
    assert v_pass.status == "PASS"

    text_fail = "The build failed. verdict: FAIL."
    v_fail = parse_verdict(text_fail)
    assert v_fail.status == "FAIL"

    text_corrupt = "I don't know what happened."
    v_corrupt = parse_verdict(text_corrupt)
    assert v_corrupt.status == "BLOCK"


def test_format_verdict():
    v = VerificationVerdict(
        status="PASS",
        risk_tier="LOW",
        summary="Documentation typo fixed.",
        same_change_set_verified=True
    )
    formatted = format_verdict(v)
    assert formatted.startswith("```json")
    assert '"status": "PASS"' in formatted
