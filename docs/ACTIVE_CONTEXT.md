# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.0 — Phases 43–48 Project Agent OS Foundation & Compilation
**Class**: FEATURE_ARCHITECTURE | **Risk**: MEDIUM
**Stage**: VERIFICATION | **Status**: PASS
**Version**: 2.0.0-PROPOSAL | **Mode**: VERIFYING
**Active Subsystem**: Universal Compiler, Lifecycle & Governance

## 1. Active Checklist
- [x] Phase 43: Project Agent OS Specification (`docs/architecture/PROJECT_AGENT_OS.md`)
- [x] Phase 44: Cryptographic Project Manifest (`framework/core/manifest.py`)
- [x] Phase 45: Six-Phase Installation Lifecycle Engine (`framework/core/installation.py`)
- [x] Phase 46: Universal Boundary Compiler (`framework/core/compiler.py`)
- [x] Phase 47: Five-Tier Ownership & Provenance Model (`framework/core/provenance.py`)
- [x] Phase 48: E2E Installation Certification across 7 Archetypal Fixtures
- [x] Antigravity Orchestration Constitution (Wave lifecycle, bounds <=10/wave, <=20/mission)
- [x] CLI Tooling (`framework/scripts/tools/install_project.py`) with all subcommands
- [x] Canonical documentation portal & decision register updated (Decisions 36–42)
- [x] Full test suite passing (480/480 tests, 100%) with 0 doc audit errors

## 2. Blockers & Invariants
- Invariant: 4-Boundary Demarcation (`SOURCE ≠ INSTANCE ≠ PROJECT ≠ ANTIGRAVITY`)
- Invariant: Protected Zones Immutability (`framework/core/`, `.agents/`, `antios.config.json`)
- Invariant: Zero third-party dependencies in Universal Core (Python 3.8+ stdlib only)
- Invariant: Orchestration bounds: Active <= 10, Total <= 20, Depth <= 2, Mandatory wave collapse
- Invariant: Active Context strictly bounded <= 60 lines (currently ~40 lines)

## 3. Changed Files & Verification State
- Verification State: VERIFIED (480/480 passing in ~28s via `tests/run_all.py`)
- Doc Audit: 0 broken references across 35 files (`framework/scripts/tools/audit_docs.py --all`)
- Working Tree: All Phase 43–48 modules and tests integrated cleanly
- Verdict: PASS (Phases 43–48 complete and certified)

## 4. Dead-End Memory & Validated Lessons
- CRLF vs LF hash drift: compute_file_sha256 and file writers must enforce newline="\n"
- Manifestless projects require deterministic fallback fingerprint derived from project identity
- Target instance template paths (.antios/, /antios skill) are distinct from repo source docs
- PreToolUse hooks run from .agents/ and must resolve scripts using robust path lookup

## 5. Next Immediate Action
Phase 43–48 complete. Finalizing independent Maker-Checker audit and structured executive report.
