# 【Minecraft】worldedit|generate 探索神奇的噪声——从原理到应用

> 作者：**imhols**（UID 632698683） · 发布：2023-03-15 · 原文：[B站专栏](https://www.bilibili.com/read/cv22408344)

## 摘要

本专栏教程旨在为mc玩家打开一扇新的大门，看完让你掌握噪声的原理和基础运用一、详解原理1.1格式https://worldedit.enginehub.org/en/latest/usage/other/expressions/我们现在先只拿perlin噪声作为例子，其中各个参数概念这里不做过多介绍，这里推荐蓝鸡的视频介绍1.2函数概念在我们写表达式时，we给我们提供了很多的函数，形式如 “函数名()”，比如常用的sqrt()、abs()、atan2()、min()、max()等等,你在括号中输入进参数，

## 图片

![22408344 image 1](../images/articles/22408344/01.jpg)

![22408344 image 2](../images/articles/22408344/02.jpg)

![22408344 image 3](../images/articles/22408344/03.jpg)

![22408344 image 4](../images/articles/22408344/05.jpg)

![22408344 image 5](../images/articles/22408344/06.jpg)

![22408344 image 6](../images/articles/22408344/07.jpg)

![22408344 image 7](../images/articles/22408344/08.jpg)

![22408344 image 8](../images/articles/22408344/09.jpg)

![22408344 image 9](../images/articles/22408344/10.jpg)

![22408344 image 10](../images/articles/22408344/11.jpg)

![22408344 image 11](../images/articles/22408344/12.jpg)

![22408344 image 12](../images/articles/22408344/13.jpg)

![22408344 image 13](../images/articles/22408344/14.jpg)

![22408344 image 14](../images/articles/22408344/15.jpg)

![22408344 image 15](../images/articles/22408344/16.jpg)

![22408344 image 16](../images/articles/22408344/17.jpg)

![22408344 image 17](../images/articles/22408344/18.jpg)

![22408344 image 18](../images/articles/22408344/19.jpg)

![22408344 image 19](../images/articles/22408344/20.jpg)

![22408344 image 20](../images/articles/22408344/21.jpg)

![22408344 image 21](../images/articles/22408344/22.jpg)

![22408344 image 22](../images/articles/22408344/23.jpg)

![22408344 image 23](../images/articles/22408344/24.jpg)

![22408344 image 24](../images/articles/22408344/25.jpg)

![22408344 image 25](../images/articles/22408344/26.jpg)

![22408344 image 26](../images/articles/22408344/27.jpg)

![22408344 image 27](../images/articles/22408344/28.jpg)

![22408344 image 28](../images/articles/22408344/29.jpg)

![22408344 image 29](../images/articles/22408344/30.jpg)

![22408344 image 30](../images/articles/22408344/31.jpg)

![22408344 image 31](../images/articles/22408344/32.jpg)

![22408344 image 32](../images/articles/22408344/33.jpg)

![22408344 image 33](../images/articles/22408344/34.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//generate 251 perlin(0,x,y,z,1,1,1)<0.5
//generate 251 perlin(1,x,y,z,1,1,1)
//generate 251 perlin(1,x,y,z,1,1,1)<0.5
//generate 251 perlin(1,x,1,z,1,1,1)<0.5
//generate 251 perlin(1,x,1,1,5,1,1)<0.5
//generate 251 y+1<perlin(1,x,1,z,1,1,1)
//generate 251 -c floor(y/3)*3+25<25*perlin(1,x,1,z,0.05,1,1)
//generate 251 perlin(1,x,y,z,5,1,1)<0.5
//generate 251 perlin(1,x,y,z/10,5,1,1)<0.5
//generate 251 perlin(1,x,y,z*5,5,1,1)<0.5
//generate 251 perlin(1,x*2,y,z/20,10,2,1)<0.3
//generate 251 perlin(1,x,3*sqrt(x^2+z^2),z,10,1,1)<0.5
//generate 251 perlin(1,1,3*sqrt(x^2+z^2),1,10,1,1)<0.5
//generate 251 perlin(1,1,3*max(abs(x),abs(z)),1,10,1,1)<0.5
//generate 251 p=perlin(1,x,20*(abs(x)+abs(z)),z,1,1,1);data=p*10%4;p<0.4
//generate 251 perlin(1,1,atan2(x,z),1,5,1,1)<0.4
//generate 251 rotate(x,z,2*y);p=perlin(1,x,3*sqrt(x^2+z^2),z,3,1,1);data=p*5%5;y+1<p*(1/(1+e^(5*(sqrt(x^2+z^2)-0.5))))
//generate 251 y+1<1/(1+e^(5*(sqrt(x^2+z^2)-0.5)))
//generate 251 p1=perlin(1,x,1,z,1,1,1);p2=perlin(2,x,1,z,3,1,1);y+1<p1*p2
//generate 251 y+1<2*perlin(23,x*2,1,z,3,1,1)*(perlin(2,x,1,z,2,1,1)-0.2)*(1-sqrt(x^2+z^2)^8)
//deform -c x=3*floor(x/3);
//generate 251 -c s=200;x+=s;z+=s;a=15;b=20;d=1;k=2;p=k*perlin(1,x,y,z,0.05,1,1);f=d+p;(x%(2*a)<a?(z%b<f||z%b>(b-f)):((z+b/2)%(2*b)<f||(z+b/2)%(2*b)>(2*b-f)))||(x%a<f||x%a>(a-f))
//generate 35 rotate(x,z,pi/4);m=0.6;n=0.4;p1=perlin(1,x,50*sqrt(x^2+z^2),z,2.5,1,1);p2=perlin(1,x,20*sqrt(x^2+z^2),z,1.5,1,1);rotate(x,z,p2/10);t=atan2(z,x)/pi+1;data=(t*p1+p1*0.2)*5%15+5;abs((sqrt(x^2+z^2)-(m+n/2)))<(n/2)&&(p1-t/2)
//generate 251 p=perlin(1,x,1,z,5,1,1);L=(p+1)/2-sqrt(x^2+z^2);1-y^2<2*p*L
//generate 251 p2=perlin(1,x,y,z,1,1,1);p1=perlin(1,x,y*8+p2*5,z,3,1,1);data=p1*4%4;x^2+z^2+y^2<0.85+0.15*p1
//generate 1 p=perlin(1,x,1,z,2*e^(1-0.5*z),1,1);y+0.9<p*8*((x+0.2*(p-0.5))^2-(x+0.2*(p-0.5))^4+0.01*(z+1))*e^(z-1)
//g 251 -c rotate(x,z,y/80+pi/3)rotate(z,y,-pi/3)rotate(z,y,.8*perlin(9,x,y,z,.02,1,1))rotate(x,z,perlin(66,x,y,z,.015,1,1)*4)z/=max((1-e^(5*(abs(y)/110-1))),0)f=(3*sin(.2*y+2*perlin(2,x,y,z,.05,1,1))+10)^2;data=f>(z*5)^2?1:f>(z*1.5)^2?3:0;f-z^2-(6*x)^2>0
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
