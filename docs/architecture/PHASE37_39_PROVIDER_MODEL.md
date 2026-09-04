# AntiOS Phase 37–39 Provider Model Specification

## 1. Overview
The Provider model abstracts the execution transport and interface source exposing tools and capabilities. A provider is not a general-purpose plugin framework; it is strictly an execution-selection abstraction.

---

## 2. Provider Categories (`ProviderType`)

* **`NATIVE`**: The native Antigravity runtime environment and standard built-in tools.
* **`LOCAL_SCRIPT`**: Local deterministic Python tools packaged under `framework/scripts/tools/`.
* **`PROJECT`**: Target repository commands declared in `antios.config.json` (e.g. `pytest`, `npm test`).
* **`EXTERNAL`**: System CLI binaries found on `PATH` (e.g. system `git`, `python`).
* **`MCP`**: External Model Context Protocol JSON-RPC servers (e.g. Chrome DevTools, Playwright).

---

## 3. Provider Policy Status (`ProviderPolicyStatus`)

* **`PERMITTED`**: Authorized for usage within declared task boundaries.
* **`RESTRICTED`**: Authorized only under strict task isolation (e.g. GitHub MCP restricted to remote PR operations).
* **`REJECTED`**: Permanently blocked under `ANTIOS_MCP_POLICY.md` (e.g. Notion, Postman, PostHog, Unauthorized).

---

## 4. `ProviderDefinition` Data Model

```python
@dataclass
class ProviderDefinition:
    provider_id: str
    name: str
    provider_type: ProviderType
    capabilities: List[str] = field(default_factory=list)
    exposed_tools: List[str] = field(default_factory=list)
    locality: Locality = Locality.LOCAL
    availability: ProviderAvailability = ProviderAvailability.AVAILABLE
    offline_capable: bool = True
    requires_network: bool = False
    permissions_required: List[str] = field(default_factory=list)
    policy_status: ProviderPolicyStatus = ProviderPolicyStatus.PERMITTED
    allowed_tasks: List[str] = field(default_factory=lambda: ["*"])
    forbidden_tasks: List[str] = field(default_factory=list)
    project_scope: str = "*"
    fallback_provider_id: Optional[str] = None
    justification: str = ""
    source: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## 5. Canonical MCP Justification Authority

The `MCPJustificationEngine` provides the single source of truth for MCP selection, answering the 8 canonical questions:
1. **Is MCP needed?** (`is_needed: bool`)
2. **Which provider?** (`provider_id: str`)
3. **Why?** (`why: str`)
4. **Is it permitted?** (`is_permitted: bool`)
5. **What local/native alternatives exist?** (`local_alternatives: List[str]`)
6. **Why are those alternatives insufficient?** (`why_insufficient: str`)
7. **What fallback exists?** (`fallback: str`)
8. **What happens if the provider is unavailable?** (`on_unavailable: str`)
