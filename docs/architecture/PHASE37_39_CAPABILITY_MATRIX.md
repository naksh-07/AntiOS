# AntiOS Phase 37–39 Tool & Provider Capability Matrix

## 1. Provider Tier Matrix

| Provider ID | Provider Type | Locality | Offline Capable | Default Availability | Policy Status | Primary Capabilities |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `provider:antigravity-native` | `NATIVE` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | File read/write/edit, grep, run-command, local Git CLI |
| `provider:local-script` | `LOCAL_SCRIPT` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | Wayfinding, doc audit, changeset check, worktree check, session recovery |
| `provider:project-local` | `PROJECT` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | Project test runner, project linter, build scripts |
| `provider:external-cli` | `EXTERNAL` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | System git, python interpreter |
| `provider:chrome-devtools` | `MCP` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | Live browser DOM inspection, a11y audit, CSS layout debugging |
| `provider:playwright` | `MCP` | `LOCAL` | YES | `AVAILABLE` | `PERMITTED` | Headless browser automation, screenshot capture, user flow driving |
| `provider:gemini-api-docs` | `MCP` | `REMOTE` | NO | `AVAILABLE` | `PERMITTED` | Upstream Gemini API / SDK documentation retrieval |
| `provider:github` | `MCP` | `REMOTE` | NO | `AVAILABLE` | `RESTRICTED` | Remote GitHub pull requests, PR comments (Local git operations strictly forbidden) |
| `provider:notion` | `MCP` | `REMOTE` | NO | `POLICY_BLOCKED` | `REJECTED` | None (Forbidden by AntiOS policy) |
| `provider:postman` | `MCP` | `REMOTE` | NO | `POLICY_BLOCKED` | `REJECTED` | None (Forbidden by AntiOS policy) |
| `provider:posthog` | `MCP` | `REMOTE` | NO | `POLICY_BLOCKED` | `REJECTED` | None (Forbidden by AntiOS policy) |
| `provider:unauthorized-external-mcp` | `MCP` | `REMOTE` | NO | `POLICY_BLOCKED` | `REJECTED` | None (Strictly blocked by security governance) |

---

## 2. Canonical Tool Registry Matrix

| Tool ID | Tier | Providing Provider | Latency Hint | Cost Hint | Risk | Applicable Tasks |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `tool:native-run-command` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `HIGH` | All tasks (`*`) |
| `tool:native-view-file` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `LOW` | All tasks (`*`) |
| `tool:native-replace-content`| `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `MEDIUM`| Code modification (`*`) |
| `tool:native-write-file` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `HIGH` | New file creation (`*`) |
| `tool:native-grep-search` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `LOW` | Code search (`*`) |
| `tool:native-list-dir` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `LOW` | Directory exploration (`*`) |
| `tool:native-git-cli` | `NATIVE` | `provider:antigravity-native` | `SUB_SECOND` | `ZERO` | `LOW` | Git status, diff, log (`*`) |
| `tool:navigate-repo` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Wayfinding, change intent (`*`) |
| `tool:audit-docs` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Doc auditing (`DOCS`, `RELEASE`) |
| `tool:check-changeset` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Changeset integrity (`FEATURE`, `BUG`) |
| `tool:check-worktree` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Working tree hygiene (`*`) |
| `tool:adapt-project` | `SCRIPT` | `provider:local-script` | `SECONDS` | `ZERO` | `MEDIUM`| Project adaptation (`SETUP`) |
| `tool:distill-memory` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Architectural distillation (`*`) |
| `tool:recover-session` | `SCRIPT` | `provider:local-script` | `SUB_SECOND` | `ZERO` | `LOW` | Session recovery (`*`) |
| `tool:project-test-runner` | `PROJECT`| `provider:project-local` | `SECONDS` | `ZERO` | `MEDIUM`| Verification, testing (`*`) |
| `tool:project-linter` | `PROJECT`| `provider:project-local` | `SECONDS` | `ZERO` | `LOW` | Verification, linting (`*`) |
| `tool:external-git` | `EXTERNAL`| `provider:external-cli` | `SUB_SECOND` | `ZERO` | `LOW` | System git fallback (`*`) |
| `tool:external-python` | `EXTERNAL`| `provider:external-cli` | `SUB_SECOND` | `ZERO` | `MEDIUM`| Standalone script execution (`*`) |
| `tool:mcp-chrome-inspect` | `MCP` | `provider:chrome-devtools` | `SECONDS` | `MEDIUM` | `LOW` | Live DOM, a11y layout inspection |
| `tool:mcp-playwright-exec` | `MCP` | `provider:playwright` | `SECONDS` | `HIGH` | `MEDIUM`| Headless browser automation |
| `tool:mcp-gemini-search-docs`| `MCP` | `provider:gemini-api-docs` | `SECONDS` | `LOW` | `LOW` | Upstream Gemini API / SDK search |
| `tool:mcp-github-create-pr` | `MCP` | `provider:github` | `SECONDS` | `HIGH` | `HIGH` | Remote GitHub pull requests |
