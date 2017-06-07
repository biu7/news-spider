# -*- coding: utf-8 -*-
import json
import os

import scrapy
from scrapy import Request
from ..items import NewsItem

class HqspiderSpider(scrapy.Spider):
    name = "hqspider"
    allowed_domains = ["huanqiu.com"]
    start_urls = []
    apis = []

    def __init__(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'api/hq.json'),'r') as f:
            self.apis = json.load(f)

    def make_requests_from_url(self, item):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
        }
        return Request(item['url'], meta={'name':item['name']},headers=headers,dont_filter=True)

    def start_requests(self):
        for item in self.apis:
            baseurl = item['url']
            for i in range(1,11):
                if i == 1:
                    item['url'] = baseurl + '.html'
                else:
                    item['url'] = baseurl + '_' + str(i) + '.html'
                yield self.make_requests_from_url(item)


    def parse(self, response):
        content = response.xpath('//ul[@class="iconBoxT14"]/li')
        for item in content:
            news_title = ''.join(item.xpath('./a/text()').extract())
            news_url = ''.join(item.xpath('./a/@href').extract())
            news_time = ''.join(item.xpath('./em/text()').extract())
            item = NewsItem()
            item['title'] = news_title
            item['time'] = news_time
            item['url'] = news_url
            item['cata'] = response.meta['name']
            yield Request(news_url,meta={'item':item},callback=self.parse_news_info,dont_filter=True)



    def parse_news_info(self,response):
        item = response.meta['item']
        try:
            text = response.xpath('//*[@id="text"]')[0]
            item['image_urls'] = text.xpath('.//img/@src').extract()
            item['content'] = ''.join(text.xpath('./p').extract())
            item['summary'] = ''
            item['site'] = 2
            yield item
        except IndexError:
            pass










