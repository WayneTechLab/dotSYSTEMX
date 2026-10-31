# Optional project-root agent entry point

For project work, read `.SYSTEMX/AGENTS.md` for the shared project guide.
Apply the current task instructions and host permissions. This pointer does
not grant access or start an agent.

The installable `.SYSTEMX` folder does not automatically create a project-root
`AGENTS.md`. If that file is absent, run `onboard bridge` in the selected outer
scope to preview the fixed pointer and its `contentSha256`. Create it only after
review with `onboard bridge --apply --expected-sha256 HASH_FROM_PREVIEW`.
Existing root files, links, and directories are preserved. If a root guide
already exists, merge a pointer manually where appropriate; keep its existing
instructions and `.SYSTEMX/AGENTS.md` as the canonical detailed guide. Bridge
preview works on Windows, while guarded apply needs POSIX anchored directory
operations in this beta.
