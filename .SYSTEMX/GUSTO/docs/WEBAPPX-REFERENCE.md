# Optional WebAppX / Firebase reference design

This is a proposed host mapping for the portable contracts. It does not deploy
Firebase resources, claim tested Cloud Functions, or require Firebase in
dotSYSTEMX. Product runtime remains in the WebAppX repository's chosen layout.

## Host files

```text
src/hr/
  model.ts                 canonical catalog + synthetic fixture mapping
  HrPage.tsx               page rendering and explicitly isolated mock state
  gusto/                   approved SDK mount + mock/live adapter boundary
functions/
  src/hr/                  future trusted provider and native HR services
firestore.rules            separately reviewed live HR membership rules
storage.rules              separately reviewed private document access
.SYSTEMX/GUSTO/             portable specification and source provenance
```

The host decides the actual filenames and deployment code. A portable contract
is not an implementation of these functions or rules.

## Reference collections

| Path | Minimum content and authority |
| --- | --- |
| `organizations/{orgId}` | Host organization identity and reviewed company linkage |
| `organizations/{orgId}/hrMembers/{uid}` | Active membership, roles, bound employee/contractor ID, reviewed manager relationships |
| `organizations/{orgId}/employees/{employeeId}` | Minimal directory projection: provider reference, display name, department, job, status, manager link |
| `organizations/{orgId}/contractors/{contractorId}` | Minimal contractor directory projection and provider reference |
| `organizations/{orgId}/hrPrivate/{recordId}` | Separately authorized sensitive projections; never a public directory field |
| `organizations/{orgId}/payrollRuns/{runId}` | Provider reference, period, state and permitted summary; provider remains execution authority |
| `organizations/{orgId}/timeEntries/{entryId}` | Employee, interval/hours, submission/approval state, reviewed export reference |
| `organizations/{orgId}/timeOffRequests/{requestId}` | Employee, requested interval/type, decision, synchronization state |
| `organizations/{orgId}/benefitEnrollments/{enrollmentId}` | Permitted plan/enrollment projection and authoritative provider reference |
| `organizations/{orgId}/hrDocuments/{documentId}` | Metadata and scoped storage/provider reference; no permanent public download URL |
| `organizations/{orgId}/hrTasks/{taskId}` | Product checklist assignment/due/state; independent of SYSTEMX agent tasks |
| `organizations/{orgId}/hrPolicies/{policyId}` | Policy edition, effective date and separate acknowledgment records |
| `organizations/{orgId}/hrAssets/{assetId}` | Item, assignment, custody and return events |
| `organizations/{orgId}/hrTraining/{assignmentId}` | Course, assigned subject and evidence |
| `organizations/{orgId}/hrPerformance/{recordId}` | Scoped goals/reviews with explicit audience |
| `organizations/{orgId}/hrCases/{caseId}` | Restricted owner/audience/classification/retention metadata |
| `organizations/{orgId}/hrSurveys/{surveyId}` | Campaign metadata and separately protected responses |
| `organizations/{orgId}/hrAutomations/{automationId}` | Disabled proposed rule, allowed action, owner and execution receipts |
| `providerEvents/{dedupeId}` | Server-only verified receipt, company mapping, digest, processing state and retry count |

Add recruiting candidates/offers in separate restricted collections. Keep
provider tokens in Secret Manager or an approved encrypted server store,
outside client-readable Firestore. Do not mirror full bank, tax, medical or
identity payloads merely because the SDK can request them.

## Proposed server services

| Service boundary | Required behavior |
| --- | --- |
| `beginGustoConnection` | Trusted owner/payroll membership, approved program/environment, one-use OAuth state and redirect validation |
| `finishGustoConnection` | Bind the callback to original user/company/state; exchange and store credentials on server only |
| `gustoWorkflowRequest` | Explicit method/path allowlist, role/self/direct-report checks, derived company/provider IDs, payload/version validation, sanitized errors |
| `receiveGustoWebhook` | Current documented verification, original request bytes where needed, bounded payload, known subscription/company, durable dedupe and processing queue |
| `reconcileGustoProjection` | Approved read-only fetch, narrow projection updates, retry/backoff and retained processing evidence |
| `submitTimeEntry` / `reviewTimeEntry` | Employee self and manager direct-report checks, valid interval, state/concurrency rules |
| `requestTimeOff` / `reviewTimeOff` | Self/request and manager approval boundaries; provider synchronization is a separate result |
| `requestHrReport` | Permitted report type/filters, async state and re-authorized download access |
| `runHrAutomation` | Explicit enabled rule/owner/allowlisted action, duplicate prevention and execution receipts |

These names are reference responsibilities, not callable endpoints shipped by
the portable package. Use argument arrays for local tooling and keep host
credentials/runtime paths outside tracked snapshots.

## Rules and acceptance

Firestore/Storage rules must deny unknown users/companies and exclude private
data from broad lists. Server code using Admin SDK bypasses rules and must
repeat authorization. A frontend role menu or Firebase custom claim alone does
not establish the per-company/self boundary. Test positive and negative cases
in a disposable emulator environment before any production deployment.

Keep local mock, local emulator, real Gusto demo API and deployed production
evidence separate. Hosting a mock screen does not prove Cloud Functions,
webhook verification, provider onboarding or payroll acceptance.
