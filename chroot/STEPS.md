
`docker create` 命令，可以创建一个新的容器但不启动它

```bash
docker run -it busybox uname -a

# 导出到 busybox.tar 
docker export $(docker create busybox) -o busybox.tar 

# 导出到 rootfs 目录
mkdir -p rootfs && (docker export $(docker create busybox) | tar -C rootfs -xvf -)
```

```bash
mkdir -p busybox && (sudo docker export $(sudo docker create busybox) | tar -C busybox -xvf -)
ls -la busybox

sudo chroot busybox bin/ls -la
sudo chroot busybox /bin/ps aux

sudo chroot busybox /bin/sh
sudo chroot busybox /bin/pwd


mkdir -p stretch && (sudo docker export $(sudo docker create debian:stretch-slim) | tar -C stretch -xvf -)
ls stretch
sudo chroot stretch /bin/ls -la
sudo chroot stretch cat /etc/issue

sudo chroot stretch /bin/bash
```


```bash
rm -fr rootfs && mkdir rootfs
cp ~/busybox/bin/{sh,mkdir,ls,echo,cat,which,whoami} rootfs/
ls rootfs

sudo chroot rootfs ./sh
```

```bash
export PATH=.:$PATH
mkdir -p /proc
mkdir -p /tmp

echo 'Hello World' > /tmp/hello.txt
```

```bash
ldd ~/stretch/bin/bash
cp ~/stretch/bin/bash ~/rootfs/
mkdir ~/rootfs/lib64
mkdir ~/rootfs/lib

cp ~/stretch/lib/x86_64-linux-gnu/ld-2.24.so ~/rootfs/lib64/ld-linux-x86-64.so.2
cp ~/stretch/lib/x86_64-linux-gnu/libtinfo.so.5.9 ~/rootfs/lib/libtinfo.so.5
cp ~/stretch/lib/x86_64-linux-gnu/libdl-2.24.so ~/rootfs/lib/libdl.so.2
cp ~/stretch/lib/x86_64-linux-gnu/libc.so.6 ~/rootfs/lib/libc.so.6
```