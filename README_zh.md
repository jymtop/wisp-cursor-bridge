# Wisp × Cursor 科研桥

<div align="center">

[English](README.md) · [简体中文](README_zh.md)

</div>

面向 [Wisp Science](https://github.com/xuzhougeng/wisp-science) 的 Cursor 侧适配。
Cursor 会员模型留在 Cursor 里。Wisp 工作流（技能 + 生物 MCP）经本仓库桥接。
科学状态写在磁盘上的 `wisp.handoff.v1`（[INTEROP.md](INTEROP.md)）。
**两侧聊天气泡不同步。**

请在 Cursor 里打开 **Wisp 课题文件夹**，不要打开本适配仓库。

- 技能路由：[research/SKILL-CATALOG.md](research/SKILL-CATALOG.md)
- 当前状态：[research/HANDOFF.md](research/HANDOFF.md)

本仓库**不会**把 Cursor 会员变成 Wisp 的 HTTP API Key，也不会嵌入 Wisp 桌面应用。

## 从 Cursor 继续 WS 任务

**路径触发。** 若 Cursor 工作区位于 Wisp 课题根目录下（示例：`D:\AI4S_WispScience\`），
即自动视为 Wisp Science（WS）课题文件夹。本适配仓库永远不算课题目录。

**口令触发**（不在上述根目录下也可以）：

- 继续 / 接管 / 接上 + WS / Wisp + 任务 / 桥
- 这是WS任务，帮我…
- 读HANDOFF继续
- 英文：`continue the WS task`、`use the wisp-cursor bridge here`、
  `take over this WS task`、`read HANDOFF and continue`

Cursor 用户规则应指向 `~/.cursor/skills/ws-continue/SKILL.md`。

**叠技能与 MCP**（可在任意目录执行；Python 3.12）。不要在课题文件夹里运行
`uv sync`。`uv sync --python 3.12` **只**在本适配仓库执行。

```powershell
uv run --directory <adapter-repo> --python 3.12 python -m tools.sync_wisp_skills --science <topic-folder>
```

`--user-mcp` 可选，最多用一次，且仅当本机还没有用户级 MCP 时才需要。

首次叠加后，重载 Cursor 窗口；若 `wisp-bio`、`wisp-history`、`figure-library`
仍是灰色，在 Settings → Tools & MCP 中批准。

**回到 Wisp：** 打开同一个课题文件夹，说 `读 HANDOFF 继续`。

## 安装（Python 3.12）

只在本适配仓库运行：

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.sync_wisp_skills
```

实网数据库调用（PubMed、GEO 等）需要给 `wisp-bio` 设置 `WISP_BIO_LIVE=1`。
许可未决工具（KEGG、CADD、PanglaoDB、Cell Model Passports）保持关闭。

## 日常用法

1. 在 Wisp 和 Cursor 中打开**同一个课题文件夹**（不要打开本适配仓库）。
2. 在 Cursor 里用上面的路径或口令触发，或 `/wisp-handoff`。
   科研步骤应走 Wisp 技能，并用 `search_bio_tools` / `use_bio_tool`。
3. 结果写进文件。更新 `research/HANDOFF.md`（`last_app: cursor`）。
4. 回到 Wisp：`读 HANDOFF 继续`。内核变量不会带到另一边；请重跑
   `research/scripts/`。

之后在 Wisp 里安装的插件：先在 Wisp 安装，再运行
`python -m tools.sync_wisp_skills`。

## 目录

| 路径 | 归属 |
| --- | --- |
| `research/`、`.wisp/WISP.md`、`.wisp/memory/` | 共享（`wisp.handoff.v1`） |
| `.cursor/`、`gateway/`、`tools/` | 仅 Cursor |
| `gateway/` | `wisp-bio`（约 247 个生物工具收成 3 个入口）与只读 `wisp-history` |
| `tools/sync_wisp_skills.py` | 把 Wisp / 插件的 `SKILL.md` 镜像到 `.cursor/skills/` |
| `vendor/wisp-science/` | 钉住的 Apache-2.0 技能与 bio-tools |

## 许可证

适配代码为 Apache-2.0。vendored 的 `skills/` 与 `mcp-servers/bio-tools/`
来自 Wisp Science（Apache-2.0 资源包）。Wisp 桌面应用为 AGPL-3.0，
未纳入本仓库。见 [NOTICE](NOTICE)。
