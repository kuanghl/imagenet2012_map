---
name: doc-init
description: Use the target project codebase (the repo where this skill is applied) as the single source of truth; scaffold a professional project Wiki as mdBook (docs/src, SUMMARY, book.toml, Mermaid baseline). Enforce completeness—navigation, architecture/API/modules, glossary, troubleshooting, changelog, traceability to code paths—and optional fusion with sibling skills (UML, architecture HTML, cloud, security). Conventions in doc-init/examples; all generated Wiki files belong to the target project, not the skills collection.
metadata:
  author: Doc-init is powered by Markdown Viewer — the best multi-platform Markdown extension (Chrome/Edge/Firefox/VS Code) with diagrams, formulas, and one-click Word export. Learn more at https://docu.md
---

# 文档初始化（doc-init）

## 数据源与产出

| 角色 | 说明 |
|------|------|
| **事实源** | **当前应用本 skill 的目标项目代码仓库**（工作区 / 用户指定的工程路径）。所有章节内容须从该仓库的源码、配置与目录结构 **推导与核对**，不得把「skills 集合仓库」里的示例当成业务真相（除非正在文档化的就是 skills 本身）。 |
| **产出** | 在上述 **同一目标项目** 内生成 **Wiki 形态的 mdBook 工程**：通常为 `docs/`（含 `book.toml`、`src/` 下 Markdown、搜索与导航）。即 **项目的官方 Wiki 文档站**，与业务代码同仓维护。 |

首次从该代码库生成 **Wiki 风格文档** 与 **mdBook**。**正文默认使用 Markdown + Mermaid**；若需更专业的架构/流程/数据表达，可按领域 **融合本 skills 集合中的其他 skill**（仅作 **写法与图示规范** 参考，内容仍来自目标项目代码）——见 [examples/doc-init.md](examples/doc-init.md) 中 mdBook/Mermaid 与 Skill 融合约定。

**Quick Start：** 锁定 **目标项目根目录** → 确认文档语言 → 分析该仓库目录与技术栈 → 按 [doc-init.md](examples/doc-init.md) 在目标项目中生成 `docs/src/` 与 `book.toml` / `SUMMARY.md` → 按需嵌入扩展图示 → 列出产出树并提示用 **doc-update** 维护。

> **IMPORTANT：** 会在 **目标项目** 的 `docs/` 下创建较多文件。写入前应让用户知晓输出根路径；除非用户明确要求，否则不要顺带大范围改动 **业务源码**。融合其他 skill 时 **必须遵守该 skill 的 Critical Rules**（围栏类型、是否禁止代码块等）。

---

## Wiki 文档质量标准（执行标准）

生成内容应达到 **可交付给工程团队与新人 onboarding** 的水平，而非目录占位符。

| 维度 | 要求 |
|------|------|
| **完整性** | 覆盖仓库真实入口、构建/运行方式、对外接口、核心数据结构与错误排查入口；无「待补充」占位的关键章节（若信息缺失，明确标注 **待确认项** 并列出需用户提供的输入）。 |
| **可追溯** | 重要论断附带 **源码路径或配置文件路径**（例如 `src/foo/bar.c`、`config/app.toml`）；API 与类型说明与符号定义处一致，避免文档独有字段名。 |
| **一致性** | 全书术语统一（与 `glossary.md` 对齐）；同一概念在 README、architecture、api 中命名相同；`SUMMARY.md` 与 `src/` 文件 **一一对应**、无死链。 |
| **图示** | 架构/主流程至少各有 **一张与实现匹配的 Mermaid**；复杂交互用 `sequenceDiagram`，组件边界用 `flowchart`/`C4` 风格子图（语法遵循 Mermaid 版本约束）；扩展图示（PlantUML/HTML/Vega）仅作补充且遵守对应 skill 围栏规则。 |
| **可操作** | `usage.md` 含环境版本约束、安装、启动命令、常见配置项；`troubleshooting.md` 含症状 → 原因假设 → 排查步骤 → 相关日志/错误码。 |
| **可演进** | 初始化时写入或预留 `docs/.doc-snapshot.json`（可与 doc-update 约定字段兼容），便于后续增量对比；`changelog.md` 首条记录本次文档初始化摘要。 |

