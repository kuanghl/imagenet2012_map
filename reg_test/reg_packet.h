#ifndef __REG_PACKET_H__
#define __REG_PACKET_H__

#include <stdint.h>

typedef enum {
    REG_CMD_EMPTY_TEST = 0,
    REG_CMD_INITED,
    REG_CMD_SYNC_TIME,
    REG_CMD_SYNC_ATC_TIME,
    USB_CMD_ALL,
} reg_cmd_u; 

// for MCU process
int mcu_send_packet(reg_shm_t *shm, uint32_t cmd, void *buf, uint32_t len);
int mcu_recv_packet(reg_shm_t *shm, void *buf, uint32_t size);

// for HPS process
typedef enum {
    REG_TASK_STA_IDLE = 0,
    REG_TASK_STA_READY = 1
} task_sta_u;

typedef struct task_handle_s {
    // for task
    volatile task_sta_u sta;    // 0: idle 1: busy
    uint8_t *buf;
    uint32_t len;

    // for process packet
    uint32_t cmd;
    uint32_t seq;
    uint32_t pk_len;            // packet len
    uint32_t recv_len;          // recv len
    uint32_t this_len;          // this recv len
} task_handle_t;

int hps_recv_init(task_handle_t *hd, uint8_t *buf, uint32_t len);
int hps_recv_packet_and_run(reg_shm_t *shm, task_handle_t *hd);
int hps_send_packet(reg_shm_t *shm, void *buf, uint32_t len);

#endif // !__REG_PACKET_H__