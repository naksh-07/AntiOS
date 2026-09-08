# AntiOS Engineering Memory: Failed Hypotheses & Dead Ends

This registry records negative results, failed approaches, and invalid conjectures
to permanently prevent regression thrashing across agent sessions.

### DE-001: Background File Watchers under INV-15
- **Status**: [TESTED_NEGATIVE]
- **Timestamp**: 2026-09-07T12:00:00Z
- **Target Subsystem**: `framework/intelligence`
- **Target File**: `framework/intelligence/freshness.py`
- **Target SHA-256**: `ad450fbcf5b1e95cf129e71b29a2dcbe14b8a218f2f45ea2e93b167da7a1518f`
- **Tags**: daemons, watchdog, inv-15, freshness
- **Hypothesis**: Use watchdog or inotify to maintain live repository cache in memory.
- **Attempted Action**: Evaluated watchdog daemon thread architecture.
- **Observed Result**: Violates constitutional invariant INV-15. Unbounded process lifecycles and background worker hangs during subprocess execution.
- **Root Cause**: AntiOS requires lifecycle-synchronous execution without persistent background daemons.
- **Guidance**: Use synchronous Combined Git Token checking (91.5ms) combined with sub-millisecond hierarchical Merkle bubble-up recalculation (59µs) in PreInvocation.

### DE-002: Inline Shell Commands in Antigravity hooks.json
- **Status**: [TESTED_NEGATIVE]
- **Timestamp**: 2026-09-07T14:30:00Z
- **Target Subsystem**: `framework/hooks`
- **Target File**: `framework/hooks/pre_tool_guard.py`
- **Target SHA-256**: `6636780c102a0b12bc85d18d9f485dbdbead269134bb587b1c4c95a0bc0e99ca`
- **Tags**: windows, powershell, hooks, quoting
- **Hypothesis**: Embedding multi-line `python -c "..."` directly into `.agents/hooks.json` allows inline path discovery without external scripts.
- **Attempted Action**: Configured inline python snippet in `.agents/hooks.json`.
- **Observed Result**: Windows `cmd.exe` and PowerShell shell parsers mangle quote escapes and parentheses, crashing with `SyntaxError: unterminated string literal`.
- **Root Cause**: Windows command-line argument quoting rules for nested subprocesses cannot reliably escape Python statements.
- **Guidance**: Always execute discrete standalone script paths (e.g. `python framework/hooks/pre_tool_guard.py`).
