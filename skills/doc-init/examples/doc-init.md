# 文档初始化（doc-init）

## 数据源与产出（原则）

- **事实源：** 应用本 skill 时 **当前工作区所指的目标项目代码仓库**（业务源码、配置、目录结构）。skills 集合中的本文件仅提供 **Wiki/mdBook 结构与写法模板**，不充当业务事实。
- **产出：** 在 **同一目标项目** 仓库内生成 **项目 Wiki**——通常为 `docs/` 下的 **mdBook**（`book.toml` + `src/*.md`），与代码同仓维护，可通过 `mdbook build` / `mdbook serve` 发布为文档站。

首次从该代码库生成体系化 Wiki 文档与 mdBook 工程；图示默认使用 **Mermaid**。

## 触发方式

输入 `/doc-init` 或明确要求「初始化项目文档」。

## 代码文件分析范围

**完整扫描以下文件类型**，不跳过任何源码文件：
- C/C++：`.c`、`.cpp`、`.h`、`.hpp`
- Python：`.py`
- Java：`.java`
- Go：`.go`
- TypeScript/JavaScript：`.ts`、`.js`
- Shell：`.sh`、`.bash`

## 能力说明

- 生成 `docs/src/` 下可扩展的 Wiki 结构（架构、原理、API、模块与子模块文档等）。
- 同步创建 mdBook：`book.toml`、`SUMMARY.md`，支持搜索与章节折叠。
- 递归识别子模块目录，为各模块生成独立文档入口。

## 工作流程

### 1. 语言选择

- 询问文档语言（中文 / 英文），默认 **中文**。
- 后续生成内容均使用该语言。

### 2. 仓库分析

- 执行 `tree -L 10 --dirsfirst`（或等价方式）获取目录结构。
- 扫描入口与清单：`main.*`、`index.*`、`app.*`、`package.json`、`go.mod`、`Cargo.toml`、`CMakeLists.txt` 等，识别技术栈。
- 根据 `import` / `require` / `#include` 等梳理模块依赖。
- 提取对外接口（HTTP/RPC/导出函数）、核心类型与关键配置、脚本与测试位置。

### 3. Wiki 目录结构（示例）

在 `docs/src/` 下生成（可按项目裁剪）：

```
docs/src/
├── SUMMARY.md
├── README.md
├── architecture.md
├── principles.md
├── usage.md
├── api.md
├── structures.md
├── changelog.md
├── troubleshooting.md
├── glossary.md
├── .review/
│   ├── code-review-*.md
│   ├── summary.md
│   ├── results.json
│   └── api-doc.md
├── modules/
│   ├── core_api.md
│   ├── script_api.md
│   └── utils_api.md
├── reference/
│   ├── commands.md
│   ├── environment.md
│   └── file_formats.md
├── tutorials/
│   ├── getting_started.md
│   └── advanced_topics.md
└── submodules/
    └── <module>/
        ├── overview.md
        └── ...
```

### 4. 文件内容要点

| 文件 | 内容要点 |
|------|----------|
| `README.md` | 简介、快速开始、文档导航、核心业务流（Mermaid）、可选徽章 |
| `architecture.md` | 分层与组件关系（如 `graph TD`）、技术选型、依赖与部署示意 |
| `principles.md` | 算法与设计模式、关键流程（`sequenceDiagram`）、状态与数据流 |
| `usage.md` | 环境、安装、运行、配置；可用 `flowchart LR` |
| `api.md` | 对外 API 列表：方法、路径、参数、返回值、示例；可选 `classDiagram` |
| `structures.md` | 核心类型与字段、关键签名；`classDiagram` 或 `erDiagram` |
| `changelog.md` | 按时间倒序的变更记录 |
| `troubleshooting.md` | FAQ、错误码、日志线索 |
| `glossary.md` | 术语与缩写 |
| `submodules/*/` | 每子模块独立概述与专题页 |

**子模块规则：** 为包含源码的子目录（排除 `docs`、`tests`、`node_modules`、`.git`、`build` 等）在 `submodules/` 下建立同名目录；若源码主要在根目录，可在 `modules/` 下增加 `root_api.md`。

### 5. mdBook 初始化（参考实现：`book.toml` + Mermaid 脚本）

