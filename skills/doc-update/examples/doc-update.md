# 文档增量更新（doc-update）

## 数据源与产出（原则）

- **事实源：** **目标项目代码仓库** 中的变更（Git diff / status 或相对 `docs/.doc-snapshot.json` 的差异）。
- **产出：** **同一项目** 内的 **Wiki/mdBook**（更新 `docs/src/`、`changelog.md`、快照等），使文档站与代码保持一致。

根据代码变更 **仅更新受影响文档**，同步 Mermaid、交叉引用与变更日志，并维护文档快照。

## 触发方式

输入 `/doc-update` 或要求「根据最新代码更新文档」。

## 能力说明

- 变更检测：Git diff / status，或无 Git 时对比 `docs/.doc-snapshot.json`。
- 影响分析：按文件类型映射到文档章节与关联文档。
- 支持预览待改范围、按模块或文档类型筛选、可选 `--force`、`--no-prompt`。

**与 doc-init 对齐：** Wiki 目录、`book.toml`、**mdBook + Mermaid 约定**以及 **与本仓库其他 skill 的融合表**以 [doc-init/examples/doc-init.md](../../doc-init/examples/doc-init.md) 为准；增量更新时同步修订其中涉及的 Mermaid 与扩展图示块，并做 **术语、glossary、changelog、SUMMARY** 一致性巡检（详见 doc-update SKILL 中「Wiki 增量更新的专业要求」）。

## 工作流程

### 1. 变更检测

- 优先：`git diff --name-only HEAD~1` 或与用户指定的提交区间对比。
- 辅助：`git status -s` 捕获工作区变更。
- 无 Git：对比快照中的哈希与时间戳。

### 2. 影响范围映射（示例）

| 变动类型 | 映射规则 | 可能关联文档 |
|----------|----------|----------------|
| HTTP 路由增改 | 更新 `api.md` 对应接口 | `architecture.md`、`modules/` |
| 类型 / 结构体增改 | 更新 `structures.md` | `api.md`、`principles.md` |
| 模块入口或组件增减 | 更新 `architecture.md` 与分层图 | `README.md`、`SUMMARY.md` |
| 算法或流程变更 | 更新 `principles.md` 与序列图 | `architecture.md`、`api.md` |
| 配置与启动脚本 | 更新 `usage.md` | `reference/environment.md` |
| 脚本工具变更 | 更新对应子模块文档 | `submodules/*/`、`modules/script_api.md` |
| 错误处理 / 错误码 | 更新 `troubleshooting.md` | `api.md` |

> 实际项目路径不同时，应先与用户确认映射表再执行批量替换。

### 3. 更新策略

- **段落级增量：** 只重写受影响小节，保留其余章节不动。
- **图表：** 重新生成或修补所有受影响的 Mermaid，使其与代码一致。
- **链接：** 更新文档内交叉引用与 SUMMARY 链接。
- **changelog：** 在 `changelog.md` 末尾追加日期、类型、摘要、受影响文件列表、issue/PR（若有）。

### 4. 预览与确认

- 展示将修改的文件与章节级摘要（类 diff 说明），确认后再写入。
- 用户可限定「只更新 API 文档」等；若约定 `--no-prompt` 则跳过交互。

### 5. 快照

更新 `docs/.doc-snapshot.json`，示例结构：

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "commit": "abc123",
  "files": {
    "src/main.c": "sha256:..."
  },
  "version": "1.0.0"
}
```

### 6. 文件级策略

- **新增源码文件：** 在对应模块文档中增加说明或小节。
- **删除源码文件：** 提示是否同步删除或归档文档段落。
- **重命名：** 更新文档内路径与 SUMMARY。

## 命令行约定（示意）

用户可在指令中携带类似语义（由 Agent 解析）：

```bash
/doc-update --all
/doc-update --api
/doc-update --module burnin
/doc-update --force --no-prompt
/doc-update --from abc123 --to def456
```

## 性能注意

- 大型仓库优先只做增量解析与增量渲染。
- 可缓存已解析的符号表，避免重复全库扫描。

---

## Wiki 专业输出自检清单（增量完成后）

- [ ] **契约：** 对外 API、类型、错误语义与仓库当前实现一致；破坏性变更在 `changelog.md`（及必要时 `usage.md`）已说明。
- [ ] **导航：** `SUMMARY.md` 与实际文件一致，无死链。
- [ ] **术语：** 与 `glossary.md` 一致，无同一概念多名。
- [ ] **图示：** 受影响 Mermaid/扩展图已按代码更新；单章节内无重复矛盾的多张「主架构图」。
- [ ] **运维：** `reference/`、`troubleshooting.md` 中与本次变更相关的条目已更新。
- [ ] **快照：** `.doc-snapshot.json` 已刷新；可选 `mdbook build` 通过。
