import scrapy
import datetime
from events.items import EventsItem
from bs4 import BeautifulSoup
import requests

api_key = "AIzaSyDLRvZpEhn81Z6hfpbFjfGWnbPHJ8orvDA"


def get_lat_lon(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
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


class VisittoledoSpider(scrapy.Spider):
    name = "visittoledo"

    end_date = None
    source_url_list = []

    def start_requests(self):
        start_date = datetime.datetime.now()

        end_date = (
            datetime.datetime.strptime(self.end_date, "%Y-%m-%d")
            + datetime.timedelta(days=1)
            - datetime.timedelta(seconds=1)
            if self.end_date
            else start_date
        )

        # Loop through all dates from current date to end date
        current_date = start_date
        while current_date <= end_date:
            formatted_current_date = current_date.strftime("%m-%d-%Y")

            page_url = (
                f"https://www.visittoledo.org/events/?date={formatted_current_date}"
            )

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9,fr;q=0.8",
                "cookie": "_gcl_au=1.1.2932431.1723734969; __utmz=7308597.1723734971.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); canPersist=true; cobiSessionId=93c9e525-fafb-44b7-91d7-8edc1ad3800a; userId=6c5784ac-6391-4cf3-93de-4b2b26ec12c6; __tld=visittoledo.org; __utmc=7308597; __utma=7308597.2131234452.1723734970.1723744247.1723879841.3; _gid=GA1.2.1851949058.1723879852; _ga_CLDFDS1LQK=GS1.1.1723879841.4.1.1723880026.33.0.0; cobiConversionExperienceId=ac46b459-7806-49f6-b400-48cd9bdaa13d; experienceId=40ed4bb7-d9ad-4b58-8ee3-9f1297715ad1; _ga=GA1.2.2131234452.1723734970; _gat_UA-56590839-1=1",
                "priority": "u=0, i",
                "referer": "https://www.visittoledo.org/events/",
                "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            }

            yield scrapy.Request(
                url=page_url,
                callback=self.parse_response,
                method="GET",
                headers=headers,
                meta={"current_date": formatted_current_date},
            )

            current_date += datetime.timedelta(days=1)

    def parse_response(self, response):
        soup = BeautifulSoup(response.body, "html.parser")

        item_list = soup.find_all("div", class_="item")
        for item in item_list:
            detail_slug = item.find("h5", class_="heading").find("a")["href"]
            detail_url = f"https://www.visittoledo.org{detail_slug}"

            start_date = item.find("div", class_="date-and-time").get_text()
            start_date = start_date.strip().replace("  ", "").replace("\r\n", " ")

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9,fr;q=0.8",
                "cache-control": "max-age=0",
                "cookie": "_gcl_au=1.1.2932431.1723734969; __utmz=7308597.1723734971.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); canPersist=true; cobiSessionId=93c9e525-fafb-44b7-91d7-8edc1ad3800a; userId=6c5784ac-6391-4cf3-93de-4b2b26ec12c6; __tld=visittoledo.org; __utmc=7308597; _gid=GA1.2.1851949058.1723879852; __utma=7308597.2131234452.1723734970.1723882146.1723883946.5; __utmt_UA-56590839-1=1; _ga_CLDFDS1LQK=GS1.1.1723882145.5.1.1723884607.49.0.0; __utmb=7308597.3.10.1723883946; cobiConversionExperienceId=51e8a77b-f040-4847-be1e-0472b50da656; experienceId=7fa367a4-5661-4641-bd15-398d90b22dd4; _ga=GA1.2.2131234452.1723734970",
                "priority": "u=0, i",
                "referer": "https://www.visittoledo.org/events/",
                "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Linux"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            }

            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail_response,
                method="GET",
                headers=headers,
                meta={"start_date": start_date},
            )

    def parse_detail_response(self, response):
        soup = BeautifulSoup(response.body, "html.parser")

        container = soup.find("main").find_all("div", class_="container")[4]
        source_url = response.url
        event_name = container.find("h2").string
        banner_image = container.find("img")["src"]
        banner_image_url = f"https://www.visittoledo.org{banner_image}"

        address_block = container.find("div", class_="lead").find("p")
        address_list = address_block.decode_contents().split("<br/>")
        address_list = [s for s in address_list if s]

        has_state_zip = address_list[-1].find(", ") > -1

        location_name = address_list[0] if len(address_list) > 0 else ""
        location_name = location_name.replace("<span>", "").replace("</span>", "")

        city_state_zip = address_list[-1] if has_state_zip else ""
        city_state_zip_list = city_state_zip.split(", ")
        city = city_state_zip_list[0] if len(city_state_zip_list) > 0 else ""
        city = city.replace("<span>", "").replace("</span>", "")

        state_zip = city_state_zip_list[1] if len(city_state_zip_list) > 1 else None
        state_zip_list = state_zip.split(" ") if state_zip else None

        state = state_zip_list[0] if state_zip_list and len(state_zip_list) > 0 else ""
        state = state.replace("<span>", "").replace("</span>", "")

        zip = state_zip_list[1] if state_zip_list and len(state_zip_list) > 1 else ""
        zip = zip.replace("<span>", "").replace("</span>", "")

        if has_state_zip:
            address_list = address_list[:-1]
        address_list = address_list[1:]

        address_line1 = ", ".join(address_list) if len(address_list) > 0 else ""
        address_line1 = address_line1.replace("<span>", "").replace("</span>", "")

        event_link_tag = container.find("a", class_="learnMore")
        event_link = event_link_tag["href"] if event_link_tag else ""

        # Remove the <div> with class "lead" and the <h2> tag
        container.find("h2").decompose()  # Removes the <h2> tag
        lead_div = container.find("div", class_="lead")
        if lead_div:
            lead_div.decompose()  # Removes the <div> with class "lead"

        if event_link_tag:
            event_link_tag.decompose()

        ticket_url_tag = container.find("a", class_="ticketsUrl")
        if ticket_url_tag:
            ticket_url_tag.decompose()

        content = container.find("div", class_="col-md-8")

        # Convert <br/> tags to newlines
        for br in content.find_all("br"):
            br.replace_with("\n")

        lat_lon = get_lat_lon(", ".join(address_list))
        if lat_lon:
            print(f"Latitude: {lat_lon[0]}, Longitude: {lat_lon[1]}")

        event_item = EventsItem(
            eventName=event_name,
            categories="",
            locationName=location_name,
            addressLine1=address_line1,
            addressLine2="",
            city=city,
            state=state,
            zip=zip,
            startDate=response.meta["start_date"],
            endDate="",
            description=content.text.strip(),
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
