# Docker 基础之 chroot

## 背景

### 什么是chroot

`chroot` 是一个 `UNIX` 操作系统上的系统调用，用于将一个进程及其子进程的根目录改变到文件系统中的一个新位置，让这些进程只能访问到该目录。这个功能的想法是为每个进程提供独立的磁盘空间


### chroot的优势

在经过 chroot 之后，系统读取到的目录和文件将不在是旧系统根下的而是新根下(即被指定的新的位置)的目录结构和文件，因此它带来的好处大致有以下3个：
* 增加了系统的安全性，限制了用户的权力；
    在经过 chroot 之后，在新根下将访问不到旧系统的根目录结构和文件，这样就增强了系统的安全性。这个一般是在登录 (login) 前使用 chroot，以此达到用户不能访问一些特定的文件。
* 建立一个与原系统隔离的系统目录结构，方便用户的开发；
    使用 chroot 后，系统读取的是新根下的目录和文件，这是一个与原系统根下文件不相关的目录结构。在这个新的环境中，可以用来测试软件的静态编译以及一些与系统不相关的独立开发。
* 切换系统的根目录位置，引导 Linux 系统启动以及急救系统等。
    chroot 的作用就是切换系统的根位置，而这个作用最为明显的是在系统初始引导磁盘的处理过程中使用，从初始 RAM 磁盘 (initrd) 切换系统的根位置并执行真正的 init。另外，当系统出现一些问题时，我们也可以使用 chroot 来切换到一个临时的系统。
	

## 如何使用 chroot

### 准备 Linux 镜像
```
mkdir -p busybox && (sudo docker export $(sudo docker create busybox) | tar -C busybox -xvf -)

mkdir -p stretch && (sudo docker export $(sudo docker create debian:stretch-slim) | tar -C stretch -xvf -)
```

`Busybox` 被称为是嵌入式 `Linux` 中的瑞士军刀。`Busybox` 包含了许多有用的命令，如 `cat`、`find` 等，但是它的体积却非常的小，`bin` 目录下所有命令都是静态编译，不依赖动态共享库文件。

`debian:stretch-slim` 即为 `Debian 9` 的稳定发行版，`slim` 表示精简版。

### 执行 chroot

`chroot` 到 `busybox` 目录，并执行命令 `/bin/busybox --list`。

```bash
sudo chroot busybox /bin/busybox --list
```
```txt
[
[[
acpid
add-shell
addgroup
adduser
adjtimex
ar
...
```

`chroot` 到 `busybox` 目录，并执行命令 `/bin/sh`。

```bash
sudo chroot busybox /bin/sh
```
在 `sh` 中执行 `busybox` 中的命令

```bash
ls
# bin dev etc home proc root sys tmp usr var
whoami
# root

mount -t proc proc /proc
ps aux
# PID   USER     TIME  COMMAND
#    1 root      0:50 /usr/lib/systemd/systemd --system --deserialize 20
#    2 root      0:00 [kthreadd]
# ...

ifconfig
# ifconfig: /proc/net/dev: No such file or directory
# docker0   Link encap:Ethernet  HWaddr 02:42:88:28:3C:C5
#          inet addr:172.17.0.1  Bcast:172.17.255.255  Mask:255.255.0.0
#          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
#
# eth0      Link encap:Ethernet  HWaddr 00:16:3E:0C:86:F9
#          inet addr:172.18.113.32  Bcast:172.18.127.255  Mask:255.255.240.0
#          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
#
...
```
对比宿主机 `IP` 配置会发现网络是没有隔离的。

`chroot` 到 `stretch` 目录，默认执行 `/bin/bash`。

```bash
sudo chroot stretch
```

在 `bash` 中执行 `stretch` 中的命令

```bash
cat /etc/issue
# Debian GNU/Linux 9 \n \l
whoami
# root
```

### chroot 如何执行可执行文件

前面演示了 `chroot` 切换到 `busybox` 及 `stretch` 目录执行命令，给人的感觉好像在使用一个全新的系统。事实上，执行命令的还是宿主操作系统，它只不过把根目录限定在了指定目录，执行文件的相关依赖也必须在此根目录下。

`chroot` 执行命令，并不需要目标目录有一个完整的 `linux` 内核，只要是和宿主操作系统同体系符合 `ELF` 格式的可执行文件，就可以直接执行。

#### 示例1

```bash
rm -fr rootfs && mkdir rootfs
cp ~/busybox/bin/ls ~/rootfs/
sudo chroot rootfs ./ls
# ls
```
#### 示例2

