# .SYSTEMX 1.11.0-beta.2 release report

This is the beta.2 **local source qualification** receipt, before GitHub
publication. The intended tag is `v1.11.0-beta.2` and
Python package metadata uses `1.11.0b2`. Exact source, package, and download
hashes will be recorded at the
[GitHub release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.2)
after publication. A template release is separate from project installation,
provider permission, deployment, device security, and owner acceptance.

## Template setup

The [Agenda settings catalog](../.SYSTEMX/AUTOBOT/AGENDA-SETTINGS.json) defines
ten fixed AUTOBOT `context_selection` settings, their Rules paths, and the allowed
`include` and `exclude` values. Every stock setting is `unset`; the template
selects no context. The
[access decision rules](../.SYSTEMX/GLOBAL/ACCESS-DECISION-RULES.json) define no-row, `gap`,
`denied`, and `reviewed-intent` outcomes and their review fields. Twenty role
defaults remain default-deny, while the canonical `options` and `decisions` arrays
remain empty. No catalog, role row, or decision grants OS, GitHub, IDE, or
provider access.

`agenda catalog` reads the definitions; status, table, session settings, and
workbook views expose them beside selected-scope records. `agenda init` previews
adding absent catalogs to a beta.1 scope without changing its existing options or
decisions; a partial or altered pair fails closed. The
[Agent 0 roster](../.SYSTEMX/docs/AGENT-0-ROSTER.md) shows registered roles, named
instances, task counts, and CLI setup pointers without starting or authenticating
a provider.

## First-time provider and instruction onboarding

`onboard status` and `onboard plan` read the selected Agent1 setup, Agent 0
roster summary, and a fixed catalog of CLI, IDE, and external Bot surfaces.
They do not save provider choices, authenticate accounts, start runtimes, or
return credential values. A selected credential consumer proposes a new key
class by default without creating a key. Explicit `--env-file` uses Agent1's
bounded key-name inventory; no dotenv value is returned. The catalog separates
OpenAI Codex CLI/IDE from an OpenAI dot, Grok Build CLI from Grok Bot, and Meta
Muse Code CLI from personal Muse and Meta Model API.

The expanded catalog also distinguishes `codex-sdk` as a host application SDK,
Amazon `kiro-cli` as a manual/discovery CLI, `kiro-ide` as a host IDE,
`kiro-web` as an offline Agent Beta cloud reference, and `aws-cli` as host
infrastructure tooling. Six further coding CLIs—`claude-code`,
`opencode-cli`, `blackbox-cli`, `gemini-cli`, `cursor-agent`, and `aider`—are
manual/discovery entries. Catalog presence grants no adapter, provider login,
credential destination, default provider, or live run.

Source CLI JSON readback lists exactly 20 provider/product IDs and five host
toolchain IDs. The initial `provider`, `surface`, `accountContext`,
`credentialConsumer`, and `credentialClass` selections are all null, and
`nativeHostBindingsInstalled` is false.

The checked-in project-root `AGENTS.md` is a short pointer to the canonical
`.SYSTEMX/AGENTS.md`. In adopted projects, `onboard bridge` previews that
pointer and its SHA-256; only explicit digest-guarded apply can create it
when absent. Existing root files or links are preserved. Guarded apply uses
POSIX anchored directory operations; native Windows offers preview only in
this beta. The bridge does not copy rules or grant host permissions.

