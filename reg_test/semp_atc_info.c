#include <stdlib.h>
#include <stdint.h>

#include <time.h>
#include <sys/time.h> 

/** 
 * eg:
 * send:
 * 1. MCU write cmd + seq to CPLD register.
 * 2. MCU write data into write buffer.
 * 3. MCU write (write data) state = wdone.
 * 4. HPS read wdone.
 * 5. HPS read cmd + seq + data.
 * 6. HPS write (write data) state = widle.
 * 7. loop 2 --> 3 --> 4 --> 5 --> 6, until a cmd + data packet send done. 
 * recv:
 * 8. MCU wait HPS data.
 * 9. HPS write data into read buffer.
 * 10. HPS write (read data) state = rdone.
 * 11. MCU read rdone.
 * 12. MCU read data.
 * 13. MCU write (read date) state = ridle.
 * 14. loop 9 --> 10 --> 11 --> 12 --> 13，until a data packet recv done.
 * 
*/

// 4B
// CMD
typedef enum {
    REG_CMD_DEFUALT = 0,                /**> default value */
    REG_CMD_SYNC_SYSTIME,               /**> synchronize system time */
    REG_CMD_AGING_CONFIG,               /**> configure for aging test */
    REG_CMD_AGING_INIT,                 /**> initialize aging test(resv) */
    REG_CMD_AGING_RUN_STP1,             /**> run aging test step 1 */
    REG_CMD_AGING_RUN_STP2,             /**> run aging test step 2 */    
    REG_CMD_AGING_STOP,                 /**> stop aging test */
    REG_CMD_GET_AGING_SFP,              /**> get sfp aging test result */
    REG_CMD_GET_AGING_DDR,              /**> get ddr aging test result */
    REG_CMD_GET_AGING_EMMC,             /**> get emmc aging test result */
    REG_CMD_GET_AGING_TCAM,             /**> get tcam port aging test result */
    REG_CMD_GET_AGING_HPT,              /**> get high power aging test result */
    REG_CMD_GET_AGING_ALL,              /**> get all aging test result */
    REG_CMD_GET_PD_INFO,                /**> get hps hardware and software information */
    REG_CMD_ALL,
} reg_cmd_u; 

// 9 * 4B
// system time
// date
struct tm {
   int tm_sec;         /* 秒，范围从 0 到 59        */
   int tm_min;         /* 分，范围从 0 到 59        */
   int tm_hour;        /* 小时，范围从 0 到 23        */
   int tm_mday;        /* 一月中的第几天，范围从 1 到 31    */
   int tm_mon;         /* 月，范围从 0 到 11        */
   int tm_year;        /* 自 1900 年起的年数        */
   int tm_wday;        /* 一周中的第几天，范围从 0 到 6    */
   int tm_yday;        /* 一年中的第几天，范围从 0 到 365    */
   int tm_isdst;       /* 夏令时                */
};

// 2 * 8B long
// RTC time
// sudo hwclock
struct timeval {
  time_t       tv_sec;   /* Seconds */
  suseconds_t  tv_usec;  /* Microseconds */
};

typedef struct aging_config_s
{ 
    uint8_t enable;             /**> Bit[0] 0 - disable 1 - enable; Bit[1:7] resv */
    uint8_t n_hpt;              /**> the number of high power test model */
    uint32_t sfp_time;          /**> the time of sfp aging test to run */
    uint32_t ddr_time;          /**> the time of ddr aging test to run */
    uint32_t tcam_time;         /**> the time of tcam aging test to run */
    uint32_t emmc_time;         /**> the time of emmc aging test to run */
    uint32_t upload_time;       /**> Bit[0:15] for MES upload atc result time; Bit[16:31] for EEPROM upload atc result time */
} aging_config_t;

typedef struct ack_ncak_s
{
    uint8_t ack;    /** Bit[0] 0 - ack; 1 - nack */
} ack_nack_t;

// !TODO
typedef struct hps_info_s
{
    uint8_t flow;           /**> software flow state */
    uint32_t hw_state;      /**> hardware link state */
    // FRU
    // TCAM SN/PN
    // FPGA SN/PN/MAC
    // FPGA SFP PORT SN/PN/MAC
    // ...
} hps_info_t;

// !TODO
typedef struct sfp_ret_s
{
    uint8_t state;
    uint8_t err_flag;
    uint8_t port0;              /**> Bit */
    uint8_t port1;
    uint8_t link_10_times;      
} sfp_ret_t;

// !TODO
typedef struct ddr_ret_s
{
    uint8_t state;
    uint8_t err_flag;
    uint8_t ddr0;   /**> Bit */
    uint8_t ddr1;   
    uint8_t ddr2;
    uint8_t ddr3;
    uint8_t ddr4;
    uint8_t ddr5;
} ddr_ret_t;

// !TODO
typedef struct emmc_ret_s
{
    uint8_t state;
    uint8_t err_flag;             
    uint32_t check;             /**> check data */
} emmc_ret_t;

// !TODO
typedef struct tcam_ret_s
{
    uint8_t state;              /**> tcam state */
    uint8_t err_flag;              
    uint32_t check;
} tcam_ret_t;

// !TODO
typedef struct hpt_ret_s
{
    uint8_t state;
    uint8_t err_flag;
    uint8_t n;                  /**> the number of high power model enable */
} hpt_ret_t;


