# 【Minecraft】worldedit|generate 深入解析gmegabuf()缓冲函数——从原理到应用

> 作者：**imhols**（UID 632698683） · 发布：2023-08-07 · 原文：[B站专栏](https://www.bilibili.com/read/cv25579754)

## 摘要

一、格式和用法https://worldedit.enginehub.org/en/latest/usage/other/expressions/（megabuf有全局的gmegabuf和本地的megabuf，为了方便，下文只写gmegabuf）看wiki翻译不难理解，gmegabuf本质上是一个数组，数组默认为0；提供了三个函数 1.1、gmegabuf()先讲这两个gmegabuf(索引值)：调用数组对应索引值处的值，后期调用使用gmegabuf(索引值,值)：把“值”存进数组对应索引值的位置，前期赋

## 作者补充说明

- 先在数组索引为0的位置赋值2*random()-1
- 再调用数组索引为0处的值
- 颜色表（仅供参考）
- gmegabuf(索引值)：调用数组对应索引值处的值，后期调用使用
- gmegabuf(索引值,值)：把“值”存进数组对应索引值的位置，前期赋值使用
- 首先介绍另一个指令：//calc 表达式，这个指令能计算输出表达式的值，单纯运行表达式而不进行生成操作，比如
- 或者默认gmegabuf(0)是0，所以
- 先在gmegabuf里存入设定好的值，用第二个函数 (g)megabuf(index, value)
- 我们分两次输入，因为带个g，是全局缓冲器，只要不重进游戏就不会自动清零，这就体现了缓冲器gmegabuf的强大之处，本来很长的指令可以分开，一条指令先给缓冲器数组赋值，另一条用来调用，调用内容包括索引和对应的值，比如
- random()返回的是个0~1的数，所以2*random()-1在-1~1之间，与在一个选区里用generate调用random()不同，generate它会在每个坐标处都运行一次你写的指令，即每个位置都会独立运行一次获取随机数的函数random()，使得整个选区内的每个位置得到的随机值并不统一，而事先用//calc在gmegabuf内存入随机数，就能让随机数确定下来，然后在//generate中用gmegabuf(索引)代替random()，让每个坐标处的调用的随机数都是这个数组gmegabuf的内容，是同一个，所以用gmegabuf相关函数能在一些需要固定的随机数的情况下很好用，就比如预先设置圆的随机半径等随机变量或者点的随机坐标（三个一组，xyz）
- 如果有fawe的话，里面有个//br scmd 散点执行命令的笔刷，具体看wiki
- （指令不缩进是为了方便复制）
- 我这里先限定了圆柱的最大和最小半径和最大最小高度，然后用/calc 存入到gmegabuf里，然后再在后面的generate里用gmegabuf(index)调出之前的已经确定的随机数，然后只需一点就能生成高度和半径的随机的圆柱了（另外里面夹的选区命令也要随最大半径和高度改变）
- 也可以简单的改造成一个随机球形的笔刷：
- 比如有一系列已经赋完值的gmegabuf，选好选区，使用generate，其中有一句i=gclosest(x,y,z,0,100,3)，意思就是，带入选区内的一点的xyz，然后从gmegabuf索引0开始3个为一组来与xyz一一比较，比较次数上限100次，先是0，1，2一组，然后是3，4，5一组……到最后是索引为297，298，299的一组gmegabuf与xyz的值进行比较，然后确定最接近xyz的那一组（三个），把这一组的第一个gmegabuf的索引值返回
- 我个人猜想，里面的计算逻辑是找到(gmegabuf(i)-x)^2+(gmegabuf(i+1)-y)^2+(gmegabuf(i+2)-z)^2的最小值所对应的索引值 i，事实证明确实是这样的，假如步长是4会是怎么样，我测试的好像是前三个正常与xyz计算，第4个不参与与xyz的计算。如果是2？算了，不想这么多了，主要以3为主
- 变相地实现了参数方程形式的表达式，用一个适当的步长，画出足够的近乎连续的点
- 首先先了解一下voronoi图，这个网站动图解释的很形象
- 第一步，我们需要一些随机的点的坐标，下面就称作样点
- 一般我们赋值顺序都是 x y z，先gmegabuf(i,2*random()-1)存为x坐标，接着gmegabuf(i+1,0)存为y坐标，赋值为0是因为下面介绍都是xz平面内的图案，用不到y，其实不写也行，反正默认就是0，最后是z，gmegabuf(i+2,2*random()-1)，跟x一样，范围在-1~1是为了在generate里方便使用
- 我们需要的是大量的xz坐标在-1~1间的点，一个个赋值不现实，我们需要用到for循环，但是在we表达式中，单个循环最大上限是256次，所以我们需要嵌套循环，实现最多256x256=65536次循环，当然如果继续嵌套还能更多
- for循环函数的用法wiki有，不赘述
- 这里是3个为一组用来分别作为一个点的xyz坐标，总共有n=1000个点，但索引k已经到了3000了
- 最后加个1是为了让它成功运行，因为需要返回一个值，不然可能会报错
- 选一块选区，generate，使用gclosest函数找到与选区里每个位置方块最接近的那一组gmegabuf存的坐标，返回这组的第一个的索引值作为data用于区分颜色，呈现效果
- data=i/3%16;1 ，i/3是因为索引值i是3个为一组（i，i+1，i+2），实际上不除也能区分各个区域，但它们是3的倍数，当%15时少颜色
- 我们用gclosest()得到了选区里每个位置坐标相距最近的样点的索引值 i ，也就同时得到了样点的坐标，只需要用第一个介绍的函数gmegabuf(i)、gmegabuf(i+2)调用出样点的xz坐标，从而实现一些更有趣的效果
- 我们先获取了样点的xz坐标，用大写XZ来区分，进而计算了选区每个位置和与它最近样点的距离r=sqrt((x-X)^2+(z-Z)^2);然后扩大60倍能与16取余当作data的值，就的得到了这一个渐变的图案，然后换上黑白渐变的材质
- 这里推荐eztaK和Zeranny想到的快速替换材质的办法
- 他并没有解释原理只讲了用法，我简单解释一下，先用queryAbs获取每个位置的方块type和data，然后让非目标type的方块不操作，return 0，如果是该type的方块让它的xyz全都指向同一世界颜色表的起始位置，然后让x或z根据前面检测的data的数值向x或z方向移动对应数值，就实现了按照data的值去上色的效果，具体点说，白色混凝土的data是0所以d=0，z+=0，所以就被替换成了第一个的方块（z=-97），橙色混凝土data是1，d=1，z+=1，所以被替换成了第二个方块（z=-96）其他同理

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
