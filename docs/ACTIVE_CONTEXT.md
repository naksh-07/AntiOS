# Active Context (`docs/ACTIVE_CONTEXT.md`)

**Mission**: AntiOS 2.1 — Phase 107 Experience Operations, Hardening & Final Certification
**Class**: ARCHITECTURE_AND_OPERATIONS | **Risk**: MEDIUM
**Stage**: COMPLETE | **Status**: CERTIFIED_PHASE_107
**Version**: 2.1.0-beta.1 (2.1 Experience Plane Complete) | **Mode**: OPERATIONAL
**Active Subsystem**: Experience Lifecycle Operations, Hardening & Proving Ground

## 1. Active Checklist
- [x] Core Operations: `restore_database()`, `purge_experience_data()`, `vacuum_database()`, `export_raw_experience()` in `experience.py`
- [x] Unified CLI: `antios data {backup,restore,purge,vacuum,export}` with `--confirm`, `--dry-run`, scoping safeguards
- [x] Core Exports: Exported Phase 105 bridge components and Phase 107 operations in `framework/core/__init__.py`
- [x] Adversarial Privacy: End-to-end multi-secret scrubbing, prompt injection defanging, and length-bounding verified
- [x] Resilience & Restart: Malformed/truncated JSONL tolerance, byte-offset checkpoints, and duplicate deduplication verified
- [x] Multi-Project Isolation: Strict tenant partitioning with separate IDs and no cross-scope data contamination verified
- [x] System A/B Non-Mutation: Cryptographic SHA-256 tree snapshots proving byte-for-byte target project immutability verified
- [x] Proving Ground A–J: 10 deterministic end-to-end execution scenarios verified
- [x] Global Suite Integration: `test_experience_operations.py` integrated into `tests/run_all.py` (72 tests, 100% pass)

## 2. Blockers & Invariants
- Invariant: Experience is raw telemetry; Learning is evidence accumulation; Proofs are physical disk byte hashes.
- Invariant: Experience Intelligence NEVER automatically feeds into learning, memory, lessons, or rules.
- Invariant: Zero background daemons, zero vector DBs, zero embeddings, zero custom agent runtimes.
- Invariant: INV-10 (Zero database files in project repositories).
- Invariant: Module size $\le 2000$ lines; Active Context $\le 60$ lines; cards $\le 25$ lines.

## 3. Changed Files & Verification State
- Core: `experience.py`, `cli.py`, `__init__.py`
- Tests: `test_experience_operations.py` (NEW), `run_all.py`
- Docs: `docs/architecture/EXPERIENCE_INTELLIGENCE.md`, `docs/ACTIVE_CONTEXT.md`
- Verdict: PASS (72/72 Phase 107 tests passing; 166/166 full Experience suite passing)

## 4. Dead-End Memory & Validated Lessons
- Destructive lifecycle operations (`restore`, `purge`) must require explicit `--confirm` and support preview `--dry-run`.
- Pre-operation hot backups taken before `restore` and `purge` prevent accidental data loss in production.
- Multi-project isolation must be enforced relationally down to turns and tool_calls via mission cascades.

## 5. Next Immediate Action
Phase 107 complete. AntiOS 2.1 Experience Plane is fully hardened, operational, and certified. Stop condition met.
