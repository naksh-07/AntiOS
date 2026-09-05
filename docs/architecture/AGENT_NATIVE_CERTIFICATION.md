# Agent-Native Certification Specification (`docs/architecture/AGENT_NATIVE_CERTIFICATION.md`)

## 1. Overview
Agent-Native Certification is the formal verification framework within AntiOS 2.0 (`framework/core/agent_native_certification.py`) that evaluates a repository's readiness for autonomous agent engineering against observable evidence.

CLI Entrypoint:
```bash
python framework/scripts/tools/certify_agent_native.py [path] [--json] [--strict]
```

---

## 2. Certification Tiers

| Level | Score Range | Criteria & Requirements | Certified Status |
|---|---|---|:---:|
| `NOT_READY` | 0.0 – 49.9 | Critical safety/integrity violations or severe missing infrastructure | **NO** |
| `BASELINE` | 50.0 – 69.9 | Basic structure present, but notable unknowns or unmapped components | **NO** |
| `AGENT_READY` | 70.0 – 84.9 | Functional wayfinding, passing test runner, bounded friction | **YES** |
| `HIGHLY_AGENT_NATIVE` | 85.0 – 94.9 | Strong project anatomy, clean manifest ownership, low friction | **YES** |
| `CERTIFIED` | 95.0 – 100.0 | Near-perfect across all 10 dimensions, 0 critical/high friction | **YES** |

---

## 3. Fail-Closed Security Invariants
Certification **unconditionally fails closed** to `NOT_READY` if ANY of the following occur:
1. **Forbidden Workflows**: Legacy `.agents/workflows/` directory exists.
2. **Shallow Depth Law Violation**: Any specialist skill claims `can_delegate=True` or depth exceeds 2.
3. **Manifest Corruption**: `.antios/manifest.json` is malformed or cryptographic hashes drift.
4. **Verification Failure**: The configured automated test runner fails to execute or exits non-zero.
5. **Unauthorized Privilege Escalation**: Unauthorized MCP configurations bypass tool policy.

---

## 4. Certification Report Format
Formal certification output emits a structured evidence card:
```text
AGENT_NATIVE_CERTIFICATION
Project:          <path>
Fingerprint:      <sha256-16>
AntiOS Instance:  AntiOS 2.0.0 (Phase 78 Certified)
Timestamp:        <iso8601>

Overall Score:    XX.X / 100
Status Level:     <LEVEL> (Confidence: <CONFIDENCE>)
Certified Pass:   <YES|NO>
------------------------------------------------------------
Dimension Scores:
  WAYFINDING               :  XX.X
  DOCUMENTATION            :  XX.X
  SKILLS                   :  XX.X
  AGENTS                   :  XX.X
  OWNERSHIP                :  XX.X
  VERIFICATION             :  XX.X
  MEMORY_KNOWLEDGE         :  XX.X
  TOOLING                  :  XX.X
  PROJECT_STRUCTURE        :  XX.X
  ORCHESTRATION_READINESS  :  XX.X
------------------------------------------------------------
CRITICAL FINDINGS (FAIL-CLOSED):
  [CRITICAL] ...
HIGH FRICTION:
  [HIGH] ...
MEDIUM FRICTION:
  [MEDIUM] ...
LOW FRICTION:
  [LOW] ...
UNKNOWN AREAS:
  ? ...
RECOMMENDATIONS:
  -> ...
```
