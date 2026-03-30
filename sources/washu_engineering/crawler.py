#!/usr/bin/env python3
"""
Washington University McKelvey Engineering 爬虫
从 https://engineering.washu.edu/news/index.html 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

WASHU_ENG_URL = "https://engineering.washu.edu/news/index.html"
RAW_DIR = "data/raw/washu_engineering"

def parse_date(date_str):
    """解析日期字符串"""
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

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'administration': ['executive', 'director', 'finance', 'budget', 'administration'],
        'faculty': ['faculty', 'professor', 'researcher'],
        'research': ['research', 'study', 'discovery'],
        'students': ['student', 'graduate', 'undergraduate']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_washu_engineering():
    """从 WashU McKelvey Engineering 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 WashU McKelvey Engineering...")
    print(f"📡 网址: {WASHU_ENG_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(WASHU_ENG_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - article.news__teaser
        article_items = soup.find_all('article', class_='news__teaser')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题
                title_elem = item.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接
                link_elem = item.find('a', class_='news__teaser-header', href=True)
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if href.startswith('http'):
                    url = href
                else:
                    # 相对路径，需要拼接
                    url = f"https://engineering.washu.edu/news/{href}"
                
                # 日期 - 转换为标准格式
                date_elem = item.find('time', class_='news__date')
                raw_date = date_elem.get_text(strip=True) if date_elem else ''
                
                # 将 MM.DD.YYYY 转换为 YYYY-MM-DD
                date_str = ""
                if raw_date:
                    try:
                        parsed = datetime.strptime(raw_date, '%m.%d.%Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = raw_date
                
                # 摘要
                summary_elem = item.find('p', class_='news__teaser-desc')
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
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
                        'source': 'WashU McKelvey Engineering',
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
            'source': 'WashU McKelvey Engineering',
            'source_url': WASHU_ENG_URL,
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
    crawl_washu_engineering()
