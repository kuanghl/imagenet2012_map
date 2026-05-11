# 代码审查（code-review）

## 数据源与产出（原则）

- **事实源：** **目标项目代码仓库** 中的源码（C/C++/Python/Shell 等）；审查逻辑与规则定义来自本 skill，分析对象始终是业务仓库。
- **主产出：** **同一项目** 下的 **`docs/src/.review/`**（报告、`results.json` 等），用于溯源与 CI。
- **可选产出：** **同一项目** 的 **Wiki/mdBook**（`docs/src/`），通过 **doc-update** 将结论写入既定章节；布局约定见 [doc-init/examples/doc-init.md](../../doc-init/examples/doc-init.md)。**入库章节与粒度**（摘要 vs 全量列表、quality/compliance/troubleshooting 分工）以 [code-review/SKILL.md](../../SKILL.md) 中的 **「Wiki 入库映射」** 为准。

## 触发方式
输入 `/code-review` 或明确提出“对项目进行代码审查”、“Code Review”。

## 代码文件分析范围

**完整扫描以下文件类型**，不跳过任何源码文件：
- C/C++：`.c`、`.cpp`、`.h`、`.hpp`
- Python：`.py`
- Java：`.java`
- Go：`.go`
- TypeScript/JavaScript：`.ts`、`.js`
- Shell：`.sh`、`.bash`

## 能力描述
基于 **CodeQL 标准查询套件**、**SEI CERT 编码标准**、**MISRA C/C++ 安全规范** 以及 **CWE 常见弱点枚举**，对 **目标项目仓库中** C/C++/Python/Shell 进行全面的自动化代码审查。由 AI 深度理解代码并执行多维规则匹配，从 **安全性**、**可靠性**、**性能**、**可维护性**、**合规性** 五大维度识别潜在缺陷、安全漏洞和代码异味，按 **PM 管理等级**（P0‑致命 / P1‑严重 / P2‑一般 / P3‑建议）分类输出到 **该项目** `docs/src/.review/` 目录，并提供详细的**根本原因分析**与**可执行的修复建议**（含代码示例）。支持全量审查、增量审查、以及自定义规则配置。将结论写入 **Wiki/mdBook** 时遵循上文「数据源与产出」第三条，细节见 [doc-init/examples/doc-init.md](../../doc-init/examples/doc-init.md) §7–§8，并由 **doc-update** 执行写入。

---

## 工作流程

### 1. 项目识别与作用域定义
- **自动识别技术栈**：扫描项目目录，识别主要编程语言（`.c`, `.cpp`, `.h`, `.py`, `.sh`, `.bash` 等），确定审查目标。
- **审查模式选择**：
  - **全量审查**：扫描所有源文件（默认）
  - **增量审查**：仅检查 `git diff` 中变更的文件（需 Git 仓库）
  - **路径筛选**：支持指定目录或文件模式进行审查
- **规则集选择**：展示可用的规则集（如 `cpp-security`, `cpp-quality`, `misra-c-2012`, `cert-c`），允许用户启用/禁用特定规则。
- **基线对比**：如存在历史审查记录，自动对比并突出新增/修复的问题。

### 2. 加载审查规则体系
AI 内建专业的多层次规则框架，融合多个行业标准：

#### 2.1 C/C++ 规则集（分层分类）
##### 安全规则（Security）
| 规则 ID | 描述 | CWE/MISRA | 严重性 |
|---------|------|-----------|--------|
| cpp/buffer-overflow | 缓冲区溢出（栈溢出、堆溢出） | CWE-119 | P0 |
| cpp/format-string | 格式化字符串漏洞 | CWE-134 | P0 |
| cpp/sql-injection | SQL 注入 | CWE-89 | P0 |
| cpp/command-injection | 命令注入 | CWE-78 | P0 |
| cpp/use-after-free | 释放后使用 | CWE-416 | P1 |
| cpp/null-pointer-dereference | 空指针解引用 | CWE-476 | P1 |
| cpp/double-free | 双重释放 | CWE-415 | P1 |
| cpp/integer-overflow | 整数溢出 | CWE-190 | P2 |
| cpp/integer-underflow | 整数下溢 | CWE-191 | P2 |
| cpp/taint-arithmetic | 受污染的算术运算 | CWE-190 | P2 |
| cpp/race-condition | 竞态条件 | CWE-362 | P1 |
| cpp/hardcoded-credentials | 硬编码凭据 | CWE-798 | P1 |
| cpp/insecure-random | 不安全的随机数生成 | CWE-330 | P2 |
| cpp/cleartext-storage | 敏感数据明文存储 | CWE-312 | P1 |

