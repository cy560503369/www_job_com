# -*- coding:utf-8 -*-

import scrapy
import time
from www_job_com import settings
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from www_job_com.items import WwwJobComItem

JOB_NAME = settings.JOB_NAME
CITY = settings.CITY


class LaGouSpider(scrapy.Spider):
    name = 'lagou'

    def __init__(self):
        self.option = Options()
        self.option.headless = False
        self.brower = webdriver.Firefox(options=self.option)
        self.wait = WebDriverWait(self.brower, 30)
        self.url = 'https://www.lagou.com/jobs/list_{}?city={}&cl='\
                   'false&fromSearch=true&labelWords='\
                   '&suginput='.format(JOB_NAME, CITY)
        self.curPage = 1
        self.totalPage = 0

    def closed(self, spider):
        print('spider close')
        self.brower.close()

    def start_requests(self):
        print("spider start")
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        for box in response.xpath('//ul[@class="item_con_list" and @style="display: block;"]/li'):
            item = WwwJobComItem()

            item['position_id'] = box.xpath('./@data-positionid').extract()[0]
            item["position_name"] = box.xpath('./@data-positionname').extract()[0]
            item["salary"] = box.xpath('./@data-salary').extract()[0]
            item["avg_salary"] = ''
            item['city'] = box.xpath('.//span[@class="add"]/em/text()').extract()[0]

            tmp = box.xpath('.//div[@class="p_bot"]/div[@class="li_b_l"]/text()').extract()[2].strip().split('/')
            item['work_year'] = tmp[0]
            item['education'] = tmp[1]
            item['company_name'] = box.xpath('.//div[@class="company_name"]/a/text()').extract()[0]

            tmp = box.xpath('.//div[@class="industry"]/text()').extract()[0].strip().split('/')
            item['industry_field'] = tmp[0]
            item['finance_stage'] = tmp[1]
            item['company_size'] = tmp[2]
            item['position_lables'] = ""
            item['time'] = box.xpath('.//span[@class="format-time"]/text()').extract()[0]
            item['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime())
            item['platform'] = "lagou"
            yield item

        self.totalPage = response.xpath('//div[@class="page-number"]/span[@class="span totalNum"]/text()').extract()[0]
        self.curPage += 1
        if self.curPage <= self.totalPage:
            print('next')
            yield scrapy.Request(url=self.url, callback=self.parse, dont_filter=True)
