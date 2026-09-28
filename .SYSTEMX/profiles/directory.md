# Operating-system directory setup

Select a working directory you own. It does not need Git, an IDE, or an
application framework. The installer creates `.SYSTEMX` beneath that directory.
It refuses a drive/filesystem root; use a named working folder such as
`C:\Projects\Example`, not `C:\` or a Windows system directory.

PowerShell, after installing the library into your chosen Python environment:

```powershell
systemx install --target 'C:\Projects\Example' --profile directory
systemx run --target 'C:\Projects\Example' -- context --agent agent.0
```

From an extracted template on Windows:

```powershell
& .\.SYSTEMX\INSTALL.ps1 --target 'C:\Projects\Example' --profile directory
& 'C:\Projects\Example\.SYSTEMX\SYSTEMX.ps1' status
```

macOS/Linux, from an extracted template:

```bash
bash .SYSTEMX/INSTALL.sh --target "$HOME/Projects/Example" --profile directory
bash "$HOME/Projects/Example/.SYSTEMX/SYSTEMX.sh" status
```

Python 3.9+ is required for commands. Documentation works without it. SYSTEMX
does not install Python, elevate privileges, change execution policy, add login
items, or create OS schedulers. Select the installed interpreter explicitly if
your terminal uses a different Python environment. Read [installation](../docs/INSTALLATION.md)
for update policy and [the library guide](../docs/LIBRARY.md) for Git-based setup.
