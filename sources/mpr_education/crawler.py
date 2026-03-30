#!/usr/bin/env python3
"""
MPR Education 爬虫
从 https://www.mprnews.org/education 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MPR_URL = "https://www.mprnews.org/education"
RAW_DIR = "data/raw/mpr_education"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y %I:%M %p',      # March 25, 2026 3:10 PM
        '%B %d, %Y',               # March 25, 2026
        '%b %d, %Y',               # Mar 25, 2026
        '%Y-%m-%d',                # 2026-03-25
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
        'safety': ['shoot', 'threat', 'crime', 'police', 'gun'],
        'higher_ed': ['student', 'university', 'college', 'fraternity'],
        'k12': ['school', 'teacher', 'district'],
        'policy': ['policy', 'legislation', 'law']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_mpr_education():
    """从 MPR Education 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 MPR Education...")
    print(f"📡 网址: {MPR_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MPR_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - article.teaser
        article_items = soup.find_all('article', class_='teaser')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h2', class_='hdg-2')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find_parent('a', href=True)
                if not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.mprnews.org{href}"
                
                # 日期 - 从time标签获取
                date_str = ""
                time_elem = item.find('time')
                if time_elem:
                    iso_date = time_elem.get('datetime', '')
                    if iso_date:
                        # 解析 ISO 格式 2026-03-25T15:10:00-05:00
                        match = re.search(r'(\d{4}-\d{2}-\d{2})', iso_date)
                        if match:
                            date_str = match.group(1)
                    else:
                        date_str = time_elem.get_text(strip=True)
                
                # 摘要
                summary_elem = item.find('div', class_='teaser_body')
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
                # 作者
                author_elem = item.find('div', class_='teaser_contributors')
                author = ""
                if author_elem:
                    author_link = author_elem.find('a')
                    if author_link:
                        author = author_link.get_text(strip=True)
                
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
                        'author': author,
                        'source': 'MPR News',
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
            'source': 'MPR Education',
            'source_url': MPR_URL,
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
    crawl_mpr_education()
