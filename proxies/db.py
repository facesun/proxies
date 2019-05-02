# -*-coding:utf-8 -*-
__author__ = 'Fog'
__date__ = '2019/4/27 下午1:35'


import redis
from random import choice

# 分数设置
MAX_SCORE = 100
MIN_SCORE = 0
INIT_SCORE = 10

# 连接信息
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies'

# 数据库最大存储的代理数量
POOL_UPPER_THRESHLD = 10000


class RedisClient:

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, passwd=REDIS_PASSWORD):
        """初始化redis对象"""
        self.db = redis.StrictRedis(host=host, port=port, password=passwd, decode_responses=True)

    def add(self, proxy, score=INIT_SCORE):
        """添加一个代理，设置初始分数"""
        if not self.db.zscore(REDIS_KEY, proxy):
            self.db.zadd(REDIS_KEY, {proxy: score})

    def random(self):
        """首先随机获取最高分的有效代理，不存在则按排名获取"""
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            # 从分数前50的代理中随机获取一个
            result = self.db.zrevrange(REDIS_KEY, 0, 50)
            if len(result):
                return choice(result)
            else:
                raise Exception('无可用代理')

    def decrease(self, proxy):
        """代理分数-1，小于指定阈值则删除"""
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            return self.db.zincrby(REDIS_KEY, -1, proxy)
        else:
            return self.db.zrem(REDIS_KEY, proxy)

    def max(self, proxy):
        """更新代理分数到最大值"""
        return self.db.zadd(REDIS_KEY, {proxy: MAX_SCORE})

    def count(self):
        """获取代理数量"""
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """获取全部代理"""
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
