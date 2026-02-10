A simple hello world kernel module, that can be build with cmake.
Utilize Kbuild through cmake, and do it in a build directory.


Usage:
1) clone it.
2) create a folder: mkdir build
3) navigate into build: cd build
4) run cmake: cmake ../
5) build it: make



Expected behavior: 

cmake ../ shall do:

```
$ cmake ../
-- The C compiler identification is GNU 9.2.1
-- Check for working C compiler: /usr/lib64/ccache/cc
-- Check for working C compiler: /usr/lib64/ccache/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Kernel release: 5.3.13-300.fc31.x86_64
-- Kernel headers: /usr/src/kernels/5.3.13-300.fc31.x86_64
-- Configuring done
-- Generating done
-- Build files have been written to: /home/ca/Code/cmake-kernel-module/build
```

make shall do:

```
make
Scanning dependencies of target driver
[100%] Generating hello.ko
[100%] Built target driver
```

insmod/rmmod do:

```
# 0 (KERN_EMERG): 紧急情况，系统不可用
# 1 (KERN_ALERT): 需要立即采取措施
# 2 (KERN_CRIT): 严重情况
# 3 (KERN_ERR): 错误
# 4 (KERN_WARNING): 警告
# 5 (KERN_NOTICE): 正常但需要注意的情况
# 6 (KERN_INFO): 信息
# 7 (KERN_DEBUG): 调试消息

# console_loglevel
# default_message_loglevel
# minimum_console_loglevel
# default_console_loglevel

cat /proc/sys/kernel/printk
sudo sh -c "echo "7 4 1 7" > /proc/sys/kernel/printk"
```

Among others the hello.ko is now present. 


Thoughts and comments are welcome. 
