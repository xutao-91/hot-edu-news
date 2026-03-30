#!/usr/bin/env python3
"""
University of Michigan Ford School of Public Policy 爬虫
从 https://fordschool.umich.edu/news 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

FORD_URL = "https://fordschool.umich.edu/news"
RAW_DIR = "data/raw/umich_ford"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
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
        'policy': ['policy', 'public policy', 'government'],
        'tax': ['tax', 'reporting', 'fiscal'],
        'research': ['project', 'research', 'study'],
        'faculty': ['professor', 'faculty', 'moynihan']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_ford():
    """从 Ford School 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 University of Michigan Ford School of Public Policy...")
    print(f"📡 网址: {FORD_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(FORD_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('article', class_='teaser')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h2', class_='teaser__title')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title_span = link_elem.find('span')
                if not title_span:
                    continue
                
                title = title_span.get_text(strip=True)
                
                # 构建完整URL
                href = link_elem.get('href', '')
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://fordschool.umich.edu{href}"
                
                # 日期
                date_str = ""
                date_elem = item.find('span', class_='teaser__date')
                if date_elem:
                    date_span = date_elem.find('span')
                    if date_span:
                        date_str = date_span.get_text(strip=True)
                
                # 摘要
                summary_elem = item.find('div', class_='teaser__desc')
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
                # 标签
                label_elem = item.find('span', class_='teaser__label')
                content_type = label_elem.get_text(strip=True) if label_elem else 'News'
                
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
                        'type': content_type,
                        'summary_en': summary_en,
                        'source': 'Ford School at UMich',
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
            'source': 'University of Michigan Ford School of Public Policy',
            'source_url': FORD_URL,
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
    crawl_ford()
