# About .SYSTEMX

> **Alpha: use at your own risk; may change daily.** See the [release policy](RELEASE-POLICY.md).

`.SYSTEMX` is an open, reusable project operating format for people and AI
assistants. Its purpose is continuity: keep project context, accepted outcomes,
current work, evidence, and learned facts available across sessions and tools.
The name is the exact folder name, including the leading dot and uppercase letters.

## Why it exists

Long conversations can bury decisions, split task status across messages, and
cause new sessions to repeat work. `.SYSTEMX` gives those facts explicit homes:
Global context for shared project knowledge, a Master Plan for outcomes, a task
ledger for state and evidence, and scoped memory for the project and its agents.
Focused handoffs can reduce repeated input and rework; see the
[token, cost, and time guide](EFFICIENCY.md) for the mechanisms and limitations.

## Principles

- Keep one canonical record for each responsibility and generate status views.
- Preserve user files, existing decisions, evidence, and task history during updates.
- Start new projects from blank records rather than inheriting someone else's backlog.
- Let Agent 0 coordinate review while keeping worker context scoped to assignments.
- Make version choice explicit, with manual updates and pins by default.
- Make installation changes inspectable and removal reversible, with local logs.
- Work across editors, operating systems, cloud folders, and LLMs without choosing
  a product stack or granting external-service authority.

The format is a project-maintained convention, not an externally certified
industry standard. Agent role files do not launch processes, authorize delegation,
create automatic cross-project memory, or guarantee delivery quality. The project
must supply requirements, actual checks, and acceptance evidence.

## Ownership, license, and provenance

Maintained by [Wayne Tech Lab LLC](https://github.com/WayneTechLab), `.SYSTEMX` is
published under the [MIT License](../LICENSE). The standalone format was curated
from the operating folder in
[SFWA-WTL-TEMPLATE](https://github.com/WayneTechLab/SFWA-WTL-TEMPLATE).
[SOURCE.json](../SOURCE.json) records the original scope and revision. The public
template excludes the original application's content and historical project state.
Preserve the license and attribution when redistributing it.

The repository is [WayneTechLab/dotSYSTEMX](https://github.com/WayneTechLab/dotSYSTEMX).
The Python distribution is `dotsystemx`; its import and command are `systemx`.
Those identifiers do not change the canonical `.SYSTEMX` folder name.

Begin with [first-time setup](FIRST-RUN.md). Read the [Technical Guide](TECHNICAL-GUIDE.md)
for architecture and the [Stack Guide](STACK-GUIDE.md) for integration boundaries.
Release IDs and history live in the
[Versions and changelog wiki](https://github.com/WayneTechLab/dotSYSTEMX/wiki/Versions-and-Changelog).
