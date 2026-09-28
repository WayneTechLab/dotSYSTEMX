# Google Drive setup

Use the same regular Markdown and JSON files in a project folder made available
locally by Drive for desktop. Choose the real mounted/mirrored path on your
computer; a `drive.google.com` folder URL is not a filesystem path.

```bash
systemx install --target "/your/local/Drive/Project" --profile drive
systemx run --target "/your/local/Drive/Project" --offline -- status
```

On Windows, quote the full path, for example `G:\My Drive\Project`; the drive
letter and folder location are user-selected, not assumed by the installer.
Make the project available offline before running commands. Google documents
mirroring and streaming in [Drive for desktop help](https://support.google.com/drive/answer/13401938).

The profile does not create a Google account, obtain OAuth access, call Drive
APIs, change sharing, or convert files into native Google Docs. Drive performs
the synchronization. Keep one writing computer/session active for a shared
project and wait for synchronization before switching: the local lock is not a
distributed lock across computers. Resolve Drive conflict copies explicitly.

For browser-only Drive, upload the reviewed folder's ordinary files while
preserving their hierarchy, or upload a [chat export](chat.md). Updates there
require an explicit download/review/upload cycle or a separately authorized
connector. There is no background cloud updater. Keep private records in an
appropriately shared folder and never publish a populated project as a template.
