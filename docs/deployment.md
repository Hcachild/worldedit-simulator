# 部署与安装

本文覆盖从零部署、离线/本机复用、升级和验收。遇到具体报错先看 [troubleshooting.md](troubleshooting.md)。

## 环境要求

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 10/11 x64 |
| Python | 3.10+，命令为 `python` |
| 网络 | 首次需要访问 EngineHub、Adoptium、Mojang；可重试 |
| 浏览器 | Edge / Chrome（需要 WebGL） |
| 磁盘 | 项目约 205MB（JRE 约 195MB）+ CLI jar 23MB + 客户端资源 27MB |
| 端口 | 本机 `127.0.0.1:8777`，不对外网开放 |

## 从零部署

```bat
git clone git@github.com:Hcachild/worldedit-simulator.git
cd worldedit-simulator
setup.cmd
web.cmd
```

`setup.cmd` 做三件事，已存在的文件会跳过：

1. 下载 `bin/worldedit-cli-7.4.7-SNAPSHOT-dist.jar`。
2. 下载并解压 Temurin JRE 25 到 `jdk-25.0.4.1+1-jre/`。
3. 下载 Minecraft 1.21.1 客户端 jar 到 `assets/client.jar`（约 27MB）。

启动后浏览器自动打开 <http://127.0.0.1:8777/>，默认空界面。

只补材质：

```bat
setup-assets.cmd
```

## 离线或已有环境

- 已安装 Minecraft 1.21.1：`tools\fetch_assets.py` 会优先从
  `%APPDATA%\.minecraft\versions\1.21.1\1.21.1.jar` 复制，不需要重新下载。
- 已有 CLI jar 和 JRE：`setup.cmd` 会直接跳过对应步骤。
- 完全离线：把 `assets/client.jar`、`bin/worldedit-cli-*.jar`、`jdk-25.0.4.1+1-jre/`
  放到对应位置即可；前端不会访问外网（Three.js、解析库、WASM 都在本地）。
- CLI 的方块表按 DataVersion 缓存到 `worldedit/cli-data/<DataVersion>_1.json`；
  第一次使用某个版本仍需要联网下载，或提前运行 `tools\ensure_data.py`。

## 启动方式

| 方式 | 命令 | 说明 |
|---|---|---|
| 3D 页面 | `web.cmd` | 启动本地 HTTP 服务并自动打开浏览器 |
| 纯 CLI | `we.cmd <file.schem> [commands.txt]` | 无 3D 页面，直接改投影 |
| 单独下载材质 | `setup-assets.cmd` | 只处理 `assets/client.jar` |
| 检查方块表 | `python tools\ensure_data.py <file.schem>` | 预下载/验证 DataVersion 数据 |

已有页面实例时再次运行 `web.cmd` 只会打开页面，不会重复启动服务，也不会清掉正在编辑的
`work/current.schem`（服务端在绑定端口后才创建工作区）。

## 目录与数据契约

| 路径 | 是否入库 | 说明 |
|---|---|---|
| `schematics/` | 仅 `.gitkeep` | 用户投影；`.schem` 文件被 `.gitignore` 忽略 |
| `assets/` | 否 | 下载的 1.21.1 客户端 jar，本地渲染使用，不随仓库分发 |
| `work/` | 否 | 当前编辑副本 `current.schem`，启动时清理 |
| `worldedit/` | 否 | CLI 工作目录：配置、语言缓存、方块表、空目录 |
| `logs/` | 否 | 正常不会生成；CLI 日志被 `bin/log4j2.xml` 改为只写控制台 |
| `bin/` | 部分 | `log4j2.xml` 入库；CLI jar 由 setup 下载 |
| `jdk-25.0.4.1+1-jre/` | 否 | setup 下载 |
| `web/static/vendor/` | 是 | Three.js、block-model-renderer、WASM |
| `web/static/assets.zip` | 是 | 解析库自带的方块实体覆盖包（约 233KB） |

## 验收清单

```bat
python tools\inspect_schem.py examples\demo.schem
copy examples\demo.schem schematics\demo.schem
we.cmd schematics\demo.schem examples\demo.txt
python tools\inspect_schem.py schematics\demo.schem
```

