# Codebook

738 mechanism instances from 19 repositories, 10 categories, 43 mechanisms. Instance IDs have the form `<owner>_<repo>#<index>`, where the index is the 0-based position in the `resilience` array of `manual_coding/<owner>_<repo>/coding.json`.

## Pattern labels

- **classic**: direct counterpart in the Azure pattern catalogue, transferred unchanged.
- **adapted**: classic counterpart whose trigger or semantics change for LLMs.
- **agent-specific**: no classic counterpart; exists because an LLM makes the decision.

## Assignment rules

1. An instance is assigned by the failure class it protects against. Its location in the code is irrelevant.
2. Enforcement (code, config, prompt) is a variation point. A limit stated only in a prompt is `run_limits` with enforcement `prompt`.
3. An instance that bundles several mechanisms receives one primary mechanism.
4. Duplicates of the same construct are merged into one instance (`merged_ids`).

## Variation points

| Field | Values |
|---|---|
| trigger | exception, threshold, validation, llm-judgment, human, other |
| decider | code, llm, human |
| reaction | abort, retry, fallback, degrade, block, feedback-to-llm, escalate-human, escalate-parent, other |
| activation | always, default_on, opt_in |
| enforcement | code, config, prompt |
| works_as_claimed | yes, no (the code path cannot do what name, comment or documentation promise), unclear (undecidable from code) |
| delegation_specific | yes if the instance exists because an agent delegates to another agent |

## Exclusions

Pure cost or latency optimisation without a failure behind it; tracing, metrics, audit logs and offline evaluation; input debouncing; bot-detection evasion; load spreading that ignores errors; domain logic; validation of developer configuration at load time; generic web-server code; platform security (authentication, authorisation, SSRF).

## Changes from codebook v1 to final

1. `duplicate_call_suppression` merged into `stagnation_control` (suppressing and detecting a repeated call are reaction variants of one mechanism).
2. `plan_replan` kept separate from `self_verification` (plan binding enforced by code is no self-check).
3. `non_blocking_delegate` became a variant of `exec_bounds` (occurs in one repository only).
4. Asynchronous offloading became a variant of `exec_bounds`.
5. Blind re-sampling became a variant of `output_validation_feedback`.
6. New reaction value `escalate-parent`.
7. Five instances corrected (`SWE-agent_mini-swe-agent#5` and `ltjed_freephdlabor#1` removed from `checkpoint_resume`, `promptise-com_Foundry#123` removed from `caching`, `pikpikcu_airecon#47` moved from `llm_critic` to `self_verification`, `promptise-com_Foundry#162` redescribed).
8. One pattern label per mechanism.

---

## K1 External dependencies
Failure class: a call to an external service (LLM provider, MCP server, web or data API, real-time stream, browser or shell process) fails transiently, hangs, is throttled, or is rejected.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `ext_retry` | The same call is repeated automatically after an error. | Changed request → `ext_request_degradation`; other model or key → `ext_fallback`; whole run → `run_retry`; error sent to the model → `output_validation_feedback`. | `SWE-agent_mini-swe-agent#13`, `volcengine_OpenViking#23` | classic |
| `ext_timeout` | Time bound on an external call, including stream idle watchdogs. | Agent-chosen tool or code → `exec_bounds`; total run time → `run_limits`. | `AgentEra_Agently#3`, `HKUDS_DeepTutor#6` | classic |
| `ext_fallback` | On error, another provider of the same capability is used (model, provider, credential, data source). | Same endpoint with a reduced request → `ext_request_degradation`. | `bubbuild_bub#1`, `AgentEra_Agently#4` | classic |
| `ext_request_degradation` | The same provider is called again with a reduced or altered request because it lacks a capability or a limit was exceeded. | Model change → `ext_fallback`. | `HKUDS_DeepTutor#9`, `ArcReel_ArcReel#38` | adapted |
| `circuit_breaker` | After N failures the dependency is skipped for a period, with a half-open probe. | Prompt hint or run-abort counter → `stagnation_control`. | `promptise-com_Foundry#35`, `gptme_gptme#0` | classic |
| `connection_recovery` | A stateful session, stream or helper process is rebuilt after a break or rotated proactively. | Stateless request → `ext_retry`. | `GetStream_Vision-Agents#13`, `Lynpoint_CyberVerse#8` | classic |
| `caching` | Results of LLM, tool or data calls, or prompt prefixes, are reused to reduce external calls where rate limits, budget or timeouts are at stake. | Purely internal computation. | `langchain-ai_langgraph#6`, `HKUDS_DeepTutor#11` | classic |

