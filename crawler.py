import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

import html
import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime


RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"


def fetch_rss(url: str) -> BeautifulSoup:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "xml")


def parse_items(soup: BeautifulSoup) -> list[dict]:
    items = []
    for item in soup.find_all("item")[:10]:
        pub_date = item.find("pubDate")
        pub_date_text = pub_date.get_text(strip=True) if pub_date else "N/A"
        try:
            dt = datetime.strptime(pub_date_text, "%a, %d %b %Y %H:%M:%S GMT")
            pub_date_text = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            pass

        items.append({
            "title": item.find("title").get_text(strip=True) if item.find("title") else "N/A",
            "link": item.find("link").get_text(strip=True) if item.find("link") else "N/A",
            "description": html.unescape(re.sub(r"<[^>]+>", "", item.find("description").get_text(strip=True))) if item.find("description") else "N/A",
            "pub_date": pub_date_text,
        })
    return items


def print_items(items: list[dict]):
    for i, item in enumerate(items, 1):
        print(f"[{i}] {item['title']}")
        print(f"    {item['pub_date']}")
        print(f"    {item['link']}")
        print(f"    {item['description']}")
        print()


if __name__ == "__main__":
    print("뉴스 RSS 크롤러 - 구글 뉴스 한국어\n")
    soup = fetch_rss(RSS_URL)
    items = parse_items(soup)
    print_items(items)
    print(f"총 {len(items)}건 수집 완료")
