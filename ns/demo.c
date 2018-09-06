#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <stdio.h>
#include <sched.h>
#include <signal.h>
#include <unistd.h>

#define STACK_SIZE (1024 * 1024)

static char container_stack[STACK_SIZE];
char* container_args[] = {
    "/bin/bash",
    NULL,
    NULL,
    NULL,
    NULL
};

int container_main(void* arg)
{
    printf("Container [%5d] - inside the container!\n", getpid());

    //set hostname
    sethostname("demo-container",10);

    //remount "/proc" to make sure the "top" and "ps" show container's information
    if (mount("proc", "./rootfs/proc", "proc", 0, NULL) != 0 ) {
        perror("proc");
    }

//    if (mount("sysfs", "./rootfs/sys", "sysfs", 0, NULL) != 0) {
//        perror("sys");
//    }

    if (mount("tmpfs", "./rootfs/run", "tmpfs", 0, NULL) != 0) {
        perror("run");
    }

    /* chroot 隔离目录 */
    if (chdir("./rootfs") != 0 || chroot("./") != 0){
        perror("chdir/chroot");
    }

    execvp(container_args[0], container_args);
    perror("exec");
    printf("Something's wrong!\n");
    return 1;
}

int main(int argc, char *argv[])
{
    if(argc < 2 || argc > 5){
       printf("Usage: demo [COMMAND...] \n");
       return 1;
    }

    for (int i = 1; i < argc; i++) {
        container_args[i - 1] = argv[i];
    }

    printf("Parent [%5d] - start a container!\n", getpid());
    int container_pid = clone(container_main, container_stack + STACK_SIZE,
            CLONE_NEWUTS | CLONE_NEWIPC | CLONE_NEWPID  |
            CLONE_NEWNET | CLONE_NEWNS | SIGCHLD, NULL);
    waitpid(container_pid, NULL, 0);
    printf("Parent - container stopped!\n");
    return 0;
}