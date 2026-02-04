# 第 1 部分：安装 VMware Workstation、Ubuntu、MobaXterm

> 警告：本文由机器翻译生成，可能导致质量不佳或信息有误，请谨慎阅读！


## 0. 讨论获得 Ubuntu 环境的方法
目前我知道有3种获取Ubuntu环境的方法，本节我们来分析3种方法：
- 方法一：使用VirtualBox安装Ubuntu。
+ 安装Ubuntu时，我们必须为Ubuntu机器分配磁盘空间、RAM和核心。 这意味着我们必须将计算机电源分为两部分，部分 1 用于计算机，部分 2 用于 Ubuntu。
+ 有限的内存、核心。 如果我们留下超过 50% 的 RAM 和 Core，Ubuntu 就会警告我们。

- 方法 2：使用 WSL（适用于 Linux 的 Windows 子系统）。
+ WSL 是一项 Windows 功能，允许您在 Windows 计算机上运行 Linux 环境，而无需虚拟机或并行安装。
+ 意味着它可以与计算机共享 Core 和 Ram。 这为使用计算机的功能提供了更大的灵活性。
+ WSL 和 Windows 之间的共享文件夹是 /mnt/c
    
- 方法三：使用docker创建Ubuntu镜像和容器。
+ 我们可以创建多个容器对应多个Ubuntu，并且可以同时并行运行多个Ubuntu。
+ 在运行 Linux 操作系统的主机上使用时功能强大。

## 1. 安装VMware
- 为了能够安装 Ubuntu 机器，我们需要一个安装环境。 我们可以使用很多工具，例如 Oracle VirtualBox、Vmware Workstation。 这里我推荐使用VMware Workstation。
- - Link video hướng dẫn: [视频](https://youtu.be/6gKA3wUI3kc?si=bXfVC-MU2VtzT8dA) 
- - Link cài đặt: [VMware 工作站 17](https://drive.google.com/file/d/1yk2tW62MPs5OfgQMPB2oWdOHMVwouF3E/view?usp=drivesdk) 
- - Link key active VMware Workstation 17: [活动密钥](https://drive.google.com/file/d/1JcVd4W4M2n6gEAGVWtc1Y5mbNNsa2lVn/view?usp=drivesdk) 

## 2. 安装Ubuntu
- 有了VMware Workstation之后，我们在上面安装一个虚拟机。 不过，在安装之前我们需要准备一个Ubuntu ISO文件。 您始终可以安装 Ubuntu 版本 22.04.5，但是对于 Myir IMX8MM 板，它需要 Ubuntu 版本 18.04.6，因此我将在下面附上两个版本。 对于未使用该板的文章（在 yocto 构建文章之前），可以使用版本 22.04.5。 在此存储库中，我将使用 ubuntu 版本 18.04.6 以避免多次安装。
- - Link video hướng dẫn: [视频](https://youtu.be/6gKA3wUI3kc?si=bXfVC-MU2VtzT8dA) 
- - Link ubuntu 22.04.5: [链接](https://drive.google.com/file/d/1fyt4MCjwr0pUXEbYOspAW8q2czW_IteU/view?usp=drivesdk) 
- - Link ubuntu 18.04.6: [链接](https://drive.google.com/file/d/1puSIXdxvpS_CyCZzL6LaXu3PR8xfeamR/view?usp=drivesdk) 
- **注意** ：这里我将用户名设置为 ***呼拉托***

## 3. 安装 MobaXterm
- 由于 Ubuntu 机器会占用大量 RAM 并且相当重，对于较弱的机器，在 VitualBox 上使用终端会非常滞后且困难。出于上述原因，我建议使用 MobaXterm 来 ssh 到 VitualBox。 将来，我们将在 MobaXterm 上使用与 VirtualBox 的所有交互。
- - Link video hướng dẫn: [视频](https://youtu.be/jmSgIrVIFAo?si=FPHLVD7_sQp94Fgd) 

### 3.1.如何从 MobaXterm ssh 到 VirtualBox
- 我们首先在 VirtualBox 机器的终端上执行此操作：
```bash
sudo apt install openssh-server
sudo apt install net-tools
ifconfig
```
- 输入ifconfig后，终端将显示Ubuntu机器的IP。 我们将复制它+用户名是 ***呼拉托*** 使用 MobaXterm 执行 ssh 到 VirtualBox。


<img src="images/image.png" alt="IP Terminal" style="width:500px; height:auto;"/>


- 我们打开MobaXterm并选择👉会话👉SSH👉输入IP👉用户名然后单击确定。


<img src="images/image-1.png" alt="SSH MobaXterm" style="width:500px; height:auto;"/>


✅ 所以我们有从 MobaXterm 到我们的 Ubuntu 机器的 ssh 连接。 💯