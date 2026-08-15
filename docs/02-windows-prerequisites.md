# 02 - Windows prerequisites

Use Windows 11 or Windows 10 with a current Docker Desktop installation and the WSL2 backend.

Recommended laptop capacity:

- 4 CPU cores minimum; 8 preferred.
- 12 GB RAM minimum; 16 GB preferred.
- 20 GB free disk space.
- DBeaver Community or Enterprise.
- PowerShell 7 is preferred, though Windows PowerShell works for the supplied scripts.

## Validate Docker

```powershell
docker version
docker compose version
docker run --rm hello-world
```

If `docker version` shows a client but no server, start Docker Desktop. If containers cannot allocate enough memory, increase Docker Desktop resources or close other heavy applications.

## Recommended directory

Use a short path without OneDrive synchronization:

```text
C:\data-engineering\catering-analytics
```

Avoid extracting into a deeply nested cloud-synced folder because bind-mounted files and line endings are easier to troubleshoot from a simple local path.
