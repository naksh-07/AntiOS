"""AntiOS Canonical Tool Selection Policy & MCP Justification Authority.

Implements:
1. Canonical MCP Justification Authority (answers the 8 canonical questions)
2. Strict 6-Tier Tool Preference:
   NATIVE (1) -> SCRIPT (2) -> PROJECT (3) -> EXTERNAL (4) -> SERVICE (5) -> MCP (6)
3. Tool Authorization Enforcement against AgentCapabilityBoundary
4. Offline / Degraded Execution Resolution
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from framework.core.tool import (
    Locality,
    ProviderAvailability,
    ToolDefinition,
    ToolPolicyStatus,
    ToolTier,
)
from framework.core.provider import (
    ProviderDefinition,
    ProviderPolicyStatus,
    ProviderType,
)
from framework.core.tool_registry import ToolRegistry


@dataclass
class MCPJustificationReport:
    """Answers the 8 canonical MCP justification questions."""
    provider_id: str
    status: str  # NOT_NEEDED, USEFUL, OPTIONAL, REJECTED, UNAVAILABLE
    is_needed: bool = False
    is_permitted: bool = False
    why: str = ""
    local_alternatives: List[str] = field(default_factory=list)
    why_insufficient: str = ""
    fallback: str = ""
    on_unavailable: str = "FAIL_CLOSED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "is_needed": self.is_needed,
            "is_permitted": self.is_permitted,
            "why": self.why,
            "local_alternatives": list(self.local_alternatives),
            "why_insufficient": self.why_insufficient,
            "fallback": self.fallback,
            "on_unavailable": self.on_unavailable,
        }


class MCPJustificationEngine:
    """Canonical, single source of truth for MCP selection and justification in AntiOS."""

    REJECTED_PROVIDERS = {
        "provider:notion": "Notion MCP is out of scope for agent engineering runtime",
        "provider:postman": "Postman MCP is redundant with native curl and deterministic test scripts",
        "provider:posthog": "PostHog analytics MCP is out of scope for agent engineering runtime",
        "provider:unauthorized-external-mcp": "Unauthorized external MCP is strictly forbidden",
    }

    @classmethod
    def evaluate(
        cls,
        task_intent: str,
        capability_id: Any,
        target_files: Optional[List[str]] = None,
        registry: Optional[ToolRegistry] = None,
    ) -> MCPJustificationReport:
        """Evaluate task intent and capability to answer the 8 canonical MCP questions."""
        intent_lower = (task_intent or "").lower()
        if isinstance(capability_id, dict):
            cap_id_str = capability_id.get("capability_id", str(capability_id))
        else:
            cap_id_str = str(capability_id or "")
        cap_lower = cap_id_str.lower()
        target_files = target_files or []

        # 1. Check for explicitly rejected MCP candidates
        for rej_id, reason in cls.REJECTED_PROVIDERS.items():
            short_name = rej_id.replace("provider:", "")
            if short_name in intent_lower or short_name in cap_lower:
                return MCPJustificationReport(
                    provider_id=rej_id,
                    status="REJECTED",
                    is_needed=False,
                    is_permitted=False,
                    why=f"REJECTED: {reason}",
                    local_alternatives=["tool:native-run-command", "tool:navigate-repo"],
                    why_insufficient="Not applicable; provider is untrusted or out of scope.",
                    fallback="NONE",
                    on_unavailable="FAIL_CLOSED",
                )

        # 2. Local Git Operations: STRICT ENFORCEMENT of Native Git > GitHub MCP
        git_local_tokens = ["git status", "git diff", "git log", "git branch", "working tree", "local commit"]
        if any(tok in intent_lower for tok in git_local_tokens) or "git:status" in cap_lower or "git:diff" in cap_lower:
            return MCPJustificationReport(
                provider_id="provider:github",
                status="NOT_NEEDED",
                is_needed=False,
                is_permitted=False,
                why="Local Git CLI is authoritative, 100% offline, zero tokens, and executes in <50ms. GitHub MCP is strictly forbidden for local repository inspection.",
                local_alternatives=["tool:native-git-cli", "tool:external-git"],
                why_insufficient="Local Git CLI is strictly superior to GitHub MCP for all local operations.",
                fallback="tool:external-git",
                on_unavailable="CONTINUE_LOCAL_CLI",
            )

        # 3. Local file inspection / repository wayfinding
        local_inspect_tokens = ["read file", "view file", "inspect file", "find symbol", "navigate", "grep", "repo structure"]
        if any(tok in intent_lower for tok in local_inspect_tokens) or "wayfinding" in cap_lower or "file:read" in cap_lower:
            return MCPJustificationReport(
                provider_id="none",
                status="NOT_NEEDED",
                is_needed=False,
                is_permitted=False,
                why="Local Antigravity native tools and deterministic scripts fully satisfy repository inspection without external transport.",
                local_alternatives=["tool:native-view-file", "tool:native-grep-search", "tool:navigate-repo"],
                why_insufficient="Native tools are zero-latency and 100% accurate on disk.",
                fallback="tool:native-view-file",
                on_unavailable="FAIL_CLOSED",
            )

        # 4. Remote GitHub PR Management
        pr_tokens = ["create pr", "create pull request", "open pr", "merge pr", "github pr", "remote pr"]
        if any(tok in intent_lower for tok in pr_tokens) or "github:create-pull-request" in cap_lower:
            # Check availability if registry provided
            avail = True
            if registry:
                p = registry.get_provider("provider:github")
                if p and p.availability != ProviderAvailability.AVAILABLE:
                    avail = False

            if not avail:
                return MCPJustificationReport(
                    provider_id="provider:github",
                    status="UNAVAILABLE",
                    is_needed=True,
                    is_permitted=True,
                    why="Remote GitHub PR creation requires GitHub API transport, but provider is currently UNAVAILABLE.",
                    local_alternatives=["tool:native-git-cli (prepares local branch/commit only)"],
                    why_insufficient="Local Git cannot create remote pull requests on github.com.",
                    fallback="NONE",
                    on_unavailable="FAIL_CLOSED",
                )

            return MCPJustificationReport(
                provider_id="provider:github",
                status="OPTIONAL",
                is_needed=True,
                is_permitted=True,
                why="GitHub remote PR operations cannot be performed locally; remote API transport is justified for PR creation after local preparation.",
                local_alternatives=["tool:native-git-cli (prepares local branch/commit only)"],
                why_insufficient="Local Git cannot create remote pull requests on github.com without remote API transport.",
                fallback="NONE",
                on_unavailable="FAIL_CLOSED",
            )

        # 5. Live Browser DOM / Accessibility Layout Inspection
        dom_tokens = ["dom", "browser layout", "accessibility tree", "a11y", "chrome devtools", "css inspection", "inspect browser"]
        if any(tok in intent_lower for tok in dom_tokens) or "browser:dom" in cap_lower or "browser:a11y" in cap_lower:
            avail = True
            if registry:
                p = registry.get_provider("provider:chrome-devtools")
                if p and p.availability != ProviderAvailability.AVAILABLE:
                    avail = False

            if not avail:
                return MCPJustificationReport(
                    provider_id="provider:chrome-devtools",
                    status="UNAVAILABLE",
                    is_needed=True,
                    is_permitted=True,
                    why="Browser DOM and accessibility layout inspection require Chrome DevTools, but provider is UNAVAILABLE.",
                    local_alternatives=["tool:native-view-file (inspects raw HTML template only)"],
                    why_insufficient="Static HTML files do not reflect computed CSS layout, active JavaScript DOM mutations, or rendered a11y trees.",
                    fallback="NONE",
                    on_unavailable="FAIL_CLOSED",
                )

            return MCPJustificationReport(
                provider_id="provider:chrome-devtools",
                status="USEFUL",
                is_needed=True,
                is_permitted=True,
                why="Chrome DevTools provides live computed styles, DOM nodes, and rendered accessibility tree inspection unavailable via static source tools.",
                local_alternatives=["tool:native-view-file (inspects raw HTML template only)"],
                why_insufficient="Static HTML files do not reflect computed CSS layout, active JavaScript DOM mutations, or rendered a11y trees.",
                fallback="NONE",
                on_unavailable="FAIL_CLOSED",
            )

        # 6. Browser E2E Automation
        e2e_tokens = ["playwright", "e2e automation", "browser automation", "click and assert", "headless browser flow"]
        if any(tok in intent_lower for tok in e2e_tokens) or "browser:e2e" in cap_lower:
            return MCPJustificationReport(
                provider_id="provider:playwright",
                status="USEFUL",
                is_needed=True,
                is_permitted=True,
                why="Playwright MCP provides active browser driving, element interaction, and visual snapshots for user flows.",
                local_alternatives=["tool:project-test-runner (if project has local playwright tests installed)"],
                why_insufficient="Command-line scripts without browser runtime cannot perform interactive browser step automation.",
                fallback="tool:project-test-runner",
                on_unavailable="FAIL_CLOSED",
            )

        # 7. Upstream Gemini API / SDK Documentation
        sdk_tokens = ["gemini api docs", "upstream gemini sdk", "gemini documentation", "google-genai docs"]
        if any(tok in intent_lower for tok in sdk_tokens) or "docs:gemini" in cap_lower:
            return MCPJustificationReport(
                provider_id="provider:gemini-api-docs",
                status="USEFUL",
                is_needed=True,
                is_permitted=True,
                why="Authoritative real-time upstream SDK reference search preventing outdated LLM hallucinations.",
                local_alternatives=["tool:native-view-file (for local vendored markdown docs)"],
                why_insufficient="Local repo does not store upstream Google Gemini SDK release documentation.",
                fallback="NONE",
                on_unavailable="FAIL_CLOSED",
            )

        # Default: MCP is NOT needed
        return MCPJustificationReport(
            provider_id="none",
            status="NOT_NEEDED",
            is_needed=False,
            is_permitted=False,
            why="Standard local tools and deterministic scripts satisfy the capability requirement with lower latency and zero remote risk.",
            local_alternatives=["tool:native-run-command", "tool:navigate-repo"],
            why_insufficient="Local tools are sufficient.",
            fallback="NONE",
            on_unavailable="FAIL_CLOSED",
        )


class DeterministicToolSelector:
    """Selects the safest, smallest, most appropriate execution mechanism for a capability."""

    # Preference ranking: lower number = higher preference
    TIER_RANKING = {
        ToolTier.NATIVE: 1,
        ToolTier.SCRIPT: 2,
        ToolTier.PROJECT: 3,
        ToolTier.EXTERNAL: 4,
        ToolTier.MCP: 6,
    }

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def select_tool(
        self,
        task_intent: str,
        capability_id: Any,
        task_class: str = "FEATURE",
        subsystem_id: str = "*",
        agent_role: Optional[Any] = None,
        target_files: Optional[List[str]] = None,
        offline_mode: bool = False,
    ) -> Dict[str, Any]:
        """Execute deterministic tool selection with authorization and availability checks."""
        if isinstance(capability_id, dict):
            capability_id = capability_id.get("capability_id", str(capability_id))
        else:
            capability_id = str(capability_id or "")

        target_files = target_files or []
        mcp_report = MCPJustificationEngine.evaluate(
            task_intent=task_intent,
            capability_id=capability_id,
            target_files=target_files,
            registry=self.registry,
        )

        # 1. Find all candidate tools exposing this capability
        candidates = self.registry.find_tools_by_capability(capability_id, enabled_only=False, available_only=False)

        # If MCP is justified and permitted, include its exposed tools as candidates
        if mcp_report.is_needed and mcp_report.provider_id:
            prov = self.registry.get_provider(mcp_report.provider_id)
            if prov:
                for tid in prov.exposed_tools:
                    t = self.registry.get_tool(tid)
                    if t and t not in candidates:
                        candidates.append(t)

        # If no specific capability match, try task-matching tools
        if not candidates:
            candidates = self.registry.find_tools_by_task_type(task_class, enabled_only=False)

        # Sort candidates according to strict tier hierarchy and availability
        def candidate_sort_key(t: ToolDefinition) -> Tuple[int, int, int]:
            # Enabled first
            enabled_rank = 0 if t.enabled else 1
            # Available first
            avail_rank = 0 if t.availability == ProviderAvailability.AVAILABLE else 1
            # Preference tier
            tier_rank = self.TIER_RANKING.get(t.tier, 99)
            return (enabled_rank, avail_rank, tier_rank)

        sorted_candidates = sorted(candidates, key=candidate_sort_key)

        selected_tool: Optional[ToolDefinition] = None
        selected_provider: Optional[ProviderDefinition] = None
        alternatives_considered: List[Dict[str, Any]] = []
        why_selected = ""
        why_alternatives_rejected: List[str] = []

        # 2. Iterate through sorted candidates and select first permitted & matching
        for cand in sorted_candidates:
            cand_prov = self.registry.get_provider(cand.provider_id)
            alt_info = {
                "tool_id": cand.tool_id,
                "tier": cand.tier.value,
                "provider_id": cand.provider_id,
                "availability": cand.availability.value,
                "enabled": cand.enabled,
            }

            # Check if candidate is explicitly forbidden/rejected
            if not cand.enabled or cand.policy_status == ToolPolicyStatus.FORBIDDEN:
                alt_info["rejected_reason"] = "Tool is disabled or forbidden by policy"
                alternatives_considered.append(alt_info)
                why_alternatives_rejected.append(f"{cand.tool_id}: Disabled/Forbidden by policy")
                continue

            if cand_prov and (not cand_prov.enabled or cand_prov.policy_status == ProviderPolicyStatus.REJECTED):
                alt_info["rejected_reason"] = f"Provider {cand_prov.provider_id} is rejected under ANTIOS_MCP_POLICY.md"
                alternatives_considered.append(alt_info)
                why_alternatives_rejected.append(f"{cand.tool_id}: Provider rejected under AntiOS policy")
                continue

            # If tool is MCP, check MCP justification
            if cand.tier == ToolTier.MCP:
                if not mcp_report.is_needed or not mcp_report.is_permitted:
                    alt_info["rejected_reason"] = f"MCP not justified: {mcp_report.why}"
                    alternatives_considered.append(alt_info)
                    why_alternatives_rejected.append(f"{cand.tool_id}: MCP not justified ({mcp_report.status})")
                    continue

            # If offline mode requested, filter out tools that require network
            if offline_mode and (not cand.offline_capable or (cand_prov and cand_prov.requires_network)):
                alt_info["rejected_reason"] = "Tool requires network connectivity, but offline mode is active"
                alternatives_considered.append(alt_info)
                why_alternatives_rejected.append(f"{cand.tool_id}: Requires network in offline mode")
                continue

            # Candidate selected!
            if selected_tool is None:
                selected_tool = cand
                selected_provider = cand_prov
                why_selected = (
                    f"Selected {cand.name} ({cand.tier.value}) as highest-priority permitted mechanism "
                    f"for capability '{capability_id}'."
                )
            else:
                alt_info["rejected_reason"] = (
                    f"Lower tier ({cand.tier.value}) than selected tool ({selected_tool.tier.value})"
                )
                alternatives_considered.append(alt_info)
                why_alternatives_rejected.append(
                    f"{cand.tool_id}: Lower tier than selected {selected_tool.tool_id}"
                )

        # 3. Tool Authorization Check against Agent Boundary
        auth_status = "AUTHORIZED"
        auth_reason = "Tool execution permitted under active agent governance."

        if selected_tool is not None and agent_role is not None:
            boundary = getattr(agent_role, "boundary", None)
            if boundary is not None:
                # Check capability access via boundary
                is_allowed, reason = boundary.validate_capability_access(capability_id)
                if not is_allowed:
                    auth_status = "BLOCKED"
                    auth_reason = f"Agent boundary violation: {reason}"
                else:
                    # Check if tool itself is forbidden by boundary
                    tool_cap = f"tool:{selected_tool.tool_id.replace('tool:', '')}"
                    t_allowed, t_reason = boundary.validate_capability_access(tool_cap)
                    if not t_allowed:
                        auth_status = "BLOCKED"
                        auth_reason = f"Agent boundary violation: Tool {selected_tool.tool_id} is explicitly forbidden for role {getattr(agent_role, 'role_id', 'unknown')}."

            # Check protected core zones if specialist
            role_type = getattr(agent_role, "role_type", None)
            role_type_val = getattr(role_type, "value", str(role_type))
            if role_type_val in ["SPECIALIST", "CHECKER"]:
                # Specialists are forbidden from mutating protected AntiOS core files
                for tf in target_files:
                    tf_norm = tf.replace("\\", "/").strip("/")
                    if tf_norm.startswith("framework/") or tf_norm.startswith(".agents/") or tf_norm == "antios.config.json":
                        if selected_tool.tool_id in ["tool:native-write-file", "tool:native-replace-content"]:
                            auth_status = "BLOCKED"
                            auth_reason = f"Constitutional Violation: Specialist role {getattr(agent_role, 'role_id', 'unknown')} cannot mutate protected AntiOS file '{tf}'."

        # 4. Handle tool unavailable status
        availability = ProviderAvailability.AVAILABLE
        if selected_tool is not None:
            availability = selected_tool.availability
            if selected_provider and selected_provider.availability != ProviderAvailability.AVAILABLE:
                availability = selected_provider.availability

        return {
            "selected_tool": selected_tool,
            "selected_provider": selected_provider,
            "execution_tier": selected_tool.tier if selected_tool else ToolTier.SCRIPT,
            "why_selected": why_selected or "No available tool matched capability requirements.",
            "alternatives_considered": alternatives_considered,
            "why_alternatives_rejected": why_alternatives_rejected,
            "mcp_report": mcp_report,
            "availability": availability,
            "offline_mode": offline_mode,
            "authorization_status": auth_status,
            "authorization_reason": auth_reason,
        }
