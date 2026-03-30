#!/usr/bin/env python3
"""
White House 新闻爬虫
从 https://www.whitehouse.gov/news/ 抓取新闻
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

WHITEHOUSE_URL = "https://www.whitehouse.gov/news/"
RAW_DIR = "data/raw/whitehouse"

def parse_date(date_str):
    """解析日期字符串为datetime对象"""
    date_formats = [
        '%B %d, %Y',      # March 23, 2026
        '%b %d, %Y',      # Mar 23, 2026
        '%Y-%m-%d',       # 2026-03-23
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=4):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        return True  # 如果解析失败，默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def crawl_whitehouse():
    """从White House抓取新闻（最近7天）"""
    print("🚀 开始抓取 White House...")
    print(f"📡 网址: {WHITEHOUSE_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(WHITEHOUSE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - li.wp-block-post
        posts = soup.find_all('li', class_='wp-block-post')
        
        print(f"✅ 找到 {len(posts)} 篇文章，开始过滤...")
        
        for post in posts[:20]:  # 检查前20篇
            try:
                # 标题和链接
                title_elem = post.find('h2', class_='wp-block-post-title')
                if title_elem:
                    link_elem = title_elem.find('a')
                    title = link_elem.get_text().strip() if link_elem else ''
                    href = link_elem.get('href', '') if link_elem else ''
                    link = href if href.startswith('http') else f"https://www.whitehouse.gov{href}"
                else:
                    title = ''
                    link = ''
                
                # 日期
                date = ""
                date_elem = post.find('div', class_='wp-block-post-date')
                if date_elem:
                    time_elem = date_elem.find('time')
                    if time_elem:
                        date = time_elem.get_text().strip()
                
                # 检查日期是否在7天内
                if not is_within_days(date, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date}")
                    continue
                
                # 分类
                category = ""
                cat_elem = post.find('div', class_='wp-block-post-terms')
                if cat_elem:
                    cat_link = cat_elem.find('a')
                    if cat_link:
                        category = cat_link.get_text().strip()
                
                if title and link:
                    articles.append({
                        'title': title,
                        'url': link,
                        'date': date,
                        'category': category,
                        'source': 'The White House'
                    })
                    print(f"\n  ✅ {title[:60]}...")
                    print(f"     📅 {date} | 📋 {category}")
                    
            except Exception as e:
                print(f"  ⚠️  解析失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 保存到 raw 目录
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'The White House',
            'source_url': WHITEHOUSE_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 原始数据已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def categorize(title):
    """分类"""
    title_lower = title.lower()
    categories = {
        'education': ['education', 'school', 'student', 'teacher'],
        'economy': ['economy', 'economic', 'jobs', 'trade'],
        'foreign_policy': ['foreign', 'international', 'china', 'russia'],
        'health': ['health', 'medical', 'covid'],
        'immigration': ['immigration', 'border']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

if __name__ == '__main__':
    print("="*60)
    print("🚀 White House爬虫启动（最近7天）")
    print("="*60)
    result = crawl_whitehouse()
    if result:
        print("\n🎉 爬虫成功！")
    else:
        print("\n❌ 爬虫失败")
