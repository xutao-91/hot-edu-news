#!/usr/bin/env python3
"""
Milwaukee School of Engineering (MSOE) 爬虫
从 https://www.msoe.edu/about-msoe/news/1/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MSOE_URL = "https://www.msoe.edu/about-msoe/news/1/"
RAW_DIR = "data/raw/msoe"

def parse_date(date_str):
    """解析日期字符串"""
    # MSOE日期格式: 03.30.2026
    date_formats = [
        '%m.%d.%Y',       # 03.30.2026
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

def categorize(title, label):
    """自动分类"""
    title_lower = title.lower()
    label_lower = label.lower() if label else ''
    
    categories = {
        'faculty': ['faculty', 'staff', 'professor', 'president', 'vp'],
        'academic': ['academic', 'academics', 'education'],
        'leadership': ['executive', 'leadership', 'appointed', 'named'],
        'announcement': ['names', 'announces', 'new']
    }
    
    # 首先检查label
    if 'faculty' in label_lower or 'staff' in label_lower:
        return 'faculty'
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_msoe():
    """从 MSOE 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Milwaukee School of Engineering (MSOE)...")
    print(f"📡 网址: {MSOE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MSOE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('article', class_='news_list_item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标签/分类
                label_elem = item.find('span', class_='news_list_item_label')
                label = label_elem.get_text(strip=True) if label_elem else ''
                
                # 日期 - 转换为标准格式
                date_elem = item.find('time', class_='news_list_item_date')
                raw_date = date_elem.get_text(strip=True) if date_elem else ''
                
                # 将 MM.DD.YYYY 转换为 YYYY-MM-DD
                date_str = ""
                if raw_date:
                    try:
                        parsed = datetime.strptime(raw_date, '%m.%d.%Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = raw_date
                
                # 标题和链接
                title_elem = item.find('span', class_='news_list_item_title_label')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                link_elem = item.find('a', class_='news_list_item_title_link')
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
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
                        'type': label if label else 'News',
                        'summary_en': '',  # 列表页无摘要
                        'source': 'MSOE',
                        'category': categorize(title, label)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str} | 📋 {label}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Milwaukee School of Engineering (MSOE)',
            'source_url': MSOE_URL,
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
    crawl_msoe()
