# Agent 0 roster

The installable [Agent 0 roster guide](../.SYSTEMX/docs/AGENT-0-ROSTER.md)
explains the read-only `root roster` view, role activation paths, and the
difference between the `.SYSTEMX` lifecycle CLI and separately installed
Agent Y providers. Start from the containing project directory:

```bash
bash .SYSTEMX/SYSTEMX.sh root roster
bash .SYSTEMX/SYSTEMX.sh agent-y providers
bash .SYSTEMX/SYSTEMX.sh onboard plan --surface cli --provider codex-cli \
  --credential-consumer local-cli --credential-class new
```

A roster row is a navigation aid. It does not activate an agent, authenticate
a provider, execute a task, or grant access. Agent 0 or the user retains
acceptance of the canonical task in `WORK/TASKS.json`.
`onboard plan` adds a read-only provider and credential-consumer menu. It
separates installed terminal CLIs from IDE and cloud Bot surfaces, but does not
authenticate them or change the Agent 0 roster. Grok Build remains a manual
CLI/discovery path until a reviewed Agent Y adapter exists. See the
[provider guide](../.SYSTEMX/docs/CLI-TOOLS.md#first-time-provider-and-credential-plan).
