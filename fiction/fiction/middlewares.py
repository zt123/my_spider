# -*- coding: utf-8 -*-
'''
设置代理文件
'''
import random
import base64
from settings import PROXIES

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        # 随机选取代理
        proxy = random.choice(PROXIES)
        # 设置代理
        request.meta['proxy'] = "http://%s" %(proxy['ip_port'])
        print "**************ProxyMiddleware have pass************" + proxy['ip_port']
        # 设置代理验证基本验证
        # proxy_user_pass = "USERNAME:PASSWORD"
        # encoded_user_pass = base64.encodestring(proxy_user_pass)
        # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass