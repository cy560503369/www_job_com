# -*- coding: utf-8 -*-
import scrapy
import time
import json
from www_job_com.items import WwwJobComItem


class ZhaopinSpider(scrapy.Spider):
    name = 'zhaopin'
    allowed_domains = ['sou.zhaopin.com']
    start_urls = ['http://sou.zhaopin.com/']
    positionUrl = ''
    curPage = 0
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
               "Accept-Encoding": "gzip, deflate, br",
               "Referer": "https://sou.zhaopin.com/?p=2&jl=%E6%B7%B1%E5%9C%B3&et=2&kw=php&kt=3&sf=0&st=0"}

    def start_requests(self):
        return [self.next_request()]

    def parse(self, response):
        print("request -> " + response.url)

        try:
            html = json.loads(response.body)
        except ValueError:
            print(response.body)
            yield self.next_request()

        if 'data' in html.keys():
            if 'results' in html['data'].keys():
                results = html.get('data').get('results')
                print('zhilian Nums:' + str(len(results)))
                for result in results:
                    item = WwwJobComItem()
                    item['salary'] = result.get('salary').replace("k", "K")
                    salary = item["salary"].split("-")
                    if len(salary) > 1:
                        item["avg_salary"] = (float(salary[0].replace("K", "")) + float(salary[1].replace("K", ""))) / 2
                    else:
                        item["avg_salary"] = item["salary"]
                    item['city'] = result.get('city').get("display")
                    item['finance_stage'] = ''
                    item['industry_field'] = ''
                    item['position_lables'] = result.get('jobType').get('items')[0].get('name')
                    item['position_id'] = result.get('number')
                    item['company_size'] = result.get('company').get('size').get('name')
                    item['position_name'] = result.get('jobName')
                    item['work_year'] = result.get('workingExp').get('name')
                    item['education'] = result.get('eduLevel').get('name')
                    item['company_name'] = result.get('company').get('name')
                    item['time'] = result.get("updateDate")
                    item['updated_at'] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                       time.localtime())
                    item['platform'] = "zhilianzhaopin"
                    yield item

                self.curPage = self.curPage + 1
                if self.curPage <= 10:
                    yield self.next_request()

    # 发送请求
    def next_request(self):
        self.curPage += 1
        if self.curPage <= 10:
            self.positionUrl = "https://fe-api.zhaopin.com/c/i/sou?pageSize=" \
                               "90&cityId=%E6%B7%B1%E5%9C%B3&workExperience=" \
                               "-1&education=-1&companyType=-1&employmentTy" \
                               "pe=2&jobWelfareTag=-1&kw=php&kt=3&_v=0.946" \
                               "46938&x-zp-page-request-id=b268493d567142a" \
                               "0ba18a608ad86ff48-1564561458575-864443&x-zp-" \
                               "client-id=10097453-22d1-4ec6-9ebe-38afe6796" \
                               "6ad&start=" + str(self.curPage * 90)
            print("zhaopin page:" + str(self.curPage))
            time.sleep(2)
            return scrapy.http.FormRequest(self.positionUrl,
                                           headers=self.headers,
                                           callback=self.parse)
