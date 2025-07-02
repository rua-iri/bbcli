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

    def get_ticker(self):
        ticker = self.get_bbc_ticker()
        if ticker is None:
            return None
        elif ticker.status_code == 404:
            return None
        else:
            data = ticker.json(strict=False)
        return self.parse_ticker_data(data)

    def parse_ticker_data(self, data):
        tickers = []

        if bool(data["asset"]) is False:
            return tickers

        # Headline
        headline = data["asset"]["headline"]

        # News Link as in /news/
        url = data["asset"]["assetUri"]

        ticker = Ticker(headline, "BREAKING NEWS", "true", BBC_URL + url)
        tickers.append(ticker)
        return tickers

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

    def get_bbc_ticker(self):
        res = None
        ua = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }
        try:
            res = requests.get(
                BBC_POLLING_URL + "/news/breaking-news/audience/domestic",
                data=None,
                headers=ua,
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


class Ticker:
    def __init__(self, headline, prompt, breaking, url):
        self.headline = headline
        self.prompt = prompt
        self.breaking = breaking
        self.url = url
