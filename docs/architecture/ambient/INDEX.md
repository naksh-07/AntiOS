# AntiOS Ambient Architecture Overview

**Directory**: `docs/architecture/ambient/`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Specification**: `ANTIOS_ARCHITECTURE.md`  

---

## 1. Vision & Core Philosophy

The Ambient Project OS architecture transforms AntiOS from an explicit, ceremony-driven framework into an **ambient, continuous, non-invasive operating environment** for software repositories.

In this model:
- AntiOS does not demand attention; it provides protection.
- Developers and AI agents write software normally, using standard tools and native workflows.
- AntiOS ensures boundaries are respected, tests are executed physically, state is preserved across context wipes, and learning accumulates automatically.

```
┌─────────────────────────────────────────────────────────────┐
│                 AMBIENT PROJECT OS PILLARS                  │
├─────────────────────────────────────────────────────────────┤
│ 1. ZERO MANDATORY RITUAL   │ No /antios for normal tasks   │
│ 2. ZERO CONTEXT INFLATION  │ Strict bounds (≤40/60 lines)   │
│ 3. ZERO CUSTOM RUNTIME     │ Pure event-driven hooks        │
│ 4. ZERO BACKGROUND DAEMONS │ 100% on-demand execution       │
│ 5. TOOLCHAIN GROUND TRUTH  │ Physical test exit code 0      │
│ 6. BOUNDARY DEMARCATION    │ SOURCE ≠ INSTANCE ≠ PROJECT    │
│ 7. CONTINUOUS TELEMETRY    │ Passive, sanitized, non-block  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Contents

This directory contains the detailed engineering specifications for the Ambient Project OS layer:

1. **[`BOOTSTRAP.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/BOOTSTRAP.md)**:
   The zero-cost session orientation model, prompt bounding laws, `docs/AGENTS.md` and `docs/ACTIVE_CONTEXT.md` protocols, and session startup priming.

2. **[`COMPILER.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/ambient/COMPILER.md)**:
   The Project Environment Compiler contract (`framework/core/compiler.py`), Five Artifact Tiers, Runtime Closure specifications, and `.antios/` instance generation.
