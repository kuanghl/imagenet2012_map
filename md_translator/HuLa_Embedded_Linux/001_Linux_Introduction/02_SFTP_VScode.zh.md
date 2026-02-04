# 第 2 部分：在 VScode 上使用 SFTP 编辑源代码 💚

> 警告：本文由机器翻译生成，可能导致质量不佳或信息有误，请谨慎阅读！


## 步骤
- 打开 VScode 并转到扩展
- 搜索SFTP并安装，如下图

<img src="images/image-2.png" alt="SFTP" style="width:500px; height:auto;"/>

- 在 VScode 上打开文件夹
- 点击 ***Ctrl+Shift+p*** 并选择 ***SFTP配置***

<img src="images/image-3.png" alt="SFTP config" style="width:500px; height:auto;"/>

- 此时，我们会看到Vscode自动创建了一个文件 ***.vscode/sftp.json*** 内容如下图

<img src="images/image-4.png" alt="SFTP config 1" style="width:500px; height:auto;"/>

- 此时，我们将上面的内容替换如下：
```bash
{
     "name": "hulatho",
     "host": "192.168.30.113",
     "protocol": "sftp",
     "port": 22,
     "username": "hulatho",
     "remotePath": "/home/hulatho",
     "uploadOnSave": true,
     "openSsh": true,
     "password": "1",
     "useTempFile": false
}
```

- 上述参数解释：
+***姓名***：虚拟机名称
+***主持人***：虚拟机的IP地址
+***用户名***：用户名
+***远程路径***：我要链接到虚拟机的路径
+***密码***: 虚拟机密码

- 完成上述步骤后，工具栏上会显示一个额外的选项卡，sftp。 如果我们切换到该选项卡，我们可以看到该文件夹的内容 ***远程路径***

<img src="images/image-5.png" alt="SFTP content" style="width:500px; height:auto;"/>

### 从虚拟机获取代码到个人电脑
- 切换到 sftp 选项卡，当您想要检索任何文件夹时，只需右键单击该文件夹，然后单击 ***下载***
<img src="images/image-6.png" alt="SFTP download" style="width:500px; height:auto;"/>

### 将代码从个人计算机上传到虚拟机
- 切换到资源管理器选项卡，然后选择要推送哪个文件夹 ***远程路径*** 虚拟机的，我们只需右键单击该文件夹并选择 ***上传文件夹***

<img src="images/image-7.png" alt="SFTP upload" style="width:500px; height:auto;"/><br><br>

✅ 因此，在本文中我们了解了如何使用 VScode 检索源代码以及将源代码推送到虚拟机并编辑代码。 💯