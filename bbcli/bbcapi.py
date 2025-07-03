import arrow
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

BBC_URL = "https://www.bbc.co.uk"
BBC_POLLING_URL = "https://polling.bbc.co.uk"
API_BASE_URL = "https://feeds.bbci.co.uk"


class BBC:
    def get_top_stories(self):
        news = self.get_bbc_story()
        if news is None:
            return None
        else:
            data = news.text
            return self.parse_news(data)


    def parse_news(self, xml_data):
        news_data = []

        root = ET.fromstring(xml_data)

        for item in root.findall(".//item"):
            ts_title = item.find("title").text if item.find(
                "title") is not None else ""
            ts_link = item.find("link").text if item.find(
                "link") is not None else ""
            ts_description = (
                item.find("description").text
                if item.find("description") is not None
                else ""
            )
            pubDate = (
                item.find("pubDate").text if item.find(
                    "pubDate") is not None else ""
            )

            ts_time = datetime.strptime(pubDate, "%a, %d %b %Y %H:%M:%S %Z")

            news_data.append(
                {
                    "title": ts_title,
                    "link": ts_link,
                    "description": ts_description,
                    "datetime": ts_time,
                    "pubDate": pubDate,
                }
            )

        news_data_sorted = sorted(
            news_data,
            key=lambda x: x["datetime"],
            reverse=True
        )

        news_item_list = []
        for data in news_data_sorted:
            timestamp_human = arrow.get(data["datetime"]).humanize()
            timestamp_last_updated = "Last updated: " + str(timestamp_human)

            news = NewsItem(
                data["title"],
                data["link"],
                data["description"],
                timestamp_last_updated
            )

            news_item_list.append(news)

        return news_item_list

    def get_bbc_story(self):
        res = None
        headers = {
            "User-Agent": "BBCNews/5.18.0 UK (Pixel 4; Android 10.0)",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "Accept": "application/json",
        }

        try:
            res = requests.get(
                API_BASE_URL + "/news/world/rss.xml",
                data=None,
                headers=headers
            )

        except requests.ConnectionError as e:
            if hasattr(e, "reason"):
                print("We failed to reach a server.")
                print("Reason: ", e.reason)
            elif hasattr(e, "code"):
                print("The server couldn't fulfill the request.")
                print("Error code: ", e.code)

        return res



class NewsItem:
    def __init__(self, title, link, description, last_updated):
        self.title = title
        self.link = link
        self.description = description
        self.last_updated = last_updated

