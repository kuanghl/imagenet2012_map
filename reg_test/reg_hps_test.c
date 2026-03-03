#include <unistd.h>

#include "reg_shm.h"
#include "reg_packet.h"
#include "log.h"

int main(int argc, char *argv[])
{
    uint8_t buf[1024] = { 0 };
    uint32_t len = 1024;
    task_handle_t hd = { 0 };

    reg_shm_t *shm = reg_shm_create(true);
    if (shm == NULL) {
        log_error("error\n");
        return -1;
    }
    hps_recv_init(&hd, buf, len);

    while (true)
    {
        hps_recv_packet_and_run(shm, &hd);
        
        // // shm
        // reg_shm_write_aword(shm, 0x0, 0x1234565);
        // uint32_t temp = reg_shm_read_aword(shm, 0x0);
        // log_info("temp 0x%lx\n", temp);

        usleep(10);
    }

    reg_shm_del(shm, true);
}