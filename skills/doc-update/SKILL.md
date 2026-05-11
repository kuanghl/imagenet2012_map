---
name: doc-update
description: Incrementally refresh the target project's professional Wiki/mdBook from git or snapshot diff — sync prose, Mermaid, cross-links, glossary/troubleshooting/changelog, compatibility notes, and .doc-snapshot.json. Perform impact mapping, consistency pass across chapters, and preserve traceability to source paths. Layout per doc-init/examples; all writes are in the documented project repo, not the skills collection.
metadata:
  author: Doc-update is powered by Markdown Viewer — the best multi-platform Markdown extension (Chrome/Edge/Firefox/VS Code) with diagrams, formulas, and one-click Word export. Learn more at https://docu.md
---

# 文档增量更新（doc-update）

## 数据源与产出

| 角色 | 说明 |
|------|------|
| **事实源** | **当前应用本 skill 的目标项目代码仓库**。通过 `git diff` / `git status` 或快照对比到的变更，均以该仓库中的 **源码与配置** 为准，**完整分析所有变更的代码文件**（`.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js` 、`.sh`等），据此决定文档哪些段落与图示需要更新。 |
| **产出** | 在同一目标项目中维护 **Wiki/mdBook**：更新 `docs/src/` 下 Markdown、**Mermaid** 与可选扩展图示、交叉引用、`changelog.md`，以及 `docs/.doc-snapshot.json`。 |

根据上述代码变更 **仅更新受影响文档**，在 **mdBook + Mermaid** 基准上同步正文、图表与交叉引用，并维护快照。**章节结构与图示扩展约定**以 **[doc-init/examples/doc-init.md](../doc-init/examples/doc-init.md)** 为准（mdBook/Mermaid 约定与 Skill 融合表见该文件）。

**Quick Start：** 在 **目标项目根** 检测变更（Git 或 `docs/.doc-snapshot.json`）→ **完整分析所有变更代码文件**（提取函数接口、结构体/类定义）→ **影响映射与语义核对**（接口/类型/行为是否变化）→ 增量改段落与 **Mermaid**（及受影响的 PlantUML/HTML/Vega 等扩展块）→ **按 doxygen 格式更新 API 与类型文档** → **跨章节一致性检查**（术语、API 表、SUMMARY）→ 预览后写入 **该项目** 的 `docs/` → 更新快照与 `changelog.md`。

> **IMPORTANT：** 默认应先展示将修改的文件与章节摘要并得到确认；仅有在用户明确要求时使用无异于确认的批量写入（如 `--no-prompt`）。更新扩展 skill 产出时 **遵守对应 SKILL.md 的 Critical Rules**。若本次变更来自 **code-review** 结论入库，须单独列出写入 Wiki 的条目并保持与 `.review/` 摘要可追溯对应。

---

## 权威参考（对齐 doc-init）

| 参考 | 用途 |
|------|------|
| [doc-init/examples/doc-init.md](../doc-init/examples/doc-init.md) | Wiki 目录、各文件职责、mdBook 参考三件套（`book.toml` / `mermaid-init.js` / `mermaid.min.js`）、Mermaid 约定、skill 融合表 |
| [doc-init/docs/book.toml](../doc-init/docs/book.toml) 等同目录 JS | 目标项目 `docs/` 下 mdBook + `mdbook-mermaid` 与浏览器 Mermaid 的 **权威模板**（与 doc-init 示例中 mdBook 一节一致） |
| [doc-init/SKILL.md](../doc-init/SKILL.md) | 初始化流程摘要与 skill 配合索引 |

新增小节、重命名文件或增减图示类型时，应同步 **`SUMMARY.md`**，并与 doc-init 中的结构约定一致。

---

## Wiki 增量更新的专业要求

| 要求 | 说明 |
|------|------|
| **语义同步** | 区分「仅重构无行为变化」与「契约变化」：后者必须更新 `api.md`、`structures.md`、`changelog.md`，必要时在 `usage.md` 增加兼容性说明或迁移提示；**更新时保持 doxygen 格式规范**（`@brief`、`@param`、`@return`、`@struct`、`@class` 等标签）。 |
| **全文一致性** | 同一符号或接口在 README、architecture、modules 中出现的名称、路径须一并修订；同步检索 **死链、过时段落、重复矛盾表述**。 |
| **术语与词汇表** | 新增领域术语或缩写时更新 `glossary.md`；重命名概念时全局替换并核对索引页。 |
| **运维与排障** | 变更日志格式、错误码、退出码或典型故障模式时，同步 `troubleshooting.md` 与 `reference/` 中相关表。 |
| **图示生命周期** | 任何影响控制流、组件边界或数据模型的代码改动，**默认视为需要复核对应 Mermaid**；扩展图示按 doc-init 融合规则逐项检查。 |
| **changelog 条目质量** | 每条记录包含：**日期、类型**（feature/fix/docs/refactor 等）、**摘要**、**关联源码路径或模块**、可选 issue/PR/commit；避免模糊措辞。 |
| **审查结论入库** | 将 code-review 摘要写入 Wiki 时：保留 **严重级别分布、质量门控结论、趋势一句话**；具体问题清单仍以 `.review/` 为准，Wiki 只保留稳定共识与行动项。 |

