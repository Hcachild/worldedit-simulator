# 【Minecraft】worldedit|generate 正多边形及正多边形尖顶的设计思路

> 作者：**imhols**（UID 632698683） · 2022年10月26日 · 类型：`DYNAMIC_TYPE_ARTICLE` · [原动态](https://www.bilibili.com/opus/721290545796743168)

**WorldEdit / 程序化建模相关**

## 动态内容

成品：八角尖顶
[图片]
//generate 35 -h r=1-(y+1)^2/4;n=8;sqrt(x^2+z^2)/cos(pi/n)*cos(pi/n-((atan2(x,z)+pi)%(2*pi/n)))<r
[图片]
一
做这种涉及正多边形的形状问题，我们首先要找到一个能画出正多边形的通式或办法，目前我能想到的和找到的有两种办法：
1、一种是能够画出边是绝对平直的正多边形，这是在知乎上找到的
zhuanlan.zhihu.com/p/522197221
...

## 指令

```text
//generate 35 -h r=1-(y+1)^2/4;n=8;sqrt(x^2+z^2)/cos(pi/n)*cos(pi/n-((atan2(x,z)+pi)%(2*pi/n)))<r
```

---

内容与图片版权归 **imhols** 所有；本页为作品集索引。
