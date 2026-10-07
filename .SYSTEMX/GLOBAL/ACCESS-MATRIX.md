# Access matrix

Template state: unconfigured. No actor, resource, permission, or approval has
been recorded for an adopted project.

Use this project-owned matrix only when access decisions matter. Record the
reviewed intent and evidence for a specific actor, resource, action, and
environment. A row is not a grant, identity proof, executable policy, or
substitute for the external system's actual access controls. The current user
instructions and applicable organization policy still govern action.

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
