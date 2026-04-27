#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdlib.h>

#include "log.h"
#include "reg_shm.h"

#define REG_SHM_NAME        "/tmp"
#define REG_SHM_NAME_ID     0
#define REG_SHM_LOCK_SIZE   100
#define REG_SHM_MAX_SIZE    (REG_SHM_LOCK_SIZE + REG_MAX_SIZE)

reg_shm_t *reg_shm_create(void)
{
    key_t key;
    reg_shm_t *shm = NULL;
    struct shmid_ds info;

    shm = calloc(1, sizeof(reg_shm_t));
    if (shm == NULL) {
        log_error("failed\n");
        return NULL;
    }

    key = ftok(REG_SHM_NAME, REG_SHM_NAME_ID);
    if (key < 0) {
        log_error("error\n");
        free(shm);
        return NULL;
    }

    shm->shm_id = shmget(key, REG_SHM_MAX_SIZE, 0666 | IPC_CREAT);
    if (shm->shm_id < 0) {
        log_error("error\n");
        free(shm);
        return NULL;
    }

    shm->shm_addr = shmat(shm->shm_id, NULL, 0);
    if (shm->shm_addr == NULL) {
        log_error("error\n");
        free(shm);
        return NULL;
    }

    shm->shm_mutex = (pthread_mutex_t *)shm->shm_addr;
    shm->shm_start = shm->shm_addr + REG_SHM_LOCK_SIZE;
    memset(shm->shm_start, 0, (REG_SHM_MAX_SIZE - REG_SHM_LOCK_SIZE));

    pthread_mutexattr_init(&shm->attr);
    pthread_mutexattr_setpshared(&shm->attr, PTHREAD_PROCESS_SHARED);
    pthread_mutexattr_setrobust(&shm->attr, PTHREAD_MUTEX_ROBUST);
    if (shmctl(shm->shm_id, IPC_STAT, &info) != -1) {
        if (info.shm_nattch == 1) {
            // log_debug("id=%d, shm_id=%d, shm_nattch=0x%x\n", id, shm->shm_id, info.shm_nattch);
            pthread_mutex_init(shm->shm_mutex, &shm->attr);
        }
    }

    return shm;
}

void reg_shm_del(reg_shm_t *shm, bool flag)
{
    shmdt(shm->shm_addr);
    if (flag) {
        pthread_mutex_destroy(shm->shm_mutex);
        shmctl(shm->shm_id, IPC_RMID, NULL);
    }
    pthread_mutexattr_destroy(&shm->attr);

    free(shm);
    shm = NULL;
}

void reg_shm_write_aword(reg_shm_t *shm, uint32_t woffs, uint32_t word)
{
    uint32_t *addr_temp = (uint32_t*)shm->shm_start + woffs;

    // 添加分支操作
    // AliFPGA3.0卡共享寄存器0x90~0x9F和0xF0~0xFF

    pthread_mutex_lock(shm->shm_mutex);
    *addr_temp = word;
    pthread_mutex_unlock(shm->shm_mutex);
}

uint32_t reg_shm_read_aword(reg_shm_t *shm, uint32_t woffs)
{
    uint32_t *addr_temp = (uint32_t*)shm->shm_start + woffs;
    uint32_t temp = 0;

    // 添加分支操作
    // AliFPGA3.0卡共享寄存器0x90~0x9F和0xF0~0xFF

    pthread_mutex_lock(shm->shm_mutex);
    temp = *addr_temp;
    pthread_mutex_unlock(shm->shm_mutex);

    return temp;
    
}

