# 【Minecraft】worldedit|generate 一键生成旋风2.0

> 作者：**imhols**（UID 632698683） · 2022年10月23日 · 类型：`DYNAMIC_TYPE_ARTICLE` · [原动态](https://www.bilibili.com/opus/719916645896683552)

**WorldEdit / 程序化建模相关**

## 动态内容

首先你得有generate的基础认识
[图片]
废话少说，看成品
[图片]
成品图
下面是设计思路包括包括基础轮廓→加噪声→旋转
[图片]
模拟轮廓
[图片]
desmos模拟x,y在-1到1的图像
网站：https://www.desmos.com/
这里用了三次方的曲线，和之前视频的一样
【Minecraft】用指令做出旋风 generate教程#2
[图片]
生成轮廓
[图片]
//generate 35 r=sqrt(x^2+z^2);10*(r-0.06)<(y+1)^3
...

## 指令

```text
//generate 35 r=sqrt(x^2+z^2);10*(r-0.06)<(y+1)^3
```

---

内容与图片版权归 **imhols** 所有；本页为作品集索引。
