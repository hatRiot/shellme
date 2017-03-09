shellme
=======

Because sometimes you just need shellcode and opcodes quickly.  This essentially just wraps
some nasm/objdump calls into a neat script.

```
bryan@devbox:~/shellme$ python shellme.py 
usage: shellme.py [-h] [-n FILE] [-o OUTPUT] [-i INSTRUCTION] [-a ARCH]

optional arguments:
  -h, --help      show this help message and exit
  -n FILE         nasm or object file
  -o OUTPUT       output file
  -i INSTRUCTION  instruction
  -a ARCH         architecture [elf/elf64]
bryan@devbox:~/shellme$ cat test.nasm
Section .text
	global _start

_start:
	mov ebx,0
	mov eax,1
	int 0x80

_stuff:
	xor eax,0
	xor ecx,0
	xor ebx,0
	push ebp
	sub esp,8
bryan@devbox:~/shellme$ python shellme.py -n test.nasm
[+] Encoded:
\xbb\x00\x00\x00\x00\xb8\x01\x00
\x00\x00\xcd\x80\x35\x00\x00\x00
\x00\x81\xf1\x00\x00\x00\x00\x81
\xf3\x00\x00\x00\x00\x55\x81\xec
\x08\x00\x00\x00
bryan@devbox:~/shellme$ python shellme.py -n test64.o -a elf64
[+] Encoded:
\x48\x89\xec
```

And stuff on the fly if you need it:
```
bryan@devbox:~/shellme$ python shellme.py -i 'jmp rbp' -a elf64
[+] Encoded:
\xff\xe5
bryan@devbox:~/shellme$ python shellme.py -i 'add rsp,4\njmp rsp' -a elf64
[+] Encoded:
\x48\x81\xc4\x04\x00\x00\x00\xff
\xe4
bryan@devbox:~/shellme$ python shellme.py -i 'add ebp,4\njmp ebp'
[+] Encoded:
\x81\xc5\x04\x00\x00\x00\xff\xe5
bryan@devbox:~/shellme$ python shellme.py -i 'mov eax,15\nadd ebp,eax\nxor eax,eax\njmp ebp'
[+] Encoded:
\xb8\x0f\x00\x00\x00\x01\xc5\x31
\xc0\xff\xe5
```

And compiled elfs:
```
bryan@devbox:~/shellme$ cat test.c
#include <stdio.h>
int main(){
	char *tmp[2];
	tmp[0] = "/bin/sh";
	tmp[1] = NULL;
	execve(tmp[0], &tmp, NULL);
}
bryan@devbox:~/shellme$ gcc test.c -o test
bryan@devbox:~/shellme$ python shellme.py -n test
[+] Encoded:
\x48\x83\xec\x08\xe8\x6b\x00\x00
\x00\xe8\xfa\x00\x00\x00\xe8\xf5
\x01\x00\x00\x48\x83\xc4\x08\xc3
\xff\x35\xba\x04\x20\x00\xff\x25
\xbc\x04\x20\x00\x0f\x1f\x40\x00
\xff\x25\xba\x04\x20\x00\x68\x00
\x00\x00\x00\xe9\xe0\xff\xff\xff
\xff\x25\xb2\x04\x20\x00\x68\x01
\x00\x00\x00\xe9\xd0\xff\xff\xff
\x31\xed\x49\x89\xd1\x5e\x48\x89
\xe2\x48\x83\xe4\xf0\x50\x54\x49
\xc7\xc0\x20\x05\x40\x00\x48\xc7
\xc1\x30\x05\x40\x00\x48\xc7\xc7
\xe4\x04\x40\x00\xe8\xb7\xff\xff
\xff\xf4\x90\x90\x48\x83\xec\x08
\x48\x8b\x05\x49\x04\x20\x00\x48
[................]
```