Agent Y now has a source-tested Muse Code CLI adapter in addition to Codex and
Copilot. It preserves provider approval and sandbox settings and runs only a
reviewed task in an isolated worktree. A live Muse account, new-worktree trust,
and provider completion have not been verified. Grok Build remains a manual
CLI and discovery path without an Agent Y execution adapter. OpenAI dot, Grok
Bot, and personal Muse remain optional offline Agent Beta identity references,
not live integrations. The [provider onboarding guide](../.SYSTEMX/docs/CLI-TOOLS.md#first-time-provider-and-credential-plan)
links the primary provider documentation and exact commands.

The opt-in `service start --stdio` direct-I/O interface now includes bounded,
read-only `roster`, compact `settings`, and `onboard` methods with no caller
parameters. It is a custom JSON-lines protocol under the parent process, not
MCP, ACP, a native IDE plugin, or an installed OS service. Focused session
service tests passed eight cases on both Python 3.14 and 3.11. Direct
subprocess smoke tests on each interpreter sent `capabilities`, `roster`,
`settings`, `onboard`, and `stop`; all five responses were `ok`, with 20 stock
roster rows, a compact rules summary, an unset provider, and exit code zero.
These checks do not prove a real IDE or provider integration.

Source CLI `root roster` JSON readback lists exactly five toolchain options:
VS Code, Codex, Cursor, Kiro, and JetBrains. It reports 20 stock role rows and
`nativeHostBindingsInstalled: false`; the options are setup navigation, not
installed native IDE bindings.

The source review also corrected an `agenda decision-add --action` argument
parser collision that overwrote the top-level command. A regression check now
covers parsing, preview, and apply. The focused Agenda suite passed 26 of 26
tests on both Python 3.14 and 3.11. In an isolated copied scope,
`agenda status` supplied the current revision; preview and `--apply` both exited zero,
reported `applied: false` and `applied: true` respectively, and kept
`accessGranted: false`. Only the fixture received one `gap` decision row.
This functional check does not establish an external permission grant.

## Source qualification

| Boundary | Required evidence | Verified local state |
| --- | --- | --- |
| Version and manifest | VERSION, SOURCE.json, pyproject.toml, and the regenerated exact-file manifest agree; `release.py --check` passes after all edits. | Current `.SYSTEMX/config/distribution.json`: 28,332 bytes, SHA-256 `29c02255b3dbac36844d040becd8b12c58e381094dc20a0d584614b919a2bf96`. `python3.14 -I -B .SYSTEMX/scripts/release.py --check` passed: 282 distributed files and 158 Markdown documents after the service capabilities fix. |
| Local suites | Full source-matched tests on available interpreters, plus catalog migration, manager compatibility, workbook, and roster checks. Record host, command, counts, skips, and duration. | On this macOS host, Python 3.14.5: `python3.14 -I -B -m unittest discover -s .SYSTEMX/tests -q`, 406 tests, OK, 6 skipped, 490.572 s. Python 3.11.15: `python3.11 -I -B -m unittest discover -s .SYSTEMX/tests -q`, 406 tests, OK, 6 skipped, 410.044 s. Both ran against final manifest `29c02255...` after the privilege fix. |
| Access Matrix XLSX | Twenty role rows, ten unset settings, four decision rules, empty active decisions/options, no formulas, and canonical JSON row comparison. | Local `ACCESS-MATRIX.xlsx` asset is 14,195 bytes, SHA-256 `ef94cdcf73ddcdf37f3927c50b8fdcaf5745e2eb219fddf5ee4bb5de8c6fcb0d`. Five sheets pass ZIP integrity and no-formula/external-link/VBA checks; ten settings, four rules, and 20 roster rows with all 13 fields match canonical JSON row by row. All 160 original nonempty cells in the first two sheets are preserved. |
| Wheel | Build from frozen source, compare every `.SYSTEMX` payload file byte for byte, install in isolation, and read `systemx --version`. | Locally qualified staged `dotsystemx-1.11.0b2-py3-none-any.whl`: 12,992,809 bytes, SHA-256 `f33c82ade9ff08641d5a0b128846a272c71df22d2e97f31d718a1c1ec4c0d8ca`. All 282 package payload files exactly match final source/manifest. Force-reinstalled in isolated Python 3.14 and 3.11 environments; each `python -I -B -m systemx --version` returned beta.2. |
| Docs and media | Check local links, public/private paths, and exact `.SYSTEMX/MEDIA/**` byte identity against beta.1. | `validate --template` checked 158 packaged Markdown documents. A separate root/changed-guide pass checked 218 local links in 12 files with no missing target. `git diff --exit-code v1.11.0-beta.1 -- .SYSTEMX/MEDIA` passed, and scoped status found no changed/untracked media or workflow file. |

The staged `ACCESS-MATRIX.xlsx` matches the workbook digest above.
`SHA256SUMS` is 188 bytes, SHA-256
`b3b3c16bc1eb64afd51a4401c2fd90a6416f1493528567831795df088e2deebf`.
`shasum -a 256 -c SHA256SUMS` passed for both staged assets.
These local hashes and byte comparisons qualify the prepared assets; GitHub
upload and downloaded asset bytes still need independent readback. The wheel
applied `first-run` to a fresh project on each interpreter, installing 282
files. Each added a `Demo` child and ran child `onboard plan` with surface
`sdk`, provider `codex-sdk`, and consumer `server-application`. Ordinary installed
`validate` passed 274 files and 149 Markdown documents per target. The
managed direct-I/O service also answered five of five requests in each
environment, advertised seven methods, showed 20 stock roster rows and
compact settings, and left the default provider unset. These are local
source/package checks, not a live provider or IDE integration. Earlier
install/suite attempts on superseded revisions remain development feedback and
are excluded from final source qualification.

The previous
[beta.1 release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.1)
retains the edition 2.1 white paper and 8K export downloads. Beta.2 changes
template definitions and navigation; it does not create a new visual edition,
video, or private authoring archive. The checked-in XLSX is a review view; JSON
remains authoritative for selected-scope choices.

## Security and runtime boundaries

Agent1 remains opt-in and warning-only; its local checks cannot certify a host
free of malware, spyware, keyloggers, or MFA interception. GitHub Actions secrets
do not populate a local `.env` through symbolic links. GitHub Agents,
Codespaces, and Dependabot secrets also have distinct consumers; the onboarding
plan does not provision any of them. An explicit
repository/environment secret write requires action-time repository admin
permission and hidden input; metadata readback does not prove a secret value or
workflow consumer. Access Matrix intent is not identity verification or external
permission. Native Windows Agent Y execution and Agent1 file-backed operations
retain the limits in the [security guide](../.SYSTEMX/docs/SECURITY.md). No
catalog, roster, or workbook command installs an OS service or starts an agent.
The direct-I/O service capabilities now state `requiresElevation: false` and
`hostPrivileges: inherited-from-launcher`. Launch it as a normal user; those
fields do not attest that the host process lacks elevated privileges. Focused
service tests passed eight of eight on both Python 3.14 and 3.11 after the fix.

GitHub Actions is disabled for this repository, and beta.2 source must contain no
`.github/workflows` file. Manual checks qualify only the exact source and host on
which they run. A macOS PowerShell smoke result cannot prove native Windows
behavior. A template release does not deploy an application; the
[release counter](../.SYSTEMX/docs/RELEASE-COUNTERS.md) separates release records from
deployment records.

## Publication readback

Before calling beta.2 published, verify direct `main` and peeled tag SHAs, tagged
codeload ZIP size/hash and complete inventory, the immutable prerelease state,
checksum asset, and every uploaded asset name, size, and SHA-256. Download the
assets and compare exact bytes. Read back the wiki and owner Page, confirm Actions
is still disabled, and record the on-demand deployment count. Owner acceptance
remains a separate decision.