在 **目标项目** 的 `docs/`（或团队约定的 mdBook 根目录）下放置配置与脚本。**本 skill 在 skills 集合中的对照文件如下**，生成 Wiki 时应 **复制并按需改写** `book.toml` 字段（`title` / `authors` / `language`），**三者放在同一目录**（与 `src/` 并列），以便 `additional-js` 相对路径生效：

| 参考文件（位于 skills 仓库 `doc-init/assets/` 下） | 说明 |
|------|------|
| [book.toml](../assets/book.toml) | 声明 `[preprocessor.mermaid]`（`command = "mdbook-mermaid"`）、`[output.html] additional-js = ["mermaid.min.js", "mermaid-init.js"]`，以及 `[build]`（如 `build-dir`、`create-missing`、`use-default-preprocessors`）。 |
| [mermaid-init.js](../assets/mermaid-init.js) | 页面加载后按 mdBook 亮/暗主题调用 `mermaid.initialize`；切换主题时通过刷新页面重绘图表。 |
| [mermaid.min.js](../assets/mermaid.min.js) | Mermaid 浏览器端运行时（vendor 大包）；可按需替换为与项目锁定的版本（如 [Mermaid Releases](https://github.com/mermaid-js/mermaid/releases)）。 |

**构建依赖（PATH 可用）：**

- [mdBook](https://github.com/rust-lang/mdBook)
- [mdbook-mermaid](https://github.com/badboy/mdbook-mermaid)（与 `book.toml` 中 `command` 一致，通常 `cargo install mdbook-mermaid`）

**初始化步骤摘要：** 创建 `docs/src/` 与 `SUMMARY.md` → 将上述三文件拷入 `docs/` → 按目标项目修改 `book.toml` 元数据 → `mdbook build` / `mdbook serve` 验证 Mermaid 代码块渲染。

- `src/SUMMARY.md` 与实际 Markdown 一致；必要时使用 `src/.gitkeep` 占位空目录。
- **不用 Mermaid 时**：可暂移除 `preprocessor.mermaid` 与 `additional-js`；文档一旦出现 `` ```mermaid ``，建议恢复与本参考一致的配置。

### 6. 交付

- 列出已生成路径树。
- 提示本地预览：`mdbook serve --open`（若已安装 mdBook）。
- 说明后续可用 `/doc-update` 做增量维护。

### 7. mdBook 与 Mermaid 约定（全项目文档基准）

- **目录约定：** Markdown 正文放在 mdBook 的 `src/` 下（本示例为 `docs/src/`）；`book.toml` 与 `src/`、`mermaid.min.js`、`mermaid-init.js` 同属 `docs/`（见 **§5 参考文件**）。
- **构建与 Mermaid：** **以 §5 中的 [book.toml](../assets/book.toml)、[mermaid-init.js](../assets/mermaid-init.js)、[mermaid.min.js](../assets/mermaid.min.js) 为默认参考**；CI 与本地均需安装 `mdbook` 与 `mdbook-mermaid`。若仅用编辑器预览 Markdown 而无 mdBook，须与团队约定「权威预览」方式，避免 CI 与本地不一致。
- **Mermaid：** 在 Markdown 中使用 ` ```mermaid ` 围栏；常用类型：`flowchart`、`sequenceDiagram`、`stateDiagram-v2`、`classDiagram`、`erDiagram`、`pie`、`gantt`（按章节需要选用）。保持图表与当前代码/接口一致。
- **与其他图示并存：** 下文「Skill 融合」中的 PlantUML、HTML、Vega 等与 Mermaid 可同时出现在书中；同一章节避免重复表达同一结构（选一主图 + 必要时附补充图）。

### 8. 与本仓库其他 Skill 融合（可选增强）

生成或迭代文档时，可在 **不改变 mdBook + Mermaid 基准** 的前提下，按领域选用本仓库其他 skill，使架构、流程与数据表达更专业。**使用前须打开对应 `SKILL.md` 并遵守其 Critical Rules**（例如 PlantUML 必须用 ` ```plantuml `；`architecture` / `infocard` 为嵌入 HTML、**禁止**用 ` ```html ` 围栏）。

| Skill | 典型章节 | 用途 |
|------|----------|------|
| [architecture](../../architecture/SKILL.md) | `architecture.md`、`README.md` | HTML/CSS 分层栅格、技术栈与多栏拓扑 |
| [uml](../../uml/SKILL.md) | `structures.md`、`api.md`、`principles.md` | 类图、时序、活动、组件等 PlantUML |
| [graphviz](../../graphviz/SKILL.md) | `architecture.md`、`principles.md` | DOT 依赖/调用图、精细边路由 |
| [mindmap](../../mindmap/SKILL.md) | `README.md`、`tutorials/` | PlantUML 思维导图、主题拆解 |
| [archimate](../../archimate/SKILL.md) | `architecture.md` | 企业架构 / TOGAF 视点（PlantUML ArchiMate） |
| [bpmn](../../bpmn/SKILL.md) | `principles.md`、`tutorials/` | 业务流程、集成模式（PlantUML BPMN） |
| [cloud](../../cloud/SKILL.md) | `architecture.md`、部署专题 | 云厂商图标与拓扑（PlantUML） |
| [network](../../network/SKILL.md) | `architecture.md`、`reference/` | 网络拓扑（PlantUML mxgraph） |
| [security](../../security/SKILL.md) | `architecture.md`、`troubleshooting.md` | 安全架构、信任边界（PlantUML） |
| [data-analytics](../../data-analytics/SKILL.md) | `principles.md`、数据专题 | 数据管道/湖仓（PlantUML） |
| [iot](../../iot/SKILL.md) | `architecture.md`、`submodules/` | IoT 设备与边缘（PlantUML） |
| [infographic](../../infographic/SKILL.md) | `README.md`、`changelog.md` 摘要 | KPI、路线图、SWOT 等信息图模板 |
| [infocard](../../infocard/SKILL.md) | `README.md`、`glossary.md` | 嵌入式 HTML 知识卡片 |
| [vega](../../vega/SKILL.md) | `principles.md`、监控与性能说明 | Vega/Vega-Lite 数据图表 |
| [canvas](../../canvas/SKILL.md) | `tutorials/`、概念整理 | JSON Canvas 自由布局白板 |

**实践建议：** `README.md` / `architecture.md` 以 Mermaid 画「最小可读」全貌；对云、网络、安全、数据等专业视图再按需追加对应 skill 产出。**新建章节或图示时**，在 `SUMMARY.md` 中登记链接（若为独立 `.md` 文件）。

## 可扩展性

- 新增模块时复制子模块文档模板并更新 `SUMMARY.md`。
- 可增加 `faq.md`、`contributing.md` 等；变更频繁时与 `changelog.md` 联动。
- **Skill 融合：** 可在 `reference/` 下增加 `visual-conventions.md`（可选），说明本项目文档中 Mermaid 与各扩展图示的分工与渲染要求。

---

## doxygen 格式文档输出示例

### 函数接口文档格式

```markdown
/**
 * @brief 初始化用户认证模块
 * 
 * 初始化认证模块，加载配置并建立连接池。
 * 
 * @param config_path 配置文件路径
 * @param timeout_ms 连接超时时间（毫秒）
 * @return int 0 表示成功，非 0 表示错误码
 * @note 需要提前调用 logger_init()
 * @see auth_destroy()
 */
int auth_init(const char* config_path, int timeout_ms);
```

### 结构体文档格式

```markdown
/**
 * @struct UserProfile
 * @brief 用户配置文件结构体
 * 
 * 存储用户的基本配置信息。
 */
typedef struct {
    /** @field username 用户名（最大 64 字符） */
    char username[64];
    /** @field email 用户邮箱地址 */
    char email[128];
    /** @field role 用户角色（admin/user/guest） */
    enum UserRole role;
    /** @field created_at 创建时间戳 */
    time_t created_at;
} UserProfile;
```

### 类文档格式

```markdown
/**
 * @class DataProcessor
 * @brief 数据处理器类
 * 
 * 提供数据清洗、转换和分析功能。
 */
class DataProcessor {
public:
    /**
     * @brief 构造函数
     * @param buffer_size 内部缓冲区大小
     */
    DataProcessor(size_t buffer_size);
    
    /**
     * @brief 处理数据块
     * @param input 输入数据指针
     * @param length 数据长度
     * @return bool 处理是否成功
     */
    bool process(const char* input, size_t length);
};
```

### 输出位置

- 函数接口文档：`api.md`
- 结构体/类文档：`structures.md`
- 模块级文档：`modules/<module_name>.md`
