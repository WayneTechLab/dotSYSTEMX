# Page-by-page HR specification

The [route catalog](../ROUTES.json) is the machine-readable canonical source.
These 64 page specifications cover four portals; route placeholders are host
identifiers resolved through trusted company membership. They are not provider
UUIDs or client-granted authority. Match static routes before parameter routes
(for example payroll history before `:payrollId`).

Every page needs an accessible title/navigation, loading state, scoped empty
state, sanitized recoverable error, keyboard controls and responsive layout.
No page may present a mock transition as a provider mutation. Live forms need
server validation, concurrency/idempotency behavior where applicable and retained
result evidence. Sections and actions describe the complete target design;
portable delivery is specification, while host implementation maturity is checked
separately.

## Portals and navigation

Employer navigation groups company setup, people, payroll, benefits, time,
documents/reports, native HR and connection settings. Employee navigation is
self-scoped; manager navigation contains only direct-report work; contractor
navigation is contractor self-scoped. Unavailable groups do not appear, and a
direct URL must enforce the same permission. Back links never widen scope.

## Employer administration

### People workspace

- Route: `/admin/hr` (`admin-hr-home`).
- Capability/backing: `hr-overview` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`, `auditor`.
- Inputs: company, scoped employees/contractors and assigned tasks.
- Sections: Company readiness, Employee onboarding, Open HR tasks, Provider mode.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No people workspace records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Company setup

- Route: `/admin/hr/company` (`admin-company-setup`).
- Capability/backing: `company-setup` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: company readiness and approved provider onboarding status.
- Sections: Legal entity readiness, Industry, Signer, Setup checklist.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No company setup records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Work locations

- Route: `/admin/hr/company/locations` (`admin-company-locations`).
- Capability/backing: `company-locations` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: location summaries and registration readiness.
- Sections: Worksites, Jurisdiction readiness, Location detail.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No work locations records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Company taxes

- Route: `/admin/hr/company/taxes` (`admin-company-taxes`).
- Capability/backing: `company-taxes` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: provider tax readiness; no raw tax identifiers in the mock.
- Sections: Federal setup, State setup, Provider readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No company taxes records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Company banking

- Route: `/admin/hr/company/banking` (`admin-company-banking`).
- Capability/backing: `company-banking` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: provider verification readiness; no bank values in the mock.
- Sections: Verification status, Provider bank workflow, Account authorization.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No company banking records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Pay schedules

- Route: `/admin/hr/company/pay-schedules` (`admin-pay-schedules`).
- Capability/backing: `pay-schedules` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: pay schedule summaries and assigned employees.
- Sections: Schedule calendar, Assignments, Effective dates.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No pay schedules records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Employees

- Route: `/admin/hr/employees` (`admin-employees`).
- Capability/backing: `employee-directory` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`, `auditor`.
- Inputs: role-filtered employee directory projection.
- Sections: Searchable roster, Status filters, Scoped profile links.
- Actions: Filter roster (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No employees records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Employee profile

- Route: `/admin/hr/employees/:employeeId` (`admin-employee-profile`).
- Capability/backing: `employee-profile` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: bound employee directory projection plus permitted profile details.
- Sections: Employment summary, Team and location, Approved profile sections.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No employee profile records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Employee onboarding

- Route: `/admin/hr/employees/:employeeId/onboarding` (`admin-employee-onboarding`).
- Capability/backing: `employee-onboarding` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: bound employee checklist, invitation and provider readiness.
- Sections: Readiness checklist, Invitation status, Provider workflow status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No employee onboarding records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Employee compensation

- Route: `/admin/hr/employees/:employeeId/compensation` (`admin-employee-compensation`).
- Capability/backing: `employee-compensation` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: explicitly authorized employee compensation projection.
- Sections: Compensation summary, Pay history, Reviewed changes.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No employee compensation records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Contractors

- Route: `/admin/hr/contractors` (`admin-contractors`).
- Capability/backing: `contractor-directory` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`, `auditor`.
- Inputs: role-filtered contractor directory projection.
- Sections: Individual and business roster, Onboarding status, Profile links.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No contractors records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Contractor profile

- Route: `/admin/hr/contractors/:contractorId` (`admin-contractor-profile`).
- Capability/backing: `contractor-profile` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: bound contractor profile and host task references.
- Sections: Contractor identity, Service summary, Payment readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No contractor profile records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Contractor onboarding

- Route: `/admin/hr/contractors/:contractorId/onboarding` (`admin-contractor-onboarding`).
- Capability/backing: `contractor-onboarding` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: bound contractor checklist and provider readiness.
- Sections: Invitation, Profile readiness, Provider onboarding.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No contractor onboarding records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Payroll workspace

- Route: `/admin/hr/payroll` (`admin-payroll`).
- Capability/backing: `payroll` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: approved pay period, calculation state and permitted totals.
- Sections: Upcoming run, Readiness blockers, Previous runs.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No payroll workspace records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Payroll run

- Route: `/admin/hr/payroll/:payrollId` (`admin-payroll-run`).
- Capability/backing: `payroll` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: approved pay period, calculation state and permitted totals.
- Sections: Pay period, Approved hours, Calculation preview, Submission readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No payroll run records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Payroll history

- Route: `/admin/hr/payroll/history` (`admin-payroll-history`).
- Capability/backing: `payroll` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`, `auditor`.
- Inputs: approved pay period, calculation state and permitted totals.
- Sections: Run status, Periods, Role-filtered totals.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No payroll history records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Contractor payments

- Route: `/admin/hr/contractor-payments` (`admin-contractor-payments`).
- Capability/backing: `contractor-payments` / `gusto-sdk`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: bound contractor payment history and approved payment state.
- Sections: Payments, Status, Approved payment setup.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No contractor payments records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Benefits

- Route: `/admin/hr/benefits` (`admin-benefits`).
- Capability/backing: `benefits` / `gusto-api`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: permitted configured plan, eligibility and enrollment projection.
- Sections: Plans, Eligibility, Enrollment status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No benefits records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Time tracking

- Route: `/admin/hr/time` (`admin-time`).
- Capability/backing: `time-tracking` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: self/direct-report time entries, submission and approval state.
- Sections: Timesheets, Approval queues, Payroll handoff.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No time tracking records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Time off

- Route: `/admin/hr/time-off` (`admin-time-off`).
- Capability/backing: `time-off` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`.
- Inputs: self/direct-report request intervals, balances and decision state.
- Sections: Policies and balances, Request queue, Coverage calendar.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No time off records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Documents

- Route: `/admin/hr/documents` (`admin-documents`).
- Capability/backing: `documents` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`, `auditor`.
- Inputs: actor-filtered metadata; download/signing permissions checked again.
- Sections: Document categories, Signature status, Scoped access.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No documents records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Reports

- Route: `/admin/hr/reports` (`admin-reports`).
- Capability/backing: `reporting` / `composite`.
- Roles: `employer-owner`, `payroll-admin`, `hr-admin`, `auditor`.
- Inputs: approved report catalog, filters, job state and redacted results.
- Sections: Report catalog, Filters, Export scope.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No reports records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Recruiting

- Route: `/admin/hr/recruiting` (`admin-recruiting`).
- Capability/backing: `recruiting` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: restricted job/candidate/interview/offer records.
- Sections: Jobs, Candidates, Interview stages, Offers.
- Actions: Review demo records (`mock`).
- Empty state: No recruiting records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Organization

- Route: `/admin/hr/organization` (`admin-organization`).
- Capability/backing: `organization` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: department, role and verified reporting-line projection.
- Sections: Departments, Teams, Reporting lines.
- Actions: Review demo records (`mock`).
- Empty state: No organization records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### People tasks

- Route: `/admin/hr/tasks` (`admin-tasks`).
- Capability/backing: `tasks` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: product checklist assignments, due state and evidence.
- Sections: Assigned work, Due dates, Completion evidence.
- Actions: Review demo records (`mock`).
- Empty state: No people tasks records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Policies

- Route: `/admin/hr/policies` (`admin-policies`).
- Capability/backing: `policies` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: published edition/effective date and subject acknowledgments.
- Sections: Published editions, Acknowledgments, Effective dates.
- Actions: Review demo records (`mock`).
- Empty state: No policies records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Assets

- Route: `/admin/hr/assets` (`admin-assets`).
- Capability/backing: `assets` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: asset assignment/custody/return records.
- Sections: Inventory, Assignments, Returns.
- Actions: Review demo records (`mock`).
- Empty state: No assets records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Access

- Route: `/admin/hr/access` (`admin-access`).
- Capability/backing: `access` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: trusted memberships and invitation decisions.
- Sections: Memberships, Invitations, Role decisions.
- Actions: Review demo records (`mock`).
- Empty state: No access records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Training

- Route: `/admin/hr/training` (`admin-training`).
- Capability/backing: `training` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: course assignment/progress/evidence.
- Sections: Courses, Assignments, Completion.
- Actions: Review demo records (`mock`).
- Empty state: No training records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Performance

- Route: `/admin/hr/performance` (`admin-performance`).
- Capability/backing: `performance` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: record audience, goals and reviews.
- Sections: Goals, Review cycles, Scoped feedback.
- Actions: Review demo records (`mock`).
- Empty state: No performance records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### People cases

- Route: `/admin/hr/cases` (`admin-cases`).
- Capability/backing: `cases` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: restricted case metadata, owner and classification.
- Sections: Restricted case queue, Assigned owner, Retention.
- Actions: Review demo records (`mock`).
- Empty state: No people cases records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Surveys

- Route: `/admin/hr/surveys` (`admin-surveys`).
- Capability/backing: `surveys` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: campaign metadata and appropriately private response summaries.
- Sections: Campaigns, Response status, Aggregate results.
- Actions: Review demo records (`mock`).
- Empty state: No surveys records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Automation

- Route: `/admin/hr/automation` (`admin-automation`).
- Capability/backing: `automation` / `systemx-native`.
- Roles: `employer-owner`, `hr-admin`.
- Inputs: disabled rules, allowed action, owner and actual execution receipts.
- Sections: Proposed rules, Approvals, Execution receipts.
- Actions: Review demo records (`mock`).
- Empty state: No automation records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Gusto connection

- Route: `/admin/hr/integrations/gusto` (`admin-gusto-connection`).
- Capability/backing: `provider-connection` / `systemx-native`.
- Roles: `employer-owner`, `payroll-admin`.
- Inputs: reviewed program/environment, server company mapping and nonsecret health status.
- Sections: Disabled/mock/demo/production mode, Application readiness, Company linkage, Health status.
- Actions: Review demo records (`mock`).
- Empty state: No gusto connection records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

## Employee self-service

### My workspace

- Route: `/employee` (`employee-home`).
- Capability/backing: `hr-overview` / `composite`.
- Roles: `employee`.
- Inputs: company, scoped employees/contractors and assigned tasks.
- Sections: My onboarding, My tasks, Pay summary readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my workspace records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My profile

- Route: `/employee/profile` (`employee-profile`).
- Capability/backing: `employee-profile` / `composite`.
- Roles: `employee`.
- Inputs: bound employee directory projection plus permitted profile details.
- Sections: Own contact details, Employment summary, Approved changes.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my profile records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My onboarding

- Route: `/employee/onboarding` (`employee-onboarding`).
- Capability/backing: `employee-onboarding` / `gusto-sdk`.
- Roles: `employee`.
- Inputs: bound employee checklist, invitation and provider readiness.
- Sections: Own checklist, Provider self-onboarding, Completion status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my onboarding records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My pay

- Route: `/employee/pay` (`employee-pay`).
- Capability/backing: `paystubs` / `gusto-sdk`.
- Roles: `employee`.
- Inputs: bound employee statement summary; signed/provider download is separately authorized.
- Sections: Own pay summary, Latest pay statement, Pay dates.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my pay records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My paystubs

- Route: `/employee/paystubs` (`employee-paystubs`).
- Capability/backing: `paystubs` / `gusto-sdk`.
- Roles: `employee`.
- Inputs: bound employee statement summary; signed/provider download is separately authorized.
- Sections: Own statements, Periods, Provider download readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my paystubs records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My tax documents

- Route: `/employee/tax-documents` (`employee-tax-documents`).
- Capability/backing: `documents` / `composite`.
- Roles: `employee`.
- Inputs: actor-filtered metadata; download/signing permissions checked again.
- Sections: Own tax documents, Delivery status, Provider form access.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my tax documents records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My benefits

- Route: `/employee/benefits` (`employee-benefits`).
- Capability/backing: `benefits` / `gusto-api`.
- Roles: `employee`.
- Inputs: permitted configured plan, eligibility and enrollment projection.
- Sections: Own eligibility, Plans, Enrollment status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my benefits records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My time

- Route: `/employee/time` (`employee-time`).
- Capability/backing: `time-tracking` / `composite`.
- Roles: `employee`.
- Inputs: self/direct-report time entries, submission and approval state.
- Sections: Own entries, Submission status, Corrections.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my time records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My time off

- Route: `/employee/time-off` (`employee-time-off`).
- Capability/backing: `time-off` / `composite`.
- Roles: `employee`.
- Inputs: self/direct-report request intervals, balances and decision state.
- Sections: Own requests, Balances, Request status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my time off records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My documents

- Route: `/employee/documents` (`employee-documents`).
- Capability/backing: `documents` / `composite`.
- Roles: `employee`.
- Inputs: actor-filtered metadata; download/signing permissions checked again.
- Sections: Own documents, Signatures, Acknowledgments.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my documents records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My tasks

- Route: `/employee/tasks` (`employee-tasks`).
- Capability/backing: `tasks` / `systemx-native`.
- Roles: `employee`.
- Inputs: product checklist assignments, due state and evidence.
- Sections: Assigned checklist, Due dates, Completion.
- Actions: Review demo records (`mock`).
- Empty state: No my tasks records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My training

- Route: `/employee/training` (`employee-training`).
- Capability/backing: `training` / `systemx-native`.
- Roles: `employee`.
- Inputs: course assignment/progress/evidence.
- Sections: Assigned courses, Progress, Completion evidence.
- Actions: Review demo records (`mock`).
- Empty state: No my training records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My goals and reviews

- Route: `/employee/performance` (`employee-performance`).
- Capability/backing: `performance` / `systemx-native`.
- Roles: `employee`.
- Inputs: record audience, goals and reviews.
- Sections: Own goals, Shared reviews, Feedback access.
- Actions: Review demo records (`mock`).
- Empty state: No my goals and reviews records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My policies

- Route: `/employee/policies` (`employee-policies`).
- Capability/backing: `policies` / `systemx-native`.
- Roles: `employee`.
- Inputs: published edition/effective date and subject acknowledgments.
- Sections: Published policy editions, Own acknowledgments, Effective dates.
- Actions: Review demo records (`mock`).
- Empty state: No assigned records are available for this actor. Show only a scoped next step.
- Error state: Deny company/self/direct-report mismatches and show a sanitized accessible retry or owner handoff.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My equipment

- Route: `/employee/assets` (`employee-assets`).
- Capability/backing: `assets` / `systemx-native`.
- Roles: `employee`.
- Inputs: asset assignment/custody/return records.
- Sections: Own assigned equipment, Custody, Return handoff.
- Actions: Review demo records (`mock`).
- Empty state: No assigned records are available for this actor. Show only a scoped next step.
- Error state: Deny company/self/direct-report mismatches and show a sanitized accessible retry or owner handoff.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My surveys

- Route: `/employee/surveys` (`employee-surveys`).
- Capability/backing: `surveys` / `systemx-native`.
- Roles: `employee`.
- Inputs: campaign metadata and appropriately private response summaries.
- Sections: Assigned campaigns, Own response status, Privacy information.
- Actions: Review demo records (`mock`).
- Empty state: No assigned records are available for this actor. Show only a scoped next step.
- Error state: Deny company/self/direct-report mismatches and show a sanitized accessible retry or owner handoff.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

## Manager workspace

### Team workspace

- Route: `/manager/hr` (`manager-home`).
- Capability/backing: `hr-overview` / `composite`.
- Roles: `manager`.
- Inputs: company, scoped employees/contractors and assigned tasks.
- Sections: Direct reports, Team onboarding, Approval queues.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No team workspace records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My team

- Route: `/manager/hr/team` (`manager-team`).
- Capability/backing: `organization` / `systemx-native`.
- Roles: `manager`.
- Inputs: department, role and verified reporting-line projection.
- Sections: Direct reports, Job summaries, Team availability.
- Actions: Review demo records (`mock`).
- Empty state: No my team records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team time

- Route: `/manager/hr/time` (`manager-time`).
- Capability/backing: `time-tracking` / `composite`.
- Roles: `manager`.
- Inputs: self/direct-report time entries, submission and approval state.
- Sections: Direct-report timesheets, Approval decisions, Corrections.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No team time records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team time off

- Route: `/manager/hr/time-off` (`manager-time-off`).
- Capability/backing: `time-off` / `composite`.
- Roles: `manager`.
- Inputs: self/direct-report request intervals, balances and decision state.
- Sections: Direct-report requests, Coverage, Approval decisions.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No team time off records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team tasks

- Route: `/manager/hr/tasks` (`manager-tasks`).
- Capability/backing: `tasks` / `systemx-native`.
- Roles: `manager`.
- Inputs: product checklist assignments, due state and evidence.
- Sections: Scoped assignments, Due dates, Completion evidence.
- Actions: Review demo records (`mock`).
- Empty state: No team tasks records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team performance

- Route: `/manager/hr/performance` (`manager-performance`).
- Capability/backing: `performance` / `systemx-native`.
- Roles: `manager`.
- Inputs: record audience, goals and reviews.
- Sections: Direct-report goals, Review cycle, Shared feedback.
- Actions: Review demo records (`mock`).
- Empty state: No team performance records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team assets

- Route: `/manager/hr/assets` (`manager-assets`).
- Capability/backing: `assets` / `systemx-native`.
- Roles: `manager`.
- Inputs: asset assignment/custody/return records.
- Sections: Assigned equipment, Returns, Owner handoff.
- Actions: Review demo records (`mock`).
- Empty state: No team assets records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### Team training

- Route: `/manager/hr/training` (`manager-training`).
- Capability/backing: `training` / `systemx-native`.
- Roles: `manager`.
- Inputs: course assignment/progress/evidence.
- Sections: Direct-report assignments, Progress, Completion evidence.
- Actions: Review demo records (`mock`).
- Empty state: No assigned records are available for this actor. Show only a scoped next step.
- Error state: Deny company/self/direct-report mismatches and show a sanitized accessible retry or owner handoff.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

## Contractor self-service

### Contractor workspace

- Route: `/contractor` (`contractor-home`).
- Capability/backing: `hr-overview` / `composite`.
- Roles: `contractor`.
- Inputs: company, scoped employees/contractors and assigned tasks.
- Sections: Own onboarding, Own tasks, Payment readiness.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No contractor workspace records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My contractor profile

- Route: `/contractor/profile` (`contractor-profile`).
- Capability/backing: `contractor-profile` / `composite`.
- Roles: `contractor`.
- Inputs: bound contractor profile and host task references.
- Sections: Own profile, Address readiness, Approved changes.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my contractor profile records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My contractor onboarding

- Route: `/contractor/onboarding` (`contractor-onboarding`).
- Capability/backing: `contractor-onboarding` / `gusto-sdk`.
- Roles: `contractor`.
- Inputs: bound contractor checklist and provider readiness.
- Sections: Own checklist, Provider self-onboarding, Completion status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my contractor onboarding records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My payments

- Route: `/contractor/payments` (`contractor-payments`).
- Capability/backing: `contractor-payments` / `gusto-sdk`.
- Roles: `contractor`.
- Inputs: bound contractor payment history and approved payment state.
- Sections: Own payment history, Statements, Status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my payments records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My contractor documents

- Route: `/contractor/documents` (`contractor-documents`).
- Capability/backing: `documents` / `composite`.
- Roles: `contractor`.
- Inputs: actor-filtered metadata; download/signing permissions checked again.
- Sections: Own tax documents, Signatures, Delivery status.
- Actions: Review demo records (`mock`), Open approved provider workflow (`live-gated`).
- Empty state: No my contractor documents records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.

### My contractor tasks

- Route: `/contractor/tasks` (`contractor-tasks`).
- Capability/backing: `tasks` / `systemx-native`.
- Roles: `contractor`.
- Inputs: product checklist assignments, due state and evidence.
- Sections: Assigned work, Due dates, Completion.
- Actions: Review demo records (`mock`).
- Empty state: No my contractor tasks records are available for this actor and company. Show a scoped next step without inventing completion.
- Error state: Show an accessible error with a retry or owner handoff. Deny unknown membership, company mismatch and unavailable provider modes before reading sensitive records.
- Acceptance: correct company and resource scope, permitted fields only, understandable state and actual result evidence; external actions remain gated until the approved adapter is configured.
