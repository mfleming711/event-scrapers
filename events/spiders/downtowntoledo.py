import scrapy
import datetime
import json
import requests
from events.items import EventsItem


class DowntowntoledoSpider(scrapy.Spider):
    name = "downtowntoledo"

    headers = {
        "Referer": "",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    end_date = None

    def start_requests(self):
        start_date = datetime.datetime.now()
        end_date = (
            datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
            + datetime.timedelta(days=1)
            - datetime.timedelta(seconds=1)
            if self.end_date
            else start_date
        )

        formatted_start_date = start_date.strftime("%Y-%m-%dT00:00:00")
        formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        api_url = f"https://api.vibemap.com/v0.3/search/events/?point=-83.539113%2C41.6494069&ordering=-score_combined&start_date_after=&shouldShuffle=false&shouldSort=false&location__geo_distance=6437m__41.6494069__-83.539113&end_date__gte={formatted_start_date}&start_date__lte={formatted_end_date}&page_size=200&cache_bust=5747111&is_approved=false&is_chain=false&is_closed=false&is_destination=false&dist=6437"

        yield scrapy.Request(
            url="http://echo.jsontest.com/insert-key-here/insert-value-here/key/value",
            callback=self.parse_api_response,
            method="GET",
            headers=self.headers,
            meta={"url": api_url},
        )

    def parse_api_response(self, response):
        api_url = response.meta["url"]

        while True:
            if api_url is None:
                break

            res = requests.request("GET", api_url, headers=self.headers, data={})
            res_json = json.loads(res.text)

            api_url = res_json["next"]

            for row in res_json["results"]["features"]:
                source_url = "https://www.downtowntoledo.org/events/"
                event_link = row["properties"]["url"]
                categories = " | ".join(row["properties"]["tags"])
                banner_image_url = (
                    row["properties"]["vibemap_images"][0]["original"]
                    if len(row["properties"]["vibemap_images"]) > 0
                    else ""
                )

                event_item = EventsItem(
                    eventName=row["properties"]["name"],
                    categories=categories,
                    locationName=row["properties"]["hotspots_place"],
                    addressLine1="",
                    addressLine2="",
                    city="",
                    state="",
                    zip="",
                    startDate=row["properties"]["start_date"],
                    endDate=row["properties"]["end_date"],
                    description=row["properties"]["description"],
                    parkingInfo="",
                    eventLink=event_link,
                    minAge="",
                    maxAge="",
                    latitude=row["properties"]["location"]["lat"],
                    longitude=row["properties"]["location"]["lon"],
                    bannerImage=banner_image_url,
                    sourceURL=source_url,
                )

                yield event_item
