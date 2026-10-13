# What Gusto supplies and what the host builds

[CAPABILITIES.json](../CAPABILITIES.json) records each capability's backing,
provider workflow exports, API areas, reference fixture collection and delivery
status. `gusto-sdk` means an actual named flow from the pinned inventory;
`gusto-api` means custom host UI with separately authorized API behavior;
`systemx-native` means host implementation; `composite` combines responsibilities.
None of these labels asserts a live connection.

| Area | Provider contribution | Host contribution |
| --- | --- | --- |
| Company onboarding | Reviewed company, location, bank, tax and pay schedule SDK blocks/flow | Partner account setup, company linkage, trusted operator, application navigation |
| Employee/contractor onboarding | Named onboarding and self-onboarding flows | Invitations, trusted user/resource binding, local checklists and role enforcement |
| Payroll/pay statements/payments | Named payroll, employee management and contractor payment flows | Bounded adapter, approved actors, period readiness, review/result evidence and reconciliation |
| PTO | Named TimeOff flow and approved PTO APIs | Self/manager request journey, scoped approval queue, coverage and synchronization evidence |
| Time entries | Approved API program's payroll/time data integration | Capture, validation, approval, corrections and reviewed payroll handoff |
| Benefits | Supported configured company/employee benefit APIs | Plan/enrollment pages, eligibility/role policy and external benefit sourcing as applicable |
| Reports | Authorized custom/general ledger report APIs; hosted report flows may exist separately | Report catalog, role filters, async job state, retention and secure downloads |
| Documents | Provider tax/employment forms and signing workflows where supported | Policy documents, private storage, acknowledgments and download authorization |
| Recruiting/org/tasks/policies/assets/access/training/performance/cases/surveys/automation | No corresponding dedicated workflow claimed in the pinned SDK | Product models, pages, persistence, permissions, lifecycle and acceptance |

Native automation is not SYSTEMX Agent X scheduling or an automatic payroll
engine. Product HR tasks are not the agent work ledger. Provider benefit data
does not itself create insurance coverage, and a requested report does not mean
the async report is complete.

Official supplemental guides:
[company benefits](https://docs.gusto.com/embedded-payroll/docs/create-company-benefits),
[employee benefits](https://docs.gusto.com/embedded-payroll/docs/manage-employee-benefits),
[custom reports](https://docs.gusto.com/embedded-payroll/docs/generate-custom-reports),
[general ledger](https://docs.gusto.com/embedded-payroll/docs/retrieve-a-general-ledger-report),
[time-off requests](https://docs.gusto.com/embedded-payroll/docs/time-off-requests),
[employee self management](https://docs.gusto.com/embedded-payroll/docs/employee-self-management).
Verify the selected program, API version and authorization before adopting a
specific guide. The endpoint inventory covers the pinned SDK rather than all
possible provider API features.
