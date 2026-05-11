---
name: code-review
description: Structured review of the target repo (C/C++/Python/Shell) using CodeQL, SEI CERT, MISRA, CWE — P0–P3, full finding schema, quality gates. Primary artifacts under docs/src/.review/; optional promotion to the same project's Wiki via doc-update (executive summary, gate results, security/maintenance narrative) aligned with doc-init. Skills repo supplies rules and templates only.
metadata:
  author: Code-review is powered by Markdown Viewer — the best multi-platform Markdown extension (Chrome/Edge/Firefox/VS Code) with diagrams, formulas, and one-click Word export. Learn more at https://docu.md
---

# 代码审查（code-review）

## 数据源与产出

| 角色 | 说明 |
|------|------|
| **事实源** | **当前应用本 skill 的目标项目代码仓库**。审查读取的 `.c` / `.cpp` / `.h` / `.py` / `.sh` / `.java` / `.go` / `.ts` / `.js` / `.sh`等均来自该仓库；规则集与报告模板来自 **code-review skill 约定**，**不替代**对真实代码路径与内容的**完整分析**。 |
| **主产出** | 在 **同一目标项目** 根目录下生成 **`docs/src/.review/`**（Markdown 报告、`results.json`、可选 SARIF）——与 Wiki 并列的 **审查溯源产物**。 |
| **可选产出（项目 Wiki）** | 经用户确认后，通过 **[doc-update](../doc-update/SKILL.md)** 将 **执行摘要、门控结论、趋势与行动项、合规/风险叙事** 写入该项目的 **`docs/src/`**（mdBook Wiki），结构遵循 **[doc-init/examples/doc-init.md](../doc-init/examples/doc-init.md)**（Mermaid 与 Skill 融合约定见该文件）。 |

基于 **CodeQL**、**SEI CERT**、**MISRA C/C++** 与 **CWE**，对 **目标仓库中** C/C++/Python/Shell 做多维度审查，按 **P0–P3** 分级。报告内图示优先 **Mermaid**（与 mdBook 文档栈一致）。

**Quick Start：** 锁定 **目标项目根** → **完整扫描所有源码文件**（`.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js`、`.sh` 等）→ 识别语言与范围 → 选用规则集 → 分析并记录问题字段 → **提取函数接口与结构体/类定义，生成 doxygen 格式文档** → 在目标项目中生成 `docs/src/.review/` 下带时间戳的报告与 `results.json` → 展示摘要；**可选：** 与用户确认后，按下文 **「Wiki 入库映射」** 经 **doc-update** 写入 **同一项目** 的 `docs/src/`（Wiki 保持概述性，**不** 用整份问题清单替代 `docs/src/.review/`）。

> **IMPORTANT：** 会在 **目标项目** 的 **`docs/src/.review/`** 下创建报告与数据文件。调整严重性、忽略规则或生成补丁前应与用户确认；报告内 Mermaid 使用常见类型（`pie`、`flowchart`）或回退为表格。同步到 Wiki 时不要破坏 doc-init 约定的目录与 `SUMMARY.md`。**双轨原则：** `docs/src/.review/` = 全量可机读溯源；Wiki = 供团队长期阅读的 **摘要、门控、规范与排障增强**。

---

## 权威参考（与文档技能对齐）

| 参考 | 用途 |
|------|------|
| [doc-init/examples/doc-init.md](../doc-init/examples/doc-init.md) | 项目文档目录、`changelog.md` / `troubleshooting.md` 等职责；mdBook 三件套与 Mermaid/扩展图示约定 |
| [doc-update/SKILL.md](../doc-update/SKILL.md) | 将审查结论、修复清单、版本对比 **增量写入** 文档与快照 |
| [security/SKILL.md](../security/SKILL.md) | 需在文档中补充 **安全架构图**（PlantUML）时可配合使用 |

---

## Wiki 入库映射（经 doc-update）

将审查结果写入项目 Wiki 时，**优先**使用下表；具体小节标题可与用户协商，但须保持 `SUMMARY.md` 可导航。

| `docs/src/.review/` 或报告内容 | 建议 Wiki 落点 | 写入要点 |
|------------------------|----------------|----------|
| 执行摘要、P0–P3 计数、风险分 | 新建 `docs/src/quality.md` 或 `README.md` 专节「质量概览」 | 1 页内可读；可含 Mermaid `pie` 分布图；**不**逐条展开全量缺陷。 |
| 质量门控通过/未通过、阻塞项 | 同上 + `changelog.md` 条目标注 | 门控规则版本、失败原因、负责人/截止（若用户要求）。 |
| 高置信 P0/P1 与修复状态 | `troubleshooting.md` 或「已知风险」子节 | **症状化**表述：风险类型、影响模块、缓解措施、指向 `docs/src/.review/` 中 ID；避免粘贴过长代码块。 |
| 合规映射（CWE/MISRA/CERT） | `docs/src/compliance.md` 或 `reference/` | 表格：**规则族 → 本项目策略 → 最近一次扫描结论**；细节仍在 `docs/src/.review/`。 |
| 趋势对比（相对上次扫描） | `quality.md` 或 `changelog.md` | 新增/修复数量 delta；回归提醒。 |
| 通用编码规范共识 | `principles.md` 短节「编码与安全惯例」 | 仅收录团队确认的惯例，不等同于完整规则手册。 |

