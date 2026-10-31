# Agent Beta local BOT/DOT panel

Agent Beta (`agent.b`, reserved role `bot-coordinator`) keeps an index of local
BOT/DOT workspaces in the explicitly selected `.SYSTEMX` or `.SYSTEMXP` scope.
The public seed has no bots and does not register Agent Beta.
New scopes copy blank records from `templates/agentb/`; active root bot records
are never used as child creation seeds.

`agent-beta setup` previews the blank records and registration. Add `--apply`
to install them in the selected scope. `agent-beta bot-add BOT_NAME` previews an
offline workspace at `AGENTB/.SYSTEMXB-BOT_NAME`; add `--apply` to create it.
Names use 1–32 uppercase ASCII letters, digits, or underscores and begin with a
letter. Use `--kind dot` for a DOT assistant; the default kind is `bot`.

The default source is `local`. To document an existing online source without
connecting to it, use `--source online-reference --provider SERVICE
--provider-identity ALIAS`. These values identify a service and non-secret
account or bot alias; never enter a token, key, password, or private URL. An
optional `--access-decision-id ACC-001` must point to a row in the selected
scope's Access Matrix for `agentb:BOT_NAME` with `reviewed-intent`. The record
always retains `online: false`, meaning this CLI has not established a
connection or verified the provider account.

For the normal selected-scope sequence, create the BOT/DOT without an access
decision, record a reviewed-intent row for `agentb:BOT_NAME` through
`agenda decision-add`, then run `agent-beta access-link BOT_NAME
--access-decision-id ACC-001`. The preview returns `revisionBefore`, which
fingerprints both the BOT record and Access Matrix. Re-run with
`--expected-revision REVISION --apply` to retain the link. A changed BOT or
matrix refuses the apply; preview again. A linked row is reviewed intent, not
an access grant or provider identity verification. A new reviewed row can
replace the reference through the same preview and revision guard.

`agent-beta assign BOT_NAME --task TASK-001` previews an advisory reference to
an existing canonical task. Add `--apply` to retain it. `status` and `validate`
read local metadata. No command launches an assistant, contacts a provider,
grants permissions, changes task state, or accepts work. The user and Agent 0
retain those decisions.

Each workspace contains `BOT.json`, `MEMORY.md`, `README.md`, and `Rules.MD`.
The rules file starts blank and requires separate provider review before it is
used as an Agenda source. Keep memory
brief and free of secrets, credentials, client data, or private payloads.
Workspace folders are ignored by Git so local context is not accidentally
included in a reusable template. Review any intentional export separately.
