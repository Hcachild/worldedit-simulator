# 128³ Image Portfolio

18 件 128×128×128 的 WorldEdit `//gen` 作品。全部图像由应用内**截图**按钮生成（只截 3D canvas，不含 UI），使用正交投影和自动适配的等轴测/工程视角；每张图的 `position`、`target`、`up`、`azimuth`、`polar`、`zoom`、正交视锥与模型 bounds 记录在 [manifest.json](manifest.json) 和 `work/shots/<name>.json` 中。

![all models](00_contact_sheet.png)

## 工程制图视角

同一个六边形蜂巢模型的等轴测、前视、顶视、右视。视角由 `Viewer.setView()` 根据**实际方块包围盒**自动取景，不是固定相机距离。

![engineering views](00_engineering_views.png)

| 视角 | 方向 | up | 方位角 | 极角 | 图像 |
|---|---|---|---:|---:|---|
| 等轴测 / isometric | `[0.5773502691896257, 0.5773502691896257, 0.5773502691896258]` | `[0, 1, 0]` | 45.0° | 54.7° | [png](images/08_hex_honeycomb_128_iso.png) |
| 前视 / front | `[0, 6.065069546397984e-17, 1]` | `[0, 1, 0]` | 0.0° | 90.0° | [png](images/08_hex_honeycomb_front.png) |
| 顶视 / top | `[0, 0.9999999999995, 1.0000444493030292e-06]` | `[0, 0, -1]` | 0.0° | 0.0° | [png](images/08_hex_honeycomb_top.png) |
| 右视 / right | `[1, 6.065069546397984e-17, 6.128247354172962e-17]` | `[0, 1, 0]` | 90.0° | 90.0° | [png](images/08_hex_honeycomb_right.png) |

## 作品

| # | 作品 | 图像 | 生成指令 | 方位角 / 极角 |
|---|---|---|---|---:|
| 01 | 鎏金心 / Kintsugi Heart | <img src="images/01_heart_128_iso.png" width="300" alt="鎏金心 / Kintsugi Heart"> | [`examples/advanced/01_heart_128.txt`](../../examples/advanced/01_heart_128.txt) | 45.0° / 54.7° |
| 02 | 三拱高架桥 / Three-Arch Viaduct | <img src="images/02_arch_bridge_128_iso.png" width="300" alt="三拱高架桥 / Three-Arch Viaduct"> | [`examples/advanced/02_arch_bridge_128.txt`](../../examples/advanced/02_arch_bridge_128.txt) | 45.0° / 54.7° |
| 03 | 糖霜甜甜圈 / Frosted Donut | <img src="images/03_donut_128_iso.png" width="300" alt="糖霜甜甜圈 / Frosted Donut"> | [`examples/advanced/03_donut_128.txt`](../../examples/advanced/03_donut_128.txt) | 45.0° / 54.7° |
| 04 | 嵌套魔方 / Nested Rubik | <img src="images/04_rubik_128_iso.png" width="300" alt="嵌套魔方 / Nested Rubik"> | [`examples/advanced/04_rubik_128.txt`](../../examples/advanced/04_rubik_128.txt) | 45.0° / 54.7° |
| 05 | 肋拱隧道 / Ribbed Tunnel | <img src="images/05_ribbed_tunnel_128_iso.png" width="300" alt="肋拱隧道 / Ribbed Tunnel"> | [`examples/advanced/05_ribbed_tunnel_128.txt`](../../examples/advanced/05_ribbed_tunnel_128.txt) | 45.0° / 54.7° |
| 06 | 龙卷风 / Tornado | <img src="images/06_tornado_128_iso.png" width="300" alt="龙卷风 / Tornado"> | [`examples/advanced/06_tornado_128.txt`](../../examples/advanced/06_tornado_128.txt) | 45.0° / 54.7° |
| 07 | 雨纹曼陀罗 / Rain Mandala | <img src="images/07_rain_mandala_128_iso.png" width="300" alt="雨纹曼陀罗 / Rain Mandala"> | [`examples/advanced/07_rain_mandala_128.txt`](../../examples/advanced/07_rain_mandala_128.txt) | 45.0° / 54.7° |
| 08 | 六边形蜂巢 / Hex Honeycomb | <img src="images/08_hex_honeycomb_128_iso.png" width="300" alt="六边形蜂巢 / Hex Honeycomb"> | [`examples/advanced/08_hex_honeycomb_128.txt`](../../examples/advanced/08_hex_honeycomb_128.txt) | 45.0° / 54.7° |
| 09 | 洋葱头穹顶 / Onion Dome | <img src="images/09_onion_dome_128_iso.png" width="300" alt="洋葱头穹顶 / Onion Dome"> | [`examples/advanced/09_onion_dome_128.txt`](../../examples/advanced/09_onion_dome_128.txt) | 45.0° / 54.7° |
| 10 | 麦田 / Wheat Field | <img src="images/10_wheat_field_128_iso.png" width="300" alt="麦田 / Wheat Field"> | [`examples/advanced/10_wheat_field_128.txt`](../../examples/advanced/10_wheat_field_128.txt) | 45.0° / 54.7° |
| 11 | 六边形玄武岩柱 / Basalt Columns | <img src="images/11_basalt_columns_128_iso.png" width="300" alt="六边形玄武岩柱 / Basalt Columns"> | [`examples/advanced/11_basalt_columns_128.txt`](../../examples/advanced/11_basalt_columns_128.txt) | 45.0° / 54.7° |
| 12 | 海螺 / Conch Shell | <img src="images/12_conch_shell_128_iso.png" width="300" alt="海螺 / Conch Shell"> | [`examples/advanced/12_conch_shell_128.txt`](../../examples/advanced/12_conch_shell_128.txt) | 45.0° / 54.7° |
| 13 | 曼德尔布罗特 / Mandelbrot | <img src="images/13_mandelbrot_128_iso.png" width="300" alt="曼德尔布罗特 / Mandelbrot"> | [`examples/advanced/13_mandelbrot_128.txt`](../../examples/advanced/13_mandelbrot_128.txt) | 45.0° / 54.7° |
| 14 | 曼德尔球 / Mandelbulb | <img src="images/14_mandelbulb_128_iso.png" width="300" alt="曼德尔球 / Mandelbulb"> | [`examples/advanced/14_mandelbulb_128.txt`](../../examples/advanced/14_mandelbulb_128.txt) | 45.0° / 54.7° |
| 15 | 门格尔海绵 / Menger Sponge | <img src="images/15_menger_128_iso.png" width="300" alt="门格尔海绵 / Menger Sponge"> | [`examples/advanced/15_menger_128.txt`](../../examples/advanced/15_menger_128.txt) | 45.0° / 54.7° |
| 16 | 曼德尔箱 / Mandelbox | <img src="images/16_mandelbox_128_iso.png" width="300" alt="曼德尔箱 / Mandelbox"> | [`examples/advanced/16_mandelbox_128.txt`](../../examples/advanced/16_mandelbox_128.txt) | 45.0° / 54.7° |
| 17 | 莫比乌斯带 / Möbius Strip | <img src="images/17_mobius_128_iso.png" width="300" alt="莫比乌斯带 / Möbius Strip"> | [`examples/advanced/17_mobius_128.txt`](../../examples/advanced/17_mobius_128.txt) | 45.0° / 54.7° |
| 18 | 银河 / Galaxy | <img src="images/18_galaxy_128_iso.png" width="300" alt="银河 / Galaxy"> | [`examples/advanced/18_galaxy_128.txt`](../../examples/advanced/18_galaxy_128.txt) | 45.0° / 54.7° |

