#include <time.h>
#include <unistd.h>

#include "log.h"
#include "reg_shm.h"
#include "reg_packet.h"

/**
 * casel
 * MCU -- transfer1 -> MCU_WRITE_DONE
 * HPS -- read transfer1 done -> HPS_READ_DONE
 * HPS -- check packet done
 */

// 1Btye for MCU write
typedef enum {
    REG_WSTATE_RESV = 0x0,               /* bit[24:31] - resv for default state, then only MCU can write */      
    REG_MCU_WRITE_DONE = 0x1,            /* bit[24:31] - MCU write REG done to set, then no option can do */
    REG_HPS_READ_DONE =  0x2,            /* bit[24:31] - HPS read REG done to set, then only MCU can write */
    REG_WSTATE_DEFAULT = 0xff            /* bit[24:31] - resv for default state, then only MCU can write */
} reg_wstate_u;

// 1Byte for HPS write
typedef enum {
    REG_RSTATE_RESV = 0x0,               /* bit[8:15] - resv for default state, then only HPS can write */      
    REG_HPS_WRITE_DONE = 0x1,            /* bit[8:15] - HPS write REG done to set, then no option can do */
    REG_MCU_READ_DONE =  0x2,            /* bit[8:15] - MCU read REG done to set, then only HPS can write */
    REG_RSTATE_DEFAULT = 0xff            /* bit[8:15] - resv for default state, only HPS can write */
} reg_rstate_u;

// ctrl: woffs = 0x0
// size = 5 * 4
// resv: woffs = 0x5
// size = 3 * 4
// data: woffs = 0x5
// size = (32 - 8) * 4 = 24 * 4
#define REG_START_WOFFS         (0x0) 
#define REG_CTRL_WOFFS          (0x0)
#define REG_CTRL_CMD_WOFFS      (0x0)                       /**< 0x0 cmd for the packet - uint32_t cmd */
#define REG_CTRL_SEQ_WOFFS      (0x1)                       /**< 0x1 per packet index for sequence - uint32_t seq */
#define REG_CTRL_WLEN_WOFFS     (0x2)                       /**< 0x2 MCU write |packet len(High 16bits)|transfer len(Low 16bits)| - uint32_t wlen */
#define REG_CTRL_RLEN_WOFFS     (0x3)                       /**< 0x3 MCU read |packet len(High 16bits)|transfer len(Low 16bits)| - uint32_t rlen*/
#define REG_CTRL_STATE_WOFFS    (0x4)                       /**<> 0x4 state for reg read/write and packet 
                                |                                 |w state(8bits)|resv(8bits)|r state(8bits)|resv(8bits)| - uint32_t state */

#define REG_WDATA_WOFFS         (REG_CTRL_WOFFS + 8)        // |0 ~ 7 | 8 ~ 19 | 20 ~ 31|
#define REG_RDATA_WOFFS         (REG_WDATA_WOFFS + 12)

#define REG_WRITE_MAX_SIZE      (12 * 4)
#define REG_READ_MAX_SIZE       (12 * 4)

// thread1 for MCU
static int mcu_transfer_max12word(reg_shm_t *shm, void *buf, uint32_t len, uint32_t packet_len)
{
    uint32_t word = 0;
    uint32_t temp = 0;
    uint32_t ti = 0, timecount = 1000;
    uint32_t tfer_size = 0, tfered = 0;
    uint32_t *pbuf = (uint32_t*)buf;

    if (len > (12 * sizeof(uint32_t))) {
        log_error("failed\n");
        return -1;
    }

    // check state
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    if (((temp >> 24) != REG_WSTATE_RESV) && 
        ((temp >> 24) != REG_WSTATE_DEFAULT) &&
        ((temp >> 24) != REG_HPS_READ_DONE)) {
        log_error("failed\n");
        return -1;
    }

    // mcu write data
    for (uint32_t i = 0; i < 12; i++) {
        tfer_size = (len - tfered) < sizeof(uint32_t) ? (len - tfered) : sizeof(uint32_t);
        memcpy((void*)&word, pbuf + i, tfer_size);
        reg_shm_write_aword(shm, REG_WDATA_WOFFS + i, word);

        tfered += tfer_size;
        if (tfered >= len) {
            break;
        }
    }
    temp = packet_len << 16 | len;
    reg_shm_write_aword(shm, REG_CTRL_WLEN_WOFFS, temp);

    // mcu write data done
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    temp = (temp & 0x00ffffff) | (REG_MCU_WRITE_DONE << 24);
    reg_shm_write_aword(shm, REG_CTRL_STATE_WOFFS, temp);

    // check hps read done
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    while ((temp >> 24) != REG_HPS_READ_DONE)
    {
        usleep(1000);
        temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);

        // timeout
        if (++ti > timecount) {
            log_error("failed\n");
            return -1;
        }
    }

    return tfered;
}

