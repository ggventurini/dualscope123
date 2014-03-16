/* Modified code from Maciek */
/* Connects to an NIOS server, asks for the specified amount of data */
/* and prints it out in HEX format */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <signal.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/socket.h>
#include <pthread.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>

void print_raw(char *buffer, const void *object, size_t size);
char *read_nios(char *hostname, int port, int ch_number, int chunks_count);
