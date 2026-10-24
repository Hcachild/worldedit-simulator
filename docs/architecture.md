# 项目架构

## 分层

```
core/                 共享 Python 核心，不依赖 HTTP/前端
  nbt.py              NBT 基本类型读写
  schematic.py        Sponge .schem 读取、写入、空白生成、DataVersion 重定向
  worldedit.py        CLI 路径、DataVersion 方块表缓存、无窗口子进程执行
  workspace.py        当前文件/工作副本/文件操作/revision/actor/锁
web/
  server.py           HTTP 路由、SSE、静态文件、/assets 路由
  static/
    index.html
    style.css
    js/
      main.js         页面状态机与事件编排
      api.js          后端 API 封装
      live.js         EventSource 实时同步
      viewer.js       Three.js 场景、相机、拾取、模型生命周期
      mc-renderer.js  block-model-renderer 适配层
      colors.js       回退颜色/透明规则
      files.js        文件列表、搜索/排序、行菜单
      ui.js           DOM、状态、日志、toast、busy
      dialogs.js      表单/确认对话框
    vendor/           Three.js、block-model-renderer、WASM
    assets.zip        block-model-renderer 的方块实体覆盖包
tools/                无头 CLI 小工具（不是 Web 依赖）
  inspect_schem.py    查看 .schem 方块统计
  make_schem.py       生成实心测试投影
  make_demo.py        生成 examples/demo.schem
  ensure_data.py      预下载 DataVersion 方块表
  retarget_schem.py   修改投影 DataVersion（只改元数据）
  fetch_assets.py     下载 Minecraft 1.21.1 客户端 jar
  agent_run.py        外部 Agent 调用 /api/run 的客户端
examples/             示例投影和命令脚本（入库）
schematics/           用户投影（.gitignore）
assets/               本地客户端资源（.gitignore）
work/                 当前编辑副本（.gitignore）
worldedit/            CLI 运行时目录（.gitignore）
```

`core` 不感知 HTTP，也不依赖前端；`web` 只做传输和展示；`tools` 是独立入口。这样命令执行、
Schm 文件格式、HTTP API 和浏览器渲染可以分别测试和替换。

## 一次命令的数据流

```
浏览器命令框
  -> POST /api/run {commands, actor}
  -> web/server.py
  -> core.workspace.Workspace.run()
       -> 获取 RLock（命令串行）
       -> 写临时命令脚本
       -> core.worldedit.run_cli()
            -> java.exe -jar worldedit-cli ... -f work/current.schem -s script
            -> 隐藏窗口（CREATE_NO_WINDOW + SW_HIDE）
            -> 超时 180s；结束后删除临时脚本
       -> 重新读取 work/current.schem
       -> 更新 dirty/revision/actor
  -> 返回 {ok, actor, log, state}
  -> 浏览器 applyState()/viewer.setModel()
  -> /api/events SSE 同时广播快照给其他标签页/Agent 页面
```

外部 Agent 走同一路径，没有单独的编辑引擎：

```http
POST /api/run
{"commands":"//pos1 0,0,0\n//pos2 7,7,7\n//set minecraft:stone","actor":"agent"}
```

## 工作区状态

`core.workspace.Workspace` 维护：

| 字段 | 含义 |
|---|---|
| `source` | `schematics/` 中的源文件 |
| `current` | `work/current.schem`，CLI 实际编辑的副本 |
| `data` | 解析后的尺寸、palette、方块数据 |
| `dirty` | 自上次 `save` 后是否被命令改过 |
| `revision` | 每次写入自增，用于 SSE 去重和前端版本比较 |
| `actor` | 最近一次变更来源（`user` / `agent`） |

所有公开方法都持有 `RLock`。命令、上传、重命名、删除不会并发修改文件。

文件操作语义：

| 操作 | 行为 |
|---|---|
| `load` | 读源文件、确保方块表、复制到 `work/current.schem` |
| `new` | 生成全空气 `.schem` 并载入 |
| `upload` | 先写临时文件并校验，再移到 `schematics/`，同名自动编号 |
| `rename` | 改源文件名；若为当前文件，同步更新会话名 |
| `duplicate` | 复制源文件；不切换当前文件 |
| `delete` | 删除源文件；若为当前文件则清空工作区 |
| `save` | 把 `work/current.schem` 覆盖回源文件，清除 dirty |
| `save_as` | 保存到新文件并切换当前源；支持覆盖 |
| `reset` | 源文件覆盖回工作副本，清除 dirty |
| `close` | 丢弃工作副本，清空当前状态 |
| `run` | 执行 WorldEdit 命令，更新 dirty/state |