// use 1024Bytes buffer to recv packet
int mcu_recv_packet(reg_shm_t *shm, void *buf, uint32_t size) 
{
    uint32_t word = 0;
    uint32_t temp = 0;
    uint32_t ti = 0, timecount = 1000;
    uint32_t tfer_size = 0, tfered = 0;
    uint32_t *pbuf = (uint32_t*)buf;
    uint32_t pk_len = 0, recv_len = 0, this_len = 0;

    // check state
    while (true)
    {
        temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
        if (((temp & 0x0000ff00) >> 8) == REG_HPS_WRITE_DONE) {
            temp = reg_shm_read_aword(shm, REG_CTRL_RLEN_WOFFS);
            pk_len = temp >> 16;
            this_len = temp & 0x0000ffff;

            for (uint32_t i = 0; i < 12; i++) {
                if ((this_len - tfered) < sizeof(uint32_t)) {
                    tfer_size = (this_len - tfered);
                    word = reg_shm_read_aword(shm, REG_RDATA_WOFFS + i);
                    memcpy((void *)pbuf, (void*)&word, tfer_size);
                }
                else {
                    tfer_size = sizeof(uint32_t);
                    *pbuf = reg_shm_read_aword(shm, REG_RDATA_WOFFS + i);
                }
                
                tfered += tfer_size;
                pbuf++;
                if (tfered >= this_len) {
                    break;
                }
            }

            // mcu read done
            temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
            temp = (temp & 0xffff00ff) | (REG_MCU_READ_DONE << 8);
            reg_shm_write_aword(shm, REG_CTRL_STATE_WOFFS, temp);

            recv_len += this_len;
            if (recv_len > size) {
                log_error("failed\n");
                return -1;
            }
            if (pk_len >= recv_len) {
                break;
            }
        }

        // timeout
        usleep(1000);
        if (++ti > timecount) {
            log_error("failed\n");
            return -1;
        }
    }

    return recv_len;
}

int mcu_send_packet(reg_shm_t *shm, uint32_t cmd, void *buf, uint32_t len) 
{
    static uint32_t seq = 0; 
    uint32_t xfer_size = 0, xfered = 0;
    void *pbuf = buf;
    int ret = 0;

    reg_shm_write_aword(shm, REG_CTRL_CMD_WOFFS, cmd);
    reg_shm_write_aword(shm, REG_CTRL_SEQ_WOFFS, seq);

    while (true)
    {
        xfer_size = (len - xfered) < REG_WRITE_MAX_SIZE ? (len - xfered) : REG_WRITE_MAX_SIZE;
        ret = mcu_transfer_max12word(shm, pbuf, xfer_size, len);
        if (ret < 0) {
            log_error("error\n");
            return -1;
        }
        xfered += xfer_size;
        pbuf += xfer_size;

        if (xfered >= len) {
            break;
        }
    }

    seq++;

    return xfered;
}

// thread2 for hps
int hps_recv_init(task_handle_t *hd, uint8_t *buf, uint32_t len)
{
    hd->sta = REG_TASK_STA_IDLE;
    hd->len = len;
    hd->buf = buf;

    hd->cmd = 0;
    hd->seq = 0;
    hd->pk_len = 0;
    hd->recv_len = 0;

    return 0;
}

int hps_recv_post(reg_shm_t *shm, task_handle_t *hd) 
{
    int ret = 0;
    uint8_t buf[1024] = { 0 };
    uint32_t len = 1024;

    if (hd->sta == REG_TASK_STA_READY) {
        switch (hd->cmd) { 
            case REG_CMD_INITED:
                // todo
                snprintf((char*)buf, len, "REG_CMD_INITED\n");
                log_info("REG_CMD_INITED\n");
                log_info("%s\n", (char *)hd->buf);
                hps_send_packet(shm, buf, strlen((char*)buf));
                break;
            case REG_CMD_SYNC_TIME:
                // todo
                log_info("REG_CMD_SYNC_TIME\n");
                break;
            case REG_CMD_SYNC_ATC_TIME:
                // todo
                log_info("REG_CMD_SYNC_ATC_TIME\n");
                break;
            default:
                // not support
                log_error("error\n");
                ret = -1;
                break; 
        }

        hd->sta = REG_TASK_STA_IDLE;  
    }

    return ret;
}

