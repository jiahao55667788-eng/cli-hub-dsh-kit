# 本机安装记录（脱敏版）

安装时间：2026-11-24 · 平台：Windows 11 + PowerShell 7 + Python 3.11
来源：<https://clianything.cc/> · <https://github.com/HKUDS/CLI-Anything>
版本：`cli-anything-hub` 0.4.1（editable，从本地 checkout 安装）

## 落地位置

| 项目 | 路径（`%USERPROFILE%` 为用户目录） |
| --- | --- |
| 仓库 clone（registry + 200+ 应用目录 + docs/demos） | `%USERPROFILE%\cli-anything` |
| 隔离 venv | `%USERPROFILE%\cli-anything\.venv` |
| `cli-hub` 可执行 | `…\.venv\Scripts\cli-hub.exe` |
| PATH 转发 shim（固化 UTF-8） | `%USERPROFILE%\.dsh\bin\cli-hub.cmd` |
| 用户 PATH 追加项 | `…\.venv\Scripts` |
| 安装台账（cli-hub 自管） | `%USERPROFILE%\.cli-hub\installed.json` |
| 矩阵状态 | `%USERPROFILE%\.cli-hub\matrix_state.json` |
| Agent 技能 | `%USERPROFILE%\.agents\skills\cli-hub-meta-skill\SKILL.md` |

## 依赖

- pip：`click 8.5.1`、`requests 2.34.2`、`urllib3 2.8.0`、`certifi`、`idna`、`charset_normalizer`
- `uv 0.13.9`（venv 内，供 `source: public` 走 `uv tool install`）

## 实测证据

```
cli-hub --version                  -> cli-hub 0.4.1
cli-hub list                       -> 分类目录正常（3D / AI / video / …）
cli-hub search video               -> kdenlive / shotcut / openscreen / videocaptioner / quietshrink
cli-hub matrix list                -> 3d-cad, game-development, image-design, knowledge-research, video-creation
cli-hub info mermaid               -> entry cli-anything-mermaid · harness · pip
cli-hub install mermaid            -> ✓ Installed Mermaid (cli-anything-mermaid)
cli-anything-mermaid --help        -> diagram / export / project / repl / session
```

DSH 侧：技能目录写入后，会话 `available_skills` 立即出现 `cli-hub-meta-skill`（无需重启）。

矩阵规模（dry-run 计划）：video-creation 14 · image-design 7 · knowledge-research 13 · 3d-cad 6 · game-development 9。

## 已知坑

1. **`pip install -e` 遇 GBK**：上游 `setup.py` 用默认编码读文件，非 UTF-8 locale 报
   `UnicodeDecodeError: 'gbk' codec can't decode byte 0x94`。设 `PYTHONUTF8=1` 后通过；shim 已固化。
2. **PATH 只对新进程生效**：旧终端需重开，或用绝对路径。
3. **`source: public` 需要 uv**：`shutil.which("uv")` 必须命中，shim 把 venv `Scripts` 前置进 PATH。
4. **harness 包从 GitHub 拉**：`pip install git+https://github.com/HKUDS/CLI-Anything.git#subdirectory=…`。
5. **CLI 不等于软件本体**：控制面之外，目标 GUI 软件要另行安装。

## 回滚

```powershell
Remove-Item "$env:USERPROFILE\cli-anything"     -Recurse -Force
Remove-Item "$env:USERPROFILE\.cli-hub"         -Recurse -Force
Remove-Item "$env:USERPROFILE\.agents\skills\cli-hub-meta-skill" -Recurse -Force
# 再从用户 PATH 移除 cli-anything\.venv\Scripts 与 shim 目录
```
