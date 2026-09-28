# Changelog

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
