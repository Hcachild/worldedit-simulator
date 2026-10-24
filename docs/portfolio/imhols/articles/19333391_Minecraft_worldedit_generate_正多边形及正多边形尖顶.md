# 【Minecraft】worldedit|generate 正多边形及正多边形尖顶的设计思路

> 作者：**imhols**（UID 632698683） · 发布：2022-10-26 · 原文：[B站专栏](https://www.bilibili.com/read/cv19333391)

## 摘要

成品：八角尖顶//generate 35 -h r=1-(y+1)^2/4;n=8;sqrt(x^2+z^2)/cos(pi/n)*cos(pi/n-((atan2(x,z)+pi)%(2*pi/n)))<r一做这种涉及正多边形的形状问题，我们首先要找到一个能画出正多边形的通式或办法，目前我能想到的和找到的有两种办法：1、一种是能够画出边是绝对平直的正多边形，这是在知乎上找到的zhuanlan.zhihu.com/p/522197221调节n的大小就会呈现n正多边形但如果直接带入到MC中，会出现x负半轴不

## 图片

![19333391 image 1](../images/articles/19333391/01.jpg)

![19333391 image 2](../images/articles/19333391/02.jpg)

![19333391 image 3](../images/articles/19333391/03.jpg)

![19333391 image 4](../images/articles/19333391/04.jpg)

![19333391 image 5](../images/articles/19333391/05.jpg)

![19333391 image 6](../images/articles/19333391/06.jpg)

![19333391 image 7](../images/articles/19333391/07.jpg)

![19333391 image 8](../images/articles/19333391/08.jpg)

![19333391 image 9](../images/articles/19333391/09.jpg)

![19333391 image 10](../images/articles/19333391/10.jpg)

![19333391 image 11](../images/articles/19333391/11.jpg)

![19333391 image 12](../images/articles/19333391/12.jpg)

![19333391 image 13](../images/articles/19333391/13.jpg)

![19333391 image 14](../images/articles/19333391/14.jpg)

![19333391 image 15](../images/articles/19333391/15.jpg)

![19333391 image 16](../images/articles/19333391/16.jpg)

![19333391 image 17](../images/articles/19333391/17.jpg)

![19333391 image 18](../images/articles/19333391/18.jpg)

![19333391 image 19](../images/articles/19333391/19.jpg)

![19333391 image 20](../images/articles/19333391/20.jpg)

![19333391 image 21](../images/articles/19333391/21.jpg)

![19333391 image 22](../images/articles/19333391/22.jpg)

![19333391 image 23](../images/articles/19333391/23.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//generate 35 -h r=1-(y+1)^2/4;n=8;sqrt(x^2+z^2)/cos(pi/n)*cos(pi/n-((atan2(x,z)+pi)%(2*pi/n)))<r
//generate 35 -h n=8;sqrt(x^2+z^2)<cos(pi/n)/cos(pi/n-(atan2(x,z)%(2*pi/n)))
//generate 35 -h n=8;sqrt(x^2+z^2)<cos(pi/n)/cos(pi/n-((atan2(x,z)+pi)%(2*pi/n)))
//generate 35 -h x^2+z^2<(0.5+0.05*sin(3*atan2(x,z)))^2
//generate 35 -h r=sqrt((1-y)/2);sqrt(x^2+z^2)/(0.8+0.05*abs(sin(10*atan2(x,z))))<r
//generate 35 -h r=1-(y+1)^2/4;sqrt(x^2+z^2)/(0.8-0.1*abs(sin(5*atan2(x,z))))<r
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
