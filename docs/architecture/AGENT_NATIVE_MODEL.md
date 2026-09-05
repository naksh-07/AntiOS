# Agent-Native Repository Architecture (`docs/architecture/AGENT_NATIVE_MODEL.md`)

## 1. Architectural Definition
An **agent-native repository** is not measured by the number of autonomous agents running inside it, but by:
> *"How efficiently, safely, and deterministically an AI agent can understand, navigate, modify, verify, and maintain the repository with minimal cognitive overhead and token burn."*

AntiOS 2.0 provides an evidence-based foundation for measuring, compiling, and optimizing agent-native repository qualities.

---

## 2. The 10 Core Dimensions of Agent-Native Quality

| # | Dimension | Primary Measurement Criteria | Epistemic Source |
|---|---|---|---|
| 1 | **WAYFINDING** | Component indexes, clear source roots, test maps, resolvable entrypoints | Physical disk & anatomy |
| 2 | **DOCUMENTATION** | Progressive disclosure, lack of dead links, <= 60-line active context | Syntactic doc audit & filesystem |
| 3 | **SKILLS** | Bounded prompts (<= 300 lines), non-overlapping triggers, canonical `/antios` | `.agents/skills/` |
| 4 | **AGENTS** | Zero legacy workflows, Shallow Depth Law (depth <= 2, `can_delegate=False`) | `.agents/hooks.json` & topology |
| 5 | **OWNERSHIP** | Cryptographic artifact manifest (`.antios/manifest.json`), 4 ownership tiers | Manifest & config |
| 6 | **VERIFICATION** | Configured automated test runners, physical test suites, Maker-Checker | `antios.config.json` & `tests/` |
| 7 | **MEMORY / KNOWLEDGE** | Procedural memory store, validated lessons, empirical observations | `.antios/knowledge.json` |
| 8 | **TOOLING** | Strict 6-tier tool escalation hierarchy (Tier 1 Native > Tier 6 MCP) | Tool policy & gap analyzer |
| 9 | **PROJECT STRUCTURE** | Clean directory hierarchy, authoritative manifests, Git boundaries | Package manifests & `.git` |
| 10 | **ORCHESTRATION READINESS** | Canonical 9-step dispatch, adaptive workforce sizing, wave collapse | Dispatch & orchestration engine |

---

## 3. Epistemic Segregation
Every dimension distinguishes three epistemic states:
- `OBSERVED`: Grounded in verified, physical files/artifacts on disk.
- `INFERRED`: Derived from static heuristics or structural relationships.
- `UNKNOWN`: Unobserved or missing information.

> [!IMPORTANT]
> `UNKNOWN` is never artificially collapsed to zero. Scores represent observed baseline evidence with explicit confidence ratings (`HIGH`, `MEDIUM`, `LOW`).

---

## 4. Documentation Compiler & Progressive Disclosure
The Documentation Compiler (`framework/core/documentation_compiler.py`) generates concise, progressive disclosure surfaces:
- `ARCHITECTURE_SUMMARY.md`: High-level system overview
- `SUBSYSTEM_MAP.md`: Tabular mapping of subsystems to test suites
- `COMPONENT_MAP.md`: Granular entrypoints and covering tests
- `TEST_MAP.md`: Configured automated verification runners
- `AGENT_GUIDANCE.md`: Operating invariants for agents

### Ownership Tiers
1. `GENERATED`: Machine-compiled, safe to regenerate.
2. `MANAGED`: Governed project adaptations.
3. `USER_AUTHORED`: Human-owned, strictly protected against autonomous overwrite.
4. `PROTECTED`: Constitutional frameworks, immutable to target projects.

---

## 5. Agent-Native Refactoring Advisor
The Refactoring Advisor (`framework/core/agent_refactoring.py`) identifies architectural structures causing excessive agent turns or search overhead.
- **Strictly Advisory**: Never autonomously rewrites code.
- **Governed Proposals**: All recommendations convert directly to `StructuredCapabilityProposal` objects.
- **NO_ACTION Principle**: If the risk or blast radius of a refactor exceeds its expected agent-native benefit, the advisor explicitly recommends `NO_ACTION`.
