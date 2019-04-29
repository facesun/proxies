# -*-coding:utf-8 -*-
__author__ = 'Fog'
__date__ = '2019/4/29 上午10:02'


from flask import Flask, g
import json

from db import RedisClient


app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis


@app.route('/')
def index():
    return '<h2>hello</h2>'


@app.route('/get')
def get_proxy():
    """获取随机可用代理"""
    conn = get_conn()
    try:
        proxy = conn.random()
        result = json.dumps({'status': 'success', 'proxy': proxy})
    except Exception as e:
        result = json.dumps({'status': 'failure', 'info': e})
    finally:
        return result


@app.route('/count')
def get_count():
    """获取代理总数"""
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run()
