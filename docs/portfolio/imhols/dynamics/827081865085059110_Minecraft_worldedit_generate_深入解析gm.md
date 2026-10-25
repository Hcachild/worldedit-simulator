# 【Minecraft】worldedit|generate 深入解析gmegabuf()缓冲函数——从原理到应用

> 作者：**imhols**（UID 632698683） · 2023年8月7日 · 类型：`DYNAMIC_TYPE_ARTICLE` · [原动态](https://www.bilibili.com/opus/827081865085059110)

**WorldEdit / 程序化建模相关**

## 动态内容

一、格式和用法
[图片]
https://worldedit.enginehub.org/en/latest/usage/other/expressions/
（megabuf有全局的gmegabuf和本地的megabuf，为了方便，下文只写gmegabuf）
看wiki翻译不难理解，gmegabuf本质上是一个数组，数组默认为0；
提供了三个函数 
1.1、gmegabuf()
先讲这两个
gmegabuf(索引值)：调用数组对应索引值处的值，后期调用使用
...

## 图片

![827081865085059110 image 1](../images/dynamics/827081865085059110/01.jpg)

![827081865085059110 image 2](../images/dynamics/827081865085059110/02.jpg)

![827081865085059110 image 3](../images/dynamics/827081865085059110/03.jpg)

---

内容与图片版权归 **imhols** 所有；本页为作品集索引。
