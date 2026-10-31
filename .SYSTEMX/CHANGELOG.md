# Changelog

The public release history is maintained in the
[Versions and changelog wiki](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog).
This copy travels with the folder for offline use.

## 1.11.0-beta.1 — Agent Beta, Agent1, and Agenda

- Add optional named BOT/DOT workspaces for Agent Beta, with separate records
  and no provider activation in the public seed. A guarded `agent-beta
  access-link` can attach a same-actor reviewed-intent ACC decision to an
  existing BOT/DOT record without connecting a provider or granting access.
- Add Agent1 advisory security and access assessment, a first-run setup path,
  and a bounded read-only stdio session. Secrets stay outside portable records.
  An explicit repository/environment Actions secret set requires a verified
  action-time repository admin permission and reads back name/scope metadata;
  first-run actor labels do not authorize writes. Organization secret writes
  remain outside the beta CLI.
- Add 20 default-deny Access Matrix role and instance rows to canonical JSON
  and an Excel review workbook. Reviewed decisions and Agent Alpha Agenda
  options start empty. Guarded `agenda decision-add` records intent, never an
  actual access grant; Agent X events and canonical task status stay separate.
- Add `session-settings --compact`: on the blank root template, output shrank
  from 3,248 to 1,043 bytes (67.9% fewer bytes), with no claim about billed
  tokens or latency. Add a read-only, on-demand GitHub release/deployment
  counter that reports observation time and unknown when data is unavailable.
- Support SemVer `alpha < beta < final` release discovery and Python package
  spelling `1.11.0b1`; existing projects keep their own records during update.
  Add a bounded read-only GitHub Actions compatibility matrix for selected
  Python versions on Ubuntu, Windows and macOS. A source test or CI job does
  not certify a downstream app or device.
- Publish a separate current white-paper edition 2.1 and new beta infographics
  while retaining older editions and working media in historical archives.
  No video or raw Blender authoring data is added to the reusable template.
- Extend the CLI, setup/uninstall guides, format contract, wiki-ready manuals,
  and asset inventory. The local alpha.8 work was a draft, not a published
  release or immutable tag.

## 1.11.0-alpha.7 — Generic template and reference-library cleanup

- Remove the current repository's film-companion directories and the optional
  white-paper/audio authoring component, including its component-specific tests.
  Published media and authoring archives remain separate from reusable defaults;
  historical immutable release identities are preserved.
- Keep published PDFs, the four-part infographic posters, legitimate reference
  images, and their static provenance. Replace current production-directory and
  media-download links with generic reference navigation and hosted YouTube
  guidance. Add no video, audio, caption, Blender, or render payload to the template.
- Refresh the public README, current install examples, and distribution metadata
  for alpha.7. The hosted film continues to describe its recorded alpha.6 baseline;
  this patch introduces no runtime capability, schema, provider, or dependency.
- Preserve actual runtime tests, schemas, policy, blank project records, manual
  updates, and additive owner-file/default-cache retention. Repository ignore
  rules protect this source checkout without changing the adopted folder's
  user-payload policy. GitHub Actions remains disabled.

## 1.11.0-alpha.6 — YouTube introduction and verified media links

