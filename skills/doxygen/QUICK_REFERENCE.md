# Doxygen Tools 快速参考

## 📋 目录

- [环境准备](#环境准备)
- [安装工具到项目](#安装工具到项目)
- [生成文档](#生成文档)
  - [方式 1: Doxygen 原生 HTML（传统）](#方式-1-doxygen-原生html传统)
  - [方式 2: Sphinx + Breathe（推荐，现代化）](#方式-2-sphinx--breathe推荐现代化)
- [常用选项](#常用选项)
- [文件位置](#文件位置)
- [故障排除](#故障排除)
- [完整工作流](#完整工作流)
- [多项目配置管理](#多项目配置管理)
- [对比](#对比)

## 环境准备

首次使用前，需要设置 Python 虚拟环境并安装依赖。

### 步骤 1: 创建虚拟环境

```bash
# 在项目根目录下执行
cd /path/to/your/project
python3 -m venv .venv
```

### 步骤 2: 激活虚拟环境

**Linux/MacOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 步骤 3: 安装依赖

```bash
sudo apt-get install graphviz doxygen # 注意版本需要达到1.12.0以上，先手动编译安装，sudo apt-get remove doxygen卸载旧版本，然后再安装，则是最新版本，依赖也在
# git clone -b Release_1_12_0 https://github.com/doxygen/doxygen.git
cd doxygen
mkdir build
cd build
cmake -G "Unix Makefiles" ..
make -j16
sudo make install
doxygen -V

pip install sphinx breathe sphinx-rtd-theme
```

### 验证安装

```bash
# 检查 Python 路径（应该指向 .venv）
which python  # Linux/MacOS
where python  # Windows

# 检查已安装的包
pip list | grep -E "sphinx|breathe"

# 预期输出：
# breathe              x.x.x
# sphinx               x.x.x
# sphinx-rtd-theme     x.x.x
```

**注意**: 每次打开新终端时，都需要重新激活虚拟环境。

---

## 安装工具到项目

将 doxygen_tools.py、Doxyfile 和 .assets 复制到目标项目。

### 基本用法（使用默认 Doxyfile）

```bash
# 从技能目录安装到项目根目录
cd /path/to/your/project
python3 .agents/skills/doxygen/doxygen_tools.py install .
```

**效果**:
- 复制 `Doxyfile` → `./Doxyfile`
- 复制 `.assets/` → `./.assets/`
- 复制 `doxygen_tools.py` → `./doxygen_tools.py`

### 使用自定义 Doxyfile（如 Doxyfile.sempICP）

```bash
# 使用 --name 参数指定 Doxyfile 变体
python3 .agents/skills/doxygen/doxygen_tools.py install . --name sempICP
```

**效果**:
- 复制 `Doxyfile.sempICP` → `./Doxyfile` ⭐
- 复制 `.assets/` → `./.assets/`
- 复制 `doxygen_tools.py` → `./doxygen_tools.py`

**说明**: 源文件是 `Doxyfile.sempICP`，但安装后重命名为 `Doxyfile`。

### 查看帮助

```bash
python3 .agents/skills/doxygen/doxygen_tools.py install --help
```

**输出**:
```
usage: doxygen_tools.py install [-h] [--name NAME] dest_dir

positional arguments:
  dest_dir     Destination directory

options:
  -h, --help   show this help message and exit
  --name NAME  Doxyfile name to install (default: 'Doxyfile').
               Use '--name sempICP' to install 'Doxyfile.sempICP' as 'Doxyfile'
```

### 多项目配置示例

假设你有多个项目需要不同的 Doxygen 配置：

```bash
# sempICP 项目（使用专用配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/sempICP --name sempICP

# cmake_doc 项目（使用默认配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/cmake_doc

# 其他项目（使用默认配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/other_project
```

---

## 生成文档

### 方式 1: Doxygen 原生 HTML（传统）

适合快速预览，不需要额外依赖。

#### 步骤 1: 构建文档

```bash
# 确保已在项目根目录
cd /path/to/your/project

# 运行 Doxygen
doxygen Doxyfile

# 来源：https://github.com/jothepro/doxygen-awesome-css.git
# 缺少这dynsections.js 和jquery.js文件，需要手动从源代码拷贝
```

**或使用工具脚本**:
```bash
python3 doxygen_tools.py build
```

#### 步骤 2: 预览文档

```bash
# 启动本地服务器（端口 3001）
python3 doxygen_tools.py serve --open
```

**参数说明**:
- `--port`: 自定义端口号（默认 3001）
- `--open`: 自动打开浏览器

**示例**:
```bash
# 使用自定义端口
python3 doxygen_tools.py serve --port 8080

# 不自动打开浏览器
python3 doxygen_tools.py serve
```

#### 访问文档

浏览器会自动打开：`http://localhost:3001`

手动访问：在浏览器中输入 `http://localhost:3001`

---

### 方式 2: Sphinx + Breathe（推荐，现代化）

提供更现代化的界面、强大的搜索功能和更好的导航体验。

#### 前置条件

确保已完成 [环境准备](#环境准备) 中的步骤。

#### 步骤 1: 生成 Doxygen XML

Sphinx 需要 Doxygen 生成的 XML 文件作为输入。

```bash
# 确保 Doxyfile 中启用了 XML 生成
grep GENERATE_XML Doxyfile
# 应该显示: GENERATE_XML = YES

# 生成 XML
doxygen Doxyfile
```

**或使用工具脚本**:
```bash
python3 doxygen_tools.py build
```

**验证 XML 生成**:
```bash
ls -la docs/doxygen/xml/
# 应该看到 index.xml 和其他 XML 文件
```

#### 步骤 2: 构建 Sphinx 文档

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # Linux/MacOS
# .venv\Scripts\activate   # Windows

# 构建 Sphinx 文档
python3 doxygen_tools.py sphinx-build
```

**输出示例**:
```
Found Doxygen XML at: /path/to/project/docs/doxygen/xml
Building Sphinx documentation...
Source: /path/to/project/.agents/skills/doxygen/.assets/sphinx/source
Output: /path/to/project/docs/doxygen/sphinx
Running Sphinx v7.2.6
...
Sphinx build complete! Output: /path/to/project/docs/doxygen/sphinx
```

#### 步骤 3: 预览文档

```bash
# 启动本地服务器（端口 3002）
python3 doxygen_tools.py sphinx-serve --open
```

**参数说明**:
- `--port`: 自定义端口号（默认 3002）
- `--open`: 自动打开浏览器

**示例**:
```bash
# 使用自定义端口
python3 doxygen_tools.py sphinx-serve --port 8080

# 不自动打开浏览器
python3 doxygen_tools.py sphinx-serve
```

#### 访问文档

浏览器会自动打开：`http://localhost:3002`

手动访问：在浏览器中输入 `http://localhost:3002`

---

## 常用选项

### 查看所有命令

```bash
python3 doxygen_tools.py --help
```

**输出**:
```
usage: doxygen_tools.py [-h] {install,build,serve,sphinx-build,sphinx-serve,sphinx-gen-structure} ...

Doxygen Tools - manage Doxygen documentation generation.

positional arguments:
  {install,build,serve,sphinx-build,sphinx-serve,sphinx-gen-structure}
    install             Install Doxyfile, .assets and this script to destination
    build               Run doxygen using Doxyfile in current directory
    serve               Build and serve generated HTML documentation
    sphinx-build        Build Sphinx documentation from Doxygen XML
    sphinx-serve        Build and serve Sphinx documentation
    sphinx-gen-structure Generate hierarchical directory structure from Doxygen XML
```

### 自定义端口

```bash
# Doxygen HTML 服务（默认 3001）
python3 doxygen_tools.py serve --port 8080

# Sphinx 服务（默认 3002）
python3 doxygen_tools.py sphinx-serve --port 9000
```

### 自动打开浏览器

```bash
# 自动打开浏览器
python3 doxygen_tools.py sphinx-serve --open

# 不自动打开浏览器（默认行为）
python3 doxygen_tools.py sphinx-serve
```

### 查看特定命令的帮助

```bash
python3 doxygen_tools.py install --help
python3 doxygen_tools.py serve --help
python3 doxygen_tools.py sphinx-serve --help
python3 doxygen_tools.py sphinx-gen-structure --help
```

## 文件位置

### 关键目录结构

```
project_root/
├── Doxyfile                    # Doxygen 配置文件
├── doxygen_tools.py            # 工具脚本
├── .assets/                    # Sphinx 资源和模板
│   └── sphinx/
│       └── source/
│           ├── conf.py         # Sphinx 配置文件
│           ├── index.rst       # Sphinx 主文档
│           └── ...             # 其他 RST 文件
├── docs/
│   └── doxygen/
│       ├── xml/                # Doxygen XML 输出（中间格式）
│       │   ├── index.xml
│       │   └── *.xml
│       ├── html/               # Doxygen HTML 输出（方式 1）
│       │   └── index.html
│       └── sphinx/             # Sphinx HTML 输出（方式 2）⭐
│           └── index.html
└── .venv/                      # Python 虚拟环境
    └── bin/
        └── activate
```

### 路径说明

| 类型 | 路径 | 说明 |
|------|------|------|
| **Doxygen XML** | `docs/doxygen/xml/` | Doxygen 生成的 XML 中间文件 |
| **Doxygen HTML** | `docs/doxygen/html/` | Doxygen 原生 HTML 文档 |
| **Sphinx 源** | `.agents/skills/doxygen/.assets/sphinx/source/` | Sphinx RST 源文件 |
| **Sphinx 输出** | `docs/doxygen/sphinx/` | Sphinx 生成的 HTML 文档 ⭐ |
| **配置文件** | `.agents/skills/doxygen/.assets/sphinx/source/conf.py` | Sphinx 配置 |
| **Doxyfile** | `Doxyfile` 或 `Doxyfile.*` | Doxygen 配置 |

### 查找文件

```bash
# 查找 Doxygen XML
find docs/doxygen/xml -name "index.xml"

# 查找 Sphinx 输出
find docs/doxygen/sphinx -name "index.html"

# 查看 Sphinx 配置
cat .agents/skills/doxygen/.assets/sphinx/source/conf.py
```

## 故障排除

### 问题 1: 找不到 sphinx/breathe 模块

**错误信息**:
```
ModuleNotFoundError: No module named 'sphinx'
ModuleNotFoundError: No module named 'breathe'
```

**原因**: 未激活虚拟环境或未安装依赖

**解决方案**:
```bash
# 1. 激活虚拟环境
source .venv/bin/activate  # Linux/MacOS
# .venv\Scripts\activate   # Windows

# 2. 验证 Python 路径
which python  # 应该显示 .venv/bin/python

# 3. 安装依赖
pip install sphinx breathe sphinx-rtd-theme

# 4. 验证安装
pip list | grep -E "sphinx|breathe"
```

---

### 问题 2: 找不到 Doxygen XML

**错误信息**:
```
Error: Doxygen XML output directory not found: /path/to/docs/doxygen/xml
Please run 'doxygen Doxyfile' first to generate XML documentation.
```

**原因**: 未生成 Doxygen XML 或 Doxyfile 配置不正确

**解决方案**:
```bash
# 1. 检查 Doxyfile 配置
grep GENERATE_XML Doxyfile
# 应该显示: GENERATE_XML = YES

# 2. 如果未启用，编辑 Doxyfile
# 找到 GENERATE_XML 行，修改为:
# GENERATE_XML = YES

# 3. 重新生成 Doxygen 文档
doxygen Doxyfile

# 4. 验证 XML 已生成
ls -la docs/doxygen/xml/index.xml

# 5. 重新构建 Sphinx
python3 doxygen_tools.py sphinx-build
```

---

### 问题 3: 端口被占用

**错误信息**:
```
Error: Port 3002 is already in use. Please choose a different port using --port.
```

**原因**: 另一个进程正在使用该端口

**解决方案**:
```bash
# 方案 1: 使用其他端口
python3 doxygen_tools.py sphinx-serve --port 8080

# 方案 2: 查找并终止占用端口的进程
lsof -i :3002  # 查看占用端口的进程
kill <PID>     # 终止进程

# 方案 3: 检查是否有其他 sphinx-serve 进程运行
ps aux | grep sphinx-serve
kill <PID>
```

---

### 问题 4: 未激活虚拟环境

**症状**: 
- `python3` 命令使用的是系统 Python 而非虚拟环境
- 导入模块失败

**检查方法**:
```bash
# 检查 Python 路径
which python  # Linux/MacOS
where python  # Windows

# 预期输出（已激活）:
# /path/to/project/.venv/bin/python

# 实际输出（未激活）:
# /usr/bin/python3
```

**解决方案**:
```bash
# 重新激活虚拟环境
source .venv/bin/activate  # Linux/MacOS
# .venv\Scripts\activate   # Windows

# 验证
which python
# 应该显示: /path/to/project/.venv/bin/python
```

**提示**: 可以将激活命令添加到 shell 配置文件中自动激活：
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'cd /path/to/project && source .venv/bin/activate' >> ~/.bashrc
source ~/.bashrc
```

---

### 问题 5: Doxyfile 不存在

**错误信息**:
```
Error: Doxyfile not found in current directory.
```

**原因**: 未在包含 Doxyfile 的目录中执行命令

**解决方案**:
```bash
# 1. 确认当前目录
cd /path/to/your/project
ls -la Doxyfile

# 2. 如果 Doxyfile 不存在，需要先安装
python3 .agents/skills/doxygen/doxygen_tools.py install .

# 3. 或者使用完整路径
doxygen /path/to/Doxyfile
```

---

### 问题 6: 指定的 Doxyfile 不存在（使用 --name 参数时）

**警告信息**:
```
Warning: /path/to/Doxyfile.xxx not found, falling back to Doxyfile
```

**原因**: 使用 `--name` 参数指定的 Doxyfile 变体不存在

**解决方案**:
```bash
# 1. 查看可用的 Doxyfile 文件
ls -la .agents/skills/doxygen/Doxyfile*

# 2. 确认文件名拼写正确
# 例如：Doxyfile.sempICP 而不是 Doxyfile.SempICP

# 3. 如果文件确实不存在，创建它或改用默认 Doxyfile
python3 doxygen_tools.py install .  # 不使用 --name 参数
```

---

### 问题 7: Sphinx 构建警告

**常见警告**:
```
WARNING: doxygenfunction: Cannot find function "xxx"
WARNING: Duplicate C++ declaration
WARNING: toctree contains reference to nonexisting document
```

**解决方案**:

这些警告通常不影响最终文档质量，但如果想消除：

```bash
# 1. 清理旧的生成文件
rm -rf docs/doxygen/xml docs/doxygen/sphinx

# 2. 重新生成 Doxygen XML
doxygen Doxyfile

# 3. 重新构建 Sphinx
python3 doxygen_tools.py sphinx-build

# 4. 如果仍有警告，查看详细日志
python3 doxygen_tools.py sphinx-build 2>&1 | tee build.log
```

更多详细信息请参考：[SPHINX_BUILD_FIX.md](./SPHINX_BUILD_FIX.md)

## 完整工作流

### 首次使用（从零开始）

```bash
# 1. 进入项目目录
cd /path/to/your/project

# 2. 安装工具到项目
python3 .agents/skills/doxygen/doxygen_tools.py install .
# 或使用自定义 Doxyfile
python3 .agents/skills/doxygen/doxygen_tools.py install . --name sempICP

# 3. 设置 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# .venv\Scripts\activate   # Windows

# 4. 安装依赖
pip install sphinx breathe sphinx-rtd-theme

# 5. 生成 Doxygen XML
doxygen Doxyfile

# 6. 构建 Sphinx 文档
python3 doxygen_tools.py sphinx-build

# 7. 预览文档
python3 doxygen_tools.py sphinx-serve --open
```

### 日常使用（已有环境）

```bash
# 1. 进入项目目录
cd /path/to/your/project

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 更新代码后，重新生成文档
doxygen Doxyfile
python3 doxygen_tools.py sphinx-build

# 4. 预览文档
python3 doxygen_tools.py sphinx-serve --open
```

### 自动化脚本示例

创建一个快捷脚本 `update-docs.sh`:

```bash
#!/bin/bash
# update-docs.sh - 快速更新文档

set -e  # 遇到错误立即退出

# 激活虚拟环境
source .venv/bin/activate

# 生成 Doxygen XML
echo "Generating Doxygen XML..."
doxygen Doxyfile

# 构建 Sphinx 文档
echo "Building Sphinx documentation..."
python3 doxygen_tools.py sphinx-build

echo "Documentation updated successfully!"
echo "Run 'python3 doxygen_tools.py sphinx-serve --open' to view."
```

**使用方法**:
```bash
chmod +x update-docs.sh
./update-docs.sh
```

---

## 多项目配置管理

如果你有多个项目需要不同的 Doxygen 配置，可以使用 `--name` 参数。

### 场景 1: 为不同项目使用不同配置

```bash
# sempICP 项目（使用专用配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/sempICP --name sempICP

# cmake_doc 项目（使用默认配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/cmake_doc

# 其他项目（使用默认配置）
python3 .agents/skills/doxygen/doxygen_tools.py install /path/to/other_project
```

### 场景 2: A/B 测试不同配置

```bash
# 测试实验性配置
python3 .agents/skills/doxygen/doxygen_tools.py install /tmp/test_exp --name experimental
cd /tmp/test_exp
python3 doxygen_tools.py build
python3 doxygen_tools.py sphinx-build
python3 doxygen_tools.py sphinx-serve --port 8080

# 测试稳定配置
python3 .agents/skills/doxygen/doxygen_tools.py install /tmp/test_stable --name stable
cd /tmp/test_stable
python3 doxygen_tools.py build
python3 doxygen_tools.py sphinx-build
python3 doxygen_tools.py sphinx-serve --port 9000

# 在浏览器中比较两个版本
```

### 可用的 Doxyfile 变体

查看 `.agents/skills/doxygen/` 目录中的所有 Doxyfile：

```bash
ls -la .agents/skills/doxygen/Doxyfile*
```

**示例输出**:
```
-rw-r--r-- 1 user user 129851 May  9 10:00 Doxyfile
-rw-r--r-- 1 user user 135420 May  9 10:00 Doxyfile.sempICP
-rw-r--r-- 1 user user 128900 May  9 10:00 Doxyfile.minimal
```

### 命名规范

**推荐**:
- `Doxyfile.sempICP` - 项目专用配置
- `Doxyfile.experimental` - 实验性配置
- `Doxyfile.minimal` - 最小化配置
- `Doxyfile.full` - 完整配置

**不推荐**:
- `Doxyfile.v1` - 版本号不明确
- `Doxyfile.new` - 语义不清
- `Doxyfile.backup` - 不应作为正式配置

更多详细信息请参考：[INSTALL_NAME_PARAMETER.md](./INSTALL_NAME_PARAMETER.md)

---

---

## 对比

### Doxygen HTML vs Sphinx + Breathe

| 特性 | Doxygen HTML | Sphinx + Breathe |
|------|-------------|------------------|
| **外观** | 传统界面 | 现代化界面 ⭐ |
| **搜索** | 基础搜索 | 强大的全文搜索 ⭐ |
| **导航** | 简单列表 | 树形侧边栏导航 ⭐ |
| **主题** | 固定主题 | 可定制主题 ⭐ |
| **扩展** | 有限插件 | 丰富的 Sphinx 插件生态 ⭐ |
| **依赖** | 仅需 Doxygen | 需要 Python + Sphinx + Breathe |
| **构建速度** | 较快 | 稍慢（多一步转换） |
| **学习曲线** | 低 | 中等 |
| **适用场景** | 快速预览、简单项目 | 大型项目、团队协作文档 |

### 推荐使用场景

**选择 Doxygen HTML**:
- ✅ 快速预览文档
- ✅ 不想安装 Python 依赖
- ✅ 简单的个人项目
- ✅ 对文档外观要求不高

**选择 Sphinx + Breathe** ⭐:
- ✅ 大型团队协作项目
- ✅ 需要强大的搜索功能
- ✅ 需要定制化文档主题
- ✅ 需要与其他 Sphinx 项目集成
- ✅ 追求现代化的文档体验

### 总结

**强烈推荐使用 Sphinx + Breathe** 获得更好的文档体验！

虽然需要额外的设置步骤，但带来的好处远超成本：
- 🎨 更美观的界面
- 🔍 更强大的搜索
- 📚 更好的导航结构
- 🔧 更多的定制选项
- 🌟 更专业的文档呈现
