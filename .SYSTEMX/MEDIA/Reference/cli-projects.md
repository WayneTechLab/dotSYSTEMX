# Full-system map: Agent 0 / X / Y / Z

[Open the 4K image](../Infographics/systemx-cli-projects-4k.jpg).

This current map connects project context, canonical work, all four standard
roles, actual tools, named child projects, and installation/recovery. It replaces
the older three-role poster in the public README/wiki. The four historical
workflow cards and white-paper edition 1.2 retain their examined baseline.

1. Read the exact `.SYSTEMX` scope: context, access decisions, Master Plan,
   MAP, focus, and reviewed memory.
2. Agent 0 assigns bounded tasks to app/IDE workers or a separate Agent Y
   external CLI lane. Only Agent 0/user accepts task outcomes.
3. `WORK/TASKS.json` owns status; TODO, working, blocked, review, done,
   cancelled, and current-focus pages are generated views.
4. Agent X records actual actors, occurrence/recording times, revisions,
   evidence, and due items; the host executes schedules.
5. Agent Y selects a provider per task, receives an explicit packet, and runs
   in a task-owned Git worktree. A task may opt into a draft PR. Accepted
   completion permits separate ready; cancellation permits close while
   preserving unmerged work; verified merge plus acceptance permits archived
   cleanup. Agent Y never merges.
6. Agent Z reviews matching inputs against 100 questions in ten categories.
   Its evidence/unknowns/delta scorecard advises acceptance; reuse unchanged
   reviews and create a bounded task for an actual gap.
7. The external `systemx` CLI manages the outer installation. Direct
   `systemx projects --target OUTER -- ...` routes selected defaults to explicit
   child operations and defaults offline. Reviewed local `SYSTEMX.sh` and
   `SYSTEMX.ps1` launchers expose `tools-guide`, `doctor`, `validate`, task/role
   commands, and configured checks/builds. Python `run()`, `projects()`, and
   `export_chat()` are optional library entry points. Git/gh and authorized
   CLI providers supply their real tools; role records grant no permissions.
8. `.SYSTEMX/Projects/Project-A/.SYSTEMXP/` and
   `.SYSTEMX/Projects/Project-B/.SYSTEMXP/` are independent siblings under one
   outer tool installation. Select `--project Project-A` explicitly. Each child
   retains separate context, plan, tasks, memory, roles, sources, decisions,
   sync status, and optional events/reviews. The managed `.SYSTEMX/.systemx/`
   cache is a different location; never nest a second `.SYSTEMX`.
9. Preview setup, pin reviewed defaults, use additive manual updates, and keep
   uninstall/restore receipts and backups. Startup notices are opt-in and
   do not select code.

Agent Y's worktree and PR controls are workflow gates, not OS isolation.
Protect host credentials and private records with appropriate host controls.
A cloud/Drive URL alone does not authorize access or synchronize writers.

The [full accessible walkthrough](https://github.com/WayneTechLab/dotSYSTEMX/blob/main/docs/assets/systemx-full-system.md)
explains every panel. See the versioned local [CLI and tools guide](../../docs/CLI-TOOLS.md),
[project routing guide](../../docs/PROJECTS.md), [Agent Y guide](../../docs/AGENT-Y.md),
[Agent X guide](../../docs/AGENT-X.md), [Agent Z guide](../../docs/AGENT-Z.md),
and [installation guide](../../docs/INSTALLATION.md) for executable contracts.
The [Visual Guide](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Visual-Guide)
provides the changeable public manual.

Generated with the built-in imagegen tool. The requested and exported canvas is
3840 × 2160; [asset metadata](ASSETS.json) records actual generation dimensions,
export method, and exact-byte SHA-256 hashes. Upscaling, if recorded there,
adds canvas pixels rather than native detail. **Alpha — use at your own risk.**
