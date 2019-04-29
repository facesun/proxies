# -*-coding:utf-8 -*-
__author__ = 'Fog'
__date__ = '2019/4/27 下午2:09'

from bs4 import BeautifulSoup

from db import RedisClient, POOL_UPPER_THRESHLD
from utils import get_page


class ProxyMetaClass(type):
    """元类，初始化类时记录所有以crawl_开头的方法"""

    def __new__(mcs, name, bases, attrs):
        count = 0
        attrs['CrawlFunc'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['CrawlFunc'].append(k)
                count += 1
        attrs['CrawlFuncCount'] = count
        return type.__new__(mcs, name, bases, attrs)


class Crawler(metaclass=ProxyMetaClass):

    def get_proxies(self, crawl_func):
        """执行指定方法来获取代理"""
        proxies = []
        for proxy in eval("self.{}()".format(crawl_func)):
            proxies.append(proxy)
        return proxies

    def crawl_kuaidaili(self, page_count=100):
        """获取快代理网站的免费代理"""
        start_url = 'https://www.kuaidaili.com/free/inha/{}/'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            html = get_page(url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                trs = soup.find('tbody').find_all('tr')
                for tr in trs:
                    ip = tr.find_all('td')[0].string
                    port = tr.find_all('td')[1].string
                    yield ':'.join([ip, port])

    def crawl_shenji(self):
        """获取神鸡代理网站的免费代理"""
        url = 'http://www.shenjidaili.com/open/'
        html = get_page(url)
        if html:
            soup = BeautifulSoup(html, 'lxml')
            # http代理
            trs = soup.find(id='pills-stable_http').find_all('tr')
            for tr in trs[1:]:
                ip = tr.find_all('td')[0].string
                port = tr.find_all('td')[1].string
                yield ':'.join([ip, port])
            # https代理
            trs = soup.find(id='pills-stable_https').find_all('tr')
            for tr in trs[1:]:
                ip = tr.find_all('td')[0].string
                port = tr.find_all('td')[1].string
                yield ':'.join([ip, port])

    def crawl_yundaili(self, page_count=5):
        """获取云代理网站的免费代理"""
        start_url = 'http://www.ip3366.net/free/?stype=1&page={}'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            html = get_page(url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                trs = soup.find('tbody').find_all('tr')
                for tr in trs:
                    ip = tr.find_all('td')[0].string
                    port = tr.find_all('td')[1].string
                    yield ':'.join([ip, port])


class Getter:
    def __init__(self):
        """初始化数据库类和代理爬虫类"""
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """判断数据库是否已经存满"""
        if self.redis.count() >= POOL_UPPER_THRESHLD:
            return True
        return False

    def run(self):
        """开始抓取各个代理网站的免费代理存入数据库"""
        if not self.is_over_threshold():
            for i in range(self.crawler.CrawlFuncCount):
                crawl_func = self.crawler.CrawlFunc[i]
                proxies = self.crawler.get_proxies(crawl_func)
                for proxy in proxies:
                    print('获取：', proxy)
                    self.redis.add(proxy)


if __name__ == '__main__':
    a = Getter()
    a.run()
