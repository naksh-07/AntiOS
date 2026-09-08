# AntiOS 3.0 Constitutional Invariants Audit

**Audit Status**: `100_PERCENT_COMPLIANT` (15/15 Invariants Certified)  
**Standard**: Universal AntiOS Constitution (`INV-01` through `INV-15`)  
**Evidence Artifact**: `reports/STAGE_4_PROVING_REPORT.json`

---

## Invariant Audit Summary

| Invariant | Title | Compliance Status | Verification Mechanism | Physical Proof Summary |
| :--- | :--- | :--- | :--- | :--- |
| **INV-01** | Platform Sovereignty | **COMPLIANT** | Architectural Review | Uses native Antigravity primitives; zero subprocess virtualization or custom agent loops. |
| **INV-02** | Declarative Core | **COMPLIANT** | Runtime Audit | Zero mutable in-process state; `antios.config.json` and `.agents/routes.json` authoritative. |
| **INV-03** | Physical Verification | **COMPLIANT** | Stop Gate Proving | Stop Gate physically executes native test runner (exit code 0); verbal claims blocked. |
| **INV-04** | Fail-Closed Boundaries | **COMPLIANT** | PreToolUse & Gate Tests | PreToolUse denies on error/traversal; Stop Gate continues on test failure. |
| **INV-05** | Maker-Checker Separation | **COMPLIANT** | Verdict Contract Tests | Independent fresh context verifier physically rejects false completion claims. |
| **INV-06** | Epistemic Hygiene | **COMPLIANT** | Memory Store Tests | 5-tier memory; hypotheses quarantined; code drift triggers `[STALE_EVIDENCE]` suppression. |
| **INV-07** | Same Change Set | **COMPLIANT** | Worktree Snapshot Tests| Source code, tests, and documentation must co-evolve atomically in the same change set. |
| **INV-08** | Progressive Disclosure | **COMPLIANT** | Compiler Token Audit | `AGENTS.md` <= 40 lines (<250 tokens); `routes.json` ~400 tokens; AST outlines cached. |
| **INV-09** | Zero Vector Databases | **COMPLIANT** | Dependency & Code Audit| Zero vector embeddings or ChromaDB; exact structural hierarchical index used. |
| **INV-10** | 4-Zone Security Demarcation | **COMPLIANT** | PreToolUse Boundary Test| `SOURCE != INSTANCE != PROJECT != ANTIGRAVITY` strictly enforced. |
| **INV-11** | Zero Framework Imports | **COMPLIANT** | Target Repo Audit | Runtime scripts pure Python stdlib; zero framework dependencies in target repositories. |
| **INV-12** | Telemetry Sanitization | **COMPLIANT** | Sanitizer Regex Audit | Secrets (API keys, tokens), home paths, and raw code scrubbed before NDJSON write. |
| **INV-13** | System A / System B Firewall | **COMPLIANT** | Database Path Audit | Markdown memory (A) firewalled from `experience.db` (B); zero auto-mutation by System B. |
| **INV-14** | Multi-Repo Federation | **COMPLIANT** | Path Resolver Audit | Longest-prefix workspace matching across arbitrary `workspacePaths`. |
| **INV-15** | Zero Background Daemons | **COMPLIANT** | Process & Merkle Audit | Synchronous Turn-0 Git token & sub-millisecond Merkle (74.5 µs); zero watchers. |

---

## Detailed Invariant Analysis

### INV-01: Platform Sovereignty
AntiOS recognizes Google Antigravity as the sole execution substrate. It never runs competing agent runtimes, LLM prompt orchestrators, or sandboxed execution containers. All tool calls and permissions flow through Antigravity's native hooks (`PreToolUse`, `Stop`).

### INV-02: Declarative Core
AntiOS Core is completely declarative. It stores no runtime state in memory across turns. All behavior is driven by the declarative adapter `antios.config.json` and compiled route maps in `.agents/routes.json`. Target project adaptations do not require modifying framework source code.

### INV-03: Physical Verification
The Stop Gate enforces physical test runner execution. In Part 8 testing:
- Exit code 0 -> Task allowed.
- Exit code 1 -> Task rejected with detailed stdout diagnostics.
Verbal promises by LLMs have zero standing in AntiOS.

### INV-04: Fail-Closed Boundaries
If an unhandled exception, syntax error, or unknown parameter occurs in a hook or resolver, AntiOS always chooses the safest path:
- `PreToolUse` returns `decision: "deny"`.
- `Stop` gate returns `decision: "continue"` (refusing completion).

### INV-05: Maker-Checker Separation
Tasks marked with high risk require an independent Checker subagent dispatched with fresh context and zero context inheritance. In Part 13 testing, a fraudulent completion verdict with a failing test was rejected by `evaluate_checker_verdict`.

### INV-06: Epistemic Hygiene
Engineering memory in `docs/memory/` enforces 5 distinct epistemic grades. Working hypotheses are strictly quarantined and never returned in context injection queries. When code is edited, target content hashes invalidate stale records automatically.

### INV-07: Same Change Set
Code, tests, and documentation must co-evolve. In `test_mvr.py` and `test_e2e_scenarios.py`, attempting to commit code without matching tests or documentation updates is detected and flagged.

### INV-08: Progressive Disclosure
`AGENTS.md` is strictly bounded to <= 40 lines (Click: 18 lines, VibeAudio: 19 lines). Deeper information is progressively disclosed via `routes.json` and `ast_outlines.json`.

### INV-09: Zero Vector Databases
AntiOS contains zero vector databases, embedding models, or vector math libraries. All navigation is exact, syntactic, and structural.

### INV-10: 4-Zone Security Demarcation
AntiOS enforces four distinct security zones:
1. `SOURCE`: Framework source code (read-only for target agents).
2. `INSTANCE`: AntiOS installation metadata (`.antios/`).
3. `PROJECT`: Target project repository (`src/`, `tests/`, `package.json`).
4. `ANTIGRAVITY`: Execution substrate (`.agents/`, hooks, logs).

### INV-11: Zero Framework Imports
Target project code never imports `antios` or `framework`. When AntiOS is removed, target projects compile and test cleanly without missing module errors.

### INV-12: Telemetry Sanitization
All tool call and event telemetry passes through `TelemetrySanitizer` before being written to disk. High-entropy keys (`ghp_*`, `sk-*`, `AIza*`, bearer tokens, private keys) and user profile directories are deterministically scrubbed.

### INV-13: System A / System B Firewall
Engineering memory (System A, Markdown in `docs/memory/`) is strictly separated from operational telemetry (System B, SQLite `experience.db`). System B has zero code authority and cannot write to or mutate target project code.

### INV-14: Multi-Repo Federation
In multi-root Antigravity workspaces, `resolve_matching_workspace` uses canonical longest-prefix matching to map target files to their enclosing workspace root without cross-repository bleed.

### INV-15: Zero Background Daemons
AntiOS spawns no persistent background worker threads, watchers (`watchdog`, `inotify`), or polling daemons. State freshness is verified synchronously on Turn-0 in under 170 ms via the Combined Git Token and updated in 74.5 µs via the Merkle tree.
