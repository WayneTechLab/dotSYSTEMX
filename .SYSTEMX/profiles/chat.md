# LLM chat setup

Use the exact directory name **`.SYSTEMX`**. Do not create or upload a separate
`.systemx` tree. OS aliases are local conveniences and are not part of this
cloud/chat format; see the [case contract](../docs/EXACT-CASE.md).

Use SYSTEMX as project reference material within the active chat's instruction
hierarchy. A setup URL does not give an LLM filesystem or cloud access.

With local files, prepare a packet from the same template and project records:

```bash
systemx install --target "/path/to/project" --profile chat
systemx export-chat --target "/path/to/project" --output "/path/to/new-session.md"
```

Review the packet for private content before attaching it to a chat. The export
includes the selected release's guidance and bounded current project context;
it does not upload anything and refuses to overwrite an existing export.
Truncation notices tell the reader which original files still need inspection.

If the chat can read a setup URL but cannot write files, use this protocol:

1. Identify the selected template release and active project. Load Global
   context, Master Plan, current tasks, and the selected agent's memory from
   attachments or authorized tools. Request missing records instead of inventing them.
2. Maintain the same canonical paths and task IDs. Propose explicit record
   changes or downloadable replacement documents for the owner to retain.
3. Mark file updates as applied only after a writable tool changes them and
   reads them back. A chat answer alone is not durable project memory.
4. Export a checkpoint at handoff and attach the current records to the next
   session. Selecting a newer standard must preserve those project records.

Without a terminal or writable connector, updates and version selection are
manual. The latest public guide is a discovery URL; choose a release-tag URL
for a reproducible standard. Profiles do not select an LLM vendor, model, agent
count, or orchestration runtime. A future MCP adapter can use the same library
and format; this release does not install an MCP server.
