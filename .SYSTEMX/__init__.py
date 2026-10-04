"""Portable SYSTEMX installation and update library. Importing performs no I/O."""

from .manager import install, update, status, set_policy, export_chat, alias, first_run, audit, uninstall, restore, projects, run

__all__ = ["install", "update", "status", "set_policy", "export_chat", "alias",
           "first_run", "audit", "uninstall", "restore", "projects", "run"]
