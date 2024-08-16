# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EventsItem(scrapy.Item):
    # define the fields for your item here like:
    eventName = scrapy.Field()
    categories = scrapy.Field()
    locationName = scrapy.Field()
    addressLine1 = scrapy.Field()
    addressLine2 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zip = scrapy.Field()
    startDate = scrapy.Field()
    endDate = scrapy.Field()
    description = scrapy.Field()
    parkingInfo = scrapy.Field()
    eventLink = scrapy.Field()
    minAge = scrapy.Field()
    maxAge = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    bannerImage = scrapy.Field()
    pass
