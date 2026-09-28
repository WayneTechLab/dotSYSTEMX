# External Service Connector Standard

## Purpose

Projects often need external vendor dashboards, APIs, SDKs, CLIs, webhooks, and
browser-only flows. SYSTEMX treats each integration as a connector with a
generic contract, not as hard-coded product logic in the template.

## Connector Contract

Every connector should document:

| Field | Meaning |
| --- | --- |
| `connectorId` | Stable generic ID, for example `fulfillment_provider` or `analytics_provider`. |
| `mode` | `disabled`, `local`, `staging`, or `production`. |
| `authMethod` | OAuth, API key, service account, CLI login, or manual dashboard login. |
| `allowedActions` | Explicit verbs the project may call. |
| `readOnlyActions` | Actions safe for diagnostics and smoke checks. |
| `writeActions` | Mutating actions and the authorization/preflight each actually requires. |
| `secrets` | Secret names only, never values. |
| `webhookEvents` | Events the app consumes. |
| `evidence` | Logs, screenshots, API responses, or local test output proving behavior. |
| `denyReasons` | Known reasons the connector must fail closed. |

## Adapter Rules

- Keep provider-specific code behind an adapter boundary.
- Put local helper scripts under `.SYSTEMX/scripts` or a project-owned
  `.SYSTEMX/connectors/<connector-id>/` folder.
- Use environment variable names that describe purpose, not private business
  process.
- Validate required config before any write action.
- Make dry-run or read-only mode the default where the provider supports it.
- Honor authorization already established for the task; confirm only missing
  authority or an ambiguous target before consequential writes.
- Record webhook assumptions and replay fixtures.
- Never commit API keys, session cookies, dashboard exports with private data,
  or provider-specific proprietary workflow text.

## Browser-Only Providers

When an external service requires browser interaction:

- Prefer official API or CLI if available.
- Use the project's approved browser tools to inspect the current flow.
- Inspect console/network state when it helps establish the failure or result.
- Store only generic selectors or project-owned helper notes.
- Keep screenshots sanitized if they show customer, order, billing, or account
  information.

## Fallback Ladder

Choose the relevant steps for the observed failure and available tools; this is
not a requirement to run every step or install a specific framework:

1. Local config check.
2. CLI auth status.
3. API read-only health call.
4. Webhook signature verification.
5. Local emulator or fixture replay.
6. A bounded UI reproduction using the project's supported tools.
7. Browser/MCP inspection.
8. Operator handoff with exact blocker and next click/action.

The public template should teach the pattern. Individual projects own the actual
vendor details.
