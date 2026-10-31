"""Restart the installed console command in isolated mode after package lookup."""

import sys


def main():
    if not sys.flags.isolated:
        bootstrap_os = sys.modules.get("os")
        if bootstrap_os is None or not sys.executable:
            sys.stderr.write("SYSTEMX requires Python's initialized OS module to enter isolated mode\n")
            return 2
        try:
            argv = [sys.executable, "-I", "-B", "-m", "systemx", *sys.argv[1:]]
            if bootstrap_os.name == "nt":
                # The CRT execv path loses argument boundaries around spaces.
                # Load subprocess from the interpreter's stdlib before restart.
                base = bootstrap_os.path.normcase(bootstrap_os.path.realpath(sys.base_prefix))
                stdlib = []
                for entry in sys.path:
                    if not entry:
                        continue
                    try:
                        real = bootstrap_os.path.normcase(bootstrap_os.path.realpath(entry))
                        if (bootstrap_os.path.commonpath((base, real)) == base
                                and "site-packages" not in real.lower().split(bootstrap_os.sep)):
                            stdlib.append(entry)
                    except (OSError, ValueError):
                        pass
                sys.path[:] = stdlib
                import subprocess as bootstrap_subprocess
                return bootstrap_subprocess.call(argv)
            bootstrap_os.execv(sys.executable, argv)
        except OSError as error:
            sys.stderr.write("SYSTEMX could not enter isolated mode: " + str(error) + "\n")
            return 2
        sys.stderr.write("SYSTEMX could not enter isolated mode\n")
        return 2
    from .manager import main as manager_main
    return manager_main()
