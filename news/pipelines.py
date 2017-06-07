# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os
import pymysql.cursors
import scrapy
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from lxml.html.clean import Cleaner
import re

class CLearDataPipeLine(object):
    def process_item(self,item,spider):
        if item['content'] == '':
            raise DropItem('抛弃图片新闻')
        cleaner = Cleaner(style=True,inline_style=True,
                          javascript=True,scripts=True,comments=True,
                          links=True,remove_unknown_tags=False,remove_tags=['a'],
                          allow_tags=['p','img','table'])
        item['content'] = cleaner.clean_html(item['content'])
        item['content'] = item['content'].replace('\n','')
        item['content'] = item['content'].replace('\r','')
        item['content'] = item['content'].replace('<p><img','<p align="center"><img')
        item['content'] = item['content'].replace('<img','<img style="width: 100%;height: auto;max-width: 100%;display: block;"')
        if '进入图片中心' in item['content']:
            raise DropItem('抛弃图片新闻')
        if item['image_urls'] is None or item['image_urls'] == []:
            return item
        for image_url in item['image_urls']:
            if not (image_url.endswith('.jpg') or image_url.endswith('.png')):
                item['content'] = re.sub('<img[\s\S]*?>','',item['content'])
                break
            split_url = image_url.split('/')[-4:]
            url = u'http://www.zzulinews.cn/static/images/{0}/{1}-{2}-{3}'.format(split_url[0], split_url[1], split_url[2], split_url[3])
            item['content'] = item['content'].replace(image_url,url)
        # item['content'] = item['content'].replace('src="', 'src="/static/images/')
        return item

class SaveImagefoPipeLine(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['image_urls']:
            if url == '':
                return item
            yield scrapy.Request(url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        file = request.url.split('/')[-4:]
        filename = u'{0}/{1}-{2}-{3}'.format(file[0], file[1], file[2],file[3])
        return filename



class SaveDataPipeLine(object):
    def __init__(self):
        self.conn = pymysql.connect(
                                    host = '127.0.0.1',
                                    user = 'root',
                                    passwd = 'panjiajia',
                                    charset = 'utf8',
                                    db = 'news',
                                    cursorclass = pymysql.cursors.DictCursor
                                        )

    def process_item(self,item,spider):
        title = item['title']
        summary = item['summary']
        time = item['time']
        category = item['cata']
        content = item['content']
        site = item['site']
        sql = 'insert into news (title,summary,timestamp,category_id,content,site_id) values (%s,%s,%s,%s,%s,%s) '
        cur = self.conn.cursor()
        cur.execute(sql,(title,summary,time,category,content,site))
        self.conn.commit()
        print('已存储',item['title'])

        return item



    def close_spider(self,spider):
        self.conn.close()