# Security reporting

.SYSTEMX is experimental alpha software, provided under the [MIT License](LICENSE)
without warranty. It is not a production-readiness or security certification.

Report suspected vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/WayneTechLab/dotSYSTEMX/security/advisories/new).
That repository feature is enabled. Include the affected release/tool version,
platform, expected boundary, and minimal sanitized reproduction. Never include
credentials, customer information, or private project records in a public issue.

Reports are reviewed as maintainer capacity permits. There is no guaranteed
response time, supported-version window, or backport commitment during alpha.
Report issues in older releases too and identify the affected versions; do not
assume an older numeric version is security-supported. Corrections will identify
their affected and fixed versions when known.

The template manager downloads explicitly selected defaults and can run configured
project commands with the caller's permissions. Review publishers, sources,
commands, and target paths. Distribution fingerprints check consistency with
their manifest; they do not independently authenticate a publisher. Avoid
administrator privileges, protect project data and operation logs, coordinate
writers, and keep recoverable backups.

For an exact remote manager install or update, `--archive-sha256` can pin the
raw codeload tag ZIP to a digest obtained through a separately trusted channel.
The selected release cache also rejects files absent from the manifest before
running its Python code. Automatic startup discovery has no independent archive
pin. Inspect [installation guidance](.SYSTEMX/docs/INSTALLATION.md) before
enabling it or accepting a new release.

Direct script entry points restart in isolated Python mode, and standalone
validation loads named local helpers from source bytes. An installed console
script resolves its package before it can restart; use `python -I -B -m systemx`
from a reviewed virtual environment when `PYTHONPATH` or the working directory is
untrusted. Review the source you choose to install; an internal manifest cannot
establish publisher identity.

Optional white-paper maintenance tools restart in Python isolated mode before
imports. They accept only HTTPS or internal-anchor links in PDF content, reject
linked figure roots, and publish outputs through opened POSIX directories so a
swapped parent path cannot redirect a PDF replacement. Existing publication
editions are preserved; build to a separate draft file. These media commands
currently fail closed without POSIX directory-descriptor support, including on
native Windows. See [publishing guidance](docs/media/README.md).

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

Project-specific security guidance remains in
[.SYSTEMX/docs/SECURITY.md](.SYSTEMX/docs/SECURITY.md). Adopting projects must define
their own security contacts, deployment boundaries, and incident process.
