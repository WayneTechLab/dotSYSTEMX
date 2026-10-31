# On-demand release and deployment counters

The public template has no fixed deployment counter. A release distributes a
version of the template; it is not evidence that an application was deployed.
Run this read-only command only when a current GitHub observation is useful:

```bash
python3 -I -B .SYSTEMX/scripts/release_counters.py
python3 -I -B .SYSTEMX/scripts/release_counters.py --repository OWNER/REPO
```

The command uses Python's standard library and GitHub's public REST API. It
does not read a local token, write files, install a service, or run on startup.
It reports the observation time and counts published software-version releases,
`media-` releases, other published releases, and GitHub deployment records
separately. Draft releases are excluded. A deployment record is a request to
deploy a ref; its presence does not establish success or live verification.

Each count is either `{"state":"observed","count":N}` or
`{"state":"unknown","count":null}`. A failed, invalid, or truncated provider
response is **unknown**, never zero. Release and deployment requests are
independent, so a successful one can still be shown when the other fails. The
exit code is `0` when both endpoints were counted and `2` when either is
unknown. Requests have a five-second timeout, a two-megabyte response limit,
and a ten-page limit per endpoint; a complete result beyond those limits needs
a different reviewed query. Public API rate limits can produce `unknown`.

The counts are observations at one time, not a durable ledger or a single
transactional snapshot across paginated requests. For a downstream project's
actual deployment outcome, retain the target, revision, provider receipt,
deployment status, and live check in its own release record or Agent X event.
Do not copy private project paths or provider data into this reusable template.
