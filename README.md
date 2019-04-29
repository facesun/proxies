# proxies
> python+redis维护一个代理池，教程见[我的博客](https://blog.csdn.net/zzh2910/article/details/89608496)


### 开发环境
- python 3.7.1
- redis 4.0.9

### 用到的第三方库
- redis
- requests
- beautifulsoup4
- aiohttp
- flask

### 如何使用
搭建好环境之后，进入项目目录， ```python run.py``` 即可，通过 **http://127.0.0.1:5000/get** 获得随机可用代理，也可以放到服务器运行，需在api.py中打开外网访问。
