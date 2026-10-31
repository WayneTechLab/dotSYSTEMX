# Optional local session service

The shared Agent 0, Agent1, settings, and onboarding transport is an explicitly
started Python
process. An IDE or CLI harness opens its standard input and output as pipes,
owns the process lifetime, and closes input to end the session. No service is
installed into macOS, Windows, or Linux. There is no listening port, daemon,
scheduled job, credential store, shell execution, or background restart.
It does not request elevation, but inherits the launching user's effective OS
permissions. Run it as a normal user. Capability output says
`requiresElevation:false` and `hostPrivileges:inherited-from-launcher`; it
does not assert that the caller is unprivileged.
This fixed JSON-lines protocol is not MCP or ACP. A host-specific MCP, ACP, or
extension adapter needs its own implementation and compatibility check.

Use `service status` to inspect the local capability. To start it, run the
selected SYSTEMX Python runner with `service start --stdio` and connect both
standard streams as pipes. The project scope can be selected with
`projects service start --project NAME --stdio`; selection is explicit and
the process never switches scopes after launch. The launcher must not send
secrets in command arguments or protocol messages. Direct `.SYSTEMX` CLI
commands handle first-run setup, task changes, and any reviewed writes.

Each input line is one UTF-8 JSON object with exactly `id` and `method`.
`id` is an ASCII token of at most 64 characters. Methods are `ping`,
`capabilities`, `assess`, `roster`, `settings`, `onboard`, and `stop`.
`assess` returns Agent1's warning-only All-In-One assessment; `roster` returns
Agent 0's selected-scope role and instance view; `settings` returns compact
settings and an aggregate Rules revision; `onboard` returns the unset provider catalog and
Agent1 setup status. These methods accept no caller-supplied path, command,
account, credential, or provider selector. Each response is one UTF-8 JSON line
with `ok` and either `result` or a generic `error`. A valid request's response
keeps its ID; a malformed request may receive `id:null`. For example:

```json
{"id":"health-1","method":"ping"}
```

```json
{"id":"health-1","ok":true,"result":{"alive":true}}
```

For current local context, a coordinator can send separate `roster`,
`settings`, and `onboard` requests. A roster may contain project-local names
and task metadata; review it before forwarding to an external model. Settings
contains state and hashes, not Rules file text or an access grant. For a large
roster that exceeds the response bound, use the direct CLI's paginated
`root roster --offset N --limit N` command.

The maximum request line is 16 KiB, the maximum response is 512 KiB, and a
session handles at most 64 requests. An oversized or unterminated request
ends the session after a generic error. EOF or `stop` also ends it. The
assessment accepts no caller-supplied path, command, or credential and returns
Agent1's sanitized local findings. Standard output is reserved for protocol
lines; clients should treat anything else as a transport failure.

This Python transport is designed to run on Python 3.9+ on macOS, Windows, and
Linux. The portable protocol is tested here; a separate host integration and
native OS installation must be designed and verified on each target platform
before claiming that an OS service is installed or protected by host controls.
