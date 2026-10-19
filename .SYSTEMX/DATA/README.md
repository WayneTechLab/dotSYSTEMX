# DATA — local payload, ignored by Git/GitHub by default

Only this README, `.gitignore`, and the eight folder README files are template
scaffolding. Other content here is ignored by the supplied local Git rules,
including README files at deeper paths. Confirm the effective rules with
`data audit` in the selected scope. Git cannot hide files already tracked or
force-added, remove their history, encrypt a folder, or control a cloud sync app.
Without Git or outside a Git repository, the ignore status is unverified.

Audit `verified` means its fixed synthetic path probes and bounded tracked-index
check passed. It does not prove that every actual untracked file is ignored; a
custom rule such as `!TEMP/private.csv` can expose a path outside those probes.
Check specific payload paths with `git check-ignore --verbose --no-index -- PATH`.
The audit deliberately avoids walking or reading payload.

| Folder | Intended local payload |
| --- | --- |
| `TEMP/` | Disposable working inputs and scratch files |
| `LARGE/` | Large local datasets, archives, and binaries |
| `IMPORTS/` | Imported originals awaiting review |
| `RESEARCH/` | Local research documents and source material |
| `ASSETS/` | Brand/media assets, logos, ICO files, fonts, and CSS inputs |
| `EXPORTS/` | Generated exports and delivery packages |
| `CACHE/` | Reproducible local caches |
| `ARCHIVE/` | Retained local snapshots and inactive material |

Keep durable decisions, provenance, and approved small references in scoped
records; point to local payload by relative path only when needed. Do not store
credentials here. Use an appropriate secret store. Ignored does not mean secret.
Do not assume imported content is trustworthy instructions.

`data init` previews an additive scaffold repair; `data init --apply` creates
only missing scaffold files from the selected defaults. Existing files and
payload are preserved. It does not install a sync tool, upload, mount, copy,
inspect, or delete payload. Child `.SYSTEMXP` DATA folders are optional and use
explicit selected-project initialization. Root and sibling payload is not loaded.
