# Optional local session service

Agent1's first service transport is an explicitly started, unprivileged Python
process. An IDE or CLI harness opens its standard input and output as pipes,
owns the process lifetime, and closes input to end the session. No service is
installed into macOS, Windows, or Linux. There is no listening port, daemon,
scheduled job, credential store, shell execution, or background restart.

Use `service status` to inspect the local capability. To start it, run the
selected SYSTEMX Python runner with `service start --stdio` and connect both
standard streams as pipes. The project scope can be selected with
`projects service start --project NAME --stdio`; selection is explicit and
the process never switches scopes after launch. The launcher must not send
secrets in command arguments or protocol messages. The service accepts only
the fixed read-only Agent1 All-In-One assessment; direct Agent1 CLI commands
handle first-run setup and any reviewed writes.

Each input line is one UTF-8 JSON object with exactly `id` and `method`.
`id` is an ASCII token of at most 64 characters. Methods are `ping`,
`capabilities`, `assess`, and `stop`. Each response is one UTF-8 JSON line
with the same ID, `ok`, and either `result` or a generic `error`. For example:

```json
{"id":"health-1","method":"ping"}
```

```json
{"id":"health-1","ok":true,"result":{"alive":true}}
```

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
