import scrapy
import datetime
import time
import urllib
import json
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
            formatted_date = current_date.strftime("%Y-%m-%dT00:00")

            payload = {
                "ppid": 8308,
                "start": formatted_date,
                "end": None,
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
                "skip": 0,
                "defFilter": "all",
            }

            yield scrapy.Request(
                url=api_url,
                callback=self.parse_api_response,
                method="POST",
                headers=self.headers,
                body=json.dumps(payload),
                #  meta = {'from': fromDate, 'to': toDate, 'count': count}
            )

            current_date += datetime.timedelta(days=1)

    def parse_api_response(self, response):
        res_json = json.loads(response.body)

        for row in res_json["Value"]:
            event_item = EventsItem(
                eventName=row["Name"],
                categories=None,
                locationName=row["Venue"],
                addressLine1=row["Address"],
                addressLine2=None,
                city=row["CityState"].split(", ")[0],
                state=row["CityState"].split(", ")[1],
                zip=row["Zip"],
                startDate=row["DateStart"],
                endDate=row["DateEnd"],
                description=row["Description"],
                parkingInfo=None,
                eventLink=row["Links"][0]["url"] if len(row["Links"]) > 0 else None,
                minAge=None,
                maxAge=None,
                latitude=row["latitude"],
                longitude=row["longitude"],
                bannerImage=row["LargeImg"],
            )

            yield event_item
