# WorldEdit-CLI 细节

本项目使用 EngineHub 的 `worldedit-cli` 7.4.7-SNAPSHOT（构建 30360）。它把 `.schem` 当作一个
“世界”来执行 WorldEdit 命令，不需要 Minecraft 服务端。

## 运行

```bat
java -jar bin\worldedit-cli-7.4.7-SNAPSHOT-dist.jar -f file.schem -s commands.txt
```

| 参数 | 说明 |
|---|---|
| `-f/--file` | 载入的 `.schem`（或 level.dat，但 level.dat 未完成） |
| `-s/--script` | 命令脚本，一行一条；没有时从 stdin 读取 |
| 脚本末尾 | 建议写 `stop`；CLI 收到后保存并退出 |
| 工作目录 | 进程 cwd；必须是项目根目录，才能找到 `worldedit/` 缓存 |

交互模式：

```text
//pos1 0,0,0
//pos2 15,15,15
//set minecraft:stone
stop
```

CLI 在每条命令成功后自动把结果写回 `-f` 指定的文件；不需要 `//schem save`。如果命令失败，
文件可能不变。

## Java 版本

7.4.7 的 class file 版本是 69，**必须 Java 25**。系统 Java 17 会报：

```text
UnsupportedClassVersionError: com/sk89q/worldedit/cli/CLIWorldEdit
class file version 69.0, this version only recognizes up to 61.0
```

项目已带 `jdk-25.0.4.1+1-jre`；`we.cmd`/`web/server.py` 使用它。不要改成系统 Java 17。

## 工作目录

```
worldedit/
  worldedit.properties   配置
  cli-data/<dv>_1.json   按 DataVersion 缓存的方块表
  schematics/            //schem 保存/载入的位置
  assets/ sessions/      运行时目录
  .archive-unpack/       翻译缓存
```

方块表 URL：

```text
https://services.enginehub.org/cassette-deck/we-cli-data/<DataVersion>/1
```

CLI 读取时**没有网络超时**，网络不通会一直卡住。本项目用 `tools/ensure_data.py` 预下载并缓存，
`core/workspace.py` 在运行前也检查缓存。缓存文件名是 `<DataVersion>_1.json`。

## 支持的 DataVersion

实测可用（EngineHub 已发布对应数据）：

```
3698 1.20.3
3700 1.20.4
3837 1.20.5
3953 1.21
3955 1.21.1
4080 1.21.2
4189 1.21.4
4325 1.21.5
4435 1.21.6
4438 1.21.7
4440 1.21.8
```

没有数据：1.20.1（3465）、1.21.9+（4556/4558）等。遇到 `No CLI data published`：

```bat
python tools\retarget_schem.py schematics\old.schem
```

`retarget` 只改 `DataVersion`，不改方块。旧 → 新通常安全；新 → 旧可能丢失新方块。

## 格式要求

- 1.13+ Sponge `.schem`（v1/v2/v3）。
- gzip NBT，根 compound 名必须是 `Schematic`。
- 必须含 `DataVersion`；CLI 用它选方块表。
- 旧 MCEdit `.schematic` 本项目 Web 不接受；CLI 虽能读，但通常没有对应数据。
- 方块索引用 varint，顺序 `(y*Length+z)*Width+x`。

## 无玩家限制

CLI 的 Actor 是控制台，没有玩家位置/朝向/手持物/点击：

不可用：`//wand`、`//hpos1/2`、`//chunk`、`//up`、`//thru`、`//jumpto`、`//ascend`、
`//descend`、`//ceil`、`/tool`、`/brush`、`/mask`（笔刷）、`/material`、超级镐、`//regen`、
`/snow`、`/thaw`、`/ex`、`/butcher`。

可用：`//pos1/2`、`//set`、`//replace`、`//walls`、`//faces`、`//hollow`、`//overlay`、
`//stack`、`//move`、`//smooth`、`//naturalize`、`//flora`、`//forest`、`//line`、`//curve`、
`//center`、`//deform`、`//setbiome`、`//gen`、`//copy`、`//paste`、`//rotate`、`//flip`、
`//schem`。

## 保存/输出

- 自动保存到 `-f` 文件；页面模式下是 `work/current.schem`，点“保存”才覆盖源文件。
- `//schem save <name>` 保存**剪贴板**到 `worldedit/schematics/<name>.schem`。
- 想另存结果：先 `//copy`，再 `//schem save`；或使用页面的“另存为”。
- 命令失败/文件损坏时先备份再重试。

## 进程与日志

- 每次运行一个 JVM，约 1–2 秒。
- 本项目在 Windows 下用 `CREATE_NO_WINDOW` + `SW_HIDE`，不弹 CMD。
- 超时 180s，超时会终止子进程；临时脚本在 `%TEMP%` 并在 finally 删除。
- `bin/log4j2.xml` 只输出控制台，不生成 `logs/`；Web 后台日志在
  `%TEMP%/worldedit-simulator-web.log`。
- 命令串行执行（Workspace 锁），不要并发跑多个 CLI 改同一文件。

## 脚本示例

```text
//pos1 0,0,0
//pos2 15,15,15
//gen minecraft:stone x^2+y^2+z^2<=1
//replace minecraft:stone minecraft:glass
stop
```

```bat
we.cmd schematics\demo.schem examples\demo.txt
```

## 工具

| 工具 | 用途 |
|---|---|
| `tools/ensure_data.py` | 预下载/检查 DataVersion 方块表 |
| `tools/retarget_schem.py` | 改 DataVersion（自动 `.bak`） |
| `tools/inspect_schem.py` | 查看尺寸/方块统计 |
| `tools/make_schem.py` | 生成实心测试投影 |
| `tools/make_demo.py` | 生成 demo 小屋 |
| `tools/agent_run.py` | 通过 HTTP 从外部 Agent 执行命令 |

## 官方参考

- <https://worldedit.enginehub.org/en/latest/commands/>
- <https://github.com/EngineHub/WorldEdit>
- <https://builds.enginehub.org/job/worldedit>


