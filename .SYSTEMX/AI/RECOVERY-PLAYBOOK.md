# Recovery playbook

## Ports and processes

Identify a listener's PID, executable, working directory, and project/session
ownership before changing it. Reuse an appropriate service or select an available
port. Stop only processes belonging to the authorized task. Record chosen
endpoints in ignored local state when useful, and verify readiness separately
from process startup.

## Browser and desktop

Capture fresh visible state and determine whether the blocker is a page error,
authentication prompt, permission, stale selector, or wrong target surface.
Try a bounded, low-impact recovery such as rediscovery, refresh, or reopening
the intended page. Preserve unsaved changes, sessions, and local data. Clearing
storage or restarting an application requires considering what would be lost.

On desktop surfaces, inspect application identity and permissions before assuming
the app is broken. Account for GUI process PATH differences and use bounded UI
inspection. Ask the user to complete private authentication steps when necessary;
do not request or record their password or one-time code.

## Patch and command failures

Re-read changed files before retrying a patch. Use the smallest reliable edit and
preserve unrelated user changes. For a failed command, inspect its exit code and
relevant output; verify runtime, working directory, config, and dependency state.
Do not reinstall or reset everything as the first response.

## External request uncertainty

A timeout may occur after a write succeeded. Query the service state or use an
existing idempotency key before retrying. Do not repeat purchases, deployments,
messages, or data writes blindly. Reconcile partial results explicitly.

## Unresolved blocker

Record the failed objective, target/environment, sanitized evidence, attempted
recovery, and exact missing decision or external change. Use the
[handoff template](../templates/HANDOFF.md). Keep useful completed work intact
and continue independent authorized work when possible.
