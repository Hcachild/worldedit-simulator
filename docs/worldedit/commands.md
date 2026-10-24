# WorldEdit 常用命令

以下命令基于 WorldEdit 7.4.x。方块使用 1.13+ 命名空间 ID；省略 `minecraft:` 时默认原版命名空间。
`//` 开头的命令属于 WorldEdit，`/` 开头的通常是工具/服务端命令。

## 通用 / 会话

| 命令 | 说明 |
|---|---|
| `//help [命令]` | 命令帮助 |
| `//version` | 版本 |
| `//undo [次数] [玩家]` | 撤销 |
| `//redo [次数] [玩家]` | 重做 |
| `//clearhistory` | 清空历史 |
| `//gmask [mask]` | 设置/清除全局 mask；无参数清除 |
| `//toggleplace` | 在自身位置和 pos1 之间切换放置点 |
| `//placement` | 选择放置方式（`here`、`min`、`max`、`world`） |
| `//world [world]` | 覆盖世界（CLI 必需时用） |
| `//drawsel` | 显示选区（仅创造模式，48³ 限制；CLI 无意义） |
| `//searchitem <关键词>` | 搜索方块/物品 |
| `//registry <registry> [query]` | 搜索注册表 |
| `//report` | 生成报告 |
| `//reload` | 重载配置 |

## 选区

| 命令 | 说明 |
|---|---|
| `//wand [-n]` | 获取选择/导航木斧（无玩家不可用） |
| `//pos1 x,y,z` | 第一个角 |
| `//pos2 x,y,z` | 第二个角 |
| `//pos1` / `//pos2` | 站在方块上方设置（CLI 无玩家不可用） |
| `//hpos1` / `//hpos2` | 看向的方块（无玩家不可用） |
| `//chunk [-cs] [x,z]` | 选中区块（无玩家不可用） |
| `//sel <cuboid\|extend\|poly\|ellipsoid\|sphere\|cyl\|convex>` | 选择模式 |
| `//expand <数量> [方向]` | 扩展 |
| `//expand <数量> <反向数量> [方向]` | 双向扩展 |
| `//expand vert` | 扩展到天空和基岩 |
| `//contract <数量> [方向]` | 收缩 |
| `//outset [-hv] <数量>` | 向外扩（`-h` 水平，`-v` 垂直） |
| `//inset [-hv] <数量>` | 向内缩 |
| `//shift <数量> [方向]` | 移动选区 |
| `//size [-c]` | 选区/剪贴板尺寸 |
| `//count <mask>` | 统计匹配方块数 |
| `//distr [-cd]` | 方块分布；`-c` 剪贴板，`-d` 按状态 |
| `//trim [mask]` | 收缩到最小包围范围 |

方向：`n`/`s`/`e`/`w`/`u`/`d` 或 `north`/`south`/`east`/`west`/`up`/`down`；`me` 表示面向，
`vert` 表示垂直方向；可组合 `n,w`。`//expand 5` 默认沿视线。

## 区域操作

| 命令 | 说明 |
|---|---|
| `//set <pattern>` | 填充选区 |
| `//replace [mask] <pattern>` | 替换；省略 mask 表示非空气 |
| `//walls <pattern>` | 建四壁（无顶/底） |
| `//faces <pattern>` | 建六面（别名 `//outline`） |
| `//hollow [厚度] [pattern]` | 挖空成壳；可指定内壁填充 |
| `//overlay <pattern>` | 在表面铺一层 |
| `//stack <次数> [方向]` | 重复选区 |
| `//move <距离> [方向] [填充pattern]` | 移动选区内容 |
| `//smooth [迭代次数]` | 平滑地形 |
| `//naturalize` | 草/土/石自然分层 |
| `//flora` | 随机花草/仙人掌 |
| `//forest <树种> [密度]` | 种树，密度 0–100 |
| `//line <pattern> [厚度] [-h]` | 在长方体两角之间画线 |
| `//curve <pattern> [厚度] [-h]` | 在 convex 选区点之间画曲线 |
| `//center <pattern>` | 设置选区中心方块 |
| `//deform <expression> [-r\|-o]` | 按表达式变形 |
| `//setbiome <biome>` | 设置生物群系（1.15+ 为 3D，4×4×4 粒度） |
| `//regen [-c]` | 重新生成（依赖世界生成器；投影里不可用） |

`//stack` 常用 flags：`-s` 同时移动选区、`-m <mask>` 只复制匹配方块、`-e` 复制实体、`-b`
复制生物群系。`//move` 支持 `-s`、`-e`、`-b`、`-m`。CLI 没有实体/生物群系时这些 flag 意义有限。