## 生成与复现

每个作品都有独立的 128³ 命令脚本，脚本开头是 `//pos1 0,0,0` / `//pos2 127,127,127`，末尾 `stop`：

```bat
:: 新建 128×128×128 空白 schem，然后运行
we.cmd schematics\my_heart.schem examples\advanced\01_heart_128.txt

:: 或在页面里：新建 -> 勾选 128³ -> 粘贴脚本 -> Ctrl+Enter
:: 视角：等轴测 / 前视 / 后视 / 左视 / 右视 / 顶视 / 底视
:: 截图：右上角“截图”，图像与机位 JSON 写入 work/shots/
```

脚本索引见 [examples/advanced](../../examples/advanced/README.md)，方法与公式见 [advanced-generation.md](../worldedit/advanced-generation.md)。

## 截图机位格式

```json
"camera": {
  "position": [x, y, z],
  "target": [x, y, z],
  "up": [x, y, z],
  "direction": [x, y, z],
  "azimuthDeg": 45.0,
  "polarDeg": 54.7356,
  "zoom": 1,
  "left": -..., "right": ..., "top": ..., "bottom": ...
}
```

- 等轴测方向为 `(1,1,1)`，正交投影，`polar≈54.7356°`、`azimuth=45°`。
- 前/后/左/右为水平正交，顶/底为垂直正交；拍摄时自动按模型包围盒和画布宽高比取景。
- 截图按钮写入 `work/shots/<model>_<view>_<timestamp>.png` 和同名 `.json`；`work/` 不入库。

## 文件

- `images/`：18 张 900×900 PNG + 4 张工程视角
- `manifest.json`：完整机位、bounds、尺寸、脚本路径
- `00_contact_sheet.png`：全部作品缩略图
- `00_engineering_views.png`：同一模型的四视图对比

## 相关

- [高级 //gen 文档](../worldedit/advanced-generation.md)
- [18 个生成脚本](../../examples/advanced/README.md)
- [应用截图/视角源码](../../web/static/js/viewer.js)

