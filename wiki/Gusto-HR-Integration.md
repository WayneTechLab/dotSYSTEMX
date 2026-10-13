# Gusto HR integration and account-free testing

SYSTEMX **1.9.0-alpha.6** includes an optional portable `.SYSTEMX/GUSTO/`
package: 64 page contracts, 33 capabilities, seven reference roles, synthetic
fixtures and the pinned Gusto React SDK endpoint inventory. It provides shared
specifications; the host app owns authentication, UI, storage and execution.
The package does not activate a Gusto account, deploy services or submit payroll.

## Start with the portable package

Read the [package overview](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/README.md)
and [getting-started guide](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/GETTING-STARTED.md).
Its subfolders are:

| Folder | Purpose |
| --- | --- |
| `docs/` | Architecture, provider setup, page specifications, permissions and migration |
| `contracts/` | Route, capability, connector, employee projection and webhook schemas |
| `mock/fixtures/` | Fictional company, employee, contractor and HR workflow examples |
| `sdk/` | Exact endpoint inventory, version provenance and Apache license |
| `webhooks/` | Event receipt/replay and reconciliation contracts |
| `examples/` | Disabled connector configuration with no granted actions |

From a reviewed source checkout, run these checks without credentials:

```bash
python3 -I -B -m unittest discover -s .SYSTEMX/tests -p test_gusto_contracts.py -v
bash .SYSTEMX/SYSTEMX.sh validate --template
```

The template check requires blank reusable coordination seeds. An adopted app
with populated context/tasks uses its normal record validation and app checks.
Synthetic HR fixtures are reference data, never actual employee records or
canonical agent task/memory history.

## Run the WebAppX mock workspace

Use the full WebAppX template for its React/Firebase host adapters:

```bash
gh repo create my-hr-app --template WayneTechLab/WebAppX --private --clone
cd my-hr-app
npm ci
npm run hr:test
npm run dev
```

Open Vite's printed URL at `/hr/demo`. It provides fictional management,
employee, manager and contractor portals.

WebAppX 3.4.0 supports these native account-free journeys:

| Journey | Host preview sequence |
| --- | --- |
| Onboarding | Review the fictional profile/job, complete the checklist, review the summary and confirm simulated completion. |
| Benefits | In the employee self preview, elect sample enrollment/waiver, review and confirm it; management remains read-only. |
| Time tracking | Submit a timesheet, obtain its scoped manager approval and link approved hours to mock payroll. |
| Payroll | Prepare approved hours, calculate fictional totals, review and simulate submission with a mock receipt. |

Use the same fictional employee and confirm elections before preparing payroll.
The fixed sample period is 2026-10-01 through 2026-10-15. Only active employees'
approved, unpaid entries in that period qualify, and a simulated receipt consumes
those entries once.

Employee search/profile edits, time-off requests/approvals, policy/training
acknowledgements and contractor previews remain available. All native workflow state
lives in browser memory and resets on refresh or Reset. These flows do not
create an account, call a provider, persist HR data to the cloud, enroll insurance
or execute payroll. The portable alpha.6 specification and its fingerprints
are unchanged by this host workflow update.

At `/hr/demo/sdk`, SDK **0.56.6** renders genuine components against isolated
development-only synthetic sessions:

| Selected component | Local mock path |
| --- | --- |
| `EmployeeManagement.EmployeeList` | Active, Onboarding and Dismissed directory queries. |
| `EmployeeOnboarding.OnboardingExecutionFlow` | Admin profile, compensation, federal/state tax, Check payment, deductions and Summary screens. |
| `Payroll.PayrollExecutionFlow` | Configuration/prepare, calculate/poll, review and synthetic submission/poll. |

SDK onboarding Summary/Done is navigation rather than completion. The host
requires explicit simulated employee-form and new-hire review before local
status update/readback. I-9, legal signatures, tax filing and eligibility
verification are outside this selected mock path.
The [host setup guide](https://github.com/WayneTechLab/WebAppX/blob/main/docs/GUSTO-SETUP.md)
walks the verified fictional Jordan/Texas/Check case, using prefilled masked
identity data and no real SSN, bank credentials or Gusto account. It also covers
the SDK payroll sample: edit **Regular Hours** `80` → `8`, save, **Calculate
and review**, inspect its separate fictional `$200` zero-tax totals, then
**Submit** through the genuine **Payroll submitted** summary and host
**Simulated payroll processed** banner. Downloads, check/paystub and cancellation
actions are outside that selected mock journey.

Supported writes mutate only local fictional fixtures. Credentials, foreign
companies and unsupported operations remain refused. Benefits/time have native
interfaces because this SDK version has no corresponding UI flows. Native state
and SDK sessions remain separate; the host does not export native approved hours
to Gusto or the SDK fixture. SDK Reset/refresh clears its sample session, and
native Reset clears its own fixture. These paths do not establish full SDK,
all onboarding scenarios, real payroll/tax accuracy or provider acceptance.
The mock middleware is absent from Hosting and production preview. See
[WebAppX setup](https://github.com/WayneTechLab/WebAppX/blob/main/docs/GUSTO-SETUP.md)
and [its HR wiki guide](https://github.com/WayneTechLab/WebAppX/wiki/Gusto-HR-and-Employee-Management).

## Test credentials and real sandbox access

Gusto does not document a shared/public integration key. Its Embedded Demo
requires a Developer Portal account, organization and application, which creates
application-specific credentials. A developer sandbox is separate from a live
payroll company. See [Gusto's setup](https://docs.gusto.com/embedded-payroll/docs/getting-started).

The public [Flows showcase](https://docs.gusto.com/embedded-payroll/docs/try-it-now)
can be viewed without API keys. It is a hosted UX demonstration, not reusable API
credentials. The local fixture tests and WebAppX mock are the account-free
development path.

The SDK does not implement OAuth acquisition/refresh. A host backend owns
authentication, trusted employer/employee mappings, credentials and curated
method/resource permissions. Review
[SDK authentication](https://sdk.gusto.com/docs/getting-started/authentication/)
and [proxy security](https://sdk.gusto.com/docs/getting-started/proxy-security-partner-guidance/).

## Provider and native ownership

Gusto remains authoritative for payroll, tax/bank and provider document workflows.
The host owns tenant memberships, source mappings, minimal projections and native
recruiting, organization, policies, assets, access, training and performance.
Page specifications distinguish SDK-backed features, API/custom work and native
HR modules. An endpoint appearing in the vendor inventory is not a permission.

Read [capability ownership](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/CAPABILITY-OWNERSHIP.md),
[all page specifications](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/PAGE-SPECIFICATIONS.md),
and [permissions](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/PERMISSIONS.md).
WebAppX adds an optional disabled Firebase foundation with organization data
contracts, restricted rules, callable helpers and webhook tests. Real provider
forwarding, token rotation, reconciliation and financial execution require
separately implemented and accepted adapters.

## Migration

The native timesheet-to-mock-payroll link is synthetic. A future App Integrations
time export must follow Gusto's [shift-level time-tracking contract](https://docs.gusto.com/app-integrations/docs/syncing-time-tracking-data),
including UTC timestamps, a named time zone and classified hours.

Move through contracts → synthetic fixtures/UI → authenticated native HR →
application-specific Gusto Demo → provider workflow/permission checks → approved
production release. Preserve existing project records and immutable snapshots
when importing a new SYSTEMX release. Read
[migration gates](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/MIGRATION.md)
and [WebAppX's Firebase guide](https://github.com/WayneTechLab/WebAppX/blob/main/docs/GUSTO-FIREBASE.md).
