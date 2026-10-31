# Agent 0 direct I/O for CLIs and IDE hosts

The portable `.SYSTEMX` exposes selected-scope records through direct CLI
commands and an optional, explicitly started JSON-lines process. A host owns
the process and its input/output pipes. The transport is read-only: it does
not install a service, start an agent, select a model, grant access, or
configure an IDE. [Agent 0's roster](AGENT-0-ROSTER.md), the
[Agenda and Access Matrix](ACCESS-AND-MAP.md), and the selected project's
canonical task records remain the sources for their respective facts.
The optional root `AGENTS.md` pointer helps compatible tools discover shared
instructions; it is separate from these structured data commands.

## Choose the scope and route

| Route | Current use | Authority |
| --- | --- | --- |
| `systemx run --target PATH --offline -- root roster` | One read of Agent 0's selected root roster | Managed CLI verifies the pinned template, then reads the selected root records. |
| `systemx run --target PATH --offline -- root packet --task TASK-ID` | Bounded selected-task context packet | Reads canonical task records; no model call or task acceptance. |
| `systemx run --target PATH --offline -- root delta` | Compare retained task mappings and external observations | Reads stored observations; it does not contact a harness or Bot. |
| `systemx run --target PATH --offline -- session-settings --compact` | Short settings/rule-revision packet | Returns compact status; load individual Rules text only for the task that needs it. |
| `systemx run --target PATH --offline -- service status` | Inspect the available stdio protocol | Reports capability and limits; it does not leave a process running. |
| `systemx run --target PATH --offline -- service start --stdio` | Host-owned, bounded read-only session | The caller connects both standard streams as pipes and closes input or sends `stop` to end it. |
| `systemx projects --target PATH -- service start --project NAME --stdio` | The same transport for one registered `.SYSTEMXP` | The explicit child selection is fixed for that process; no request can switch scope. |

`PATH` is the directory containing the outer `.SYSTEMX`. From a reviewed
folder-only copy, `bash .SYSTEMX/SYSTEMX.sh service start --stdio` supplies the
same local protocol. PowerShell uses `pwsh -File .SYSTEMX/SYSTEMX.ps1 service
start --stdio`. The local launcher and managed runner must be selected from
the intended project; a different directory or installed package may use a
different release. `--offline` suppresses only the manager's optional startup
release check. It does not confine other explicitly run commands or providers.

## Fixed JSON-lines contract

Send one UTF-8 JSON object per line with **exactly** `id` and `method`.
`id` is a 1–64 character ASCII token beginning with an alphanumeric character;
the rest may contain alphanumeric characters, dot, underscore, or hyphen.
Each response is one line with `ok` and either `result` or a generic `error`.
A valid request keeps its `id`; an invalid request may receive `id:null`. The
input line limit is 16 KiB, the response limit is 512 KiB, and one session
handles at most 64 requests. `stop` and EOF close it.
An oversized or unterminated input ends it after a bounded error. Standard
output is reserved for protocol lines.

| Method | Read-only result |
| --- | --- |
| `ping` | Process liveness. |
| `capabilities` | Method names, transport, limits, and selected scope. |
| `assess` | Agent1's warning-only All-In-One local assessment. |
| `roster` | Agent 0's bounded role and instance view, decision pointers, and source revision. |
| `settings` | Compact selected-scope settings and one aggregate Rules revision. |
| `onboard` | Unselected provider catalog and Agent1 setup status; no `.env` is opened. |
| `stop` | Acknowledges and ends the session. |

The protocol has no path, provider, account, secret, command, or write
arguments. For a shell pipeline in a managed installation, the following
sends four independent requests and then closes the process:

```bash
printf '%s\n' \
  '{"id":"roster-1","method":"roster"}' \
  '{"id":"settings-1","method":"settings"}' \
  '{"id":"setup-1","method":"onboard"}' \
  '{"id":"stop-1","method":"stop"}' \
  | systemx run --target "/path/to/project" --offline -- service start --stdio
```

Responses can contain the selected local scope path, project names, task
metadata, and revision hashes; review them before sending them to an external
model. `settings` contains status and hashes, not full Rules text or permission
grants. For a roster larger than the response bound, use
`root roster --offset N --limit N` through the direct
CLI. The [service protocol](../Setup/SERVICE.md) specifies the exact lifetime
and error behavior.

## Make a reviewed change through the direct CLI

The stdio session cannot mutate the Access Matrix. To record one selected-scope
review outcome, read `agenda status` and copy its current `accessRevision`.
Then preview an `agenda decision-add` command with the real actor, resource,
owner, evidence, and review time. For a gap record, a shell example is:

```bash
ACCESS_REVISION="<accessRevision from agenda status>"
REVIEWED_AT="<UTC timestamp, for example 2026-10-31T12:00:00Z>"
DECISION_ARGS=(
  --id ACC-001 --actor agent.0 --resource example-service --action read
  --environment test --decision gap --owner project-owner
  --evidence review-record --reviewed-at "$REVIEWED_AT"
  --expected-revision "$ACCESS_REVISION"
)
systemx run --target "/path/to/project" --offline -- agenda decision-add "${DECISION_ARGS[@]}"
systemx run --target "/path/to/project" --offline -- agenda decision-add "${DECISION_ARGS[@]}" --apply
```

Run the final line only after reviewing the preview and confirming that the
source revision is still current. A change in the matrix between preview and
apply is rejected. The decision records review state; even `reviewed-intent`
does not authenticate an actor or grant OS, repository,
IDE, or cloud access. See the [Access Matrix guide](ACCESS-AND-MAP.md) for
the fields and `--policy-ref` required for reviewed intent.

## Host integration map

| Host | Available route in this template | Native integration boundary |
| --- | --- | --- |
| [VS Code](https://code.visualstudio.com/docs/agents/reference/mcp-configuration) | Its terminal or a user-controlled extension process can launch the CLI and pipe JSON-lines. | VS Code's AI tools use their own MCP configuration; this process is not an MCP server or installed extension. |
| [Codex CLI](https://learn.chatgpt.com/docs/extend/mcp) and [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) | A human CLI session or an application using the SDK can invoke the reviewed `systemx` subprocess and parse its JSON-lines output. | Codex MCP and SDK/app-server interfaces are separate protocols. This template has no native Codex tool registration. |
| [Cursor](https://cursor.com/docs/cli/acp) | A host-controlled terminal or subprocess can use the direct CLI contract. | Cursor [MCP](https://cursor.com/help/customization/mcp) or ACP integration needs a real adapter and host configuration; none is supplied here. |
| [Kiro](https://kiro.dev/docs/cli/acp/) | A host-controlled terminal or subprocess can use the direct CLI contract. | Kiro [MCP](https://kiro.dev/docs/mcp/configuration/) or ACP integration needs its own adapter and trust review; none is supplied here. |
| [JetBrains AI Assistant](https://www.jetbrains.com/help/ai-assistant/acp.html) | A host-controlled terminal or subprocess can use the direct CLI contract. | JetBrains supports ACP agents and [MCP tools](https://www.jetbrains.com/help/ai-assistant/mcp.html), but this JSON-lines service implements neither. |

These are documented host targets, not a popularity ranking or a claim that
their native chat panels are connected. A later MCP/ACP adapter would need
protocol negotiation, schemas, scope selection, resource limits, process
ownership, permission mapping, and host-specific tests. Host credentials and
provider login remain under the chosen host or application.
