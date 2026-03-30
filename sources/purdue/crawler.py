#!/usr/bin/env python3
"""
Purdue University Newsroom 爬虫
从 https://www.purdue.edu/newsroom/articles/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

PURDUE_URL = "https://www.purdue.edu/newsroom/articles/?order=DESC&orderby=date&paged=1&custom_post_type=post"
RAW_DIR = "data/raw/purdue"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 30, 2026
        '%b %d, %Y',      # Mar 30, 2026
        '%Y-%m-%d',       # 2026-03-30
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
        'research': ['research', 'study', 'science', 'scholar'],
        'education': ['education', 'student', 'program'],
        'technology': ['technology', 'engineering', 'tech'],
        'partnership': ['agreement', 'partnership', 'collaboration'],
        'award': ['award', 'fellowship', 'scholar']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_purdue():
    """从 Purdue Newsroom 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Purdue University Newsroom...")
    print(f"📡 网址: {PURDUE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(PURDUE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章卡片
        article_items = soup.find_all('a', class_='purdue-home-cta-card--story')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题
                title_elem = item.find('p', class_='purdue-home-cta-grid__card-title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接
                url = item.get('href', '')
                
                # 日期
                date_elem = item.find('span', class_='purdue-date-tag')
                date_str = date_elem.get_text(strip=True) if date_elem else ''
                
                # 检查日期是否在4天内
                if date_str and not is_within_days(date_str, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过4天）: {title[:40]}... | {date_str}")
                    continue
                
                # 类型标签
                type_elem = item.find('span', class_='purdue-tax-tag')
                content_type = type_elem.get_text(strip=True) if type_elem else 'News'
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': content_type,
                        'summary_en': '',  # 列表页无摘要
                        'source': 'Purdue University',
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
            'source': 'Purdue University Newsroom',
            'source_url': PURDUE_URL,
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
    crawl_purdue()
