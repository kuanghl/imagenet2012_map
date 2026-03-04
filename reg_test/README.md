### 原理作用

1. 使用一块共享寄存器，申请互斥锁用于进程间互斥
2. 每个寄存器只能一个word一个word的访问
3. MCU作为master，HPS作为slave
4. 开辟的内存如下：

```sh
32WORD CPLD寄存器空间可用 -- 0x20

0x0 -- 1word -- cmd
0x1 -- 1word -- seq
0x2 -- 1word -- wlen -- bit[0:15] 用于描述单笔mcu to hps传输的size，
                        bit[16:31] 用于描述整个mcu to hps的数据包大小(可由1次或者多次单笔传输合并而成)
0x3 -- 1word -- rlen -- bit[0:15] 用于描述单笔hps to mcu传输的size，
                        bit[16:31] 用于描述整个hps to mcu的数据包大小(可由1次或者多次单笔传输合并而成)
0x4 -- 1word -- state --    bit[0:7] resv暂时保留
                            bit[8:15] hps to mcu数据填充完毕和读取完毕状态，由hps写0x1表示数据准备到读缓冲完毕，mcu写0x2读取读缓冲完毕
                            bit[16:23] resv暂时保留
                            bit[24:31] mcu to hps数据填充完毕和读取完毕状态，由mcu写0x1表示数据准备到写缓冲完毕，hps写0x2读取写缓冲完毕
0x5 ~ 0x7 暂时保留
0x8 ~ 0x13 (8 ~ 19)用作写缓冲区
0x14 ~ 0x1f (20 ~ 31)用作读缓冲区
```

### 共享内存移除

```sh
ipcs
ipcrm -m shmid
```

### 运行方式

```sh
mkdir build && cd build
cmake ..
make -j8

# 终端1执行
./reg_hps_test

# 终端2执行
./reg_mcu_test

# 其中reg_mcu_test作为master，用于模拟主机访问一块共享寄存器空间，
# 控制和读写从机reg_hps_test
```

### 优化方向

```c
// 读写缓冲区合并共用，分时复用即可，缓冲区增大一倍
// 更改state为以下
typedef enum {
    REG_RWSTATE_RESV = 0x0, 
    REG_WDONE = 0x1,
    REG_WIDLE = 0x2,
    REG_RDONE = 0x3,
    REG_RIDLE = 0x4,
    REG_RWDEFAULT_RESV = 0xffffffff, 
} reg_rwstate_u;

// 状态变化如下
/**
 *   +---loop1--+        +--loop2--+   
 *   ↓          |        ↓         |     
 * WDONE --> WIDLE --> RDONE --> RIDLE
 *   ↑                             | 
 *   +-----------------------------+
 * 
 * 其中loop1完成MCU to HPS的多次发送组成一个整包
 * loop2完成HPS to MCU的多次发送组成一个整包
 * 
 * 封装接口以整包收发为基准即可   
 */
```

### i2c(SMBus)工具

1. BMC下的i2c-test工具

```sh

~ $ i2c-test
i2c-test
Usage: i2c-test <arguments>
Arguments:

*** I2C Functions ***
        -b <bus number>: Set the bus number for this transaction.  Defaults to 0
        -mm : Puts the device in Slave-Recieve mode and reponds to the message request
        -mmd : Puts the device in Slave-Recieve mode and show the receive data
        --sethost <addr>:       Set the host slave address
        --gethost:      Get the current host slave address for the specified bus
        --reset:        Reset the I2C controller
        --sysreset:     Emergency Reset the I2C controller Module
        --setspeed <speed>:     Set the bus speed
                        (Supported speed modes are: Standard - 0x64(100Kbits/sec), Fast - 0x190(400Kbits/sec)
        --scan:         Scan the I2C bus and show the slave addresses
                        that respond
        -s slave:       Communicate with the specified slave address in 7-bit format (in
                        hexadecimal)
                        Defaults to 0x5a
        -d <bytes>:     Send any number of data bytes to the specified slave.
                        Separate hexadecimal data bytes with spaces.  If this
                        flag is used, it must be the last one on the
                        command line.
                        EG: i2c-test -m 1 -d 0x00 0x01 0x02 0x03
        -rc count:      Read the specified number of bytes.  Defaults to 1
        -r:             Just read from the specified address, don't do a write.
        -w:             Just write to the specified address, don't do a read.
        -m mode:        Send and receive in the specified mode:
                        0: Write a data byte, then receive a data byte in
                           separate operations
                        1: Combined write and read using repeated start
                        Default mode is 0
        -f:             Repeat the specified test forever (stress test mode)
        -sbd:           Don't display any output unless there is an error
        --delay:        Specify the delay in milliseconds between tests in run forever mode
        --getrecinfo:   Get the current recovery info
```

2. linux(ubuntu)下的i2c-tools

```sh
sudo apt-get install python-smbus
sudo apt-get install i2c-tools

https://github.com/groeck/i2c-tools
https://linux.die.net/man/8/i2cdetect
https://linux.die.net/man/8/i2cdump
https://linux.die.net/man/8/i2cget
https://linux.die.net/man/8/i2cset
```