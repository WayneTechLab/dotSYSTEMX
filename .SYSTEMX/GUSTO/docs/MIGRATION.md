# Phased migration from specification to live HR

| Phase | Deliverable | Required evidence |
| --- | --- | --- |
| 0: Portable contract | Reviewed capabilities/routes/roles, pinned SDK inventory, authored setup guide and synthetic fixtures | Template and contract validation; blank seeds preserved |
| 1: Host mock | Isolated employer/employee/manager/contractor pages and native sample workflows | Route/role/self/direct-report tests, browser journey, reset and no-network/no-persistence proof |
| 2: Local SDK workflow | Selected SDK component mounted with implemented synthetic wire requests | Actual workflow render, handled request inventory, error/empty states and peer/build checks; unsupported workflows denied |
| 3: Trusted host services | Real authentication/membership, narrow adapter, private models, webhook processing and rules | Emulator or equivalent positive/negative access, payload validation, replay/idempotency/retry tests |
| 4: Authorized provider demo | Developer app and approved test company in Gusto's demo environment | Read/write workflow results from the actual demo API, credential isolation, concurrency and failure recovery |
| 5: Approved production | Reviewed commercial/onboarding/security state and operator-authorized live target | Exact deployment identity, live company/access verification, approved bounded acceptance and recovery |

Phases are a delivery guide rather than new SYSTEMX ledger fields. Adopted
projects record their own accepted tasks/evidence; this reusable package leaves
its core task and memory seeds blank.

## Preserve existing WebAppX

Add the package through the reviewed public-upstream import. Keep React/Vite/
Firebase, existing setup/session/LAN behavior, kits, research and checksums.
New host HR pages and services are independent changes. Avoid rewriting starter
or production configuration until it is an explicit reviewed host requirement.

Use new upstream release IDs for changed distributions. Retain old immutable
snapshots and fingerprints. Existing customized outer package files remain
preserved; reconcile them deliberately with the selected new reference files.

## Native feature maturity

Directory/sample pages for recruiting, organization, HR tasks, policies, assets,
access, training, performance, cases, surveys and automation are host features.
Gusto's installed SDK does not implement these processes simply by being present.
Each feature needs its own persistence, policy, audit, lifecycle and acceptance.
An automation example ships disabled and has zero executions; it cannot start
payroll or invite real people.

## Exit conditions

Never describe local mock/API fixtures as sandbox validation. Never describe
an SDK mount as a complete payroll integration. Never infer production access
from an OAuth token, published open-source package or hosted-flow demonstration.
Record the exact revision, environment, actual request/response evidence and
remaining blocker at each acceptance boundary.
