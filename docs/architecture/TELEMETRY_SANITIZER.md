# AntiOS 2.1 Telemetry Sanitizer & Privacy Engine (`docs/architecture/TELEMETRY_SANITIZER.md`)

## 1. Overview & Primary Objective

AntiOS 2.1 establishes a **Deterministic, Fail-Closed Telemetry Sanitizer & Privacy Engine** (`framework/core/sanitizer.py`).
Its sole mandate is to act as the non-bypassable security boundary through which all future telemetry must pass before reaching the Central Experience Store (`experience.db`).

```text
Antigravity / Runtime Event (Future Phase 105)
             ↓
         Raw Event
             ↓
 ┌─────────────────────────────────────────┐
 │   Telemetry Sanitizer & Privacy Engine  │  ← Phase 104
 │   - Fail-Closed Redline Enforcement     │
 │   - Layered Secret Redaction            │
 │   - Workspace Boundary Protection       │
 │   - Prompt & CoT Exclusion              │
 │   - Error & Diagnostics Normalization   │
 │   - Bounded Payload Envelopes           │
 └────────────────────┬────────────────────┘
                      ↓
              Normalized Safe Event
                      ↓
               Experience Store               ← Phase 103
```

---

## 2. Constitutional Privacy Boundary & Collection Redlines

The sanitizer is strictly **FAIL-CLOSED**: if the system cannot confidently determine that a field is safe to persist, it must **REDACT** or **DROP**. It never stores raw untrusted data.

### Categorical Collection Redlines
The following data categories are **permanently prohibited from entering storage, logs, or exports**:
1. **Credentials & Secrets**:
   - Passwords, API keys, Personal Access Tokens (PAT), private keys, SSH keys, certificates, bearer tokens, session tokens, refresh tokens.
2. **HTTP Authentication**:
   - `Authorization` headers, `Proxy-Authorization` headers, `Cookie` / `Set-Cookie` headers.
3. **Sensitive Files & Credentials**:
   - `.env`, `.env.*`, `credentials.json`, `secrets.yaml`, `id_rsa`, `id_ed25519`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `.npmrc`, `.pypirc`.
4. **Machine & Personal Boundary Violations**:
   - System clipboard contents, OS keystroke logs, files outside the governed project root (e.g. `~/Documents`, `~/Downloads`, OS system directories).
   - User home directory traces (automatically relativized or replaced with `~`).
5. **Model Reasoning & Internal History**:
   - Raw model Chain-of-Thought (CoT), `thinking` deltas, `thought` fields, internal reasoning tokens.
   - Raw user prompts and conversational transcripts.
   - Hidden instructions or system directives.

> [!CAUTION]
> **No CoT Sanitization**: AntiOS does not attempt to "sanitize" chain-of-thought into a persistent format. Chain-of-thought is excluded entirely (0 bytes).

---

## 3. Layered Secret Redaction Engine

The redaction engine employs a multi-tiered, compiled regex hierarchy:

| Tier | Target Patterns | Redaction Token |
| :--- | :--- | :--- |
| **Tier 1: High-Entropy Provider Keys** | Google API keys (`AIza...`), GitHub PAT/OAuth (`ghp_...`, `github_pat_...`), Anthropic (`sk-ant-...`), OpenAI (`sk-...`), AWS (`AKIA...`), Slack (`xox...`) | `[REDACTED_GOOGLE_API_KEY]`, `[REDACTED_GITHUB_TOKEN]`, etc. |
| **Tier 2: Private Key Blocks** | RSA, DSA, EC, OPENSSH private key blocks (`-----BEGIN ... PRIVATE KEY-----`), inline SSH private keys | `[REDACTED_PRIVATE_KEY]`, `[REDACTED_SSH_KEY]` |
| **Tier 3: Auth Headers & Tokens** | `Authorization: Bearer ...`, `Cookie: ...`, standalone JWT tokens | `[REDACTED_AUTH_HEADER]`, `[REDACTED_COOKIE]`, `[REDACTED_JWT]` |
| **Tier 4: Connection URIs** | Database and network URIs with credentials (`postgres://user:pass@host`, `mongodb://...`, `redis://...`) | `proto://[REDACTED_USER]:[REDACTED_PASS]@host` |
| **Tier 5: Key-Value Secret Assignments** | JSON, YAML, shell, or CLI flag assignments (`password="xyz"`, `api_key: "xyz"`, `--password xyz`) | `[REDACTED_SECRET]` |

Every redaction decision is logged in structured audit records (`SanitizerDecision.REDACT`, `SanitizerReason.SECRET_DETECTED`) without ever retaining the sensitive data.

---

## 4. Sensitive Path Policy & Path Relativization