- Link the public [YouTube introduction](https://www.youtube.com/watch?v=-EM-T6uNQAs)
  from the README, media library, and wiki, with a clickable
  [3840 × 2160 poster](https://github.com/WayneTechLab/dotSYSTEMX/releases/download/media-intro-v1.0/SYSTEMX-Introduction-v1.0-poster-4K.jpg).
  Keep original MP4, caption, and transcript downloads available independently.
- Distinguish the 1080p film and its ten animated scenes/native MP4 chapter
  markers from the 4K thumbnail and nine YouTube navigation chapters.
- Refresh current installation examples and distribution metadata for alpha.6.
  Keep white paper edition 2.0, its alpha.4 examined implementation and alpha.5
  publication identity, and the alpha.3 four-part field guide unchanged.
- Retain generic blank project records, manual updates, additive preservation,
  and the existing runtime behavior. No GitHub Actions workflow or runtime
  dependency is added; repository Actions remains disabled.

## 1.11.0-alpha.5 — White paper edition 2.0

- Replace the active edition 1.2 paper with edition 2.0 PDF, editable Markdown,
  publication metadata, and a sanitized local-verification record. Earlier
  editions remain available in immutable history and existing adopted folders.
- Document ROOT, scoped .SYSTEMXP records, Agent 0/X/Y/Z, Agent Alpha, the ten
  AUTOBOT reference functions, local DATA, and their distinct authority and
  evidence boundaries. Add four technical figures in PNG and SVG formats;
  the PDF includes clickable references and navigation.
- Pin the examined implementation to `1.11.0-alpha.4`, commit
  `e086ba15a1e70c6b585b8f12a703defc5c984b2c`. Keep publication edition 2.0,
  the alpha.5 distribution, and the existing `1.11.0-alpha.3` 4K field-guide edition
  distinct rather than relabeling their evidence.
- Retain the provider-free walkthrough's 30 local CLI commands on both
  Python 3.9 and 3.14, including aggregate task mapping, stale fingerprints,
  original-observation reuse, completion-review gates, and future-event
  refusal checks. These synthetic checks do not establish model quality,
  autonomous throughput, or live provider synchronization.
- Present input-token arithmetic as a hypothetical accounting model and
  evaluation proposal; no measured token, cost, or processing-time savings
  are claimed. This publication update changes no core runtime behavior,
  blank project seeds, update-preservation policy, or GitHub Actions setting.

## 1.11.0-alpha.4 — Restore the generic template boundary

- Remove the application-specific integration package, its dedicated validation
  fixtures, and its public setup page from the distributed base template.
- Remove provider-specific appendices and host-application links from the
  README and portable documentation. Application SDKs, business workflows,
  credentials, and runtime fixtures remain the adopting project's responsibility.
- Update distribution metadata and installation examples while retaining the
  ROOT-inclusive four-part field guide and its recorded media edition.
- Keep core project records blank and preserve existing adopted files during
  additive installation and updates. Removing files from this template does not
  silently delete a user's local copy or change historical releases.

## 1.11.0-alpha.3 — ROOT-inclusive four-part field guide

- Refresh the four selected 3840 × 2160 infographic exports to show ROOT,
  SX-RULES, SX-MILESTONE, Agent 0/X/Y/Z, Agent Alpha, ten AUTOBOT reference
  functions, DATA, tooling, and named .SYSTEMXP scopes together.
- Explain canonical task-state authority, observed harness and optional bot
  TODOs, read-only delta reports, authorized reconciliation, and fresh readback.
  External completion still requires normal evidence, review, and acceptance.
- Update README, accessible companion, prompt records, asset provenance, and
  public wiki navigation. Retain native/export dimensions and exact-byte hashes;
  a 4K canvas export is not a claim of native 4K generation.
- Preserve the four earlier environment cards, frozen white paper, blank project
  seeds, and runtime coordination behavior.

## 1.11.0-alpha.2 — ROOT write boundaries and full manual review

- Validate the complete rendered ROOT response before committing a new record.
  Oversized preview and apply requests now fail without changing the ledger.
  Packet and response limits count the indented UTF-8 JSON actually emitted,
  including scope and capability metadata.
- Extend Agent Y's protected coordination paths to `ROOT/` and `AUTOBOT/`,
  including explicit allow-path requests and edits detected beneath a broader
  allowed parent. CLI workers return proposals; shared record changes remain
  with the coordinator's existing acceptance and integration boundary. Retain
  older handoff history unchanged; execution and readiness enforce the current
  policy while inspection, cancellation, and recovery keep their normal gates.
- Review README and the portable/wiki manuals together. Correct remaining
  wave/execution-batch terminology, optional-feature onboarding, target/CWD
  instructions, library preview/apply parity, and the first milestone/task
  example. Document `SingleTask` as the prose alias for an `action` node.
- Clarify that registration and record commands do not execute providers,
  while an explicitly authorized Agent Y run can. Expand the technical map
  with ROOT, AUTOBOT, DATA, and Agent Alpha.
- Label the retained graphics and frozen white paper by their examined
  baselines; link later ROOT guidance without changing image or paper bytes.
  Keep public seeds blank and preserve adopted files during updates.

## 1.11.0-alpha.1 — Optional ROOT planning and observed task deltas

- Added `ROOT/SX-RULES.md` for the internal operating contract and
  `ROOT/SX-MILESTONE.md` for reusable planning terms, tool cards, and worked
  examples. Current environment/user instructions retain their authority.
- Reconciled the planning outline as milestone → wave → phase → optional group
  → task → optional subtask → single action. Projects may skip levels and choose
  their own counts. Expand the next bounded work only; no numeric task quota or
  complete combinatorial tree is generated.
- Separated originating requests (`RTask`), delegated requests (`STask`),
  hierarchy, task state, and Agent X events. The existing `WORK/TASKS.json`
  remains the only task-status ledger, including evidence and acceptance gates.
- Added optional preview-first `root` commands for blank initialization,
  immutable request/plan records, many-to-many harness/bot task mappings,
  evidence-linked observations, bounded tool cards, and read-only delta reports.
  Canonical task changes invalidate old observation fingerprints. Recorded
  external completion cannot accept a canonical task.
- Added independent selected `.SYSTEMXP/ROOT` support and dedicated blank seeds.
  Older scopes can omit this extension. Additive updates preserve existing
  local ROOT files; new default tools live in the selected immutable release.
- Added distribution/package guards, regressions, menu option 21, and public
  manual links. ROOT records do not execute tools, authenticate callers, connect
  to IDE/cloud APIs, synchronize remote state, or start retry/check loops.

The four-page image guide remains the labeled 1.10.0-alpha.3 media edition;
current ROOT behavior is documented in text and Mermaid. Public project records
remain blank. Alpha status and the existing permission boundaries continue.

## 1.10.0-alpha.3 — Four-page system infographic field guide

- Replaced the current one-page poster with four 3840 × 2160 imagegen exports:
  complete overview; Agent 0/X/Y/Z coordination and tools; AGENTA and all ten
  AUTOBOT specialists; DATA, named .SYSTEMXP projects and update/recovery boundaries.
- Added a complete accessible text companion and generation/correction prompts.
  Recorded native 1672 × 941 dimensions, 4K canvas upscaling, raw-byte checksums,
  feature baseline and export settings. Each portable image stays below 2 MiB.
- Updated README, portable media navigation and wiki guides. The prior poster
  stays available in immutable history; the four environment cards and frozen
  white paper retain their original examined baselines.
- Updated portable inventory and package version for additive adoption. Existing
  installations keep their local records, files and prior media; no runtime
  behavior, project seed, agent policy or GitHub Actions setting changes.

## 1.10.0-alpha.2 — Final validation boundary fixes

- Corrected optional validation to respect the AUTOBOT request ledger's 8 MiB
  bound independently of the 256 KiB context-file bound. A regression retains
  a valid 300 KiB ledger unchanged through validation and initialization.
- Strict public-template validation rejects unlisted DATA payload paths before
  parsing their contents. Adopted validation continues to leave payload outside
  the project-record scan.
- This is the published release of the AUTOBOT/DATA addition. The initial
  alpha.1 source tag is retained without a release; it was not repointed.

## 1.10.0-alpha.1 — On-demand AUTOBOT and local DATA

- Added the optional tier-2 `AUTOBOT/` reference panel with ten exact-case named
  specialist files: Design, Soul, Memory, Rules, Research, Brand, Media, Tokens,
  Data, and Archive. `AGENTA.MD` defines Agent Alpha (`agent.a`), activated
  separately from X/Y/Z; the public registry still contains only Agent 0.
- Added preview-first `autobot` / `agent-a` tools for additive initialization,
  bounded selected context, fingerprinted request reuse, explicit evidence-linked
  completion, and stale-context reporting. No bot process, recursive routing,
  model call, task acceptance, or background refresh is started.
- Added independent root and named `.SYSTEMXP` panels, with dedicated blank
  creation seeds that never copy adopted root brand, research, memory, or payload.
- Added `DATA/` with TEMP, LARGE, IMPORTS, RESEARCH, ASSETS, EXPORTS, CACHE and
  ARCHIVE guides. Only exact scaffold files are packaged/tracked by default;
  payload is ignored recursively. `data init` preserves existing files;
  `data status` / `data audit` inspect bounded Git metadata and flag tracked
  payload or ineffective ignore rules without reading payload contents.
- Added Agent Alpha and DATA guides, menu options 19/20, role/scope validation,
  packaging declarations, regression coverage, README/wiki routing and Mermaid
  diagrams. Brand, ICO/favicon/logo/font rights, media kit, CSS tokens, source
  provenance, retention and explicit input revisions are covered in reusable
  blank specialist formats. Existing core project records remain unchanged.
- The installer rejects incomplete 1.10 bundles and populated AUTOBOT request
  seeds before installation, including internally rehashed malformed bundles.

Ignore rules are not encryption or removal from Git history. Cloud/Drive sync,
force-add, existing tracked files, project tooling and external actions still
require their own handling. Older diagrams/white paper remain identified
baselines; the current AUTOBOT manual describes this added tier. Alpha status
continues; source checks do not certify a host application's production safety.

## 1.9.0-alpha.6 — Historical application-specific package

This release bundled an application-specific integration alongside the generic
format. That package is outside the base template's scope and is excluded from
1.11.0-alpha.4 onward. Tagged historical releases remain immutable; additive
updates preserve files already present in adopted projects. Existing core
context, plan, task, memory, and project seeds were unchanged by this edition.

## 1.9.0-alpha.5 — CLI tools and explicit .SYSTEMXP routing

- Added direct installed-CLI project routing:
  `systemx projects --target OUTER -- SUBCOMMAND ...`. It uses the selected
  verified managed defaults, requires explicit scope where applicable, preserves
  output and command exit status, and defaults offline. `--online` permits only
  the configured startup notice; it does not select/download new defaults.
- Added a versioned CLI/tools guide, a `tools-guide` command, and menu option
  18. Documented management commands, operational commands, Python API,
  external provider/Git tools, and exact child execution directories.
- Restored reviewed folder-only PowerShell launcher operation. Both Bash and
  PowerShell treat any installation marker as managed state and refuse invalid
  files, directories, or dangling links without falling back to local code.
- Revised the full-system infographic with prominent CLI examples and a
  Project-A/Project-B `.SYSTEMXP` tree. The new portable graphic and companion
  use new filenames so ordinary managed updates add them without overwriting
  earlier local media. Only the latest map ships in the new template; tagged
  alpha.4 artwork and existing users' files remain available.
- Updated the README, wiki, setup examples, project guide, and library examples
  for the new outer-target CLI. Project records remain blank and independent;
  Agent 0/X/Y/Z responsibilities and gated PR authority are unchanged.

Existing managed projects need a reviewed external alpha.5 tool and an explicit
backed-up bootstrap refresh for recognized stock manager/launcher changes
before selecting these defaults. Ordinary updates remain additive; do not
replace customized bootstraps or user records. See the release report for
actual local, package, and public-tag evidence and inherited platform limits.

## 1.9.0-alpha.4 — Agent Y visual and manual refresh

- Replaced the public full-system poster with the current Agent 0/X/Y/Z
  workflow, including separate app/IDE subagents and per-task external CLI
  work, event records, fixed reviews, and Agent 0 acceptance.
- Added one latest 4K full-system JPEG and its accessible guide to the portable
  media library. The public web PNG is also 3840 × 2160; metadata records the
  native 1672 × 941 generation, resize method, and exact-byte hashes. Removed
  the duplicate web 4K file. Earlier artwork remains in tagged history.
- Refreshed the README, technical diagrams, current wiki guidance, and workflow
  guides for optional draft PR creation, separate ready/close actions, and
  merged-and-accepted archival cleanup. Agent Y has no merge command.
- Corrected configured-provider guidance to describe preparation-time
  executable path/SHA-256/file-identity binding and launch-time checks. Reviewed
  run arguments and interpreter/dependency trust remain separate.
- Updated exact-version setup examples. The four earlier workflow cards and
  white-paper edition 1.2 retain their examined baseline and original bytes;
  current four-role material is clearly identified alongside them.

This release updates documentation and media plus their distribution inventory;
it does not change Agent Y execution or PR semantics. Updates stay additive and
preserve existing user files and older local media. Prior alpha.3 test/security
evidence remains tied to that reviewed source; see this release's review report
for its actual publication checks and inherited limits.

## 1.9.0-alpha.3 — Distribution and delegation hardening

- Distribution manifest schema 2 hashes binary and unknown files byte for byte
  while retaining LF/CRLF equivalence for reviewed UTF-8 text. New 1.9.0-alpha.3
  bundles cannot downgrade to the older schema. The installer also refuses a
  1.9 release missing Agent Y's core files, even if its manifest was recomputed.
  Historical schema-1 releases remain readable; published alpha.2 assets are
  immutable and were not changed.
- Agent X rejects a completed or cancelled due item with a closure time far in
  the future. A future planned due time remains valid.
- Agent Y cleanup detects ignored material as well as tracked and untracked
  files before removing its worktree. PR readiness refuses a base branch that
  moved since the handoff was prepared. Git-backed local sidecars and cleanup
  archives must be effectively ignored and untracked before Agent Y writes them.
- Agent Y binds a selected CLI executable's canonical path, SHA-256, and file
  identity at preparation, then checks it before launch. Older unrun handoffs
  without that binding cannot start a provider; `agent-y abandon` retires a
  genuinely unrun handoff so Agent 0 can prepare a reviewed replacement.
  Already-run older jobs remain readable for their gated PR lifecycle.
- The trusted external manager refuses `run` against an unmanaged target rather
  than executing that target's local Python. An untrusted target's own managed
  state is still not an independent authenticity anchor.
- Clarified the private original-template provenance, added Windows setup
  examples, and published a separate erratum for the frozen white-paper edition
  1.2 release-report link. The original PDF and media bytes were preserved.

This is an alpha hardening release, not production certification. Agent Y's
provider runs with the host account's effective access; its path and PR rules
do not isolate credentials or external writes. An optional remote archive pin
must come from an independently trusted source. See [security](docs/SECURITY.md),
[release policy](docs/RELEASE-POLICY.md), and the public release report for the
verified local and remote boundaries.

## 1.9.0-alpha.2 — Optional Agent Y CLI and PR lane

The earlier `v1.9.0-alpha.1` tag was withdrawn before a release was published:
its source archive failed the distribution fingerprint check for a test file.
Do not install that tag. This corrected release regenerates the manifest from
the final source and verifies the exact public tag archive through a pinned
remote install before publication.

- Added Agent Y (`agent.y`) as an opt-in, per-task CLI handoff under Agent 0.
  The public template still seeds only Agent 0; role activation creates blank
  Agent Y records without starting a worker or changing an adopted project.
- Added preview-first task packets with an explicit project task, selected
  installed CLI provider, repository/base, allowed paths, and PR policy.
  Agent Y runs separately from app/IDE subagents, so it must receive context
  explicitly and return recorded source revision and evidence.
- Added a task-owned Git worktree and branch path for CLI work. Successful,
  authorized runs can push and open a **draft** GitHub PR when the task opted in.
  Agent 0 acceptance, Agent Z review, Agent X events, PR readiness, cancellation,
  merge, and branch cleanup remain separate facts and transitions. No model
  output or score grants merge authority; GitHub Actions remains disabled.
- Extended role validation, tests, public instructions, and the wiki for the
  four-role coordination loop. The historical white-paper edition 1.2 and 4K
  images remain frozen at their earlier Agent 0/X/Z baseline; current Agent Y
  guidance lives in the manual.

## 1.8.9-alpha.1 — Template records and local safety

- Added blank, project-owned `GLOBAL/ACCESS-MATRIX.md` and `PLAN/MAP.md` to the
  root format and each new `.SYSTEMXP` child. The matrix records reviewed access
  intent and gaps; the map points to sources, interfaces, and boundaries. They
  do not grant permissions, scan infrastructure, or replace `WORK/TASKS.json`
  as the task authority. Existing project files remain preserved during updates.
- Management reads now require bounded regular files for distribution inputs,
  installation state, operation logs, and restore receipts. Explicit empty or
  whitespace target paths and empty `--source` values are rejected rather than
  silently selecting the current directory or bundled source.
- The opt-in, check-only startup notice waits at most five seconds for release
  metadata discovery. On timeout it warns and runs the selected local defaults;
  no archive is fetched or new release selected. A timed-out metadata request
  may finish in a daemon thread but cannot write the check record.
- White-paper and narration tools validate HTTPS links more strictly, keep
  output operations anchored to reviewed directories, and refuse writing the
  reserved published PDF path. The existing paper and 4K media are unchanged.
- Reorganized the public README around a preview-first setup and verification
  path, with the detailed manual and high-resolution visual gallery linked
  separately. The alpha and evidence limits remain explicit.
- On the upstream GitHub repository, secret scanning, secret-scanning push
  protection, and Dependabot vulnerability alerts are enabled. Automated
  Dependabot security updates remain disabled. A repository ruleset blocks
  deletion and force-pushes on `main` and `Alpha1`. GitHub Actions remains
  disabled. These repository settings do not transfer into projects created
  from this template.

## 1.8.8-alpha.1 — Check-only startup release notices

- Opt-in `--auto on-start` now reads release metadata and reports an available
  version without downloading its archive, selecting defaults, or changing
  project-owned files. Checks are cached for up to 24 hours after success;
  malformed or stale check metadata is retried safely.
- A pinned installation may enable the startup notice while keeping its pin.
  Choosing another version still requires an explicit unpin and manual update;
  an independently obtained `--archive-sha256` remains available for the exact
  remote ZIP before parsing it.
- Enabling startup checks refuses an older preserved root manager until its
  stock bootstrap has been explicitly refreshed with a reviewed external tool.
  Existing installations should switch old startup selection to manual policy
  before that migration. Tests cover the notice, cache, pin, migration guard,
  and digest-pinned update path on Python 3.9 and 3.14.

## 1.8.7-alpha.1 — Release integrity and coordination hardening

- Reject unlisted files, packages, links, and other unexpected entries in a
  retained default snapshot before its Python runner can execute. A partial
  interrupted update can still be retried without replacing or deleting local
  project files.
- Isolated direct `manager.py` imports from an adopted `.SYSTEMX` root so a
  project-owned module cannot shadow Python standard-library imports. Fresh
  adoption now refuses a manifest-listed executable default whose existing
  bytes differ from the reviewed distribution.
- Direct Python entry points restart in isolated mode before importing
  application or standard-library modules. The installed console command
  restarts before importing the manager, after Python resolves the package.
  Standalone validation and release maintenance load only named local helpers
  from source bytes, so unlisted modules or matching cached bytecode cannot
  execute before inventory checks. The optional white-paper tools also enter
  isolated mode before imports, reject unapproved PDF link schemes and linked
  figure roots, and anchor output replacements to an opened directory. Text
  output cannot follow symlinks or overwrite hardlinked sources. A frozen PDF
  edition cannot be rebuilt in place; choose a separate draft output.
- Added preview-first `bootstrap-refresh` for eight stock root bootstrap and
  launcher files: four Python helpers and four shell/PowerShell entry points. It
  accepts only recognized contents from intact retained releases, saves the
  original bytes of replacements under local history, and explicitly replaces
  those files. It may create a missing stock file absent from every intact
  retained historical release (such as v1.5.0's missing `versions.py`); a file
  previously present but now missing is a conflict. A changed-release update
  refuses an older bootstrap or launcher until this
  reviewed refresh is complete. Refreshed launchers and the selected runner use
  Python isolated mode (`-I`); customized wrappers require manual review.
- The current manager refuses installation and new selection of releases older
  than 1.8.7-alpha.1, the native isolated runner floor. It can inspect and run
  an already selected verified older snapshot through an isolated compatibility
  shim during external migration; the old code keeps its historical behavior.
  Historical reselection needs a separate reviewed backup or legacy path.
- Added an optional `--archive-sha256` pin for an exact remote tag ZIP. The
  digest is checked before archive parsing and its verification mode is recorded
  with the installation. Automatic startup discovery remains opt-in and does not
  supply an independent archive pin.
- Agent X now rejects future occurrence times for every non-`planned` event and
  validates the same rule when reading existing ledgers. Timestamp spelling is
  consistent across supported Python versions.
- Coordination writers wait briefly for a local lock. The lock records process,
  host, and creation time to support manual stale-lock inspection; it is not a
  distributed lock and is never removed automatically after a crash.
- Agent Z default policy 1.1.0 asks for independent corroboration of decisive
  claims and proof that decisive checks can fail on relevant bad inputs. Report
  comparison rejects reversed time order and evidence-stage regressions, and
  marks any per-question applicability change as a scope change rather than
  progress. Distinct reports with equal timestamps return an unverified order
  instead of a misleading improvement or regression label.
- Enabled immutable GitHub releases for subsequently published versions,
  disabled repository GitHub Actions, and removed the workflow. Maintainers run
  documented validation, tests, package, and release checks locally.
- The selected-release cache guard and new metadata are manager-owned. Ordinary
  updates still preserve existing project records and root files; the separate,
  explicit bootstrap refresh is the limited exception for eight stock files.
  Agent Z policy copies, task history, and update pins remain preserved.

## 1.8.6-alpha.1 — Curated media library

- Organized the current white paper and four 4K workflow cards into
  `MEDIA/White-Paper` and `MEDIA/Infographics`, with editing references in
  `MEDIA/Reference`. Older editions and original images remain available in
  prior release history.

## 1.8.5-alpha.1 — Illustrated paper and publication format

- Published the illustrated edition 1.2 research paper with a reusable
  publication template, source bibliography, linked figures, and updated PDF
  builder. The media edition and template release have separate version IDs.

## 1.8.4-alpha.1 - Expanded white paper and audio companion

- Added edition 1.1 as a 50-page implementation reference with 29 chapters,
  exact record contracts, the complete 100-question policy, command families,
  source inventory, coordination mechanics and recovery boundaries.
- Added an executable disposable walkthrough that verifies failed/corrected
  checks, state transitions, stable event replay, review deltas and acceptance.
- Retained edition 1.0 unchanged; added numbered PDF contents and a separate
  synthetic audio companion in the release, outside the portable file bundle.
- Updated public README/wiki discovery and package inventory. Runtime behavior
  and record schemas are unchanged.

## 1.8.3-alpha.1 — Public white paper

- Added a 17-page white paper and editable Markdown in `.SYSTEMX/MEDIA`, with
  document provenance, raw-byte checksums and a repository PDF builder.
- Described architecture, Agent 0/X/Z, scoring, project isolation, execution
  environments, additive lifecycle, efficiency hypotheses and an evaluation method.
- Included a worked web-app plan, an adoption prompt, pinned implementation
  references and external primary sources; distinguished implemented features,
  illustrative examples and future directions.
- Added public README/wiki discovery and included the paper in folder/wheel
  distributions. Runtime behavior and record schemas are unchanged.

## 1.8.2-alpha.1 — Portable use-case media library

- Added `.SYSTEMX/MEDIA` with four standalone cards for ChatGPT + Google Drive,
  Codex + GitHub/main, Dots / Codex Cloud, and Codex / Copilot CLI + local drive.
- Retained native imagegen PNGs and added separate 3840 × 2160 JPEG exports,
  accessible text guides, exact prompts, dimensions and raw-byte checksums.
- Added README/wiki galleries and explicit access, execution, acceptance and
  persistence boundaries for each workflow and Agent 0/X/Z.
- Included all media in the portable inventory and Python wheel. File sizes stay
  within existing installer limits; updates still preserve user-owned files.
- No runtime, task/review schema, scheduler or update-policy behavior change.

## 1.8.1-alpha.1 — Complete-project and shared-workspace manual

- Added a deep-research-to-completion guide with a 20-page web app matrix,
  toolchain mapping, phases/milestones/tasks/waves, and reusable super prompts.
- Added repository/portfolio/hybrid, Drive, cloud snapshot, multi-chat, bot,
  physical-machine, and VM patterns with explicit record authority and persistence.
- Updated the public README, portable entry instructions, manual navigation,
  Agent 0/X/Z feedback explanations, and current editable infographics.
- Corrected the command reference's unpinned alpha discovery description and
  documented all existing menu guide entries and transport boundaries.
- No runtime behavior, project-record schema, or adopted review-policy change.
  Existing project files and selected pins remain preserved.

## 1.8.0-alpha.1 — Agent X and Agent Z

- Added explicit standard-role activation with preserved registries and setup receipts.
- Added Agent X event/time tracking, stable retry keys, bounded event views,
  due-item bookkeeping, and clear external-scheduler boundaries.
- Added Agent Z's fixed 100-question/10-category policy, evidence-backed answer
  records, advisory scorecards, frozen policy versions, and comparable deltas.
- Reused unchanged review inputs; kept task acceptance and execution with the
  coordinator/user rather than automatic score-driven work loops.
- Hardened workspace argument selection, malformed/ambiguous JSON handling,
  root record link boundaries, and child-configuration error reporting.
- Removed repeated sibling-directory scans from child record guards and exported
  the documented `run` library entry point.
- Added regression checks and updated public guides, upgrade/rollback boundaries,
  and generic activation templates. No scheduler, cloud service, or agent runtime
  is installed; public work/event/review histories remain empty.

## 1.7.0-alpha.1 — SYSTEMX PROJECTS

- Added generic `Projects/NAME/.SYSTEMXP` child records with a blank project
  registry, per-project context/plan/tasks/focus, sources, decisions, and Agent 0 memory.
- Added preview-first creation receipts, explicit scope selection, scoped task and
  agent commands, local status snapshots, and project working-directory execution.
- Reused ledger validation and acceptance rules while keeping root and siblings
  isolated; rejected case conflicts, linked records, and nested installations.
- Added a library routing function and selected-project chat export.
- Preserved child records/code through shared version updates and reversible
  uninstall/restore; documented explicit migration of custom registries.
- Expanded README, portable guides, and wiki with generic setup and subagent examples.
  The public template still ships no adopted projects or private project history.

## 1.6.0-alpha.1 — Alpha1

- Consolidated all existing template branches into `Alpha1`, retaining `main`
  as the default public branch and preserving branch history.
- Declared alpha maturity, use-at-own-risk status, and possible daily changes
  across public entry points; immutable release IDs distinguish reviewed snapshots.
- Added strict alpha IDs, numeric prerelease ordering, stable-channel isolation,
  alpha discovery, final-release graduation, and implicit-downgrade refusal.
- Added `systemx --version`, selected release-channel reporting, Python alpha
  package metadata, and documented migration from pre-alpha managers.
- Added discoverable licensing, contribution/support/security reporting paths,
  bug-report templates, and release/compatibility guidance for public adopters.
- Kept pins/manual updates by default, additive preservation, operation receipts,
  exact casing, reversible removal, and blank reusable project records.

## 1.5.0

- Added honest token/cost/time guidance, a measurement approach, and new Technical,
  Stack, About, First-Time Setup, and Uninstall guides.
- Added preview-first `first-run` with explicit apply, empty configuration seeding,
  preservation of existing settings, and clear remaining setup steps.
- Added local install/update/policy/alias/first-run operation receipts and an
  offline audit of the selected project's installation footprint.
- Added reversible uninstall to a new external same-filesystem backup, including
  user records, file inventories, raw-byte hashes, alias handling, and an external log.
- Added verified restore with conflict refusal and failure/recovery receipts;
  package removal and manual integrations have separate logged cleanup instructions.
- Kept updates additive, new installs pinned/manual, reusable records blank,
  exact-case path guards active, and all existing host files protected.

## 1.4.0

- Standardized the public name and canonical folder spelling as `.SYSTEMX`.
- Added shared exact-case guards for installers, updates, library calls, local
  sources, remote archives, and direct project commands, including mixed-case conflicts.
- Added an opt-in relative `.systemx -> .SYSTEMX` alias through setup, CLI,
  menu, and library. Case-insensitive filesystems need no extra directory entry.
- Added path diagnostics, conflict recovery guidance, explicit LLM and chat
  naming rules, and portable alias checks across Linux, macOS, and Windows.
- Preserved all project records, version pins, earlier snapshots, root defaults,
  and the compatible nested manager cache. No case-conflict data is merged or deleted.

## 1.3.0

- Added setup profiles for project roots/VS Code, OS directories, local Google
  Drive folders, and LLM chats, using one canonical template and record format.
- Added a Python library and CLI, Bash and PowerShell installation entry points,
  exact version selection, per-project pins, and manual updates by default.
- Added immutable default snapshots and an additive updater that preserves all
  existing project files, directories, and prior releases, including upstream removals.
- Added opt-in startup updates with an offline override and manual major-version
  changes; no background OS scheduler or automatic user-record migration.
- Added a fingerprinted distribution inventory, local writer locking, state
  history, dry-run planning, and local chat packet export without uploads.

## 1.2.0

- Added a compact focus record and generated CURRENT.md, linked to existing
  task state and optional dated checkpoints. Focus changes preserve task history.
- Added advisory dependency-ready task selection and bounded worker packets
  with explicit source-revision provenance and selected-owner memory.
- Prioritized focus tasks in resume context; retained bounded loading and
  independent historical checkpoints.
- Added evidence categories, compact worker reports, live-job ownership and
  changed-condition retry guidance, and a record-preserving upgrade guide.
- Applied reusable lessons from existing SYSTEMX deployments without importing
  their project records, provider configuration, domain rules, or agent runtime.
- Added a canonical format contract and `validate --template` for blank public
  distributions, including seed fingerprints and an explicit file inventory.
- Replaced source-specific component restrictions with the public distribution
  inventory; adopted projects can add their own linked supporting documents.
- Standardized task-note terminology and instruction-precedence guidance;
  aligned the optional message schema with its documented evidence requirements.
- Enforced chronological history and consistent current fields, and replaced
  recursive dependency traversal so long task chains remain valid.

## 1.1.0

- Added an LLM start/resume entry point, global project context, master plan,
  shared project memory, and session checkpoint templates.
- Added Agent 0 coordination, a worker registry, and per-agent memory files.
- Added one canonical task ledger with generated TODO, WORKING-ON, BLOCKED,
  REVIEW, DONE, and CANCELLED pages.
- Added work/status/context commands, dependency and acceptance checks,
  transition history, and guarded local writes.
- Kept all project records empty in the reusable template. Role registration
  does not start agent processes, and context loading does not sync global memory.

## 1.0.0

- Extracted a standalone operations standard from the upstream `.SYSTEMX` folder.
- Consolidated overlapping setup and instruction packets into one standard,
  one setup guide, and reusable project templates.
- Removed the local builder, asset collections, embedded application starter,
  provider-specific provisioning, automatic Git hooks, and historical project state.
- Added explicit project command configuration, a portable launcher, local
  validation, and regression checks. No app or cloud provider is preconfigured.
- Retained the upstream MIT notice and recorded the exact source revision in
  [SOURCE.json](SOURCE.json).

This version belongs to the operations template. Downstream products own their
application versions and release histories separately.
