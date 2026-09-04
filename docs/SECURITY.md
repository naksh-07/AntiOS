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

### B. Path Normalization Engine (`path_normalizer.py`)
To prevent path traversal bypasses, all file paths pass through `normalize_path()`:
- Resolution of relative dot segments (`..`, `.`)
- Canonicalization of Windows drive letters and case
- Normalization of forward and backward slashes
- Rejection of null bytes (`\0`) and control characters
- Resolution of symlinks to their physical on-disk targets
- Blocking of UNC paths (`\\server\share`)

### C. Shell Safety & Command Filtering (`security.py`)
CLI tools and runners pass through `evaluate_shell_command()`:
- Deterministic tokenization of shell command lines.
- Rejection of piped command chains containing destructive primitives.
- Execution within explicit working directories with hard timeouts.

### D. 6-Tier Tool Preference & MCP Policy (`tool_policy.py`)
AntiOS restricts external tool invocation using a strict 6-tier hierarchy:
$$\text{NATIVE} > \text{SCRIPT} > \text{PROJECT} > \text{EXTERNAL} > \text{SERVICE} > \text{MCP}$$
MCP servers are relegated to Tier 6 and require passing the 8 canonical justification criteria defined in `ANTIOS_MCP_POLICY.md`.
