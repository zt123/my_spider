# -*- coding: utf-8 -*-
'''
@title 红袖网的幻侠小说
@author zhangt <zhang84tan@163.com>
@copyright zhangt
'''
import scrapy
from fiction.items import FictionItem

class HongXiuSpider(scrapy.Spider):
    name = 'huanxia'
    CONTENT = ''
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
        item = FictionItem()
        item['url'] = response.url
        sel = response.css('#htmlSai2014 h1 a')
        if len(sel) == 0:
            return
        else:
            item['title'] = u'《' + sel.css('::text').extract()[0] + u'》'
            # yield item
            content_url = response.css('#htmldiyizh::attr(href)').extract()[0]
            request = scrapy.Request(response.urljoin(content_url), self.parse_fiction_content)
            request.meta['item'] = item
            yield request

    def parse_fiction_content(self, response):
        '''
        小说内容
        '''
        global CONTENT
        print CONTENT
        # content = ''
        item = response.meta['item']
        # 小说内容
        text = response.css('#htmlContent > em')
        if len(text) > 1:
            p_text = text[1].css('p::text').extract()
            for p in p_text:
                content += p

        # 下一章
        next_url = response.css('.pb_cen > a::attr(href)').extract()[0]
        if next_url.find('more') > -1:
            # 判断是否是最后一张
            request = scrapy.Request(response.urljoin(next_url), self.parse_fiction_content)
            request.meta['item'] = item
            yield request
        else:
            print content
            # item['content'] = content
            # yield item
        