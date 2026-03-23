#!/usr/bin/env python3
"""
Education Week 专用爬虫
只从 edweek.org 抓取真实新闻
"""
import json
import feedparser
import requests
from datetime import datetime, timedelta
import os

# Education Week RSS源
EDWEEK_RSS = "https://www.edweek.org/feeds/rss.xml"

def crawl_edweek():
    """从Education Week RSS抓取新闻"""
    print("🚀 开始抓取 Education Week...")
    print(f"📡 RSS源: {EDWEEK_RSS}")
    
    try:
        # 解析RSS
        feed = feedparser.parse(EDWEEK_RSS)
        
        print(f"✅ RSS解析成功，共 {len(feed.entries)} 条")
        
        news_list = []
        for entry in feed.entries[:10]:  # 取前10条
            # 提取日期
            date_str = entry.get('published', entry.get('updated', ''))
            
            # 检查是否是最近7天的
            if not is_recent(date_str):
                continue
            
            news_item = {
                "title": entry.title,
                "url": entry.link,
                "published": date_str,
                "source": "Education Week",
                "summary": entry.get('summary', '')[:500],
                "author": entry.get('author', ''),
                "category": categorize(entry.title)
            }
            
            news_list.append(news_item)
            print(f"  ✅ {entry.title[:60]}...")
        
        # 保存结果
        output = {
            "source": "Education Week",
            "source_url": "https://www.edweek.org",
            "crawled_at": datetime.now().isoformat(),
            "total_news": len(news_list),
            "news": news_list
        }
        
        # 确保目录存在
        os.makedirs('data/edweek', exist_ok=True)
        
        # 按日期保存
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'data/edweek/{date_str}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(news_list)} 条新闻")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def is_recent(date_str, days=7):
    """检查日期是否在最近N天内"""
    try:
        from dateutil import parser
        date = parser.parse(date_str)
        delta = datetime.now() - date
        return delta.days <= days
    except:
        return True  # 解析失败默认保留

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    if any(kw in title_lower for kw in ['federal', 'department of education', 'congress']):
        return 'federal'
    elif any(kw in title_lower for kw in ['teacher', 'teaching', 'educator']):
        return 'teaching'
    elif any(kw in title_lower for kw in ['technology', 'digital', 'online']):
        return 'technology'
    elif any(kw in title_lower for kw in ['assessment', 'testing', 'standardized']):
        return 'assessment'
    else:
        return 'general'

if __name__ == '__main__':
    crawl_edweek()
