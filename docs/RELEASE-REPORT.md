# .SYSTEMX 1.11.0-beta.1 release report

This is the source review receipt for the beta prerelease. The intended Git tag is
`v1.11.0-beta.1` and Python package metadata uses `1.11.0b1`. The exact
published commit and release assets must be read from the
[GitHub release](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.1).
A template release is not an installed-project,
live-service, or owner-acceptance receipt.

## Source candidate and local verification

| Claim | Prepublication evidence | Final gate |
| --- | --- | --- |
| Version and package | `.SYSTEMX/VERSION`, `SOURCE.json`, and `pyproject.toml` identify beta.1. `release.py --check` validated **272 distributed files**, including **156 Markdown files**. | Read back the Git tag and direct `main` SHA on the published release. |
| Portable wheel | `dotsystemx-1.11.0b1-py3-none-any.whl`: **12,938,678 bytes**, SHA-256 `5028f5e01b732f934bcccd1bfda579ef52200b5bb76a37743bd2c05cb627fa19`; **272 payload files matched exact bytes, with no missing or extra files**, and an exact manifest match. The final wheel installed in isolated Python 3.14 and 3.11 virtual environments; each `systemx --version` reported beta.1. | Read back the published release-asset download and checksum. |
| Local suite | The completed beta source ran **373 tests: 367 passed, 6 skipped** on macOS 27.2 with both Python 3.14.5 (**371.642 s**) and the resolved Python 3.11.15 binary (**319.873 s**), using `-I -B -m unittest discover -s .SYSTEMX/tests -v`. Five skips require a case-sensitive filesystem; one requires native Windows handles. An initial 3.11 run via a user-local symlinked launcher had one environmental failure: its `venv.EnvBuilder` produced an interpreter pointed at nonexistent `/install/lib/python3.11`. The full rerun through the actual 3.11 binary passed. | Preserve the source/tag SHA and repeat on each native host before claiming host coverage; native Windows remains unverified. |
| Documentation | **808 local links** checked across **167 existing Markdown files**, with **zero missing targets**. | Rendered GitHub and wiki link readback after publication. |
| Media and white paper | The media verifier checked **22 repository assets**: 18 beta 7680 × 4320 SVGs (four feature guides, seven role cards, seven detailed agent guides) and four retained 4K JPGs. It matched **18 separate external 8K JPEG hashes** and found minimum SVG overlay text and panel color contrast **5.72:1**; that is not a full accessibility certification of the composited JPEGs. The detail guides show each role's folder, prompt/input, flow, and CLI boundary; their command panels use the project-local `bash .SYSTEMX/SYSTEMX.sh ROLE --help` form and each actual role token and subcommands (`root` for Agent 0, `agent-a` for Alpha). The installed package CLI manages lifecycle and routes into a selected project. See the [accessible text companion](../.SYSTEMX/MEDIA/Reference/agent-detail-guide.md) and [visual library](media/README.md). White-paper edition 2.1 provenance matches its manuscript, five-page PDF, and builder. No new video was made for beta. | Read back release JPEG/PDF downloads and inspect the published visuals. |
| Private archive | **63/63 archived source members** matched local/external originals and downloaded private Drive bytes before 38 superseded files were removed from the current repository. Private archive index SHA-256: `f6a4665a0c0668bc66ae29c27267dfde11e908c5350273eff33e1bcadd0b55b2`. | Owner-only archive index and retention records; no private URL in this public report. |
| Private detail-art archive | The corrected detail-art ZIP contains **24 verified members**, **34,996,366 bytes**, SHA-256 `31f02cc5b4432bcbce6163bfa56ce51875a253947a23a89cdc35859d0082f29b`. Its owner-only Drive download matched that exact hash. The companion private manifest is **4,686 bytes**, SHA-256 `bfdec1d820423397d982a29c8324b16b74096659d8becc9ba14d9208c97aca75`. | Retain the private ZIP receipt and retention owner; no private URL in this public report. |

`session-settings --compact` reduced one blank-root response from 3,248 to 1,043 output bytes (67.9%). This measures that response's bytes, not billed tokens, total cost, latency, or model quality. The [release counter](../.SYSTEMX/docs/RELEASE-COUNTERS.md) observes software/media releases and GitHub deployment records separately on demand; it is not a persistent deploy counter.

## Security and runtime boundaries

Agent1 is opt-in and warning-only. Its filename scan answers zero of its 400 evidence questions, and it cannot certify a host free of malware, spyware, keyloggers, or MFA interception. The read-only `.env` inventory returns variable names only and writes no secret values to shared records. On macOS/Linux, file-backed Agent1 operations use anchored no-follow handles and a post-open one MiB bound; existing setup changes require a full-answer preview and matching SHA guard. On Windows, dotenv and answer-file operations plus setup reconfiguration fail closed in this beta; metadata first-run setup, status, questions, and filename checks remain available. A writer with access to the same directory can still race after the final hash check, so guarded replacements require other writers to be quiescent. Repo/environment GitHub secret writes require an action-time exact-repository admin-permission check and hidden terminal input; post-write readback verifies name/scope metadata, never the secret value or a workflow consumer. A guest role label does not authorize a write. Organization-level secret writes and local vault delivery are outside this beta CLI. This provider path was tested with mocks; no live secret write is claimed.

Agent Beta's Access Matrix reference records reviewed intent. It does not verify identity, grant OS/provider access, connect a model, or start a background service. Native Windows Agent Y execution remains disabled pending process-termination verification. The portable CLI targets Python 3.9+ without third-party runtime dependencies. Maintainers run supported-host checks manually and record exact source, interpreter, operating system, and results. A macOS PowerShell smoke check does not establish Windows-host behavior.

Codex Security Deep Scan did not start because the worker required a managed filesystem permission profile. No Deep Scan coverage or finding is claimed. Local static review and tests are separate evidence. The template prerelease does not deploy an app, install an OS service, activate a secret consumer, or certify any downstream product for production.

## GitHub Actions state

The GitHub API readback on 2026-10-31 returned `enabled: false` for this
repository. The current template ships no `.github/workflows` file. Earlier
beta-candidate Actions runs are historical evidence from earlier commits,
not a passing test receipt for the final tag. No release qualification depends
on GitHub Actions or claims a verified Windows host result without a separate
source-matched manual run.

## Publication receipt destinations

| Boundary | Direct readback to record | Scope at source review |
| --- | --- | --- |
| Source and tag | Direct `main` and tag SHA, release ID, and prerelease state. | GitHub release page. |
| Package and archive | Wheel and tagged source archive SHA-256/size, exact manifest comparison. | GitHub release and checksum asset. |
| Cross-host checks | Exact source SHA, operating system, Python version, command, result, and retained local receipt for each host actually checked. | Manual host-specific validation; unrun hosts remain unverified. |
| Wiki and Page | Beta wiki revision and linked dotSYSTEMX Page sequence/hash. | Published wiki and owner Page. |
| Private archive | Owner-only index for the 63-member archive and exact-byte receipt for the 24-member detail-art ZIP. | Private owner ledger; no public Drive URL. |
| Deployment | Timestamped GitHub deployment API count and any named downstream provider receipt. | On-demand release counter; no deployment claimed. |
| Owner acceptance | Explicit owner review of the published tag, assets, and docs. | Await owner review. |

Historical edition 2.0 paper and alpha media remain available from their published tagged releases and the private archive. Raw Blender authoring data and new video files are outside this portable template.
