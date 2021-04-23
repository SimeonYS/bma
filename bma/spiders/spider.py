import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BmaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BmaSpider(scrapy.Spider):
	name = 'bma'
	start_urls = ['https://www.bma.com.af/dari/news_details.php?w_id=125']

	def parse(self, response):
		articles = response.xpath('//div[@class="media-body"]')
		for article in articles:
			date = article.xpath('.//h6/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="col-sm-8 main_blog"]/h2/text()').get()
		content = response.xpath('//div[@class="col-xs-11 blog_content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BmaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
