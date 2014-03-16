/* Modified code from Maciek */
/* Connects to an NIOS server and gets the specified amount of data */

#define h_addr h_addr_list[0] /* for backward compatibility */

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

void print_raw(char *buffer, const void *object, size_t size)
{
	size_t i;
	for(i = 0; i < size; i++)
	{
		sprintf(&buffer[i*2], "%02x", ((const unsigned char *) object)[i] & 0xff);
		/* printf("%02x", ((const unsigned char *) object)[i] & 0xff); */
	}
	return;
}

char *read_nios(char *hostname, int port, int ch_number, int chunks_count)
{
	int sock, i, j;
	long int n, nold;
	/* const struct sockaddr serv_addr; */
	struct sockaddr_in serv_addr;
	struct hostent *server;
	
	char *buffer;
	char *ret;
	
	signed int acq_data_cast;
	
	unsigned int acq_data;
	unsigned int chunk_size = 350;
	unsigned int data_count;
	unsigned char start_stop;
	unsigned char data_type;
	
	unsigned char payload_counter;
	unsigned int error_counter;
	unsigned int requests_counter;
	unsigned int frame_number;
	
	unsigned char command[4];
	
	struct timeval t_start;
	struct timeval t_end;
	long int read_time_us;
	
	unsigned int points;
	double data_mean;
	int data_max;
	int data_min;
	int suppress_count = 5;
	
	signed short prev_sample;
	
	/* create socket */
	if((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		perror("socket");
		exit(EXIT_FAILURE);
	}

	server = gethostbyname(hostname);

	if (server == NULL) {
		fprintf(stderr,"ERROR, no such host\n");
		exit(0);
	}

	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, 
		   (char *)&serv_addr.sin_addr.s_addr,
				server->h_length);
	serv_addr.sin_port = htons(port);
	
	/* Now connect to the server */
	if (connect(sock, &serv_addr, sizeof(serv_addr)) < 0) 
	{
		 perror("ERROR connecting");
		 exit(1);
	}	
	
	error_counter = 0;
	requests_counter = 0;

	if (ch_number < 0 || ch_number >7){
		perror("ERROR: channels go from 0 to 7.");
		exit(1);
	}
		

	data_count = chunks_count*chunk_size*4;
	buffer = (char*)malloc(data_count);
	if (buffer==NULL) 
	{
		perror("ERROR allocating READ buffer");
		exit(1);
	}
	bzero(buffer, data_count);
	ret = (char*)malloc(data_count*2);
	if (ret==NULL) 
	{
		perror("ERROR allocating DATA buffer");
		exit(1);
	}
	bzero(ret, 2*data_count);
	
	/* Send command to the server */
	start_stop = 1;
	data_type = 0;
		
	command[0] = start_stop << 7 | (data_type & 3)<<5 | (ch_number & 7)<<2 | (chunks_count&0x3000000)>>18;
	command[1] = (unsigned char)((chunks_count&0xFF0000)>>16);
	command[2] = (unsigned char)((chunks_count&0xFF00)>>8);
	command[3] = (unsigned char)(chunks_count&0xFF);
		
	/* printf("command = %x %x %x %x\n", command[0], command[1], command[2], command[3]); */
		
	n = (long int) write(sock,command,4);
	if (n < 0) 
	{
		 perror("ERROR writing to socket");
		 exit(1);
	}
		
	/* Now read server response */
		
	n = 0L; /* read(sock, buffer, data_count); */
	nold = 0L;
	payload_counter = 0;

	while(n<data_count)
	{
		n += (long int) read(sock, buffer+n, data_count-n);
		if (n <= nold) 
		{
			 perror("ERROR reading from socket");
			 exit(1);
		}
		nold = n;
	}
		
	for(i=0; i < chunks_count*chunk_size; i++)
	{
		acq_data = (buffer[i*4]&0xFF)<<24 | (buffer[i*4+1]&0xFF)<<16 | (buffer[i*4+2]&0xFF)<<8 | (buffer[i*4+3]&0xFF) ;
		acq_data_cast = (signed int)((acq_data&0x003FFFFF) << 11);
		acq_data_cast = acq_data_cast >> 11;
		frame_number = (unsigned int)(acq_data&0x07E00000)>>21;
		
		print_raw(&ret[8*i], &acq_data_cast, 4);
		/* check if some data was lost */
		if( payload_counter != ((acq_data>>21)&0x3F) )
		{
			error_counter++;
			if (error_counter <= suppress_count)
				fprintf(stderr, "Dropping packets: payload counter is %d, expected payload counter is %d\n", ((acq_data>>21)&0x3F), payload_counter);
			if(error_counter == suppress_count)
				fprintf(stderr, "Further dropped packets notices will be suppressed.\n");
			payload_counter = ((acq_data>>21)&0x3F);
		}

		/* payload_counter will count 0-63 */
		/* payload_counter must be 8 bits  */
		payload_counter = (payload_counter<<2) + (1<<2);
		payload_counter >>= 2;
	}
	if (error_counter > suppress_count)
		fprintf(stderr, "%d errors have been suppressed.\n", error_counter, requests_counter);
	/* print_raw(buffer, data_count); */
	/* printf("%s", (char *) buffer); */
	close(sock);
	free(buffer);
	
	return ret;
}
int main(int argc,char** argv)
{
	int port, ch_number, chunks_count;
	char *buf;
	if(argc < 4)
	{
		fprintf(stderr,"usage %s hostname port channel nchunks\nChannels start at 1!\n", argv[0]);
		exit(EXIT_FAILURE);
	}
	port = atoi(argv[2]);     /*Convert port number to integer*/
	ch_number = atoi(argv[3])-1;
	chunks_count = atoi(argv[4]);
	buf = (char *) read_nios(argv[1], port, ch_number, chunks_count);
	fprintf(stdout, "%s", buf);
	free(buf);
	exit(0);
}
