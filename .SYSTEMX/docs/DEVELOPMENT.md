# Development

## Architecture and implementation

Read the existing source, tests, configuration, and accepted decisions first.
State the behavior to change and its acceptance criteria before implementation.
Use the project's language and conventions. Prefer clear boundaries and small
modules over speculative frameworks or unneeded dependencies.

Document entry points, service boundaries, ownership, data flow, failure modes,
and external contracts in [architecture](../templates/ARCHITECTURE.md). Record
substantial tradeoffs with a [decision](../templates/DECISION.md). Avoid writing
a second architecture document for facts already captured elsewhere.

Validate input at trust boundaries. Handle cancellation, timeouts, retries,
partial failure, and resource cleanup when applicable. Use idempotency for
repeatable external writes and document the actual failure behavior. Treat
dependency upgrades as changes requiring compatibility checks, not housekeeping
that automatically belongs in every task.

## Data and integrations

Identify authoritative data sources, schemas, migration ownership, retention,
backup, and restore requirements. Version migrations and plan compatibility
across releases. Test on representative sanitized fixtures before touching
shared or production data. A backup is useful only if restore is understood.

Keep provider-specific code behind explicit interfaces when that boundary is
useful. Document required permissions, rate limits, webhook authenticity, retry
behavior, idempotency, and reconciliation. Use the
[connector standard](../AI/EXTERNAL-SERVICE-CONNECTOR-STANDARD.md) where applicable.

## User experience and accessibility

For user-facing work, define the intended user journey and inspect the result
in the actual target surface. Cover loading, empty, success, error, disabled,
and permission states that the feature can reach.

Use semantic controls, accessible names, visible keyboard focus, meaningful
reading order, readable contrast, and understandable error feedback. Check
keyboard access, zoom or scaling, reduced motion, and responsive layouts where
applicable. Record the accessibility target chosen by the project and validate
it with appropriate automated and manual checks. Do not claim conformance from
one automated test.

## Content, design, and media

Use the project's approved voice, terminology, visual tokens, and asset rights.
Replace starter copy with verified product facts. Keep claims about sourcing,
pricing, security, availability, and features aligned with actual behavior.
Do not imply an integration is live when it is a fixture or placeholder.

Handle localization, dates, currencies, search metadata, discoverability, and
privacy disclosures only where applicable. Optimize media for its use, retain
required attribution, and provide useful alternate text for meaningful images.

## Performance and maintainability

Measure a relevant baseline before optimization. Choose budgets suited to the
product: response time, startup, memory, bundle size, battery, throughput, or
operating cost. Check regressions against representative workloads. Explain
non-obvious constraints close to the code and keep documentation runnable.