## K2 Execution and containment
Failure class: an action or sub-step raises, hangs or exhausts resources and would otherwise abort the run or propagate.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `tool_error_feedback` | Exceptions and unknown tool names are caught and returned as tool results; the model decides how to react. | Invalid output format or arguments → K3. | `langchain-ai_langgraph#7`, `HKUDS_Vibe-Trading#8` | agent-specific |
| `exec_bounds` | Timeouts and resource limits (CPU, memory, processes) on agent-triggered execution. | Output truncation → `tool_output_reduction`; host isolation → `sandbox_isolation`. | `gptme_gptme#23`, `pikpikcu_airecon#0` | classic |
| `unit_failure_isolation` | Each unit (node, step, sub-agent, batch item) runs in its own error scope; its failure becomes a status and the others continue. | Error returned to the model → `tool_error_feedback`; dependents blocked → `dependency_failure_handling`. | `HKUDS_DeepTutor#27`, `promptise-com_Foundry#107` | classic |
| `dependency_failure_handling` | The failure of a task determines what happens to dependent tasks in a task graph. | No dependency structure → `unit_failure_isolation`. | `HKUDS_Vibe-Trading#25`, `ArcReel_ArcReel#33` | classic |
| `graceful_degradation` | When an optional subsystem fails, the agent continues with reduced function. | Equivalent alternative → `ext_fallback`. | `promptise-com_Foundry#30`, `strands-agents_samples#43` | classic |
| `run_retry` | A complete agent run, job or attempt is restarted after failure. | Single call → `ext_retry`. | `strands-agents_samples#17`, `HKUDS_Vibe-Trading#24` | adapted |

## K3 Output validity
Failure class: the LLM output is syntactically or structurally unusable (broken JSON, wrong protocol, schema violation, truncation, inapplicable patch).

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `constrained_generation` | The format is enforced before generation (structured output, forced tool choice, schema in the prompt). | Checked afterwards → `output_validation_feedback`. | `LvcidPsyche_auto-browser#10`, `ArcReel_ArcReel#15` | agent-specific |
| `output_repair` | Code tolerates or repairs broken output without a new LLM call. | Model asked again → `output_validation_feedback`. | `volcengine_OpenViking#1`, `AgentEra_Agently#5` | agent-specific |
| `output_validation_feedback` | Output or action is checked against rules; on violation the model receives the error and generates again. Includes blind re-sampling. | Content check → K4; repeated abort → `stagnation_control`. | `SWE-agent_mini-swe-agent#0`, `HKUDS_DeepTutor#0` | adapted |

## K4 Reasoning quality
Failure class: the output is well-formed and wrong in content, unsupported, hallucinated or incomplete; the agent declares itself done prematurely.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `completion_gate` | Code checks postconditions or evidence before a result or "done" is accepted. | LLM judges → `llm_critic`; structural check → K3. | `LvcidPsyche_auto-browser#23`, `ltjed_freephdlabor#8` | agent-specific |
| `llm_critic` | A separate LLM call or agent evaluates the result during the run; the verdict drives revision or routing. | Judge after the run → excluded; same agent → `self_verification`. | `strands-agents_samples#28`, `promptise-com_Foundry#13` | agent-specific |
| `self_verification` | The acting agent is made to check its own result (prompt, hook or phase). | Other instance → `llm_critic`; code → `completion_gate`. | `HKUDS_Vibe-Trading#15`, `ArcReel_ArcReel#23` | agent-specific |
| `grounding` | Claims are tied to data or tool results: facts are injected beforehand or evidence rules are enforced. | Checked afterwards → `completion_gate` or `llm_critic`. | `HKUDS_Vibe-Trading#29`, `volcengine_OpenViking#3` | agent-specific |
| `plan_replan` | An explicit plan artefact; progress is checked against it and replanning is bounded. | Iteration bound only → `run_limits`. | `HKUDS_DeepTutor#18`, `ltjed_freephdlabor#3` | agent-specific |
| `experience_learning` | Failures and successes are persisted and influence later runs. | Knowledge stays in the current context → `tool_error_feedback`. | `promptise-com_Foundry#59`, `HKUDS_AnyTool#13` | agent-specific |

## K5 Loop control
Failure class: the agent runs endlessly, stagnates, repeats itself, lets cost or time escalate, or stops without a usable result.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `run_limits` | Upper bound on steps, turns, cost, tokens, tool calls, delegations or wall-clock time. | A final result produced at the limit → `graceful_finalization`. | `langchain-ai_langgraph#3`, `SWE-agent_mini-swe-agent#2` | adapted |
| `graceful_finalization` | When a limit or error approaches or is reached, the model is brought to a final answer. | Plain abort → `run_limits`. | `HKUDS_Vibe-Trading#3`, `HKUDS_DeepTutor#1` | agent-specific |
| `stagnation_control` | Detects patterns without progress (repetition, empty or text-only turns, repeated errors, handoff ping-pong) and reacts with a nudge, block, escalation or abort. Includes suppression of duplicate tool calls. | | `gptme_gptme#29`, `LvcidPsyche_auto-browser#0` | agent-specific |

