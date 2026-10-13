# HR authorization contract

[ROLES.json](../ROLES.json) defines seven reference roles. It is a reviewed
design seed, not an IAM grant. Every live request requires a trusted host user,
active company membership and action-specific server authorization.

| Role | Default scope | Sensitive boundaries |
| --- | --- | --- |
| employer-owner | Approved company | Business owner authority does not replace provider agreements or operator confirmation for an unapproved consequential action |
| payroll-admin | Approved company payroll functions | Approved compensation/payroll; no browser tokens, raw bank/tax copies or broad HR case access |
| hr-admin | Approved company people operations | No payroll execution, employee compensation or bank/tax privileges by default |
| manager | Verified direct reports | Team summaries/time/leave/goals; exclude compensation, bank/tax and private HR documents |
| employee | Bound employee self | Own profile/onboarding/pay/statements/benefits/documents; no arbitrary employee selection |
| contractor | Bound contractor self | Own profile/onboarding/payments/documents/tasks; no employee/payroll administration |
| auditor | Read-only, approved company projection | Redacted evidence/reports only; no mutation, credentials or raw financial identifiers |

One person may have multiple separately reviewed memberships. Server policy
must check the selected company and capability; a general application `admin`
flag alone must not grant employer-owner or payroll-admin.

## Required negative cases

- An authenticated user with no HR membership cannot access live HR records.
- A valid role for company A cannot read or mutate company B.
- An employee cannot replace an employee parameter with a colleague's ID.
- A contractor cannot view another contractor's payments/documents.
- A manager cannot access indirect reports or compensation through an API,
  export, search index, document link or mixed summary response.
- A read-only auditor cannot invoke POST/PUT/DELETE or a mutating SDK block.
- An allowed route cannot forward arbitrary provider endpoints or body IDs.
- Missing, disabled or stale provider configuration cannot fall back to a more
  privileged provider mode or token.

Use short-lived download authorization for private documents and validate scope
again when issuing it. Do not let a public storage path or an unrestricted URL
undo the page's permission boundary. Native cases, reviews and survey responses
need narrower per-record policy than broad directory access.

## Writes and completion

Review consequential actions against authority already established for the
task. Require only missing authority or ambiguous targets; do not invent a
blanket confirmation ritual. Separate calculations/previews from payroll
submission, invitations from accepted membership, planned automations from actual
execution, and report requests from successful report availability.

An actor selector is allowed only in the isolated synthetic demo. It must never
create live membership, override server identity or enable external writes.