## HTTP API

| 方法/路径 | 说明 |
|---|---|
| `GET /api/state` | `{ok, revision, state}`；空工作区时 `state: null` |
| `GET /api/files` | 文件列表（name/size/mtime/active/dirty） |
| `GET /api/events` | SSE 快照流，事件为 `{revision, actor, state, files}` |
| `GET /api/download[?name=]` | 下载当前结果或指定源文件 |
| `GET /assets/client.jar` | 本地 Minecraft 客户端资源 |
| `POST /api/load` | `{name}` 载入投影 |
| `POST /api/new` | `{name,width,height,length}` 新建空白投影 |
| `POST /api/upload?name=` | 原始 `.schem` 字节上传 |
| `POST /api/rename` | `{name,newName}` |
| `POST /api/duplicate` | `{name,newName?}` |
| `POST /api/delete` | `{name}` |
| `POST /api/close` | 关闭当前投影 |
| `POST /api/save` | 覆盖源文件 |
| `POST /api/save-as` | `{name,overwrite}` |
| `POST /api/reset` | 恢复源文件 |
| `POST /api/run` | `{commands,actor?}` |
| `POST /api/reveal` | 打开 `schematics/` |

错误返回 `{ok:false,error}` 和 4xx/5xx；`/api/run` 即使命令失败通常也返回 200，用 `ok` 和
`log` 表达结果。详见 [api.md](api.md)。

## SSE 实时同步

- `Workspace.revision` 只在状态/文件变更时自增；`snapshot()` 在同一把锁内返回
  `{revision, actor, state, files}`。
- `web/server.py` 的 `/api/events` 每 0.3s 检查一次 revision；变化时发送完整快照。
- 前端 `live.js` 用 `EventSource` 接收，按 revision 去重；重连时重置 lastRevision。
- `main.js` 在 `app.busy` 时把事件放入 `pendingLive`，操作结束后应用最新状态。
- 外部 `actor: agent` 的变更会显示「AI 已更新」toast；用户自己的操作不重复提示。
- 模型构建是异步的；`applyState` 用 `applyToken` 防止旧构建覆盖新状态，`viewer` 用
  `buildToken` 取消过期构建。

## 进程模型

- 服务器是单进程 `ThreadingHTTPServer`，只绑定 `127.0.0.1:8777`。
- WorldEdit 每次命令启动一个 JVM，`run_cli` 串行等待；超时会终止并回收。
- Windows 下 Java/curl 用 `CREATE_NO_WINDOW` + `STARTUPINFO(SW_HIDE)`，不弹 CMD。
- 临时命令脚本在 `%TEMP%`，`finally` 删除；curl 超时会清理半成品。
- 二次启动在绑定端口后才创建工作区，避免清掉正在运行实例的 `work/current.schem`。
- 日志：Web 后台写 `%TEMP%/worldedit-simulator-web.log`；CLI 日志由 `bin/log4j2.xml`
  改为只输出到控制台，项目内不生成 `logs/`。

## 渲染管线

```
state.data (base64 varint)
  -> mc-renderer.buildBlockData()
       -> palette/state 字符串拆分 id + properties
       -> 扁平 palette/raw Int32Array
  -> block-model-renderer.createScene()
       -> blockstates 变体/multipart
       -> models/parent/textures
       -> 隐藏面剔除、贪心面合并、纹理图集
       -> 半透明排序、动画、方块实体/流体
  -> handle.group
       -> scale 1/16，position 居中
       -> viewer.scene
  -> 不可见 InstancedMesh 拾取层（不参与绘制）
```

材质来自 `assets/client.jar`（Minecraft 1.21.1）；解析库的 `assets.zip` 和 WASM 在
`web/static/` 本地提供。细节见 [rendering.md](rendering.md)。

## 设计边界

- 不做 Minecraft 世界/存档编辑，只处理 `.schem` 投影。
- 不模拟玩家实体、掉落物、红石、实体 AI；WorldEdit 命令只改方块/方块状态。
- 不实现完整 Minecraft 版本模型：CLI 方块表支持一组 DataVersion，3D 材质固定 1.21.1。
- 不做远程多用户权限系统；默认只允许本机访问。
