# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import datetime
from scrapy import signals
from scrapy.exporters import CsvItemExporter


class QuoteAllDialect(csv.excel):
    quoting = csv.QUOTE_ALL


class QuoteAllCsvItemExporter(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs.update({"dialect": QuoteAllDialect})
        super(QuoteAllCsvItemExporter, self).__init__(*args, **kwargs)


class EventsPipeline:
    def __init__(self):
        self.files = {}
        self.exporter = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        current_date = datetime.datetime.now()
        start_date = current_date.strftime("%Y-%m-%d")
        filename = (
            f"toledocitypaper[{start_date}].csv"
            if start_date == spider.end_date or spider.end_date is None
            else f"toledocitypaper[{start_date} ~ {spider.end_date}].csv"
        )
        file = open(filename, "w+b")
        self.files[spider] = file
        self.exporter = QuoteAllCsvItemExporter(file)
        self.exporter.fields_to_export = [
            "eventName",
            "categories",
            "locationName",
            "addressLine1",
            "addressLine2",
            "city",
            "state",
            "zip",
            "startDate",
            "endDate",
            "description",
            "parkingInfo",
            "eventLink",
            "minAge",
            "maxAge",
            "latitude",
            "longitude",
            "bannerImage",
        ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
