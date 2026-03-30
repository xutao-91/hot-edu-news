#!/usr/bin/env python3
"""
Student Life (WashU student newspaper) 爬虫
从 https://www.studlife.com/news 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

STUDLIFE_URL = "https://www.studlife.com/news"
RAW_DIR = "data/raw/studlife"

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
        'ai': ['ai', 'artificial intelligence'],
        'technology': ['technology', 'digital'],
        'campus': ['washu', 'campus', 'student'],
        'event': ['talk', 'week', 'event']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_studlife():
    """从 Student Life 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Student Life (WashU)...")
    print(f"📡 网址: {STUDLIFE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(STUDLIFE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - div.article-box
        article_items = soup.find_all('div', class_='article-box')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h1', class_='article-headline')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find_parent('a', href=True)
                if not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 日期 - 从time标签获取
                date_str = ""
                time_elem = item.find('time')
                if time_elem:
                    iso_date = time_elem.get('datetime', '')
                    if iso_date:
                        match = re.search(r'(\d{4}-\d{2}-\d{2})', iso_date)
                        if match:
                            date_str = match.group(1)
                    else:
                        date_text = time_elem.get_text(strip=True)
                        try:
                            parsed = datetime.strptime(date_text, '%B %d, %Y')
                            date_str = parsed.strftime('%Y-%m-%d')
                        except:
                            date_str = date_text
                
                # 摘要
                summary_elem = item.find('div', class_='article-excerpt')
                summary_en = ""
                if summary_elem:
                    p_elem = summary_elem.find('p')
                    if p_elem:
                        summary_en = p_elem.get_text(strip=True)[:400]
                
                # 作者
                author_elem = item.find('span', class_='author-name')
                author = ""
                if author_elem:
                    authors = author_elem.find_all('a', class_='author')
                    author = ', '.join([a.get_text(strip=True) for a in authors])
                
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
                        'source': 'Student Life',
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
            'source': 'Student Life (WashU)',
            'source_url': STUDLIFE_URL,
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
    crawl_studlife()
