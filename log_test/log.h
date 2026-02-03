#ifndef __LOG_H__
#define __LOG_H__

#include <stdio.h>
#include <stdarg.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#ifdef __cplusplus
extern "C"{
#endif /*__cplusplus*/

typedef struct {
    va_list ap;
    const char *fmt;
    const char *tag;
    const char *file;
    const char *func;
    struct tm *time;
    void *udata;
    int line;
    int level;
} log_event;

/*
 eg:
    void callback1(log_event *ev)
    {
        char buf[16];
        buf[strftime(buf, sizeof(buf), "%H:%M:%S", ev->time)] = '\0';
        fprintf(stdout, "callback 1 %s %-5s %s:%d: ", buf, "INFO", ev->file, ev->line);
        vfprintf(stdout, ev->fmt, ev->ap);
        fprintf(stdout, "\n");
        fflush(stdout);
    } 

    // use
    log_add_callback(callback1, "none", LOG_ERROR);
    log_add_callback(callback1, NULL, LOG_ERROR);
 */
typedef void (*log_logcb)(log_event *ev);

/*
 eg:
    void log_lock(bool lock, void* udata) {
        pthread_mutex_t *LOCK = (pthread_mutex_t*)(udata);
        if (lock)
            pthread_mutex_lock(LOCK);
        else
            pthread_mutex_unlock(LOCK);
    }

    // use
    pthread_mutex_t alock;
    log_set_lock(log_lock, &alock);
 */
typedef void (*log_lockcb)(bool lock, void *udata);

/**
 * Returns the name of the given log level as a string.
 */
const char* log_level_string(int level);

/**
 * If the log will be written to from multiple threads a lock function can be set. 
 * The function is passed the boolean true if the lock should be acquired or false if the lock should be released and the given udata value.
 */
void log_set_lock(log_lockcb fn, void *udata);

/**
 * The current logging level can be set by using the log_set_level() function. 
 * All logs below the given level will not be written to stderr. By default the level is LOG_TRACE, such that nothing is ignored.
 */
void log_set_level(int level);
int log_get_level(void);

/**
 * Quiet-mode can be enabled by passing true to the log_set_quiet() function. 
 * While this mode is enabled the library will not output anything to stderr, but will continue to write to files and callbacks if any are set.
 */
void log_set_quiet(bool enable);

/**
 * One or more callback functions which are called with the log data can be provided to the library by using the log_add_callback() function. 
 * A callback function is passed a log_Event structure containing the line number, filename, fmt string, va printf va_list, level and the given udata.
 * If callback array filled fully a value < 0 is returned. However, return register id > 0.
 */
int log_add_cb(log_logcb fn, void *udata, int level);

/**
 * Remove fn callback registered from log_add_callback() according to register id.
 */
void log_remove_cb(int id);

/**
 * One or more file pointers where the log will be written can be provided to the library by using the log_add_fp() function. 
 * The data written to the file output is of the following format: 2047-03-11 20:18:26 TRACE src/main.c:11: Hello world
 * Any messages below the given level are ignored. 
 * If the library failed to add a file pointer a value < 0 is returned. However, return register id > 0.
 */
int log_add_fp(FILE *fp, int level);

/**
 * Remove fp callback registered from log_add_fp() according to register id.
 */
void log_remove_fp(int id);

/**
 * log to use.
 */
void log_log(int level, const char *tag, const char *file, int line, const char *func, const char *fmt, ...);

/**
 * log initialize
 */
void log_init(int level, const char *log_file);
void log_deinit(void);

// #define DEFAULT         "\033["
// #define BLACK           "\033[30"
// #define GREY            "\033[1;30"
// #define DARK_RED        "\033[31"
// #define RED             "\033[1;31"
// #define DARK_GREEN      "\033[32"
// #define GREEN           "\033[1;32"
// #define DARK_YELLOW     "\033[33"
// #define YELLOW          "\033[1;33"
// #define DARK_BLUE       "\033[34"
// #define BLUE            "\033[1;34"
// #define DARK_MAGENTA    "\033[35"
// #define MAGENTA         "\033[1;35"
// #define DARK_CYAN       "\033[36"
// #define CYAN            "\033[1;36"
// #define LIGHT_GREY      "\033[37"
// #define WHITE           "\033[1;37"

// #define BG_DEFAULT      "m"
// #define BG_BLACK        ";40m"
// #define BG_RED          ";41m"
// #define BG_GREEN        ";42m"
// #define BG_YELLOW       ";43m"
// #define BG_BLUE         ";44m"
// #define BG_MAGENTA      ";45m"
// #define BG_CYAN         ";46m"
// #define BG_WHITE        ";47m"

#define LOG_TRACE_COLOR     "\x1b[94m"
#define LOG_DEBUG_COLOR     "\x1b[36m"
#define LOG_INFO_COLOR      "\x1b[32m"
#define LOG_WARN_COLOR      "\x1b[33m"
#define LOG_ERROR_COLOR     "\x1b[31m"
#define LOG_FATAL_COLOR     "\x1b[1;31m"
#ifndef logcolor_en
#define logcolor_en true 
#endif // !logcolor_en

/* log level to compile */
#define LOG_TRACE 5
#define LOG_DEBUG 4
#define LOG_INFO  3
#define LOG_WARN  2
#define LOG_ERROR 1
#define LOG_FATAL 0
#ifndef log_level
#define loglevel LOG_ERROR
#endif // !log_level

/* log file maxsize */
#define LOG_FILE_MAXSIZE    (4096 - 1024) // (64 * 1024 * 1024 - 1024)  // 64MB - 1KB, 1KB for last log line

/* loglevel as list */
// #define log_trace(...) log_log(LOG_TRACE, "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)
// #define log_debug(...) log_log(LOG_DEBUG, "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)
// #define log_info(...)  log_log(LOG_INFO,  "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)
// #define log_warn(...)  log_log(LOG_WARN,  "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)
// #define log_error(...) log_log(LOG_ERROR, "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)
// #define log_fatal(...) log_log(LOG_FATAL, "tag", __FILE__, __LINE__, __func__, __VA_ARGS__)

#define alog_trace(tag, ...)    log_log(LOG_TRACE, (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)
#define alog_debug(tag, ...)    log_log(LOG_DEBUG, (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)
#define alog_info(tag, ...)     log_log(LOG_INFO,  (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)
#define alog_warn(tag, ...)     log_log(LOG_WARN,  (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)
#define alog_error(tag, ...)    log_log(LOG_ERROR, (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)
#define alog_fatal(tag, ...)    log_log(LOG_FATAL, (tag), __FILE__, __LINE__, __func__, __VA_ARGS__)

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
