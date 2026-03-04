#ifndef __REG_SHM_H__
#define __REG_SHM_H__

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>


/************************************************************************
 *                          Hardware                                    *
 ************************************************************************/

/**
 * hardware reg space as list: (word index)
 * 
 * ctrl: woffs = 0 ~ 4
 * size = 5 * 4
 * 
 * resv: woffs = 5 ~ 7
 * size = 3 * 4
 * 
 * data: woffs = 8 ~ 31
 * size = (32 - 8) * 4 = 24 * 4
 * - wdata: woffs = 8 ~ 19
 * - size = 12 * 4
 * - rdata: woffs = 20 ~ 31
 * - size = 12 * 4
 */
#define REG_MAX_WORD            32
#define REG_MAX_SIZE            (32 * 4)

/**
 * word index: | 0 ~ 7 |
 */
#define REG_CTRL_WOFFS          (0x0)

/**
 * word index: | 8 ~ 19 |
 */
#define REG_WDATA_WOFFS         (REG_CTRL_WOFFS + 8)

/**
 * word index: | 20 ~ 31 |
 */
#define REG_RDATA_WOFFS         (REG_WDATA_WOFFS + 12)

#define REG_WRITE_MAX_WORD      (12)
#define REG_READ_MAX_WORD       (12)
#define REG_WRITE_MAX_SIZE      (REG_WRITE_MAX_WORD * 4)
#define REG_READ_MAX_SIZE       (REG_READ_MAX_WORD * 4)
#define REG_WPACKET_MAX_SIZE    (1024)
#define REG_RPACKET_MAX_SIZE    (1024)

/**
 * < 0x0 cmd for the packet 
 * - uint32_t cmd 
 */
#define REG_CTRL_CMD_WOFFS      (0x0)

/** 
 * < 0x1 per packet index for sequence 
 * - uint32_t seq 
 */
#define REG_CTRL_SEQ_WOFFS      (0x1)

/** 
 * < 0x2 MCU write len for hps input 
 * |packet len(High 16bits)|transfer len(Low 16bits)| 
 * - uint32_t wlen 
 */   
#define REG_CTRL_WLEN_WOFFS     (0x2) 

/** 
 * < 0x3 MCU read len form hps output
 * |packet len(High 16bits)|transfer len(Low 16bits)| 
 * - uint32_t rlen
 */
#define REG_CTRL_RLEN_WOFFS     (0x3)

/** 
 * <> 0x4 state for reg read/write packet 
 * |w state(8bits)|resv(8bits)|r state(8bits)|resv(8bits)| 
 * - uint32_t state 
 */
#define REG_CTRL_STATE_WOFFS    (0x4)

typedef enum {
    REG_WSTATE_RESV = 0x0,               /* bit[24:31] - resv for default state, then only MCU can write */      
    REG_MCU_WRITE_DONE = 0x1,            /* bit[24:31] - MCU write REG done to set, then no option can do */
    REG_HPS_READ_DONE =  0x2,            /* bit[24:31] - HPS read REG done to set, then only MCU can write */
    REG_WSTATE_DEFAULT = 0xff            /* bit[24:31] - resv for default state, then only MCU can write */
} reg_wstate_u;

typedef enum {
    REG_RSTATE_RESV = 0x0,               /* bit[8:15] - resv for default state, then only HPS can write */      
    REG_HPS_WRITE_DONE = 0x1,            /* bit[8:15] - HPS write REG done to set, then no option can do */
    REG_MCU_READ_DONE =  0x2,            /* bit[8:15] - MCU read REG done to set, then only HPS can write */
    REG_RSTATE_DEFAULT = 0xff            /* bit[8:15] - resv for default state, only HPS can write */
} reg_rstate_u;

typedef enum {
    REG_CMD_EMPTY_TEST = 0,
    REG_CMD_INITED,
    REG_CMD_SYNC_TIME,
    REG_CMD_SYNC_ATC_TIME,
    USB_CMD_ALL,
} reg_cmd_u; 

/************************************************************************
 *                          Software                                    *
 ************************************************************************/

/**
 * shm memory for reg space simulate
 */
typedef struct reg_shm_s
{
    int shm_id;
    void *shm_addr;
    void *shm_start;
    pthread_mutexattr_t shm_mutexattr;
    pthread_mutex_t *shm_mutex;
} reg_shm_t;

reg_shm_t *reg_shm_create(void);
void reg_shm_del(reg_shm_t *shm, bool flag);

void reg_shm_write_aword(reg_shm_t *shm, uint32_t woffs, uint32_t word);
uint32_t reg_shm_read_aword(reg_shm_t *shm, uint32_t woffs);

#endif // !__REG_SHM_H__
