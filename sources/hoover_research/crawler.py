#!/usr/bin/env python3
"""
Hoover Institution Education Research 爬虫
从 https://www.hoover.org/topic/education/ 抓取最新教育研究文章
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

HOOVER_URL = "https://www.hoover.org/topic/education/?research_type=Articles&research_type=Essays&research_type=News%2FPress&research_type=Working-Papers"
RAW_DIR = "data/raw/hoover_research"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
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
        'k12': ['school', 'k-12', 'local schools', 'education'],
        'policy': ['policy', 'reform', 'governance'],
        'research': ['research', 'study', 'survey', 'voices'],
        'commentary': ['commentary', 'essay', 'opinion']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_hoover():
    """从 Hoover Institution 抓取最新教育研究（最近4天）"""
    print("🚀 开始抓取 Hoover Institution Education Research...")
    print(f"📡 网址: {HOOVER_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(HOOVER_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - li.ais-Hits-item
        article_items = soup.find_all('li', class_='ais-Hits-item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题
                title_elem = item.find('h6')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接 - from "Read More" link
                link_elem = item.find('a', href=True, text='Read More')
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.hoover.org{href}"
                
                # 日期 - from span.date
                date_str = ""
                date_elem = item.find('span', class_='date')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    try:
                        parsed = datetime.strptime(date_text, '%B %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 摘要 - from p after h6
                summary_en = ""
                p_elem = item.find('p')
                if p_elem:
                    summary_en = p_elem.get_text(strip=True)[:400]
                
                # 类型 - from span.tag
                content_type = ""
                tag_elem = item.find('span', class_='tag')
                if tag_elem:
                    content_type = tag_elem.get_text(strip=True)
                
                # 作者 - from author-name
                author = ""
                author_elem = item.find('strong', class_='author-name')
                if author_elem:
                    author = author_elem.get_text(strip=True)
                
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
                        'type': content_type or 'Research',
                        'summary_en': summary_en,
                        'source': 'Hoover Research',
                        'category': categorize(title),
                        'author': author
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str}")
                    if author:
                        print(f"     👤 {author}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Hoover Institution Education Research',
            'source_url': HOOVER_URL,
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
    crawl_hoover()
