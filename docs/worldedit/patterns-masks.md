# Pattern 与 Mask

## 区别

- **Pattern**：放什么。用于 `//set`、`//replace` 的目标、`//gen` 的方块、`/brush` 的材质。
- **Mask**：改哪些。用于 `//replace` 的 from、`//gmask`、`/mask`、部分 brush 参数。

Pattern 和 mask 经常可以写得很像，但语义不同：`//replace stone glass` 的 `stone` 是 mask，
`glass` 是 pattern。

## Pattern

### 单方块 / 带状态 / NBT

```text
//set minecraft:stone
//set oak_stairs[facing=east,half=top]
//set note_block[instrument=chime,note=18]
//set oak_sign[rotation=12]{'is_waxed':1}
//set oak_sign|Line1|Line2
//set player_head|dinnerbone
//set spawner|squid
```

- 状态写在 `[]`，键值用逗号分隔；未写的状态使用默认值。
- NBT 写在状态后，使用 SNBT：`block[state=value]{'key':value}`。
- 告示牌文本用 `|` 分隔；带空格时整个参数加引号。
- 头颅皮肤、刷怪笼实体用 `|`。

### 特殊来源

| Pattern | 说明 |
|---|---|
| `hand` | 主手方块（CLI 无玩家，不可用） |
| `offhand` | 副手方块（CLI 无玩家，不可用） |
| `pos1` | pos1 处方块 |
| `#clipboard` | 按剪贴板排列取方块 |
| `#clipboard@[x,y,z]` | 带偏移 |

### 随机 / 权重

```text
//set stone,diorite,andesite,granite
//set 50%red_wool,10%red_stained_glass
```

逗号分隔等概率；`x%pattern` 是相对权重，不必加到 100。`50%red_wool,10%glass` = 50/(50+10) 与
10/(50+10)。单个 `5%dirt` 不合法；需要 5% 概率请用 `%5` mask。

### 随机状态 / 类别

```text
//set *oak_log
//set ##wool
//set ##*slabs
```

- `*block`：在方块的所有状态中随机。
- `##tag`：在 tag 内的方块默认状态中随机；`##*tag` 使用所有状态。
- 常见 tag：`##stairs`、`##slabs`、`##wool`、`##carpets`、`##planks`、`##logs`。

### 只改类型/状态

```text
//replace oak_stairs ^acacia_stairs
//replace ##slabs ^[type=double]
//set ^[waterlogged=false]
```

`^` 是“应用”pattern：只改类型或指定状态，保留其余状态/方向。适合批量换材质但保留楼梯朝向。

## Mask

### 组合

空格表示 **交集**（同时满足）：

```text
//replace "stone <air" minecraft:dirt
/mask "air #sel"
```

逗号表示 **并集**（匹配任一）：

```text
//replace oak_fence[east=true],oak_fence_gate minecraft:air
```

`!` 表示否定：

```text
//replace !dirt,stone,grass_block minecraft:stone
```

注意：`//gmask` 与笔刷 `/mask` 会叠加；两个 mask 是交集，可能什么都不匹配。

### 内置 mask

| Mask | 匹配 |
|---|---|
| `#existing` | 非空气（包含 cave_air 等区别） |
| `#solid` | 实体可碰撞的固体 |
| `#fullcube` | 占满整格的方块 |
| `#surface` / `#exposed` | 至少有一面暴露在空气中 |
| `#region` / `#sel` / `#selection` | 命令执行时的选区副本 |
| `#dregion` / `#dsel` | 动态跟随当前选区 |
| `#clipboard` | 与剪贴板同位置的方块 |
| `##tag` | 方块 tag |

### 偏移 / 邻接

```text
//replace >##planks smooth_stone_slab
//replace ~spawner glowstone
```

- `>` 上方 / `<` 下方匹配另一个 mask。
- `~` 匹配与另一个 mask 相邻（含上下，不含对角）的方块。

### 随机噪声

```text
//replace %50 minecraft:stone
```

`%50` 匹配 50% 的方块。注意 pattern 的 `50%pattern` 是权重，mask 的 `%50` 才是概率。

### 状态 mask

```text
//replace ^[open=false] minecraft:air
//replace ^=[open=false] minecraft:air
```

- `^[...]` 宽松：缺少该属性的方块也算匹配。
- `^=[...]` 严格：必须拥有该属性且等于给定值。

### 表达式 mask

```text
//gmask =y<64
//gmask =queryRel(0,-2,0,0,0)
```

`=` 后接表达式，返回 >0 匹配；可用 `x,y,z`。适合按高度/噪声筛选。

### 生物群系 / 其他

```text
//replace $minecraft:plains minecraft:grass_block
```

`$biome` 匹配生物群系。CLI 的投影通常没有 biome 数据，这类 mask 基本不可用。`//gmask` 无参数
清除全局 mask。

## 实战

把选区里的石头换成 70% 石头 + 30% 安山岩，只改地表：

```text
//replace "stone #surface" 70%stone,30%andesite
```

把所有楼梯换成云杉楼梯但保留朝向：

```text
//replace ##stairs ^spruce_stairs
```

把所有含水方块的水去掉：

```text
//set ^[waterlogged=false]
```

在 planks 上方铺半砖：

```text
//replace >##planks smooth_stone_slab
```

## CLI 注意

- `hand`、`offhand` 不可用；`pos1` 可用（pos1 是坐标，不依赖玩家）。
- `#region`/`#dregion` 在 CLI 中选区是当前会话的；每次脚本先设置 pos1/pos2。
- 复杂表达式/大选区会显著变慢；先用 `//count` 估算。

## 官方参考

- <https://worldedit.enginehub.org/en/latest/usage/general/patterns/>
- <https://worldedit.enginehub.org/en/latest/usage/general/masks/>
