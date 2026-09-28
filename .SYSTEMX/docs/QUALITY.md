# Quality and evidence

## Two separate checks

`bash .SYSTEMX/SYSTEMX.sh validate` checks the operations folder: required files,
readable JSON, config structure, local Markdown file links, and references to
removed components. It does not check external URLs, Markdown anchors, JSON
Schema semantics, credentials, dependencies, or application behavior.
It also validates task/agent records, dependencies, transition history, milestone
references, completion evidence fields, and generated work-view consistency.
Recorded evidence and reviewer names are not independently authenticated.

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
python3 -B -m unittest discover -s .SYSTEMX/tests -v
```

These tests use temporary copies and fake project commands. They do not install
tools, invoke configured user deployments, or contact cloud services. Keep
validation behavior and the command documentation aligned when changing either.
