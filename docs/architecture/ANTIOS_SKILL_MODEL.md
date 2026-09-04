# AntiOS Primary Skill Architecture (`docs/architecture/ANTIOS_SKILL_MODEL.md`)

**Date**: 2026-09-05  
**Status**: Authoritative Architectural Specification (Phases 49–54 Consolidated)  
**Governing Principle**:
> *"The main `antios` skill is the single user-facing entry point and authoritative control plane.*  
> *It must remain intentionally small, orchestrating wayfinding, capabilities, workforce sizing, and verification through progressive disclosure rather than monolithic bloat."*

---

## 1. The Single Operating Interface

In any AntiOS-governed project, the developer interacts with a single primary skill:

```text
/antios
```

or triggers AntiOS governance naturally through normal engineering task prompts.

The human user does **not** need to manually coordinate:
- Wayfinding and component mapping
- Capability pack resolution
- Agent topology selection
- Tool and MCP justification
- Concurrency and launch budgeting
- Wave transitions and workforce collapse
- Maker-Checker audit and physical Stop Gate verification

The main `antios` skill orchestrates these subsystems deterministically.

---

## 2. The Control Plane vs Monolithic Instruction Anti-Pattern

```text
┌─────────────────────────────────────────────────────────────┐
│                    ANTI-PATTERN: MONOLITH                   │
│  - 2,000-line prompt stuffing every rule into one prompt    │
│  - Context saturation, instruction drift, amnesia           │
│  - High token overhead on trivial tasks                     │
└─────────────────────────────────────────────────────────────┘
                              VS
┌─────────────────────────────────────────────────────────────┐
│                 ANTIOS MODEL: CONTROL PLANE                 │
│  - Intentionally compact entry point (<= 80 lines)          │
│  - Establishes operating axioms and boundary laws           │
│  - Discloses deeper knowledge on demand (L0 to L5)          │
│  - Dispatches specialized skills only when justified        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. The 9-Stage Control Pipeline

When invoked, `/antios` guides the executing agent through a strict 9-stage sequence:

```text
1. UNDERSTAND
   Identify user intent, acceptance criteria, constraints, and non-goals.
         ↓
2. CHECK PROJECT STATE
   Read .antios/knowledge.json and docs/ACTIVE_CONTEXT.md (<= 60 lines).
         ↓
3. LOCATE
   Query WayfindingEngine (`python framework/scripts/tools/navigate_repo.py --query "<query>"`).
         ↓
4. CLASSIFY
   Determine TaskClass (FEATURE | BUG | REFACTOR | INVESTIGATION | DOCUMENTATION | RELEASE) and RiskTier.
         ↓
5. SELECT CAPABILITIES
   Resolve skills, rules, test runners, and tool policies via CapabilityRouter.
         ↓
6. SELECT WORKFORCE
   Evaluate Gate A (Pre-Planning) and Gate B (Execution Dispatch) to size workforce.
         ↓
7. EXECUTE
   Apply guarded code changes using controlled single-writer or disjoint branch workspaces.
         ↓
8. VERIFY
   Execute physical test runner (exit code 0) + independent Maker-Checker audit (`antios-verifier`).
         ↓
9. REMEMBER
   Record dead ends and distill active task progress in docs/ACTIVE_CONTEXT.md.
```

---

## 4. Progressive Disclosure & Specialist Delegation

The main skill does not duplicate domain or specialist procedures. It delegates to focused specialist skills when justified:

```text
                             /antios
                       (Main Control Plane)
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
[ antios-engineer ]     [ antios-debug ]        [ antios-verifier ]
Universal lifecycle,    Systematic 5-step       Independent audit,
Same Change Set, and    root-cause debugging    diff inspection, &
implementation rules.   and surgical patch.     JSON verdict schema.
                                │
                                ▼
                     [ antios-adapt-project ]
                     Project discovery, manifest
                     synchronization, & adaptation.
```

---

## 5. Source Repository vs Project Instance Demarcation

AntiOS strictly separates the Core framework source from target project installations:

- **Source AntiOS Repository**: Contains core governance engines (`framework/core/`), scripts (`framework/scripts/`), and test harnesses (`tests/`).
- **Target Project Instance**: Contains **only** the compiled `.antios/` metadata directory, `.agents/skills/antios/SKILL.md`, and `.agents/hooks.json`.
- The source repository is **never** copied into target repositories. Target project code and user-authored skills remain sovereign and protected.
