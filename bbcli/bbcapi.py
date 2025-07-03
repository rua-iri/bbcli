import arrow
import requests
from datetime import datetime
from xmltodict import parse as xml_parse_dict

BBC_URL = "https://www.bbc.co.uk"
API_BASE_URL = "https://feeds.bbci.co.uk"
WORLD_NEWS_ENDPOINT = "/news/world/rss.xml"


class BBC:
    def get_top_stories(self):
        news = self.get_bbc_story()
        if news is None:
            return None
        else:
            data = news.text
            return self.parse_news_improved(data)

    def parse_news_improved(self, xml_data):
        news_data = []

        data_dict = xml_parse_dict(xml_input=xml_data)

        news_item_data = data_dict["rss"]["channel"]["item"]

        for item in news_item_data:

            published_date = item.get("pubDate")

            timestamp_time = datetime.strptime(
                published_date,
                "%a, %d %b %Y %H:%M:%S %Z"
            )

            news_data.append(
                {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "description": item.get("description"),
                    "datetime": timestamp_time,
                    "pubDate": published_date,
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
                API_BASE_URL + WORLD_NEWS_ENDPOINT,
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
