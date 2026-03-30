#!/usr/bin/env python3
"""
Heritage Foundation Education 爬虫
从 https://www.heritage.org/education 抓取最新报告
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

HERITAGE_URL = "https://www.heritage.org/education"
BASE_URL = "https://www.heritage.org"
RAW_DIR = "data/raw/heritage"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%b %d, %Y',      # Mar 26, 2026
        '%B %d, %Y',      # March 26, 2026
        '%Y-%m-%d',       # 2026-03-26
    ]
    
    # 清理字符串
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
        return True  # 解析失败默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'ai_technology': ['artificial intelligence', 'AI', 'technology', 'digital'],
        'higher_ed': ['college', 'university', 'higher education', 'campus'],
        'k12': ['k-12', 'school choice', 'charter school', 'homeschool'],
        'policy': ['policy', 'reform', 'legislation', 'federal'],
        'workforce': ['workforce', 'career', 'apprenticeship', 'job'],
        'parental_rights': ['parent', 'family', 'rights'],
        'curriculum': ['curriculum', 'academic', 'standards'],
        'federal_policy': ['department of education', 'federal', 'congress']
    }
    
    for cat, keywords in categories.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_heritage():
    """从 Heritage Foundation 抓取最新报告（最近7天）"""
    print("🚀 开始抓取 Heritage Foundation - Education...")
    print(f"📡 网址: {HERITAGE_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(HERITAGE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章行
        article_items = soup.find_all('div', class_='views-row')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 查找结果卡片
                card = item.find('section', class_='result-card')
                if not card:
                    continue
                
                # 标题和链接
                title_elem = card.find('a', class_='result-card__title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                href = title_elem.get('href', '')
                
                # 完整链接
                if href.startswith('/'):
                    url = BASE_URL + href
                else:
                    url = href
                
                # 类型/标签
                type_elem = card.find('p', class_='result-card__eyebrow')
                content_type = type_elem.get_text().strip() if type_elem else 'Article'
                
                # 日期
                date_elem = card.find('p', class_='result-card__date')
                date_str = ""
                if date_elem:
                    span_elem = date_elem.find('span')
                    if span_elem:
                        date_str = span_elem.get_text().strip()
                
                # 检查日期是否在7天内
                if date_str and not is_within_days(date_str, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date_str}")
                    continue
                
                # 阅读时间
                read_time = ""
                if date_elem:
                    date_text = date_elem.get_text()
                    read_match = re.search(r'(\d+)\s+min\s+read', date_text)
                    if read_match:
                        read_time = f"{read_match.group(1)} min"
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': content_type,
                        'read_time': read_time,
                        'source': 'Heritage Foundation',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str} | 📋 {content_type} | ⏱️ {read_time}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Heritage Foundation - Education',
            'source_url': HERITAGE_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻（最近7天）")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_heritage()
