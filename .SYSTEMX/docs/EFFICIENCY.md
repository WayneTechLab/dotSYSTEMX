# Tokens, cost, and processing time

`.SYSTEMX` can reduce repeated context and avoidable work by giving an LLM a
small, current project handoff instead of asking it to rediscover the project
from a long transcript. Savings depend on how the host assistant loads files,
which model is used, caching, generated output, tool calls, and task difficulty.
There is no automatic token compressor, billing integration, or measured savings
claim built into this template.

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
defaults and current project records in the [entry-point order](../START-HERE.md).
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

## Fixed review without automatic reprocessing

Agent Z keeps the same 100 questions for a policy version and reuses unchanged
requests/reports. Agent X links observations to original event times and revisions.
Load these records only for a relevant decision; they are not appended to every
context packet. A scorecard does consume review effort and model context if an
LLM evaluates it. Group work into meaningful acceptance boundaries, retain valid
evidence, and repeat checks only for changed inputs or unresolved concerns.
No fixed savings or automatic 10,000-event throughput is promised.
