#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

# 配置
BASE_URL = "https://www.hanoverresearch.com/reports-and-briefs/"
SOURCE_NAME = "hanover_research"
DAYS_TO_FETCH = 4
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/raw/hanover_research/")

def fetch_articles():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    articles = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 通用文章抓取逻辑，你可以根据页面结构调整选择器
        for item in soup.select("article, .post, .news-item, .story"):
            try:
                title_elem = item.select_one("h1, h2, h3, .title, .headline")
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                link_elem = item.select_one("a")
                if not link_elem or not link_elem.get("href"):
                    continue
                url = link_elem.get("href")
                if not url.startswith("http"):
                    url = BASE_URL.rstrip("/") + "/" + url.lstrip("/")
                
                date_elem = item.select_one("time, .date, .published")
                date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime("%B %d, %Y")
                
                summary_elem = item.select_one("p, .excerpt, .summary")
                summary = summary_elem.get_text(strip=True) if summary_elem else ""
                
                articles.append({
                    "title": title,
                    "url": url,
                    "date": date_str,
                    "summary": summary,
                    "source": SOURCE_NAME,
                    "crawled_at": datetime.now().isoformat()
                })
            except Exception as e:
                continue
                
        # 保存结果
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join(OUTPUT_DIR, f"{today}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "source": SOURCE_NAME,
                "source_url": BASE_URL,
                "crawled_at": datetime.now().isoformat(),
                "total_news": len(articles),
                "news": articles
            }, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 抓取到 {len(articles)} 篇文章")
        return 0
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return 1

if __name__ == "__main__":
    exit(fetch_articles())
