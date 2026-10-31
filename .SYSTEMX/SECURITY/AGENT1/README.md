# Agent 1 security and access review

Agent 1 is an optional, local review reference. Its default profile is
`all-in-one`, and every finding is a warning. The 20 categories in
`questions.json` contain exactly 20 distinct evidence questions each. The ten
event buckets in `event_buckets.json` assign one primary bucket to each
observation; outcome, severity, and causality are separate fields. A question
is not answered merely because a filename was found.

The first-run setup asks for personal or enterprise context, exact GitHub
repository identity, root or project scope, owner/operator/guest role, intended
GitHub Actions secret target, local runtime secret store choice, and whether
tracked `.env` history and rotation have been reviewed. Missing answers are
reported. Setup does not install a service or grant cloud access.
The read-only `onboard plan` command pairs these questions with a selected
provider surface and credential consumer. Its selections are navigation, not
saved Agent1 answers; complete `agent-1 setup` separately in the exact scope.

```sh
bash .SYSTEMX/SYSTEMX.sh onboard plan --account-context personal \
  --surface cli --provider codex-cli --credential-consumer local-cli \
  --credential-class new
```

From the repository root, the standalone commands are:

```sh
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 status
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 setup
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 check
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 questions --category C01
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 env-inventory --env-file .env
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 env-sanitize --env-file .env
python3 -B .SYSTEMX/scripts/security_agent1.py agent-1 env-migrate --env-file .env --repo OWNER/REPO
```

`setup --apply` requires all eight first-run answers, registers `agent.1` with
the `security-access` role using the existing agent registry, and creates a
warning-only configuration record under the selected scope's ignored `local/`
directory. A matching existing role and memory are preserved; a conflicting
role stops setup. To change an existing setup record, provide all eight answers
again without `--apply` and review the `proposed` record and `existingSHA256`.
Then repeat with `--apply --replace-existing --expect-sha256 HASH`. A changed
record or missing guard stops replacement; the agent registry and memory are
preserved. This changes local intent only and does not alter GitHub secrets or
host credentials. A child project uses its `.SYSTEMXP/local/` directory. The
default `check` scans a
bounded set of filenames and safe OS signals. It identifies dependency manifest
names, adjacent JavaScript lockfile presence, `.env` filenames, and whether a
`.env` name is tracked by Git. It does not read source files, check advisories,
contact a provider, inspect processes, or claim that any of the 400 questions
passed. A truncated scan reports a warning.

`questions` shows the fixed catalog by profile or category. `review --answers`
validates a complete answer matrix with one `pass`, `fail`, `unknown`, or `na`
result per selected question. Pass, fail, and N/A require a relative evidence
reference. The command validates coverage and syntax only; it does not open
or authenticate referenced evidence and never makes a blocking decision.

`env-inventory` reads a selected, contained dotenv file into process memory to
extract key names. Values are discarded after parsing and never emitted, stored,
or copied into results. This does not control logs written by unrelated project
processes. Unsupported lines and duplicate names are reported without echoing
their contents. `env-sanitize --env-file .env` previews a names-only
`.env.example`; `--apply` creates it with blank placeholders and leaves `.env`
intact. A differing existing example requires both `--replace-existing` and
`--expect-sha256` matching the previewed existing file. Runtime store wiring
and any rotation still require separate owner action; a session terminal prompt
is the fallback until OS store integration is available.

File-backed Agent 1 commands anchor each path component to a selected project
directory handle, refuse symlinks and nonregular files, and enforce the one MiB
limit after opening. This uses POSIX `dir_fd` and `O_NOFOLLOW` support on macOS
and Linux. On Windows, dotenv inventory, sanitization, migration, answer-file
review, and setup reconfiguration fail closed in this beta because equivalent
native reparse-point-safe handle operations are not yet implemented. First-run
setup, status, questions, and warning-only filename checks remain available.
No filesystem operation can prevent a different process with write access to
the same directory from changing a file immediately after a hash check; do
guarded replacements in a workspace where other writers are quiescent.

`env-migrate` is a dry-run preview by default. An explicit
`--apply --name KEY --repo OWNER/REPO` on an
interactive terminal requires completed setup, registered `agent.1`, an
exact repository and secret target matching setup. The saved owner, operator,
or guest role describes the user; it grants no provider permission. At action
time, the command checks the active GitHub CLI account and requires the
authenticated account's repository `permissions.admin` to be exactly `true`.
An unavailable, false, or unknown result stops before secret input. This
conservative beta gate also permits a guest who actually has repository admin
access. It then asks for that one
value with hidden input, and passes it to `gh secret set --app actions` over
standard input. `--environment NAME` selects an Actions environment secret.
The default `--credential-class new` asks for a fresh value. Reusing a current
credential is marked `existing-test` and requires `--ack-test-only`; neither
selection proves that rotation happened. No upload occurs during preview.
The command does not copy the value from `.env`, alter or delete the file, or
rotate historical exposures. Review the exact account and target before entry.
After `gh secret set` succeeds, a target-scoped `gh secret list --json name`
attempts to confirm the name in the selected repository or environment scope.
The result reports `verified` or `unknown`; a failed or delayed readback is
`unknown`, and neither result reveals or verifies the value or proves workflow
use. Organization-level secret writes, including cross-repository visibility,
are outside this beta command. GitHub's
[Actions secret permissions](https://docs.github.com/en/code-security/reference/secret-security/secret-types)
and [CLI secret list](https://cli.github.com/manual/gh_secret_list) describe
the provider scopes and name-only listing.
The GitHub CLI [secret set documentation](https://cli.github.com/manual/gh_secret_set)
describes standard-input entry and local encryption. GitHub Secrets are remote
provider records, not filesystem links or a symlink replacement for `.env`.
The [GitHub secret types](https://docs.github.com/en/code-security/reference/secret-security/secret-types)
have different consumers: Actions workflows, Codespaces, and Dependabot do
not receive the same secret automatically. [Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/configure-secrets-and-variables)
uses its own Agents secret type. The `onboard plan --credential-consumer`
choice makes this boundary visible, but it does not provision any destination.
This Agent1 beta command writes **Actions** secrets only. The dotSYSTEMX
repository currently has Actions disabled; that is a repository policy, not a
default imposed on projects adopting this template. A local Codex, Grok, Muse,
or Copilot CLI and a VS Code extension need their own reviewed sign-in or
local runtime secret path. A newly issued credential is the preferred setup;
`existing-test` labels reuse without claiming rotation.

For host integration, `security_agent1.add_cli(subparsers, scope=None)` adds
`agent-1` and `security_agent1.dispatch(root, defaults, args)` returns JSON-ready
results. `security_agent1.assess(root, defaults, profile="all-in-one")` is the
read-only entry point for a session service. The service should expose only the
selected root, never accept an arbitrary client-supplied filesystem path, and
keep its own lifecycle separate from setup. The scoped project path remains
the source of truth for local observations; no service or IDE connection is
established by this module.
OS keychain, Credential Manager, and Linux Secret Service integration is not
yet implemented.
