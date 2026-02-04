# Part 1: Install VMware Workstation, Ubuntu, MobaXterm

> Warning: This page is translated by MACHINE, which may lead to POOR QUALITY or INCORRECT INFORMATION, please read with CAUTION!


## 0. Discuss ways to get an Ubuntu environment
Currently I know 3 ways to get Ubuntu environment, in this section let's analyze 3 ways:
- Method 1: Use VirtualBox to install Ubuntu.
+ When installing Ubuntu, we must allocate disk space, RAM and core for the Ubuntu machine. That means we have to divide the computer power into 2 parts, part 1 is used for the computer and part 2 is used for Ubuntu.
+ Limited RAM, Core. If we leave more than 50% of RAM and Core, Ubuntu will warn us.

- Method 2: Use WSL (Windows Subsystem for Linux).
+ WSL is a Windows feature that allows you to run a Linux environment on a Windows computer without the need for a virtual machine or side-by-side installation.
+ Meaning it can share Core and Ram with the computer. This gives more flexibility in using the computer's power.
+ Share folder between WSL and Windows is /mnt/c
    
- Method 3: Use docker to create Ubuntu images and containers.
+ We can create multiple containers corresponding to multiple Ubuntus and can run multiple Ubuntus in parallel at the same time.
+ Strong when used on Host computers running Linux operating system.

## 1. Install VMware
- To be able to install an Ubuntu machine we need an environment to install it. There are many tools we can use such as Oracle VirtualBox, Vmware Workstation. Here I recommend using VMware Workstation.
- - Link video hướng dẫn: [Videos](https://youtu.be/6gKA3wUI3kc?si=bXfVC-MU2VtzT8dA) 
- - Link cài đặt: [VMware Workstation 17](https://drive.google.com/file/d/1yk2tW62MPs5OfgQMPB2oWdOHMVwouF3E/view?usp=drivesdk) 
- - Link key active VMware Workstation 17: [Active Key](https://drive.google.com/file/d/1JcVd4W4M2n6gEAGVWtc1Y5mbNNsa2lVn/view?usp=drivesdk) 

## 2. Install Ubuntu
- After we have VMware Workstation, we install a virtual machine on it. However, before installing we need to prepare an Ubuntu ISO file. You can always install Ubuntu version 22.04.5, however with the Myir IMX8MM board, it requires Ubuntu version 18.04.6 so I will attach both versions below. For articles that have not used the board (before the yocto build article), you can use version 22.04.5. In this repo, I will use ubuntu version 18.04.6 to avoid having to install multiple times.
- - Link video hướng dẫn: [Videos](https://youtu.be/6gKA3wUI3kc?si=bXfVC-MU2VtzT8dA) 
- - Link ubuntu 22.04.5: [Link](https://drive.google.com/file/d/1fyt4MCjwr0pUXEbYOspAW8q2czW_IteU/view?usp=drivesdk) 
- - Link ubuntu 18.04.6: [Link](https://drive.google.com/file/d/1puSIXdxvpS_CyCZzL6LaXu3PR8xfeamR/view?usp=drivesdk) 
- **NOTE**: Here I will put the username as ***hulatho***

## 3. Install MobaXterm
- Because the Ubuntu machine will take up a lot of RAM and is quite heavy, with a weak machine, using the terminal on VitualBox will be very laggy and difficult. For the above reason, I recommend using MobaXterm to ssh to VitualBox. In the future, we will use all interactions with VirtualBox on MobaXterm.
- - Link video hướng dẫn: [Videos](https://youtu.be/jmSgIrVIFAo?si=FPHLVD7_sQp94Fgd) 

### 3.1. How to ssh from MobaXterm to VirtualBox
- We do this on the terminal of the VirtualBox machine first:
```bash
sudo apt install openssh-server
sudo apt install net-tools
ifconfig
```
- After typing ifconfig, the terminal will display the Ubuntu machine's IP. We will copy it + username is ***hulatho*** to use MobaXterm to perform ssh to VirtualBox.


<img src="images/image.png" alt="IP Terminal" style="width:500px; height:auto;"/>


- We open MobaXterm and select 👉 Session 👉 SSH 👉 Enter IP 👉 Username then click OK.


<img src="images/image-1.png" alt="SSH MobaXterm" style="width:500px; height:auto;"/>


✅ So we have ssh connection from MobaXterm to our Ubuntu machine. 💯