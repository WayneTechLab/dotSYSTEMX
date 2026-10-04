# Tokens, cost, and processing time

`.SYSTEMX` can reduce repeated context and avoidable work by giving an LLM a
small, current project handoff instead of asking it to rediscover the project
from a long transcript. Savings depend on how the host assistant loads files,
which model is used, caching, generated output, tool calls, and task difficulty.
There is no automatic token compressor, billing integration, or measured savings
claim built into this template.

## A practical example

Imagine resuming a feature after a week away. A transcript may contain several
abandoned approaches, raw test output, and repeated explanations. A maintained
handoff can instead point to the accepted requirement, current revision, two
open tasks, the relevant check result, and the next action. The assistant still
opens the underlying evidence when needed, but it has a clearer starting point.

The potential saving comes from avoiding unnecessary rediscovery and rework.
Keeping the original acceptance criteria visible also helps detect drift before
it becomes another implementation cycle. Follow [Daily workflow](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Daily-Workflow)
and [Anti-drift and long-running work](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Anti-Drift-and-Long-Running-Work) to create
those records as part of actual work.

## Where the benefit comes from

| Mechanism | Potential benefit | Required practice |
| --- | --- | --- |
| One task ledger and generated status views | Less conflicting or repeated status text | Edit canonical records; load only the view needed |
| Current focus and checkpoint | Fewer planning restarts and repeated investigations | Record verified progress and the exact next action |
| Bounded `context --agent agent.0` | Smaller resume input than a full history dump | Load the packet plus original instructions and relevant evidence |
| Scoped `task-packet` and worker memory | Less unrelated context per worker | Give each worker the actual acceptance criteria and dependencies |
| Project memory with source references | Less repeated discovery | Keep durable facts concise and recheck volatile facts |
| Argument-array local commands | Less repeated command reconstruction | Configure real checks and preserve their results and scope |

The current context command limits individual document excerpts to 6,000
characters, task summaries to 2,000 characters, and displayed relevant tasks to
25. Worker packets limit their JSON excerpt to 14,000 characters and selected
worker memory to 3,000 characters. These are **character limits, not token
budgets**. Truncation markers direct the reader to the original files; omitted
acceptance criteria or evidence must still be read. A chat export also includes
selected default guidance and can be larger than a context packet.

Do not load every generated status page, all worker memories, every historical
checkpoint, and every retained default snapshot on every turn. Load the selected
defaults and current project records in the [entry-point order](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/START-HERE.md).
Compaction is useful only while the model retains enough information to do the
work correctly. Extra workers and repeated context packets can increase usage.

## What this can mean for money

For usage-priced APIs, fewer billable tokens or fewer unnecessary requests can
lower costs. Distinguish uncached input, cached input, output, reasoning, and tool
charges according to the provider's actual usage fields and current rates.
Fixed-price subscriptions may yield more available capacity without changing
the subscription bill. `.SYSTEMX` itself does not call an LLM or meter billing.

Illustrative arithmetic, **not a benchmark**: replacing 20,000 input tokens with
5,000 equally sufficient tokens avoids 15,000 input tokens per request, or
1.5 million over 100 requests. That is a 75% reduction in that input component.
For entirely uncached input billed at `R` currency units per million tokens,
the corresponding input saving would be `1.5 × R`. Output, cached input, other
charges, and additional requests must be accounted for separately. It is not a
75% claim about total cost.

## What this can mean for time

Smaller context may reduce prompt processing. Clear checkpoints can also avoid
repeating searches, tests, tool calls, and planning. End-to-end time still depends
on model generation, reasoning, queues, network latency, and external tools.
A reduction in input tokens does not imply the same percentage reduction in
latency. OpenAI's [latency guide](https://developers.openai.com/api/docs/guides/latency-optimization)
describes output generation as a major contributor and notes that input reduction
often has a smaller effect. Its [cost guide](https://developers.openai.com/api/docs/guides/cost-optimization)
discusses minimizing token usage; those provider principles are not measurements
of this template.

## Measure your own result

Compare representative tasks with the same model, tools, acceptance criteria,
and comparable cache conditions. Record input/cached/output token usage, tool
calls, elapsed time, retries, and accepted outcomes for a full-history baseline
and a focused `.SYSTEMX` handoff. Include the cost of generating and maintaining
the handoff. Use several runs and report variation, not just the fastest result.
Accept a smaller packet only if the resulting work still meets the same criteria.
Store sanitized measurements in the adopted project, never in the blank template.

Compare total usage across Agent 0 and every worker, including failed runs,
retries, integration, review, and checkpoint maintenance. Parallel work can
finish sooner while costing more. A requested ten-worker ceiling is a capacity
limit, not an efficiency target. Start with the workers the task needs.

| Measure | Record for both approaches |
| --- | --- |
| Accepted outcome | Same requirement and evidence standard |
| Context and generation | Provider-reported input, cached input, output, and any separately reported usage |
| Coordination | Number of workers, packet preparation, reviews, and retries |
| Tools and time | Tool calls and wall-clock time through accepted completion |
| Rework and drift | Reopened work, repeated investigation, and unapproved scope changes |
| Total cost | Applicable usage charges across the complete workflow |

Do not add a separately reported token category twice if the provider already
includes it in another usage field. Use the provider's current accounting rules.
Keep comparisons illustrative until you have reproducible measurements from
your own project. No usage data is collected or uploaded by `.SYSTEMX` itself.

## Select only the relevant project

[SYSTEMX PROJECTS](PROJECTS.md) lets a session load one child's `.SYSTEMXP`
context instead of combining every project's backlog and history. This can reduce
irrelevant input and accidental drift across channels. Root status lists identities
without importing child memory. Selected-ledger validation may still read the
full local ledger; compact model output is not a guarantee of constant processing
time. Measure actual tokens, latency, accepted outcomes, and rework for your workflow.

## Fixed review without automatic reprocessing

Agent Z keeps the same 100 questions for a policy version and reuses unchanged
requests/reports. Agent X links observations to original event times and revisions.
Load these records only for a relevant decision; they are not appended to every
context packet. A scorecard does consume review effort and model context if an
LLM evaluates it. Group work into meaningful acceptance boundaries, retain valid
evidence, and repeat checks only for changed inputs or unresolved concerns.
No fixed savings or automatic 10,000-event throughput is promised.

## Research quality and coordinated turns

A deep-research brief can reduce guessing and later rework when it provides
relevant verified facts, source references, constraints, and acceptance criteria.
Keep the full evidence index, but load only the context required by the selected
task. More raw information is not automatically better: unrelated, stale, or
contradictory input consumes attention and tokens. Record uncertainty explicitly.

Phases and waves give the coordinator useful checkpoints; bounded workers return
reviewable summaries; X timestamps and Z scorecards preserve meaningful evidence.
This can make later turns better informed without retraining the model. Measure
research, coordination, integration, and review costs together. Compare accepted
outcomes, not agent count or prompt length. See [the one-shot guide](ONE-SHOT-PROJECT.md).
