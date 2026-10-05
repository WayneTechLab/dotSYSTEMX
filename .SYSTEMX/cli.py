"""Restart the installed console command in isolated mode after package lookup."""

import sys


def main():
    if not sys.flags.isolated:
        bootstrap_os = sys.modules.get("os")
        if bootstrap_os is None or not sys.executable:
            sys.stderr.write("SYSTEMX requires Python's initialized OS module to enter isolated mode\n")
            return 2
        try:
            bootstrap_os.execv(sys.executable,
                               [sys.executable, "-I", "-B", "-m", "systemx", *sys.argv[1:]])
        except OSError as error:
            sys.stderr.write("SYSTEMX could not enter isolated mode: " + str(error) + "\n")
            return 2
        sys.stderr.write("SYSTEMX could not enter isolated mode\n")
        return 2
    from .manager import main as manager_main
    return manager_main()
