# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cata= scrapy.Field()
    time = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    site = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()


