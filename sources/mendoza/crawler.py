#!/usr/bin/env python3
"""
Mendoza College of Business at Notre Dame 爬虫
从 https://mendoza.nd.edu/news/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MENDOZA_URL = "https://mendoza.nd.edu/news/"
RAW_DIR = "data/raw/mendoza"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 29, 2026
        '%b %d, %Y',      # Mar 29, 2026
        '%Y-%m-%d',       # 2026-03-29
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
        'business': ['business', 'management', 'operations'],
        'social_impact': ['water', 'africa', 'communities', 'ngo'],
        'research': ['study', 'research', 'models'],
        'global': ['global', 'international', 'rural']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_mendoza():
    """从 Mendoza College of Business 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Mendoza College of Business at Notre Dame...")
    print(f"📡 网址: {MENDOZA_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MENDOZA_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('li', class_='listing__item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 日期
                date_elem = item.find('div', class_='listing__date')
                date_str = date_elem.get_text(strip=True) if date_elem else ''
                
                # 标题和链接
                link_elem = item.find('a', class_='feed__link')
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 摘要
                summary_elem = item.find('p', class_='p-small')
                summary_en = ""
                if summary_elem:
                    # 移除 <strong> 标签
                    strong_elem = summary_elem.find('strong')
                    if strong_elem:
                        strong_elem.decompose()
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
                        'source': 'Mendoza College of Business',
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
            'source': 'Mendoza College of Business at Notre Dame',
            'source_url': MENDOZA_URL,
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
    crawl_mendoza()
