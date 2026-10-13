# Verified webhook ingestion and replay

This package defines a host receipt contract and synthetic replay example.
It does not run a webhook receiver or supply a secret. The
[example events](events.example.json) use `mock.*` names and are not provider
subscription names.

Before enabling ingress, follow the selected program's current official
[Gusto webhook documentation](https://docs.gusto.com/embedded-payroll/docs/webhooks)
and verify the actual request format, verification mechanism and subscribed
events. Do not invent an HMAC header, token format or event name from a generic
example. Record only secret names in tracked configuration.

1. Bound request size and reject invalid content/type and unknown subscriptions.
2. Preserve original bytes as required for the documented verification method.
3. Verify before parsing into trusted projections; reject unverified events.
4. Bind the event's provider company to a known authorized host organization.
5. Create a server-only dedupe receipt before queued processing. A duplicate
   delivery must not resubmit payroll, repeat payments or duplicate side effects.
6. Reconcile with an authorized read-only provider fetch rather than trusting
   the event body as the full current record.
7. Retain attempts, processing state, sanitized errors and the payload digest;
   retry transient failures with bounded backoff, and route permanent failures
   to the owner. Handle out-of-order delivery and stale versions explicitly.

Raw payloads may contain personal data. Keep them outside tracked release files,
apply a retention policy and avoid embedding them in SYSTEMX global memory or
public task receipts. Verify replay, duplicate, wrong-company, unverified,
out-of-order and partial-failure behavior in temporary tests.
