#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@title 设置代理文件
@author zhangt <zhangt@wanthings.com>
@copyright wanthings.com
'''
import time
from twisted.web._newclient import ResponseNeverReceived, ResponseFailed
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError, TCPTimedOutError
from FieldGenerator.myssdb import myssdb
from datetime import datetime, timedelta

class ProxyMiddleware(object):
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ResponseFailed, TCPTimedOutError, ValueError)

    def __init__(self):
        # 保存上次不用代理的时间点
        self.last_no_proxy_time = datetime.now()
        # 初始化代理池
        # self.proxyes = [{"proxy": None, "valid":True}]
        self.proxyes = []
        # 一个代理池的代理数量
        self.proxy_nums = 3
        # 获取代理池的次数
        self.times = 1
        # 代理在代理池中的位置下标,初始时使用0号代理
        self.proxy_index = 0
        # 从数据库中获得可用代理,作为初始代理
        for i in range(0, self.proxy_nums):
            ip_port = self.get('proxy_http')
            proxy = {"proxy": "http://" + ip_port,
                    "valid": True}
            self.proxyes.append(proxy)

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
        # print u'地址状态:' + str(response.status) + u'当前Ip下标:' + str(request.meta['proxy_index'])
        if response.status in [502, 503, 504, 520]:
            self.invalid_proxy(request.meta['proxy_index'])
            print '++++++response+++++' + response.url + '+++++'
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        '''
        处理由于使用代理导致的连接异常
        '''
        # print u'异常:' + exception
        request_proxy_index = request.meta["proxy_index"]
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            self.invalid_proxy(request_proxy_index)     # 禁用并切换代理
            # print u'代理异常-----exception----' + request.url
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

        proxy = self.proxyes[self.proxy_index]
        if not proxy['valid']:
            self.inc_proxy_index()  # 将代理列表的索引移到下一个有效代理的位置
            proxy = self.proxyes[self.proxy_index]
        
        # if self.proxy_index == 0:   # 每次不用代理时，更新此时的时间(self.last_no_proxy_time)
            # self.last_no_proxy_time = datetime.now()

        if proxy['proxy']:
            request.meta['proxy'] = proxy['proxy']
            print  '*****request.url:%s' %(request.url)
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
            self.fetch_valid_proxy()      # 获取有效代理

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
        for i in range(0, self.proxy_nums):
            ip_port = self.get('proxy_http')
            if ip_port:
                proxy = {"proxy": "http://" + ip_port,
                        "valid": True}
                self.proxyes.append(proxy)
            else:
                # 若代理不够，则不使用代理
                self.proxyes = [{"proxy": None, "valid": True}]

    def get(self, field):
        ssdb = myssdb(table=field, host='125.65.43.196', port=54321)
        return ssdb.get()


# # import time
# import random
# import base64
# # from settings import PROXIES

# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         # 随机选取代理
#         # proxy = random.choice(PROXIES)
#         # print type(proxy)
#         # print proxy['ip_port']
#         # time.sleep(10)
#         # 设置代理
#         request.meta['proxy'] = "http://115.223.237.72:9000" 
#         print "**************ProxyMiddleware have pass************"
#         # 设置代理验证基本验证
#         # proxy_user_pass = "USERNAME:PASSWORD"
#         # encoded_user_pass = base64.encodestring(proxy_user_pass)
#         # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass