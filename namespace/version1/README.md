```bash
sudo apt-get -y update
sudo apt-get -y install python-software-properties
sudo apt-get -y upgrade
sudo apt-get -y dist-upgrade
sudo apt-get -y install autoconf build-essential
```

```bash
cat ns.c | ssh deploy@10.211.55.7 'cat > ~/codes/ns.c'

cat ns2.c | ssh deploy@10.211.55.7 'cat > ~/codes/ns2.c'

cat ipc.c | ssh deploy@10.211.55.7 'cat > ~/codes/ipc.c'

cat pid.c | ssh deploy@10.211.55.7 'cat > ~/codes/pid.c'

cat fs.c | ssh deploy@10.211.55.7 'cat > ~/codes/fs.c'

cat net.c | ssh deploy@10.211.55.7 'cat > ~/codes/net.c'
```



```bash
gcc -Wall ns.c -o ns && ./ns

gcc -Wall ns2.c -o ns2 && sudo ./ns2

gcc -Wall ipc.c -o ipc && sudo ./ipc

gcc -Wall pid.c -o pid && sudo ./pid
echo "=> My PID: $$"
mkdir -p proc
mount -t proc proc proc
ls proc

gcc -Wall fs.c -o fs && sudo ./fs
mount -t proc proc /proc
ps aux
```

```bash
# Create a "demo" namespace
ip netns add demo
# create a "veth" pair
ip link add veth0 type veth peer name veth1
# and move one to the namespace
ip link set veth1 netns demo
# configure the interfaces (up + IP)
ip netns exec demo ip link set lo up
ip netns exec demo ip link set veth1 up
ip netns exec demo ip addr add 169.254.1.2/30 dev veth1
ip link set veth0 up
ip addr add 169.254.1.1/30 dev veth0

# make sure ip forwarding is enabled
echo 1 > /proc/sys/net/ipv4/ip_forward
# enable Internet access for the namespace, assuming you ran the previous example
iptables -t nat -A POSTROUTING -i veth0 -j  MASQUERADE
# Forward main ":80" to guest ":80"
iptables -t nat -A PREROUTING -d <your main ip>/32 -p tcp --dport 80 -j  DNAT --to-destination  169.254.1.2:80
```


```bash
gcc -Wall net.c -o net && sudo ./net
```