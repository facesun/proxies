# -*-coding:utf-8 -*-

__author__ = 'Fog'
__date__ = '2019/4/28 下午4:37'


import asyncio
import aiohttp
import time

from db import RedisClient


# 目标网址
TEST_URL = 'http://www.baidu.com'
# 正确的响应码列表
TRUE_STATUS_CODE = [200]
# 同时测试一组代理的数量
BATCH_TEST_SIZE = 50


class Tester:

    def __init__(self):
        """初始化数据库管理对象"""
        self.redis = RedisClient()

    async def test_one_proxy(self, proxy):
        """对目标网站测试一个代理是否可用"""
        conn = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    # 解码为字符串
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                async with session.get(TEST_URL, proxy=real_proxy, timeout=30) as response:
                    if response.status in TRUE_STATUS_CODE:
                        # 代理可用
                        self.redis.max(proxy)
                        print(proxy, 100, '可用')
                    else:
                        # 代理不可用
                        self.redis.decrease(proxy)
                        print(proxy, -1, "状态码错误")
            except Exception as e:
                self.redis.decrease(proxy)
                print(proxy, -1, e.args)

    async def start(self):
        """启动协程， 测试所有代理"""
        try:
            proxies = self.redis.all()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [self.test_one_proxy(proxy) for proxy in test_proxies]
                await asyncio.gather(*tasks)
                time.sleep(5)
        except Exception as e:
            print('测试器发生错误', e.args)

    def run(self):
        asyncio.run(self.start())


if __name__ == '__main__':
    a = Tester()
    a.run()


