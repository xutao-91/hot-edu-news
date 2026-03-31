#!/usr/bin/env python3
"""
Center for American Progress Education 爬虫
从 https://www.americanprogress.org/topic/education/ 抓取最新教育政策文章
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

CAP_URL = "https://www.americanprogress.org/topic/education/"
RAW_DIR = "data/raw/american_progress"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # February 5, 2026
        '%b %d, %Y',      # Feb 5, 2026
        '%Y-%m-%d',       # 2026-02-05
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
        'childcare': ['child care', 'childcare', 'families', 'low-income'],
        'policy': ['hhs', 'department', 'notice', 'comments'],
        'social': ['assistance', 'costs', 'providers'],
        'advocacy': ['opposing', 'roll back', 'progress']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_cap():
    """从 American Progress Education 抓取最新文章（最近4天）"""
    print("🚀 开始抓取 Center for American Progress Education...")
    print(f"📡 网址: {CAP_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(CAP_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - article.card2
        article_items = soup.find_all('article', class_='card2')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h4', class_='card2-title')
                if not title_elem:
                    continue
                
                # 查找标题文本
                title_span = title_elem.find('span', class_='-hs:1')
                if not title_span:
                    continue
                
                title = title_span.get_text(strip=True)
                
                # 链接 - from card2-link
                link_elem = item.find('a', class_='card2-link', href=True)
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # 日期 - from time tag in card2-meta
                date_str = ""
                time_elem = item.find('time', datetime=True)
                if time_elem:
                    iso_date = time_elem.get('datetime', '')
                    if iso_date:
                        date_str = iso_date[:10]  # Extract YYYY-MM-DD
                    else:
                        date_text = time_elem.get_text(strip=True)
                        try:
                            parsed = datetime.strptime(date_text, '%B %d, %Y')
                            date_str = parsed.strftime('%Y-%m-%d')
                        except:
                            date_str = date_text
                
                # 摘要 - from card2-excerpt
                summary_en = ""
                excerpt_elem = item.find('p', class_='card2-excerpt')
                if excerpt_elem:
                    summary_en = excerpt_elem.get_text(strip=True)[:400]
                
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
                        'type': 'Article',
                        'summary_en': summary_en,
                        'source': 'American Progress',
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
            'source': 'American Progress Education',
            'source_url': CAP_URL,
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
    crawl_cap()
