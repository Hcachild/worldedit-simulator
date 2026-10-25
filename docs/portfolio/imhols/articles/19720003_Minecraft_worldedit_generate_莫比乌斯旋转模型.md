# 【Minecraft】worldedit|generate 莫比乌斯旋转模型

> 作者：**imhols**（UID 632698683） · 发布：2022-11-12 · 原文：[B站专栏](https://www.bilibili.com/read/cv19720003)

## 摘要

成品//generate 35 a=atan2(x,z)*2;x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);data=(X<0)?(Y>0?1:2):(Y<0?3:4);(abs(X)-0.1)^2+(abs(Y)-0.1)^2<0.1^2//generate 35 a=atan2(x,z)/2;x1=sqrt(x^2+(z)^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos

## 作者补充说明

- 先讲下主要的设计思路，我们以成品的第二个图为例，把表达式拆开一步步分析
- 把x替换成X，y替换成Y,学过仿射变换的应该知道，这个来源于
- 这个直接记住就行了，xy平面内旋转就把x和y替换掉
- 接着如果我们把仿射变换里的原x再提前做个变换
- 我们把 x1=x-0.7; 改成 x1=sqrt(x^2+z^2)-0.7;这里我可能也说不清楚，大概就是让本来只与x相关改成与x，z同时相关的（也就是把本来 x轴上的点距离原点大小 改成 平面上的点与原点的距离大小），这一步就可以让这个形状形成半径为0.7的环状
- 下一步，角度a不能再是与z的值相关的了，该改成atan2(x,z)/2，范围：-pi/2~pi/2 总长：pi
- 当然这个值可以变，改成2*atan2(x,z)就是一圈转了4pi，也就是两圈
- 好，依照上面的思路，如果我们在第一步时使用的不是一个椭圆柱，而是四个圆柱相贴合
- 然后，后面的操作同理，我们想让这个环多转点，那就a=atan2(x,z)*2
- 接下来是上色部分，我们只需要分开这四个圆柱就行了，data=(X<0)?(Y>0?1:2):(Y<0?3:4);
- 这里用了嵌套，应该不用多说
- 后面接一个在x,y平面内的图形的表达式，把表达式内的x,y分别替换成X,Y

## 图片

![19720003 image 1](../images/articles/19720003/01.jpg)

![19720003 image 2](../images/articles/19720003/02.jpg)

![19720003 image 3](../images/articles/19720003/03.jpg)

![19720003 image 4](../images/articles/19720003/04.jpg)

![19720003 image 5](../images/articles/19720003/05.jpg)

![19720003 image 6](../images/articles/19720003/06.jpg)

![19720003 image 7](../images/articles/19720003/07.jpg)

![19720003 image 8](../images/articles/19720003/08.jpg)

![19720003 image 9](../images/articles/19720003/09.jpg)

![19720003 image 10](../images/articles/19720003/10.jpg)

![19720003 image 11](../images/articles/19720003/11.jpg)

![19720003 image 12](../images/articles/19720003/12.jpg)

![19720003 image 13](../images/articles/19720003/13.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//generate 35 a=atan2(x,z)*2;x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);data=(X<0)?(Y>0?1:2):(Y<0?3:4);(abs(X)-0.1)^2+(abs(Y)-0.1)^2<0.1^2
//generate 35 a=atan2(x,z)/2;x1=sqrt(x^2+(z)^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);(X)^2+15*Y^2<0.2^2
//generate 35 x^2+15*y^2<0.2^2
//generate 35 a=(1+z)*pi/2;X=x*cos(a)-y*sin(a);Y=x*sin(a)+y*cos(a);X^2+15*Y^2<0.2^2
//generate 35 a=(1+z)*pi/2;x1=x-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);X^2+15*Y^2<0.2^2
//generate 35 a=atan2(x,z)/2;x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);X^2+15*Y^2<0.2^2
//generate 35 (abs(x)-0.1)^2+(abs(y)-0.1)^2<0.1^2
//generate 35 a=atan2(x,z);x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);(abs(X)-0.1)^2+(abs(Y)-0.1)^2<0.1^2;
//generate 35 a=atan2(x,z)*2;x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);data=(X<0)?(Y>0?1:2):(Y<0?3:4);(abs(X)-0.1)^2+(abs(Y)-0.1)^2<0.1^2;
//generate 35 a=atan2(x,z)/2;x1=sqrt(x^2+z^2)-0.7;X=x1*cos(a)-y*sin(a);Y=x1*sin(a)+y*cos(a);X^10+Y^10<0.001^2;
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
