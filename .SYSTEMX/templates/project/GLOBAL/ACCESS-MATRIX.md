# Project access matrix

Template state: unconfigured. The selected scope's JSON Access Matrix may list
standard role names with no template grants. It contains no reviewed permission,
actor/resource decision, or approval until its owner supplies verified facts.
The workbook is a readable view of JSON, not an authority for access.

Use `agenda decision-add` to preview a specific selected-scope decision, then
apply it with the observed access revision. `agenda workbook-check` detects a
stale generated view and `agenda workbook-export --apply --expected-revision`
writes a current XLSX only under ignored `local/`. The distributed workbook is
a static seed. Excel edits do not update JSON or external IAM.
For an older scope without the fixed default-role catalog, preview
`agenda roles-upgrade` and apply it with the observed access revision; existing
decisions are preserved.

- Selected project name and record path:
- Applicability, decision owner, and applicable shared policy reference:
- Authoritative external IAM/ACL or permission source:
- Data classification, trust boundary, and last review:

| Actor or role | Resource | Action | Environment / tenant | Decision or gap | Decision owner | Approval or policy reference | Verification evidence | Reviewed / recheck |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

A row documents a reviewed decision; it does not grant access or authenticate
an actor. Record permission work and its status in this project's
[WORK/TASKS.json](../WORK/TASKS.json). Do not import a sibling project's grants,
secrets, or identity assumptions. Bind a named BOT/DOT or native subagent
instance to its selected-scope record and review it separately; a role pattern
never grants access to its future instances. Use the outer defaults'
`docs/ACCESS-AND-MAP.md` for the format guidance.