// use 1024Bytes buffer to recv packet
int hps_recv_packet_and_run(reg_shm_t *shm, task_handle_t *hd)
{
    uint32_t word = 0;
    uint32_t temp = 0;
    uint32_t tfer_size = 0, tfered = 0;
    uint32_t *pbuf = (uint32_t*)(hd->buf + hd->recv_len);

    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    if (((temp >> 24) == REG_MCU_WRITE_DONE)) {
        temp = reg_shm_read_aword(shm, REG_CTRL_WLEN_WOFFS);
        hd->pk_len = temp >> 16;
        hd->this_len = temp & 0x0000ffff;
        hd->cmd = reg_shm_read_aword(shm, REG_CTRL_CMD_WOFFS);
        hd->seq = reg_shm_read_aword(shm, REG_CTRL_SEQ_WOFFS);

        for (uint32_t i = 0; i < 12; i++) {
            if ((hd->this_len - tfered) < sizeof(uint32_t)) {
                tfer_size = (hd->this_len - tfered);
                word = reg_shm_read_aword(shm, REG_WDATA_WOFFS + i);
                memcpy((void *)pbuf, (void*)&word, tfer_size);
            }
            else {
                tfer_size = sizeof(uint32_t);
                *pbuf = reg_shm_read_aword(shm, REG_WDATA_WOFFS + i);
            }
            
            tfered += tfer_size;
            pbuf++;
            if (tfered >= hd->this_len) {
                break;
            }
        }

        hd->recv_len += hd->this_len;
        if (hd->recv_len >= hd->len) {
            log_error("error\n");
            return -1;
        }
        
        log_info("packet len %ld recv len %ld\n", hd->pk_len, hd->recv_len);
        if (hd->recv_len >= hd->pk_len) {
            hd->sta = REG_TASK_STA_READY;
            hd->recv_len = 0;
        }

        // hps read done
        temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
        temp = (temp & 0x00ffffff) | (REG_HPS_READ_DONE << 24);
        reg_shm_write_aword(shm, REG_CTRL_STATE_WOFFS, temp);

        // data packet post-processing
        hps_recv_post(shm, hd);
    }

    return 0;
}


static int hps_transfer_max12word(reg_shm_t *shm, void *buf, uint32_t len, uint32_t packet_len)
{
    uint32_t word = 0;
    uint32_t temp = 0;
    uint32_t ti = 0, timecount = 1000;
    uint32_t tfer_size = 0, tfered = 0;
    uint32_t *pbuf = (uint32_t*)buf;

    if (len > (12 * sizeof(uint32_t))) {
        log_error("failed\n");
        return -1;
    }

    // check state
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    if ((((temp & 0x0000ff00) >> 8) != REG_RSTATE_RESV) && 
        (((temp & 0x0000ff00) >> 8) != REG_RSTATE_DEFAULT) &&
        (((temp & 0x0000ff00) >> 8) != REG_MCU_READ_DONE)) {
        log_error("failed\n");
        return -1;
    }

    // hps write data
    for (uint32_t i = 0; i < 12; i++) {
        tfer_size = (len - tfered) < sizeof(uint32_t) ? (len - tfered) : sizeof(uint32_t);
        memcpy((void*)&word, pbuf + i, tfer_size);
        reg_shm_write_aword(shm, REG_RDATA_WOFFS + i, word);

        tfered += tfer_size;
        if (tfered >= len) {
            break;
        }
    }
    temp = packet_len << 16 | len;
    reg_shm_write_aword(shm, REG_CTRL_RLEN_WOFFS, temp);

    // hps write data done
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    temp = (temp & 0xffff00ff) | (REG_HPS_WRITE_DONE << 8);
    reg_shm_write_aword(shm, REG_CTRL_STATE_WOFFS, temp);

    // check mcu read done
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    while (((temp & 0x0000ff00) >> 8) != REG_MCU_READ_DONE)
    {
        usleep(1000);
        temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);

        // timeout
        if (++ti > timecount) {
            log_error("failed\n");
            return -1;
        }
    }

    return tfered;  
}

int hps_send_packet(reg_shm_t *shm, void *buf, uint32_t len) 
{
    uint32_t xfer_size = 0, xfered = 0;
    void *pbuf = buf;
    int ret = 0;

    while (true)
    {
        xfer_size = (len - xfered) < REG_READ_MAX_SIZE ? (len - xfered) : REG_READ_MAX_SIZE;
        ret = hps_transfer_max12word(shm, pbuf, xfer_size, xfer_size);
        if (ret < 0) {
            log_error("error\n");
            return -1;
        }
        xfered += xfer_size;
        pbuf += xfer_size;

        if (xfered >= len) {
            break;
        }
    }

    return xfered;
}
