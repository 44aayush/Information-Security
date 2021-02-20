#include<stdio.h>
#include<unistd.h>
#include<sys/types.h>

int main()
{
	char *argv[2];
	argv[0] = "/bin/sh";
	argv[1] = "NULL";

	setuid(0);
	execve("/bin/sh",argv,NULL);
	return 0;
}
