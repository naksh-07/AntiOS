# Two-Way Adaptation Contract (`docs/architecture/TWO_WAY_ADAPTATION.md`)

## 1. Overview & Architectural Demarcation
AntiOS 2.0 establishes a formal, bidirectional information and adaptation contract governing the boundary between the target repository and the AntiOS runtime OS:
- **`TARGET_PROJECT`**: The target host codebase containing application code, tests, and user documentation.
- **`PROJECT_INSTANCE`**: The compiled project-local Agent OS instance located in `.antios/` and `.agents/`.
- **`ANTIOS_SOURCE`**: The canonical upstream AntiOS source repository, core architecture (`framework/core/`), and master constitution.
- **`PLATFORM`**: The Antigravity IDE and execution runtime.

The Two-Way Adaptation Contract guarantees that while Project Agent OS instances continuously adapt to the unique traits, toolchains, and workflows of target projects, the canonical AntiOS Core remains strictly immutable (`CORE ≠ ADAPTER`).

---

## 2. Four Authority Tiers & Epistemic Hierarchy

All information crossing adaptation boundaries is enveloped within deterministic `AdaptationSignal` records and governed by strict authority tiers:

| Authority Tier | Weight / Scope | Authorized Actions |
|---|---|---|
| `CONSTITUTION` | Absolute / Immutable | Sovereign invariant enforcement (`ANTIOS_CONSTITUTION.md`) |
| `CORE_SPEC` | Upstream Framework | Canonical contracts (`framework/core/`) |
| `HUMAN_DIRECTIVE` | Explicit Operator | Approval of new skills, rules, and configuration changes |
| `GOVERNANCE_GATE` | Automated Ratchet | Stop gates, test suites, and physical verification checks |
| `PROJECT_MANIFEST` | Instance Provenance | Tracked artifacts and ownership records (`.antios/manifest.json`) |
| `PROJECT_LOCAL` | Project Adapter | Declarative adapter settings (`antios.config.json`) |
| `AGENT_INFERENCE` | 0.3 / Ephemeral | Hypotheses and observations; CANNOT approve changes or mutate rules |

---

## 3. Epistemic Segregation
AntiOS enforces strict epistemic boundaries:
1. **`OBSERVATION`**: Physical witness of project reality (test exit codes, execution output, file states).
2. **`INFERENCE`**: Derived patterns or hypotheses from 1+ observations.
3. **`PROPOSAL`**: Structured recommendation for configuration, tool, or skill evolution.
4. **`APPROVED_CHANGE`**: Formally authorized change verified against boundary contracts.

> [!IMPORTANT]
> **Epistemic Law**: `PROPOSAL` is never equivalent to `APPROVED_CHANGE`. Agent inference alone (`AGENT_INFERENCE`, confidence $\le 0.4$) can never authorize durable core rules, alter security policies, or mutate configuration without explicit governance approval.

---

## 4. Core Immutability Law
Signals and proposals originating from target projects are physically blocked from modifying protected core assets:
- `framework/`
- `ANTIOS_CONSTITUTION.md`
- `ANTIOS_SOURCE_OF_TRUTH.md`
- `ANTIOS_V1.md`
- `.agents/hooks.json`
- `.git/`

When a target project identifies a framework-level deficit, the transition gate routes the signal as a read-only upstream Request For Comments (`ESCALATION_REQUIRED`) to upstream framework maintainers rather than executing a local file write.
