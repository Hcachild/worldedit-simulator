# 【Minecraft】worldedit|generate 深入解析gmegabuf()缓冲函数——从原理到应用

> 作者：**imhols**（UID 632698683） · 发布：2023-08-07 · 原文：[B站专栏](https://www.bilibili.com/read/cv25579754)

## 摘要

一、格式和用法https://worldedit.enginehub.org/en/latest/usage/other/expressions/（megabuf有全局的gmegabuf和本地的megabuf，为了方便，下文只写gmegabuf）看wiki翻译不难理解，gmegabuf本质上是一个数组，数组默认为0；提供了三个函数 1.1、gmegabuf()先讲这两个gmegabuf(索引值)：调用数组对应索引值处的值，后期调用使用gmegabuf(索引值,值)：把“值”存进数组对应索引值的位置，前期赋

## 图片

![25579754 image 1](../images/articles/25579754/01.jpg)

![25579754 image 2](../images/articles/25579754/02.jpg)

![25579754 image 3](../images/articles/25579754/03.jpg)

![25579754 image 4](../images/articles/25579754/04.jpg)

![25579754 image 5](../images/articles/25579754/05.jpg)

![25579754 image 6](../images/articles/25579754/06.jpg)

![25579754 image 7](../images/articles/25579754/07.jpg)

![25579754 image 8](../images/articles/25579754/08.jpg)

![25579754 image 9](../images/articles/25579754/09.jpg)

![25579754 image 10](../images/articles/25579754/10.jpg)

![25579754 image 11](../images/articles/25579754/11.jpg)

![25579754 image 12](../images/articles/25579754/12.jpg)

![25579754 image 13](../images/articles/25579754/13.jpg)

![25579754 image 14](../images/articles/25579754/14.jpg)

![25579754 image 15](../images/articles/25579754/15.jpg)

![25579754 image 16](../images/articles/25579754/16.jpg)

![25579754 image 17](../images/articles/25579754/17.jpg)

![25579754 image 18](../images/articles/25579754/18.jpg)

![25579754 image 19](../images/articles/25579754/19.jpg)

![25579754 image 20](../images/articles/25579754/20.jpg)

![25579754 image 21](../images/articles/25579754/21.jpg)

![25579754 image 22](../images/articles/25579754/22.jpg)

![25579754 image 23](../images/articles/25579754/23.jpg)

![25579754 image 24](../images/articles/25579754/24.jpg)

![25579754 image 25](../images/articles/25579754/25.jpg)

![25579754 image 26](../images/articles/25579754/26.jpg)

![25579754 image 27](../images/articles/25579754/27.jpg)

![25579754 image 28](../images/articles/25579754/28.jpg)

![25579754 image 29](../images/articles/25579754/29.jpg)

![25579754 image 30](../images/articles/25579754/30.jpg)

![25579754 image 31](../images/articles/25579754/31.jpg)

![25579754 image 32](../images/articles/25579754/32.jpg)

![25579754 image 33](../images/articles/25579754/33.jpg)

![25579754 image 34](../images/articles/25579754/34.jpg)

![25579754 image 35](../images/articles/25579754/35.jpg)

![25579754 image 36](../images/articles/25579754/36.jpg)

![25579754 image 37](../images/articles/25579754/37.jpg)

![25579754 image 38](../images/articles/25579754/38.jpg)

![25579754 image 39](../images/articles/25579754/39.jpg)

![25579754 image 40](../images/articles/25579754/40.jpg)

![25579754 image 41](../images/articles/25579754/41.jpg)

![25579754 image 42](../images/articles/25579754/42.jpg)

![25579754 image 43](../images/articles/25579754/43.jpg)

![25579754 image 44](../images/articles/25579754/44.jpg)

![25579754 image 45](../images/articles/25579754/45.jpg)

![25579754 image 46](../images/articles/25579754/46.jpg)

![25579754 image 47](../images/articles/25579754/47.jpg)

![25579754 image 48](../images/articles/25579754/49.jpg)

![25579754 image 49](../images/articles/25579754/50.jpg)

![25579754 image 50](../images/articles/25579754/51.jpg)

![25579754 image 51](../images/articles/25579754/52.jpg)

![25579754 image 52](../images/articles/25579754/53.jpg)

![25579754 image 53](../images/articles/25579754/54.jpg)

![25579754 image 54](../images/articles/25579754/55.jpg)

![25579754 image 55](../images/articles/25579754/56.jpg)

![25579754 image 56](../images/articles/25579754/57.jpg)

![25579754 image 57](../images/articles/25579754/58.jpg)

![25579754 image 58](../images/articles/25579754/59.jpg)

![25579754 image 59](../images/articles/25579754/60.jpg)

![25579754 image 60](../images/articles/25579754/61.jpg)

## 指令摘录

> 从原文正文/代码块中提取，可能包含作者当时的版本差异；先在测试选区运行。

```text
//calc
//generate 251 n=100;d=0.01;i=gclosest(x,y,z,0,n,3)for(u=-1,1)for(v=-1,1)for(w=-1,1){I=gclosest(x+d*u,y+d*v,z+d*w,0,n,3)if(I!=i){return 0}}1
//generate 251 n=150;d=0.1*(max(sqrt(x^2+z^2)-0.5,0));i=gclosest(x,y,z,0,n,3)for(u=-1,1)for(v=-1,1)for(w=-1,1){I=gclosest(x+d*u,y+d*v,z+d*w,0,n,3)if(I!=i){return 0}}1
//generate 251 n=150;d=0.1*(max(1-sqrt(x^2+z^2),0));i=gclosest(x,y,z,0,n,3)for(u=-1,1)for(v=-1,1)for(w=-1,1){I=gclosest(x+d*u,y+d*v,z+d*w,0,n,3)if(I!=i){return 0}}1
//generate 251 n=200;d=0.08*(max(1-max(abs(x),abs(z)),0));i=gclosest(x,y,z,0,n,3)for(u=-1,1)for(v=-1,1)for(w=-1,1){I=gclosest(x+d*u,y+d*v,z+d*w,0,n,3)if(I!=i){return 0}}1
//generate 251 s=1;f=3;d=0.01;i=voronoi(s,x,y,z,f)for(u=-1,1)for(v=-1,1)for(w=-1,1){I=voronoi(s,x+d*u,y+d*v,z+d*w,f);if(I!=i){return 0}}data=i*16%16;1
//g 251 n=100;a=0;i=gclosest(x,y,z,0,n,3);for(d=0;a==0;d+=.005){for(u=-1,1)for(w=-1,1){I=gclosest(x+d*u,y,z+d*w,0,n,3)a+=(I!=i)}}d>0.02
//g 251 n=200;a=0;i=gclosest(x,y,z,0,n,3);for(d=0;a==0;d+=.005){for(u=-1,1)for(w=-1,1){I=gclosest(x+d*u,y,z+d*w,0,n,3)a+=(I!=i)}}data=i/3%16;d>0.1*(1-sqrt(x^2+z^2))
//generate 251 n=100;r=9;I=0;for(i=0,255)for(j=0;j<255*3;j+=3){k=i*255+j;if(k>n*3)break;X=x-gmegabuf(k)Z=z-gmegabuf(k+2);if((R=abs(X)+abs(Z))<r){r=R;I=k}}data=I%16;1
//g 251:1 s=1;f=5;d=0do{d+=0.005;A=voronoi(s,x+d,1,z,f)B=voronoi(s,x-d,1,z,f)C=voronoi(s,x,1,z+d,f)D=voronoi(s,x,1,z-d,f)}while((A==B)+(B==C)+(C==D)+(A==C)+(A==D)+(B==D)!=1);data=d*50
//generate 251 n=100;l=gclosest(x,y,z,0,n,3);I=0;for(i=0,255)for(j=0;j<255*3;j+=3){k=i*255+j;if(k>n*3)break;if(k==l)continue;a=(x-gmegabuf(I));b=(z-gmegabuf(I+2));I=(((x-gmegabuf(k))^2+(z-gmegabuf(k+2))^2)<a^2+b^2)?k:I;}data=I/3%16+.1
//g 251 n=100;a=0;i=gclosest(x,y,z,0,n,3);for(d=0;a==0;d+=.005){for(u=-1,1)for(w=-1,1){I=gclosest(x+d*u,y,z+d*w,0,n,3)a+=(I!=i)}}r=sqrt((x-gmegabuf(i))^2+(z-gmegabuf(i+2))^2);data=i/3%16;d>max(.01,.8*(r-.1))
//g 251 n=200;i=gclosest(x,y,z,0,n,3);X=gmegabuf(i);Z=gmegabuf(i+2)r=1;for(l=0,255)for(k=0;k<255*3;k+=3){if((j=l*255+k)>n*3)break;if(j==i)continue;r=min(sqrt((gmegabuf(j)-X)^2+(gmegabuf(j+2)-Z)^2),r)}data=i/3%16;(x-X)^2+(z-Z)^2<(r/2)^2;
```

---

图片与正文版权归 **imhols** 所有；本页只做学习索引，原文链接见上。
