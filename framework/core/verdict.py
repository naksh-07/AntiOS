"""AntiOS Maker-Checker Structured Verdict Protocol.

Defines the contract and parser for Independent Verifier subagent reports.
Ensures machine-readable, deterministic pass/fail accounting.
"""

from __future__ import annotations
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ResultItem:
    command: str
    exit_code: int
    passed: bool
    details: str = ""


# Alias for backward compatibility
TestResult = ResultItem


@dataclass
class VerificationVerdict:
    status: str  # "PASS", "FAIL", "BLOCK"
    risk_tier: str  # "LOW", "MEDIUM", "HIGH"
    files_audited: List[str] = field(default_factory=list)
    tests: List[ResultItem] = field(default_factory=list)
    same_change_set_verified: bool = True
    summary: str = ""
    issues: List[str] = field(default_factory=list)
    git_head: Optional[str] = None
    manifest_fingerprint: Optional[str] = None
    adapter_verified: bool = True
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def parse_verdict(raw_text: str) -> VerificationVerdict:
    """Parses a structured verdict from raw verifier text or fenced JSON code block."""
    if not raw_text or not raw_text.strip():
        return VerificationVerdict(
            status="BLOCK",
            risk_tier="HIGH",
            summary="Empty verifier response received",
            issues=["No verdict payload emitted by verifier."]
        )

    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    payload_str = json_match.group(1) if json_match else raw_text.strip()

    try:
        data = json.loads(payload_str)
        if not isinstance(data, dict):
            raise ValueError("Root JSON must be an object")

        raw_status = str(data.get("status", "BLOCK")).upper()
        if raw_status not in ("PASS", "FAIL", "BLOCK"):
            raw_status = "BLOCK"

        raw_tier = str(data.get("risk_tier", "MEDIUM")).upper()
        if raw_tier not in ("LOW", "MEDIUM", "HIGH"):
            raw_tier = "MEDIUM"

        tests = []
        for t in data.get("tests", []):
            if isinstance(t, dict):
                tests.append(
                    ResultItem(
                        command=str(t.get("command", "")),
                        exit_code=int(t.get("exit_code", 0)),
                        passed=bool(t.get("passed", False)),
                        details=str(t.get("details", "")),
                    )
                )

        git_head = data.get("git_head")
        manifest_fingerprint = data.get("manifest_fingerprint")
        adapter_verified = bool(data.get("adapter_verified", True))
        timestamp = data.get("timestamp")

        return VerificationVerdict(
            status=raw_status,
            risk_tier=raw_tier,
            files_audited=[str(f) for f in data.get("files_audited", [])],
            tests=tests,
            same_change_set_verified=bool(data.get("same_change_set_verified", True)),
            summary=str(data.get("summary", "")),
            issues=[str(i) for i in data.get("issues", [])],
            git_head=str(git_head) if git_head else None,
            manifest_fingerprint=str(manifest_fingerprint) if manifest_fingerprint else None,
            adapter_verified=adapter_verified,
            timestamp=str(timestamp) if timestamp else None,
        )

    except Exception as e:
        status = "BLOCK"
        if "VERDICT: PASS" in raw_text.upper():
            status = "PASS"
        elif "VERDICT: FAIL" in raw_text.upper():
            status = "FAIL"

        return VerificationVerdict(
            status=status,
            risk_tier="HIGH",
            summary="Extracted via heuristic fallback",
            issues=[f"Failed to parse formal JSON verdict: {str(e)}"]
        )


def format_verdict(verdict: VerificationVerdict) -> str:
    """Formats a VerificationVerdict into a standardized markdown block."""
    return f"```json\n{verdict.to_json(indent=2)}\n```"