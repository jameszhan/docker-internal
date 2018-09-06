
```bash
cat hello.c | ssh deploy@10.211.55.7 'cat > ~/codes/hello.c'
```

```bash
gcc -Wall hello.c -o hello
./hello
```

```bash
cat hello_uts.c | ssh deploy@10.211.55.7 'cat > ~/codes/hello_uts.c'
```

```bash
gcc -Wall hello_uts.c -o hello_uts
sudo ./hello_uts
hostname
uname -n
```


```bash
cat hello_ipc.c | ssh deploy@10.211.55.7 'cat > ~/codes/hello_ipc.c'
```

```bash
gcc -Wall hello_ipc.c -o hello_ipc
sudo ./hello_ipc
ipcmk -Q
ipcs -q
```



```bash
cat hello_pid.c | ssh deploy@10.211.55.7 'cat > ~/codes/hello_pid.c'
```

```bash
gcc -Wall hello_pid.c -o hello_pid
sudo ./hello_pid
ps -elf
ls /proc
top
```


```bash
cat rootfs.c | ssh deploy@10.211.55.7 'cat > ~/codes/rootfs.c'
```

```bash
gcc -Wall rootfs.c -o rootfs
sudo ./rootfs
ps -elf
ls /proc
top
```


```bash
cat namespace.c | ssh deploy@10.211.55.7 'cat > ~/codes/namespace.c'
```

```bash
gcc -Wall namespace.c -o namespace
sudo ./namespace
ps -elf
ls /proc
top
```

cd ubuntu
wget http://mirrors.huaweicloud.com/repository/ubuntu-cdimage/ubuntu-core/16/stable/ubuntu-core-16-amd64.img.xz
xz -d ubuntu-core-16-amd64.img.xz
fdisk -l ubuntu-core-16-amd64.img

```bash
# wget http://mirrors.huaweicloud.com/repository/ubuntu-cdimage/ubuntu-core/vivid/daily-preinstalled/current/vivid-preinstalled-core-amd64.tar.gz
wget http://cdimage.ubuntu.com/ubuntu-core/vivid/daily-preinstalled/current/vivid-preinstalled-core-amd64.tar.gz

sudo tar -C ubuntu -zxvf vivid-preinstalled-core-amd64.tar.gz
```

