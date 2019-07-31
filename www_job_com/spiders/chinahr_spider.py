# -*- coding: utf-8 -*-
import scrapy
import time
from www_job_com.items import WwwJobComItem

CITY_DICT = {'天津': '35,399', '南京': '16,169', '惠州': '25,301',
             '重庆': '37,401', '石家庄': '11,111', '武汉': '23,264',
             '昆明': '29,342', '北京': '34,398',
             '大连': '13,134', '苏州': '16,173',
             '哈尔滨': '15,156', '杭州': '17,182', '成都': '27,312',
             '上海': '36,400', '合肥': '18,193', '广州': '25,291',
             '福州': '19,210', '长春': '14,147', '沈阳': '13,133',
             '西安': '30,358', '济南': '21,230', '长沙': '24,277',
             '东莞': '25,307', '郑州': '22,247', '深圳': '25,292'}

CITY = '深圳'
JOB_NAME = 'python'


class ZhipinSpider(scrapy.Spider):
    name = 'chinahr'
    allowed_domains = ['www.chinahr.com']
    start_urls = ['http://www.chinahr.com/']
    positionUrl = ''
    curPage = 0
    headers = {}

    def start_requests(self):
        return [self.next_request()]

    def parse(self, response):
        print("request -> " + response.url)
        job_list = response.css('div.jobList > ul')
        if (len(job_list) > 0):
            print("chinahr Nums:" + str(len(job_list)))
            for job in job_list:
                item = WwwJobComItem()
                item['position_id'] = job.css('li.l1 > span.e1 > a::attr(href)').extract_first().strip().replace(
                    ".html?searchplace=" + CITY_DICT[CITY], "").replace("http://www.chinahr.com/job/", "")
                item["position_name"] = job.css('li.l1 > span.e1 > a::text').extract_first().strip()
                salary = job.css('li.l2 > span.e2::text').extract_first().strip().split("-")
                item["salary"] = str(int(int(salary[0]) / 1000)) + "K-" + str(int(int(salary[1]) / 1000)) + "K"
                item["avg_salary"] = (int(salary[0]) + int(salary[1])) / 2000
                info_primary = job.css('li.l2 > span.e1::text').extract_first().strip().split("/")
                item['city'] = info_primary[0] + info_primary[1]
                item['work_year'] = info_primary[2].replace("]\r\n\t\t\t\t\t\t\t", "")
                item['education'] = info_primary[3]
                item['company_name'] = job.css('li.l1 > span.e3 > a::text').extract_first().strip()

                item['industry_field'] = ""
                item['finance_stage'] = ""
                item['company_size'] = ""

                item['position_lables'] = ""
                item['time'] = job.css('li.l1 > span.e2::text').extract_first().strip()
                item['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['platform'] = "chinahr"
                yield item
            yield self.next_request()

    # 发送请求
    def next_request(self):
        self.curPage += 1
        self.positionUrl = "http://www.chinahr.com/sou/?orderField=relate&" \
                           "keyword={}&city={}&page=".format(JOB_NAME, CITY_DICT[CITY]) + str(self.curPage)
        print("chinahr page:" + str(self.curPage))
        time.sleep(10)
        return scrapy.http.FormRequest(
            self.positionUrl,
            headers=self.headers,
            callback=self.parse)
