# AUTOBOT tier-2 context panel

AUTOBOT is an optional panel of exactly 10 named specialist slots. AGENTA
(`agent.a`, Agent Alpha) routes explicit bounded requests and ties the results
back to Agent 0, X, Y, Z and the selected scope. These files are advisory context,
not a model runtime, scheduler, source of permissions, or automatic check loop.

Use `autobot init` to preview registration, then `autobot init --apply` to opt in.
Use `autobot list` for the catalog and `autobot context --bot autobot.design`
for selected context only. Create and complete a request explicitly; reuse a
stored response when the chosen files, policy, scope, and input revision match.
Update the input revision when outside facts change. Stale results remain history.
Never load all files or scan DATA simply because a turn began.

## Fixed panel

| Specialist | Exact file | Purpose |
| --- | --- | --- |
| `autobot.design` | [Design.MD](Design.MD) | Interface and layout decisions |
| `autobot.soul` | [Soul.MD](Soul.MD) | Purpose and values |
| `autobot.memory` | [Memory.MD](Memory.MD) | Accepted short-term context |
| `autobot.rules` | [Rules.MD](Rules.MD) | Project constraints |
| `autobot.research` | [Research.MD](Research.MD) | Source register and research questions |
| `autobot.brand` | [Brand.MD](Brand.MD) | Company and product identity |
| `autobot.media` | [Media.MD](Media.MD) | Logo and icon asset references |
| `autobot.tokens` | [Tokens.MD](Tokens.MD) | CSS and design token references |
| `autobot.data` | [Data.MD](Data.MD) | Dataset metadata and provenance |
| `autobot.archive` | [Archive.MD](Archive.MD) | Superseded context references |

AGENTA is the coordinator above the 10 specialists. [AGENTA.MD](AGENTA.MD)
sets the routing and stop contract. `CATALOG.json` describes fixed identities;
`REQUESTS.json` retains explicit request identities and immutable completions.
Private root facts must not be copied into a child `.SYSTEMXP`; initialize each
child from the blank creation templates. Reviewed additions preserve edited files.
The user and host instructions retain authority; no AUTOBOT may accept tasks,
start provider tools, delete archives, or route recursively to another AUTOBOT.

## Agenda setting defaults

The `AUTOBOT/AGENDA-SETTINGS.json` catalog defines the ten fixed
`context_selection` choices, their allowed `include` and `exclude` values, and
the safe `unset` default when no choice is recorded. Use `agenda catalog` to
read the stock definitions. This catalog is reference data; the selected
`AUTOBOT/AGENDA.json` record starts with `options: []`. Absence is `unset`,
meaning Agenda includes no reference automatically; `exclude` is a separate
explicit reviewed value. An `include` needs a reviewed
same-scope Access Matrix decision, a matching Rules file digest, a reason, a
review time, and evidence. Neither `include` nor `exclude` starts a worker or
grants access. See `docs/ACCESS-AND-MAP.md` before
recording a project-specific choice.

## Files and data

Store compact policy, metadata, and references here. Put local temporary or large
payloads in the selected `.SYSTEMX/DATA/` or `.SYSTEMXP/DATA/` after verifying its
Git exclusions. Ignore rules are not encryption or access control and do not
untrack previously committed files. Use `Data.MD` for pointers, not private bytes.
Keep credentials outside these context records. See the shared AUTOBOT manual.
