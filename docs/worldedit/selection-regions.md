# 选区与区域操作

## 选区模型

WorldEdit 的区域由“选择模式 + 点”组成。最常见的是 **cuboid**：两个对角点确定一个与世界轴对齐的
长方体。

```text
//pos1 0,0,0
//pos2 15,15,15
```

CLI 没有玩家，所以：

- `//pos1`/`//pos2` 必须带 `x,y,z`；不带参数的形式依赖玩家位置，不可用。
- `//hpos1`、`//hpos2`、`//wand`、`//chunk` 不可用。
- 每次批处理都要重新设置选区，因为 CLI 每次进程是独立会话。

## 选择模式

| 模式 | 说明 |
|---|---|
| `cuboid` | 两角长方体，默认 |
| `extend` | 第一个点后，每次右击扩展包围盒 |
| `poly` | 2D 多边形，上下取最高/最低点 |
| `ellipsoid` | 中心 + 三个半径 |
| `sphere` | 中心 + 半径 |
| `cyl` | 中心 + XZ 半径，高度为最高/最低点 |
| `convex` | 多个点的凸包 |

CLI 中只有 cuboid 的 `//pos1/2 x,y,z` 最直接；其他模式依赖玩家点击，基本不可用。需要复杂形状
时用 `//gen` 的表达式。

## 调整选区

```text
//expand 10 up
//expand 5 me
//expand 10 n,w
//contract 5 down
//outset -h 3
//inset -v 2
//shift 2 north
//expand vert
```

- 方向：`n,s,e,w,u,d`、`north,south,east,west,up,down`、`me`（朝向）、`vert`（天空/基岩）。
- `//expand <a> <b> [dir]`：向相反两个方向各扩 a/b。
- `//outset -h/-v`：水平/垂直六向；不写 `-h/-v` 为全部。
- `//contract` 的 `down` 表示从上方收缩。

## 选区信息

```text
//size
//size -c
//count stone
//count #existing
//distr
//distr -d
//distr -c -d
//trim
//trim stone
```

`//trim` 将选区缩到刚好包住非空气（或给定 mask）方块的最小范围。

## 基本区域操作

```text
//set minecraft:stone
//set 70%stone,30%cobblestone
//replace minecraft:stone minecraft:glass
//replace #existing minecraft:grass_block
//replace "sand <air" minecraft:diamond_block
//walls minecraft:oak_planks
//faces minecraft:stone_bricks
//hollow 1 minecraft:air
//hollow 2 minecraft:stone
```

- `//replace` 省略 mask 等价于 `#existing`（非空气）。
- `//walls` 只建四壁，不含顶/底；`//faces`（别名 `//outline`）建六面。
- `//hollow [厚度] [内壁pattern]`：默认内部空气；可把内壁填成另一种方块。

## 表面与重复

```text
//overlay minecraft:snow_block
//stack 4
//stack 4 north
//stack 2 up -m minecraft:stone
//move 5 north
//move 3 down minecraft:dirt
```

`//stack` 沿方向复制选区；`//move` 移动内容，留下的空洞默认空气。CLI 没有实体/生物群系，
`-e/-b` 基本无效果。

## 地形与植被

```text
//smooth 3
//naturalize
//flora
//forest oak 5
/forestgen 20 oak 5
```

`//smooth` 是高度图平滑，适合地表，不适合洞穴/墙面。`//forest` 在选区内种树；
`/forestgen` 以放置点为中心。树生成可能无法撤销（取决于平台）。

## 线、曲线、中心、变形

```text
//line minecraft:stone 2
//line -h minecraft:glass 3
//curve minecraft:stone 1
//center minecraft:gold_block
//deform y-=1
//deform y+=0.2*sin(x*10)
//deform swap(x,y)
```

- `//line` 用 cuboid 两角；`//curve` 用 convex 多点的顺序。
- `//deform` 的表达式返回每个方块的新坐标；默认 -1..1 归一化，`-r` 原始坐标，`-o` 相对放置点。
- 变形可能产生空洞/重叠，先在小范围试。

## 生物群系

```text
//setbiome minecraft:plains
//expand vert
//setbiome minecraft:ocean
```

1.15+ 生物群系是 3D 的 4×4×4 粒度，无法精确到单个方块；设置后可能需要重新进入世界/重新加载
页面才能看到颜色变化。本项目渲染器使用固定的 1.21.1 温带 tint，不读取投影 biomes。

## 选区操作实战：生成一个房间

```text
//pos1 0,0,0
//pos2 15,7,15
//walls minecraft:stone_bricks
//faces minecraft:stone_bricks
//hollow 1 minecraft:air
//pos1 3,1,0
//pos2 5,3,0
//set minecraft:air
```

最后一步在墙上开一个 3×3 的门洞；注意坐标要落在墙面上。

## CLI 注意事项

- 每个脚本先 `//pos1`/`//pos2`。
- 选区默认是闭区间：`0..15` 是 16 格。
- 没有玩家朝向，`//expand 5`/`//stack 4` 的方向参数建议显式写。
- `//regen`、`/snow`、`/thaw`、`/ex` 依赖世界/玩家，投影里不可用。
- 大选区命令会消耗内存；先用 `//size` 确认体积。

## 官方参考

- <https://worldedit.enginehub.org/en/latest/usage/regions/selections/>
- <https://worldedit.enginehub.org/en/latest/usage/regions/regionops/>
- <https://worldedit.enginehub.org/en/latest/commands/>



