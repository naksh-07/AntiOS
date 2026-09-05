# AntiOS 2.0 Agent-Native Mission Benchmark (Phase 92)

## 1. Benchmark Purpose & Scope
The AntiOS Agent-Native Mission Benchmark measures **engineering workflow quality and governance confinement**, NOT raw LLM model intelligence. It evaluates whether project wayfinding, context budgeting, safe compaction, wave orchestration, and independent verification improve software engineering outcomes over a naive agent baseline.

---

## 2. Explicitly Labeled Proxy Metrics
All measurements are explicitly labeled as proxies:
- `time_to_correct_location_proxy`: Steps before first authoritative file identified.
- `unnecessary_files_inspected`: Files inspected outside target subsystem or dependency closure.
- `context_consumed_tokens_proxy`: Estimated tokens across all prompt/tool interactions.
- `tool_calls_count`: Total tool calls executed.
- `workforce_launches`: Total worker subagents spawned.
- `active_workers_per_wave_peak`: Maximum concurrent workers in any wave.
- `redundant_work_count`: Repeated identical queries or duplicate tool invocations.
- `failed_attempts`: Errors or test failures encountered prior to resolution.
- `recovery_events`: Crash recoveries and context refreshes executed.
- `verification_attempts`: Test suite or verifier runs executed.
- `final_correctness`: Boolean indicator of independent verified PASS.
- `evidence_completeness_ratio`: Verified evidence items / required acceptance criteria.
- `mission_completion_cost_proxy`: Deterministic composite score.

---

## 3. BASELINE vs ANTIOS Comparison Model
- **`BASELINE`**: Represents a naive, ungoverned workflow (unbudgeted context, no wave collapse, unverified worker claims, unbounded tool outputs).
- **`ANTIOS`**: Governed workflow (wayfinding, context budget governor, safe compactor, wave collapse, maker-checker verification).

### Conservative Outcome Language
AntiOS never claims unsupported causal percentages. It categorizes comparative outcomes strictly into:
- **`OBSERVED_IMPROVEMENT`**: Deterministically superior metrics under AntiOS.
- **`MEASURED_DIFFERENCE`**: Observable divergence without strict Pareto dominance.
- **`INSUFFICIENT_DATA`**: Insufficient data points or identical outcomes.

---

## 4. Controlled Proving-Ground Scenarios (A through J)
Ten deterministic synthetic fixtures:
- **Scenario A**: Simple single-file change (Solo workforce, minimal context)
- **Scenario B**: Multi-file feature change (Disjoint modules, bounded wave orchestration)
- **Scenario C**: Targeted frontend change (Visual/component isolation, bounded tool output)
- **Scenario D**: Test failure requiring diagnosis (Deterministic error trace, fix, verify)
- **Scenario E**: Stale context after repository mutation (Detect hash drift, mandatory refresh)
- **Scenario F**: Interrupted multi-wave mission (Recovery engine preserves launch budget, resumes wave)
- **Scenario G**: Conflicting evidence (Two tools disagree $\rightarrow$ CONFLICTING state $\rightarrow$ INCONCLUSIVE)
- **Scenario H**: Incorrect worker success claim (Worker claims PASS without test evidence $\rightarrow$ fail-closed FAIL)
- **Scenario I**: Unnecessary exploration trap (Unbounded grep/file crawl vs targeted wayfinding)
- **Scenario J**: Large tool-output/context pressure (Oversized stdout $>2000$ chars $\rightarrow$ truncated with SHA-256)

---

## 5. Benchmark Safety Invariants
Benchmark execution never weakens or bypasses AntiOS constitutional rules:
- Max 10 active agents per wave
- Max 20 lifetime launches per mission
- Delegation depth $\le 2$
- Mandatory wave collapse
- Single-writer write safety
- Fail-closed verification
