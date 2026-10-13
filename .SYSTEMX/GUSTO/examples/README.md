# Adopted connector example

[connector.example.json](connector.example.json) defaults to disabled with no
allowed/read-only/write actions. It stores secret names, never values. Copy and
configure it only in an adopted host after program, environment, company and
action scope are reviewed. It does not obtain credentials or grant IAM rights.

The host owns its persisted configuration. Keep local paths, tokens, real
employee/company identities and runtime logs outside tracked immutable release
files. A selected SYSTEMX release can provide the current blank example while
preserving an adopted outer copy.
