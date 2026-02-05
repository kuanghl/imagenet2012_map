#include <pthread.h>
#include <libgen.h>

#include "log.h"

#define MAX_CALLBACKS 1

typedef struct {
    log_logcb fn;       /* callback function */
    void *udata;        /* handle */
    int level;          /* callback function level trigger in log function >= level */
} log_cb;

static struct {
    void *udata;                /* handle */
    log_lockcb lock;            /* lock callback function for multi-thread call */
    int level;                  /* global log level */
    bool quiet;                 /* printf in terminal disable */
    log_cb cbs[MAX_CALLBACKS];  /* array for callback function, such as file_callback/stdout_callback/... */
} log_ctx = {  // log context to use
    NULL, NULL, 0, false, {0}
};

static struct {
    bool once;                      /* whether log file is initialized for alog */
    FILE *fp;                       /* file pointer for alog_ctx for alog */
    pthread_mutex_t lock;           /* log lock for alog */
    size_t pos;                     /* current file position for alog */ 
} alog_ctx = {
    false, NULL, PTHREAD_MUTEX_INITIALIZER, 0
};

static const char *level_strings[] = {
    "FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"
};

#if logcolor_en
static const char *level_colors[] = {
    LOG_FATAL_COLOR, LOG_ERROR_COLOR, LOG_WARN_COLOR, LOG_INFO_COLOR, LOG_DEBUG_COLOR, LOG_TRACE_COLOR
};
#endif

static void log_reset_file_pos(void);

static void stdout_callback(log_event *ev) 
{
    char buf[64];
    // ev->udata is stderr
    buf[strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", ev->time)] = '\0';
#if logcolor_en
    fprintf(
        ev->udata, "[%s] %s%-5s\x1b[0m [%s] \x1b[90m%s:%d:%s():\x1b[0m ",
        buf, level_colors[ev->level], level_strings[ev->level], ev->tag,
        ev->file, ev->line, ev->func);
#else
    fprintf(
        ev->udata, "[%s] %-5s [%s] %s:%d:%s(): ",
        buf, level_strings[ev->level], ev->tag, ev->file, ev->line, ev->func);
#endif
    vfprintf(ev->udata, ev->fmt, ev->ap);
    fprintf(ev->udata, "\n");
    fflush(ev->udata);
}


static void file_callback(log_event *ev) 
{
    size_t size = 0;
    char buf[64];
    // ev->udata is file handle
    buf[strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", ev->time)] = '\0';
    size = fprintf(
        ev->udata, "[%s] %-5s [%s] %s:%d:%s(): ",
        buf, level_strings[ev->level], ev->tag, ev->file, ev->line, ev->func);
    size += vfprintf(ev->udata, ev->fmt, ev->ap);
    size += fprintf(ev->udata, "\n");
    fflush(ev->udata);
    
    // check log position 
    alog_ctx.pos += size;
    if (alog_ctx.pos >= LOG_FILE_MAXSIZE) {
        log_reset_file_pos();
        alog_ctx.pos = 0;
    }
}


static void lock(void)   
{
    if (log_ctx.lock) 
        log_ctx.lock(true, log_ctx.udata);  
}


static void unlock(void) 
{
    if (log_ctx.lock)
        log_ctx.lock(false, log_ctx.udata);
}


const char* log_level_string(int level) 
{
    return level_strings[level];
}


void log_set_lock(log_lockcb fn, void *udata) 
{
    log_ctx.lock = fn;
    log_ctx.udata = udata;
}


void log_set_level(int level) 
{
    if (level < LOG_FATAL || level > LOG_TRACE)
        return;
    log_ctx.level = level;
}


int log_get_level(void)
{
    return log_ctx.level;
}


void log_set_quiet(bool enable) 
{
    log_ctx.quiet = enable;
}


int log_add_cb(log_logcb fn, void *udata, int level) 
{
    for (int i = 0; i < MAX_CALLBACKS; i++) {
        if (!log_ctx.cbs[i].fn) {
            log_ctx.cbs[i] = (log_cb) { fn, udata, level };
            return i;
        }
    }
    return -1;
}


void log_remove_cb(int id)  
{
    if(id >= 0 && id < MAX_CALLBACKS)
        log_ctx.cbs[id] = (log_cb) { NULL, NULL, 0 };
}


int log_add_fp(FILE *fp, int level) 
{
    return log_add_cb(file_callback, fp, level);
}


void log_remove_fp(int id) 
{
    log_remove_cb(id); 
}


static void init_event(log_event *ev, void *udata) 
{
    if (!ev->time) {
        time_t t = time(NULL);
        ev->time = localtime(&t);
    }
    ev->udata = udata;
}


void log_log(int level, const char *tag, const char *file, int line, const char *func, const char *fmt, ...) 
{
    log_event ev = {
        .fmt   = fmt,
        .tag   = tag,
        .file  = basename((char *)file),
        .func  = func,
        .line  = line,
        .level = level,
    };

    lock();
    
    /* printf log */
    if (!log_ctx.quiet && level <= log_ctx.level) {
        init_event(&ev, stderr); // stdout
        va_start(ev.ap, fmt);
        stdout_callback(&ev);
        va_end(ev.ap);
    }

    /* callback */
    for (int i = 0; i < MAX_CALLBACKS && log_ctx.cbs[i].fn; i++) {
        log_cb *cb = &log_ctx.cbs[i];
        if (level <= cb->level) {
            init_event(&ev, cb->udata);
            va_start(ev.ap, fmt);
            cb->fn(&ev);
            va_end(ev.ap);
        }
    }

    unlock();
}

//
// for case of semptian
//

void log_lock(bool lock, void* udata) 
{
    pthread_mutex_t *LOCK = (pthread_mutex_t*)(udata);
    if (lock)
        pthread_mutex_lock(LOCK);
    else
        pthread_mutex_unlock(LOCK);
}

// reset file pos for ringbuffer log
void log_reset_file_pos(void)
{
    FILE *fp = NULL;

    if (log_ctx.cbs[0].fn) {
        fp = (FILE *)log_ctx.cbs[0].udata;
        fseek(fp, 0, SEEK_SET);
    }     
}

// used log name is hps-main.log for semptian
void log_init(int level, const char *log_file)
{
    int ret = 0;

    if (alog_ctx.once) {
        // already initialized
        return;
    }

    // hps-main_%s_%d.log, (time %Y_%m_%d_%H_%M_%S), rand()
    log_set_level(level);
    if (log_file) {
        // log file exist check
        // slog_fp = fopen(log_file, "rb+"); 
        // if (NULL == slog_fp) 
        alog_ctx.fp = fopen(log_file, "wb+");
        if (alog_ctx.fp) {
            ret = log_add_fp(alog_ctx.fp, level);
            if (ret < 0) {
                printf("%s, log_add_fp failed\n", __func__);
                fclose(alog_ctx.fp);
                return;
            }
        }
        else {
            printf("%s, open log file %s fail\n", __func__, log_file);
            return;
        }
    }

    // lock and unlock to init mutex if set
    log_set_lock(log_lock, &alog_ctx.lock);
    alog_ctx.once = true;

    // for new log start
    alog_fatal("log", "===================== Log Initialized ====================\n");
}

void log_deinit(void)
{
    if (!alog_ctx.once) {
        return;
    }

    if (alog_ctx.fp) {
        fclose(alog_ctx.fp);
        alog_ctx.fp = NULL;
    }
    alog_ctx.once = false;
}