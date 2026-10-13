# Pinned Gusto SDK inventory

[endpoint-inventory.json](endpoint-inventory.json) is copied byte for byte from
the official `@gusto/embedded-react-sdk` **0.56.6** npm tarball. It contains 106
blocks, 22 flows and 25 hooks. Its SHA-256 is
`42912e7c02fa0367ae92d2c8225f4ecfa3f62f5c9508604be2e3125a06fd4074`.
[VERSION-PIN.json](../VERSION-PIN.json) records the tarball digest and API alias.

The npm package also exports this as
`@gusto/embedded-react-sdk/endpoint-inventory.json`. Use the inventory to review
all methods, paths and variables of an allowed component, including nested
flows/hooks. A namespace or UI title is not an authorization scope.

## Exported workflow families

- Company onboarding: `CompanyOnboarding.OnboardingFlow`.
- Employee management/onboarding: `EmployeeManagement.EmployeeListFlow`,
  `EmployeeManagement.DashboardFlow`, `EmployeeManagement.TerminationFlow`,
  `EmployeeOnboarding.OnboardingFlow`, `EmployeeOnboarding.OnboardingExecutionFlow`,
  `EmployeeOnboarding.SelfOnboardingFlow`.
- Contractor management/onboarding/payment flows under `ContractorManagement`
  and `ContractorOnboarding`; use exact names in the inventory.
- Payroll: `Payroll.PayrollFlow`, `Payroll.PayrollExecutionFlow`,
  `Payroll.OffCycleFlow`, `Payroll.DismissalFlow`, `Payroll.TransitionFlow`.
- PTO: `TimeOff.TimeOffFlow`.
- Information requests: `InformationRequests.InformationRequestsFlow`.

CompanyManagement exports components but has no separate flow family in this
inventory. The package describes that area as alpha. No dedicated manager,
recruiting, benefits, report, performance or general time-entry SDK flow is
claimed here. Authorized API/host implementation can complement the SDK.

## Attribution and limits

Source: [official published npm metadata](https://registry.npmjs.org/@gusto%2fembedded-react-sdk/0.56.6),
repository revision [`9e8b5cc94846cc95fc1a4acb0a7458035d54d170`](https://github.com/Gusto/embedded-react-sdk/tree/9e8b5cc94846cc95fc1a4acb0a7458035d54d170).
The exact inventory is third-party material under the
[Apache License 2.0](LICENSE-APACHE-2.0.txt). SYSTEMX-authored specifications retain
the repository's MIT license. No SDK runtime/source dependency tree is copied here.
The SDK's source license does not grant Gusto API, commercial service or trademark
rights; see the [upstream disclaimer](https://github.com/Gusto/embedded-react-sdk/blob/9e8b5cc94846cc95fc1a4acb0a7458035d54d170/DISCLAIMER.md).
