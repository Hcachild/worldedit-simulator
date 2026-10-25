# 128³ 高级生成示例

这些是 `//gen` 的 128×128×128 艺术建模脚本。每个文件都是**完整的 WorldEdit 命令脚本**，
开头会清空 128³ 选区，末尾 `stop`；不会修改脚本以外的文件。

![gallery](../../docs/images/advanced-gallery.png)

完整图像作品集（等轴测、四视图、相机机位）：[docs/portfolio/README.md](../../docs/portfolio/README.md)。

## 怎么运行

### 页面

1. `＋` 新建投影，勾选 **128 × 128 × 128 大型画布**。
2. 打开命令面板，把某个 `.txt` 的内容粘进去，`Ctrl+Enter`。
3. 等待完成；大模型第一次渲染可能需要几秒到几十秒。
4. 满意后点“另存为”。

### CLI

```bat
:: 先建一个 128³ 空白投影（页面新建，或用 Python create_blank）
we.cmd schematics\my_heart.schem examples\advanced\01_heart_128.txt
```

脚本里的 `//pos1/2` 会固定到 0..127；目标文件必须是 128³，否则会裁切/越界。
脚本末尾 `stop` 让 CLI 保存并退出；通过页面运行时 `stop` 也无害。

### API / Agent

```bat
python tools\agent_run.py -f examples\advanced\01_heart_128.txt
```

## 龙卷风的白模 + 颜色曲线

`06_tornado_128.txt` 现在只生成**白色漏斗和场景**。颜色由脚本按 Y 轴分位曲线映射，不再手写几条水平色带：

```bat
python tools\colorize_y.py work\advanced\tornado_white128.schem ^
  --palette tornado_glass_layers ^
  --output work\advanced\tornado_colored.schem ^
  --overlay work\advanced\tornado_overlay.schem ^
  --send --name tornado_colored
```

- `tornado`：不透明灰/白渐变
- `tornado_glass` / `tornado_glass_layers`：上部换成白色、淡蓝、青色、蓝色玻璃，增强透明层次
- 脚本会读取每个非空气 Y 层的数量，用**累计分位**而不是直接 Y 位置来分配颜色，避免宽大的顶部把白色/蓝色吃掉。
- `--send` 在当前 128³ 规模下通过 `/api/upload` 上传完整结果并加载；WorldEdit-CLI 的 `//paste` 对大剪贴板不稳定，脚本保留 overlay 供手动/小尺寸使用。

## 作品列表

| # | 文件 | 内容 | 验证方块数 | CLI 约耗时 |
|---|---|---|---|---|
| 01 | `01_heart_128.txt` | 鎏金心 + 黑石底座 | 254k | 15s |
| 02 | `02_arch_bridge_128.txt` | 三拱高架桥、河、树、灯 | 279k | 35s |
| 03 | `03_donut_128.txt` | 粉色糖霜甜甜圈 + 糖针 + 盘子 | 282k | 11s |
| 04 | `04_rubik_128.txt` | 3×3 魔方 + 切角 + 嵌套内层 | 228k | 31s |
| 05 | `05_ribbed_tunnel_128.txt` | 弯曲肋拱隧道 + 铁轨 | 181k | 15s |
| 06 | `06_tornado_128.txt` | 上宽下窄白模 + 平滑双曲线尘柱；再用 `colorize_y.py` 玻璃分层上色 | 119k | 15s |
| 07 | `07_rain_mandala_128.txt` | 同心圆/三角形/五边形曼陀罗 | 43k | 23s |
| 08 | `08_hex_honeycomb_128.txt` | 六边形蜂巢墙/蜂蜜背板 | 145k | 9s |
| 09 | `09_onion_dome_128.txt` | 俄罗斯洋葱头穹顶 + 十字 | 125k | 12s |
| 10 | `10_wheat_field_128.txt` | Perlin 麦田 + 小路/篱笆/草垛 | 220k | 25s |
| 11 | `11_basalt_columns_128.txt` | 六边形玄武岩柱 + 苔藓/熔岩 | 239k | 12s |
| 12 | `12_conch_shell_128.txt` | 螺旋海螺 + 壳口/珍珠色带 | 17k | 11s |
| 13 | `13_mandelbrot_128.txt` | 曼德尔布罗特金浮雕 | 60k | 26s |
| 14 | `14_mandelbulb_128.txt` | 8 次幂 Mandelbulb 壳 | 67k | 24s |
| 15 | `15_menger_128.txt` | 4 级门格尔海绵 | 134k | 15s |
| 16 | `16_mandelbox_128.txt` | Mandelbox（10 次迭代） | 606k | 79s |
| 17 | `17_mobius_128.txt` | 莫比乌斯带 + 发光边 | 86k | 25s |
| 18 | `18_galaxy_128.txt` | 对数螺旋银河 + 黑洞/吸积环 | 120k | 27s |

数字来自一次性本机验证，因随机糖针/云/星尘会略有浮动。CLI 时间不含网页渲染。

## 先跑哪个

- 想看“公式生成”的极限：`14_mandelbulb_128.txt`、`15_menger_128.txt`、`16_mandelbox_128.txt`。
- 想直接当建筑/展示：`01_heart_128.txt`、`03_donut_128.txt`、`09_onion_dome_128.txt`、
  `18_galaxy_128.txt`。
- 想改造成自己的场景：`02_arch_bridge_128.txt`、`05_ribbed_tunnel_128.txt`、
  `06_tornado_128.txt`、`10_wheat_field_128.txt`。

## 性能提示

- `16_mandelbox_128.txt` 约 60 万块；页面会跳过方块点选（`[pick] disabled`），渲染仍可用。
- 如果浏览器卡住，先刷新页面，等右上角 `[render]` 指标出来再操作。
- 想快速迭代，把脚本里的 `127` 改成 `63`，所有坐标按比例缩小；公式本身不用改。
  但 `-r` 的绝对尺度会变，适合看轮廓，不适合最终出图。

## 相关文档

- [高级 `//gen` 方法与公式](../../docs/worldedit/advanced-generation.md)
- [生成与表达式](../../docs/worldedit/generation-expressions.md)
- [CLI 细节](../../docs/worldedit/cli.md)
- [踩坑清单](../../docs/worldedit/gotchas.md)
