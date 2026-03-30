#!/usr/bin/env python3
"""
Kelley School of Business at IU 爬虫
从 https://kelley.iu.edu/news-events/index.html 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KELLEY_URL = "https://kelley.iu.edu/news-events/index.html"
RAW_DIR = "data/raw/kelley"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 27, 2026
        '%b %d, %Y',      # Mar 27, 2026
        '%Y-%m-%d',       # 2026-03-27
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
        'business': ['business', 'finance', 'management'],
        'career': ['internship', 'career', 'student'],
        'policy': ['policy', 'capitol', 'washington'],
        'research': ['research', 'study']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_kelley():
    """从 Kelley School of Business 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Kelley School of Business at IU...")
    print(f"📡 网址: {KELLEY_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(KELLEY_URL, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('li', class_='feed-item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('span', itemprop='headline')
                if not title_elem:
                    title_elem = item.find('p', class_='title')
                    if title_elem:
                        title_elem = title_elem.find('a')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接
                link_elem = item.find('a', itemprop='url')
                if not link_elem:
                    link_elem = item.find('p', class_='title')
                    if link_elem:
                        link_elem = link_elem.find('a')
                
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # 日期
                date_str = ""
                date_elem = item.find('p', class_='date')
                if date_elem:
                    iso_date = date_elem.get('content', '')
                    if iso_date:
                        date_str = iso_date
                    else:
                        date_str = date_elem.get_text(strip=True)
                
                # 摘要
                summary_elem = item.find('p', itemprop='description')
                summary_en = ""
                if summary_elem:
                    # 移除"Read more"链接
                    read_more = summary_elem.find('a')
                    if read_more:
                        read_more.decompose()
                    summary_en = summary_elem.get_text(strip=True)[:400]
                
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
                        'source': 'Kelley School of Business',
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
            'source': 'Kelley School of Business at IU',
            'source_url': KELLEY_URL,
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
    crawl_kelley()
