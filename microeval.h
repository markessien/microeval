
#ifndef _MICROEVAL_H_
#define _MICROEVAL_H_

void ulogdf_impl(char* s, int log_level, char* filename, int line, const char* functionname, ...);
void ulogdf_impl_simple(char* format, ...);
void ulog_init();
void ulog_error_impl_simple(char* format, ...);

#define CURRENTLOG_LEVEL LOG_DEBUG

#define LOG_ALL       0
#define LOG_CRITICAL  1
#define LOG_IMPORTANT 2
#define LOG_INFO      3
#define LOG_DEBUG     4

#define ULOG_ENABLED  1

#if ULOG_ENABLED



/*
	#define	ulog printf
	#define ulog_error printf
	#define ulog_info(x, ...)
*/

	#define ulog ulogdf_impl_simple
	#define ulog_error ulog_error_impl_simple
	#define ulog_info(x, ...)
	#define ulog_force printf

	// #define ulog(x, ...) ulogdf_impl(x, LOG_ALL, __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)
	// #define ulog_info(x, ...) ulogdf_impl(x, LOG_INFO, __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)

	// #define ulog_debug(x, ...) ulogdf_impl(x, LOG_DEBUG, __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)
	// #define ulog_error(x, ...) ulogdf_impl(x, LOG_CRITICAL, __FILE__, __LINE__, __FUNCTION__, ##__VA_ARGS__)
	// #define ulog_force printf
#else
	#define ulog(x, ...)
	#define ulog_info(x, ...)
	#define ulog_debug(x, ...)
	#define ulog_error(x, ...)
	#define ulog_force printf
#endif



#endif
