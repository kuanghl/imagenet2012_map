#### imagenet概述

- 下载链接及imagenet分类

```sh
# 国内人工智能数据集：https://opendatalab.org.cn/OpenDataLab/ILSVRC2012_Images

训练集（ILSVRC2012_img_train.tar）：wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_train.tar --no-check-certificate

验证集（ILSVRC2012_img_val.tar）：wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate

标签映射文件（ILSVRC2012_devkit_t12.tar.gz）：wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_devkit_t12.tar.gz --no-check-certificate

测试集 （ILSVRC2012_img_test.tar）：wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_test.tar --no-check-certificate
```

#### imagenet标签及映射

1. 下载验证集及标签映射文件

```sh
mkdir imagenet2012
cd imagenet2012
wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate
wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_devkit_t12.tar.gz --no-check-certificate
```

2. 解压及文件格式

```sh
cd imagenet2012
tar xvf ILSVRC2012_img_val.tar -C ./val
tar -xzf ILSVRC2012_devkit_t12.tar.gz

[root@localhost ILSVRC2012_img_val]# tree -L 1
.
├── ILSVRC2012_devkit_t12
└── val
```

3. 分类排序

```sh
# 两个文件的关联关系:
# 验证集图片: ILSVRC2012_val_00000001.JPEG
# ↓
# 标签文件: 第1行 -> 154 (数字标签)
# ↓
# 元数据: ID=154 -> WNID=n01440764, 描述="tench, Tinca tinca"
# ↓
# 文件夹: n01440764 --> 存放对应图片ILSVRC2012_val_00000001.JPEG

# 利用Linux下WIND文件夹n01440764等等的默认排序方式是只按照数字部分大小的方式：按照从小到大排序
# 建立WIND文件夹的index与照片名称的关系，这个关系常常用于验证精度
cd imagenet2012
git clone git@github.com:kuanghl/imagenet2012_map.git
cd imagenet2012_map
python3 category_gen_labels.py > val_label.txt

# 目录结构
[root@localhost ILSVRC2012_img_val]# tree -L 1
.
├── ILSVRC2012_devkit_t12
├── imagenet2012_map
└── val
```

#### 昇腾芯片Ascend310P残差神经网络测试

