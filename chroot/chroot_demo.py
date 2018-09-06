#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import ctypes
# import ctypes.util
import os
import sys


# libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
# libc.mount.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p)
#
#
# def mount(source, target, fs, options=''):
#     ret = libc.mount(source, target, fs, 0, options)
#     if ret < 0:
#         errno = ctypes.get_errno()
#         raise OSError(errno, "Error mounting {} ({}) on {} with options '{}': {}".
#                       format(source, fs, target, options, os.strerror(errno)))
#
#
# def umount(directory):
#     ret = libc.umount(directory)
#     if ret < 0:
#         errno = ctypes.get_errno()
#         raise OSError(errno, "Error umounting {}".format(directory))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chroot [COMMAND...] \n")
    else:
        os.chroot("/home/james/busybox")
        os.chdir("/")

        os.system("umount ./proc")
        os.system("mount -t proc ./proc /proc")
        # umount('./proc')
        # mount("/proc", "./proc", "proc")

        os.execvp(sys.argv[1], sys.argv[1:])
