# 【Minecraft】worldedit|表达式蒙版 噪声+条纹=人造摩尔纹？

> 作者：**imhols**（UID 632698683） · 发布：2022-11-27 · 原文：[B站专栏](https://www.bilibili.com/read/cv20073301)

## 摘要

成品//re =(x+50*perlin(1,x,y,z,0.02,1,1))%10<5 251//re =x-=528;z-=-176;(sqrt(x^2+z^2)+80*perlin(1,x,y,z,0.02,1,1))%4<2 hand表达式蒙版里使用的是世界坐标，在之前的专栏里也提到过求余的操作，可以先看一下这一篇保证被除数是大于0的，我目前所选区范围内x始终是正数，就不用做调整下面我先示范一下基础的条纹制作轴向：//re =x%10<5 251求余使得沿着x方向出现条形纹理，其中10可

## 图片

![20073301 image 1](../images/articles/20073301/01.jpg)

![20073301 image 2](../images/articles/20073301/02.jpg)

![20073301 image 3](../images/articles/20073301/03.jpg)

![20073301 image 4](../images/articles/20073301/04.jpg)

![20073301 image 5](../images/articles/20073301/05.jpg)

![20073301 image 6](../images/articles/20073301/06.jpg)

![20073301 image 7](../images/articles/20073301/07.jpg)

![20073301 image 8](../images/articles/20073301/08.jpg)

![20073301 image 9](../images/articles/20073301/09.jpg)

![20073301 image 10](../images/articles/20073301/10.jpg)

![20073301 image 11](../images/articles/20073301/11.jpg)

![20073301 image 12](../images/articles/20073301/12.jpg)

![20073301 image 13](../images/articles/20073301/13.jpg)

![20073301 image 14](../images/articles/20073301/14.jpg)

![20073301 image 15](../images/articles/20073301/15.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//re =(x+50*perlin(1,x,y,z,0.02,1,1))%10<5 251
//re =x-=528;z-=-176;(sqrt(x^2+z^2)+80*perlin(1,x,y,z,0.02,1,1))%4<2 hand
//re =x%10<5 251
//re =x-=528;z-=-176;sqrt(x^2+z^2)%10<5 251
//re =(x+30*ridgedmulti(1,x,y,z,0.01,1))%4<2 251
//re =(x+80*voronoi(1,x,y,z,0.03))%10<5 251
//re =x-=528;z-=-176;(sqrt(x^2+z^2)+80*perlin(1,x,y,z,0.015,1,1))%8<4 251
//re "=x-=528;z-=-176;(sqrt(x^2+z^2)+80*perlin(1,x,y,z,0.02,1,1))%8<4 #existing" 251
//re "=x-=528;z-=-176;(sqrt(x^2+z^2)+80*perlin(1,x,y,z,0.02,1,1))%8<4 #existing" 251，
//re "=(x+80*perlin(1,x,y,z,0.02,1,1))%8<4 #existing" 251
//re "=(x+10*perlin(1,x,y,z,0.02,1,1))%8<4 #existing" 251
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
