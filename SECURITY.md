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

Project-specific security guidance remains in
[.SYSTEMX/docs/SECURITY.md](.SYSTEMX/docs/SECURITY.md). Adopting projects must define
their own security contacts, deployment boundaries, and incident process.
