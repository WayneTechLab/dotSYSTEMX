# Access matrix and project map

The blank [root access matrix](../GLOBAL/ACCESS-MATRIX.md) and
[root map](../PLAN/MAP.md) are reusable project records. A selected
`.SYSTEMXP` child receives its own blank `GLOBAL/ACCESS-MATRIX.md` and
`PLAN/MAP.md`. Populate only the selected scope after adoption; never copy
another project's identities, topology, task history, or private evidence.

## Access decisions

Use the matrix when the project has protected data, privileged actions, shared
resources, or distinct environments. For each reviewed access path, identify
the actor or role, resource, action, allow/deny/defer decision, environment or tenant,
decision owner, applicable policy or approval, verification evidence, and review
or expiry condition. State `unknown`, `not applicable`, or `deferred` with a
reason and owner instead of inventing a permission.

The matrix records intent and review history. Actual authorization is enforced
by the relevant operating system, repository, cloud provider, application, or
service. An Agent 0/X/Z registry entry is not an authenticated identity or a
grant. Confirm the live account, target, and permission at the external boundary
before a consequential action. Keep credentials and secret values out of records.
When an access gap requires work, create or update a task in the selected
`WORK/TASKS.json`; do not add status columns or competing checkboxes here.

## Source and system boundaries

Use the map when a navigation view helps the team locate code, data, interfaces,
and owners. Cite the actual architecture, repository path and revision,
configuration, inventory, or observed endpoint for each entry. Distinguish a
planned connection from an implemented one and an observed live path from a
source-only description. A URL in `SOURCES.json` or a map is a reference; it
does not mount Drive, fetch a repository, open a chat, or prove access.

The map is supporting navigation. `GLOBAL/CONTEXT.md` owns accepted project
identity and source hierarchy; `PLAN/MASTER-PLAN.md` owns outcomes and
milestones; `WORK/TASKS.json` owns task state, dependencies, and acceptance
evidence; `WORK/FOCUS.json` owns the selected objective; and original source
files or external systems remain authoritative for their actual implementation
and permissions. Link these records rather than copying their changing content.

## Scope and upkeep

Root records cover the outer project or shared workspace. Child records cover
only the explicitly selected `.SYSTEMXP`. Use qualified references for
cross-project links, and reconcile shared policy with child-specific decisions.
Neither file is part of the default bounded agent context packet; open the
relevant section when the task needs it to avoid loading an entire inventory
on every turn.

Review entries after a material change to identity, resource, environment,
architecture, or ownership. Preserve prior evidence and record the observation
date and revision. These Markdown records are not executable policy, an access
scanner, a topology crawler, or production-readiness proof. The CLI validates
their location and local links as distribution files, not the truth of their
claims. See [security](SECURITY.md), [evidence](EVIDENCE.md), and
[SYSTEMX PROJECTS](PROJECTS.md).
