# -*- coding: utf-8 -*-
'''
设置代理文件
'''
# # import time
# import random
# import base64
# from settings import PROXIES

# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         # 随机选取代理
#         proxy = random.choice(PROXIES)
#         # print type(proxy)
#         # print proxy['ip_port']
#         # time.sleep(10)
#         # 设置代理
#         request.meta['proxy'] = "http://%s" %(proxy['ip_port'])
#         print "**************ProxyMiddleware have pass************" + proxy['ip_port']
#         # 设置代理验证基本验证
#         # proxy_user_pass = "USERNAME:PASSWORD"
#         # encoded_user_pass = base64.encodestring(proxy_user_pass)
#         # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass

import time
# import logging
from datetime import datetime, timedelta

class ProxyMiddleware(object):

    def __init__(self):
        # 保存上次不用代理的时间点
        self.last_no_proxy_time = datetime.now()
        # 初始化代理池
        self.proxyes = [{"proxy": None, "valid":True, "count": 0}]
        # 一个代理池的代理数量
        self.proxy_nums = 20
        # 代理在文件中的位置下标,初始时使用0号代理(即不使用代理)
        self.proxy_index = 0
        # 存放代理文件
        self.proxy_file = "./fiction/proxyes.txt"
        # 从文件读取初始代理
        with open(self.proxy_file, "r") as fp:
            lines = fp.readlines()
            for line in lines[0:self.proxy_nums]:
                if not line:
                    continue
                line = line.split('\'')[1]
                proxy = {"proxy": "http://" + line,
                        "valid": True,
                        "count": 0,}
                self.proxyes.append(proxy)

    def process_request(self, request, spider):
        '''
        将request设置为使用代理
        '''
        self.set_proxy(request)

    def set_proxy(self, request):
        '''
        将request设置使用当前或下一个有效代理
        '''
        proxy = self.proxyes[self.proxy_index]
        if not proxy['valid']:
            # 将代理列表的索引移到下一个有效代理的位置
        
        if self.proxy_index == 0:   # 每次不用代理时，更新此时的时间(self.last_no_proxy_time)
            self.last_no_proxy_time = datetime.now()
