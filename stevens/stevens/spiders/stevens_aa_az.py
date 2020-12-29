import scrapy
import re


class StevensSpider(scrapy.Spider):
    name = "stevens"

    def start_requests(self):
        urls = 'http://www.ecountyworks.com/stevens/TaxSearchAdvanced.php'
        formdata = []
        src2 = ["aa"]
        src = ["aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj", "ak", "al", "am", "an", "ao", "ap", "aq",
               "ar", "as", "at", "au", "av", "aw", "ax", "ay", "az"]
        dictbase = {"submit_check": "1",
                    "searchname": "aa",
                    "nametype": "Owner",
                    "searchparcel": "",
                    "loanco": "",
                    "tyearfrom": "2020",
                    "tyearthru": "",
                    "stmtnumfrom": "",
                    "stmtnumthru": "",
                    "streetnum": "",
                    "streetdir": "",
                    "streetname": "",
                    "ctytwp": "",
                    "zipcode": "",
                    "section": "",
                    "township": "",
                    "range": "",
                    "sub": "",
                    "lot": "",
                    "block": "",
                    "Minerals": "1"}
        for s in src2:
            dictbase["searchname"] = s
            dicty = dict(dictbase)
            formdata.append(dicty)
        for form in formdata:
            yield scrapy.FormRequest(url=urls, formdata=form, callback=self.parse)

    def parse(self, response):
        src = response.xpath("//input[@name='searchname']").attrib['value']
        filename = f'stevens-{src}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
        for row in response.xpath(
                '//html/body[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[td[contains(., "2020")]]'):
            yield {
                'year': row.xpath('td[1]/text()').get(),
                'statement': row.xpath('td[3]/text()').get(),
                'type': row.xpath('td[5]/text()').get(),
                'parcel number': row.xpath('td[7]/a/text()').get(),
                'property address': row.xpath('td[7]/text()').getall()[0],
                'section': re.search(r'SECTION: (.*?) ', row.xpath('td[7]/text()').getall()[1]).group(1),
                'township': re.search(r'TOWNSHIP: (.*?) ', row.xpath('td[7]/text()').getall()[1]).group(1),
                'range': re.search(r'(\s(\w+)$)', row.xpath('td[7]/text()').getall()[1]).group(1).replace(' ', ''),
                'owner': row.xpath('td[9]').get().replace('<td style="vertical-align:top;">', '').replace('</td>', ''),
                'taxpayer': row.xpath('td[11]').get().replace('<td style="vertical-align:top;">', '').replace('</td>', ''),
                'war red': row.xpath('td[13]/text()').get(),
                'total due': row.xpath('td[15]/text()').get(),
                'loan company': row.xpath('td[17]/text()').get(),
                'search': src
            }
