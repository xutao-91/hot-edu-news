#!/usr/bin/env python3
"""
NCSES (National Center for Science and Engineering Statistics) 爬虫
从 https://ncses.nsf.gov/search?query=&excludePubAssets=true&pageSize=40&sort=date 抓取最新博士统计数据
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

NCSES_URL = "https://ncses.nsf.gov/search?query=&excludePubAssets=true&pageSize=40&sort=date"
RAW_DIR = "data/raw/ncses_data"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 13, 2026
        '%b %d, %Y',      # Mar 13, 2026
        '%Y-%m-%d',       # 2026-03-13
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
        'doctorate': ['doctorate', 'phd', 'doctoral'],
        'data': ['survey', 'statistics', 'data'],
        'university': ['university', 'graduate'],
        'report': ['report', 'analysis']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_ncses():
    """从 NCSES 抓取最新报告（最近4天）"""
    print("🚀 开始抓取 NCSES Data...")
    print(f"📡 网址: {NCSES_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(NCSES_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有结果 - li.result
        article_items = soup.find_all('li', class_='result')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h4', class_='result-title')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://ncses.nsf.gov{href}"
                
                # 日期 - from li.result-published-date
                date_str = ""
                date_elem = item.find('li', class_='result-published-date')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    try:
                        parsed = datetime.strptime(date_text, '%B %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 摘要 - from p.result-description span
                summary_en = ""
                desc_elem = item.find('p', class_='result-description')
                if desc_elem:
                    span_elem = desc_elem.find('span')
                    if span_elem:
                        summary_en = span_elem.get_text(strip=True)[:400]
                
                # 内容类型 - from p.result-content-type
                content_type = ""
                type_elem = item.find('p', class_='result-content-type')
                if type_elem:
                    content_type = type_elem.get_text(strip=True)
                
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
                        'type': content_type or 'Report',
                        'summary_en': summary_en,
                        'source': 'NCSES Data',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str}")
                    print(f"     📝 {content_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'NCSES (National Center for Science and Engineering Statistics)',
            'source_url': NCSES_URL,
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
    crawl_ncses()
