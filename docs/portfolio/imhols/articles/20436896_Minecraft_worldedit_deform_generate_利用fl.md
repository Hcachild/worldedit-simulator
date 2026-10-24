# 【Minecraft】worldedit|deform&generate 利用floor函数实现“二次体素化”

> 作者：**imhols**（UID 632698683） · 发布：2022-12-12 · 原文：[B站专栏](https://www.bilibili.com/read/cv20436896)

## 摘要

成品//deform -c x=3*floor(x/3);z=3*floor(z/3);y=3*floor(y/3)//generate -c 251 X=3*floor(x/3);Z=3*floor(z/3);y+60<40*perlin(1,x,1,z,0.03,1,1)//generate -c 251 Y=2*floor(y/2);Y+60<40*perlin(1,x,1,z,0.03,1,1)想必也注意到了 ，这里只是用了新的X，Y，Z替换了本来的x，y，zX=a*floor(x/b)

## 图片

![20436896 image 1](../images/articles/20436896/01.jpg)

![20436896 image 2](../images/articles/20436896/02.jpg)

![20436896 image 3](../images/articles/20436896/03.jpg)

![20436896 image 4](../images/articles/20436896/04.jpg)

![20436896 image 5](../images/articles/20436896/05.jpg)

![20436896 image 6](../images/articles/20436896/06.jpg)

![20436896 image 7](../images/articles/20436896/07.jpg)

![20436896 image 8](../images/articles/20436896/08.jpg)

![20436896 image 9](../images/articles/20436896/09.jpg)

![20436896 image 10](../images/articles/20436896/10.jpg)

![20436896 image 11](../images/articles/20436896/11.jpg)

![20436896 image 12](../images/articles/20436896/12.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//deform -c x=3*floor(x/3);z=3*floor(z/3);y=3*floor(y/3)
//generate -c 251 X=3*floor(x/3);Z=3*floor(z/3);y+60<40*perlin(1,x,1,z,0.03,1,1)
//generate -c 251 Y=2*floor(y/2);Y+60<40*perlin(1,x,1,z,0.03,1,1)
//deform -c y=3*floor(y/3)
//deform -c x=3*floor(x/3)
//deform -c x=3*floor(x/3);z=3*floor(z/3)
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
