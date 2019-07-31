# -*- coding: utf-8 -*-
import scrapy
import time
from urllib.parse import quote
from www_job_com.items import WwwJobComItem

# 城市为空列表的时候表示全国
CITY_DICT = {'天津': '050000', '南京': '070200', '惠州': '030300', '重庆': '060000', '石家庄': '160200', '武汉': '180200',
             '无锡': '070400', '昆明': '250200', '北京': '010000', '宁波': '080300', '大连': '230300', '苏州': '070300',
             '哈尔滨': '220200', '杭州': '080200', '成都': '090200', '上海': '020000', '合肥': '150200', '广州': '030200',
             '福州': '110200', '长春': '240200', '沈阳': '230200', '西安': '200200', '济南': '120200', '长沙': '190200',
             '东莞': '030800', '郑州': '170200', '深圳': '040000'}
# 职位
JOBNAME = 'Python'
# 城市
CITYS = ['深圳']


class Job51Spider(scrapy.Spider):
    name = 'job51'
    allowed_domains = ['search.51job.com']
    start_urls = ['http://search.51job.com/']
    positionUrl = ''
    curPage = 0
    headers = {}

    def start_requests(self):
        return [self.next_request()]

    def parse(self, response):
        print("request -> " + response.url)
        job_list = response.css('div.dw_table > div.el')
        if (len(job_list) > 1):
            print("51job Nums:" + str(len(job_list)))
            for job in job_list:
                item = WwwJobComItem()
                str_time = job.css('span.t5::text').extract_first().strip()
                if (str_time == "发布时间"):
                    continue
                else:
                    item['position_id'] = job.css('p.t1 > input::attr(value)').extract_first().strip()
                    item["position_name"] = job.css('p.t1 > span > a::text').extract_first().strip()
                    salary = job.css('span.t4::text').extract_first().strip()
                    if (salary.find("万/月") > -1):
                        salary = salary.replace("万/月", "").split("-")
                        item["salary"] = str(float(salary[0]) * 10) + "K-" + str(float(salary[1]) * 10) + "K"
                        item["avg_salary"] = (float(salary[0]) * 10 + float(salary[1]) * 10) / 2
                    elif (salary.find("万/年") > -1):
                        salary = salary.replace("万/年", "").split("-")
                        item["salary"] = str(float(salary[0]) / 12) + "K-" + str(float(salary[1]) / 12) + "K"
                        item["avg_salary"] = (float(salary[0]) / 12 + float(salary[1]) / 12) / 2
                    elif (salary.find("元/天") > -1):
                        continue
                    else:
                        salary = salary.replace("千/月", "").split("-")
                        item["salary"] = salary[0] + "K-" + salary[1] + "K"
                        item["avg_salary"] = (float(salary[0]) + float(salary[1])) / 2
                    item['city'] = job.css('span.t3::text').extract_first().strip()
                    item['work_year'] = ""
                    item['education'] = ""
                    item['company_name'] = job.css('span.t2 > a::text').extract_first().strip()

                    item['industry_field'] = ""
                    item['finance_stage'] = ""
                    item['company_size'] = ""
                    item['position_lables'] = ""
                    item['time'] = str_time
                    item['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['platform'] = "51job"
                    yield item
            yield self.next_request()

    # 发送请求
    def next_request(self):
        self.curPage += 1

        base_url = "http://search.51job.com/list/{},000000,0000,00,9,99,{},2,"

        if len(CITYS) == 1:
            citynum = CITY_DICT[CITYS[0]]
        elif len(CITYS) > 1:
            lis = [CITY_DICT[c] for c in CITYS]
            citynum = ','.join(lis)
        else:
            citynum = ''

        the_url = base_url.format(quote(citynum), quote(JOBNAME))
        self.positionUrl = the_url + str(self.curPage) + ".html"
        print("51job page:" + str(self.curPage))
        time.sleep(1)
        return scrapy.http.FormRequest(self.positionUrl,
                                       headers=self.headers,
                                       callback=self.parse)
