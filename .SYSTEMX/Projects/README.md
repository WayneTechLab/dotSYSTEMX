# SYSTEMX PROJECTS

Keep one outer .SYSTEMX for shared tools and coordination. Each selected project
or channel owns Projects/NAME/.SYSTEMXP for its information, plans, tasks,
decisions, evidence references, status, and agent memory.

[REGISTRY.json](REGISTRY.json) is the explicit routing authority. The template
ships with no registered projects. Create Project-A, Project-B, or your own names
only in an adopted workspace. Read the [multi-project guide](../docs/PROJECTS.md).

Code and working files belong beside the project's .SYSTEMXP, or in an external
location explicitly referenced by its SOURCES.json. Never put a second .SYSTEMX
inside the outer .SYSTEMX. A source reference does not clone, synchronize, grant
access to, or publish the referenced system.

The root can list identities without loading project memories. Every project
command needs an exact selection; there is no remembered active-project pointer.
Tasks and Agent 0 IDs are local to each record scope.
