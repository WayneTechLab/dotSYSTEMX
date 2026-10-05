# Contributing to .SYSTEMX

.SYSTEMX is alpha and may change daily. Read the
[release policy](.SYSTEMX/docs/RELEASE-POLICY.md) and open an
[issue](https://github.com/WayneTechLab/dotSYSTEMX/issues) to discuss changes that
affect the format, version management, or compatibility. Contributions are reviewed
as capacity permits; no response or release schedule is guaranteed.

Keep `.SYSTEMX` self-contained, generic, and stack-neutral. Use that exact folder
case. Keep the reusable task ledger, project context, master plan, memory, focus,
and configuration blank. Use temporary projects for testing. Do not contribute
private project records, secrets, absolute workstation paths, provider accounts,
or unrelated application code.

Base work on current `main`, use a focused branch, and submit a pull request to
`main`. `Alpha1` identifies the consolidated alpha series. Explain the user-visible
problem, preservation/compatibility effects, and validation evidence. Do not reset
someone else's branch or rewrite released tags.

From the repository root, after changing distribution files:

```bash
python3 -I -B .SYSTEMX/scripts/release.py
python3 -I -B .SYSTEMX/scripts/systemx.py validate --template
python3 -B -m unittest discover -s .SYSTEMX/tests -v
```

Use `py -3` in place of `python3` on Windows. Add new distributed files to the
explicit inventory in `.SYSTEMX/scripts/systemx.py`; regenerate the manifest only
after reviewing the changes. Never refresh blank-record fingerprints to disguise
populated project records. Include meaningful regression tests for behavior or
data-preservation changes. Run checks locally and include the results with the
pull request; this repository does not run GitHub Actions.

For a release, assign a fresh version, align `VERSION`, provenance, distribution
manifest, and Python metadata, update the offline changelog and wiki, validate the
actual archive and wheel, then publish a GitHub prerelease. Keep detailed release
history in the wiki; keep the README focused on adoption and current maturity.
Published artifacts should contain only the reviewed distribution inventory.

Contributions are made under the repository's [MIT License](LICENSE). Retain
existing attribution. Report sensitive vulnerabilities through
[private security reporting](SECURITY.md), not a public issue.
