# Gusto SDK and account setup boundaries

## Reviewed SDK pin

This package records `@gusto/embedded-react-sdk` **0.56.6**. Its published package
declares the API dependency alias
`@gusto/embedded-api = npm:@gusto/embedded-api-v-2026-06-15@0.3.1`.
The React SDK and API client are different packages. The reviewed React peer
range is `^18.0.0 || ^19.0.0`, React Query is `^5`, and TypeScript is `^5.8.3`.
Use [VERSION-PIN.json](../VERSION-PIN.json) and the published
[npm metadata](https://registry.npmjs.org/@gusto%2fembedded-react-sdk/0.56.6).

The portable folder redistributes the exact endpoint inventory under its
upstream license; it does not ship an SDK runtime or install those dependencies.
The host owns any approved package install, lockfile and peer compatibility checks.

## Account-free choices

| Choice | What can be tested | Credential requirement |
| --- | --- | --- |
| SYSTEMX synthetic fixtures | Page layout, local transitions, role-filtered demo data and adapter contracts | None |
| Local SDK mock transport | A specifically implemented SDK workflow against synthetic wire fixtures | None; test only implemented request/response shapes |
| Gusto hosted-flow Try It Now | Gusto's hosted visual workflow | Public demo, not credentials for local API/SDK requests |
| Gusto demo environment | Real API semantics and authorized sandbox workflows | Developer organization/application with its own client credentials and authorized test company |
| Production | Approved live business operation | Separate approved environment, access and operator authority |

Gusto's [developer getting-started guide](https://docs.gusto.com/embedded-payroll/docs/getting-started)
requires a developer account, organization and application. Its official
[SDK demo app instructions](https://github.com/Gusto/embedded-react-sdk-demo-app/blob/main/README.md)
also require credentials for API integration. The reviewed sources do not
document a shared public API test key. Do not fabricate one or commit one.

[Hosted-flow Try It Now](https://docs.gusto.com/embedded-payroll/docs/try-it-now)
does not grant local OAuth/API access. A local mock is the reusable template's
account-free default; it does not pretend to be Gusto's sandbox.

## Select the actual provider program

Gusto Embedded Payroll and Gusto App Integrations are distinct onboarding/API
programs. Select the approved program before implementing endpoints, scopes and
OAuth. An existing employer account is not automatically an Embedded partner
application. App Integration time-sync guidance is not proof of equivalent
Embedded API access. See [Embedded getting started](https://docs.gusto.com/embedded-payroll/docs/getting-started)
and [App Integration time tracking](https://docs.gusto.com/app-integrations/docs/syncing-time-tracking-data).

## Server trust boundary

The browser receives no client secret, refresh token or unrestricted company
token. Authenticate the user, bind a reviewed company and permitted role on the
server, then allow only workflow endpoints justified by the selected page.
Inspect all blocks/hooks in the pinned [inventory](../sdk/endpoint-inventory.json).
Do not forward arbitrary paths or grant the entire employee dashboard to an
employee self portal: some component operations can create or change resources.
Provider routing and self authorization must hold even if the browser supplies
a different company/employee identifier.

Keep secret values in the host's approved secret store. Configuration contains
secret names only. Separate mock/demo/production credentials, company mappings,
request telemetry and webhook verification. Connection setup must not implicitly
submit payroll, purchase insurance, sign forms or change bank/tax records.

The SDK source license grants source-code rights rather than service, production
or trademark rights. Production needs the applicable Gusto onboarding and
agreements; see the pinned upstream [disclaimer](https://github.com/Gusto/embedded-react-sdk/blob/9e8b5cc94846cc95fc1a4acb0a7458035d54d170/DISCLAIMER.md).
