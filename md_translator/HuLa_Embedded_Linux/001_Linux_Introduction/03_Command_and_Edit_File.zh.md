# 第 3 部分：常用命令行以及如何使用文件 💚

> 警告：本文由机器翻译生成，可能导致质量不佳或信息有误，请谨慎阅读！


## 1. 安装必要的工具
```bash
sudo apt install gcc
sudo apt install make
sudo apt install vim
sudo apt install tree
```

## 2. 如何使用文件
- 编辑文件，我们可以使用vim，nano...这里我们使用vim。
+ vim main.c: 创建main.c文件
+ 按 i，i 被插入然后你可以编辑代码。
+ 设置编号：显示行号。
+ dd：删除一行，按u返回。
+ Ship g：将鼠标指针移至文件末尾。
+ gg：将鼠标光标移至文件开头。
+ 退出文件：
+ 按 ESC 键
+": wq": 注意标志 "Hai chấm nhé"，wq 表示write 和quit。
+": q!": 注意标志 "Hai chấm nhé"，q！ 退出而不保存。

<img src="images/image-9.png" alt="hello" style="width:500px; height:auto;"/>        

## 3. 常用命令行
 ***输入 2 至 3 个字符，然后按 TAB 退出***
```bash
sudo apt-get install XXX: Install XXX
pwd: Xem đường dẫn hiện tại
tree
    sudo apt-get install tree​
    tree . : Hiển thị cấu trúc cây thư mục hiện tại
    tree –a: hiển thị cả file ẩn
    tree -a -L 1 .
ls: Xem trong thư mục hiện tại có những file gì
    ls –l: Hiển thị dưới dạng list.​
    ls –R: Hiển thị tất cả các tập trong thư mục con.​
    ls –a: Hiển thị các tệp ẩn.​
    ls –al: Hiển thị tất cả các thông tin chi tiết như quyền, kích thước, chủ sở hữu...
cd {Folder}: Đi tới thư mục
exit: Thoát khỏi.​
cd -: Toggle giữa 2 folder.​
touch tho.txt: Tạo file.​
vim tho.c: Mở file tho.c nếu đã tồn tại, nếu chưa tồn tại thì tạo mới file.​
rm –rf tho.c: Xóa file.​
rm –rf tho.c *.o: Xóa file tho.c và tất cả các file .o​
clear hoặc ctrl l: Xóa toàn màn hình.​
du –hs: ví dụ du –hs ThoNV/, kiểm tra dung lượng của folder.​
cat tho.c: xem nhanh file.​
less tho.c: file dài quá dùng mũi tên để lên xuống, thoát bấm q​
find < thư mục cần tìm> –name <tên file cần tìm> : tìm file​
lsblk: Kiểm tra ổ cứng.​
mkdir VanTho: Tạo folder VanTho.​
mkdir tho1 tho2 tho3: Tạo nhiều thư mục một lúc.​
cp: sao chép từu tệp sang một thư mục khác, ví dụ cp tho.img /folder_img​
    cp –r folder1 ./vantho/folder​
mv: di chuyển tệp, ví dụ mv file.txt /home/vantho/document​
    mv name new_name: Đổi tên tệp hoặc thư mục.​
ctrl c: Dừng và kết thức lệnh.​
ctrl z: Tạm dừng lệnh.​
scrot –s a.png: Chụp ảnh màn hình.​
Nếu vô tình bấm ctrl S thì terminal sẽ bị đóng băng khi đó chỉ cần bấm ctrl Q
Ta có thể chạy nhiều dòng lệnh bằng việc ngăn cách bởi dấu “;”, ví dụ lệnh 1; lệnh 2; lệnh 3 hoặc có thể dung && nếu mình muốn lệnh sau chạy khi lệnh trước đã thành công.​
Apt list --installed | grep chrome  : Apt list --installed sẽ xuất ra 1 list danh sách, lệnh grep để tìm từ chrome trong mớ đó​
```

✅ 所以在这篇文章中我们了解了如何使用命令行与文件交互以及经常使用的基本命令行。 💯