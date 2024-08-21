import scrapy
import datetime
from events.items import EventsItem
from bs4 import BeautifulSoup
import requests


def get_lat_lon(address, API_KEY):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            return lat, lon
        else:
            print("No results found for the given address.", address)
    else:
        print(f"Error: {response.status_code}")
    return None


class ToledoSpider(scrapy.Spider):
    name = "toledo"

    end_date = None
    source_url_list = []

    def start_requests(self):
        start_date = datetime.datetime.now()
        formatted_start_date = start_date.strftime("%Y-%m-%d")

        end_date = self.end_date if self.end_date else formatted_start_date

        headers = {
            "Referer": "",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }

        yield scrapy.Request(
            url="http://echo.jsontest.com/test/insert-here/key/value",
            callback=self.parse_response,
            method="GET",
            headers=headers,
            meta={"start_date": formatted_start_date, "end_date": end_date},
        )

    def parse_response(self, response):
        end_date = response.meta["end_date"]

        print (end_date)

        url = "https://www.toledo.com/events/"
        origin_url = "https://www.toledo.com/events/"
        index = 1

        payload = {}
        headers = {
            "accept": "text/html, */*; q=0.01",
        }

        while True:
            if url is None:
                break

            res = requests.request("GET", url, headers=headers, data=payload)
            soup = BeautifulSoup(res.text, "html.parser")

            item_list = soup.find_all("article", class_="item")
            start_date = None if len(item_list) > 0 else end_date
            for item in item_list:
                detail_slug = item.find("a", class_="title")["href"]
                detail_url = f"https://www.toledo.com/{detail_slug}"

                start_date = item.find("p", class_="date")["content"]

                if start_date <= end_date:
                    yield scrapy.Request(
                        url=detail_url,
                        callback=self.parse_detail_response,
                        method="GET",
                        headers=headers,
                        meta={"start_date": start_date},
                    )

            if start_date <= end_date:
                index += 1
                url = f"{origin_url}{index}/"
            else:
                url = None

    def parse_detail_response(self, response):
        soup = BeautifulSoup(response.body, "html.parser")

        event_name = soup.find("h1", itemprop="name").string
        event_link = soup.find("a", itemprop="url")["href"]
        location_name = soup.find("span", itemprop="name").string
        zip = soup.find("span", itemprop="postalCode").string
        state = soup.find("span", class_="state").string
        state = state.upper() if state else ""
        city = soup.find("span", itemprop="addressLocality").string
        street_address = soup.find("span", itemprop="streetAddress").string
        time_slot = soup.find_all("section")[1].find("p").string
        description = soup.find("section", itemprop="description").string
        source_url = response.url

        banner_image = soup.find("img", class_="header-image")["data-src"]
        banner_image_url = f"https://www.toledo.com/{banner_image}"

        categories = soup.find("pre").find("a").string
        categories = categories.replace("&", "|") if categories else ""

        API_KEY = self.settings.get("GEO_CODE_API_KEY")

        lat_lon = get_lat_lon(
            f"{location_name}, {street_address}, {city}, {state} {zip}", API_KEY
        )
        if lat_lon:
            print(f"Latitude: {lat_lon[0]}, Longitude: {lat_lon[1]}")

        event_item = EventsItem(
            eventName=event_name,
            categories=categories,
            locationName=location_name,
            addressLine1=street_address,
            addressLine2="",
            city=city,
            state=state,
            zip=zip,
            startDate=response.meta["start_date"],
            endDate="",
            description=description,
            parkingInfo="",
            eventLink=event_link,
            minAge="",
            maxAge="",
            latitude=lat_lon[0] if lat_lon else "",
            longitude=lat_lon[1] if lat_lon else "",
            bannerImage=banner_image_url,
            sourceURL=source_url,
        )

        if source_url not in self.source_url_list:
            self.source_url_list.append(source_url)
            yield event_item
