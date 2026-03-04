#include <time.h>
#include <unistd.h>

#include "log.h"
#include "reg_shm.h"
#include "reg_packet_master.h"

static int mcu_transfer_max12word(reg_shm_t *shm, void *buf, uint32_t len, uint32_t packet_len)
{
    uint32_t word = 0;
    uint32_t temp = 0;
    uint32_t ti = 0, timecount = 1000;
    uint32_t tfer_size = 0, tfered = 0;
    uint32_t *pbuf = (uint32_t*)buf;

    if (len > REG_WRITE_MAX_SIZE) {
        log_error("single transfer len %ld overflow %ld\n", len, REG_WRITE_MAX_SIZE);
        return -1;
    }

    // check state
    temp = reg_shm_read_aword(shm, REG_CTRL_STATE_WOFFS);
    if (((temp >> 24) != REG_WSTATE_RESV) && 
        ((temp >> 24) != REG_WSTATE_DEFAULT) &&
        ((temp >> 24) != REG_HPS_READ_DONE)) {
        log_error("REG state 0x%lx not allow to write\n", temp);
        return -1;
    }

    // mcu write data
    for (uint32_t i = 0; i < REG_WRITE_MAX_WORD; i++) {
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
            log_error("slave state 0x%lx is not done\n", temp);
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
    uint32_t tfer_size = 0, tfered;
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

            tfered = 0;
            for (uint32_t i = 0; i < REG_READ_MAX_WORD; i++) {
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
                log_error("the buffer size %ld too small then receive %ld\n", size, recv_len);
                return -1;
            }

            log_info("packet len %ld recv len %ld\n", pk_len, recv_len);
            if (recv_len >= pk_len) {
                break;
            }
        }

        // timeout
        usleep(1000);
        if (++ti > timecount) {
            log_error("recv timeout\n");
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

    if (len > REG_WPACKET_MAX_SIZE) {
        log_error("packet len %ld overflow %ld\n", len, REG_WPACKET_MAX_SIZE);
        return -1;
    }

    reg_shm_write_aword(shm, REG_CTRL_CMD_WOFFS, cmd);
    reg_shm_write_aword(shm, REG_CTRL_SEQ_WOFFS, seq);

    while (true)
    {
        xfer_size = (len - xfered) < REG_WRITE_MAX_SIZE ? (len - xfered) : REG_WRITE_MAX_SIZE;
        ret = mcu_transfer_max12word(shm, pbuf, xfer_size, len);
        if (ret < 0) {
            log_error("transfer failed %d\n", ret);
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