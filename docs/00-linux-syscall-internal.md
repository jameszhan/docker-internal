```bash
vim hello.c
```

```c
#include <stdio.h>
int main(void) {
  printf("hello, world!\n");
  return 0;
}
```

```bash
gcc -Wall hello.c -o hello.out

strace ./hello.out
# ...
# mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f8bd8ede000
# write(1, "hello, world!\n", 14hello, world!
# )         = 14
# exit_group(0)                           = ?
# ...
```

```c
#include <unistd.h>
int main(void) {
  write(1, "hello, world!\n", 14);
  return 0;
}
```

```bash
gcc -S hello.c
cat hello.s
```

```asm
...
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$14, %edx
	movl	$.LC0, %esi
	movl	$1, %edi
	call	write
	movl	$0, %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
...
```

```c
#include <unistd.h>
#include <sys/syscall.h>
int main(void) {
  syscall(SYS_write, 1, "hello, world!\n", 14);
  return 0;
}
```

```bash
gcc -Wall hello.c -o hello.out && ./hello.out

gcc -S hello.c
cat hello.s
```

```asm
...
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$14, %ecx
	movl	$.LC0, %edx
	movl	$1, %esi
	movl	$1, %edi
	movl	$0, %eax
	call	syscall
	movl	$0, %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
...
```

# Linux 系统调用

Intel 的 x86 架构的 CPU 提供了 0 到 3 四个特权级，而在 Linux 操作系统中主要采用了 0 和 3 两个特权级，也就是我们通常所说的内核态和用户态。

从用户态向内核态切换通常有 3 种情况： A) 系统调用(主动)，用户态的进程申请操作系统的服务，通常用软中断实现；B) 产生异常，如缺页异常、除0异常；C) 外设产生中断，如键盘、磁盘等。

下面以系统调用来讲解。

## 简介
在 x86 中，通过中断来调用系统调用的效率被证明是非常低的，如果用户程序频繁使用系统调用接口，那么会显著降低执行效率。Intel 很早就注意到了这个问题，并且引进了一个更有效的 sysenter 和 sysexit 形式的系统调用接口。

快速系统调用最初在 Pentium Pro 处理器中出现，但是由于硬件上的 bug ，实际上并没有被大量 CPU 采用。这就是为什么可以看到 PentiumⅡ 甚至 Pentium Ⅲ 最后实际引入了 sysenter 。

由于硬件的问题，操作系统经历了很长时间才支持快速系统调用，Linux 最早在 2002.11 才开始支持，此时已经过去了 10 年。通过反汇编可以发现，`__kernel_vsyscall` 实际会调用 sysenter 。

## 使用系统调用

系统调用号可以从 `/usr/include/syscall.h` 中查看，在 C 中调用系统调用可以使用 `syscall()` 或者 `glibc` 封装的系统调用。

```c
#include <stdio.h>
#include <unistd.h>
#include <syscall.h>       /* for SYS_write etc. */
#include <sys/types.h>

int main(void) {
    char s[] = "Hello World\n";
    int ret;

    /* direct system call */
    ret = syscall(SYS_write, 2, s, sizeof(s)); /* man 2 syscall */
    printf("syscall(SYS_write) return %d\n", ret);

    /* or "libc" wrapped system call */
    ret = write(2, s, sizeof(s));
    printf("libc write() return %d\n", ret);

    return(0);
}
```

或者使用汇编。

```asm
# Writes "Hello, World" to the console using only system calls. Runs on 64-bit Linux only.
# gcc -c hello.s && ld hello.o && ./a.out or gcc -nostdlib hello.s && ./a.out

    .global _start
    .text
_start:
    # write(1, message, 13)
    mov     $1, %rax                # system call 1 is write
    mov     $1, %rdi                # file handle 1 is stdout
    mov     $message, %rsi          # address of string to output
    mov     $13, %rdx               # number of bytes
    syscall                         # invoke operating system to do the write

    # exit(0)
    mov     $60, %rax               # system call 60 is exit
    xor     %rdi, %rdi              # we want return code 0
    syscall                         # invoke operating system to exit
message:
    .ascii  "Hello, world\n"
    
```

