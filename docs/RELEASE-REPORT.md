# .SYSTEMX 1.11.0-beta.4 release report

This report records the white-paper edition 2.2 publication and source/package
qualification for `1.11.0-beta.4`. The beta.3 media release and its full
[historical report](https://github.com/WayneTechLab/dotSYSTEMX/blob/v1.11.0-beta.3/docs/RELEASE-REPORT.md)
retain their own evidence and asset identities. The
[beta.4 GitHub prerelease](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.4)
identifies the final source revision and downloadable artifacts.
The final source revision is the peeled annotated `v1.11.0-beta.4` tag;
the immutable release notes state its full commit SHA. This tag identity
avoids a circular commit hash inside a file committed by that same revision.

## Scope and publication

- Template version: `1.11.0-beta.4`; Python package version: `1.11.0b4`.
- White-paper edition 2.2 examines this beta.4 source and package baseline.
  Its selectable-text PDF has 6 US Letter pages and 10 outline entries. The
  Markdown manuscript is the accessible text alternative; the PDF is not
  tagged PDF/UA.
- The paper corrects the current media inventory and documents the beta.2
  stock governance catalogs, Agent 0 roster, host-controlled CLI/IDE routes,
  named and configured Agent Y adapters, and authority boundaries.
- The prior edition 2.1 is preserved at its
  [original beta.1 tag](https://github.com/WayneTechLab/dotSYSTEMX/tree/v1.11.0-beta.1/.SYSTEMX/MEDIA/White-Paper)
  and in an owner archive. Edition 2.0 remains in immutable alpha.5 history.
- The twelve beta.3 SVGs and the
  [beta.3 8K export pack](https://github.com/WayneTechLab/dotSYSTEMX/releases/tag/v1.11.0-beta.3)
  retain that release's art provenance. No new image, video, Blender scene,
  narration, or raw authoring master is bundled for this paper release.

## White-paper evidence

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Markdown manuscript | 21,154 | `0cd978e8b4784a66ded5991f7ef2ab8ac5a7d04c3ad1b9562d7a075a47d556c7` |
| PDF | 27,182 | `6008ef999e329f19e0795995ecb7bd02a2915e8c6cf32fa39219447ead87ab12` |
| PDF builder | 8,396 | `690bfcbc7a9b1f0469db6fb955103a0e68f925fa27dfc4bdcba908e99cc3c7fd` |
| Provenance JSON | 1,551 | `4345c83cc06cd19138d888e300d2b952ea279d32c2215c862f4f915659dc433e` |

ReportLab 4.4.9 and pypdf 6.10.0 built the PDF deterministically. Every
rendered page was inspected for clipping, overlap, headers, footers, and links;
extracted text, document metadata, ten outline entries, and the provenance
checksums were verified. The PDF was rebuilt byte-identically after the final
manuscript correction.

## Source, package, and runtime checks

| Boundary | Evidence |
| --- | --- |
| Portable distribution | `release.py` validates 269 exact files and 155 Markdown documents; manifest SHA-256 `5b5584478df840699bdc2824f68cf52cb1763db0c000422379174f0fcceb7b5e`. |
| Current graphics | Twelve canonical SVGs, 4,810,816 bytes, 11 source panels plus one locked atlas; minimum checked text contrast 10.43:1. The verifier accepts the unchanged beta.3 art baseline in the later beta.4 template and rejects older or future baselines. |
| Python suites | Final clean terminal runs: Python 3.11.15 ran 406 tests in 263.923 seconds, OK with 6 skipped; Python 3.14.5 ran 406 tests in 303.662 seconds, OK with 6 skipped. Both processes exited zero against the frozen beta.4 portable manifest. |
| Wheel | Clean build: `dotsystemx-1.11.0b4-py3-none-any.whl`, 4,182,214 bytes, SHA-256 `1dd87d3b293f1412a3d8c79dfe2c8ad3e9e3da9f371b6eac7771c1989613c489`. The full-wheel gate matched all 269 portable files byte for byte, validated package metadata, entry point, and `RECORD`, and rejected unexpected installable members. |
| Installed wheel | Fresh isolated Python 3.11.15 and 3.14.5 virtual environments reported beta.4. Both completed local-source first-run preview/apply and offline selected-template validate and doctor in temporary project roots. |
| GitHub Actions | Repository Actions permission readback returned `enabled=false`; no workflow is shipped. |
| Public source and pages | The final tag, release assets, README, wiki, and Page require publication-time readback. The immutable GitHub release notes and current wiki receipt record those observations after publication; this tagged report does not claim future provider state. |

## Acceptance boundary

This release qualifies the reviewed reusable source and package on the tested
host interpreters. It does not install an adopter's project, authenticate an
online assistant, grant provider access, create an OS service, inspect a device
for malware, deploy an application, or prove measured token savings. The
Access Matrix remains default-deny and Agenda choices remain unset in the
stock template. A downstream operator must verify its own credentials,
provider and host integration, runtime behavior, deployment when relevant,
and owner acceptance.
