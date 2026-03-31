#!/usr/bin/env python3
"""
The PIE News 爬虫
从 https://thepienews.com/category/news/ 抓取最新国际教育新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

PIE_URL = "https://thepienews.com/category/news/"
RAW_DIR = "data/raw/pie_news"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%b %d',          # Mar 30
        '%B %d',          # March 30
        '%b %d, %Y',      # Mar 30, 2026
        '%B %d, %Y',      # March 30, 2026
        '%Y-%m-%d',       # 2026-03-30
    ]
    
    date_str = date_str.strip()
    
    # Add current year if not present
    if date_str and ',' not in date_str and len(date_str.split()) == 2:
        date_str = f"{date_str}, {datetime.now().year}"
    
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
        'immigration': ['visa', 'immigration', 'f-1', 'f1'],
        'international': ['international', 'global', 'overseas'],
        'us': ['us', 'usa', 'america'],
        'students': ['students', 'colleges', 'universities']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_pie():
    """从 The PIE News 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 The PIE News...")
    print(f"📡 网址: {PIE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(PIE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'lxml')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - div.card-1
        article_items = soup.find_all('div', class_='card-1')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 链接和标题
                link_elem = item.find('a', href=True, title=True)
                if not link_elem:
                    continue
                
                url = link_elem.get('href', '')
                
                # Get title from h6 inside title div
                title_div = item.find('div', class_='title')
                if not title_div:
                    continue
                
                h6_elem = title_div.find('h6')
                if not h6_elem:
                    continue
                
                title = h6_elem.get_text(strip=True)
                
                # 日期 - from span with border-l border-orange
                date_str = ""
                date_elem = item.find('span', class_=lambda x: x and 'border-l' in x and 'border-orange' in x)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # Format: "Mar 30"
                    try:
                        if ',' not in date_text:
                            date_text_full = f"{date_text}, {datetime.now().year}"
                        else:
                            date_text_full = date_text
                        
                        parsed = datetime.strptime(date_text_full, '%b %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 分类 - from Immigration link
                category = ""
                cat_elem = item.find('a', href=lambda x: x and '/category/' in x)
                if cat_elem:
                    category = cat_elem.get_text(strip=True)
                
                # 作者 - from byline
                author = ""
                author_elem = item.find('span', class_='font-bold text-black')
                if author_elem:
                    author = author_elem.get_text(strip=True)
                
                # 摘要 - from line-clamp-3 div
                summary_en = ""
                summary_elem = item.find('div', class_=lambda x: x and 'line-clamp-3' in str(x))
                if summary_elem:
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
                        'type': category or 'News',
                        'summary_en': summary_en,
                        'source': 'The PIE News',
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
            'source': 'The PIE News',
            'source_url': PIE_URL,
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
    crawl_pie()