对于相应的系统调用可以通过 `strace -e trace=write ./a.out` 查看，注意，如果通过如下的 `vdso` 则不会捕捉到相应的系统调用。

## 系统实现

在比较老的系统中，是通过软中断实现。在 32-bits 系统中，系统调用号通过 `eax` 传入，各个参数依次通过 `ebx`, `ecx`, `edx`, `esi`, `edi`, `ebp` 传入，然后调用 `int 0x80` ；返回值通过 `eax` 传递。所有寄存器的值都会保存。

在 64-bits 系统中，系统调用号通过 `rax` 传入，各个参数依次通过 `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9` 传入, 然后调用 `syscall`；返回值通过 `rax` 传递。系统调用时 `rcx` 和 `r11` 不会保存。

对于系统调用的执行过程，可通过解析反汇编代码查看，真正的程序入口是 `_start`，下面解析查看过程。

### 示例程序

以 `write()` 系统调用为例，通过 `gcc -o write write.c -static` 编译，注意最好静态编译，否则不方便查看。

```c
#include <unistd.h>
int main(int argc, char **argv)
{
    write(2, "Hello World!\n", 13);
    return 0;
}
```

通过如下方式查看函数调用过程，`write()` 是 `glibc` 封装的函数，具体实现可以查看源码，`callq` 等同于 `call` 。

```asm
(gdb) disassemble main                                      # 反汇编main函数
Dump of assembler code for function main:
   0x0000000000400dc0 <+0>:     push   %rbp
   0x0000000000400dc1 <+1>:     mov    %rsp,%rbp            # 保存栈桢
   0x0000000000400dc4 <+4>:     mov    $0xd,%edx            # 字符串长度
   0x0000000000400dc9 <+9>:     mov    $0x48f230,%esi       # 字符串地址，打印数据 x/s 0x48f230
   0x0000000000400dce <+14>:    mov    $0x2,%edi            # 传入的第一个参数
   0x0000000000400dd3 <+19>:    callq  0x40ed30 <write>
   0x0000000000400dd8 <+24>:    mov    $0x0,%eax
   0x0000000000400ddd <+29>:    pop    %rbp
   0x0000000000400dde <+30>:    retq
End of assembler dump.

(gdb) disassemble 0x40ed30                                   # 反汇编write函数
Dump of assembler code for function write:
   0x000000000040ed30 <+0>:     cmpl   $0x0,0x2ae155(%rip)
   0x000000000040ed37 <+7>:     jne    0x40ed4d <write+29>
   0x000000000040ed39 <+0>:     mov    $0x1,%eax             # wirte的系统调用号
   0x000000000040ed3e <+5>:     syscall                      # 执行系统调用
   ... ...
```

系统会采用 `syscall` 和 `sysenter`，`x32` 大多采用 `sysenter`，而 `x64` 采用的是 `syscall` 。

### 内核实现

Linux 内核中维护了一张系统调用表 `sys_call_table[ ]@arch/x86/kernel/syscall_64.c` ，这是一个一维数组，索引为系统调用号，表中的元素是系统调用函数。

```c
const sys_call_ptr_t sys_call_table[__NR_syscall_max+1] = {
    [0 ... __NR_syscall_max] = &sys_ni_syscall,
#include <asm/syscalls_64.h>;
};
```

如上所示，默认所有调用都初始化为 `sys_ni_syscall()` ，而 `asm/syscalls_64.h` 实际是在编译时动态产生的。

编译内核时，会执行 `arch/x86/syscalls/Makefile` ，该文件会调用 `shell` 脚本 `syscalltdr.sh` ，该脚本以 `syscall_64.tbl` 文件作为输入，然后生成 `arch/x86/include/generated/asm/syscalls_64.h` ，最后生成的内容如下。

```c
//### arch/x86/include/generated/asm/syscalls_64.h
__SYSCALL_COMMON(0, sys_read, sys_read)
__SYSCALL_64(19, sys_readv, sys_readv)
__SYSCALL_X32(515, compat_sys_readv, compat_sys_readv)

//### arch/x86/kernel/syscall_64.c
extern asmlinkage void sys_read(void) ;
extern asmlinkage void sys_readv(void) ;
const sys_call_ptr_t sys_call_table[__NR_syscall_max+1] = {
    [0 ... __NR_syscall_max] = &sys_ni_syscall,
    [0] = sys_read, ...
    [19] = sys_readv, ...
};
```

