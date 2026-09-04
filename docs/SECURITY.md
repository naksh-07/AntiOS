# AntiOS Security Posture & Boundary Policy (`docs/SECURITY.md`)

AntiOS implements a defense-in-depth security model to govern autonomous agent behavior and prevent unauthorized actions, path escapes, credential exposure, or framework corruption.

---

## 1. Threat Model & Protected Assets

AntiOS defends against six primary threat categories:

1. **Framework Corruption**: Autonomous agents modifying their own governance rules, hooks, or core modules.
2. **Upstream Domain Violation**: Agents modifying protected domain cores without authorization.
3. **Path Traversal & Escapes**: Directory traversal tricks (`../`, encoded separators, symlinks, null bytes).
4. **Shell Injection & Hazardous Commands**: Execution of arbitrary destructive shell commands (`rm -rf`, `format`, fork bombs).
5. **Credential & Secret Leakage**: API keys, tokens, or private keys exposed in logs or transcripts.
6. **Tool & MCP Sprawl**: Agents bypassing local tools to invoke untrusted or unauthenticated MCP servers.

---

## 2. Defense Mechanisms

### A. PreToolUse Interception Guard
AntiOS registers a native `PreToolUse` hook in `.agents/hooks.json` mapped to `framework/scripts/hooks/pre_tool_guard.py`. Before any file modification tool runs, the guard evaluates:
- Normalized target path against AntiOS framework paths (`.agents/**`, `framework/**`).
- Target path against project `protected_zones` and `protected_domain_cores`.
- Operation type (Write, Create, Delete, Move).

If any boundary check fails, the guard returns `PERMISSION_DENIED` and immediately aborts the tool invocation.

### B. Path Canonicalization & Confinement Engine (`framework/core/guard.py`)
To prevent path traversal bypasses, all file paths pass through strict canonicalization in `guard.py`:
- Resolution of relative dot segments (`..`, `.`)
- Canonicalization of Windows drive letters and case
- Normalization of forward and backward slashes
- Rejection of null bytes (`\0`) and control characters
- Resolution of symlinks to their physical on-disk targets
- Confinement verification strictly within repository boundary (`os.path.commonpath`)

### C. Shell Safety & Command Filtering (`framework/core/guard.py`)
CLI executions pass through deterministic boundary evaluation:
- Deterministic tokenization of shell command lines.
- Rejection of piped command chains attempting to write to protected zones.
- Execution within explicit working directories with hard timeouts.

### D. 6-Tier Tool Preference & MCP Policy (`framework/core/tool_policy.py`)
AntiOS restricts external tool invocation using a strict 6-tier hierarchy:
$$\text{NATIVE} > \text{SCRIPT} > \text{PROJECT} > \text{EXTERNAL} > \text{SERVICE} > \text{MCP}$$
MCP servers are relegated to Tier 6 and require passing the 8 canonical justification criteria defined in [docs/reference/MCP_POLICY.md](reference/MCP_POLICY.md).
