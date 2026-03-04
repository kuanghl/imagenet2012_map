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

    pthread_mutexattr_init(&shm->shm_mutexattr);
    pthread_mutexattr_setpshared(&shm->shm_mutexattr, PTHREAD_PROCESS_SHARED);
    pthread_mutexattr_setrobust(&shm->shm_mutexattr, PTHREAD_MUTEX_ROBUST);
    pthread_mutex_init(shm->shm_mutex, &shm->shm_mutexattr);

    return shm;
}

void reg_shm_del(reg_shm_t *shm, bool flag)
{
    shmdt(shm->shm_addr);
    if (flag) {
        shmctl(shm->shm_id, IPC_RMID, NULL);
    }
    pthread_mutex_destroy(shm->shm_mutex);
    pthread_mutexattr_destroy(&shm->shm_mutexattr);

    free(shm);
    shm = NULL;
}

void reg_shm_write_aword(reg_shm_t *shm, uint32_t woffs, uint32_t word)
{
    uint32_t *addr_temp = (uint32_t*)shm->shm_start + woffs;

    pthread_mutex_lock(shm->shm_mutex);
    *addr_temp = word;
    pthread_mutex_unlock(shm->shm_mutex);
}

uint32_t reg_shm_read_aword(reg_shm_t *shm, uint32_t woffs)
{
    uint32_t *addr_temp = (uint32_t*)shm->shm_start + woffs;
    uint32_t temp = 0;

    pthread_mutex_lock(shm->shm_mutex);
    temp = *addr_temp;
    pthread_mutex_unlock(shm->shm_mutex);

    return temp;
    
}

