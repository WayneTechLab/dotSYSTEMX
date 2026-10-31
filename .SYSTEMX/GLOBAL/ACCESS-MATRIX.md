# Access matrix

Template state: unconfigured. The companion `ACCESS-MATRIX.json` lists fixed
agent, AUTOBOT, native-subagent, and BOT/DOT role defaults with no template
grants. Its `decisions` array is empty. No actor/resource permission or approval
has been recorded for an adopted project. The workbook is a readable view of
that JSON record and does not update it.

For a selected scope, `agenda status` supplies the access revision. Use
`agenda decision-add` first as a preview, then with `--apply` and that revision
to record one reviewed intent, denial, or gap. `agenda table --format json`
reads the current rows. `agenda table --format csv` returns JSON containing
three CSV strings (`roleCsv`, `accessCsv`, and `agendaCsv`).

The checked-in workbook is the reusable seed view. `agenda workbook-check`
compares a generated workbook in ignored `local/` with current selected-scope
JSON. `agenda workbook-export` previews its source revision and target; use
`--apply --expected-revision REVISION` to write the current formula-free XLSX
view under `local/`. Editing Excel cells does not change the JSON decisions.
An older selected scope without the fixed role catalog can run
`agenda roles-upgrade` as a preview, then apply it with its observed access
revision; this preserves existing decisions.

Use this project-owned matrix only when access decisions matter. Record the
reviewed intent and evidence for a specific actor, resource, action, and
environment. A row is not a grant, identity proof, executable policy, or
substitute for the external system's actual access controls. The current user
instructions and applicable organization policy still govern action.

For each real instance, use its selected-scope registry or BOT/DOT record,
verify the harness or provider identity, then record a specific decision with
an owner, evidence, and recheck trigger. Pattern rows in the standard catalog
never assign access to new instances automatically.

- Applicability, scope, and decision owner:
- Authoritative policy, IAM/ACL configuration, or service reference:
- Data classification and trust boundaries to consider:
- Last reviewed, recheck trigger, and unresolved decisions:

| Actor or role | Resource | Action | Environment / tenant | Decision or gap | Decision owner | Approval or policy reference | Verification evidence | Reviewed / recheck |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Record denials and negative tests where relevant. Put work to obtain or verify
access in [WORK/TASKS.json](../WORK/TASKS.json), with its current state there;
do not turn this matrix into another task list. For multiple projects, keep
child-specific decisions in that project's `.SYSTEMXP/GLOBAL/ACCESS-MATRIX.md`
and reference only approved shared policy here. See the
[access and map guide](../docs/ACCESS-AND-MAP.md).
