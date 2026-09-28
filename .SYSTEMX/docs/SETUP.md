# Setup

## Adopt the folder

1. Identify the destination repository and inspect existing files, including
   hidden files and local changes.
2. Copy the complete `.SYSTEMX` folder. If one already exists, compare versions
   and merge deliberately. Do not replace project config, secrets, or evidence.
   Use a clean template checkout or reviewed release archive; a working project's
   folder can contain ignored private data that ordinary filesystem copying retains.
3. Read the [standard](../STANDARD.md) and inspect the scripts before execution.
4. Run `bash .SYSTEMX/SYSTEMX.sh validate` and `bash .SYSTEMX/SYSTEMX.sh doctor`.
   Python 3.9+ is required only for the command tools. Git is optional for
   documentation use; the doctor uses it if available.

Before initializing a pristine distribution, `validate --template` additionally
checks that its project seeds are blank and that only distribution files are
present. Use ordinary `validate` after adoption. The [format contract](../FORMAT.md)
documents these separate modes.

## Record project choices

Run `bash .SYSTEMX/SYSTEMX.sh init` to create `.SYSTEMX/project.json`. This creates
only that file and never overwrites existing configuration.

Create `.SYSTEMX/project/` as needed. Copy the [project brief](../templates/PROJECT-BRIEF.md)
and [architecture](../templates/ARCHITECTURE.md) there, and replace prompts with
project facts. Keep reusable templates blank for the next project. Describe
unknowns as unknowns rather than making up requirements.

Fill [GLOBAL/CONTEXT.md](../GLOBAL/CONTEXT.md) with approved shared context and
create the accepted milestones in [PLAN/MASTER-PLAN.md](../PLAN/MASTER-PLAN.md).
Use [WORK/README.md](../WORK/README.md) to create concrete tasks. The coordinator
is `agent.0`; register other workers only as needed. Begin and end work with the
[memory protocol](../MEMORY/README.md), keeping records specific to this project.

Select the runtime, package manager, build approach, environments, integration
owners, deployment target, and applicable quality checks. Do not install every
tool mentioned in the documentation. Pin the selected runtime and dependency
versions through the host project's normal files and lockfiles.

## Wire commands

Edit `.SYSTEMX/project.json` using the configuration contract in the
[README](../README.md). Point each check at a real project command. Order fast
checks before expensive ones. Add development, build, and deployment commands
only when the host project supports those operations.

Use checked-in scripts for complex workflows. Do not put credentials in command
arrays. A docs-only project can use document validation and generation; a library
may leave deployment unconfigured until its publish process is defined.

```bash
bash .SYSTEMX/SYSTEMX.sh doctor
bash .SYSTEMX/SYSTEMX.sh check --dry-run
bash .SYSTEMX/SYSTEMX.sh check
```

Read the displayed plan before running unfamiliar commands. `--dry-run` runs
no project commands, including quality checks. Missing executable names are
reported by `doctor`; remote authentication and service health are not tested.

## Establish boundaries

- Add host-project ignore rules for secrets, dependencies, caches, and artifacts.
  `.SYSTEMX/.gitignore` protects only paths inside `.SYSTEMX`.
- Use `.SYSTEMX/local/`, `logs/`, or `state/` for private local runtime artifacts.
  Git ignore rules are convenience, not secret protection or access control.
- Keep sanitized project configuration and project records in version control.
- Configure public output allowlists so `.SYSTEMX` and private material cannot
  be published accidentally.
- Put any AI discovery entry point required by your tool at the host repository
  root and link it to [START-HERE.md](../START-HERE.md). Merge the supplied
  [entry-point template](../templates/AGENT-ENTRYPOINT.md) with existing instructions.
  A hidden folder is not automatically discovered by every AI tool.

## Ready for project work

Project setup is ready when context is recorded, selected tools are available,
configured checks pass, and local run/build instructions are reproducible.
Production acceptance additionally requires the applicable release steps in
[OPERATIONS.md](OPERATIONS.md). A template validation pass proves neither state.
