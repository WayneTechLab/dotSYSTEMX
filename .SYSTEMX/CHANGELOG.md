# Changelog

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