---

## Critical Rules

| 规则 | 说明 |
|------|------|
| **目标仓库优先** | 变更检测与文档写入均在 **被文档化的项目** 内进行；不以 skills 仓库的示例内容覆盖业务文档事实。 |
| **Git 优先** | 有 Git 时用 `git diff` / `git status`；无 Git 时用快照哈希对比。 |
| **映射表可对齐项目** | 示例映射表中的路径需按实际仓库调整；执行前与用户确认。 |
| **Mermaid 与代码一致** | 所有受影响流程/架构类 Mermaid 与当前实现一致。 |
| **完整代码文件分析** | 不跳过任何变更的源码文件；遍历所有 `.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js` 、`.sh`等文件提取接口与类型定义变化。 |
| **doxygen 格式输出** | 更新 API 与类型文档时保持 doxygen 格式规范（`@brief`、`@param`、`@return`、`@struct`、`@class`、`@field` 等标签）。 |
| **扩展图示同步** | 若某章节含 PlantUML/HTML/Vega 等（见 doc-init Skill 融合表），代码变更波及该视图时一并修订对应块。 |
| **快照随写更新** | 写入文档后更新 `docs/.doc-snapshot.json`，便于下次增量；变更文件列表与哈希或提交号应与本次改动一致。 |
| **构建可验证** | 条件允许时在目标项目执行 `mdbook build`，修复因链接或预处理导致的失败后再收尾。 |

---

## Examples

| 内容 | 文件 |
|------|------|
| 变更检测、影响映射表、快照格式、命令语义示意 | [doc-update.md](examples/doc-update.md) |

---

## 工作流程摘要

1. **变更检测：** `git diff`、指定提交区间，或对照快照；记录变更文件列表与提交号。
2. **代码文件分析：** **完整分析所有变更代码文件**（`.c`、`.cpp`、`.h`、`.py`、`.java`、`.go`、`.ts`、`.js` 、`.sh`等），提取函数接口、结构体/类定义变化。
3. **影响分析：** 按变动类型映射到 `api.md`、`architecture.md` 等（见 [examples/doc-update.md](examples/doc-update.md)）；标注 **对外契约是否变化**。
4. **正文与图示更新：** 段落级修改、**Mermaid**、扩展图示块；**按 doxygen 格式更新 API 与类型文档**；更新交叉链接与 `SUMMARY.md`（若有新增或重命名）。
5. **一致性巡检：** 术语与 `glossary.md`、重复章节、`reference/` 与 `troubleshooting.md` 中与本次改动相关的条目。
6. **changelog：** 追加结构化条目（类型、摘要、路径、关联）。
7. **确认：** 展示变更摘要后写入（除非 `--no-prompt`）。
8. **快照与可选构建：** 刷新 `.doc-snapshot.json`；可选 `mdbook build` 验证。

---

## 与本项目其他 Skill 的配合

- **结构与原约定：** 始终以 [doc-init 示例](../doc-init/examples/doc-init.md) 为纲；扩展图示选型见其中 Skill 融合表。
- **常用链接：** [uml](../uml/SKILL.md)、[architecture](../architecture/SKILL.md)、[graphviz](../graphviz/SKILL.md)、[cloud](../cloud/SKILL.md)、[security](../security/SKILL.md)、[vega](../vega/SKILL.md)、[mindmap](../mindmap/SKILL.md)、[bpmn](../bpmn/SKILL.md)（按需打开，勿混用错误围栏）。
- **审查结论入库：** [code-review](../code-review/SKILL.md) 产出的摘要、趋势或合规说明可经本流程写入 `troubleshooting.md`、独立安全章节或 `changelog.md`（与用户确认章节位置）。

---

## Common Pitfalls

| 情况 | 处理 |
|------|------|
| 无 Git 且无快照 | 先做一次全量快照或完整 `doc-init`，再启用增量流程。 |
| 映射与仓库布局不符 | 与用户共同修订映射表，避免误改章节。 |
| 只改代码不改扩展图 | 检查该章节是否含 doc-init 融合表所列非 Mermaid 图示，避免文档与代码「半套一致」。 |
