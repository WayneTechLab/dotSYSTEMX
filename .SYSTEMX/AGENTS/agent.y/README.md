# Agent Y: delegated CLI work

This is the optional `agent.y` (`cli-worker`) role definition, not an active CLI process,
installed provider, or permission grant. The public agent registry remains
Agent 0 only. Activate this role explicitly in the selected root or
`.SYSTEMXP` scope with compatible tools, and keep its memory blank until an
authorized project assignment is recorded.

Read the [Agent Y guide](../../docs/AGENT-Y.md). Agent 0 owns task selection,
integration, and acceptance. Agent Y owns one bounded provider handoff and only
the task branch/PR operations allowed by its recorded policy. Its scoped
`JOBS.json` tracks handoffs and observations, not canonical task state. Agent X tracks
observed events; Agent Z reviews evidence. The host environment supplies model,
CLI runtime, credentials, GitHub permissions, and process control.
