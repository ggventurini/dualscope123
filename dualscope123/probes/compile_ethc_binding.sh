gcc -c -Wall -O2 -Wall -ansi -pedantic -fPIC -o ethc.o ethc.c
gcc -o libethc.so -shared ethc.o
