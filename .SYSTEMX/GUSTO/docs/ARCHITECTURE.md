# Portable HR architecture

## Layers and owners

| Layer | Owner | Boundary |
| --- | --- | --- |
| Portable specification | dotSYSTEMX | Route/role/capability contracts, synthetic fixtures, reviewed SDK inventory |
| Product UI and accessibility | Host application | Employer, employee, manager and contractor journeys |
| Trusted identity and company membership | Host application | Company/self/direct-report authorization before data access |
| Provider adapter and secrets | Host server | Allowed methods/paths, OAuth, versioning, error normalization and audited requests |
| Payroll/company regulated records | Gusto where supported | Authorized provider system of record; host projections contain only required fields |
| Native HR processes | Host application | Recruiting, organization, tasks, policies, assets, access, training, performance, cases, surveys, automation |
| Verified event ingestion | Host server | Signature verification, deduplication, retry, reconciliation and narrow projections |

The existing SYSTEMX connector standard uses disabled/local/staging/production
operating categories. This optional adapter's disabled/mock/demo/production
labels map mock to local and demo to staging. Neither spelling creates an
environment or credential. Default examples have no allowed actions.

## Request sequence

1. The page selects a canonical route/capability and a trusted host actor.
2. The host authorizes the company and resource scope. Deny missing mappings.
3. Mock mode reads only synthetic data and mutates isolated demo state.
4. A configured live adapter derives provider identifiers from trusted records,
   validates the specific method/path/body, and executes an approved provider request.
5. Normalize errors, retain minimal request evidence, and update only the
   necessary host projection. A pending/failed external request is not complete.

The host API must never be a generic open Gusto proxy. Role capabilities are
reference policy; endpoint authorization needs action-specific rules, resource
binding, and payload validation. Frontend routes hide unavailable actions but
do not enforce security by themselves.

## Data authority

Use provider IDs alongside independent host company/employee IDs. Preserve the
provider version/concurrency field for updates where required. Keep payroll
submission, bank/tax setup, form signatures and contractor payment state in the
authorized provider workflow. Mirror only fields needed for the host UI;
never assume a cached projection is the latest payroll state.

Time entry and approval may start as native host records, while accepted totals
are delivered to the approved payroll integration. PTO policy/balance, requests,
manager approvals and provider synchronization are separate records. Benefits
pages represent supported configured benefits/contributions and enrollment data;
they do not claim that a template buys or brokers insurance.

## Environment and execution

Maintain separate mock, demo and production adapter instances. Keep host paths,
credentials, sessions, raw webhook payloads and private run evidence outside
tracked release files. SYSTEMX role records do not authorize HR jobs, grant
provider access or schedule payroll. Product automations require explicit owners,
allowlisted actions, idempotency, approvals and execution evidence.

Use [WebAppX reference models](WEBAPPX-REFERENCE.md) when choosing Firebase, or
map the same contracts to the host's own database and server. No cloud platform
is mandatory for the portable package.