---

## 各核心页面的最低内容深度

| 页面 | 最低要求（专业 Wiki） |
|------|------------------------|
| `README.md` | 项目一句话定位、受众、**文档地图**（链接到 architecture/usage/api）、与仓库根 `README`（若存在）互补而非空白重复。 |
| `architecture.md` | 分层/模块边界、主要依赖关系、部署或运行时拓扑（若适用）、与 `principles.md` 的职责划分（架构 vs 算法/流程）。 |
| `principles.md` | 关键算法或状态机、主业务序列（Mermaid）、非显而易见的约束与设计权衡简述。 |
| `api.md` | 对外接口表格或列表：**路径或符号名、方法、参数、响应/返回值、鉴权、错误语义**；必要时链接到 `structures.md`。 |
| `structures.md` | 核心类型/表结构字段说明；与源码定义同步的字段名与必选/可选。 |
| `modules/`、`submodules/` | 每模块：**职责、入口文件、对外暴露点、与上下游模块关系**；大模块拆多页时保持 `SUMMARY.md` 层级清晰。 |
| `reference/` | 命令行、环境变量、文件格式等与运维/集成相关的 **可查表**。 |
| `glossary.md`、`troubleshooting.md` | 术语与缩写全覆盖关键域名词；FAQ 与典型故障可与错误码、日志字段交叉引用。 |

---

## 权威参考（doc-init 目录）

以下保持一致：**本 SKILL** → **[examples/doc-init.md](examples/doc-init.md)**（完整目录树、章节职责、mdBook/Mermaid）→ **mdBook + Mermaid 参考三件套**（见下表）→ **Skill 融合表**。

**doc-update** 与 **code-review** 在更新文档或回填审查结论时，应优先对齐此目录中的 Wiki 结构与图示约定，避免章节名与 `SUMMARY.md` 脱节。

---

## Critical Rules

| 规则 | 说明 |
|------|------|
| **目标仓库优先** | 一切读取与分析指向 **被文档化的项目**；`doc-init/examples` 仅提供 **结构与约定模板**，不替代真实代码与配置。 |
| **先定语言** | 询问中文或英文，默认中文；全书术语与章节语言保持一致。 |
| **mdBook + Mermaid 为基准** | 架构/流程/数据模型优先用 Mermaid；配置对齐 **[docs/book.toml](docs/book.toml)** + **`mermaid-init.js` / `mermaid.min.js`**（详见 [examples/doc-init.md](examples/doc-init.md)）。 |
| **图表与代码一致** | `architecture.md`、`principles.md`、`api.md` 等与 **目标项目** 源码、接口真相一致。 |
| **融合 skill 不破坏基准** | 扩展图示（PlantUML、HTML、Vega 等）作为补充；同一观点避免重复多头维护。 |
| **仅创建文档所需路径** | 按示例结构生成；空目录可用 `.gitkeep`，勿随意添加无关占位文件。 |
| **SUMMARY 对齐** | `SUMMARY.md` 与实际 `src/` 文件一一对应，避免死链。 |
| **首次快照** | 初始化末尾生成或更新 `docs/.doc-snapshot.json`（字段与 doc-update 示例对齐），记录关键源码路径哈希或提交号，支撑后续增量。 |
| **审查友好** | 结构预留与 **code-review** 的衔接：`troubleshooting.md`、安全或质量小节可被 doc-update 追加摘要而不破坏章节层级（见 code-review SKILL）。 |

---

## Examples

