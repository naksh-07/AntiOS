# Contributing to AntiOS

AntiOS is an Agent-Native Engineering OS for Google Antigravity designed to operate under strict governance, deterministic verification, and clear responsibility boundaries.

All contributions — whether authored by human engineers or autonomous AI agents — must conform to the following engineering standards and constitutional invariants.

---

## 1. Constitutional Invariants

Every contribution must honor the 7 core invariants codified in [ANTIOS_CONSTITUTION.md](ANTIOS_CONSTITUTION.md):

1. **Platform Sovereignty**: Respect Antigravity native primitives; never circumvent ambient platform controls.
2. **Protected Zones Immutability**: `framework/core/` and `.agents/` represent core governance and cannot be modified without formal architectural consensus.
3. **Toolchain Ground Truth**: Ambient runtime tools, exit codes, and physical disks represent ground truth over verbal agent claims.
4. **Physical Stop Gate Ratchet**: The verification ratchet is immutable; tasks cannot conclude if tests or lint suites fail.
5. **Same Change Set Discipline**: Any modification to runtime code MUST include corresponding unit/integration tests and updated documentation within the same atomic change set.
6. **Shallow Delegation Depth**: Agent hierarchies must remain strictly shallow (depth <= 2).
7. **Bounded Context & Skills**: Active context ledger (`docs/ACTIVE_CONTEXT.md`) and agent skills (`.agents/skills/*/SKILL.md`) must strictly observe hard line budgets (<= 60 lines).

---

## 2. Same Change Set Verification

AntiOS enforces atomic co-modification. Before opening a pull request or merging changes, execute the changeset verification tool:

```bash
python framework/scripts/tools/check_changeset.py .
```

A valid changeset ensures:
- Code changes in `framework/` are accompanied by tests in `tests/`.
- Architectural or interface modifications are documented in `docs/`.
- No untracked or orphaned files remain in the working tree.

---

## 3. Test Suite Execution

AntiOS requires zero external test dependencies; tests execute on standard Python 3.10+ via:

```bash
python tests/run_all.py
```

All 766 tests across all 115 test suites must pass cleanly without skips, suppressions, or timing flakiness.

---

## 4. Documentation & Reference Integrity

To prevent documentation drift, all markdown references, file links, and backticked paths are verified deterministically:

```bash
python framework/scripts/tools/audit_docs.py --all
```

Zero broken references are permitted across the entire documentation tree.

---

## 5. Development Workflow

1. **Understand Task**: Consult [docs/INDEX.md](docs/INDEX.md) and identify affected subsystems.
2. **Plan Safely**: Review invariants and design boundaries in [ANTIOS_V1.md](ANTIOS_V1.md).
3. **Implement**: Keep changes minimal, modular, and decoupled.
4. **Verify Physically**: Execute `run_all.py`, `audit_docs.py`, and `check_changeset.py`.
5. **Update Ledger**: Synchronize `docs/ACTIVE_CONTEXT.md` before task completion.
