# Quality and evidence

## Two separate checks

`bash .SYSTEMX/SYSTEMX.sh validate` checks the operations folder: required files,
readable JSON, config structure, local Markdown file links, and record
consistency. It does not check external URLs, Markdown anchors, JSON
Schema semantics, credentials, dependencies, or application behavior.
It also validates task/agent records, dependencies, transition history, milestone
references, completion evidence fields, and generated work-view consistency.
Recorded evidence and reviewer names are not independently authenticated.
Current-focus references and the generated `CURRENT.md` are also checked.

`validate --template` adds the [public distribution checks](../FORMAT.md#public-distribution-versus-adopted-project):
only the standard file inventory, reviewed blank seed hashes, empty tasks/focus
and commands, and Agent 0 only. Unlike ordinary validation, it checks normally
ignored folders for extra files. This is a publication check, not a secret scanner.

`bash .SYSTEMX/SYSTEMX.sh check` first validates the folder, then runs the
project's configured check commands. An empty check list is a configuration
error. Commands run in order and stop at the first failure. Passing means those
commands passed, not that every possible quality concern was assessed.

## Choose checks by risk

| Change | Useful evidence |
| --- | --- |
| Documentation or configuration | Parse/format checks, valid links, and accurate executable examples. |
| Logic or defect fix | Focused regression test proving the affected behavior and relevant boundaries. |
| API or data change | Contract, migration, compatibility, rejection, and partial-failure checks. |
| User interface | Target-surface verification of the affected journey, accessibility, and layouts. |
| Authorization or sensitive data | Positive and negative permission cases, isolation, and leakage checks. |
| Release or infrastructure | Target/account verification, reproducible build, smoke check, and rollback evidence. |

Use the project's formatter, linter, type checker, tests, and dependency checks
as appropriate. Avoid tests that only repeat the implementation or add little
confidence. Broaden verification when the change, a failure, or an unresolved
concern justifies it.

## Evidence contract

Use the [evidence and acceptance guide](EVIDENCE.md) for independent source,
artifact, deployed/installed, functional, operational, and publication claims.
Only adopt the boundaries the project's acceptance criteria require.

Record the command or action, relevant revision, environment, date, result, and
artifact location. Distinguish automated verification from manual observation.
Record skips and their reasons. Do not hide a failing check behind optional
flags or describe an unavailable integration as passing.

Use concise, sanitized output. Keep private runtime evidence in ignored local
folders and commit only the durable summary needed by reviewers. Link the
result from a [task](../templates/TASK.md), [release](../templates/RELEASE.md), or
[handoff](../templates/HANDOFF.md) record.

## Maintaining the template

When changing the command runner, run:

```bash
bash .SYSTEMX/SYSTEMX.sh validate
bash .SYSTEMX/SYSTEMX.sh validate --template
python3 -B -m unittest discover -s .SYSTEMX/tests -v
```

These tests use temporary copies and fake project commands. They do not install
tools, invoke configured user deployments, or contact cloud services. Keep
validation behavior and the command documentation aligned when changing either.

After intentionally changing distribution files, regenerate the inventory with
`python3 -I -B .SYSTEMX/scripts/release.py`, review its diff, and rerun the relevant
checks. Never regenerate blank-seed hashes for populated project records. Build
the Python package from a pristine reviewed distribution and validate an installed
wheel plus its exported folder; a successful package build alone does not verify
that all hidden template files were included. Test installer updates in temporary
projects, including pins, custom files, upstream removals, and unavailable networks.
