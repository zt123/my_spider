# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json

# class FictionPipeline(object):
#     def process_item(self, item, spider):
#         return item

class JsonWriterPipeline(object):
    '''
    输出json
    '''
    def __init__(self):
        self.file = open('./fiction/spiders/items.json', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode('unicode_escape'))
        return item