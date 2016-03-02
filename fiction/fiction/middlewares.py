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
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from datetime import datetime, timedelta

class ProxyMiddleware(object):
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)

    def __init__(self):
        # 保存上次不用代理的时间点
        self.last_no_proxy_time = datetime.now()
        # 初始化代理池
        # self.proxyes = [{"proxy": None, "valid":True}]
        self.proxyes = []
        # 一个代理池的代理数量
        self.proxy_nums = 5
        # 获取代理池的次数
        self.times = 1
        # 代理在代理池中的位置下标,初始时使用0号代理
        self.proxy_index = 0
        # 存放代理文件
        self.proxy_file = "./china/proxyes.txt"
        # 从文件读取初始代理
        with open(self.proxy_file, "r") as fp:
            lines = fp.readlines()
            for line in lines[0:self.proxy_nums]:
                if not line:
                    continue
                line = line.split('\'')[1]
                proxy = {"proxy": "http://" + line,
                        "valid": True,}
                self.proxyes.append(proxy)
        # print self.proxyes[0]['proxy']
        # time.sleep(100)

    def process_request(self, request, spider):
        '''
        将request设置为使用代理
        '''
        # spider发现parse error， 要求更换代理，因为有些代理返回的是它自己的页面
        if 'change_proxy' in request.meta.keys() and request.meta['change_proxy']:
            self.invalid_proxy(request.meta['proxy_index'])     # 设置此代理不可用
            request.meta['change_proxy'] = False

        self.set_proxy(request)

    def process_response(self, request, response, spider):
        '''
        检查response, 根据内容切换到下一个proxy, 或者禁用proxy, 或者什么都不做
        '''
        if response.status in [500, 502, 503, 504, 520,407, 404, 403, 400, 401, 409, 301, 302]:
            self.invalid_proxy(request.meta['proxy_index'])
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        '''
        处理由于使用代理导致的连接异常
        '''
        request_proxy_index = request.meta["proxy_index"]
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            self.invalid_proxy(request_proxy_index)     # 禁用并切换代理
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

    def set_proxy(self, request):
        '''
        将request设置使用当前或下一个有效代理
        '''
        nums = self.check_valid_proxy_nums()    # 检查有效代理数量,若为0，则重置代理池和代理下标
        if nums == 0:
            self.proxy_index = 0
            self.proxyes = []
            self.fetch_valid_proxy()      # 获取有效代理
            # print self.proxyes
            # time.sleep(100)

        proxy = self.proxyes[self.proxy_index]
        if not proxy['valid']:
            self.inc_proxy_index()  # 将代理列表的索引移到下一个有效代理的位置
            proxy = self.proxyes[self.proxy_index]
        
        # if self.proxy_index == 0:   # 每次不用代理时，更新此时的时间(self.last_no_proxy_time)
            # self.last_no_proxy_time = datetime.now()

        if proxy['proxy']:
            request.meta['proxy'] = proxy['proxy']
            print  '********uesful_proxy_nums:%d********now_proxy:%s' %(nums, proxy['proxy']) 
        elif 'proxy' in request.meta.keys():    # 不用代理的时候，就删除代理
            del request.meta['proxy']

        request.meta['proxy_index'] = self.proxy_index    # 记录代理下标

    def inc_proxy_index(self):
        '''
        将代理列表的索引移到下一个有效代理的位置
        '''
        i = 0
        while i < self.proxy_nums:
            i += 1
            self.proxy_index = (self.proxy_index + 1) % self.proxy_nums
            if self.proxyes[self.proxy_index]['valid']:
                break
        if i == self.proxy_nums:    # 若循环完代理池都没有可用的，则重置代理池
            self.proxy_index = 0
            self.proxyes = []
            self.fetch_valid_proxy      # 获取有效代理

    def invalid_proxy(self, index):
        '''
        将index指向的proxy设置为invalid;
        并调整当前proxy_index到下一个有效代理的位置;
        '''
        if self.proxyes[index]['valid']:
            self.proxyes[index]['valid'] = False
            if index == self.proxy_index:
                self.inc_proxy_index()

    def check_valid_proxy_nums(self):
        '''
        检查有效代理数量
        '''
        num = 0
        for proxy in self.proxyes:
            if proxy['valid']:
                num += 1
        return num

    def fetch_valid_proxy(self):
        '''
        获取有效代理
        '''
        with open(self.proxy_file, "r") as fp:
            lines = fp.readlines()
            for line in lines[self.times*self.proxy_nums:self.proxy_nums*(self.times + 1)]:
                if not line:
                    continue
                line = line.split('\'')[1]
                proxy = {"proxy": "http://" + line,
                        "valid": True,}
                self.proxyes.append(proxy)
        self.times += 1