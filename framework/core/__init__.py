"""AntiOS v1 Core Framework Package.

This package provides the governance and capability primitives for AntiOS:
- config: Declarative adapter configuration and defaults
- guard: Deterministic path protection and boundary enforcement
- gate: Dynamic test runner execution and verification ratchets
- verdict: Structured verifier verdict data model and parsing
"""

from framework.core.config import AntiOSConfig, load_config
from framework.core.guard import evaluate_tool_call
from framework.core.gate import evaluate_stop_gate
from framework.core.verdict import VerificationVerdict, parse_verdict, format_verdict

__all__ = [
    "AntiOSConfig",
    "load_config",
    "evaluate_tool_call",
    "evaluate_stop_gate",
    "VerificationVerdict",
    "parse_verdict",
    "format_verdict",
]
