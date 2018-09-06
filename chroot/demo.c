#include <stdio.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    if(argc < 2){
       printf("Usage: chroot [COMMAND...] \n");
       return 1;
    }

    chroot("/home/james/busybox");
    chdir("/");

    
    mount("proc", "./proc", "proc", 0, NULL);
    mount("sysfs", "./sys", "sysfs", 0, NULL);

    argv += 1;

    execvp(argv[0], argv);

    printf("chroot: cannot run command %d, `%s`\n", argc, *argv);

    return 0;
}

