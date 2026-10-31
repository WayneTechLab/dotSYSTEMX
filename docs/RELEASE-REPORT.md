# .SYSTEMX 1.11.0-beta.1 release report

This is the source review receipt for the beta prerelease. The Git tag is
`v1.11.0-beta.1` and Python package metadata uses `1.11.0b1`. The exact
published commit, release assets, and provider results must be read from the
[GitHub release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.1)
and its linked CI runs. A template release is not an installed-project,
live-service, or owner-acceptance receipt.

## Source candidate and local verification

| Claim | Prepublication evidence | Final gate |
| --- | --- | --- |
| Version and package | `.SYSTEMX/VERSION`, `SOURCE.json`, `pyproject.toml`, and the distribution manifest agree on beta.1. `release.py --check` validated **264 files and 155 Markdown documents**. | Git tag and direct `main` SHA readback on the release page. |
| Portable wheel | `dotsystemx-1.11.0b1-py3-none-any.whl`: **11,033,033 bytes**, SHA-256 `5b70730eb02fd932c8a4abc868ad7e92ae0c1a16c8f65d570f82ed142d0c3e99`; all 263 listed payload hashes and the manifest itself match exactly. An isolated Python 3.14 virtual environment installed the release candidate wheel and `systemx --version` reported beta.1. | Release-asset download and checksum readback. |
| Final local suite | `python3 -I -B -m unittest discover -s .SYSTEMX/tests -v` on macOS 27.2 / Python 3.14.5: **371 run, 366 passed, 5 skipped** in 320.487 seconds. The skips require a case-sensitive filesystem. | Four sampled GitHub Actions jobs on the tagged commit. |
| Documentation | **765 local links** checked across **142 existing Markdown files**; no missing targets. | Rendered GitHub and wiki link readback. |
| Media and white paper | The current manifest verifies **15 assets**: four retained 4K field guides and eleven 7680 × 4320 SVGs. SVG checks found a minimum **7.69:1** overlay text contrast; all eleven separate 8K JPEG export hashes matched. White-paper edition 2.1 provenance matches its manuscript, five-page PDF, and builder. | Release JPEG/PDF asset byte readback and rendered visual check. |
| Private archive | **63/63 archived source members** matched local/external originals and downloaded private Drive bytes before 38 superseded files were removed from the current repository. Private archive index SHA-256: `f6a4665a0c0668bc66ae29c27267dfde11e908c5350273eff33e1bcadd0b55b2`. | Owner-only archive index and retention records; no private URL in this public report. |

`session-settings --compact` reduced one blank-root response from 3,248 to 1,043 output bytes (67.9%). This measures that response's bytes, not billed tokens, total cost, latency, or model quality. The [release counter](../.SYSTEMX/docs/RELEASE-COUNTERS.md) observes software/media releases and GitHub deployment records separately on demand; it is not a persistent deploy counter.

## Security and runtime boundaries

Agent1 is opt-in and warning-only. Its filename scan answers zero of its 400 evidence questions, and it cannot certify a host free of malware, spyware, keyloggers, or MFA interception. The `.env` inventory stores names, not secret values, in shared records. On macOS/Linux, file-backed Agent1 operations use anchored no-follow handles and a post-open one MiB bound; existing setup changes require a full-answer preview and matching SHA guard. On Windows, dotenv and answer-file operations plus setup reconfiguration fail closed in this beta; metadata first-run setup, status, questions, and filename checks remain available. A writer with access to the same directory can still race after the final hash check, so guarded replacements require other writers to be quiescent. Repo/environment GitHub secret writes require an action-time exact-repository admin-permission check and hidden terminal input; post-write readback verifies name/scope metadata, never the secret value or a workflow consumer. A guest role label does not authorize a write. Organization-level secret writes and local vault delivery are outside this beta CLI. This provider path was tested with mocks; no live secret write is claimed.

Agent Beta's Access Matrix reference records reviewed intent. It does not verify identity, grant OS/provider access, connect a model, or start a background service. Native Windows Agent Y execution remains disabled pending process-termination verification. The portable CLI targets Python 3.9+ without third-party runtime dependencies; the planned CI matrix samples Ubuntu/Python 3.9 and 3.14, Windows/Python 3.11, and macOS/Python 3.11. A macOS PowerShell smoke check does not establish Windows-host behavior.

Codex Security Deep Scan did not start because the worker required a managed filesystem permission profile. No Deep Scan coverage or finding is claimed. Local static review and tests are separate evidence. The template prerelease does not deploy an app, install an OS service, activate a secret consumer, or certify any downstream product for production.

## GitHub Actions source and provider settings

The source workflow at [`.github/workflows/template-ci.yml`](../.github/workflows/template-ci.yml) is read-only: repository `contents: read`, no checkout credential persistence, no secret use or deploy step, and GitHub-owned `checkout`/`setup-python` actions pinned to full commit SHAs. This is a source inspection, not a provider run.

The GitHub API readback on 2026-10-31 found Actions enabled, allowed actions
restricted to GitHub-owned actions, full-SHA pinning required, default
`GITHUB_TOKEN` permission `read`, and PR approvals disabled for workflows.
These provider settings do not prove a passing run. Confirm the four job
conclusions and exact commit in the [Actions history](https://github.com/WayneTechLab/dotSYSTEMX/actions)
before treating cross-host tests as verified.

## Publication receipt destinations

| Boundary | Direct readback to record | Scope at source review |
| --- | --- | --- |
| Source and tag | Direct `main` and tag SHA, release ID, and prerelease state. | GitHub release page. |
| Package and archive | Wheel and tagged source archive SHA-256/size, exact manifest comparison. | GitHub release and checksum asset. |
| Template CI | Exact run URL, commit SHA, and four sampled job conclusions. | GitHub Actions history. |
| Wiki and Page | Beta wiki revision and linked dotSYSTEMX Page sequence/hash. | Published wiki and owner Page. |
| Private archive | Owner-only index for 63-member exact-byte archive and external-copy readback. | Private owner ledger. |
| Deployment | Timestamped GitHub deployment API count and any named downstream provider receipt. | On-demand release counter; no deployment claimed. |
| Owner acceptance | Explicit owner review of the published tag, assets, and docs. | Await owner review. |

Historical edition 2.0 paper and alpha media remain available from their published tagged releases and the private archive. Raw Blender authoring data and videos are outside this portable template.
