# 渲染与性能

## 资源来源

3D 渲染使用 Minecraft Java **1.21.1** 客户端 jar 作为资源包：

- 路径：`assets/client.jar`（约 27MB，`.gitignore`，不随仓库分发）
- 获取：`setup.cmd` 或 `setup-assets.cmd`，优先复制本机
  `%APPDATA%\.minecraft\versions\1.21.1\1.21.1.jar`
- 解析：`block-model-renderer` 2.20.0（MPL-2.0，本地 vendored）
- 本地依赖：`web/static/vendor/block-model-renderer.min.js`、
  `block_model_renderer_bg.wasm`、`web/static/assets.zip`（方块实体覆盖）
- 服务端路由：`GET /assets/client.jar`

如果客户端 jar 缺失，前端会回退到颜色方块，并提示运行 `setup-assets.cmd`；这时不会显示真实
形状和材质。

## 支持的形状

由完整 blockstate/model 管线处理：

- 完整方块、台阶（上/下/双）、楼梯、栅栏、栅栏门、墙、玻璃板、门、活板门、梯子、铁栏杆
- 植物、花、作物、树苗、藤蔓、火把、灯笼等 cutout 模型
- 原木/柱子的 `axis`、楼梯/门的 `facing`、半砖的 `type` 等朝向/状态
- 水、岩浆等流体的表面形状
- 箱子、告示牌、床、头颅、旗帜等方块实体（由解析库的覆盖包处理）
- 玻璃、染色玻璃、冰等半透明方块
- 草方块、树叶、水等生物群系 tint

当前仅支持资源包/模型能表达的方块；实体、粒子、红石逻辑不渲染。

## 管线

```
state.palette + state.data
  -> 拆分 "minecraft:oak_stairs[facing=east,half=bottom]" 为 id + properties
  -> 扁平 palette + Int32Array raw（type,x,y,z,...）
  -> block-model-renderer.createScene()
       blockstate: variants / multipart
       model: parent 链、elements、textures、uv、rotation
       texture atlas + tint + cutout/translucent
       face culling + greedy merging + translucent sort
  -> handle.group，按 1/16 缩放并居中
  -> viewer.scene
```

拾取层是独立的不可见 `InstancedMesh`，每个非空气方块一个单位立方体；它不加入
`scene`，只用于 `Raycaster`，因此不增加 draw call，但会占实例矩阵内存。

## 优化清单

已做：

- 隐藏面剔除（相邻不透明方块之间的面不生成）
- 贪心面合并（同平面同材质合成大 quad）
- 少量 draw call（整个场景合并成 1–3 个批次）
- 纹理图集，避免每种方块一个 draw call
- cutout 用 `alphaTest`，不进入半透明排序；半透明单独排序
- prepared assets 缓存（`prepareAssets({cache:true})`）
- 材质只加载一次；只有状态变更才重建场景
- 新状态取消旧构建（`shouldCancel` + token），旧 handle `dispose()`
- 拾取层不参与绘制
- renderer `pixelRatio` 上限 2；关闭阴影、后处理
- `lighting: {light:false}`，保留世界面光照但关闭 light volume flood fill
- WASM 网格化器（`block_model_renderer_bg.wasm`），不可用时回退 JS
- 空投影不加载材质（先解析方块数据，空则直接返回）

实测（同一台机器、浏览器 WebGL）：

| 场景 | 方块数 | draw calls | triangles |
|---|---:|---:|---:|
| 16³ 石头球体 | 1,736 | 1 | 1,522 |
| 13×8×13 demo | 730 | 1 | 286 |
| 8³ 玻璃立方体 | 512 | 1 | 12（贪心合并） |
| 19 种混合方块 | 19 | 3 | 288 |

旧的纯立方体渲染是每个方块 12 triangles，且不剔除内部：16³ 球体约 20,832 triangles；
新管线减少约 13 倍，且材质和形状正确。玻璃立方体因整面合并，从 6,144 triangles 降到 12。

## 当前瓶颈

- 每次命令/Agent 更新都重建整个场景；百万方块级投影会有构建时间。
- 场景合并成少量 mesh，没有额外的分块视锥裁剪/LOD；相机只看到局部时仍可能绘制整批。
- 拾取是逐实例 raycast；百万级方块点击会变慢。
- 材质固定 1.21.1；其他 DataVersion 的新方块可能缺失或状态名不同。
- 关闭了 light volume/AO；需要火把照明和平滑 AO 时要开启，构建时间会上升。
- 首次加载 27MB 客户端 jar，之后靠浏览器缓存和 prepared assets 复用。
- 资源包是原版风格；自定义资源包/模组方块需要替换/叠加资源，当前没有 UI。

## 可调参数

`web/static/js/mc-renderer.js` 的 `createScene` 选项：

| 选项 | 当前 | 说明 |
|---|---|---|
| `version` | `1.21.1` | 资源版本 |
| `lighting` | `{light:false}` | 世界面光照，不做 flood fill；可改 `"item"` 或开 `light` |
| `optimize` | `true` | 合并/剔除；关闭会保留每个方块对象，慢很多 |
| `animate` | `true` | 动画纹理（水/岩浆等） |
| `biome` | 温带 | 草/树叶/水 tint |
| `onProgress` | 有 | 构建进度 |
| `shouldCancel` | 有 | 新状态取消旧构建 |

解析库还支持 `resortDistance`、`maxAtlas`、`sharedAtlas` 等优化参数；当前使用默认值。

## 调试

- 页面控制台会打印 `[render] {drawCalls, tris}`；也可读 `window.__renderMetrics`。
- 如果看到颜色方块和 toast，检查 `assets/client.jar` 是否可访问、浏览器 Network 里
  `client.jar`/`assets.zip`/WASM 是否 404。
- 检查当前投影的 DataVersion 是否和 1.21.1 资源匹配；不匹配时先看
  [worldedit/cli.md](worldedit/cli.md) 的 DataVersion 表。
- 需要拍照/自动化截图时，不要用 `msedge --screenshot` 打开带 SSE 的页面（长连接可能让
  截图进程不退出）；用 CDP 的 `Page.captureScreenshot`。

## 更新材质

1. 替换 `assets/client.jar`（推荐 1.21.1）。
2. 同步 `mc-renderer.js` 的 `ASSET_VERSION` 和 `fetch_assets.py` 的 `VERSION`。
3. 删除浏览器缓存或 F5。
4. 如果换的是更高版本，检查 `block-model-renderer` 是否支持对应的模型格式；必要时升级库和
   `assets.zip`/WASM。
