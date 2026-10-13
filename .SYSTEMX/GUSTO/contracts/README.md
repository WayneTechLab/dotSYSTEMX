# Portable contracts

These JSON Schemas describe SYSTEMX host contracts, not Gusto's API wire models.
Provider request/response validation must use the approved API version and
actual documented schemas.

- [routes.schema.json](routes.schema.json): canonical route fields, portal,
  role list, sections, mock/live-gated action descriptions and state guidance.
- [capabilities.schema.json](capabilities.schema.json): ownership, backing,
  delivery status, inventory export references and live prerequisites.
- [connector.schema.json](connector.schema.json): disabled default adapter
  example, program/environment and secret names; no credentials.
- [employee.schema.json](employee.schema.json): minimal host directory projection.
- [webhook-envelope.schema.json](webhook-envelope.schema.json): normalized
  verified/rejected receipt, not a raw provider payload or signature recipe.

The core SYSTEMX validator parses JSON and checks the distribution, but does not
automatically enforce arbitrary JSON Schema semantics. Portable contract tests
add referential/inventory/fixture checks. Hosts must validate their payloads and
permissions at the actual server boundary.