### Canonical Path Classification
Every path evaluated by `TelemetrySanitizer.classify_path(path, project_root)` produces an explicit classification:
- **`SAFE_PROJECT_PATH`**: Path resolves within `project_root` and does not match sensitive file patterns. Converted to a clean, forward-slash relative path (e.g. `src/auth/login.py`).
- **`SENSITIVE_PROJECT_PATH`**: Path resolves within `project_root` but references a sensitive file (`.env`, `credentials.json`, `id_rsa`, `*.pem`). Payload dropped or replaced with `[REDACTED_SENSITIVE_PATH]`.
- **`OUTSIDE_PROJECT`**: Path resolves outside `project_root` (including directory traversal `../../`, absolute system paths `C:\Windows\`, user personal files). Dropped or replaced with `[OUT_OF_WORKSPACE_PATH]`.
- **`UNKNOWN_PATH`**: Malformed or unresolvable paths. Dropped.

### Cross-Platform Normalization
- Standardizes backslashes (`\`) to forward slashes (`/`).
- Lowercases Windows drive letters (`C:` $\to$ `c:`).
- Normalizes `.` and resolves relative components without escaping project root.
- Replaces absolute home directory paths with `~` in error diagnostics.

---

## 5. Content Policy & Bounded Envelopes

To prevent database bloat, DoS payloads, and memory exhaustion, all telemetry fields are strictly bounded:

| Field / Component | Bound Ceiling | Truncation / Policy |
| :--- | :--- | :--- |
| `output_summary` | **500 chars** | Trailing ellipsis (`...`); full scrubbed SHA-256 retained |
| `payload_json` | **1,000 chars** | Trailing ellipsis (`...`) |
| Individual string argument | **2,000 chars** | Trailing ellipsis (`...`) |
| Relative files list | **20 files** | Truncated to first 20 safe paths |
| Stack trace message | **500 chars** | Absolute user paths scrubbed to `~` |
| Nested data structures | **10 levels** | Replaced with `[NESTING_LIMIT_EXCEEDED]` |
| Array elements | **50 items** | Truncated to first 50 items |
| Raw prompt | **0 chars** | Dropped; normalized to `{task_category, subsystem, normalized_intent}` |
| Raw Chain-of-Thought | **0 chars** | Prohibited keys dropped completely from payload dicts |

---

## 6. Prompt & Intent Normalization

Raw user prompts are **never stored**. Instead, `TelemetrySanitizer.normalize_intent()` extracts high-level engineering facts:
- `task_category`: e.g. `BUG_FIX`, `FEATURE_IMPLEMENTATION`, `VERIFICATION`, `REFACTOR`, `DOCUMENTATION`.
- `subsystem`: e.g. `auth`, `storage`, `governance`, `api`, `cli`, `telemetry`.
- `normalized_intent`: High-level synthesized summary (e.g. `BUG_FIX on auth`).

---

## 7. Error Sanitization & Engineering Utility

Diagnostics from failed commands, test runners, and compilers remain actionable while stripping sensitive artifacts:
- **Preserved Facts**:
  - `error_category`: `SYNTAX_ERROR`, `TEST_FAILURE`, `PERMISSION_DENIED`, `TIMEOUT`, `MISSING_RESOURCE`, `COMMAND_FAILURE`, `RUNTIME_EXCEPTION`.
  - `exception_type`: Standard exception class name (e.g. `AssertionError`, `SyntaxError`).
  - `affected_file`: Validated project-relative file path.
  - `test_name`: Name of failed test function (e.g. `test_login`).
  - `exit_code`: Numeric return code.
- **Scrubbed Data**:
  - Personal machine directory prefixes.
  - Embedded credentials, tokens, or environment dumps.

---

## 8. Anti-Poisoning & Epistemic Separation

1. **Untrusted Data Invariant**:
   - All incoming telemetry is treated as untrusted data.
   - Telemetry strings are never evaluated, executed, or used to alter AntiOS configuration, skills, rules, or governance.
2. **Prompt Injection Defanging**:
   - Scans text for injection signatures (`ignore previous instructions`, `bypass stop gate`, `override system prompt`).
   - Replaces matched directives with `[DEFANGED_INJECTION_DIRECTIVE]`.
3. **Epistemic Demarcation**:
   - Sanitization is NOT learning.
   - Sanitized events are observations (`FACT`), never `EVIDENCE`, `VERDICT`, `DECISION`, or `PROJECT_PROOF`.

---

## 9. Safe Event Contracts (Phase 105 Interface)

Phase 105 will consume two canonical contracts:

### `SafeToolCall`
```python
@dataclass
class SafeToolCall:
    call_id: str
    turn_id: str
    tool_name: str
    sanitized_args_json: str = "{}"
    exit_code: Optional[int] = None
    status: str = "SUCCESS"
    output_sha256: Optional[str] = None
    output_summary: str = ""
    duration_ms: int = 0
    created_at: str = ""
```

### `SafeEngineeringEvent`
```python
@dataclass
class SafeEngineeringEvent:
    event_id: str
    mission_id: str
    project_id: str
    event_type: str
    epistemic_grade: str
    affected_file: Optional[str] = None
    event_signature: str = ""
    payload_json: str = "{}"
    created_at: str = ""
    # Extended telemetry metadata
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    source: str = "runtime_telemetry"
    tool_category: Optional[str] = None
    normalized_intent: Optional[str] = None
    relative_files: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    error_category: Optional[str] = None
    duration_ms: int = 0
    exit_code: Optional[int] = None
    retry_count: int = 0
    sanitizer_version: str = "2.1.0"
```

Both contracts serialize cleanly to JSON and map 1:1 to SQLite tables `tool_calls` and `engineering_events` in `experience.db`.

---

## 10. Phase 104 Limitations & Invariants

> [!IMPORTANT]
> **Phase 104 builds the Privacy Boundary ONLY.**
> - **Telemetry collection is NOT active yet.**
> - **No platform transcript parsing is active.**
> - **No PostToolUse hooks or execution loops are connected.**
> - **Zero background daemons or processes exist.**
> - **Zero third-party dependencies are introduced.**
>
> Ingestion hooks and transcript tailing will be introduced in Phase 105. AntiOS 2.0 governance and freeze invariants remain 100% intact.
