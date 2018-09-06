
```bash
sudo sh -c su root

mkdir -p /sys/fs/cgroup/cpu/cgroup_demo
echo 10000 | tee /sys/fs/cgroup/cpu/cgroup_demo/cpu.cfs_quota_us

cat /sys/fs/cgroup/cpu/cgroup_demo/cpu.cfs_quota_us
cat /sys/fs/cgroup/cpu/cgroup_demo/cpu.cfs_period_us

exit
```

```bash
cd codes
gcc -Wall cgroup_demo.c -o cgroup_demo
echo "hello cgroup" && ./cgroup_demo > /dev/null &

top -u james -bcn 1
```

```bash
echo 9629 | sudo tee /sys/fs/cgroup/cpu/mygroup/tasks
top -u james -bcn 1
```

Install GoLang On CentOS 7

```bash
cd /tmp
curl -LO https://storage.googleapis.com/golang/go1.11.linux-amd64.tar.gz

# Compare digest with https://storage.googleapis.com/golang/go1.11.linux-amd64.tar.gz.sha256
sha256sum go1.11*.tar.gz

sudo tar -C /usr/local -xvzf go1.11.linux-amd64.tar.gz
ls /usr/local/go

export PATH=$PATH:/usr/local/go/bin
```