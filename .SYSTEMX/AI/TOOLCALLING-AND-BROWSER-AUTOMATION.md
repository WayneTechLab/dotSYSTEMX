# Tool calling and browser automation

## Select the tool

Use the smallest available tool that can perform and verify the requested action:

1. Inspect local files, source, configuration, and logs for repository questions.
2. Use established project scripts for builds and checks.
3. Prefer a supported connector, API, SDK, or CLI for structured service work.
4. Use browser tools for actual user journeys, visible state, and web-only flows.
5. Use desktop automation when the requested native surface needs it.

Respect the user's named application and the tool's permission boundaries. Do
not claim an app or browser was opened based only on a successful launch command;
verify its state. Tool availability does not require installing or invoking it.

## Browser and UI evidence

Use the project's chosen automation framework where available; Playwright and
Chrome DevTools MCP are optional examples. Use fresh DOM, accessibility, or
screenshot evidence before interacting. Scope selectors to the intended page,
account, dialog, or application. Refresh evidence after navigation or mutations.

Check the relevant user journey, errors, requests, and visible result. Prefer
local or staging fixtures for repeatable checks. Capture sanitized traces or
screenshots for failures and record the tested URL/environment. Never bypass
authentication, MFA, permissions, or transaction confirmation requirements.

## External actions

Confirm the target account, environment, and authorized effect before writing.
Reuse authorization already established in the task; ask only when it is missing
or ambiguous. Read back the result after creation or modification. Use idempotency
and status checks before retrying a request whose outcome is uncertain.

## Failures

Classify the blocker as authentication, permission, modal, process, port,
network, rate limit, apply failure, or unknown. Inspect the cause before retrying.
Use the [recovery playbook](RECOVERY-PLAYBOOK.md), then report the exact unresolved
condition and next required action. Avoid unattended loops and repeated unchanged
polling.
