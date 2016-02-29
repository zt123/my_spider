# -*- coding: utf-8 -*-
'''
@title 红袖网的幻侠小说
@author zhangt <zhang84tan@163.com>
@copyright zhangt
'''
import scrapy
import sys
import os
import time
from fiction.items import FictionItem

class HongXiuSpider(scrapy.Spider):
    name = 'huanxia'
    content = ''
    start_urls = [
        'http://www.hongxiu.com/huanxia/'
    ]

    def parse(self, response):
        '''
        全本小说
        '''
        url = response.css('.nico_2 a::attr(href)').extract()[0]
        request = scrapy.Request(url, self.parse_fiction_list)
        yield request

    def parse_fiction_list(self, response):
        '''
        全本小说列表
        '''
        for sel in response.css('#BookList > li'):
            url = sel.css('.nrrk strong a::attr(href)').extract()[0]
            request = scrapy.Request(url, self.parse_fiction_detail)
            yield request


        # 分页
        next_li = response.css('#htmlPage > li')[-2].css('a::attr(href)')
        if len(next_li.extract()) > 0:
            next_url = response.urljoin(next_li.extract()[0])
            request = scrapy.Request(next_url, self.parse_fiction_list)
            yield request

    def parse_fiction_detail(self, response):
        '''
        小说详情
        '''
        sel = response.css('#htmlSai2014 h1 a')
        if len(sel) == 0:
            return
        else:
            text_name = u'《' + sel.css('::text').extract()[0] + u'》'
            content_url = response.css('#htmldiyizh::attr(href)').extract()[0]
            request = scrapy.Request(response.urljoin(content_url), self.parse_fiction_content)
            request.meta['text_name'] = text_name
            yield request

    def parse_fiction_content(self, response):
        '''
        小说内容
        '''
        # 小说内容
        text_1 = response.css('#htmlContent > em')
        text_2 = response.css('#htmlContent > div')
        text_3 = response.css('#htmlContent > span')
        text_4 = response.css('#htmlContent > label')
        text_5 = response.css('#htmlContent > font')
        fp = open('./fiction/txt/' + response.meta['text_name'] + '.txt', 'a')

        if len(text_1) > 1:
            p_text = text_1[1].css('p::text').extract()
            for p in p_text:
                p = p + "\n"
                fp.write(p)
        elif len(text_2) > 1:
            p_text = text_2[1].css('p::text').extract()
            for p in p_text:
                p = p + "\n"
                fp.write(p)
        elif len(text_3) > 1:
            p_text = text_3[1].css('p::text').extract()
            for p in p_text:
                p = p + "\n"
                fp.write(p)
        elif len(text_4) > 1:
            p_text = text_4[1].css('p::text').extract()
            for p in p_text:
                p = p + "\n"
                fp.write(p)
        elif len(text_5) > 1:
            p_text = text_5[1].css('p::text').extract()
            for p in p_text:
                p = p + "\n"
                fp.write(p)

        # 下一章
        if len(response.css('.pb_cen > a::attr(href)')) > 0:
            next_url = response.css('.pb_cen > a::attr(href)').extract()[0]
            if next_url.find('more') == -1:
                # 判断是否是最后一章
                request = scrapy.Request(response.urljoin(next_url), self.parse_fiction_content)
                request.meta['text_name'] = response.meta['text_name']
                yield request
            else:
                fp.close()