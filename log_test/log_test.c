#include "log.h"
#include <unistd.h>

int main(int argc, char *argv[])
{
    log_init(LOG_DEBUG, "./log_test.log");

    while (true)
    {
        alog_trace("test", "hello\n");
        alog_debug("test", "hello\n");
        alog_info("test", "hello\n");
        alog_warn("test", "hello\n");
        alog_error("test", "hello\n");
        alog_fatal("test", "hello\n");
        alog_fatal("test", "hello, %s\n", __FILE__);
        alog_fatal("test", "123\n");
        sleep(1);
    }

    log_deinit();
    
    return 0;
}