# Doxygen Tools 快速参考

## 环境准备

首次使用前，需要设置 Python 虚拟环境并安装依赖：

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境（Linux/MacOS）
source .venv/bin/activate

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install sphinx breathe sphinx-rtd-theme
```

## 生成文档

### 方式 1: Doxygen 原生 HTML（传统）

```bash
# 构建
python3 doxygen_tools.py build

# 预览（端口 3001）
python3 doxygen_tools.py serve --open
```

### 方式 2: Sphinx + Breathe（推荐，现代化）

```bash
# 构建
python3 doxygen_tools.py sphinx-build

# 预览（端口 3002）
python3 doxygen_tools.py sphinx-serve --open
```

## 常用选项

```bash
# 自定义端口
python3 doxygen_tools.py sphinx-serve --port 8080

# 不自动打开浏览器
python3 doxygen_tools.py sphinx-serve

# 查看帮助
python3 doxygen_tools.py --help
python3 doxygen_tools.py sphinx-serve --help
```

## 文件位置

- **Doxygen XML**: `docs/doxygen/xml/`
- **Sphinx 源**: `.agents/skills/doxygen/.assets/sphinx/source/`
- **Sphinx 输出**: `docs/doxygen/sphinx/`
- **配置文件**: `.agents/skills/doxygen/.assets/sphinx/source/conf.py`

## 故障排除

### 找不到 sphinx/breathe 模块
```bash
# 确保已激活虚拟环境并安装依赖
source .venv/bin/activate
pip install sphinx breathe sphinx-rtd-theme
```

### 找不到 XML
```bash
# 确保 Doxyfile 中 GENERATE_XML = YES
doxygen Doxyfile
python3 doxygen_tools.py sphinx-build
```

### 端口被占用
```bash
python3 doxygen_tools.py sphinx-serve --port 8080
```

### 未激活虚拟环境
```bash
# 检查是否已激活虚拟环境
which python  # 应该显示 .venv/bin/python

# 如果未激活，重新激活
source .venv/bin/activate
```

## 完整工作流

```bash
# 1. 首次使用，设置环境
python3 -m venv .venv
source .venv/bin/activate
pip install sphinx breathe sphinx-rtd-theme

# 2. 生成 Doxygen XML
cd /path/to/project
doxygen Doxyfile

# 3. 构建 Sphinx 文档
python3 .agents/skills/doxygen/doxygen_tools.py sphinx-build

# 4. 预览文档
python3 .agents/skills/doxygen/doxygen_tools.py sphinx-serve --open
```

## 对比

| 特性 | Doxygen HTML | Sphinx + Breathe |
|------|-------------|------------------|
| 外观 | 传统 | 现代化 ⭐ |
| 搜索 | 基础 | 强大 ⭐ |
| 导航 | 简单 | 树形侧边栏 ⭐ |
| 主题 | 固定 | 可定制 ⭐ |
| 扩展 | 有限 | 丰富插件 ⭐ |

**推荐使用 Sphinx + Breathe** 获得更好的文档体验！
