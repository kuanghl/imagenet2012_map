### 原理作用

1. 使用一块共享寄存器，申请互斥锁用于进程间互斥
2. 每个寄存器只能一个word一个word的访问
3. 开辟的内存如下：

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