##### 可靠性规则（Reliability）
| 规则 ID | 描述 | MISRA/SEI CERT | 严重性 |
|---------|------|---------------|--------|
| cpp/unchecked-return-value | 未检查关键函数返回值 | CERT FIO32-C | P2 |
| cpp/resource-leak | 资源泄漏（内存、文件、锁） | SEI CERT MEM31-C | P2 |
| cpp/uninitialized-variable | 未初始化变量读取 | MISRA C:2012 Rule 9.1 | P2 |
| cpp/dangling-pointer | 悬空指针 | CWE-825 | P1 |
| cpp/array-index-out-of-bounds | 数组越界 | MISRA C:2012 Rule 17.6 | P1 |
| cpp/incompatible-pointer-types | 不兼容的指针类型转换 | CWE-704 | P2 |
| cpp/signed-unsigned-mismatch | 有符号/无符号不匹配 | MISRA C:2012 Rule 10.1 | P2 |
| cpp/float-equality | 浮点数直接比较 | SEI CERT FLP30-C | P3 |

##### 性能规则（Performance）
| 规则 ID | 描述 | 严重性 |
|---------|------|--------|
| cpp/inefficient-algorithm | 低效算法（O(n²) 的不必要使用） | P3 |
| cpp/redundant-copy | 冗余复制操作 | P3 |
| cpp/unnecessary-memory-allocation | 不必要的内存分配 | P3 |
| cpp/inefficient-file-io | 低效的文件 I/O | P3 |

##### 可维护性规则（Maintainability）
| 规则 ID | 描述 | 严重性 |
|---------|------|--------|
| cpp/dead-code | 死代码/不可达代码 | P3 |
| cpp/unused-variable | 未使用的变量 | P3 |
| cpp/unused-function | 未使用的函数 | P3 |
| cpp/magic-numbers | 魔法数字 | P3 |
| cpp/long-function | 过长函数（>50行） | P3 |
| cpp/complex-condition | 复杂条件表达式 | P3 |
| cpp/missing-return | 缺失返回语句 | P2 |

##### MISRA C:2012 合规性规则（可选）
| 规则 ID | 描述 | MISRA 规则 | 严重性 |
|---------|------|-----------|--------|
| cpp/misra-10.1 | 运算数类型不匹配 | Rule 10.1 | P2 |
| cpp/misra-10.3 | 复杂表达式中不允许使用负值 | Rule 10.3 | P2 |
| cpp/misra-12.2 | 运算符优先级需显式括号 | Rule 12.2 | P3 |
| cpp/misra-17.6 | 数组索引需在范围内 | Rule 17.6 | P1 |
| cpp/misra-17.7 | 函数参数数组不能修改 | Rule 17.7 | P3 |

#### 2.2 Python 规则集
##### 安全规则
| 规则 ID | 描述 | CWE | 严重性 |
|---------|------|-----|--------|
| py/sql-injection | SQL 注入 | CWE-89 | P0 |
| py/code-injection | 代码注入（eval, exec） | CWE-94 | P0 |
| py/command-injection | 命令注入（os.system, subprocess） | CWE-78 | P0 |
| py/stack-trace-exposure | 异常信息泄露 | CWE-209 | P1 |
| py/clear-text-logging-sensitive-data | 敏感数据明文日志 | CWE-532 | P1 |
| py/insecure-deserialization | 不安全反序列化（pickle, yaml） | CWE-502 | P1 |
| py/hardcoded-credentials | 硬编码密码/密钥 | CWE-798 | P1 |
| py/insecure-random | 不安全的随机数 | CWE-330 | P2 |
| py/weak-hash | 弱哈希算法（MD5, SHA1） | CWE-327 | P2 |
| py/ssrf | 服务端请求伪造 | CWE-918 | P1 |

