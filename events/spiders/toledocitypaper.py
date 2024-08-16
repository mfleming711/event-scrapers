import scrapy
import datetime
import time
import urllib
import json
from slugify import slugify
from events.items import EventsItem


class ToledocitypaperSpider(scrapy.Spider):
    name = "toledocitypaper"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://toledocitypaper.com",
        "Referer": "https://toledocitypaper.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }
    end_date = None
    item_count_in_response = {}
    source_url_list = []

    def start_requests(self):
        start_date = datetime.datetime.now()
        api_url = "https://portal.cityspark.com/v1/events/ToledoCityPaper"

        end_date = (
            datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
            if self.end_date
            else start_date
        )

        # Loop through all dates from current date to end date
        current_date = start_date
        while current_date <= end_date:
            formatted_current_date = current_date.strftime("%Y-%m-%dT00:00")
            skip = 0
            while True:
                if (
                    formatted_current_date in self.item_count_in_response
                    and self.item_count_in_response[formatted_current_date] < 25
                ):
                    break
                print("###############")
                print(self.item_count_in_response.get(formatted_current_date))
                print("###############")
                end_at = (current_date + datetime.timedelta(days=1)).strftime(
                    "%Y-%m-%dT00:00"
                )
                payload = {
                    "ppid": 8308,
                    "start": formatted_current_date,
                    "end": end_at,
                    "labels": [],
                    "pick": False,
                    "tps": None,
                    "sparks": False,
                    "sort": "Time",
                    "category": [],
                    "distance": 150,
                    "lat": 41.65380859375,
                    "lng": -83.536262512207,
                    "search": "",
                    "skip": skip,
                    "defFilter": "all",
                }

                yield scrapy.Request(
                    url=api_url,
                    callback=self.parse_api_response,
                    method="POST",
                    headers=self.headers,
                    body=json.dumps(payload),
                    meta={"current_date": formatted_current_date, "skip": skip},
                )
                skip = skip + 25

            current_date += datetime.timedelta(days=1)

    def parse_api_response(self, response):
        res_json = json.loads(response.body)
        if res_json["Value"] == None:
            self.item_count_in_response[response.meta["current_date"]] = 0
            return
        else:
            self.item_count_in_response[response.meta["current_date"]] = len(
                res_json["Value"]
            )
        for row in res_json["Value"]:
            slug = slugify(row["Name"])
            time_slug = row["DateStart"].split(":")[0]
            source_url = f"https://toledocitypaper.com/calendar/details/{slug}/{row['PId']}/{time_slug}"

            event_item = EventsItem(
                eventName=row["Name"],
                categories="",
                locationName=row["Venue"],
                addressLine1=row["Address"],
                addressLine2="",
                city=row["CityState"].split(", ")[0],
                state=row["CityState"].split(", ")[1],
                zip=row["Zip"],
                startDate=row["DateStart"],
                endDate=row["DateEnd"],
                description=row["Description"],
                parkingInfo="",
                eventLink=row["Links"][0]["url"] if len(row["Links"]) > 0 else "",
                minAge="",
                maxAge="",
                latitude=row["latitude"],
                longitude=row["longitude"],
                bannerImage=row["LargeImg"],
                sourceURL=source_url,
            )

            if source_url not in self.source_url_list:
                self.source_url_list.append(source_url)
                yield event_item
