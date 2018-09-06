#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chroot [COMMAND...] \n")
    else:
        root = sys.argv[1]
        print("newroot = {}".format(root))

        if os.chroot(root):
            print("chroot {} error.".format(root))
            sys.exit(1)

        if os.chdir("/"):
            print("chdir / error.")
            sys.exit(1)

        if len(sys.argv) == 2:
            argv = []
            shell = os.getenv("SHELL")
            if not shell:
                shell = "/bin/bash"
            argv.append(shell)
            argv.append("-i")
        else:
            argv = sys.argv[2:]

        os.execvp(argv[0], argv)
        print("chroot: cannot run command `{}`".format(argv))