| 内容 | 文件 |
|------|------|
| 完整流程、Wiki 目录、mdBook/Mermaid 约定与全仓库 Skill 融合表 | [doc-init.md](examples/doc-init.md) |
| **mdBook + Mermaid 参考（复制到目标项目 `docs/`）** | [book.toml](docs/book.toml)、[mermaid-init.js](docs/mermaid-init.js)、[mermaid.min.js](docs/mermaid.min.js) |

---

## 工作流程摘要

1. **语言：** 确认文档语言（默认中文）。
2. **分析：** 目录树、入口与清单文件、依赖、对外接口与核心类型。
3. **生成：** 在 `docs/src/` 下建立 README、architecture、api、modules、submodules 等（详见示例）。
4. **mdBook：** 在目标项目 `docs/` 对齐 **[book.toml](docs/book.toml)**，并放入 **[mermaid-init.js](docs/mermaid-init.js)**、**[mermaid.min.js](docs/mermaid.min.js)**；安装 `mdbook` 与 `mdbook-mermaid`（详见 [examples/doc-init.md](examples/doc-init.md) 第 5 节）。
5. **可选增强：** 按领域从该示例「Skill 融合」表选用 [architecture](../architecture/SKILL.md)、[uml](../uml/SKILL.md)、[cloud](../cloud/SKILL.md) 等 skill 生成附加图示或卡片。
6. **自检：** 遍历 `SUMMARY.md` 链接；核对图表与源码路径；检查术语与 `glossary.md`；运行 `mdbook build`（若环境可用）确认 Mermaid 与预处理无报错。
7. **交付：** 打印目录树与 **验收摘要**（已生成页面列表、已知待确认项、快照路径）；提示 `mdbook serve --open`；说明后续使用 **`/doc-update`** 增量维护，**`/code-review`** 结论可经 doc-update 写入 Wiki。

---

## 与本项目其他 Skill 的配合（摘要）

完整映射与章节建议见 **[examples/doc-init.md](examples/doc-init.md)** 中的「Skill 融合」一节。常用组合：

- **软件建模：** [uml](../uml/SKILL.md)、[graphviz](../graphviz/SKILL.md)、[mindmap](../mindmap/SKILL.md)
- **分层/拓扑：** [architecture](../architecture/SKILL.md)（HTML）、[cloud](../cloud/SKILL.md)、[network](../network/SKILL.md)、[iot](../iot/SKILL.md)
- **流程与企业视角：** [bpmn](../bpmn/SKILL.md)、[archimate](../archimate/SKILL.md)
- **安全与数据：** [security](../security/SKILL.md)、[data-analytics](../data-analytics/SKILL.md)
- **版面与数据叙事：** [infographic](../infographic/SKILL.md)、[infocard](../infocard/SKILL.md)、[vega](../vega/SKILL.md)、[canvas](../canvas/SKILL.md)

文档生命周期：**[doc-update](../doc-update/SKILL.md)**（随代码增量同步）、**[code-review](../code-review/SKILL.md)**（结论可经 doc-update 写入 `troubleshooting.md` / 安全相关章节）。

---

## Common Pitfalls

| 情况 | 处理 |
|------|------|
| 子模块目录识别过宽/过窄 | 与用户确认「源码根」与排除列表（如 `node_modules`、`build`）。 |
| mdBook 路径混淆 | 约定 Markdown 位于 `docs/src/`；`book.toml` 与 `mermaid*.js` 位于 `docs/`（与 [docs/book.toml](docs/book.toml) 参考一致）。 |
| Mermaid 在 CI 不渲染 | 在 CI 安装 `mdbook-mermaid`，并确保 `book.toml` 中 `[preprocessor.mermaid]` 与 [additional-js](docs/book.toml) 指向的脚本已随仓库提交或由构建步骤提供。 |
| PlantUML/HTML 与 mdBook | 确保流水线支持对应围栏或嵌入方式；禁止混用错误的 fence（见各 skill）。 |