**禁止：** 把完整 `results.json` 或数百行问题列表直接粘贴进 Wiki（应以链接 `docs/src/.review/` 路径或 CI 产物为准）。**推荐：** Wiki 中保留「如何触发审查、产物路径、门控策略」说明。

---

## Critical Rules

| 规则 | 说明 |
|------|------|
| **目标仓库优先** | 扫描路径、报告中的 `file` 字段、以及后续入库章节，均指向 **被审查的项目**；skills 仓库仅提供规则与示例骨架。 |
| **范围明确** | 默认全量；增量需 Git；路径筛选需列出目录或 glob。**不跳过任何源码文件**，完整扫描 `.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js`、`.sh` 等文件。 |
| **规则与语言匹配** | 仅对扫描到的语言启用 C++/Python/Shell 对应规则集。 |
| **每条缺陷字段齐全** | `file`、行号、`rule_id`、`severity`、`category`、`confidence`、说明与建议等（见示例）。 |
| **定级可追溯** | 给出定级理由；必要时说明 CWE/MISRA/CERT 映射。 |
| **入库需对照 doc-init** | 将执行摘要、质量门控结果写入 Wiki 时，章节命名与 `SUMMARY.md` 与 doc-init 示例一致，并由用户确认。 |
| **Wiki 粒度** | Wiki 仅承载 **摘要与可追溯指针**；每条高危问题在 Wiki 中最好用一行「标题 + 跳转 `.review#anchor`」级别表述（若报告支持锚点）。 |
| **doxygen 格式输出** | 为每个代码文件生成函数接口与结构体/类的 doxygen 格式文档（含 `@brief`、`@param`、`@return`、`@struct`、`@class`、`@field` 等标签），便于与项目现有文档集成。 |

---

## Examples

| 内容 | 文件 |
|------|------|
| 完整流程、规则表、输出结构与质量门控 | [code-review.md](examples/code-review.md) |
| 报告 Markdown 骨架、`results.json`、标准 Mermaid | [code-review-report-sample.md](examples/code-review-report-sample.md) |

---

## 工作流程摘要

1. **代码文件扫描：** **完整遍历所有源码文件**（`.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js`、`.sh` 等），提取函数接口、结构体/类定义。
2. **识别：** 语言、审查模式（全量 / 增量 / 路径）、规则集与历史基线。
3. **分析：** 数据流 / 控制流 / 模式匹配 / 上下文加权。
4. **产出：** `docs/src/.review/code-review-*.md`、`summary.md`、`results.json`（可选 SARIF）；**生成 doxygen 格式的函数接口与结构体/类文档**；报告图示约定见 [code-review-report-sample.md](examples/code-review-report-sample.md)。
5. **交互：** 摘要、按条展开、可选补丁与规则屏蔽。
6. **可选文档化：** 与用户确认入库范围 → 调用 **[doc-update](../doc-update/SKILL.md)**，按「Wiki 入库映射」写入 `quality.md`（或等价）、`changelog.md`、`troubleshooting.md`、`compliance.md` 等；趋势类数值如需图表可 **[vega](../vega/SKILL.md)** 嵌入（遵守 Vega fence 规则）；完成后由 doc-update 刷新快照。

---

## 与本项目其他 Skill 的配合

- **文档正文与 mdBook：** [doc-init](../doc-init/SKILL.md) / [doc-update](../doc-update/SKILL.md)；权威结构与融合表：[doc-init/examples/doc-init.md](../doc-init/examples/doc-init.md)。
- **报告内可视化：** Mermaid 为主；指标仪表盘式输出可选用 [vega](../vega/SKILL.md)（与示例报告区分边界：静态审查报告 vs 文档内长期维护图）。
- **安全叙事与架构：** 若需在文档中展开威胁建模、信任边界，除 Mermaid 外可按 [security](../security/SKILL.md) 生成 PlantUML 安全视图（嵌入规则见该 SKILL）。
- **架构 HTML 展板：** 高层执行摘要对外展示可选用 [architecture](../architecture/SKILL.md)（嵌入式 HTML，禁止 ` ```html `）。

---

## Common Pitfalls

| 情况 | 处理 |
|------|------|
| 混合语言项目 | 分语言加载规则，避免误报。 |
| Mermaid 无法渲染 | 使用 `pie` / `flowchart`；分布数据改用 Markdown 表格。 |
| 置信度低的问题 | 标注为「需人工确认」，避免当作阻断项。 |
| 审查结果与文档两套皮 | 明确「`docs/src/.review/` 为溯源，Wiki 为共识」；同步时用 doc-update 单次变更集，避免手工拷贝漂移。 |
