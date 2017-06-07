# -*- coding: utf-8 -*-
import json
import os
import re

import logging
import scrapy
from lxml import etree
from scrapy.http import Request
from scrapy.selector import Selector

from news.items import NewsItem

class QqspiderSpider(scrapy.Spider):
    name = "qqspider"
    allowed_domains = ["qq.com"]
    start_urls = []
    apis = []


    def __init__(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'api/qq.json'),'r') as f:
            self.apis = json.load(f)

        # self.start_urls = [item['url'] for item in self.apis]

    def make_requests_from_url(self, item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
            'Referer': item['Referer']
        }
        return Request(item['url'], meta={'name':item['name']},headers=headers,dont_filter=True)

    def start_requests(self):
        for item in self.apis:
            baseurl = item['url']
            for i in range(1,11):
                item['url'] =  baseurl+ str(i)
                yield self.make_requests_from_url(item)
    #解析腾讯新闻的新闻列表
    def parse(self, response):
        try:
            #把获取到的数据转化为json
            jsonresponse = json.loads(response.body_as_unicode())
            try:
                info = jsonresponse['data']['article_info']
                list = Selector(text=info).xpath('//div')
                for news in list:
                    cat = news.xpath('span[@class="t-tit"]/text()').extract()[0]
                    if '图片' in cat:
                        print('跳过图片新闻')
                        continue
                    time = ''.join(news.xpath('dl/dt/span/text()').extract())
                    title = ''.join(news.xpath('dl/dt/a/text()').extract())
                    url = ''.join(news.xpath('dl/dt/a/@href').extract())
                    summary = ''.join(news.xpath('dl/dd/text()').extract())
                    item = NewsItem()
                    item['time'] = time
                    item['title'] = title
                    item['url'] = url
                    item['summary'] = summary
                    item['cata'] = response.meta['name']
                    yield scrapy.Request(url, meta={'item': item}, callback=self.parse_content)
            except TypeError:
                pass
        except:
            pass



    def parse_content(self,response):
        print(response.request)
        item = response.meta['item']
        try:
            content = response.xpath('//div[@bosszone="content"]')[0]
            item['image_urls'] = content.xpath('.//img/@src').extract()

            content_tag_p = content.xpath('./p').extract()
            item['content'] = ''.join(content_tag_p)
            item['site'] = 1
            yield item
        except IndexError as e:
            print('跳过图片新闻')




