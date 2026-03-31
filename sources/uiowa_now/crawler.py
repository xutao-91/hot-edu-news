#!/usr/bin/env python3
"""
University of Iowa Now 爬虫
从 https://now.uiowa.edu/tags/featured-headlines 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

UIOWA_URL = "https://now.uiowa.edu/tags/featured-headlines"
RAW_DIR = "data/raw/uiowa_now"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%A, %B %d, %Y',  # Thursday, March 26, 2026
        '%B %d, %Y',      # March 26, 2026
        '%b %d, %Y',      # Mar 26, 2026
        '%Y-%m-%d',       # 2026-03-26
    ]
    
    date_str = date_str.strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=4):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        return True
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'leadership': ['president', 'ceo', 'named', 'appointed'],
        'advancement': ['advancement', 'development', 'fundraising'],
        'academic': ['academic', 'faculty', 'professor'],
        'students': ['student', 'graduate', 'undergraduate']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_uiowa():
    """从 UIowa Now 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 University of Iowa Now...")
    print(f"📡 网址: {UIOWA_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(UIOWA_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - div.views-row
        article_items = soup.find_all('div', class_='views-row')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题
                title_elem = item.find('span', class_='headline__heading')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接
                link_elem = item.find('a', class_='click-target', href=True)
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # 日期
                date_str = ""
                date_elem = item.find('div', class_='card__subtitle')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    try:
                        parsed = datetime.strptime(date_text, '%A, %B %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 摘要
                summary_elem = item.find('div', class_='field--name-body')
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
                # 检查日期是否在4天内
                if date_str and not is_within_days(date_str, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过4天）: {title[:40]}... | {date_str}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': 'News',
                        'summary_en': summary_en,
                        'source': 'UIowa Now',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'University of Iowa Now',
            'source_url': UIOWA_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻（最近4天）")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_uiowa()
