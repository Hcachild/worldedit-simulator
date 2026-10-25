# 文档索引

本目录记录 `worldedit-simulator` 的部署、架构、API、渲染和 WorldEdit 用法。目标是让新接手的人不依赖历史对话或反复联网搜索，也能完成部署和日常使用。

## 先读哪一篇

| 你的目标 | 先读 |
|---|---|
| 从零部署、换机器、离线安装 | [deployment.md](deployment.md) |
| 了解模块划分、数据流、状态与进程模型 | [architecture.md](architecture.md) |
| 用 AI Agent / HTTP 修改当前投影 | [api.md](api.md) |
| 调整材质、模型、性能 | [rendering.md](rendering.md) |
| 遇到报错、卡死、空白页面 | [troubleshooting.md](troubleshooting.md) |
| 查 WorldEdit 命令、选区、生成 | [worldedit/README.md](worldedit/README.md) |
| 看 128³ 图像作品集与机位 | [portfolio/README.md](portfolio/README.md) |
| 看 256³ 三叶草结/烟花与生成器 | [portfolio/256/README.md](portfolio/256/README.md) |
| 做 128³/256³ 艺术模型、看高级 `//gen` | [worldedit/advanced-generation.md](worldedit/advanced-generation.md) |

## WorldEdit 使用文档

| 文档 | 内容 |
|---|---|
| [worldedit/README.md](worldedit/README.md) | 总览、命令速查、CLI 与游戏内差异 |
| [worldedit/commands.md](worldedit/commands.md) | 按类别整理的常用命令 |
| [worldedit/selection-regions.md](worldedit/selection-regions.md) | 选区、区域操作 |
| [worldedit/patterns-masks.md](worldedit/patterns-masks.md) | 方块 pattern 与 mask |
| [worldedit/clipboard-schematics.md](worldedit/clipboard-schematics.md) | 复制粘贴、投影格式与保存 |
| [worldedit/generation-expressions.md](worldedit/generation-expressions.md) | 球体/圆柱/`//gen` 与表达式 |
| [worldedit/advanced-generation.md](worldedit/advanced-generation.md) | 128³ 艺术建模、B 站教程索引、18 个配方、256³ 三叶草结/烟花 |
| [worldedit/tools-brushes.md](worldedit/tools-brushes.md) | 工具、笔刷及 CLI 限制 |
| [worldedit/cli.md](worldedit/cli.md) | 无头 CLI 的行为、数据和退出码 |
| [worldedit/gotchas.md](worldedit/gotchas.md) | 踩坑清单（含本项目实测问题） |

## 图像作品集

- [portfolio/README.md](portfolio/README.md)：18 张 128³ 等轴测图、四视图对比、相机机位与生成指令。
- [portfolio/256/README.md](portfolio/256/README.md)：256³ 三叶草结（Frenet 正方形扫掠）与 glowstone 烟花。
- [portfolio/imhols/README.md](portfolio/imhols/README.md)：B站 imhols 的 WorldEdit 进阶专栏/动态索引。

## 版本基线

- WorldEdit-CLI：`7.4.7-SNAPSHOT`（EngineHub 构建 30360）
- Java：Temurin JRE 25（WorldEdit 7.4.x 的 class file 版本为 69）
- 渲染资源：Minecraft Java 1.21.1 客户端 jar（DataVersion 3955）
- 实测环境：Windows 11 x64、Python 3.11
- 3D 资源解析：`block-model-renderer` 2.20.0（MPL-2.0）

## 官方资料

- 命令列表：<https://worldedit.enginehub.org/en/latest/commands/>
- 使用手册：<https://worldedit.enginehub.org/en/latest/usage/>
- 生成：<https://worldedit.enginehub.org/en/latest/usage/generation/>
- 表达式：<https://worldedit.enginehub.org/en/latest/usage/other/expressions/>
- 选区：<https://worldedit.enginehub.org/en/latest/usage/regions/selections/>
- 区域操作：<https://worldedit.enginehub.org/en/latest/usage/regions/regionops/>
- 剪贴板：<https://worldedit.enginehub.org/en/latest/usage/clipboard/>
- Pattern：<https://worldedit.enginehub.org/en/latest/usage/general/patterns/>
- Mask：<https://worldedit.enginehub.org/en/latest/usage/general/masks/>
- 工具：<https://worldedit.enginehub.org/en/latest/usage/tools/tools/>
- 笔刷：<https://worldedit.enginehub.org/en/latest/usage/tools/brushes/>
- B 站 `//gen` 系统课：<https://www.bilibili.com/video/BV1AP4y1b7EN/>
- 128³ 示例：[examples/advanced](../examples/advanced/README.md)
- 256³ 三叶草结/烟花：[portfolio/256](portfolio/256/README.md)

文档中的命令以 WorldEdit 7.4.x 为准；方块 ID 使用 1.13+ 的命名空间 ID（例如 `minecraft:stone`），不再使用 1.12 及以前的数字 ID。
