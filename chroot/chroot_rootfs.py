#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chroot [COMMAND...] \n")
    else:
        root = sys.argv[1]
        print("root = {}".format(root))

        try:
            os.chroot(root)
            os.chdir("/")

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
        except OSError as e:
            print("OSError: {0} with command {1}".format(e, sys.argv))