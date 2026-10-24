# 排错手册

先收集三样东西：

1. 浏览器 F12 Console / Network 的报错。
2. `%TEMP%\worldedit-simulator-web.log`（后台模式）。
3. `GET http://127.0.0.1:8777/api/state` 和 `/api/files` 的返回。

## 启动与依赖

| 现象 | 原因 | 处理 |
|---|---|---|
| `UnsupportedClassVersionError ... class file version 69` | 用了 Java 17/21，而 CLI 7.4.7 用 Java 25 编译 | 使用 `jdk-25.0.4.1+1-jre`；不要用系统 Java |
| `java`/`python` 不是命令 | PATH 问题 | 安装 Python 3.10+；脚本使用目录内 JRE |
| `setup.cmd` 下载失败 | 网络 reset/timeout | 重试；`setup-assets.cmd` 单独补资源；离线放置文件 |
| JRE 下载 URL 的 `%2B` 出错 | 批处理转义 | 当前 `setup.cmd` 使用 `%%2B`；不要手工改成 `%2B` |
| `web.cmd` 一闪而过 | 端口被占/缺少依赖 | 看控制台；`python web\server.py` 手动运行看 traceback |
| 浏览器打不开 | 服务未启动/端口不是 8777 | 检查 `Get-NetTCPConnection -LocalPort 8777`；看日志 |

## CLI / DataVersion

| 现象 | 原因 | 处理 |
|---|---|---|
| CLI 卡住无输出 | `FileRegistries` 用无超时的 `URL.openStream()` 下载方块表 | 运行 `python tools\ensure_data.py file.schem` 预下载；检查网络 |
| `No CLI data published for DataVersion X` | EngineHub 没有该版本数据（如 3465、4556+） | `python tools\retarget_schem.py file.schem <supported>` |
| `Failed to obtain data version` | `.schem` 没有 `DataVersion` | 用 WorldEdit 重新保存，或补元数据 |
| `不是 Sponge .schem 文件` | 根 NBT 名不是 `Schematic` / 旧 `.schematic` | 转换为 Sponge `.schem` |
| 改版本后新方块丢失/未知 | `retarget` 只改元数据 | 用与方块匹配的版本；不要向下改新投影 |
| 命令报未知方块 | 方块不在该 DataVersion 的方块表 | 查版本方块；换成该版本存在的方块 |
| `//schem save` 报空剪贴板 | 没有先 `//copy` | 先 `//copy`，或让 CLI 自动保存当前文件 |

支持的 CLI 数据版本（实测）：

```
1.20.3 3698, 1.20.4 3700, 1.20.5 3837, 1.21 3953, 1.21.1 3955,
1.21.2 4080, 1.21.4 4189, 1.21.5 4325, 1.21.6-1.21.8 4435/4438/4440
```

缓存位置：`worldedit/cli-data/<DataVersion>_1.json`。删除可强制重下。

## 页面与渲染

| 现象 | 原因 | 处理 |
|---|---|---|
| 只有颜色方块，没有真实材质 | 缺少 `assets/client.jar`、404 或版本不匹配 | 运行 `setup-assets.cmd`；F5；看 Network |
| 形状都是立方体 | 回退渲染（资源加载失败）或旧标签页 | F5；检查 Console toast/`client.jar` |
| 页面空白 | JS 报错/WebGL 不可用 | F12 Console；更新 Edge/Chrome；检查 `vendor` 文件 |
| 模型不显示但方块数正常 | 资源解析失败/模型未构建完成 | 等构建；看 `[render]` 指标和 toast |
| 台阶/楼梯/植物形状错误 | 资源版本与方块状态不匹配 | 用 1.21.1 投影；或换对应版本资源 |
| 玻璃不透明/全白 | 半透明检测或资源缺失 | 确认客户端 jar；库按纹理 alpha 判定 |
| 页面不自动刷新 | 旧标签页没有 `live.js` 或 SSE 断开 | F5；检查 `/api/events`；看 Network |
| 外部命令后页面提示「AI 已更新」但模型旧 | 模型正在构建/构建被取消 | 等构建完成；看 revision 是否增加 |
| 点击方块没有信息 | 拾取层未构建/旧页面 | F5；确认方块非空气 |

前端静默回退时会有 toast：「缺少材质包，已使用颜色方块」或「模型渲染失败」。真实材质需要
`assets/client.jar` 和 `web/static/assets.zip`、WASM 都能访问。

## 端口、实例与状态

| 现象 | 原因 | 处理 |
|---|---|---|
| `Address already in use` | 已有实例 | `web.cmd` 会检测并打开页面；不要重复启动 |
| 第二次启动后正在编辑的文件丢了 | 旧版在端口检查前创建工作区 | 当前版本已修复；升级到最新 |
| 页面显示未保存圆点 | 命令改的是 `work/current.schem` | 点「保存」写回 `schematics/` 源文件 |
| 关闭/删除当前文件后 3D 空 | 正常行为，工作副本被丢弃 | 重新载入或从 `schematics/` 选择 |
| 下载/另存为得到旧内容 | 未保存工作副本 | 先保存，或下载当前工作副本（不带 name） |

## 进程与窗口

| 现象 | 原因 | 处理 |
|---|---|---|
| 每运行一次弹 CMD | 旧版 Java 子进程未隐藏 | 当前版使用 `CREATE_NO_WINDOW`；F5/更新 |
| 关闭页面后 Java 仍在 | 命令正在执行/超时前 | 等待；超时 180s 会终止；不要同时多开命令 |
| 端口被其他程序占用 | 非本服务 | 改 `web/server.py` 的 `PORT`，或结束占用进程 |
| 日志文件找不到 | 后台日志在 `%TEMP%` | 见 `worldedit-simulator-web.log` |

## 外部 Agent

| 现象 | 原因 | 处理 |
|---|---|---|
| `/api/run` 返回「还没有载入投影」 | 空工作区 | 先 `/api/load` 或 `/api/new` |
| 页面没变化 | 旧页面/SSE 断开/actor 非 agent | F5；看 `/api/events`；传 `"actor":"agent"` |
| 命令成功但方块没变 | 选择为空/表达式不匹配/方块 ID 错 | 看 `log`；先 `//pos1`/`//pos2` |
| `//gen` 生成 0 个 | 默认坐标是归一化 -1..1 | 用 `x^2+y^2+z^2<=1`，或加 `-c`/`-r` |
| 端口能从外网访问 | 误改绑定地址/端口映射 | 保持 `127.0.0.1`；远程用隧道和鉴权 |

## 恢复步骤

按顺序尝试：

```bat
python tools\fetch_assets.py
python tools\ensure_data.py examples\demo.schem
python tools\inspect_schem.py examples\demo.schem
```

仍异常时：

1. 停止 `pythonw`/`web.cmd`。
2. 删除 `work/`（当前未保存副本会丢失）。
3. 删除 `worldedit/cli-data/`（下次重新下载方块表）。
4. 删除 `assets/client.jar`，重新 `setup-assets.cmd`。
5. 重新 `web.cmd`，F5。

不要删除 `schematics/`、`examples/`、`core/`、`web/`、`bin/log4j2.xml`。
