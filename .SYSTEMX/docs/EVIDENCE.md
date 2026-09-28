# Evidence and acceptance

Task state answers whether a specific assignment has been accepted. It does not
describe every property of the product. A source repair can be done while the
release, installation, or real user workflow remains open.

## Name the claim before checking it

Record the required evidence in each task's acceptance criteria before work
starts. Use the [evidence record](../templates/EVIDENCE.md) to capture:

- The exact claim and task ID.
- Original observation time, source revision, and relevant local changes.
- Environment, target, and build/artifact identity when applicable.
- The command or observed action, result, and retained artifact location.
- What the evidence does and does not establish, including skipped checks.
- Reviewer and any reason the observation must be refreshed.

A copied report or new wrapper timestamp does not refresh its observations.
Keep failed checks and uncertainty visible. Do not combine overlapping test runs
or different task/route inventories into an inflated completion count.

## Independent acceptance boundaries

| Boundary | What evidence can establish | What remains separate |
| --- | --- | --- |
| Source verified | Changed implementation passes relevant checks at an identified revision | Integration and running behavior |
| Integrated | The intended changes are combined and checked in the target checkout/branch | Remote publication, release artifact, and deployment |
| Artifact verified | The identified build/package passes applicable checks | Installation or serving that exact artifact |
| Deployed or installed | The intended destination contains the identified artifact | Real functional behavior and persistent operation |
| Functional | Required user actions and data paths work in the observed environment | Restart, recovery, sustained operation, and release authority |
| Operational | Applicable persistence, recovery, monitoring, and ownership requirements hold | Permission to perform unrelated external actions |
| Published | The accepted version is available to its intended audience | All other claims not directly verified |

These are evidence categories, not a mandatory seven-stage process. A document
or local library may not need deployment or persistent-runtime acceptance.
Record why a boundary does not apply instead of inventing work to fill it.
Authentication, privacy, legal, financial, and owner decisions remain separate
where the actual project requires them; this guide creates no new approval gates.

## Keep source credit without claiming product completion

For work that genuinely needs separate source and runtime acceptance, use two
existing or newly scoped task records: one for the verified source change and
one for the applicable runtime acceptance, linked by `dependsOn`. Attach each to
the existing master-plan milestone. Do not reopen accepted source work merely
because its dependent deployment is still pending. Reopen when new evidence
invalidates the original acceptance; retain its transition history.

The CLI requires evidence and a coordinator/owner reviewer to accept `done`.
It validates record consistency, not the truth of an artifact, the caller's
identity, or the sufficiency of proof. Agent 0 must inspect the original evidence
and the actual production caller or user path relevant to the acceptance claim.
Mocks establish only the behavior they exercise; a screenshot or successful
build alone does not establish an entire workflow.

## Resume without repeating unchanged work

1. Read [CURRENT.md](../CURRENT.md), the selected tasks, and the linked checkpoint.
2. Recheck only volatile facts needed for the next decision: revision, working
   tree, relevant artifact, target, and any retained live process/job handle.
3. Preserve previously accepted evidence at its original scope. Follow the
   earliest unmet dependency or concrete failure in the existing plan.
4. Run checks that cover the causal change and affected joins. Repeat after a
   relevant change, failure, or unresolved concern; explain broader validation.
5. Update canonical task state and select the next focus. Archive dated detail
   in session checkpoints; keep the entry point short.

A timeout is not a cancelled job. Follow an owned handle to a terminal result
before starting a replacement that could conflict. Record failed attempts and
the changed condition that justifies a retry. Shared compilers, installers,
databases, browser sessions, and deployment targets need explicit ownership.
