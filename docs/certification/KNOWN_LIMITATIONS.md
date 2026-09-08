# AntiOS 3.0 Known Limitations & Operating Boundaries

**Document Status**: `AUTHORITATIVE_TRANSPARENCY`  
**Scope**: Production Operational Constraints & Architectural Boundaries

---

## 1. Operating System & Filesystem Quirks

### Windows File Locking
- **SQLite Concurrency**: Under Windows NTFS, concurrent write access to SQLite databases (`experience.db`) across multiple processes can result in transient `database is locked` errors. AntiOS mitigates this with WAL mode (`PRAGMA journal_mode=WAL`), busy timeouts (`5000ms`), and randomized exponential backoff retries.
- **Git Index Locking**: Frequent rapid git commands may occasionally encounter `.git/index.lock`. AntiOS read-only freshness checks rely on git plumbing (`git status --porcelain`, `git rev-parse`) to minimize index locking.

---

## 2. Test Runner Watch Flag Sanitization

- Many modern test runners (Jest, Vitest, Mocha) default to interactive watch mode when invoked via `npm test`.
- Interactive watch processes hang indefinitely in non-interactive agent environments.
- **Limitation & Mitigation**: AntiOS includes an automatic `sanitize_command` in `gate.py` that strips `--watch` and `--watchAll` flags and injects non-watch flags (e.g. `--watchAll=false`). However, runners with custom non-standard watch flags (e.g. `node --test`) must be explicitly declared in `antios.config.json` with their non-watch arguments.

---

## 3. Multi-Language AST Parsing

- **Python**: Full syntactic AST line-range extraction is performed natively via Python standard library `ast.parse`.
- **Non-Python (JavaScript, TypeScript, Go, Rust)**: Handled via regex-based structural line-boundary scanners. Complex multi-line macro expansions or esoteric syntax may result in approximate function boundaries.
- **Non-Faking Guarantee**: If a file cannot be parsed reliably, AntiOS emits the file with `unparsed` status rather than hallucinating symbols or line numbers.

---

## 4. Monorepo Repository Scale

- For repositories exceeding 50,000 files, running a full recursive directory crawl during Turn-0 discovery can exceed the 100 ms compilation budget.
- **Recommended Practice**: Large monorepos should configure discrete `antios.config.json` adapters at each workspace package/submodule root rather than a single monolithic root adapter.

---

## 5. Experience Intelligence (System B) Epistemic Limits

- **Passive Telemetry Only**: System B (`experience.db`) collects sanitized empirical data for human and operational review.
- **Zero Automatic Code Mutation**: Telemetry observations in System B do **not** automatically alter project code, update invariants, or modify configurations. AntiOS enforces strict separation between passive telemetry observation and durable project truth.
