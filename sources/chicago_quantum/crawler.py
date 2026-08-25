#!/usr/bin/env python3
"""Chicago Quantum Exchange news crawler."""
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

API_URL = "https://chicagoquantum.org/api/v1/news/index"
SOURCE_URL = "https://chicagoquantum.org/news"
SOURCE_NAME = "Chicago Quantum Exchange"
SOURCE_KEY = "chicago_quantum"
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../../data/raw/chicago_quantum"
)


def parse_date(value):
    try:
        return datetime.strptime(value.strip(), "%B %d, %Y").date()
    except (AttributeError, ValueError):
        return None


def fetch_articles(days):
    cutoff = (datetime.now() - timedelta(days=days)).date()
    articles = []
    headers = {"User-Agent": "hot-edu-news/1.0 (+https://github.com/xutao-91/hot-edu-news)"}

    for page in range(1, 30):
        response = requests.get(API_URL, params={"page": page}, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        if not items:
            break

        reached_older_items = False
        for item in items:
            published = parse_date(item.get("date", ""))
            if not published:
                continue
            if published < cutoff:
                reached_older_items = True
                continue

            title = (item.get("title") or "").strip()
            # External teasers retain their canonical original URL; CQE stories
            # use their public CQE path.
            url = item.get("authored_url") or urljoin(SOURCE_URL, item.get("url", ""))
            if not title or not url:
                continue
            articles.append({
                "title": title,
                "url": url,
                "date": published.strftime("%Y-%m-%d"),
                "summary_en": (item.get("description") or "").strip()[:500],
                "source": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "category": "quantum",
            })

        if reached_older_items:
            break

    return articles


def main():
    try:
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 4
        articles = fetch_articles(days)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"{datetime.now():%Y-%m-%d}.json")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump({
                "source": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "crawled_at": datetime.now().isoformat(),
                "total_news": len(articles),
                "news": articles,
            }, handle, ensure_ascii=False, indent=2)
        print(f"[OK] {SOURCE_NAME}: {len(articles)} 篇文章")
        return 0
    except requests.RequestException as error:
        print(f"[ERROR] {SOURCE_NAME}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
