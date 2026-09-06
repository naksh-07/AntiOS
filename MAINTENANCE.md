# AntiOS 2.0 Maintenance & Architecture Freeze Policy

This document defines the governance rules for maintaining and contributing to AntiOS 2.0.

---

## 1. Architecture Freeze Declaration

AntiOS 2.0 completed final certification across 101 phases (900/900 tests, 20 canonical invariants, universal adoption proving grounds).

> **The architecture of AntiOS 2.0 is FROZEN.**
>
> Engineering work on AntiOS 2.0 is strictly limited to **productization, release engineering, maintenance, and bug fixes**. No new core architecture or platform reimplementation is permitted.

---

## 2. Permitted Maintenance Categories

Under the Architecture Freeze, changes to AntiOS are permitted **exclusively** within these 8 categories:

1. **BUG_FIX**: Correcting demonstrable defects, race conditions, or unhandled exceptions.
2. **SECURITY_FIX**: Addressing vulnerabilities, secret leaks, or path traversal issues.
3. **CORRECTNESS_IMPROVEMENT**: Aligning implementation behavior with established specifications.
4. **PERFORMANCE_IMPROVEMENT**: Optimizing wayfinding latency, memory usage, or test execution speed.
5. **DOCUMENTATION_CORRECTION**: Clarifying guides, updating diagrams, or fixing outdated references.
6. **COMPATIBILITY_IMPROVEMENT**: Supporting newer language runtimes (e.g. Python 3.12/3.13) or toolchains.
7. **NEW_PROJECT_ADAPTER**: Adding declarative adapters for new tech stacks in `antios.config.json`.
8. **RELEASE_ENGINEERING**: Hardening packaging, CI workflows, and release pre-flight gates.

---

## 3. Permanently Prohibited Changes (Banned in 2.x)

The following architectural concepts are **permanently banned** from the AntiOS 2.x branch:

- **Custom Agent Schedulers / Runtimes**: Antigravity owns agent execution and scheduling (`INV-01`, `INV-16`).
- **Autonomous Swarms**: AntiOS enforces the Shallow Depth Law ($\le 2$: Parent $\to$ Child) (`INV-06`).
- **Background Daemons / Pollers**: AntiOS is strictly event-driven; zero background processes (`INV-15`).
- **Vector Databases & Embeddings**: AntiOS relies on deterministic lexical and structural wayfinding.
- **Autonomous Self-Mutation of Governance**: Core governance rules cannot be rewritten by agents.
- **Unnecessary MCP Servers**: Native platform and standard tools take precedence over MCP.

Any proposal requiring these items must be triaged as an **AntiOS 3.0 Candidate RFC** and deferred.
