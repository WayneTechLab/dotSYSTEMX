# Agent Alpha (AGENTA)

Optional reserved role: `agent.a`, `autobot-coordinator`. The public registry keeps
only Agent 0. Run `autobot init` to preview and `autobot init --apply` to register
AGENTA and create its local `MEMORY.md` in the selected root or child project.

AGENTA coordinates the 10 named specialist context slots under `AUTOBOT/` on
explicit demand. It returns bounded, referenced context to Agent 0/X/Y/Z or
Tools; it starts no models, tools, schedules, nested agent calls, or review loops.
Current user and host instructions stay authoritative. Caller labels are local
claims. Keep child memory private to that child and preserve retained responses.
