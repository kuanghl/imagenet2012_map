#include <time.h>
#include <unistd.h>

#include "log.h"
#include "reg_shm.h"
#include "reg_packet_slave.h"

static int hps_recv_post(reg_shm_t *shm, task_handle_t *hd);

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

        for (uint32_t i = 0; i < REG_WRITE_MAX_WORD; i++) {
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
            log_error("the buffer size %ld small then receive %ld\n", hd->len, hd->recv_len);
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

    if (len > REG_READ_MAX_SIZE) {
        log_error("single transfer len %ld overflow %ld\n", len, REG_READ_MAX_SIZE);
        return -1;
    }

    // check state
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    if ((((temp & 0x0000ff00) >> 8) != REG_RSTATE_RESV) && 
        (((temp & 0x0000ff00) >> 8) != REG_RSTATE_DEFAULT) &&
        (((temp & 0x0000ff00) >> 8) != REG_MCU_READ_DONE)) {
        log_error("reg state 0x%lx not allow to write\n", temp);
        return -1;
    }

    // hps write data
    for (uint32_t i = 0; i < REG_READ_MAX_WORD; i++) {
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
            log_error("master state 0x%lx is not done\n", temp);
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

    if (len > REG_WPACKET_MAX_SIZE) {
        log_error("packet len %ld overflow %ld\n", len, REG_WPACKET_MAX_SIZE);
        return -1;
    }

    while (true)
    {
        xfer_size = (len - xfered) < REG_READ_MAX_SIZE ? (len - xfered) : REG_READ_MAX_SIZE;
        ret = hps_transfer_max12word(shm, pbuf, xfer_size, len);
        if (ret < 0) {
            log_error("transfer failed %d\n", ret);
            return -1;
        }
        xfered += xfer_size;
        pbuf += xfer_size;

        // log_info("pbuf 0x%lx xfer_size 0x%lx\n", pbuf, xfer_size);
        if (xfered >= len) {
            break;
        }
    }

    return xfered;
}

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

static int hps_recv_post(reg_shm_t *shm, task_handle_t *hd) 
{
    int ret = 0;
    uint8_t buf[1024] = { 0 };
    uint32_t len = 1024;

    if (hd->sta == REG_TASK_STA_READY) {
        switch (hd->cmd) { 
            case REG_CMD_INITED:
                // todo
                snprintf((char*)buf, len, \
                "\r\nREG_CMD_INITED, this is a test for CPLD register, and mcu as master,\
                \r\nhps as slave. I am hps slave sending less than 1024Bytes packet is allowed\n");
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