`//deform` 的表达式返回新坐标：`//deform y-=1` 会把每个方块从下方复制；默认坐标归一化 -1..1，
`-r` 用原始坐标，`-o` 相对放置点。

## 剪贴板

| 命令 | 说明 |
|---|---|
| `//copy [-e] [-b] [-m <mask>]` | 复制选区到剪贴板 |
| `//cut [-e] [-b] [-m <mask>]` | 剪切 |
| `//paste [-aoeb] [-m <mask>] [-s] [-n] [-o]` | 粘贴 |
| `//rotate <y> [x] [z]` | 绕 Y/X/Z 旋转（90° 倍数） |
| `//flip [direction]` | 按方向翻转 |
| `//clearclipboard` | 清空剪贴板 |
| `//schem save <name>` | 保存剪贴板 |
| `//schem load <name>` | 载入投影到剪贴板 |
| `//schem list [-dn] [-p <page>]` | 列出投影 |
| `//schem delete <name>` | 删除投影 |
| `//schem listformats` | 可用格式 |
| `//schem share [name]` | 上传分享（需要外部服务） |

`//paste` 的 `-o` 回原坐标；`-a` 不粘贴空气；`-s` 选中粘贴区域；`-n` 只选不粘；`-e` 实体；
`-b` 生物群系；`-m` 只粘贴匹配方块。复制时记录的“相对位置”很重要：相对粘贴是相对**复制时**
你站的位置，不是相对选区中心。

## 生成

| 命令 | 说明 |
|---|---|
| `//sphere [-r] <pattern> <r>` | 实心球；`-r` 抬高使底部在脚下 |
| `//hsphere [-r] <pattern> <r>` | 空心球 |
| `//sphere <pattern> <rNS>,<rUD>,<rEW>` | 椭球（半径顺序：南北、上下、东西） |
| `//cyl <pattern> <r> [高]` | 实心圆柱 |
| `//hcyl <pattern> <r> [高]` | 空心圆柱 |
| `//cyl <pattern> <rEW>,<rNS> [高]` | 椭圆柱 |
| `//pyramid <pattern> <size>` / `//hpyramid` | 金字塔 |
| `//gen <pattern> <expression>` | 表达式形状（`//g`、`//gen`） |
| `/forestgen [size] [type] [density]` | 以放置点为中心生成森林 |
| `/pumpkins [size]` | 南瓜地 |

`//sphere`/`//cyl` 使用放置点（默认玩家位置，CLI 无玩家时需注意）；本项目里通常直接用 `//gen`
在选区内生成。

## 工具 / 笔刷（CLI 不可用）

| 命令 | 说明 |
|---|---|
| `/tool tree [type]` | 点地种树 |
| `/tool repl <pattern>` | 替换点击方块 |
| `/tool lrbuild <左键> <右键>` | 远程放置/破坏 |
| `/tool farwand` | 远程选区 |
| `/tool cycler` | 循环方块状态 |
| `/tool info` | 方块信息 |
| `/tool floodfill <pattern> <range>` | 洪泛填充 |
| `//sp single\|area\|recur` | 超级镐 |
| `/brush sphere\|cyl\|set\|clipboard\|smooth\|gravity\|forest\|extinguish\|butcher\|deform\|raise\|lower\|biome` | 笔刷 |
| `/mask <mask>` / `/material <pattern>` / `/size <n>` / `/range <n>` | 笔刷设置 |
| `/brush none` | 解绑 |

这些需要玩家、手持物品和点击目标，**无头 CLI 无法使用**。需要类似效果时用区域命令或
`//gen` 代替；详见 [tools-brushes.md](tools-brushes.md)。

## 导航（CLI 不可用）

`/jumpto`、`/thru`、`/ascend`、`/descend`、`/ceil`、`/up`、`/unstuck` 都需要玩家实体/位置；
CLI 没有玩家，不能使用。

## 其他

| 命令 | 说明 |
|---|---|
| `/butcher [半径] [flags]` | 清除实体（CLI 无实体） |
| `/remove <mask>` | 移除匹配方块（可用 `//replace mask air` 替代） |
| `/snow` / `/thaw` | 下雪/融雪（世界相关） |
| `/ex` | 熄灭火焰（世界相关） |
| `/cs <script>` / `/.s` | CraftScript |

## 命令组合示例

```text
//pos1 0,0,0
//pos2 15,15,15
//set minecraft:stone
//replace minecraft:stone minecraft:glass
//walls minecraft:oak_planks
//hollow 1 minecraft:air
```

```text
//pos1 0,0,0
//pos2 15,15,15
//gen minecraft:stone x^2+y^2+z^2<=1
```



