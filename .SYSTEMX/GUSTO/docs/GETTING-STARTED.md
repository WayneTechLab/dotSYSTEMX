# Start with an account-free HR mock

## Choose the boundary

The portable folder provides contracts and sample data. A host application owns
its authentication, pages, adapter, storage and checks. In WebAppX, keep product
runtime under `src/hr/`, optional SDK runtime under `src/hr/gusto/`, and privileged
server behavior under `functions/`. Do not place React dependencies or Firebase
deployments inside an upstream release snapshot.

1. Load [ROUTES.json](../ROUTES.json), [CAPABILITIES.json](../CAPABILITIES.json)
   and the [synthetic fixture](../mock/fixtures/demo-company.json).
2. Display an explicit mock badge and fictional company. Use only reserved
   `example.invalid` addresses. Never infer a real employee/company from a login.
3. For each demo actor, filter company, self and direct-report data before
   rendering. An actor selector in the demo is not an authentication mechanism.
4. Keep demo edits in isolated temporary state. Reset restores the fixture;
   it must not write Firestore, contact Gusto, send invitations or start jobs.
5. Make external provider actions unavailable until the host meets the
   [live prerequisites](MIGRATION.md). A successful mock click proves only
   the demo journey.

In WebAppX, public demo paths can be mapped under `/hr/demo/admin/`,
`/hr/demo/employee/`, `/hr/demo/manager/` and `/hr/demo/contractor/`. Canonical live
route specifications remain `/admin/hr/`, `/employee/`, `/manager/hr/` and
`/contractor/`. A host should keep these modes and identities separate.

## Demo actor bindings

The fixture defines manager `employee-001`, employee self `employee-002`, and
contractor self `contractor-001`. These identifiers are fictional; they are not
Gusto UUIDs or real Firebase users. The employer/payroll demo may show fictional
pay totals. Managers see direct-report employment summaries and approvals,
without compensation, bank, tax or personal document fields.

## Check the host behavior

Verify route access, parameter existence, wrong-company rejection, self scope,
manager scope, compensation exclusion, mock reset, empty/error states, keyboard
navigation and narrow screen layouts. Verify native feature actions separately
from provider workflows. A mock cannot establish tax, payroll, benefits or
production correctness.

Native recruiting, policies, equipment, training, performance, cases, surveys and
automation require their own host implementation and acceptance. Synthetic
cards/specifications do not mean those business processes are live.
