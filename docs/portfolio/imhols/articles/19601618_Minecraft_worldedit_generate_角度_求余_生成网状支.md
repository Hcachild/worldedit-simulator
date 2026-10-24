# 【Minecraft】worldedit|generate 角度+求余=生成网状支撑结构？

> 作者：**imhols**（UID 632698683） · 发布：2022-11-08 · 原文：[B站专栏](https://www.bilibili.com/read/cv19601618)

## 摘要

成品//generate 35 -h A=(atan2(x,z)+pi)/pi;type=((((A+(1+y))*40)%8<1)||(((A+(1-y))*40)%8<1))?35:95;x^2+z^2<0.5^2求余很好理解，就是一个除数一个被除数，求出余数，比如5%3=2，如果放入到we中，可以用在判断语句中，比如在表达式蒙版中，如果要做出相隔a距离（这里指的是空白区域）的且有b宽度的格栅的图案就可以用 //re =x%(a+b)<b 1 来实现，如图//re =(-x)%10<2 1还

## 图片

![19601618 image 1](../images/articles/19601618/01.jpg)

![19601618 image 2](../images/articles/19601618/02.jpg)

![19601618 image 3](../images/articles/19601618/03.jpg)

![19601618 image 4](../images/articles/19601618/04.jpg)

![19601618 image 5](../images/articles/19601618/05.jpg)

![19601618 image 6](../images/articles/19601618/06.jpg)

![19601618 image 7](../images/articles/19601618/07.jpg)

![19601618 image 8](../images/articles/19601618/08.jpg)

![19601618 image 9](../images/articles/19601618/09.jpg)

![19601618 image 10](../images/articles/19601618/10.jpg)

![19601618 image 11](../images/articles/19601618/11.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//generate 35 -h A=(atan2(x,z)+pi)/pi;type=((((A+(1+y))*40)%8<1)||(((A+(1-y))*40)%8<1))?35:95;x^2+z^2<0.5^2
//re =(-x)%10<2 1
//generate 35 type=( (((atan2(x,z)+pi)/pi)*40)%5<2 )?35:95 x^2+z^2<0.5^2
//generate 35 -h A=(atan2(x,z)+pi)/pi;type=(((A+(1+y))*40)%8<2)?35:0;x^2+z^2+y^2<1
//generate 35 -h A=(atan2(x,z)+pi)/pi;type=((((A+(1+y))*40)%8<1)||(((A+(1-y))*40)%8<1))?35:95;z/=sqrt((1.8-y)/2);x/=sqrt((1.8-y)/2);rotate(x,z,-(1+y)*pi/3);x^2+z^2<(0.5+0.13*cos(3/2*atan2(x,z))^4)^2
//re =x%(a+b)<b 1 来实现，如图
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
