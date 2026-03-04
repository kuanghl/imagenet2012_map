#ifndef __REG_PACKET_MASTER_H__
#define __REG_PACKET_MASTER_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C"{
#endif /*__cplusplus*/

int mcu_send_packet(reg_shm_t *shm, uint32_t cmd, void *buf, uint32_t len);
int mcu_recv_packet(reg_shm_t *shm, void *buf, uint32_t size);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif // !__REG_PACKET_MASTER_H__