```bash
rm -fr rootfs && mkdir rootfs
cp ~/busybox/bin/{sh,ls,echo,cat,mkdir} ~/rootfs/
sudo chroot rootfs ./sh
```

```bash
./mkdir tmp
./echo 'Hello World' > /tmp/hello.txt
./cat /tmp/hello.txt
# Hello World
./ls /
# cat    echo   ls     mkdir  sh     tmp
./ls /tmp
hello.txt
```

#### 示例3

```bash
cp ~/stretch/bin/bash ~/rootfs/
sudo chroot rootfs ./bash
# chroot: failed to run command ‘./bash’: No such file or directory
```
这里报错，是因为，在 `stretch` 的 `bash` 不是静态编译的，它依赖于其它的动态库，只有把依赖文件也准备好，`bash` 命令才可以正确执行。

```bash
# 查看 bash 依赖的动态库
ldd ~/stretch/bin/bash

mkdir ~/rootfs/lib ~/rootfs/lib64
cp ~/stretch/lib/x86_64-linux-gnu/ld-2.24.so ~/rootfs/lib64/ld-linux-x86-64.so.2
cp ~/stretch/lib/x86_64-linux-gnu/libtinfo.so.5.9 ~/rootfs/lib/libtinfo.so.5
cp ~/stretch/lib/x86_64-linux-gnu/libdl-2.24.so ~/rootfs/lib/libdl.so.2
cp ~/stretch/lib/x86_64-linux-gnu/libc.so.6 ~/rootfs/lib/libc.so.6

tree ~/rootfs
# /home/james/rootfs
# ├── bash
# ├── lib
# │   ├── libc.so.6
# │   ├── libdl.so.2
# │   └── libtinfo.so.5
# └── lib64
#     └── ld-linux-x86-64.so.2
#     
sudo chroot rootfs ./bash
```

### chroot 系统调用

上面介绍了 chroot 命令行使用，但是更常见的方式是其它程序语言通过系统调用的方式来使用。chroot 的编写涉及了2个函数，chroot() 以及 chdir()，它们都包含在 unistd.h 头文件中。

#### 示例1

本例演示了 `chroot` 到 `~/busybox` 目录中执行命令。

```bash
vim chroot_demo.py
chmod +x chroot_demo.py
```

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: chroot [COMMAND...] \n")
    else:
        os.chroot("/home/james/busybox")
        os.chdir("/")

        os.system("umount ./proc")
        os.system("mount -t proc ./proc /proc")

        os.execvp(sys.argv[1], sys.argv[1:])
```

```bash
sudo ./chroot_demo.py ls
# bin dev etc home proc root sys tmp usr var
sudo ./chroot_demo.py whoami
# root

sudo ./chroot_demo.py ps
# PID   USER     TIME  COMMAND
#    1 root      0:49 /usr/lib/systemd/systemd --system --deserialize 20
#    2 root      0:00 [kthreadd]
#    3 root      0:02 [ksoftirqd/0]
# ...

sudo ./chroot_demo.py ifconfig
# docker0   Link encap:Ethernet  HWaddr 02:42:88:28:3C:C5
#           inet addr:172.17.0.1  Bcast:172.17.255.255  Mask:255.255.0.0
#           UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
#           RX packets:3702045 errors:0 dropped:0 overruns:0 frame:0
#           TX packets:4221866 errors:0 dropped:0 overruns:0 carrier:0
#           collisions:0 txqueuelen:0
#           RX bytes:150990614 (143.9 MiB)  TX bytes:36552003396 (34.0 GiB)
# 
# eth0      Link encap:Ethernet  HWaddr 00:16:3E:0C:86:F9
#           inet addr:172.18.113.32  Bcast:172.18.127.255  Mask:255.255.240.0
#           UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
#           RX packets:105629916 errors:0 dropped:0 overruns:0 frame:0
#           TX packets:43745130 errors:0 dropped:0 overruns:0 carrier:0
#           collisions:0 txqueuelen:1000
#           RX bytes:102811026834 (95.7 GiB)  TX bytes:70775210676 (65.9 GiB)
# 
...
```

#### 示例2

本例展示如何用系统调用的方式来实现一个类 `chroot` 命令。

```bash
vim chroot_rootfs.py
chmod +x chroot_rootfs.py
```

```python
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
```

```bash
./chroot_rootfs.py
Usage: chroot NEWROOT [COMMAND...]

sudo ./chroot_rootfs.py ~/busybox /bin/ls
# bin dev etc home proc root sys tmp usr var
```