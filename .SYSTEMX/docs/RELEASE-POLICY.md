# Alpha release policy

**.SYSTEMX is alpha. Use at your own risk. It may change daily.** Guidance,
interfaces, defaults, and compatibility may change during development. The MIT
license provides the terms and warranty disclaimer. Passing template tests does
not certify a downstream project for production. Keep recoverable backups and
test your workflows before adopting or updating.

## Branches and exact versions

`main` is the default public template branch. `Alpha1` is the integration branch
for this alpha series. Both contain the consolidated history of the earlier
template branches at the first alpha publication. Branches are moving references;
use an exact release tag for repeatable installation. Earlier branches and tags
remain available as history.

The first explicitly labeled alpha is **1.6.0-alpha.1**, tagged
[`v1.6.0-alpha.1`](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.6.0-alpha.1).
It follows the existing 1.5.0 history without reusing or rewriting old versions.
The Python package spells that same version **1.6.0a1**. Subsequent alpha snapshots
increment the alpha number, or start a new base version when appropriate.
Published tags and assets are not intentionally replaced; corrections get a new
version. Daily development does not mean an automatic release every day.

Prior numeric versions and GitHub release labels are retained for compatibility.
Those historical labels are not a production-readiness certification. The current
development series is explicitly published as GitHub prereleases. There is no
stable-release date, support SLA, or promise of compatibility throughout alpha.
Changes should document migrations and preserve project-owned data.

## Pins and update channels

- New projects are pinned to their chosen version and use manual updates.
- An exact alpha tag or reviewed alpha source explicitly selects alpha defaults.
- Unpinned final-version projects discover only final releases. An alpha tag
  incorrectly labeled final on GitHub is refused by stable discovery.
- Unpinned alpha projects discover published alpha and final releases, ordered
  numerically: `alpha.2 < alpha.10 < final` for the same base version. A final
  selected version returns the project to final-only discovery.
- Startup selection still requires `--auto on-start`, stays within the current
  major version, and checks at most daily after a successful check. Alpha releases
  can still change interfaces within that major version. Keep manual updates when
  a review is needed before every change.
- Discovery never silently downgrades a project. Explicit `--version` or a local
  `--source` can select an older version after unpinning and compatibility review.

The channel is derived from `activeVersion`; no new setting is inserted into user
records or the compatible schema-1 installation state. Alpha discovery inspects
up to 1,000 GitHub releases and fails with exact-version guidance if that bound is
exhausted. Drafts, unsupported version forms, and inconsistently labeled releases
are excluded. Failed startup checks retain verified installed defaults.

## Upgrade an existing project to alpha

Managers from 1.5.0 and earlier cannot parse alpha IDs. Upgrade the external
tool environment first, from outside the project's `.SYSTEMX` folder. Use the
interpreter belonging to that environment; the example assumes it is activated:

```bash
python -m pip --log dotsystemx-alpha-install.log install --upgrade "git+https://github.com/WayneTechLab/dotSYSTEMX.git@v1.8.2-alpha.1"
systemx --version
systemx status --target "/path/to/project"
systemx policy --target "/path/to/project" --pin none --auto manual
systemx update --target "/path/to/project" --version 1.8.2-alpha.1 --dry-run
systemx update --target "/path/to/project" --version 1.8.2-alpha.1
systemx policy --target "/path/to/project" --pin current
systemx run --target "/path/to/project" --offline -- validate
systemx run --target "/path/to/project" --offline -- context --agent agent.0
```

Review the preview before applying. A reviewed checkout's new `manager.py` offers
the same commands without a package install. Old root launchers and `VERSION`
are preserved, so use the new external `systemx` command to select and run cached
defaults. Do not reinstall the old tool to operate a project still selecting an
alpha version. Roll back its selected defaults with the new manager first, and
check record/schema compatibility before invoking older tools.

Updates add snapshots and missing files. They never remove or replace existing
project files or directories; only manager-owned selection/history metadata is
updated. Existing project records remain schema 1. A future record migration must
be explicit and preserve source records and evidence. For removal, use the logged
[uninstall and restore workflow](UNINSTALL.md).

## Public distribution and support

GitHub hosts the source, template, wiki, versioned folder archive, and Python wheel.
The library is not currently published to PyPI. No hosted application, background
service, telemetry collector, or MCP server is deployed by this release. Network
use is for requested release retrieval and opted-in startup discovery; configured
project commands can have their own effects and must be reviewed separately.

The release includes SHA-256 checksums and validation evidence. Hashes detect
inconsistent files; they are not an independent signature or security audit.
Windows, macOS, and Linux are covered by CI on Python 3.9 and 3.13. Python 3.9 is
the compatibility floor; prefer a currently maintained interpreter. Drive requires
locally available regular files and coordinated writers. Chat requires an export
or authorized writable tools; saving a chat alone does not persist project files.

Use [support](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/SUPPORT.md),
[contributing](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/CONTRIBUTING.md),
and [private security reporting](https://github.com/WayneTechLab/dotSYSTEMX/security/advisories/new).
Review logs before sharing; paths, project names, and exported context may be private.

Version references: [Semantic Versioning](https://semver.org/),
[Python version specifiers](https://packaging.python.org/en/latest/specifications/version-specifiers/),
and [GitHub release API](https://docs.github.com/en/rest/releases/releases).
