# AntiOS Phase 31–33 Architecture: Project Capability Layer (`docs/PHASE31_33_ARCHITECTURE.md`)

**Version**: 1.0.0  
**Status**: CANONICAL SPECIFICATION  
**Phase**: Phase 31–33 (Project Capability Layer)  
**Authors**: AntiOS Core Architecture Team  

---

## 1. Executive Purpose

Phase 28–30 answered:
> *"Where is the relevant knowledge?"* (Knowledge graph, component boundaries, transitive dependencies, blast radius).

Phase 31–33 answers:
> *"Given this project, this subsystem, this component, and this task, what engineering capabilities should the agent use and why?"*

The system executes the canonical resolution pipeline:
```text
PROJECT
  ↓
PROJECT KNOWLEDGE
  ↓
TASK / CHANGE INTENT
  ↓
CAPABILITY RESOLUTION
  ↓
SKILL · RULE · WORKFLOW · TOOL · VERIFIER · SPECIALIST · PROVIDER · MCP
```

---

## 2. The Four Cardinal Demarcations

AntiOS explicitly maintains four distinct concepts:

| Demarcation | Definition | Implementation |
| :--- | :--- | :--- |
| **PROJECT KNOWLEDGE** | What the project is and where things are | `KnowledgeGraph`, `WayfindingEngine`, `LocalityResolution` |
| **PROJECT CAPABILITY** | How agents should work on the project | `CapabilityRegistry`, `Capability` entities across 8 types |
| **TASK ROUTING** | Which subset of those capabilities is relevant now | `TaskIntent`, `CapabilityRouter`, deterministic scoring |
| **CAPABILITY PACK** | Bounded agent-facing bundle for the current task | `CapabilityPack` ($\le 25$ lines card, JSON format, L0–L5) |

---

## 3. Four-Tier Architectural Hierarchy

```text
+-------------------------------------------------------------------------------+
|                       TIER 1: ANTIGRAVITY PLATFORM                            |
| Native agent runtime, stdio IPC hooks, interactive planning UI, tool execution|
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                         TIER 2: ANTIOS CORE                                   |
| Universal governance: Guard, Gate, Verdict, Lifecycle, Registry, Router, Pack |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       TIER 3: PROJECT ADAPTER                                 |
| Declarative bindings (antios.config.json), test runners, custom capabilities  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       TIER 4: TARGET PROJECT                                  |
| Domain source code, local manifests, test suites, schemas                     |
+-------------------------------------------------------------------------------+
```

AntiOS Core remains **100% universal and domain-agnostic**. No application-specific, framework-specific, or single-language concepts are hardcoded into Core.

---

## 4. Capability Lifecycle & Epistemic Authority

Every capability carries explicit epistemic status:
```text
OBSERVED (1.0) ──► CANDIDATE (0.3) ──► VALIDATED (0.8) ──► DURABLE (1.0)
```
- **OBSERVED**: Extracted from physical codebase manifests or verified execution.
- **INFERRED**: Derived through deterministic heuristic matching.
- **UNKNOWN**: Explicit gap where no capability or subsystem maps to the intent (confidence `0.0`). AntiOS never hallucinates missing capabilities.
