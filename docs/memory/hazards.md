# AntiOS Engineering Memory: Tool Hazards & Forbidden Operations

### HAZ-001: Interactive Watch Modes in Automated Test Runners
- **Status**: [VERIFIED_FACT]
- **Timestamp**: 2026-09-07T17:00:00Z
- **Target Subsystem**: `framework/hooks/gate.py`
- **Target File**: `framework/hooks/gate.py`
- **Tags**: jest, vitest, pytest, watch, hang
- **Hazard**: Executing test commands without explicit non-watch flags (e.g. `npm test`, `jest`, `vitest`) defaults to interactive file watcher mode in some configurations.
- **Consequence**: Subprocess hangs until the hook execution timeout is reached, failing the verification turn.
- **Rule**: Injected test runners must append anti-watch arguments (`--watchAll=false`, `--watch=false`, or `--run`) to ensure one-shot execution.

### HAZ-002: Broad Deletion and Recursive Directory Removal
- **Status**: [VERIFIED_FACT]
- **Timestamp**: 2026-09-07T17:30:00Z
- **Target Subsystem**: `framework/hooks/pre_tool_guard.py`
- **Target File**: `framework/hooks/pre_tool_guard.py`
- **Tags**: rm, deletion, pre_tool_guard, safety
- **Hazard**: Tool invocations executing destructive commands (`rm -rf`, `git reset --hard`, `git clean -fd`) destroy uncommitted work.
- **Consequence**: Irreversible data loss and invariant violation.
- **Rule**: `PreToolUse` hook intercepts and rejects destructive shell commands.
