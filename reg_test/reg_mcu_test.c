#include <unistd.h>

#include "reg_shm.h"
#include "reg_packet.h"
#include "log.h"

int main(int argc, char *argv[])
{
    uint8_t buf[1024] = { 0 };
    uint32_t len = 1024;

    uint8_t rbuf[1024] = { 0 };
    uint32_t rlen = 1024;

    reg_shm_t *shm = reg_shm_create(true);
    if (shm == NULL) {
        log_error("error\n");
        return -1;
    }

    snprintf((char *)buf, 1024, "hallo world\n");
    while (true)
    {
        // // shm
        // reg_shm_write_aword(shm, 0x0, 0x1234565);
        // uint32_t temp = reg_shm_read_aword(shm, 0x0);
        // log_info("temp 0x%lx\n", temp);

        mcu_send_packet(shm, (uint32_t)REG_CMD_INITED, buf, 508);
        mcu_recv_packet(shm, rbuf, rlen);

        log_info("recv from hps: %s\n", rbuf);

        sleep(1);

        log_info("MCU send data done\n");
    }

    reg_shm_del(shm, false);
    
    return 0;
}