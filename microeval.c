#include "microeval.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdarg.h>
#include <mutex.h>

// Specifies how deep in the function calling heirachy we are
int print_level = 1; // The function call depth to be printed
int flag_have_newline; // says if last print had a newline

char spacing[30];
static int verbose = 0;
// static mutex_t print_mutex;
static volatile int print_lock = 0;

void ulog_init()
{
	// mutex_init(&print_mutex);
}

void ulogdf_impl_simple(char* format, ...)
{
	// mutex_lock(&print_mutex);


	/*
	char x[300];
	strcpy(x, format);

	int len = strlen(x);
	for (int i=0;i<len;i++)
	{
		if (x[i] == '%' && x[i+1] == 's')
			x[i] = 'X';
	}

	va_list args;
	va_start( args, format );
	vfprintf( stdout, format, args );
	va_end( args );
*/
	char out[200];

    va_list args;
    va_start(args, format);
    vsnprintf(out, 200, format, args);
    va_end( args );

	printf(out);
	printf("\n");
	fflush(stdout);

    // mutex_unlock(&print_mutex, true);
}

void ulog_error_impl_simple(char* format, ...)
{
//	mutex_lock(&print_mutex);

	char out[200];

	printf("(ERROR)");

    va_list args;
    va_start(args, format);
    vsnprintf(out, 200, format, args);
    va_end( args );

	printf(out);
	printf("\n");
	fflush(stdout);

  //  mutex_unlock(&print_mutex, true);
}

void ulogdf_impl(char* s, int log_level, char* filename, int line, const char* functionname, ...)
{
	if (log_level == LOG_INFO && verbose == 0)
		return; // no output of 'info' in non-verbose mode

	/*
	mutex_lock(&print_mutex);
	printf(s);
	printf("\n");
	fflush(stdout);
	mutex_unlock(&print_mutex, true);
	*/

	/*
	print_lock = 1;

	char* short_file_name = strrchr(filename, '/') + 1;

	if (s[0] == '>')
		strcpy(spacing, "     ");
	else
		strcpy(spacing, " ");

	char* error = " ";
	if (log_level == LOG_CRITICAL)
	{
		error = " (ERROR) ";
	}

	char msgbuffer[400];
	snprintf(msgbuffer, 397, "%s# %s%-30s      @ln%d in %s -- function %s\n", spacing, error, s, line, short_file_name, functionname);

	// char out[200];
    va_list args;
    va_start(args, functionname);
    //vsnprintf(out, 200, msgbuffer, args);
    vprintf(msgbuffer, args );
    va_end( args );

    // printf(out);
    fflush(stdout);

    flag_have_newline = 0;
    print_lock = 0;
    */

}



