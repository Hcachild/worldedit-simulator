# 【Minecraft】worldedit|generate洋葱顶进阶及上色办法|包含data/type、atan2、min

> 作者：**imhols**（UID 632698683） · 发布：2022-10-25 · 原文：[B站专栏](https://www.bilibili.com/read/cv19312092)

## 摘要

成品如下//generate 35 G=min(sin(18*atan2(x,z)+20*(y+1)),sin(18*atan2(x,z)-20*(y+1)));data=(G>(-0.7))?4:13;i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)+0.02*G之前在视频里演示的不是很详细，这次将其进行了改进一第一步就是先有个大致的轮廓，上个专栏也提过，视频里也有演示，就先跳过这一步了//generate 35 i=sqrt

## 图片

![19312092 image 1](../images/articles/19312092/01.jpg)

![19312092 image 2](../images/articles/19312092/02.jpg)

![19312092 image 3](../images/articles/19312092/03.jpg)

![19312092 image 4](../images/articles/19312092/04.jpg)

![19312092 image 5](../images/articles/19312092/05.jpg)

![19312092 image 6](../images/articles/19312092/06.jpg)

![19312092 image 7](../images/articles/19312092/07.jpg)

![19312092 image 8](../images/articles/19312092/08.jpg)

![19312092 image 9](../images/articles/19312092/09.jpg)

![19312092 image 10](../images/articles/19312092/10.jpg)

![19312092 image 11](../images/articles/19312092/11.jpg)

![19312092 image 12](../images/articles/19312092/12.jpg)

![19312092 image 13](../images/articles/19312092/13.jpg)

![19312092 image 14](../images/articles/19312092/14.jpg)

![19312092 image 15](../images/articles/19312092/15.jpg)

![19312092 image 16](../images/articles/19312092/16.jpg)

![19312092 image 17](../images/articles/19312092/17.jpg)

![19312092 image 18](../images/articles/19312092/18.jpg)

![19312092 image 19](../images/articles/19312092/19.jpg)

![19312092 image 20](../images/articles/19312092/20.jpg)

![19312092 image 21](../images/articles/19312092/21.jpg)

![19312092 image 22](../images/articles/19312092/22.jpg)

![19312092 image 23](../images/articles/19312092/23.jpg)

![19312092 image 24](../images/articles/19312092/24.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//generate 35 G=min(sin(18*atan2(x,z)+20*(y+1)),sin(18*atan2(x,z)-20*(y+1)));data=(G>(-0.7))?4:13;i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)+0.02*G
//generate 35 i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)
//generate 35 G=sin(18*atan2(x,z));i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)+0.05*G
//generate 35 G=sin(18*atan2(x,z)+10*(y+1));i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)+0.05*G
//generate 35 data=1 y>0
//generate 35 G=sin(18*atan2(x,z)+10*(y+1));data=(G>-0.6?4:13)i=sqrt(x^2+z^2);k=0.9;a=6.5;b=0.9;m=0.6;i<k*a^(-b*(y+m)^2)+0.05*G
//generate 35 data=(y>0?4:13) min(0.2*sin(10*x),0.2*sin(10*z))>y
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
