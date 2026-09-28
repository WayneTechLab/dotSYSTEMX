# Stack Guide

> **Alpha: use at your own risk; may change daily.** See the [release policy](RELEASE-POLICY.md).

`.SYSTEMX` is stack-neutral. It organizes how work is understood and verified;
your project chooses its languages, frameworks, data stores, and deployment tools.

## What is required

| Usage | Requirement | Installed by `.SYSTEMX`? |
| --- | --- | --- |
| Read/write project documents | Markdown/JSON-capable editor or file tools | No editor is installed |
| Optional CLI and library | Python 3.9+ | Runtime must already be available |
| Git-based package installation | Git and pip in the chosen Python environment | No Git installation |
| Wheel or reviewed folder usage | Python; no Git required for the folder tools | Only requested package/folder files |
| Bash launchers | Bash plus Python | No shell configuration changes |
| Windows launchers | PowerShell plus Python launcher/Python | No execution-policy changes |
| VS Code | Optional editor | No extension or global settings changes |
| Google Drive profile | Locally available regular files, or explicit browser uploads | No Drive client, OAuth, or account setup |
| LLM chat | Explicit attachments or authorized file tools | No model subscription or API calls |

There are no third-party Python runtime dependencies, database requirements,
Node.js requirements, background daemons, system services, login jobs, or automatic
Git hooks in the standard installation. Building a wheel uses setuptools as a
build dependency in the build environment. The GitHub release wheel avoids a
local source build.

## Fit it to your project

| Project type | Typical integration |
| --- | --- |
| Python library/application | Point checks at the project's chosen test and lint commands |
| JavaScript/TypeScript | Point checks/build at existing npm, pnpm, or other scripts |
| .NET, Java, Go, Rust, or native apps | Use the existing compiler/test CLI as argument arrays |
| Documentation/research | Use document validation and evidence review; leave deployment empty |
| Desktop workspace or non-Git directory | Use explicit project paths and local records |
| Cloud/Drive workspace | Coordinate one writer and verify synchronization before switching |

For example, if a JavaScript project already defines a working `test` script,
a check can use `{"name": "tests", "command": ["npm", "test"]}`. That does not
install npm, create a test suite, or prove the command passes. Keep missing
commands empty until the project supplies them. See the
[configuration contract](../README.md#configuration-contract).

Keep application dependencies, credentials, infrastructure, and build output in
the host project's chosen layout. Use the appropriate package manager to install
and remove those dependencies. A `.SYSTEMX` folder uninstall must not remove a
shared SDK or unrelated project environment. If a project-specific setup adds
external resources, record the exact owner, version, install location, original
state, verification, uninstall command, and log location in that project.

## Portable adoption

Use `.SYSTEMX` with exact casing everywhere, UTF-8 documents, quoted containing
project paths, and argument arrays. Treat local lowercase aliases as optional;
do not rely on Git, Drive, or archives preserving them. Prefer an isolated Python
environment for the library so its package and logs are easy to identify and
remove. Start with [first-time setup](FIRST-RUN.md), then keep the
[uninstall guide](UNINSTALL.md) with the project handoff.
