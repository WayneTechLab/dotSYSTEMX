# ChatGPT + Google Drive

[Gallery](../README.md) · [4K JPEG](../Infographics/chatgpt-google-drive-4k.jpg)

[![ChatGPT + Google Drive: six steps connecting project context, work, review and a saved handoff.](../Infographics/chatgpt-google-drive-4k.jpg)](../Infographics/chatgpt-google-drive-4k.jpg)

## Workflow

1. **Connect.** Use an authorized Drive connection or attach a current export.
2. **Select.** Open Project/.SYSTEMX/ and confirm the owner and revision.
3. **Load.** Read START-HERE.md, GLOBAL, PLAN and the relevant WORK records.
4. **Work.** Research, plan and draft within the agreed task scope.
5. **Save.** Use an available write tool and read back. Otherwise hand changes to the owner.
6. **Resume.** Start the next chat with the same folder URL and latest checkpoint.

## Agent responsibilities

- **Agent 0:** scope, tasks, handoffs and acceptance within user authority.
- **Agent X:** events, timestamps and due items; the host executes schedules.
- **Agent Z:** the fixed review policy with 10 categories and 100 questions.

These are roles implemented through the available toolchain. The public template
starts with Agent 0 only; [activate Agent X/Z](../../docs/AGENT-X.md) explicitly in
the selected scope. A review score is advisory and does not approve external actions.

Use `Project/.SYSTEMX/` as the selected source. Read `START-HERE.md`,
`GLOBAL/CONTEXT.md`, `PLAN/MASTER-PLAN.md`, `WORK/TASKS.json`, current focus and
relevant `MEMORY/PROJECT.md` and agent notes. Assign one canonical writer and
check freshness before saving. When write tools are unavailable, return proposed
file changes for the owner to save; then read back the resulting files. A folder
URL does not grant access, recursively load every file, or synchronize chats.
For child projects, explicitly select `Projects/NAME/.SYSTEMXP`.

## Copyable prompt

```text
Use the current .SYSTEMX at [Drive URL]. Confirm access and freshness, resume the next agreed task, and return a verified update or an owner handoff.
```

## Platform reference

ChatGPT can use connected plugins such as Google Drive; the available file operations depend on the connection. See [Use ChatGPT](https://learn.chatgpt.com/docs/use-chatgpt).

Platform references checked 2026-10-04. Availability and permissions depend on
the account, host and configuration. The workflow is a .SYSTEMX usage pattern,
not a built-in integration or third-party endorsement.
