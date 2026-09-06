# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.1 — Final Pre-Release Audit & Beta Release Gate
**Class**: RELEASE_ENGINEERING | **Risk**: MEDIUM
**Stage**: COMPLETE | **Status**: CERTIFIED_RELEASE_READY
**Version**: 2.1.0-beta.1 (Experience Plane Certified) | **Mode**: OPERATIONAL
**Active Subsystem**: Release Engineering, Packaging, Governance & Invariant Enforcement

## 1. Active Checklist
- [x] Forensic Bug Hunt: Remediated PEP 639 packaging classifier conflict in `pyproject.toml`
- [x] Release Engine: Added missing `import sys` to `release_engine.py` for automated pre-flight testing
- [x] CLI Robustness: Structured JSON error returns on `antios data` subcommands, `--apply` validation in `cmd_repair`
- [x] Test Decoupling: Decoupled GitHub capabilities unit test from live machine auth state
- [x] Platform Hygiene: Set `__test__ = False` on `ResultItem`, guarded `normalize_path(None)`, ASCII hyphen in CLI description
- [x] Version Alignment: Synchronized `2.1.0-beta.1` across `version.py`, `pyproject.toml`, `CHANGELOG.md`, `README.md`
- [x] System A vs System B: Confirmed 100% architectural decoupling and cryptographic byte immutability
- [x] Canonical Invariants: Verified INV-01 through INV-20 compliance; zero background daemons; zero vector DBs
- [x] Pre-Flight Gate: `antios release check` passing with 0 blockers

## 2. Blockers & Invariants
- Invariant: Experience is raw telemetry; Learning is evidence accumulation; Proofs are physical disk byte hashes.
- Invariant: Experience Intelligence NEVER automatically feeds into learning, memory, lessons, or rules.
- Invariant: Zero background daemons, zero vector DBs, zero embeddings, zero custom agent runtimes.
- Invariant: INV-10 (Zero database files in project repositories).
- Invariant: Module size $\le 2000$ lines; Active Context $\le 60$ lines; cards $\le 25$ lines.

## 3. Changed Files & Verification State
- Core: `pyproject.toml`, `release_engine.py`, `cli.py`, `verdict.py`, `sanitizer.py`, `version.py`
- Tests: `test_git_github_release_capabilities.py`
- Docs: `CHANGELOG.md`, `README.md`, `docs/ACTIVE_CONTEXT.md`
- Verdict: PASS (All 1086+ unit tests passing; release check passes cleanly)

## 4. Dead-End Memory & Validated Lessons
- PEP 639 requires omitting `License :: OSI Approved :: MIT License` classifiers when `license = "MIT"` expression is set.
- Subprocess invocations in test suites must be hermetic and not assert live machine credentials.
- Machine-readable CLI modes (`--json`) must wrap all top-level exceptions in structured envelopes.

## 5. Next Immediate Action
Audit and remediations verified. System certified release ready for AntiOS 2.1.0-beta.1.

