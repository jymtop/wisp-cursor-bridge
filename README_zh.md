# Wisp × Cursor 科研桥

<div align="center">

[English](README.md) · [简体中文](README_zh.md)

</div>

面向 [Wisp Science](https://github.com/xuzhougeng/wisp-science) 的 Cursor 侧适配。
Cursor 会员模型留在 Cursor 里。Wisp 工作流（技能 + 生物 MCP）经本仓库桥接。
科学状态写在磁盘上的 `wisp.handoff.v1`（[INTEROP.md](INTEROP.md)）。
**两侧聊天气泡不同步。**

本仓库**不会**把 Cursor 会员变成 Wisp 的 HTTP API Key，也不会嵌入 Wisp 桌面应用。

请在 Cursor 里打开 **Wisp 课题文件夹** 做科研，不要把本适配仓库当课题。

- 技能路由：[research/SKILL-CATALOG.md](research/SKILL-CATALOG.md)
- 当前状态：[research/HANDOFF.md](research/HANDOFF.md)

## 给其他用户（克隆这个 GitHub 地址）

**不要**粘贴别人的个人 Cursor User Rules。某台机器上的路径只是示例。

1. 克隆 [https://github.com/jymtop/wisp-cursor-bridge](https://github.com/jymtop/wisp-cursor-bridge)。
2. 在 Cursor 中打开**本仓库**（Claude Code 等会读 [AGENTS.md](AGENTS.md)）。
3. 第一次相关对话时，代理应运行安装检查并**提示你完成设置**（git、批准 MCP、
   给课题文件夹叠 overlay）。也可以自己跑：

```powershell
uv run --python 3.12 python -m tools.check_bridge_setup
```

检查脚本会打印一份提示清单。适配器模式：你打开的是桥仓库，科研请换课题文件夹；
`uv sync --python 3.12` **只**能在这里跑。课题模式：若 `.cursor/mcp.json` 没有
`wisp-bio`，按提示叠 overlay。

### 触发口令

在课题文件夹里说下面任一句话（或符合 Pattern 的近义说法）。触发后代理走
`.cursor/skills/ws-continue/SKILL.md`：必要时叠 overlay，读
`research/HANDOFF.md`，然后做你的 xxx 或 HANDOFF 的 `next`。

| 类别 | 口令 |
| --- | --- |
| 继续 / 接管 | 继续这个WS任务, 继续WS任务, 继续这个 Wisp 任务, 接管WS任务, 接上Wisp桥, 读HANDOFF继续, … |
| 这是 WS 任务 | 这是WS任务，帮我… / 请帮我… / 我要…; WS任务，帮我… |
| 换应用接着做 | 从Wisp转过来, 用Cursor接着做, 接着做这个WS |
| 英文 | `use the wisp-cursor bridge here`, `continue the WS task`, `wire the wisp bridge`, `take over this WS task` |
| Pattern | 含 (WS 或 Wisp 或 wisp 或 维斯普) **并且**含 (继续 / 接管 / 接上 / 接着 / 交接 / HANDOFF / 帮我 / 请帮我 / 我要 / 帮忙 / 桥 / 课题)，**或**以 这是WS / 这是Wisp / WS任务 / Wisp任务 开头 |

路径触发是**可选**的。若设置了 `WISP_TOPICS_ROOT`，或在
`.wisp/topics-root.local` 写一行路径（见 `.wisp/topics-root.local.example`），
该根目录下的工作区会自动视为课题。本适配仓库永远不算课题。

### 给课题文件夹叠 overlay

```powershell
uv run --directory <adapter-repo> --python 3.12 python -m tools.sync_wisp_skills --science <topic-folder>
```

不要在课题文件夹里运行 `uv sync`，也不要在那里添加 `pyproject.toml`。
仅当 `~/.cursor/mcp.json` 还没有 `wisp-bio` 时才加 `--user-mcp`。
首次叠加后：Reload Window；若 `wisp-bio`、`wisp-history`、`figure-library`
仍是灰色，在 Settings → Tools & MCP 中批准。

### 可选的短 User Rule（可移植）

把 `.cursor/skills/ws-continue/SKILL.md` 复制到
`~/.cursor/skills/ws-continue/SKILL.md`（或完成第一次 overlay）之后，
可以加一段短规则。不要粘贴别人的个人规则。

```
Follow ~/.cursor/skills/ws-continue/SKILL.md (or .cursor/skills/ws-continue/SKILL.md).
If this workspace is under WISP_TOPICS_ROOT or .wisp/topics-root.local, treat it as a WS topic folder.
Never treat a wisp-cursor-bridge clone (INTEROP.md + gateway/ + tools/sync_wisp_skills.py) as a science folder.
Spoken: 继续WS任务, 接上Wisp桥, 读HANDOFF继续, 这是WS任务，帮我…, continue the WS task, wire the wisp bridge.
After a trigger: overlay if needed, read research/HANDOFF.md, do the user's xxx or HANDOFF next.
Never uv sync in a topic folder. Do not pass --user-mcp unless ~/.cursor/mcp.json has no wisp-bio.
```

**回到 Wisp：** 打开同一个课题文件夹，说 `读 HANDOFF 继续`。

## 安装（Python 3.12）

只在本适配仓库运行：

```powershell
uv sync --python 3.12
uv run --python 3.12 pytest
uv run --python 3.12 python -m tools.check_bridge_setup
uv run --python 3.12 python -m tools.sync_wisp_skills
```

实网数据库调用（PubMed、GEO 等）需要给 `wisp-bio` 设置 `WISP_BIO_LIVE=1`。
许可未决工具（KEGG、CADD、PanglaoDB、Cell Model Passports）保持关闭。

## 日常用法

1. 在 Wisp 和 Cursor 中打开**同一个课题文件夹**（不要打开本适配仓库）。
2. 在 Cursor 里用上面的口令，或 `/wisp-handoff`。科研步骤应走 Wisp 技能，
   并用 `search_bio_tools` / `use_bio_tool`。
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
| `tools/check_bridge_setup.py` | 给新克隆用的 git + overlay 提示清单 |
| `vendor/wisp-science/` | 钉住的 Apache-2.0 技能与 bio-tools |

## 许可证

适配代码为 Apache-2.0。vendored 的 `skills/` 与 `mcp-servers/bio-tools/`
来自 Wisp Science（Apache-2.0 资源包）。Wisp 桌面应用为 AGPL-3.0，
未纳入本仓库。见 [NOTICE](NOTICE)。
