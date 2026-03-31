#!/usr/bin/env python3
"""
EdSurge News 爬虫
从 https://www.edsurge.com/news 抓取最新教育科技新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

EDSURGE_URL = "https://www.edsurge.com/news"
RAW_DIR = "data/raw/edsurge_news"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%b %d',          # Mar 27
        '%B %d',          # March 27
        '%b %d, %Y',      # Mar 27, 2026
        '%B %d, %Y',      # March 27, 2026
        '%Y-%m-%d',       # 2026-03-27
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
        'ai': ['ai', 'artificial intelligence', 'chatgpt', 'generative'],
        'teaching': ['teachers', 'teaching', 'classroom', 'instruction'],
        'edtech': ['technology', 'digital', 'software', 'platform'],
        'research': ['research', 'study', 'commentary']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_edsurge():
    """从 EdSurge News 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 EdSurge News...")
    print(f"📡 网址: {EDSURGE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(EDSURGE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'lxml')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - a.js-feed-item
        article_items = soup.find_all('a', class_='js-feed-item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # URL
                href = item.get('href', '')
                if not href:
                    continue
                
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.edsurge.com{href}"
                
                # 标题 - from h4
                title_elem = item.find('h4')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 分类 - from first h6 (category)
                category = ""
                h6_elems = item.find_all('h6')
                if h6_elems:
                    # First h6 is usually the category
                    category_elem = h6_elems[0]
                    category = category_elem.get_text(strip=True)
                
                # 日期和作者 - from last h6
                date_str = ""
                author = ""
                if len(h6_elems) >= 2:
                    meta_elem = h6_elems[-1]
                    meta_text = meta_elem.get_text(strip=True)
                    
                    # Extract date and author
                    # Format: "Mar 27 · Mi Aniefuna" or "Mar 27"
                    if '·' in meta_text:
                        parts = meta_text.split('·')
                        date_str = parts[0].strip()
                        author = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        date_str = meta_text
                
                # Format date
                if date_str:
                    try:
                        # Add year if missing
                        if ',' not in date_str:
                            date_str_full = f"{date_str}, {datetime.now().year}"
                        else:
                            date_str_full = date_str
                        
                        parsed = datetime.strptime(date_str_full, '%b %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        pass
                
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
                        'summary_en': '',
                        'source': 'EdSurge',
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
            'source': 'EdSurge News',
            'source_url': EDSURGE_URL,
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
    crawl_edsurge()
