#### 参考来源.

```sh
# superpowers skills中文版：https://github.com/jnMetaCode/superpowers-zh.git
# superpowers skills英文版: https://github.com/obra/superpowers.git
# markdown-viewer skills图表信息处理：https://github.com/markdown-viewer/skills.git
# anthropics skils通用技能：https://github.com/anthropics/skills.git
# 生产技能skills：https://github.com/addyosmani/agent-skills.git
# vue ai skills前端app：https://github.com/vuejs-ai/skills.git
# deepwiki skills用rust实现：https://github.com/sopaco/deepwiki-rs.git
```

#### 使用.

```sh
# 在trae的@Builder场景下
/ai-context-generator   生上下文
/doc-init 初始化项目文档
/code-review 代码review
/doc-update 文档更新

# 启动
cd docs
mdbook serve --open --port 3001
```

#### gitnexus使用.

```sh
# 参考：https://mp.weixin.qq.com/s/eWrUzX1jKtvO5ZOJZ6qn_g
npm install -g gitnexus

# todo...
```

#### graphifyy和code-review-graph使用.

```sh
# 说明： 软件的函数调用图谱生成
# 源仓库：https://github.com/safishamsi/graphify.git

# 创建虚拟环境（命名为'.venv'是常见约定）
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate # Linux/MacOS

# 查看安装的包
pip3 list

# 导出依赖
pip3 freeze > requirements.txt

# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf .venv      # Linux/macOS

# 安装graphifyy
uv tool instyall graphifyy && graphify install
# or: pip install graphifyy && graphify install
# or: pipx install graphifyy && graphify install

# 运行graphifyy
graphify install

# 提示词
# 我已经安装了graphify，在虚拟环境中，需要使用source .venv/bin/activate激活使用
/graphify 基于本智能体进行完整提取graph，不需要密钥
/graphify query "QDMA驱动架构" 基于本智能体进行，不需要密钥，输出到docs目录下
/graphify query "ftest架构分析" 基于本智能体进行，不需要密钥，输出到docs目录下
/graphify explain "Ftest Platform & Utils" 基于本智能体进行，不需要密钥，输出到docs目录下，修正tools_usage_guide.md和ftest_architecture_analysis.md
/graphify query "本项目下所有工具使用的方法分析" 基于本智能体进行，不需要密钥，输出到docs目录下
/graphify path "ftest" "QDMA" 基于本智能体进行，不需要密钥，输出到docs目录下
/graphify explain "semp_udd_fpga_reg_get" 基于本智能体进行，不需要密钥，输出到docs目录下

# 生成wiki文档
/graphify ./ --wiki 基于本智能体进行，不需要密钥，输出到docs目录下

# code code-review-graph安装(暂无法使用)
# pip install code-review-graph
```

#### wsl node环境隔离.

```sh
# 解决WSL2 与 Windows 环境交叉污染的问题: https://www.raysblog.top/posts/wsl2%E5%AE%89%E8%A3%85%E7%8B%AC%E7%AB%8B%E7%9A%84npm/

# 1. vim ~/.bashrc，添加到底部，移除 Windows 的 Node.js 路径污染
export PATH=$(echo "$PATH" | sed -e 's/:\/mnt\/c\/Program Files\/nodejs//g' -e 's/:\/mnt\/c\/Users\/[^\/]*\/AppData\/Roaming\/npm//g')
source ~/.bashrc

# 2. 安装node和npm
# 安装 Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
# 验证
which node  # 输出 /usr/bin/node
# 在 Windows PowerShell 中执行
wsl --shutdown
# 然后重新打开 WSL2

# 3. 可选：保留调用 Windows npm 的能力
# 添加到 vim ~/.bashrc
alias npm-win='/mnt/c/Program\ Files/nodejs/npm'
alias node-win='/mnt/c/Program\ Files/nodejs/node.exe'
source ~/.bashrc

# 查看全局的安装包
npm list -g --depth=0
npm list -g

# oh-my-mermaid安装分析
sudo npm install -g npm@11.14.1     # 升级
sudo npm install -g oh-my-mermaid && omm setup

# skills扫描
/omm-scan  # 生成.omm, 分析代码库 → 生成架构文档
/omm-view  # 查看结果
/omm-push  # 推送云端

# npm omm模块命令
omm setup                          # 向 AI 工具注册技能
omm view                           # 打开交互式查看器
omm config language zh             # 设置内容语言
omm update                         # 更新到最新版本
```

#### doxygen和plantuml等使用.

```sh
# 项目api文档：https://ramzanbhutto.github.io/posts/doxygen/
# doxygen生成xml --> .md文档
# npm install moxygen -g
sudo apt-get install graphviz doxygen # 注意版本需要达到1.12.0以上，先手动编译安装，sudo apt-get remove doxygen卸载旧版本，然后再安装，则是最新版本，依赖也在
# git clone -b Release_1_12_0 https://github.com/doxygen/doxygen.git
doxygen -g
doxygen Doxyfile

# 1. 安装工具到目标项目目录
cd .agents/skills/doxygen
python3 doxygen_tools.py install ../../../

# 2. 进入项目目录后，仅构建文档
python3 doxygen_tools.py build

# 3. 构建并启动服务器（自动打开浏览器）
python3 doxygen_tools.py serve --open --port 3001

# 4. 尝试转换为markdown失败(跳过)
cd .agents/skills/doxygen
pip install markdownify beautifulsoup4
pip install lxml
# 混乱，都不好用-a指定mermaid.min.js等资源路径
python3 doxygen_html_to_mdbook.py ../../../docs/doxygen/html -o ../../../docs/doxygen/mdbook
python3 doxygen_xml_to_mdbook.py ../../../docs/doxygen/xml -o ../../../docs/doxygen/mdbook -a ../../../docs

# 5. 增加sphinx支持(不够完美)
pip install sphinx breathe sphinx-rtd-theme sphinx-sitemap
python3 doxygen_tools.py sphinx-gen-structure
python3 doxygen_tools.py sphinx-build
python3 doxygen_tools.py sphinx-serve --open --port 3001
```