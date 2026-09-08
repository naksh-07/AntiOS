# AntiOS Engineering Memory: Environment Quirks & Host Workarounds

### ENV-001: Windows NTFS 8.3 Short Name Aliasing
- **Status**: [VERIFIED_FACT]
- **Timestamp**: 2026-09-07T16:00:00Z
- **Target Subsystem**: `framework/hooks/path_resolver.py`
- **Target File**: `framework/hooks/path_resolver.py`
- **Tags**: windows, ntfs, 8.3-alias, security
- **Context**: Windows NTFS generates short 8.3 names for directories with dots or long names (e.g. `.agents` -> `AGENTS~1`).
- **Hazard**: Malicious tool calls targeting `AGENTS~1` could bypass simple string prefix matching on `.agents`.
- **Remedy**: All path checking must resolve canonical paths via `os.path.realpath` and explicitly evaluate both long and short name variants.

### ENV-002: Windows Subprocess Git Paging
- **Status**: [VERIFIED_FACT]
- **Timestamp**: 2026-09-07T16:45:00Z
- **Target Subsystem**: `framework/hooks/gate.py`
- **Target File**: `framework/hooks/gate.py`
- **Tags**: git, windows, subprocess, hang
- **Context**: When invoking git in Windows subprocesses without a tty, git may invoke a pager (e.g. `less.exe` or `more.com`) and hang indefinitely.
- **Hazard**: Test runners or hooks hang for 300s waiting for EOF on stdin.
- **Remedy**: Always pass `PAGER=cat` and `GIT_PAGER=cat` in environment dictionaries for git subprocess invocations.
