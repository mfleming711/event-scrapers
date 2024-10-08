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

        yield scrapy.Request(
            url="http://echo.jsontest.com/insert-key-here/insert-value-here/key/value",
            callback=self.parse_response,
            method="GET",
            headers={
                "Referer": "",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            },
            meta={"start_date": formatted_start_date, "end_date": end_date},
        )

    def parse_response(self, response):
        end_date = response.meta["end_date"]

        url = "https://www.toledo.com/events/"
        origin_url = "https://www.toledo.com/events/"
        index = 1

        payload = {}
        headers = {
            "accept": "text/html, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9,fr;q=0.8",
            "cookie": "PHPSESSID=9440d7c27cf808ff8c94f29498; _ga=GA1.2.1746171625.1723734965; _hjSessionUser_64303=eyJpZCI6ImYwZjI1Mjk5LTgxYmYtNWE3YS04YmM2LTkwYzRiNzc3ZTBmNCIsImNyZWF0ZWQiOjE3MjM3MzQ5NjYxNjIsImV4aXN0aW5nIjp0cnVlfQ==; _gid=GA1.2.69996161.1724168806; _hjSession_64303=eyJpZCI6ImZlNGU5ZGI3LTQ2YzgtNDJjYy1iMzVkLTc3MjkxN2UwZjNjNCIsImMiOjE3MjQxNjg4MDc2NjIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _ga_56GJ538Y8Y=GS1.2.1724168808.5.1.1724168854.0.0.0",
            "priority": "u=1, i",
            "referer": "https://www.toledo.com/events",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        while True:
            if url is None:
                break

            SCRAPE_TOKEN = self.settings.get("SCRAPE_TOKEN")

            res = requests.request(
                "GET",
                f"http://api.scrape.do?token={SCRAPE_TOKEN}&url={url}",
                headers=headers,
                data=payload,
            )
            soup = BeautifulSoup(res.text, "html.parser")

            item_list = soup.find_all("article", class_="item")

            if len(item_list) == 0:
                break

            start_date = None if len(item_list) > 0 else end_date

            print("start_date", start_date)
            print("end_date", end_date)
            API_KEY = self.settings.get("GEO_CODE_API_KEY")
            for item in item_list:
                detail_slug = item.find("a", class_="title")["href"]
                detail_url = f"https://www.toledo.com/{detail_slug}"

                start_date = item.find("p", class_="date")["content"]

                if start_date <= end_date:
                    detail_res = requests.request(
                        "GET",
                        f"http://api.scrape.do?token={SCRAPE_TOKEN}&url={detail_url}",
                        headers=headers,
                        data=payload,
                    )
                    print("%" * 20)
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                    event_name = detail_soup.find("h1", itemprop="name")
                    event_name = event_name.string if event_name else ""

                    event_link = detail_soup.find("a", itemprop="url")
                    event_link = event_link["href"] if event_link else ""

                    location_name = detail_soup.find("span", itemprop="name")
                    location_name = location_name.string if location_name else ""

                    zip = detail_soup.find("span", itemprop="postalCode")
                    zip = zip.string if zip else ""

                    state = detail_soup.find("span", class_="state")
                    state = state.string if state else ""
                    state = state.upper() if state else ""

                    city = detail_soup.find("span", itemprop="addressLocality")
                    city = city.string if city else ""

                    street_address = detail_soup.find("span", itemprop="streetAddress")
                    street_address = street_address.string if street_address else ""
                    # time_slot = detail_soup.find_all("section")[1].find("p").string
                    description = detail_soup.find("section", itemprop="description")
                    description = description.string if description else ""
                    source_url = detail_url

                    banner_image = detail_soup.find("img", class_="header-image")
                    banner_image = banner_image["data-src"] if banner_image else ""
                    banner_image_url = f"https://www.toledo.com/{banner_image}"

                    categories = detail_soup.find("pre").find("a").string
                    categories = categories.replace("&", "|") if categories else ""

                    lat_lon = get_lat_lon(
                        f"{location_name}, {street_address}, {city}, {state} {zip}",
                        API_KEY,
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
                        startDate=start_date,
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

            if start_date <= end_date:
                index += 1
                url = f"{origin_url}{index}/"
            else:
                url = None