最早的时候，在 x86 中，需要通过门进入内核态，系统调用通过 `int $0x80` 指令产生一个编号为 `128` 的软中断，对应于是中断描述符表 `IDT` 中的第 `128` 项，在此预设了一个内核空间的地址，它指向了系统调用处理程序 `system_call()` (该函数在 `arch/x86/kernel/entry_64.S` 中定义)。

由于传统的 `int 0x80` 系统调用浪费了很多时间，2.6 以后会采用 `sysenter/sysexit/syscall` 。

### 添加系统调用

添加系统调用方法如下。

#### 1. 定义系统调用号

在系统调用向量表里添加自定义的系统调用号。

向 `arch/x86/syscalls/syscall_64.tbl` 中加入自定义的系统调用号和函数名，添加时可以参考文件的注释，在 x86-64 中可以定义 `common/64/x32` 三种类型。

```c
555 common foobar    sys_foobar
```

#### 2. 添加函数声明

在 `arch/x86/include/asm/syscalls.h` 中添加函数声明。

```c
asmlinkage void sys_foobar(void) ;
```

#### 3. 添加函数的定义

在文件 `kernel/sys.c` 文件中加入对 `sys_foobar()` 的定义。

```c
SYSCALL_DEFINE0(foobar)
{
    printk(KERN_WARN "hello world foobar!");
    return 0;
}

EXPORT_SYMBOL(sys_foobar);
```

#### 4. 编译安装

通过 `make bzImage` && `make install` 编译安装。

## 优化

`vsyscall` 和 `vDSO` 是两种用来加速系统调用的机制。两者在执行系统调用时，都不需要改变优先级进入内核模式，不过相比来说后者更安全。如果获得了 `system()` 的入口，那么可以执行几乎任意的程序，`vDSO` 采用随机地址 (`cat /proc/self/maps`)，而且去除了一些可能有风险的代码。

静态连接都会调用”调用系统”，如果通过 `strace` 跟踪，则都会观察到系统调用。

### 示例

简单介绍 `gettimeofday()` 的使用方法，一般不需要获取时区，所以第二个参数通常设置为 NULL 。

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

int main(int argc, char **argv)
{
    struct  timeval    tv;
    struct  timezone   tz;
    gettimeofday(&tv, &tz);

    printf("tv_sec:%d\n", (int)tv.tv_sec);
    printf("tv_usec:%d\n", (int)tv.tv_usec);
    printf("tz_minuteswest:%d\n", tz.tz_minuteswest);
    printf("tz_dsttime:%d\n", tz.tz_dsttime);

    return 0;
}
```

在 x32 上，`gettimeofday()` 会调用 `__kernel_vsyscall()`，然后到 `sysenter` 指令。而在 x64 上，同时使用 `vsyscall` 和 `vdso`（这个可以通过/proc/PID/maps查看），应该优先使用 `vdso` 。

```bash
$ gcc gettimeofday.c -o gettimeofday -Wall -g
$ gdb gettimeofday -q
Reading symbols from /tmp/gettimeofday...done.
(gdb) b gettimeofday
Breakpoint 1 at 0x400460
(gdb) run
(gdb) disassemble
... ...
0x00007ffff7acb082 <+50>:    callq  0x7ffff7b4e8c0 <_dl_vdso_vsym>
... ...

