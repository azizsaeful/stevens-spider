import scrapy
import re


class StevensSpider(scrapy.Spider):
    name = "stevens"

    def start_requests(self):
        urls = 'http://www.ecountyworks.com/stevens/TaxSearchAdvanced.php'
        formdata = []
        start = 1
        end = 20000
        combination = []
        now = start
        while now <= end:
            combination.append(now)
            now = now + 200
        print(combination)
        dictbase = {"submit_check": "1",
                    "searchname": "",
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
        for i in combination:
            dictbase["stmtnumfrom"] = i
            dictbase["stmtnumthru"] = i + 199
            dicty = dict(dictbase)
            formdata.append(dicty)
        for form in formdata:
            yield scrapy.FormRequest(url=urls, formdata=form, callback=self.parse)

    def parse(self, response):
        i = response.xpath("//input[@name='stmtnumfrom']").attrib['value']
        filename = f'stevens-{i}to-{i+199}.html'
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
                'statement range': str(i) + " to " + str(i+199)
            }
