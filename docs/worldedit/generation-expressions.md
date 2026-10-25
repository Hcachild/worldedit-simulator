# 生成与表达式

## 内置形状

### 球体

```text
//sphere <pattern> <radius>
//hsphere <pattern> <radius>
//sphere [-r] <pattern> <radius>
//sphere <pattern> <rNS>,<rUD>,<rEW>
```

- 默认中心是放置点上方一格；`-r` 抬高使球底在脚下。
- 椭球半径顺序：南北、上下、东西。
- CLI 没有玩家，`//sphere` 的放置点行为不适合精确定位；需要控制中心时用 `//gen -c` 或先选好
  坐标。
- 半径可以是小数，边缘更自然。

### 圆柱 / 圆

```text
//cyl <pattern> <radius> [height]
//hcyl <pattern> <radius> [height]
//cyl <pattern> <rEW>,<rNS> [height]
```

高度 1 就是圆。圆柱从放置点脚部向上；CLI 中同样建议用 `//gen` 控制位置。

### 金字塔

```text
//pyramid <pattern> <size>
//hpyramid <pattern> <size>
```

`size` 是高度/层数，底层边长是 `2*size`，每层向内收一格。

### 森林 / 南瓜

```text
//forest <tree_type> [density]
/forestgen [size] [type] [density]
/pumpkins [size]
```

`//forest` 在选区内；`/forestgen` 以放置点为中心。密度 0–100，默认 5。树生成可能无法撤销。

## `//generate`（别名 `//gen`、`//g`）

```text
//gen <pattern> <expression>
//gen -h <pattern> <expression>
//gen -c <pattern> <expression>
//gen -r <pattern> <expression>
//gen -o <pattern> <expression>
```

表达式对选区中的**每个方块**求值；结果 >0 放置方块，<=0 不放置。表达式可用 `x,y,z`。

### 坐标系统（最容易踩坑）

| Flags | 坐标 | 说明 |
|---|---|---|
| 无 | `-1..1` 归一化 | 整个选区是 2×2×2 单位；非立方选区会被拉伸 |
| `-c` | 原点在选区中心，1 方块=1 单位 | 需要真实比例时用 |
| `-r` | 原始世界坐标，1 方块=1 单位 | 公式直接写世界坐标 |
| `-o` | 以放置点为原点，1 方块=1 单位 | 以玩家/pos1 为中心 |

**重要**：默认不是方块坐标。`(x-7.5)^2+(y-7.5)^2+(z-7.5)^2<=49` 在 16³ 选区默认模式下
通常匹配 0 个方块，因为 x/y/z 实际是 -1..1。正确写法：

```text
//pos1 0,0,0
//pos2 15,15,15
//gen minecraft:stone x^2+y^2+z^2<=1
```

如果要用“半径 7 方块”：

```text
//gen -c minecraft:stone x^2+y^2+z^2<=7^2
```

### 球体/椭球

```text
//gen stone x^2+y^2+z^2<=1
//gen -c stone x^2+y^2+z^2<=7^2
//gen -c -h glass x^2+y^2+z^2<=7^2
//gen -c stone (x/7)^2+(y/4)^2+(z/7)^2<=1
```

`-h` 只生成外壳：只有邻接非形状方块的方块会被放置。

### 圆环 / 心形 / 波浪（官方示例）

```text
//g stone (0.75-sqrt(x^2+y^2))^2+z^2 < 0.25^2
//g red_wool (z/2)^2+x^2+(5*y/4-sqrt(abs(x)))^2<0.6
//g -h glass sin(x*5)/2<y
//g -h glass cos(sqrt(x^2+z^2)*5)/2<y
//g stone -(z^2/12)+(y^2/4)-(x^2/12)>-0.03
```

### 表达式语法

- 算术：`+ - * / % ^`（`^` 是乘方，不是 XOR）
- 比较：`< > <= >= == != ~=`
- 逻辑：`&& || !`，真为 1，假为 0
- 位运算：`<< >>`、`~`（按 32 位整数）
- 三元：`条件 ? 真分支 : 假分支`
- 赋值：`= += -= *= /= %= ^=`；可创建临时变量
- 阶乘后缀 `!`；前缀/后缀 `++ --`
- 函数：`abs, acos, asin, atan, atan2, cbrt, ceil, cos, cosh, exp, floor, ln, log, log10, max,
  min, rint, round, sin, sinh, sqrt, tan, tanh`
- 其他：`rotate(x,y,angle)`、`swap(x,y)`、`random()`、`randint(max)`、`perlin(...)`、
  `voronoi(...)`、`ridgedmulti(...)`
- `rotate(a,b,angle)` / `swap(a,b)` **只接受变量并原地改写**，不会返回新坐标。XZ 平面旋转必须写
  `u=dx; v=dz; rotate(u,v,angle)`；半径 `sqrt(dx²+dz²)` 只能用来计算角度/宽度，不能当坐标参数。
- 常量：`e`、`pi`、`true`、`false`
- 控制：`if/else`、`while`、`do/while`、`for`；循环最多 256 次
- 最后一条语句的值会作为结果返回；末尾分号通常可省略

`type`/`data` 变量和 `query*` 函数使用 1.12 旧 ID；1.13+ 新方块请直接用 pattern 参数或先放占位
方块再 `//replace`。

### 表达式 mask

`//gmask =y<64`、`//replace =x^2+z^2<25 stone` 使用同一个表达式语法；返回 >0 匹配。
`//deform` 则是把 `x/y/z` 赋值为“从哪里复制”的新坐标。

## 在 CLI 中生成球体

```text
//pos1 0,0,0
//pos2 15,15,15
//gen minecraft:stone x^2+y^2+z^2<=1
```

- 选区必须是立方体，否则默认归一化会得到椭球/压扁形状。
- 想按真实半径：`//gen -c ... x^2+y^2+z^2<=7^2`。
- 生成后用 `//replace` 换材质，比在表达式里写复杂 pattern 更稳。
- 大选区表达式会逐方块计算；先用 `//size` 估算，必要时分块。

## 官方参考

- <https://worldedit.enginehub.org/en/latest/usage/generation/>
- <https://worldedit.enginehub.org/en/latest/usage/other/expressions/>

