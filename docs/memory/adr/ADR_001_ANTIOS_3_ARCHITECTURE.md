# ADR-001: AntiOS 3.0 Architecture & Native Antigravity Integration

- **Status**: [ARCHITECTURAL_DECISION]
- **Date**: 2026-09-07
- **Target Subsystem**: `framework`
- **Tags**: architecture, adr, antios-3, lifecycle

## Context
AntiOS 2.0 operated via custom runtime abstractions and emulation layers. With Antigravity 2.0 establishing native lifecycle hooks (`PreInvocation`, `PreToolUse`, `PostToolUse`, `Stop`) and skills, a unified architecture is required to eliminate dual-control planes and guarantee zero-daemon operation.

## Decision
1. **Compile, Don't Interpret**: The Project Compiler extracts static topologies, entrypoints, and test runners into standard Antigravity structures (`routes.json`, `AGENTS.md`).
2. **Native Lifecycle Hooks**: Physical enforcement occurs directly in the native Antigravity lifecycle via zero-dependency Python hooks in `framework/hooks/`.
3. **Synchronous Cryptographic Freshness**: Freshness is determined via Combined Git Token (`HEAD + porcelain`) and hierarchical Merkle tree updates in `PreInvocation` without background daemons (`INV-15`).
4. **Epistemic Memory Hygiene**: Engineering memory is stored in Git-tracked Markdown files under `docs/memory/` with SHA-256 target code binding.
5. **6-Dimension MVR Verification**: The Stop Gate executes physical test runners and inspects working trees for conflict markers before allowing task completion.

## Consequences
- 100% native compatibility with Antigravity platform contracts.
- Zero vector databases, zero background daemons, zero external dependencies.
- Perfect cryptographic guarantees for codebase freshness and verification.
