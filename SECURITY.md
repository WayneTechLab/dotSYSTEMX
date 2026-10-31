# Security reporting

.SYSTEMX is prerelease beta software, provided under the [MIT License](LICENSE)
without warranty. It is not a production-readiness or security certification.

As of 11 October 2026, this public repository has GitHub secret scanning,
push protection, and Dependabot vulnerability alerts enabled. GitHub Actions
remains disabled; these repository checks do not run or certify the template's
local tests. A repository ruleset blocks deletion and force pushes to `main`
and `Alpha1`. Review the current repository settings rather than relying on
this dated statement for a later release.

Report suspected vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/WayneTechLab/dotSYSTEMX/security/advisories/new).
That repository feature is enabled. Include the affected release/tool version,
platform, expected boundary, and minimal sanitized reproduction. Never include
credentials, customer information, or private project records in a public issue.

Reports are reviewed as maintainer capacity permits. There is no guaranteed
response time, supported-version window, or backport commitment during prerelease development.
Report issues in older releases too and identify the affected versions; do not
assume an older numeric version is security-supported. Corrections will identify
their affected and fixed versions when known.

The template manager downloads explicitly selected defaults and can run configured
project commands with the caller's permissions. Review publishers, sources,
commands, and target paths. Distribution fingerprints check consistency with
their manifest; they do not independently authenticate a publisher. Avoid
administrator privileges, protect project data and operation logs, coordinate
writers, and keep recoverable backups.

For releases beginning with 1.9.0-alpha.3, the distribution manifest hashes
binary and unknown files byte for byte. Older immutable releases retain their
published format. `systemx run` requires a managed installation and refuses a
plain folder target, but a target's own installation state is not independent
proof of origin. Do not execute launchers or scripts from an untrusted checkout.

For an exact remote manager install or update, `--archive-sha256` can pin the
raw codeload tag ZIP to a digest obtained through a separately trusted channel.
The selected release cache also rejects files absent from the manifest before
running its Python code. Automatic startup discovery has no independent archive
pin. Inspect [installation guidance](.SYSTEMX/docs/INSTALLATION.md) before
enabling it or accepting a new release.

Agent Y's allowed-path checks and PR transitions are workflow controls, not an
OS sandbox. An external CLI can use credentials and files available to its host
account; the controller cannot undo out-of-repository writes or network calls.
For untrusted provider execution, use a separate OS account or container without
the controller's GitHub credentials or write access to project `.SYSTEMX`
records. See [Agent Y's security boundary](.SYSTEMX/docs/AGENT-Y.md).

Direct script entry points restart in isolated Python mode, and standalone
validation loads named local helpers from source bytes. An installed console
script resolves its package before it can restart; use `python -I -B -m systemx`
from a reviewed virtual environment when `PYTHONPATH` or the working directory is
untrusted. Review the source you choose to install; an internal manifest cannot
establish publisher identity.

The optional white-paper builder is an authoring script, outside the template
runtime. It imports ReportLab and pypdf at startup and writes the current PDF
and provenance at fixed paths. It does not restart in isolated mode, anchor
output replacement through directory descriptors, or preserve prior editions
on its own. Run it only from a reviewed source and Python environment in a
separate draft copy; review the manuscript links, generated files, and diff
before publishing. Keep earlier editions in immutable Git releases. See
[publishing guidance](docs/media/README.md).

Fresh adoption refuses conflicting executable defaults. A managed project's
older root bootstrap must be explicitly refreshed from a reviewed new external
tool before a changed-release update; that limited operation backs up and
replaces only eight recognized stock bootstrap and launcher files, with the
refreshed launchers using Python isolated mode (`-I`). It does not replace
customized wrappers or approve customized local code.
This manager refuses to install or newly select releases older than
1.8.7-alpha.1. It can inspect and run an already selected, verified older
snapshot through an isolated compatibility shim during a reviewed external
migration. The old code retains its historical behavior and security limits;
reselection below the floor requires a separately reviewed backup or legacy path.

Agent Alpha and its ten [AUTOBOT functions](.SYSTEMX/docs/AUTOBOT.md) provide
selected advisory context and local request records. They do not authenticate
callers, override current instructions, execute models, or accept tasks. Review
reference Markdown and request summaries for private information before sharing.
The scoped [DATA folder](.SYSTEMX/docs/DATA.md) ignores payloads in Git by default
except exact scaffold files. Ignore rules do not remove committed history,
prevent force-add, enforce OS access, or control backups, cloud sync, and other
uploads. Use `data audit` to inspect the adopted checkout; no payload contents
are recursively read and no data is automatically uploaded or deleted.

Project-specific security guidance remains in
[.SYSTEMX/docs/SECURITY.md](.SYSTEMX/docs/SECURITY.md). Adopting projects must define
their own security contacts, deployment boundaries, and incident process.
