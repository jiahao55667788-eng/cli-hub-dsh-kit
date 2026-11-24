# CLI-Hub DSH Kit

把 [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) 的 agent 原生 CLI 目录落到本机：
隔离 venv 装 `cli-hub`、PATH 直调、agent 技能可发现，并附一个**离线可搜索的试玩台**（GitHub Pages 静态页）。

> 一句话：任何软件 / 代码库 / Web API → 一条命令生成的 agent-native CLI → agent 直接操作，不用点 GUI。

- 试玩台：见仓库 Pages 首页（本文档所在仓库的 `docs/index.html`）
- 上游站点：<https://clianything.cc/>
- 上游仓库：<https://github.com/HKUDS/CLI-Anything>（Apache-2.0）

## 目录

```
cli-hub-dsh-kit/
├─ docs/index.html                 # 试玩台（单文件，无外链、无追踪，Pages 直接托管）
├─ site/build_site.py              # 试玩台生成器：registry 快照 + 本机安装台账 → docs/index.html
├─ data/*.snapshot.json            # 上游三份注册表快照（79 harness + 24 public + 5 matrix）
├─ scripts/install-cli-hub.ps1     # 一键复现安装（clone → venv → pip → shim → PATH → skill）
├─ skill/cli-hub-meta-skill/SKILL.md  # 供 DSH / Claude Code / Codex 发现的元技能
├─ INSTALL-NOTES.md                # 本机安装记录：路径、依赖、实测证据、坑、回滚
└─ LICENSE-upstream                # 上游 Apache-2.0 原文
```

## 一键安装（Windows / PowerShell）

```powershell
git clone <this-repo>
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-cli-hub.ps1
```

脚本做的事（每一步都可回滚，全部落在 `%USERPROFILE%\cli-anything`）：

1. `git clone --depth 1 https://github.com/HKUDS/CLI-Anything.git`
2. `python -m venv` 建私有环境（不碰系统 Python）
3. `pip install -e cli-hub` + `pip install uv`
4. 写 `cli-hub.cmd` shim（固化 `PYTHONUTF8=1`），把 shim 目录与 venv `Scripts` 追加到用户 PATH
5. 把 `cli-hub-meta-skill` 复制到 `%USERPROFILE%\.agents\skills\`

macOS / Linux 等价手动步骤：

```bash
git clone --depth 1 https://github.com/HKUDS/CLI-Anything.git ~/cli-anything
cd ~/cli-anything && python3 -m venv .venv
PYTHONUTF8=1 .venv/bin/pip install -e cli-hub uv
ln -sf ~/cli-anything/.venv/bin/cli-hub ~/.local/bin/cli-hub
mkdir -p ~/.agents/skills && cp -r cli-hub-meta-skill ~/.agents/skills/cli-hub-meta-skill
```

## 命令面

| 命令 | 作用 |
| --- | --- |
| `cli-hub list` | 全量目录（按分类） |
| `cli-hub search <词>` | 按名称 / 描述 / 分类检索 |
| `cli-hub info <name>` | 依赖、entry point、安装策略、当前状态 |
| `cli-hub install <name>` | 安装：harness 类 → pip（进 venv），public 类 → uv / npm |
| `cli-hub launch <name> -- --help` | 装完直接拉起，参数透传 |
| `cli-hub can "<任务>"` | 按能力反查矩阵，不知道装什么时用 |
| `cli-hub matrix list` | 5 条能力矩阵（视频 / 图像 / 知识研究 / 3D CAD / 游戏开发） |
| `cli-hub matrix install <name> [--only a,b] [--resume]` | 一次装齐一条工作流 |
| `cli-hub update / uninstall <name>` | 升级 / 卸载 |
| `cli-hub previews ...` | 预览包与实时会话（生成物可直接开浏览器） |

安装台账：`%USERPROFILE%\.cli-hub\installed.json`；矩阵状态：`matrix_state.json`（同目录）。

## 在 agent 里怎么用

技能 `cli-hub-meta-skill` 会被 DSH / Claude Code / Codex 自动发现。遇到"找个现成 CLI 干活"的需求：

```
skill cli-hub-meta-skill     # 先加载流程
cli-hub can "edit a video"   # 定位矩阵/能力
cli-hub install kdenlive     # 装
cli-anything-kdenlive --help # 当工具直接调用
```

## 试玩台

- 纯静态单文件：`docs/index.html`，数据内嵌，离线可用、无追踪脚本。
- 内容：103 条 CLI（79 harness + 24 public）、5 条矩阵、分类筛选、`/` 聚焦搜索、命令一键复制、深浅色、本机已装标记。
- 重新生成（数据或安装状态变化后）：

```bash
python site/build_site.py     # 需要 data/*.snapshot.json；会读 ~/.cli-hub/installed.json
```

## 已知坑

1. **GBK 编码炸 `pip install -e`**：上游 `setup.py` 用默认编码读文件，非 UTF-8 locale 下报
   `UnicodeDecodeError: 'gbk' codec can't decode byte`。设 `PYTHONUTF8=1` 即可（shim 已固化）。
2. **PATH 只对新进程生效**：装完重开终端；临时可用绝对路径 `%USERPROFILE%\cli-anything\.venv\Scripts\cli-hub.exe`。
3. **public 类需要 uv**：`source: public` 走 `uv tool install`，脚本已装 uv 并把 venv `Scripts` 前置进 PATH。
4. **harness 类要从 GitHub 拉**：`install_cmd` 形如
   `pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=<app>/agent-harness`，需要能访问 GitHub。
5. **GUI 软件本体仍要装**：CLI 只是控制面（走 socket / CLI / 文件），比如 Blender、Kdenlive 本机得先有。

## 回滚

```powershell
Remove-Item "$env:USERPROFILE\cli-anything" -Recurse -Force
Remove-Item "$env:USERPROFILE\.cli-hub" -Recurse -Force
Remove-Item "$env:USERPROFILE\.agents\skills\cli-hub-meta-skill" -Recurse -Force
# 再从用户 PATH 里去掉 cli-anything\.venv\Scripts 与 shim 目录两条
```

## 归属

- 目录内容、CLI 实现、注册表：**HKUDS/CLI-Anything**，Apache-2.0（见 `LICENSE-upstream`）。
- 本仓库只含：安装脚本、注册表快照、试玩台生成器与静态页、安装记录。无上游源码改动。
- Public CLI 条目归各自软件所有者，CLI-Hub 只做发现与安装编排。
