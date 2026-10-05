"""Portable SYSTEMX installation and update library. Importing performs no I/O."""

__all__ = ["install", "update", "bootstrap_refresh", "status", "set_policy", "export_chat", "alias",
           "first_run", "audit", "uninstall", "restore", "projects", "run"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))
    manager = __import__(__name__ + ".manager", fromlist=(name,))
    value = getattr(manager, name)
    globals()[name] = value
    return value