预期：demo 为 13×8×13，初始 730 个非空气方块；执行脚本后出现金块屋顶、白桦墙和浅蓝玻璃。

页面验收：

1. 打开页面，应只有 3D 网格和侧栏，没有欢迎弹窗或操作指引。
2. 点击 `schematics/` 中的文件，3D 区域应显示**真实材质和方块形状**（不是纯色立方体）。
3. 点击方块，HUD 显示方块 ID 和坐标。
4. 输入 `//gen minecraft:stone x^2+y^2+z^2<=1`，点运行，应生成球体并显示未保存圆点。
5. 点保存，圆点消失；刷新页面后仍是同一结果。
6. 外部 Agent：

```bat
python tools\agent_run.py --command "//pos1 0,0,0`n//pos2 3,3,3`n//set minecraft:glass"
```

页面应自动刷新并提示「AI 已更新」，不需要手动刷新。

## 升级

1. 替换 `bin/worldedit-cli-*.jar`，同时更新 `core/worldedit.py` 和 `setup.cmd` 中的文件名/下载地址。
2. 如果要换 Minecraft 资源版本，替换 `assets/client.jar`，并同步修改：
   - `web/static/js/mc-renderer.js` 的 `ASSET_VERSION`
   - `tools/fetch_assets.py` 的 `VERSION`
   - README 中的版本说明
3. 删除旧的 `worldedit/cli-data/` 可强制重新下载方块表（会重新联网）。
4. 清浏览器缓存或普通刷新；静态文件使用 `no-cache`，一般不需要硬刷新。

## 网络与下载

- EngineHub CLI：`https://ci.enginehub.org/...`，构建产物名含 `worldedit-cli-*-dist.jar`。
- EngineHub 方块表：`https://services.enginehub.org/cassette-deck/we-cli-data/<DataVersion>/1`。
- Mojang 客户端：`https://piston-meta.mojang.com/...` 和 `https://piston-data.mojang.com/...`。
- 国内网络可能间歇性 reset/timeout：`setup`/`fetch_assets` 已带 5 次重试；Mojang 失败会尝试
  BMCLAPI 镜像；EngineHub 数据下载由 `tools/ensure_data.py` 带超时处理。
- 不要关闭 SSL 校验；不要为了重试把 `--retry` 无限放大。

## 备份与清理

- 需要备份的只有：`schematics/`、`examples/`、`config` 类文件（本项目的 `core`、`web`、`tools`）。
- `work/`、`worldedit/`、`assets/`、JRE 都可重建，不必备份。
- 清理后首次启动会重新生成运行时目录；不会修改 `schematics/` 源文件。
- `assets/client.jar` 是 Minecraft 客户端资源，仅限本地渲染使用，不要提交到仓库或再分发。

## 部署常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| `UnsupportedClassVersionError` / class file 69 | 用了系统 Java 17 | 必须用目录内 JRE 25，或设置 `JAVA` 为 25 |
| CLI 无输出、像卡死 | Java URL 下载无超时，访问 EngineHub 数据失败 | 用 `ensure_data.py` 预下载；检查网络 |
| `No CLI data published for DataVersion` | 该版本没有官方方块表（如 1.20.1、1.21.9+） | `retarget_schem.py` 改到受支持版本 |
| `setup.cmd` 下载 JRE 失败 | `%2B` 在批处理里未转义 / 网络 | 脚本已用 `%%2B`；重试或手动放 JRE |
| 页面只有颜色方块 | `assets/client.jar` 缺失或版本不对 | 运行 `setup-assets.cmd`，F5 |
| 3D 页面 404/空白 | 服务未启动、端口被占、浏览器旧缓存 | 看控制台/`web.cmd`；访问 8777；F5 |
| 运行命令弹 CMD | 旧版本未用隐藏子进程 | 使用当前版本；网页模式应有 `CREATE_NO_WINDOW` |
| 页面不自动刷新 | 旧标签页或 SSE 断开 | F5；检查 `/api/events` |
| `//gen` 生成 0 个方块 | 默认坐标是 -1..1，不是方块坐标 | 用归一化公式，或加 `-c`/`-r` |
| 安装后文件列表为空 | 正常：`schematics/` 初始为空 | 上传或从 `examples/` 复制示例 |

更多排错见 [troubleshooting.md](troubleshooting.md)。
