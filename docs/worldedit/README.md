# WorldEdit 用法总览

本目录是 WorldEdit 7.4.x 的本地速查文档，偏重无头 CLI 和本项目实际用到的命令。官方完整命令表见
<https://worldedit.enginehub.org/en/latest/commands/>。

## 先理解三件事

1. **选区**：大多数区域命令只对当前选区生效。CLI 没有玩家，必须显式给坐标，例如
   `//pos1 0,0,0`、`//pos2 15,15,15`。
2. **pattern 与 mask**：`//set`、`//replace` 等接收 pattern；`//replace` 的 from 参数、`//gmask`
   等接收 mask。pattern 决定放什么，mask 决定改哪些。
3. **CLI 的“世界”是投影文件**：`work/current.schem`。命令成功后自动写回这个文件；不是服务器世界。

## 选区速查

| 命令 | 作用 |
|---|---|
| `//pos1 x,y,z` / `//pos2 x,y,z` | 设置长方体两个角（CLI 必用带坐标形式） |
| `//hpos1` / `//hpos2` | 看向的方块（CLI 无玩家，不可用） |
| `//chunk` | 当前区块（CLI 无玩家，不可用） |
| `//wand` | 获取木斧（CLI 无玩家，不可用） |
| `//sel cuboid\|extend\|poly\|ellipsoid\|sphere\|cyl\|convex` | 切换选择模式 |
| `//expand <n> [方向]` / `//contract <n> [方向]` | 扩展/收缩 |
| `//outset <n>` / `//inset <n>` | 六个方向同时外扩/内缩 |
| `//shift <n> [方向]` | 平移选区 |
| `//size` / `//count <mask>` / `//distr` | 查看尺寸/计数/分布 |

方向：`n/s/e/w/u/d`、`up/down/north/south/east/west`，以及 `me`（面向）、`vert`（到天空/基岩）。

## 区域操作速查

| 命令 | 作用 |
|---|---|
| `//set <pattern>` | 填充选区 |
| `//replace [mask] <pattern>` | 替换（省略 mask = 非空气） |
| `//walls <pattern>` / `//faces <pattern>` | 四壁 / 六面（`//outline` 别名） |
| `//hollow [thickness] [pattern]` | 挖空成壳 |
| `//overlay <pattern>` | 在表面铺一层 |
| `//stack <count> [direction]` | 沿方向重复 |
| `//move <distance> [direction] [pattern]` | 移动选区内容 |
| `//smooth [iterations]` | 平滑地形 |
| `//naturalize` | 草/土/石自然分层 |
| `//flora` / `//forest <type> [density]` | 植被/森林 |
| `//line <pattern> [thickness]` / `//curve ...` | 线/曲线 |
| `//center <pattern>` | 设置中心方块 |
| `//deform <expression>` | 按表达式变形 |
| `//setbiome <biome>` | 设置生物群系 |

## 剪贴板与投影

| 命令 | 作用 |
|---|---|
| `//copy` / `//cut` | 复制/剪切选区到剪贴板 |
| `//paste [-o]` | 粘贴；`-o` 回原坐标 |
| `//rotate <y> [x] [z]` | 旋转剪贴板 |
| `//flip [direction]` | 翻转剪贴板 |
| `//schem save <name>` | 保存剪贴板为 `.schem` |
| `//schem load <name>` | 载入投影为剪贴板 |
| `//schem list` / `//schem delete <name>` | 管理投影 |

## 生成速查

| 命令 | 作用 |
|---|---|
| `//sphere <pattern> <r>` / `//hsphere` | 球/空心球 |
| `//cyl <pattern> <r> [h]` / `//hcyl` | 圆柱/空心圆柱 |
| `//pyramid <pattern> <size>` / `//hpyramid` | 金字塔 |
| `//gen <pattern> <expression>` | 任意表达式形状（别名 `//g`） |
| `//forest <type> [density]` | 森林 |
| `/pumpkins [size]` | 南瓜地 |

## CLI 限制（很重要）

无头 CLI 没有玩家实体，所以以下命令**不可用**：

- 依赖玩家位置/朝向：`//wand`、`//hpos1/2`、`//chunk`、`//up`、`//thru`、`//jumpto`、`//ascend`、
  `//descend`、`//ceil` 等导航命令。
- 依赖手持物品/点击：`/tool`、`/brush`、`/mask`（笔刷用）、`/material`、超级镐等。
- 需要实体/生物的命令：`/butcher` 等。
- `//regen` 依赖世界生成器，投影世界里不可用。
- `//schem share` 需要联网服务，当前 CLI 不保证可用。

可以用的命令通常只依赖选区/坐标/pattern/mask，例如 `//set`、`//replace`、`//walls`、`//gen`、
`//copy`、`//paste`、`//stack`、`//deform`。

## 本项目里的执行方式

```bat
:: 命令行
we.cmd schematics\demo.schem scripts\demo.txt

:: 页面/Agent
POST /api/run {"commands":"//pos1 ...\n//pos2 ...\n//set ...","actor":"agent"}
```

一次脚本建议先设置 `//pos1`/`//pos2`，再执行操作，最后 `stop`。CLI 会在命令成功后自动保存到
载入的文件。

## 详细页面

- [commands.md](commands.md)：完整常用命令表
- [selection-regions.md](selection-regions.md)：选区与区域操作
- [patterns-masks.md](patterns-masks.md)：pattern 与 mask
- [clipboard-schematics.md](clipboard-schematics.md)：剪贴板与 `.schem`
- [generation-expressions.md](generation-expressions.md)：`//gen` 与表达式
- [tools-brushes.md](tools-brushes.md)：工具/笔刷及 CLI 限制
- [cli.md](cli.md)：CLI 细节、DataVersion、保存
- [gotchas.md](gotchas.md)：踩坑清单

