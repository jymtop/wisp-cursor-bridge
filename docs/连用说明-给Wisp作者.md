# 给 Wisp Science 作者：Cursor 作为第二客户时的连用方式

收件人：Wisp Science 维护者（https://github.com/xuzhougeng/wisp-science ，站点 https://wispscience.com/）。  
发送人：使用者侧适配（桥仓库 https://github.com/jymtop/wisp-cursor-bridge ）。  
规范名：`wisp.handoff.v1`（全文：[INTEROP.md](../INTEROP.md)）。  
MCP 标准：https://modelcontextprotocol.io/

本文只谈**产品边界和建议合入点**，不要求你们改桌面架构。Cursor 专属路径（`.cursor/`）不是本协议的一部分。

---

## 1. 使用者实际在做什么

部分用户同时有 **Wisp** 和 **Cursor 会员**。他们希望：

- 科研流程、技能名称、生物数据库仍按 Wisp 的方式走；
- 模型额度花在 Cursor 上；
- 当天在 Cursor 做的文献/分析，第二天能在 Wisp 里接着做。

做不到、也不应做的：

- 把 Cursor 会员变成 Wisp「设置 → 模型」里的 HTTP API Key（Cursor 无对外部的稳定官方推理 API）；
- 把两侧聊天气泡做成双向同步（Wisp 的 `.wisp/wisp.sqlite` 与 Cursor 会话库不是同一套）；
- 在 Cursor 扩展里嵌入完整 Wisp 桌面（Tauri）再回调会员模型。

**可行的产品形状**：两边打开**同一课题目录**；科学状态用目录契约交接；Cursor 通过 MCP 复用你们已经发布的 bio-tools / 插件 MCP，而不是另写一套数据库客户端。

---

## 2. 建议你们认的契约（已在用）

只要课题根目录遵守 `wisp.handoff.v1`，今天用户就可以在 Wisp 里说「读 HANDOFF 继续」，**你们不必先改代码**。你们已经会读 `AGENTS.md`、`.wisp/WISP.md`，并能搜 `.wisp/memory/*.md`。

| 路径 | 含义 |
| --- | --- |
| `research/HANDOFF.md` | 唯一当前状态。后写覆盖。含 `last_app` / `next` / `key_files` |
| `research/sessions/{app}-YYYY-MM-DD-slug.md` | 分段笔记。`app` = `wisp` \| `cursor` \| … |
| `research/scripts/` | 可重跑分析（默认 Python 3.12） |
| `.wisp/memory/*.md` | 短事实，供 `search_memory` |
| `AGENTS.md` / `.wisp/WISP.md` | 课题级说明；不得和 HANDOFF 打架 |

技能对外名称请保持稳定：`literature-review`、`analysis-workflow`、`singlecell-qc`、`pdf-explore`、`public-data-access`、`figure-composer`、`paper-narrative`、`local-env-setup`。Cursor 侧按同名镜像，避免两套术语。

聊天气泡**不在**本契约内。

---

## 3. 建议合入 Wisp 的最小改动

按优先级：

1. **新会话若存在 `research/HANDOFF.md`，与 `AGENTS.md` 一样自动注入。**  
2. **`/handoff` 或回合结束时**：重写 HANDOFF（`last_app: wisp`），写 `research/sessions/wisp-*.md`，重要事实追加 `.wisp/memory/`。  
3. **可选**：把 `research/sessions/cursor-*.md` 列进「外部会话」列表（类似现有 Codex/Claude 导入），只读文件即可，不必解析 Cursor 专有库。  
4. 文档里引用规范名 `wisp.handoff.v1`。

这四条不绑定 Cursor；Claude / Codex / 以后别的客户也能用同一目录。

---

## 4. 工具层：我们怎么复用你们的 MCP（供参考，非协议）

Cursor 不适合一次挂载约 247 个 bio 工具。桥侧做了 **3 工具网关**：

- `list_bio_domains`
- `search_bio_tools`
- `use_bio_tool`

实现读你们 vendored 的 `mcp-servers/bio-tools` 目录与 `domains.json`。实网调用用环境变量打开（`WISP_BIO_LIVE=1`）。  
**许可未决工具保持关闭**：KEGG、CADD、PanglaoDB、Cell Model Passports——与你们 `deferred.json` 对齐。

插件（例如 figure-library）按 `plugin.json` 的 `mcp_servers` 原样拉进 Cursor 的 MCP 列表，不改插件协议。

会话库：提供**只读** MCP，指向桌面 `wisp.sqlite`，不写入。这是调试用，不是交接主通道；交接主通道仍是 HANDOFF 文件。

---

## 5. 请你们不必支持的

- 把 Cursor 当作 Wisp 的模型供应商；  
- 双向同步聊天气泡；  
- 在协议里写死 `.cursor/` 或某家 IDE 的配置格式。

---

## 6. 我们希望听到的反馈

1. `wisp.handoff.v1` 的字段是否要增删（例如是否要 `last_app` 枚举扩展）。  
2. 自动注入 HANDOFF 是否愿意进主线。  
3. 3-工具网关是否值得做成你们官方的「给外部 IDE 的 bio MCP 剖面」，避免每个客户自己摊 247 个 tool。  
4. 技能改名时能否有一份稳定别名表，方便镜像。

联系与实现：桥仓库 README 与 [INTEROP.md](../INTEROP.md)。规范变更请以 INTEROP 为准，本文是给作者的导读。