1. [AI-P 加速模块驱动开发指南（EP场景）03](https://support.huawei.com/enterprise/zh/doc/EDOC1100445967/b1977c97?idPath=23710424|251366513|254884019|261408772|263024819): 驱动和固件安装，含npu-smi工具及LP固件验证部分。

2. [MindCluster Toolbax安装](https://www.hiascend.com/document/detail/zh/mindx-dl/600/toolbox/ascenddmi/toolboxug_0004.html)：工具箱安装，含ascend-dmi带宽/算力/功耗测试部分。

3. [CANN Toolkit安装](https://www.hiascend.com/document/detail/zh/canncommercial/601/devtools/auxiliarydevtool/atlasprofiling_16_0012.html)：CANN开发工具套件，含ais_bench及pytorch支持的CANN测试集。

4. [ais_bench推理工具使用指南](https://gitee.com/ascend/tools/tree/master/ais-bench_workload/tool/ais_bench#ais_bench%E6%8E%A8%E7%90%86%E5%B7%A5%E5%85%B7%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)：部署python相关的ais_bench工具。

5. [atc转换模型](https://www.hiascend.com/document/detail/zh/canncommercial/80RC2/devaids/auxiliarydevtool/atlasatc_16_0003.html)：使用atc工具将onnx或者其他网络模型转换成om格式的离线模型。

6. [昇腾Reset50推理指导](https://gitcode.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer)：结合imagenet2012验证昇腾芯片推理精度，基于ais_bench。

7. [A300I A2 推理卡适配测试指导书 01](https://support.huawei.com/enterprise/zh/doc/EDOC1100526512/33832688)：测试指导，含测试工具及测试方案等。

8. [ONNX网络模型转换成离线模型](https://www.hiascend.com/document/detail/zh/canncommercial/80RC2/devaids/auxiliarydevtool/atlasatc_16_0003.html)：以下推理参考ModelZoo中的Resnet50网络。

```sh
# 首先使用扫描昇腾设备与Host Link状态(良好在执行以下操作)
lspci -tv |grep d500

# 按照上述步骤，安1,2,3顺序执行

# 安装依赖检查
sudo yum install gcc g++ make kernel-devel dkms net-tools

# 使能昇腾环境
. /usr/local/Ascend/toolbox/set_env.sh
. /usr/local/Ascend/ascend-toolkit/set_env.sh

# clone resnet50相关仓库并安装依赖
git clone https://gitcode.com/Ascend/ModelZoo-PyTorch.git
cd ModelZoo-PyTorch/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer
cat README.md
pip3 install -r 
pip3 install attrs cython numpy==1.24.0 decorator sympy cffi pyyaml pathlib2 psutil protobuf==3.20 scipy requests absl-py
pip3 install cloudpickle jinja2 ml-dtypes tornado

# 从Pytorch官网获取权重文件：https://download.pytorch.org/models/resnet50-0676ba61.pth
# 将权重文件放置在ModelZoo-PyTorch/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer路径下
cd ModelZoo-PyTorch/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer
# resnet50-0676ba61.pth to resnet50_official.onnx
python3 pth2onnx.py ./resnet50-0676ba61.pth
# resnet50_official.onnx to resnet50_bs64.om
atc --model=resnet50_official.onnx --framework=5 --output=resnet50_bs64 --input_format=NCHW --input_shape="actual_input_1:64,3,224,224" --enable_small_channel=1 --log=error --soc_version=Ascend${chip_name} --insert_op_conf=aipp_resnet50.aippconfig

# 预处理imagenet2012
python3 imagenet_torch_preprocess.py resnet ./imagenet2012/val ./prep_dataset
chmod 750 prep_dataset/

# 执行推理
python3 -m ais_bench --model ./resnet50_bs64.om --input ./prep_dataset/ --output ./ --output_dirname result --outfmt TXT

# 比对精度结果
# 拷贝上面生成的val_label.txt文件到ModelZoo-PyTorch/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer目录
python3 vision_metric_ImageNet.py ./result ./val_label.txt ./ result.json
cat ./result.json   # 查看top-1和top-5的精度及打印的性能
```

结果如下：

```sh
# 性能参考：[INFO] throughput 1000*batchsize.mean(64)/NPU_compute_time.mean(13.476432624680307): 4749.03127425521

(.venv) [root@localhost Resnet50_Pytorch_Infer]# python3 -m ais_bench --model ./resnet50_bs64.om --input ./prep_dataset/ --output ./ --output_dirname result --outfmt TXT
[INFO] acl init success
[INFO] open device 0 success
[INFO] create new context
[INFO] load model ./resnet50_bs64.om success
[INFO] create model description success
[INFO] try get model batchsize:64
[INFO] output path:./result
[INFO] get filesperbatch files0 size:196608 tensor0size:12582912 filesperbatch:64 runcount:782
[INFO] warm up 1 done
Inference array Processing: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 782/782 [03:54<00:00,  3.33it/s]
[INFO] -----------------Performance Summary------------------
[INFO] NPU_compute_time (ms): min = 13.384765625, max = 13.640625, mean = 13.476432624680307, median = 13.4765625, percentile(99%) = 13.55142578125
[INFO] throughput 1000*batchsize.mean(64)/NPU_compute_time.mean(13.476432624680307): 4749.03127425521
[INFO] ------------------------------------------------------
[INFO] unload model success, model Id is 1
[INFO] end to reset device 0
[INFO] end to finalize acl

# 精度参考
(.venv) [root@localhost Resnet50_Pytorch_Infer]# python3 vision_metric_ImageNet.py ./result ./val_label.txt ./ result.json
(.venv) [root@localhost Resnet50_Pytorch_Infer]# cat ./result.json
{"title": "Overall statistical evaluation", "value": [{"key": "Number of images", "value": "50000"}, {"key": "Number of classes", "value": "1000"}, {"key": "Top1 accuracy", "value": "76.14%"}, {"key": "Top2 accuracy", "value": "86.0%"}, {"key": "Top3 accuracy", "value": "89.75%"}, {"key": "Top4 accuracy", "value": "91.63%"}, {"key": "Top5 accuracy", "value": "92.87%"}]}
```

#### .vscode用作为sempICP的vscode配置文件

- 含编译任务和单步调试方法
- 测试方法后续整合即可

####  centos源

- centos源提供给/etc/yum.repos.d/目录下

```sh 
mv /etc/yum.repos.d/ yum.repos.d_backup
mkdir /etc/yum.repos.d/
cp centos/CentOS-Base.repo /etc/yum.repos.d/
yum clean all     # 清除系统所有的yum缓存
yum repolist
yum grouplist
yum makecache     # 生成yum缓存
yum update
```