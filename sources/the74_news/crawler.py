#!/usr/bin/env python3
"""
The 74 Million News 爬虫
从 https://www.the74million.org/news/ 抓取最新教育新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

THE74_URL = "https://www.the74million.org/news/"
RAW_DIR = "data/raw/the74_news"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%m-%d-%Y',       # 3-27-2026
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
        'ai': ['ai', 'artificial intelligence', 'chatgpt'],
        'policy': ['guidelines', 'schools', 'nyc', 'releases'],
        'tech': ['technology', 'digital', 'computing'],
        'k12': ['schools', 'students', 'education']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_the74():
    """从 The 74 Million News 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 The 74 Million News...")
    print(f"📡 网址: {THE74_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(THE74_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - div.post.news
        article_items = soup.find_all('div', class_='post news')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 链接
                link_elem = item.find('a', href=True)
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # 标题 - from h3
                title_elem = item.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 日期 - from time tag
                date_str = ""
                time_elem = item.find('time', datetime=True)
                if time_elem:
                    date_attr = time_elem.get('datetime', '')
                    if date_attr:
                        try:
                            parsed = datetime.strptime(date_attr, '%m-%d-%Y')
                            date_str = parsed.strftime('%Y-%m-%d')
                        except:
                            date_str = date_attr
                
                # 作者 - from address.author
                author = ""
                author_elem = item.find('address', class_='author')
                if author_elem:
                    author = author_elem.get_text(strip=True)
                
                # 标签 - from post_tag
                tag = ""
                tag_elem = item.find('div', class_='post_tag')
                if tag_elem:
                    tag = tag_elem.get_text(strip=True)
                
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
                        'type': tag or 'News',
                        'summary_en': '',
                        'source': 'The 74 Million',
                        'category': categorize(title),
                        'author': author
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
            'source': 'The 74 Million News',
            'source_url': THE74_URL,
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
    crawl_the74()
