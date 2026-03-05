波特率 115200
账号密码 admin admin
或者 sysadmin superuser
说明：
新老化板有5个slot，从左到右的slot丝印是slot9~slot5, 对应slot编号是1~5.

1. hpm（jed）格式cpld firmware升级
1.1 选择槽位
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x07 (1~5) 1
1.2 hpm升级
ipmitool -I lanplus -H ${IP} -U admin -P admin hpm upgrade SR3829_CPLD_U40_V17_2021_0717.hpm force -z 0x1600
1.3 取消槽位
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x07 (1~5) 0

Note：
查看槽位选择状态
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x06 (1~5)

2. Get Slot Device Present Status
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x00 (1~5)
返回值为01表示在位，00表示不在位。

3. Get Slot Power Status
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x01 (1~5)
返回值为00表示卡没有上电，01表示卡上电了。

4. Set Slot Power Status
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x02 (1~5) (0x00/0x01)------0X3代表3号槽位
其中：
0x00: Power off
0x01: Power on

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0xa0 0x02 1 0x01

Slot is not present SlotNumber 9


5. Get Fan Mode 
ipmitool -I lanplus -H ${IP} -U admin -P admin raw  0x3a 0x30  0x00              
(返回0/1，手动模式/自动模式 )

6. Set Fan Mode
ipmitool -I lanplus -H ${IP} -U admin -P admin raw   0x3a 0x30  0x01 (0x00/0x01)
其中：
0x00:MANUAL
0x01:AUTO

7. Set Fan PWM(风速调整，需要将模式设为MANUAL)
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0x30 0x02 (1~5) (20~100)
其中：
20~100：20%~100%的风速

ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0x30 0x02 (0xff) (20~100)
其中：
0xff: 设置所有风扇风速

8. Get  Fan PWM
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0x30 0x06 (1~5)         返回（0x14~0x64）20%到100%的风速

9. 升级BMC hpm文件
ipmitool -I lanplus -H ${IP} -U admin -P  admin hpm upgrade rom.hpm force -z 0x1800

10. 老化柜项目往EEPROM中设置BMC静态IP方法

考虑到当前老化柜项目BMC在升级或者重启，IP地址都会恢复到默认IP 192.168.254.1，
需要重新设置IP，新版BMC添加了在BMC启动时通过读取EEPROM中的IP地址来重新设置IP。
操作方法如下：
10.1 假设想让BMC一直使用固定IP 192.168.2.241，输入如下命令，并重启生效（注意，需要搭配新版本的BMC）
ipmitest raw 0x3a 0x10 2 0xa6 0 0 6 1 192 168 2 241

如果想检查设置的对不对，用如下命令查看：
ipmitest raw 0x3a 0x10 2 0xa6 5 0 6

10.2 不想让BMC使用EEPROM中的IP地址，输入如下命令，并重启生效（注意，需要搭配新版本的BMC）
ipmitest raw 0x3a 0x10 2 0xa6 0 0 6 0 

11.老化柜项目往EEPROM中设置MAC的方法
11.1 假设MAC地址是D4:7C:44:D5:42:F4，往EEPROM里面写的命令是：
ipmitest raw 0x3a 0x10 2 0xa6 0 0 0 0xD4 0x7C 0x44 0xD5 0x42 0xF4

11.2 如果想检查设置的MAC对不对，用如下命令查看：
ipmitest raw 0x3a 0x10 2 0xa6 6 0 0

12.适配不同类型网卡的命令(建议插卡或重启后都设置一次)：
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x08 (1~4)
1        Used for Mega 2.5 Card
2        Used for Mega 2.0 Card
3        Used for Fass Card
4        Used for guomi Card


1.风扇模式命令：    ipmitest raw 0x3a 0x30  0x00                            获取风扇模式，返回0/1（手动模式/自动模式） 
                                ipmitest raw 0x3a 0x30 0x01 0x00(mode)       设置风扇模式，此为设置为手动，0x01为自动

调整风速需要将模式设置为手动，才能生效
 2.风速命令：          ipmitest raw 0x3a 0x30  0x02  0x01(fan number 1~5) 0x32(pwm , 0x1)   

 3.适配不同类型网卡的命令(建议插卡或重启后都设置一次)：
ipmitool -I lanplus -H ${IP} -U admin -P admin raw 0x3a 0xa0 0x08 (1~4)
1        Used for Mega 2.5 Card
2        Used for Mega 2.0 Card
3        Used for Fass Card
4        Used for guomi Card


ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0xa0 0x02 1 0x00

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x06 1

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 1 0

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 3 30
ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 3 60


ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x00
ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 5 80


ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x01 0x00 
ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 5 80


IIC
i2c-test -b 0 --scan  (扫描）
i2c-test -b 0 -s 0x70 -w -d 0x02 （选通）
i2c-test -b 0 --scan（再次扫描完成看到更多的地址）
i2c-test -b 0 -s 0x53 -r -rc 1 （读EEPROOM)
i2c-test -b 0 -s 0x20 -r -rc 1 (CPLD 读取)
i2c-test  -b 0 -s 0x20 -rc 4 -d 0x02 (CPLD寄存器地址0x02读取4个字节)
i2c-test -b 0 -s 0x20 -w -d 0x60 0x00 0x00 0x00 0x13  (CPLD寄存器地址0x02写入4个字节即0x00000013)

访问2Bytes寄存器地址
访问带外EEPROM(0x53)方式，i2c-test会自增读写指针
i2c-test -b 0 -s 0x53 -w -d 0x00 0x00     # 设置读指针到地址 0x0000
i2c-test -b 0 -s 0x53 -r -rc 512          # 读取 512 字节数据
i2c-test -b 0 -s 0x53 -w -d 0x00 0x00 0xfc 0x76   # 向带外EEPROM位置 0x0000 写0xfc76数据
i2c-test -b 0 -s 0x53 -w -d 0x00 0x00     # 设置读指针到地址 0x0000
i2c-test -b 0 -s 0x53 -r -rc 512          # 读取 512 字节数据

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x00
ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0x30 0x02 5 80

ipmitool -I lanplus -H 127.0.0.1 -U admin -P admin raw 0x3a 0xa0 0x02 5 0x01
