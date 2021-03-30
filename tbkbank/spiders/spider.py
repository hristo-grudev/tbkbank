import scrapy

from scrapy.loader import ItemLoader

from ..items import TbkbankItem
from itemloaders.processors import TakeFirst


class TbkbankSpider(scrapy.Spider):
	name = 'tbkbank'
	start_urls = ['https://www.tbkbank.com/our-bank/news-events/']

	def parse(self, response):
		post_links = response.xpath('//div[contains(@class,"inner full-background")]')
		for post in post_links:
			url = post.xpath('.//a/@href').get()
			title = post.xpath('.//h6/text()').get()
			date = post.xpath('.//p[@class="date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		next_page = response.xpath('/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@id="content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=TbkbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
