#ifndef __REG_SHM_H__
#define __REG_SHM_H__

#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>

typedef struct reg_shm_s
{
    int shm_id;
    void *shm_addr;
    void *shm_start;
    pthread_mutexattr_t shm_mutexattr;
    pthread_mutex_t *shm_mutex;
} reg_shm_t;

reg_shm_t *reg_shm_create(bool flag);
void reg_shm_del(reg_shm_t *shm, bool flag);

void reg_shm_write_aword(reg_shm_t *shm, uint32_t woffs, uint32_t word);
uint32_t reg_shm_read_aword(reg_shm_t *shm, uint32_t woffs);

#endif // !__REG_SHM_H__
