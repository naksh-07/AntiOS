# AntiOS Experience Architecture Overview

**Directory**: `docs/architecture/experience/`  
**Status**: `RATIFIED` (Phase 108)  
**Parent Specification**: `ANTIOS_ARCHITECTURE.md`  

---

## 1. Vision & Architecture Philosophy

The AntiOS Experience Architecture provides non-blocking, privacy-preserving, centralized empirical intelligence across all AntiOS-governed workspaces.

Unlike brittle machine-learning wrappers that attempt to fine-tune prompts dynamically or pollute project repositories with metrics databases, the AntiOS Experience plane:
- Persists all telemetry to a centralized SQLite store outside the target repository.
- Scans and redacts 100% of API keys, tokens, passwords, and private file paths before storage.
- Operates purely in the background without blocking engineering tasks.
- Enforces an absolute, mathematically verified firewall between Project Memory (System A) and Experience Intelligence (System B).

```
┌─────────────────────────────────────────────────────────────┐
│                 EXPERIENCE PLANE FOUNDATIONS                │
├─────────────────────────────────────────────────────────────┤
│ 1. ZERO REPO POLLUTION     │ No .db files in project repos │
│ 2. NON-BLOCKING INGESTION  │ Telemetry failure never blocks│
│ 3. FAIL-CLOSED REDACTION   │ 100% secret & credential scrub│
│ 4. SYSTEM A/B SEPARATION   │ Zero cross-plane dependencies │
│ 5. CONTINUOUS CAPTURE      │ Hook-embedded event ingestion │
│ 6. DETERMINISTIC METRICS   │ OBSERVED, DERIVED, UNKNOWN    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Contents

This directory contains the authoritative specifications for the Experience Architecture:

1. **[`CONTINUOUS_TELEMETRY.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/experience/CONTINUOUS_TELEMETRY.md)**:
   The continuous, hook-embedded telemetry ingestion pipeline, byte-offset transcript checkpointing, and non-blocking failure tolerance.

2. **[`SYSTEM_A_B_SEPARATION.md`](file:///c:/Users/Suraj/Documents/Antigravity/AntiOs/docs/architecture/experience/SYSTEM_A_B_SEPARATION.md)**:
   The formal specification of the epistemic, storage, operational, and code-import firewall separating Project Learning (System A) from Experience Intelligence (System B).
