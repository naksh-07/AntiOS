"""AntiOS Minimal Tool Abstraction.

Defines a clean, lightweight abstraction for tool identity, capability tiers,
standardized execution results, structured failure classification, and tool
selection policy without wrapping native Antigravity tools or creating an
artificial agent runtime.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ToolTier(str, Enum):
    """Tier of tool capability under AntiOS tool selection policy."""
    NATIVE = "NATIVE"      # Antigravity native tool (highest priority)
    SCRIPT = "SCRIPT"      # Deterministic local script (framework/scripts/tools/)
    MCP = "MCP"            # Model Context Protocol external server (selective)


class ToolStatus(str, Enum):
    """Standardized tool execution status."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    DENIED = "DENIED"
    TIMEOUT = "TIMEOUT"


class FailureClass(str, Enum):
    """Structured failure taxonomy for tool execution and verification."""
    NONE = "NONE"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    TIMEOUT = "TIMEOUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    POLICY_DENIED = "POLICY_DENIED"
    ENVIRONMENT_MISSING = "ENVIRONMENT_MISSING"
    EXECUTION_FAILED = "EXECUTION_FAILED"


@dataclass(frozen=True)
class ToolIdentity:
    """Identity and metadata for an executable tool capability."""
    tool_id: str
    name: str
    tier: ToolTier
    description: str
    entrypoint: str
    applicable_platforms: List[str] = field(default_factory=lambda: ["win32", "linux", "darwin"])
    requires_network: bool = False
    is_deterministic: bool = True


@dataclass
class ToolResult:
    """Standardized result emitted by tool executions."""
    status: ToolStatus
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    data: Optional[Dict[str, Any]] = None
    failure_class: FailureClass = FailureClass.NONE
    failure_reason: Optional[str] = None
    evidence: List[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status == ToolStatus.SUCCESS and self.exit_code == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "data": self.data or {},
            "failure_class": self.failure_class.value,
            "failure_reason": self.failure_reason,
            "evidence": self.evidence,
        }

    @classmethod
    def success(cls, stdout: str = "", data: Optional[Dict[str, Any]] = None, evidence: Optional[List[str]] = None) -> ToolResult:
        return cls(
            status=ToolStatus.SUCCESS,
            exit_code=0,
            stdout=stdout,
            data=data or {},
            evidence=evidence or [],
        )

    @classmethod
    def failure(
        cls,
        failure_class: FailureClass,
        reason: str,
        exit_code: int = 1,
        stdout: str = "",
        stderr: str = "",
        evidence: Optional[List[str]] = None,
    ) -> ToolResult:
        return cls(
            status=ToolStatus.FAILURE,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            failure_class=failure_class,
            failure_reason=reason,
            evidence=evidence or [],
        )

    @classmethod
    def denied(cls, reason: str, evidence: Optional[List[str]] = None) -> ToolResult:
        return cls(
            status=ToolStatus.DENIED,
            exit_code=126,
            failure_class=FailureClass.POLICY_DENIED,
            failure_reason=reason,
            evidence=evidence or [],
        )

    @classmethod
    def timeout(cls, seconds: int, evidence: Optional[List[str]] = None) -> ToolResult:
        return cls(
            status=ToolStatus.TIMEOUT,
            exit_code=124,
            failure_class=FailureClass.TIMEOUT,
            failure_reason=f"Tool execution timed out after {seconds} seconds",
            evidence=evidence or [],
        )


class ToolSelectionPolicy:
    """AntiOS 3-Tier Tool Selection Policy:
    
    1. Prefer Antigravity native capability.
    2. If unavailable, prefer a deterministic local script.
    3. Use MCP only when a separate process/tool protocol gives meaningful capability.
    """

    @staticmethod
    def select_tool_tier(has_native: bool, has_script: bool, mcp_justified: bool) -> ToolTier:
        if has_native:
            return ToolTier.NATIVE
        if has_script:
            return ToolTier.SCRIPT
        if mcp_justified:
            return ToolTier.MCP
        return ToolTier.SCRIPT
