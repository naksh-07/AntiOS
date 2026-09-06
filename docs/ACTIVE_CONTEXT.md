# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Productization, Release Engineering & Beta Readiness
**Class**: PRODUCTIZATION_AND_RELEASE_ENGINEERING | **Risk**: HIGH
**Stage**: COMPLETE | **Status**: CERTIFIED_BETA_READY
**Version**: 2.0.0-beta.1 | **Mode**: OPERATIONAL
**Active Subsystem**: Unified CLI, Release Engine & Beta Lifecycle

## 1. Active Checklist
- [x] Packaging: `pyproject.toml` setuptools package discovery, console script `antios`
- [x] Version Authority: `version.py` authoritative SemVer (`2.0.0-beta.1`, beta channel)
- [x] Product Surface: Unified `antios` CLI (`version`, `status`, `doctor`, `install`, `update`, `rollback`, `repair`, `remove`, `adapt`, `verify`, `issue`, `release`)
- [x] Lifecycle Hardening: Pre-update snapshotting, rollback, downgrade protection
- [x] Diagnostics: `DoctorEngine` (10 drift domains, runtime closure, secret redaction)
- [x] Git & GitHub: Local Git CLI abstraction, GitHub capability, freeze triage
- [x] Release Engineering: `ReleaseEngine` pre-flight gate, matrix CI, `scripts/`
- [x] Test Suite: 920/920 tests passing (100% pass rate, 0 failures, 0 skips)
- [x] Proving Ground: 14-step Beta Readiness Proving Ground verified in sandbox
- [x] Documentation & ADRs: `CHANGELOG.md`, `BETA_READINESS.md`, ADR 86 ratified

## 2. Blockers & Invariants
- Invariant: Zero background daemons, zero custom schedulers/swarms, zero vector DBs.
- Invariant: Architecture frozen under Phase 101 / ADR 85 governance.
- Invariant: AntiOS rollback strictly scoped; never reverts user application code.
- Invariant: Module size ceiling $\le 2000$ lines; Active Context $\le 60$ lines; cards $\le 25$ lines.
- Invariant: INV-01 to INV-20 canonical invariants ratified and permanently locked.

## 3. Changed Files & Verification State
- Core: `version.py`, `git_capability.py`, `github_capability.py`, `doctor.py`, `release_engine.py`, `installation.py`, `manifest.py`, `drift_health.py`, `__init__.py`, `cli.py`
- Automation & CI: `.github/workflows/ci.yml`, `scripts/*`
- Tests: `test_versioning.py`, `test_lifecycle_productization.py`, `test_git_github_release_capabilities.py`, `test_beta_productization_e2e.py`, `run_all.py`
- Docs: `CHANGELOG.md`, `README.md`, `BETA_READINESS.md`, `RELEASE.md`, `RELEASE_ENGINEERING.md`, `VERSIONING.md`, `INSTALLATION.md`, `UPGRADING.md`, `ROLLBACK.md`, `TROUBLESHOOTING.md`, `MAINTENANCE.md`, `MCP_CAPABILITIES.md`, `DECISION_REGISTER.md` (ADR 86)
- Verdict: PASS (920/920 tests pass cleanly, 0 failures, 0 errors, 0 skips)

## 4. Dead-End Memory & Validated Lessons
- Setuptools flat-layout requires explicit `include = ["framework*"]` package filter.
- Windows terminals raise `UnicodeEncodeError` on `\u2713`; use ASCII-safe indicators.
- External projects configure runners via `antios.config.json:test_runners`; check before flagging missing `tests/run_all.py`.
- Automated secret redaction must scrub both `gho_*` tokens and key/value credential pairs.

## 5. Next Immediate Action
AntiOS 2.0.0-beta.1 certified and ready for beta release distribution.
