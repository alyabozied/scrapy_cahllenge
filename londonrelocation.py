import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        
        for area_url in area_urls:
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):
      
        base_url = 'https://londonrelocation.com/properties-to-rent/properties/'
        # an example for adding a property to the json list:
        searchResults = response.css('div.test-inline')


        for result in searchResults:        
            property = ItemLoader(item=Property())
            title = result.css('div.h4-space').css('a::text').get().replace("\n",'')
            price_as_string = result.css('div.bottom-ic h5::text').get()

            price =[int(s) for s in price_as_string.split() if s.isdigit()][0]
            if(price_as_string[-2:]=="pw"):
                price*=4
            price = str(price)
            url = result.css('div.h4-space').css('a').attrib['href']
            property.add_value('title',title )
            property.add_value('price',price ) 
            property.add_value('url', base_url+url)
            yield property.load_item()
       
        try:
            next_page = response.css('div.pagination a::attr(href)').getall()[1]
            isSecond = response.css('div.pagination a::text').getall()[1]==2
            if isSecond:
                yield response.follow(next_page,callback=self.parse_area_pages)
        except:
            pass
    