(gdb) b _dl_vdso_vsym
(gdb) b __gettimeofday
```

## VDSO

Virtual Dynamic Shared Object, VDSO 是内核提供的功能，也就是为什么需要 `asm/vsyscall.h` 头文件，它提供了一种快速廉价的系统调用方式。

有些系统调用如 `gettimeofday()` ，会经常调用，传统的系统调用方式是通过软中断指令 `int 0x80` 实现的，最新的采用 `syscall()` 。不论何种操作，都需要进行压栈、跳转、权限级别提升，恢复用户栈，并跳转回低级别代码。

`vdso` 是将内核态的调用映射到用户态的地址空间中，会将当前时间放置到其它应用都可以访问的固定地方，这样应用不需要系统调用即可以。linux 中通过 `vsyscall` 实现，现在只支持三种系统调用，详见 `asm/vsyscall.h` 。

`vdso.so` 就是内核提供的虚拟的 .so ，这个 .so 文件不在磁盘上，而是在内核里头。内核把包含某 .so 的内存页在程序启动的时候映射入其内存空间，对应的程序就可以当普通的 .so 来使用里头的函数，比如 `syscall()` 。

### ASLR

Address-Space Layout Randomization, ASLR 将用户的一些地址随机化，如 `stack`, `mmap region`, `heap`, `text` ，可以通过 `randomize_va_space` 配置，对应的值有三种：

- 0 - 表示关闭进程地址空间随机化。
- 1 - 表示将mmap的基址，stack和vdso页面随机化。
- 2 - 表示在1的基础上增加栈（heap）的随机化。

可通过 `echo '0' > /proc/sys/kernel/randomize_va_space` 或 `sysctl -w kernel.randomize_va_space=0` 设置。然后，可以通过如下方式获取 `vdso.so` 文件。

```bash
$ cat /proc/sys/kernel/randomize_va_space
# sysctl -w kernel.randomize_va_space=0                           # 关闭随机映射
$ cat /proc/self/maps                                             # 查看vdso在内存中的映射位置
... ...
7ffff7ffa000-7ffff7ffc000 r-xp 00000000 00:00 0  [vdso]           # 占用了2pages
... ...
# dd if=/proc/self/mem of=linux-gate.so bs=4096 skip=$[7ffff7ffa] count=2  # 从内存中复制

$ readelf -h linux-gate.so                                        # 查看头信息
$ file linux-gate.so                                              # 查看文件类型，为shared-library ELF
$ objdump -T linux-gate.so                                        # 打印符号表，或者用-d反汇编
$ objdump -d linux-gate.so | grep -A5 \<__vdso.*:                 # 查看包含vdso的函数
```

可以从内存中读取该文件，或者使用 `extract_vdso.c` 直接读取该文件。

### 内核实现

内核实现在 `arch/x86/vdso` 中，编译生成 `vdso.so` 文件，通常来说该文件小于一个 `page(4096)` ，那么在内存中会映射为一个 `page` ，如果大于 `4k` ，会映射为 `2pages` 。

细节可以直接查看内核代码。

### 添加函数

在此通过 `vdso` 添加一个函数，返回一个值。

#### 1. 定义函数

在 `arch/x86/vdso` 目录下创建 `vfoobar.c`，其中 `notrace` 在 `arch/x86/include/asm/linkage.h` 中定义，也就是 `#define notrace __attribute__((no_instrument_function))` 。

同时需要告诉编译器一个用户态的函数 `foobar()` ，该函数属性为 `weak` 。`weak` 表示该函数在运行时才会解析，而且可以被覆盖。

```c
#include <asm/linkage.h>
notrace int __vdso_foobar(void)
{
    return 666;
}
int foobar(void) __attribute__((weak, alias("__vdso_foobar")));
```

#### 2. 添加到连接描述符

修改 `arch/x86/vdso/vdso.lds.S` ，这样编译的时或才会添加到 vdso.so 文件中。

```conf
VERSION {
    LINUX_2.6 {
        global:
            ... ...
            getcpu;
            __vdso_getcpu;

            foobar;
            __vdso_foobar;
        local: *;
    };
}
```

#### 3. 添加Makefile

修改 `arch/x86/vdso/Makefile` 文件，从而可以在编译内核时同时编译该文件。

```bash
# files to link into the vdso
vobjs-y := vdso-note.o vclock_gettime.o vgetcpu.o vfoobar.o
```

#### 4. 编辑用户程序

通过 `gcc foobar_u.c vdso.so` 编译如下文件，其中 vdso.so 提供了编译时的符号解析。

```c
#include <stdio.h>
int main(void)
{
    printf("His number is %d\n", foobar());
    return 0;
}
```

不过这样有一个缺陷，就是即使已经修改了内核，那么该函数还是返回之前设置的值。实际上可以返回一个内核中的值，如 `gettimeofday()` ，实际通过 `update_vsyscall()@arch/x86/kernel/vsyscall_64.c` 进行更新，相应的设置可以参考相关函数调用。