##### 质量规则
| 规则 ID | 描述 | 严重性 |
|---------|------|--------|
| py/overly-broad-exception | 过度捕获异常（except:） | P2 |
| py/empty-except | 空 except 块 | P3 |
| py/unused-import | 未使用的导入 | P3 |
| py/unused-variable | 未使用的变量 | P3 |
| py/missing-docstring | 缺失文档字符串 | P3 |
| py/mutable-default-arg | 可变默认参数 | P2 |
| py/global-statement | 过度使用 global | P3 |
| py/missing-type-hints | 缺失类型注解（大型项目） | P3 |

#### 2.3 Shell 脚本规则集
| 规则 ID | 描述 | 严重性 |
|---------|------|--------|
| shell/unquoted-variable | 未引用的变量扩展 | P2 |
| shell/command-substitution-unsafe | 不安全的命令替换 | P2 |
| shell/set-e-missing | 缺失 `set -e` 错误处理 | P3 |
| shell/set-u-missing | 缺失 `set -u` 未定义变量检查 | P3 |
| shell/pipe-fail-missing | 缺失 `set -o pipefail` | P3 |
| shell/magic-numbers | 魔法数字 | P3 |
| shell/unreachable-code | 不可达代码 | P3 |

### 3. 多维分析与缺陷发现
AI 通过深度代码理解，执行以下分析：

#### 3.1 静态分析
- **数据流分析**：追踪变量传播，识别未初始化使用、污染传播路径
- **控制流分析**：识别死代码、不可达路径、逻辑漏洞
- **类型检查**：验证类型安全，识别危险转换
- **资源生命周期**：检查资源的获取/释放匹配

#### 3.2 模式匹配
- 对每个文件，AI 识别与上述规则匹配的模式，例如：
  - `sprintf(buffer, "%s", user_input)` → `cpp/buffer-overflow`
  - `eval(user_input)` → `py/code-injection`
  - `system("cmd $var")` → `shell/command-injection`

#### 3.3 上下文分析
- 评估缺陷的**影响范围**（核心功能？边缘情况？）
- 评估缺陷的**触发条件**（攻击者可控？需要特定输入？）
- 检查是否有**缓解措施**（如输入验证、边界检查）
- 根据上下文调整严重性等级

#### 3.4 问题记录格式
对每个发现的问题，详细记录：
| 字段 | 说明 |
|------|------|
| `file` | 文件路径 |
| `line_start` - `line_end` | 行号范围 |
| `rule_id` | 规则 ID |
| `title` | 问题标题 |
| `severity` | 严重性（P0-P3） |
| `category` | 类别（安全/可靠性/性能/可维护性/合规性） |
| `confidence` | 置信度（高/中/低） |
| `cwe` | 关联的 CWE 编号（如有） |
| `code_snippet` | 触发代码片段（高亮显示） |
| `description` | 详细描述 |
| `risk` | 风险分析（潜在影响、利用场景） |
| `severity_rationale` | 定级理由 |
| `recommendation` | 修复建议（含代码示例） |

### 4. 严重性评级与验证
#### 4.1 PM 管理等级定义
| 等级 | 名称 | 定义与示例 | 响应时间要求 |
|------|------|-----------|------------|
| **P0** | 致命 | 可直接导致系统崩溃、任意代码执行、敏感数据泄露的高确信漏洞。<br>示例：缓冲区溢出、SQL 注入、命令注入、硬编码的根密码。 | **立即修复**（24小时内） |
| **P1** | 严重 | 大概率引发安全问题或导致严重故障的缺陷。<br>示例：释放后使用、空指针解引用、不安全反序列化、竞态条件。 | **优先修复**（1周内） |
| **P2** | 一般 | 降低安全性或可能引发运行时异常的代码质量问题。<br>示例：未检查返回值、资源泄漏、不安全的随机数、过度捕获异常。 | **计划修复**（下个迭代） |
| **P3** | 建议 | 代码风格、可维护性问题、轻微缺陷。<br>示例：未使用变量、魔法数字、空 except 块、死代码。 | **建议修复**（可选） |

