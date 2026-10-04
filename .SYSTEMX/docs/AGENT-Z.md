# Agent Z: repeatable evidence review

Agent Z is the standard **review** role (`agent.z`). It is a structured peer
review of a prompt, task, change, or project. Agent 0 coordinates work; Agent X
tracks time and events; Agent Z reports evidence, gaps, and changes. Agent 0 or
the user retains acceptance authority. A high score is not production readiness,
a deployment permission, or a reason to mark a task complete automatically.

## One fixed 10-by-10 policy

The default [policy](../config/agent-z-policy.json) contains exactly 10 categories,
10 questions per category, and 100 stable question IDs. The same ordered questions
are presented on every call using that policy version. No model generates new
questions during a review.

| Category | Scope |
| --- | --- |
| C01 | Intent and acceptance |
| C02 | Scope and authority |
| C03 | Context and provenance |
| C04 | Planning and dependencies |
| C05 | Correctness and completeness |
| C06 | Verification and evidence |
| C07 | Security and data handling |
| C08 | Usability and documentation |
| C09 | Delivery and operational state |
| C10 | Time, continuity, and delta |

A human or authorized LLM assesses each question against the selected subject and
original evidence. The CLI validates record consistency and calculates the score;
it does not call an LLM, run tests, inspect references, or decide the answers.
Repeatable questions and arithmetic do not make model judgments deterministic.
Retain evidence and reviewer reasoning so disagreements can be examined.

## First review

Activate the two standard roles once with `roles-init --apply` after reviewing
its preview. For a child project use `projects roles-init --project NAME --apply`.
See [Agent X setup and compatibility](AGENT-X.md#activate-once-in-the-selected-scope).
Then select the subject and the exact code/input and evidence versions:

```bash
bash .SYSTEMX/SYSTEMX.sh agent-z policy
bash .SYSTEMX/SYSTEMX.sh agent-z prepare \
  --kind task --subject TASK-001 --task TASK-001 \
  --revision OBSERVED_REVISION --evidence-revision EVIDENCE_SNAPSHOT \
  --stage checked
```

Omit `--task` for a prompt or untracked subject. `--kind` accepts `prompt`, `task`,
`change`, or `project`; `--stage` accepts `planned`, `implemented`, `checked`,
`deployed`, or `live_verified`. These identify the claimed review scope, not a
proof that a stage occurred. Evidence should identify an artifact hash, run ID,
or equivalent stable snapshot. Volatile live observations need a new evidence
revision and time even if source code did not change.

The command previews 100 `unknown` answers and a request ID. Add `--apply` to save
it at the returned `REVIEWS/requests/R-....json` path. The questions/policy are
frozen with the request; edit only its answers. Do not change its subject,
revision, identity, or policy snapshot in place. Repeating identical preparation
returns the existing request and preserves completed answers.

Each answer has `id`, `result`, `note`, and `evidence`:

```json
{
  "id": "Z01.01",
  "result": "pass",
  "note": "The accepted brief states a measurable outcome.",
  "evidence": ["Original brief revision and section reference"]
}
```

Allowed results are `pass`, `partial`, `fail`, `unknown`, and `not_applicable`.
Pass/partial require a note and original evidence references. Fail requires a
concrete note. N/A needs a rationale and a reference supporting non-applicability.
Unknowns stay visible; do not substitute confidence or a favorable guess for
missing proof. Every review must retain all 100 answers in the fixed order.

## Score without starting another work loop

```bash
bash .SYSTEMX/SYSTEMX.sh agent-z score R_RETURNED_ID
bash .SYSTEMX/SYSTEMX.sh agent-z score R_RETURNED_ID --apply
```

These are placeholders: use the complete generated `R-...` identifier. Preview
is read-only. Applying saves an immutable-by-command JSON scorecard at the returned
`REVIEWS/reports/Z-....json` path. Repeated identical inputs reuse that report
without updating its timestamp or generating another report.

Each pass earns **1 point**, partial **0.5**, and fail/unknown/N/A **0**. The main
score is **earned points out of 100**, with ten category scores out of 10. N/A
never receives free points. The scorecard separately shows applicable maximum,
applicable percentage, evidence coverage, and the count of each result. An
all-N/A review has zero raw points and undefined applicable percentage/coverage;
it cannot appear as a perfect review. Do not compare raw scores across subjects
with different applicability without examining that difference.

Scores remain advisory. There is no universal passing threshold, no automatic
acceptance, no implicit deployment, and no task reopening. The review writes
neither task state nor schedules and executes no checks. Required acceptance,
authority, and unresolved critical findings override any aggregate score.

## Compare the delta

```bash
bash .SYSTEMX/SYSTEMX.sh agent-z compare Z_PREVIOUS_ID Z_CURRENT_ID
```

Use two complete returned report IDs. Comparison requires the same subject and
policy fingerprint. It reports total/category point changes, question-level
result changes, changed evidence/notes, and before/after source/evidence versions.
A policy change requires a new baseline; the tool refuses a misleading numeric
comparison. Historical reports keep their exact question set and answers.

Use one review at a meaningful completion boundary (`needs_review`), or when
explicitly requested for a prompt or intermediate result. Reuse the saved report
when the code/input, evidence, and policy have not changed. After a relevant
change, prepare a new revision, reassess the same 100 questions, and cite still
valid evidence rather than rerunning unrelated checks. Correcting a judgment can
create a new report from edited answers; retain the original report and explain
the changed reasoning. A score difference alone is not a new work order.

Agent 0 reviews the findings against original acceptance criteria, identifies the
remaining delta, and chooses the next bounded action or accepts completion.
Stop when the accepted objective is met or a concrete blocker requires input.

## Customize without changing history

Activation creates project-owned `REVIEWS/POLICY.json` from the selected default.
Edit question text, category names, and policy references there to fit the project
or company. Keep the 10-by-10 shape and stable question IDs; increment the policy
`version` whenever wording or meaning changes. A previously used policy ID/version
cannot be reused with different contents. Add organization-specific requirements
through these questions and cited supporting policies; keep extra independent
checklists separate if they would change the 100-question core.

`REVIEWS/policies/` retains frozen policy versions. Requests and reports carry
policy fingerprints and snapshots. Updates never overwrite the project policy,
answers, reports, or role memory. They do not silently adopt new default questions.
Fingerprints detect inconsistent records, not malicious edits by a user with
filesystem access; this is not a signed attestation system.

Use `agent-z validate R_ID` or `agent-z validate Z_ID` to inspect one record's
integrity. Ordinary context loading does not add the 100 questions or past reviews
to every prompt. Read the relevant report only when needed. Review files are
bounded at 32 MiB and contain no automatically fetched external data.

## Multi-project and chat use

Use `projects agent-z COMMAND --project Project-A` to keep policy, requests,
reports, and memory in that project's `.SYSTEMXP`. Do not mix equal task IDs from
different projects. Example: `projects agent-z policy --project Project-A`.

For an initial prompt, use `--kind prompt --stage planned`, identify the saved
prompt/version, and record unproven claims as unknown or justified N/A. In a chat
without filesystem tools, the same fixed questions can be used as a document;
save the complete scorecard yourself and reattach it when continuing. Never claim
that an unsaved chat review is persistent project memory.

[Agent X](AGENT-X.md) supplies timestamped event references.
[Evidence and acceptance](EVIDENCE.md) defines verification scope.
[SYSTEMX PROJECTS](PROJECTS.md) defines project selection and preservation.
