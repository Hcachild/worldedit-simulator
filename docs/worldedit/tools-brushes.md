# 工具与笔刷

这些功能需要玩家、手持物品和点击目标。**本项目的无头 CLI 不能使用**，但了解它们有助于在游戏内
配套使用，或用区域命令/`//gen` 找到等价做法。

## 工具（/tool）

先手持一个物品，再执行命令绑定；`/tool none` 解绑。

| 命令 | 作用 |
|---|---|
| `/tool tree [type]` | 右击种树 |
| `/tool deltree` | 删除悬空树 |
| `/tool repl <pattern>` | 右击替换方块；左击取样 |
| `/tool lrbuild <左击pattern> <右击pattern>` | 远程放置/破坏 |
| `/tool farwand` | 远程选区（等价 `//hpos1/2`） |
| `/tool cycler` | 左击选属性，右击循环值 |
| `/tool info` | 方块信息 |
| `/tool floodfill <pattern> <range>` | 从点击点洪泛替换同类方块 |
| `/tool selwand` | 绑定选择木斧 |
| `/tool navwand` | 绑定导航指南针 |

### 超级镐

```text
//            // 切换单方块超级镐
/sp single
/sp area <radius>
/sp recur <radius>
```

左击任意镐触发；`/sp` 关闭。`area` 同类型范围破坏，`recur` 只破坏连通的同类型（矿脉）。

## 笔刷（/brush）

手持物品绑定，右击使用；`/brush none` 解绑。

| 命令 | 作用 |
|---|---|
| `/brush sphere [-h] <pattern> [r]` | 球形笔刷 |
| `/brush cylinder [-h] <pattern> [r] [h]` | 圆柱笔刷 |
| `/brush set <shape> [size] <pattern>` | 球/柱/立方设置 |
| `/brush clipboard [-aoeb] [-m <mask>]` | 粘贴剪贴板 |
| `/brush smooth [r] [iterations] [mask]` | 平滑 |
| `/brush gravity [r] [-h]` | 重力 |
| `/brush forest <shape> [r] [density] <tree>` | 森林 |
| `/brush extinguish [r]` | 灭火 |
| `/brush butcher [r] [-pngabtfr]` | 清除实体 |
| `/brush deform <shape> [size] [expr] [-ro]` | 表达式变形 |
| `/brush raise <shape> [size]` | 抬高（`y-=1`） |
| `/brush lower <shape> [size]` | 降低（`y+=1`） |
| `/brush biome <shape> [r] <biome>` | 设置生物群系 |

常用别名：`/br s`、`/br cyl`、`/br ex`、`/br kill`。

### 笔刷设置

| 命令 | 作用 |
|---|---|
| `/mask <mask>` | 笔刷只影响匹配方块 |
| `/material <pattern>` | 替换笔刷材质 |
| `/size <n>` | 笔刷半径/尺寸 |
| `/range <n>` | 最大作用距离 |
| `/brush none` | 解绑 |

`//gmask` 与笔刷 mask 会叠加（交集）。例如全局 mask 是 dirt、笔刷 mask 是 stone，则没有方块
能同时满足，笔刷不会生效。

## CLI 等价做法

| 游戏内操作 | CLI/页面替代 |
|---|---|
| `//wand` + 点击选区 | `//pos1 x,y,z` / `//pos2 x,y,z` |
| `//hpos1/2` | 用已知坐标 |
| `/brush sphere stone 5` | `//sphere` 或 `//gen -c` |
| `/brush cylinder` | `//cyl` / `//gen` |
| `/brush smooth` | `//smooth` |
| `/brush gravity` | 用 `//deform y-=1` 或手动 |
| `/tool floodfill` | `//replace`/`//gen`，或按区域分块 |
| `/tool repl` | `//replace` |
| `/tool info` | 页面点击方块查看 HUD |
| `/brush clipboard` | `//paste`/`//paste -o` |

## 为什么 CLI 不可用

WorldEdit 工具/笔刷依赖：

- 玩家实体（位置、朝向、视线目标）
- 手持物品槽位
- 左/右键事件
- 服务端权限/世界上下文

WorldEdit-CLI 的 Actor 是控制台，没有这些信息；命令解析器会拒绝依赖玩家的操作。强行执行通常
报错或没有目标。

## 官方参考

- <https://worldedit.enginehub.org/en/latest/usage/tools/tools/>
- <https://worldedit.enginehub.org/en/latest/usage/tools/brushes/>