#### 4.2 评级调整因子
- **影响范围**：核心业务模块 → 升级
- **攻击面**：暴露于外部输入 → 升级
- **利用难度**：容易利用 → 升级，难以触发 → 降级
- **历史漏洞**：该模式曾导致真实漏洞 → 升级
- **缓解措施**：已存在边界检查 → 降级

#### 4.3 置信度评估
- **高**：非常确定存在此问题，可复现
- **中**：很可能存在，但需人工确认
- **低**：可能存在，有可疑模式，建议审查

### 5. 生成专业审查报告
在项目根目录下创建 `docs/src/.review/` 目录，输出以下文件：


#### 5.1 详细报告 `code-review-YYYY-MM-DD-HHmmss.md`

- 元数据、执行摘要、按 P0–P3 分组的问题列表、修复优先级与附录等 **完整 Markdown 骨架** 见同目录 [code-review-report-sample.md](code-review-report-sample.md)。
- 图表请使用常见 Mermaid 类型（如 `pie`、`flowchart`）；需要兼容性时可用表格代替柱状图或折线图。

#### 5.2 简明报告 `summary.md`
简明的执行摘要，供管理层使用：
- 风险分数（0-100）
- 问题分类统计
- 关键发现与建议
- 修复优先级列表

#### 5.3 机器可读数据 `results.json`
结构化 JSON 数据，便于 CI/CD 集成：
```json
{
  "metadata": {...},
  "issues": [
    {
      "id": "P0-001",
      "severity": "P0",
      "file": "src/user_input.c",
      "line": 42,
      "rule_id": "cpp/buffer-overflow",
      ...
    }
  ],
  "summary": {...}
}
```

#### 5.4 GitLab/GitHub 兼容格式（可选）
生成可直接用于 PR/MR 评论的格式：
- SARIF 格式（SARIF 2.1）
- 纯文本评论格式

---

### 6. 交互式确认与后续
- 展示审查结果的**高级摘要**
- 询问用户是否需要：
  - 查看某个问题的详细分析
  - 自动生成修复补丁（针对简单问题）
  - 调整某些问题的严重性评级
  - 屏蔽/忽略特定规则
- 提供快速修复命令（如自动格式化等）

---

## 高级功能

### 增量审查模式
检测自上次审查以来的变更：
- 对比文件哈希或 Git diff
- 仅分析变更文件中的新问题
- 标记已修复的问题（若已解决）
- 生成差异报告

### 自定义规则支持
用户可追加自定义规则：
- 模式匹配规则（正则表达式）
- 语义规则（描述）
- 公司/团队特定编码规范

### 多语言支持
支持同时分析混合语言项目：
- C/C++ + Python 混合
- C/C++ + Shell 混合
- 自动为每种语言加载相应规则集

---

## 质量门控（Quality Gates）
可配置自动拦截标准：
- P0 问题 > 0 → 阻塞
- P1 问题 > 5 → 需评审
- 安全评分 < 70 → 需改进

---

## doxygen 格式文档输出

代码审查过程中，同时为每个代码文件生成 doxygen 格式的函数接口与结构体/类文档，便于与项目现有文档集成。

### 输出内容

| 文档类型 | 输出位置 | 包含内容 |
|----------|----------|----------|
| 函数接口文档 | `docs/src/.review/api-doc.md` | 函数签名、参数、返回值、注释 |
| 结构体/类文档 | `docs/src/.review/struct-doc.md` | 类型定义、字段说明 |
| 模块索引 | `docs/src/.review/module-index.md` | 文件与符号索引 |

### 输出格式示例

**函数接口：**
```markdown
/**
 * @brief 初始化日志模块
 * 
 * @param config 配置结构体指针
 * @return int 0=成功，非0=错误码
 * @note 线程安全
 */
int logger_init(const LoggerConfig* config);
```

**结构体：**
```markdown
/**
 * @struct LoggerConfig
 * @brief 日志配置结构体
 * @field level 日志级别
 * @field output_path 输出路径
 * @field max_file_size 最大文件大小(MB)
 */
typedef struct {
    LogLevel level;
    char output_path[256];
    size_t max_file_size;
} LoggerConfig;
```

### 与审查报告的关联

- 每个问题报告关联到对应的函数/结构体文档
- 在 `results.json` 中添加符号引用信息
- 支持从问题定位到 API 文档的跳转链接
