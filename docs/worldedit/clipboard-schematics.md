# 剪贴板与投影

## 剪贴板

| 命令 | 说明 |
|---|---|
| `//copy [-e] [-b] [-m <mask>]` | 复制选区到剪贴板 |
| `//cut [-e] [-b] [-m <mask>]` | 复制并删除 |
| `//paste [-aoeb] [-m <mask>] [-s] [-n] [-o]` | 粘贴 |
| `//rotate <y> [x] [z]` | 绕轴旋转，90° 倍数 |
| `//flip [north\|south\|east\|west\|up\|down]` | 翻转 |
| `//clearclipboard` | 清空剪贴板 |
| `//size -c` | 剪贴板尺寸 |

### 相对位置

`//copy` 记录的不是“选区中心”，而是**复制时你相对选区的位置**。相对粘贴时以这个相对位置为准：

- 复制时站在建筑顶部 → 相对粘贴会把建筑放在你脚下。
- `//paste -o` 忽略相对位置，回到复制时选区原点。
- 想围绕建筑中心旋转，复制时尽量站在中心。

CLI 没有玩家，`//copy`/`//paste` 的“相对位置”由控制台 Actor 的位置决定，通常不可靠；本项目
更推荐直接用文件级操作或 `//schem` 载入加 `//paste -o`。需要精确时，把操作拆成
`//copy` 后的 `//paste -o` 或直接对同一坐标做区域操作。

### 粘贴 flags

| Flag | 含义 |
|---|---|
| `-a` | 不粘贴空气（等价 `-m #existing`） |
| `-o` | 回到原坐标 |
| `-s` | 把选区设为粘贴区域 |
| `-n` | 只选不粘 |
| `-e` | 粘贴实体 |
| `-b` | 粘贴生物群系 |
| `-m <mask>` | 只粘贴匹配方块 |

CLI 没有实体/生物群系，`-e/-b` 基本无效果。

## 投影（schematic）

### 保存/载入

```text
//schem save my_build
//schem load my_build
//schem list
//schem list -n
//schem delete my_build
//schem listformats
```

- `//schem save` 保存的是**剪贴板**，不是当前选区；要先 `//copy`。
- CLI 载入 `.schem` 后，命令直接修改文件并自动保存；`//schem save` 不是必需的。
- 世界/服务器里的路径：`plugins/WorldEdit/schematics/`（Bukkit）或
  `config/worldedit/schematics/`（Fabric/Forge）。本项目 CLI 的路径是 `worldedit/schematics/`。
- 名称可以带子目录：`//schem save houses/small`。

### 格式

- **Sponge `.schem`**：1.13+，本项目支持 v1/v2/v3。
- 旧 **MCEdit `.schematic`**：WorldEdit 可读，但 CLI 数据/本项目 Web 不支持；请先转换为 `.schem`。

Sponge `.schem` 是一个 gzip 压缩的 NBT 文件：

```text
Schematic (compound)
  Version: int          // 1/2/3
  DataVersion: int      // 例如 3955 = MC 1.21.1
  Width/Height/Length: short
  Offset: int[3]
  Metadata: { WEOffsetX/Y/Z }
  PaletteMax: int
  Palette: { "minecraft:stone": 0, ... }
  BlockData: byte[]     // 每格一个 varint palette 索引，索引顺序 (y*Length+z)*Width+x
  BlockEntities: list
```

v3 把方块放在 `Schematic.Blocks.Palette` / `Blocks.Data`。根 compound 名必须是 `Schematic`；
否则 WorldEdit 识别不了。

### DataVersion 与方块

- CLI/渲染器按 `DataVersion` 找方块表和资源。
- 本项目的 CLI 数据只发布了部分版本（见 [cli.md](cli.md)）；渲染材质固定 1.21.1。
- `tools/retarget_schem.py` 只改 `DataVersion` 元数据，不转换方块：
  - 旧 → 新通常可用（旧方块仍存在）。
  - 新 → 旧可能丢失新方块/状态。
- 不要用 `retarget` 伪装成另一个版本后使用该版本不存在的新方块。

### 在本项目中保存

页面上的“保存”把 `work/current.schem` 覆盖回 `schematics/<source>.schem`；“另存为”写新文件。
直接编辑 `schematics/` 里的文件不会自动加载，需要在页面点击或调用 `/api/load`。
`work/`、`worldedit/` 都是运行时目录，不要手动当源文件管理。

### 文件命名

- 只接受 `.schem`；上传同名自动加 `_1`。
- 不使用路径分隔符；中文/空格可用。
- 删除不可恢复；删除当前文件会关闭投影。

## 示例：把 demo 的一段复制到新文件

```text
//pos1 0,0,0
//pos2 12,7,12
//copy
//schem save demo_copy
```

在 CLI 中，`//copy` 后剪贴板有效；`//schem save demo_copy` 写入
`worldedit/schematics/demo_copy.schem`。下一次可以：

```text
//schem load demo_copy
//paste -o
```

## 官方参考

- <https://worldedit.enginehub.org/en/latest/usage/clipboard/>
- <https://github.com/SpongePowered/Schematic-Specification>

