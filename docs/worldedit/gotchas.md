# 踩坑清单

按项目实测整理。更细的报错见 [../troubleshooting.md](../troubleshooting.md)。

## `//gen` 球体生成 0 个方块

**现象**

```text
//pos1 0,0,0
//pos2 15,15,15
//gen stone (x-7.5)^2+(y-7.5)^2+(z-7.5)^2<=49
```

日志：`已创建 0 个方块`。

**原因**：`//gen` 默认把选区归一化到 `-1..1`，不是方块坐标 0..15。`x-7.5` 远远超出范围。

**正确写法**

```text
//gen stone x^2+y^2+z^2<=1
```

或按真实半径：

```text
//gen -c stone x^2+y^2+z^2<=7^2
```

`-c` 原点在选区中心、1 方块=1 单位；`-r` 原始世界坐标；`-o` 以放置点为原点。

## CLI 没有玩家

- `//pos1`/`//pos2` 不带坐标 → 依赖玩家位置，不可用；必须 `//pos1 x,y,z`。
- `//hpos1/2`、`//wand`、`//chunk`、`//up`、`//thru`、`//jumpto`、`//ascend`、`//descend`、
  `//ceil` 等依赖玩家/视线，不可用。
- `/tool`、`/brush`、`/mask`（笔刷用）、`/material`、超级镐需要手持物品，不可用。
- `//regen` 需要世界生成器，投影里不可用。
- 替代：区域命令 + `//gen`（见 [tools-brushes.md](tools-brushes.md)）。

## DataVersion

- CLI 按 `.schem` 的 `DataVersion` 加载方块表；没有 `DataVersion` 会失败。
- 官方只发布部分版本的数据；1.20.1、1.21.9+ 等会 `No CLI data published`。
- `retarget_schem.py` 只改元数据：
  - 旧 → 新通常可用；
  - 新 → 旧可能丢失新方块/状态。
- 3D 材质固定 1.21.1，和 CLI 数据版本不是同一件事；其他 DataVersion 的方块可能没有贴图/模型。

## 方块表下载卡死

CLI 内部用无超时的 `URL.openStream()` 下载 `we-cli-data/<dv>/1`。网络不通会一直等。

- 运行 `python tools\ensure_data.py file.schem` 预下载（带 Python/curl 超时）。
- 缓存：`worldedit/cli-data/<dv>_1.json`。
- 下载失败会报错而不是挂住；`core/workspace.py` 在运行前检查缓存。

## `.schem` 格式

- 根 compound 名必须是 `Schematic`，否则 CLI/解析器不认。
- 只支持 1.13+ Sponge `.schem`；旧 `.schematic` 本项目 Web 拒绝。
- 必须有 `DataVersion`。
- 方块索引是 varint，顺序 `(y*Length+z)*Width+x`。
- `//schem save` 保存的是剪贴板，不是选区；先 `//copy`。
- CLI 会自动保存载入的文件，不需要 `//schem save`。

## Java 版本

- 7.4.7 用 Java 25 编译（class 69）；系统 Java 17 报 `UnsupportedClassVersionError`。
- 必须用目录内 `jdk-25.0.4.1+1-jre`，或显式指定 Java 25。
- `setup.cmd` 下载的 JRE 是 x64；ARM64/其他架构需自行替换。

## 启动与实例

- 端口 `8777` 固定；二次启动只打开页面，不重复启动。
- 旧版本曾在端口检查前创建工作区，二次启动会清掉 `work/current.schem`；当前版本已修复。
- `web.cmd` 是控制台程序；网页模式的 Java/curl 子进程隐藏窗口，不弹 CMD。
- `we.cmd` 本身是控制台程序，只有命令行模式出现。

## 保存语义

- 页面/Agent 命令改的是 `work/current.schem`；点“保存”才覆盖 `schematics/` 源文件。
- 关闭/删除当前文件会丢弃未保存副本；先保存。
- 重命名当前文件会同步更新会话名；复制不会切换当前文件。
- 删除不可恢复；没有回收站。

## 材质 / 渲染

- 真实材质需要 `assets/client.jar`（1.21.1）+ `web/static/assets.zip` + WASM。
- 缺失时回退颜色方块，并 toast 提示；这是降级，不是正常效果。
- 资源版本和投影 DataVersion 不一致时，新方块可能缺失或状态名不同。
- 首次加载 27MB；之后浏览器缓存 + prepared assets 复用。
- 页面卡顿/黑屏先看 F12 Console 与 `[render] {drawCalls,tris}`。
- 自动化截图不要用 `msedge --screenshot` 打开带 SSE 的页面（长连接可能不退出）；用 CDP
  `Page.captureScreenshot`。

## SSE / 实时刷新

- 外部 `/api/run` 后页面不自动更新：旧标签页没有 `live.js`，按 F5。
- SSE 断线会自动重连；重连时按当前 revision 重新应用。
- `actor` 不传默认 `user`，仍会刷新但不显示「AI 已更新」；要提示就传 `actor:"agent"`。
- 大投影每次变更发完整快照；需要增量时自行扩展。

## 网络

- GitHub/EngineHub/Mojang 在国内可能间歇 reset/timeout；脚本已带重试。
- 不要关闭 SSL 校验；不要无限放大 retry。
- Mojang 下载失败会尝试 BMCLAPI 镜像；EngineHub 数据 404 是版本未发布，不是网络问题。

## 命令路径

- CLI 工作目录必须是项目根目录，才能找到 `worldedit/` 下的缓存/配置。
- `worldedit/` 是运行时目录，删除后重新生成；不要把手写投影放进去。
- `schematics/` 是用户文件；`examples/` 是示例，不自动出现在页面列表。
- 文件名不能含路径分隔符；上传同名自动编号。

## 验收命令

```bat
python tools\fetch_assets.py
python tools\ensure_data.py examples\demo.schem
python tools\inspect_schem.py examples\demo.schem
we.cmd schematics\demo.schem examples\demo.txt
```

```text
//pos1 0,0,0
//pos2 15,15,15
//gen minecraft:stone x^2+y^2+z^2<=1
```
