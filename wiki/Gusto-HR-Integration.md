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
npm run dev
npm run hr:test
```

Open Vite's printed URL at `/hr/demo`. It provides fictional management,
employee, manager and contractor portals. Mock actions include employee search,
profile edits, onboarding checklists, time entries, time-off requests/approvals,
policy/training acknowledgements and payroll/payment previews. Browser state
resets on refresh. Real payroll execution is unavailable.

At `/hr/demo/sdk`, the genuine SDK **0.56.6** renders the employee directory
using development-only local wire-format fixtures. Active, Onboarding and
Dismissed reads are covered. Credentials, writes, foreign companies and unknown
operations are refused. This is a limited SDK contract test, not full SDK coverage.
The mock middleware is not a deployed API. See
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

Move through contracts → synthetic fixtures/UI → authenticated native HR →
application-specific Gusto Demo → provider workflow/permission checks → approved
production release. Preserve existing project records and immutable snapshots
when importing a new SYSTEMX release. Read
[migration gates](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/.SYSTEMX/GUSTO/docs/MIGRATION.md)
and [WebAppX's Firebase guide](https://github.com/WayneTechLab/WebAppX/blob/main/docs/GUSTO-FIREBASE.md).
