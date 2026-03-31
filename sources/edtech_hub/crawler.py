#!/usr/bin/env python3
"""
EdTech Innovation Hub 爬虫
从 https://www.edtechinnovationhub.com/ 抓取最新教育科技新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

EDTECH_HUB_URL = "https://www.edtechinnovationhub.com/"
RAW_DIR = "data/raw/edtech_hub"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%d/%m/%Y',       # 31/03/2026 (DD/MM/YYYY)
        '%B %d, %Y',      # March 31, 2026
        '%b %d, %Y',      # Mar 31, 2026
        '%Y-%m-%d',       # 2026-03-31
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
        'ai': ['ai', 'artificial intelligence', 'machine learning'],
        'innovation': ['innovation', 'new model', 'breakthrough'],
        'higher_ed': ['university', 'college', 'higher education', 'degree'],
        'policy': ['granted', 'powers', 'accreditation']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_edtech_hub():
    """从 EdTech Innovation Hub 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 EdTech Innovation Hub...")
    print(f"📡 网址: {EDTECH_HUB_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        }
        response = requests.get(EDTECH_HUB_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'lxml')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - article.blog-basic-grid--container
        article_items = soup.find_all('article', class_='blog-basic-grid--container')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题
                title_elem = item.find('h1', class_='blog-title')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.edtechinnovationhub.com{href}"
                
                # 日期 - from time.blog-date
                date_str = ""
                date_elem = item.find('time', class_='blog-date')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # Format: 31/03/2026 (DD/MM/YYYY)
                    try:
                        parsed = datetime.strptime(date_text, '%d/%m/%Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 分类 - from blog-categories
                categories = []
                cat_elems = item.find_all('a', class_='blog-categories')
                for cat in cat_elems:
                    cat_text = cat.get_text(strip=True)
                    if cat_text and cat_text not in categories:
                        categories.append(cat_text)
                
                # 作者 - from blog-author
                author = ""
                author_elem = item.find('span', class_='blog-author')
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
                        'type': ', '.join(categories) if categories else 'News',
                        'summary_en': '',
                        'source': 'EdTech Innovation Hub',
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
            'source': 'EdTech Innovation Hub',
            'source_url': EDTECH_HUB_URL,
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
    crawl_edtech_hub()
