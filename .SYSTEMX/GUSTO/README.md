# Optional Gusto HR integration package

This folder defines a reusable people-management contract for SYSTEMX hosts.
It contains page specifications, capability ownership, role rules, an exact
published SDK endpoint inventory, and synthetic fixtures. It does not install
an application, create a Gusto account, submit payroll, grant permissions, or
connect to a provider. The default connector mode is **disabled**.

The WebAppX host implements the React/Firebase application separately. Other
hosts can implement these contracts using their own stack. Agent 0 coordinates
adoption and review; HR tasks in the product are separate from SYSTEMX's
`WORK/TASKS.json` agent ledger. Core project, plan, memory and task seeds remain blank.

## Canonical files

| Source | Responsibility |
| --- | --- |
| [MANIFEST.json](MANIFEST.json) | Optional package identity, boundaries and canonical paths |
| [CAPABILITIES.json](CAPABILITIES.json) | Provider/native/shared ownership and delivery status |
| [ROUTES.json](ROUTES.json) | Employer, employee, manager and contractor page contracts |
| [ROLES.json](ROLES.json) | Seven reference roles and company/self/direct-report scopes |
| [VERSION-PIN.json](VERSION-PIN.json) | Reviewed SDK/API package versions and raw-byte fingerprints |
| [Contracts](contracts/README.md) | Host projection/configuration schemas; not provider wire schemas |
| [Demo company fixture](mock/fixtures/demo-company.json) | Synthetic, account-free product records |
| [Pinned endpoint inventory](sdk/endpoint-inventory.json) | Exact vendor inventory for allowed workflow review |

## Test without a real employer account

Use the synthetic fixtures and WebAppX's isolated mock pages. No API key or
developer account is needed for those pages. Gusto's public hosted-flow
[Try It Now](https://docs.gusto.com/embedded-payroll/docs/try-it-now) is a separate
visual demonstration; it does not supply API credentials to a local SDK app.
An actual demo API integration requires a developer organization/application and
its own credentials. There is no shared public test key documented in the
reviewed onboarding material. See [provider setup](docs/PROVIDER-SETUP.md).

## Adopt into a new app

1. Read the selected SYSTEMX release's START-HERE and STANDARD; preserve the
   outer project's records and custom extensions.
2. Read [getting started](docs/GETTING-STARTED.md), [architecture](docs/ARCHITECTURE.md)
   and [page specifications](docs/PAGE-SPECIFICATIONS.md).
3. Implement mock routes and role filtering in the host. Keep fixtures isolated
   from real users, credentials and persistent employee data.
4. Implement the [permission contract](docs/PERMISSIONS.md) and server adapter
   before any real provider request. Verify original source and company ownership.
5. Review the [SDK inventory](sdk/README.md) and [migration gates](docs/MIGRATION.md)
   before a separately authorized sandbox or production connection.

The [WebAppX reference](docs/WEBAPPX-REFERENCE.md) describes optional Firebase
models and Cloud Function boundaries. It is a design guide rather than deployed
infrastructure. See [webhook design](webhooks/README.md) for verified ingress,
duplicate delivery, retry and reconciliation requirements.

## Managed updates

This package travels in the immutable selected release. Ordinary imports add
missing outer files and preserve existing adopted files. Consult the selected
`.systemx/releases/<version>/GUSTO/` files for current defaults; do not assume an
older customized outer copy updates automatically. Changed distributions use a
fresh upstream version. SDK upgrades must refresh provenance and review actual
workflow endpoints, not overwrite a retained release or silently widen access.