## K6 Action safety
Failure class: the agent performs a harmful, irreversible, unauthorised or out-of-scope action, or untrusted content manipulates it.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `sandbox_isolation` | Actions run isolated from the host (container, OS sandbox, worktree, restricted builtins). | Path checks only → `access_confinement`. | `SWE-agent_mini-swe-agent#18`, `promptise-com_Foundry#156` | classic |
| `access_confinement` | Addressable resources (paths, hosts, scope) are limited to an allowlist or workspace. | | `volcengine_OpenViking#20`, `ArcReel_ArcReel#2` | classic |
| `action_policy_guard` | A rule-based policy blocks or defuses actions before execution. | Human decides → `approval_gate`; content scanned → `content_guardrail`. | `gptme_gptme#21`, `LazyAGI_LazyLLM#16` | classic |
| `content_guardrail` | Input, tool output or model output is scanned for injection, PII, toxicity or secrets and blocked, redacted or flagged. | | `strands-agents_samples#0`, `promptise-com_Foundry#43` | agent-specific |

## K7 Human control
Failure class: the agent continues wrongly or unsafely because nobody can intervene (unclear task, dead end, risky action).

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `approval_gate` | An action, plan or stage runs only after human confirmation. | Human intervenes on own initiative → `human_intervention`. | `SWE-agent_mini-swe-agent#6`, `promptise-com_Foundry#49` | agent-specific |
| `human_intervention` | A channel for asking the user, interrupting, taking over or escalating, where it addresses a failure case. | Chat pause without failure reference → excluded. | `ltjed_freephdlabor#6`, `lsdefine_GenericAgent#14` | agent-specific |

## K8 State
Failure class: progress or state is lost or becomes inconsistent on crash, abort or restart.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `checkpoint_resume` | Progress is persisted; a new run continues from it. | Logged and never read back → excluded. | `langchain-ai_langgraph#5`, `LvcidPsyche_auto-browser#6` | classic |
| `rollback` | A previous state is restored when a change fails or is unwanted. | | `gptme_gptme#16`, `ArcReel_ArcReel#0` | classic |
| `state_integrity` | Locks, leases, idempotency, terminal-state guards, atomic writes, reconciliation with the outside world. | | `ArcReel_ArcReel#29`, `HKUDS_Vibe-Trading#34` | classic |

## K9 Context
Failure class: the context window overflows or the context degrades (pollution, lost key information).

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `llm_compaction` | Old history is replaced by an LLM-generated summary. | Deterministic cut → `history_trimming`. | `HKUDS_Vibe-Trading#1`, `strands-agents_samples#11` | agent-specific |
| `history_trimming` | Deterministic sliding window, stubbing or pruning of the history. | | `HKUDS_AnyTool#2`, `HKUDS_Vibe-Trading#0` | agent-specific |
| `tool_output_reduction` | Tool results are shortened or offloaded to a file before entering the context. | | `SWE-agent_mini-swe-agent#21`, `volcengine_OpenViking#25` | agent-specific |
| `context_budgeting` | The context is assembled under a budget; only relevant parts are loaded (incl. progressive disclosure of tools). | | `promptise-com_Foundry#62`, `volcengine_OpenViking#15` | agent-specific |
| `context_isolation` | Work is moved into a separate context (sub-agent, side channel) to keep the main context clean. | Delegation for division of labour only → excluded. | `bubbuild_bub#8`, `ArcReel_ArcReel#18` | agent-specific |

## K10 Load, latency and lifecycle
Failure class: overload, resource exhaustion, orphaned or hanging sessions and processes, start in a broken state; in real-time systems, excessive latency or answers to stale input.

| Mechanism | Definition | Boundary | Examples | Pattern |
|---|---|---|---|---|
| `load_limiting` | Limits on incoming load, internal concurrency or outgoing call rate. | | `promptise-com_Foundry#68`, `LvcidPsyche_auto-browser#7` | classic |
| `lifecycle_cleanup` | Idle, hanging or dead sessions and processes are detected and cleaned up; orderly shutdown. | | `gptme_gptme#41`, `GetStream_Vision-Agents#0` | classic |
| `health_preflight` | Dependencies are checked before use or start; fail fast on critical errors. | | `HKUDS_Vibe-Trading#52`, `LazyAGI_LazyLLM#24` | classic |
| `realtime_turn_control` | A real-time agent answers in time and to the current input (latency hiding, barge-in). Applies only where latency itself is the failure. | General cost or latency optimisation → excluded; reuse of results → `caching`. | `GetStream_Vision-Agents#4`, `Lynpoint_CyberVerse#14` | adapted |
