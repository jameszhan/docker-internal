# Dodker基础技术

### 容器发展的历史

| 年份    | 名称                | 描述  |
| ------ |:-------------------:|:----- |
| 1979   | chroot              | 容器的概念始于 1979 年的 UNIX  chroot，它是一个 UNIX 操作系统上的系统调用，用于将一个进程及其子进程的根目录改变到文件系统中的一个新位置，让这些进程只能访问到该目录。这个功能的想法是为每个进程提供独立的磁盘空间。其后在 1982年，它被加入到了 BSD 系统中。 |
| 2000   | FreeBSD Jails       | FreeBSD Jails 是最早的容器技术之一，它由 R&D Associates 公司的 Derrick T. Woolworth 在 2000 年为 FreeBSD 引入。这是一个类似 chroot 的操作系统级的系统调用，但是为文件系统、用户、网络等的隔离增加了进程沙盒功能。因此，它可以为每个 jail 指定 IP 地址、可以对软件的安装和配置进行定制，等等。  |
| 2001   | Linux VServer       | Linux VServer 是另外一种 jail 机制，它用于对计算机系统上的资源（如文件系统、CPU 处理时间、网络地址和内存等）进行安全地划分。每个所划分的分区叫做一个安全上下文（security context），在其中的虚拟系统叫做虚拟私有服务器（virtual private server，VPS）。  |
| 2004   | Solaris Containers  | Solaris Containers 支持在 x86 和 SPARC 系统，首次出现在 2004 年 2 月发布的 Solaris 10 的 build 51 beta 上，其后完整发布在 2005 年的 Solaris 10 上。 Solaris Container 是由系统资源控制和通过 zones 提供的边界分离（boundary separation）所组合而成的。zones 是一个单一操作系统实例中的完全隔离的虚拟服务器。    | 
| 2005   | OpenVZ              | OpenVZ 类似于 Solaris Containers，它通过对 Linux 内核进行补丁来提供虚拟化、隔离、资源管理和状态检查（checkpointing）。每个 OpenVZ 容器都有一套隔离的文件系统、用户及用户组、进程树、网络、设备和 IPC 对象。 |
| 2006   | Process Containers  | Process Containers 是由 Google 在 2006 年实现的，用于对一组进程进行限制、记账、隔离资源使用（CPU、内存、磁盘 I/O、网络等）。后来为了避免和 Linux 内核上下文中的“容器”一词混淆而改名为 Control Groups。它被合并到了 2.6.24 内核中。这表明 Google 很早就参与了容器技术的开发，以及它们是如何回馈到社区的。 |
| 2007   | Control Groups      | 如上面所述，Control Groups （即  cgroups）是由 Google 实现的，并于 2007 年加到了 Linux 内核中。 |
| 2008   | LXC                 | LXC 的意思是 LinuX Containers，它是第一个最完善的 Linux 容器管理器的实现方案，是通过 cgroups 和 Linux 名字空间（namespace）实现的。LXC 存在于 liblxc 库中，提供了各种编程语言的 API 实现，包括 Python3、Python2、Lua、Go、Ruby 和 Haskell。与其它容器技术不同的是， LXC 可以工作在普通的 Linux 内核上，而不需要增加补丁。现在 LXC project 是由 Canonical 公司赞助并托管的。 |
| 2011   | Warden              | Warden 是由 CloudFoundry 在 2011 年开发的，开始阶段是使用的 LXC，之后替换为他们自己的实现方案。不像 LXC，Warden 并不紧密耦合到 Linux 上，而是可以工作在任何可以提供隔离环境的操作系统上。它以后台守护进程的方式运行，为容器管理提供了 API。 |
| 2013   | LMCTFY              | lmctfy 的意思是“让我为你包含（Let Me Contain That For You）”。这是一个 Google 容器技术的开源版本，提供 Linux 应用容器。Google 启动这个项目旨在提供性能可保证的、高资源利用率的、资源共享的、可超售的、接近零消耗的容器（参考自：lmctfy 演讲稿）。现在为 Kubernetes 所用的 cAdvisor 工具就是从 lmctfy 项目的成果开始的。lmctfy 首次发布于 2013 年10月，在 2015 年 Google 决定贡献核心的 lmctfy 概念，并抽象成 libcontainer，因此，lmctfy 现在已经没有活跃的开发了。  libcontainer 项目最初由  Docker 发起，现在已经被移交给了开放容器基金会（Open Container Foundation）。 |
| 2013   | Docker              | Docker 是到现在为止最流行和使用广泛的容器管理系统。它最初是一个叫做 dotCloud 的 PaaS 服务公司的内部项目，后来该公司改名为 Docker。类似 Warden，Docker 开始阶段使用的也是 LXC ，之后采用自己开发的 libcontainer 替代了它。不像其它的容器平台，Docker 引入了一整个管理容器的生态系统，这包括高效、分层的容器镜像模型、全局和本地的容器注册库、清晰的 REST API、命令行等等。稍后的阶段， Docker 推动实现了一个叫做 Docker Swarm 的容器集群管理方案。 |
| 2014   | Rocket              | Rocket 是由 CoreOS 所启动的项目，非常类似于 Docker，但是修复了一些 Docker 中发现的问题。CoreOS 说他们的目的是提供一个比 Docker 更严格的安全性和产品需求。更重要的是，它是在一个更加开放的标准 App Container 规范上实现的。在 Rocket 之外，CoreOS 也开发了其它几个可以用于 Docker 和 Kubernetes的容器相关的产品，如：CoreOS 操作系统、etcd 和 flannel。 |
| 2016   | Windows Containers  | 微软 2015 年也在 Windows Server 上为基于 Windows 的应用添加了容器支持，它称之为 Windows Containers。它与 Windows Server 2016 一同发布。通过该实现， Docker 可以原生地在 Windows 上运行 Docker 容器，而不需要启动一个虚拟机来运行 Docker（ Windows 上早期运行 Docker 需要使用 Linux 虚拟机）。 |
