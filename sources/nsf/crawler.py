#!/usr/bin/env python3
"""
NSF (National Science Foundation) 爬虫
从 https://www.nsf.gov/news/releases 抓取最新新闻
筛选主题：AI、教育、STEM、研究
只抓取最近3天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

NSF_URL = "https://www.nsf.gov/news/releases"
BASE_URL = "https://www.nsf.gov/news/releases"
RAW_DIR = "data/raw/nsf"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 25, 2026
        '%b %d, %Y',      # Mar 25, 2026
        '%Y-%m-%d',       # 2026-03-25
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
        'ai_technology': ['artificial intelligence', 'AI', 'machine learning', 'tech'],
        'education': ['education', 'student', 'school', 'teacher', 'learning'],
        'stem': ['science', 'engineering', 'mathematics', 'STEM', 'research'],
        'workforce': ['workforce', 'worker', 'business', 'community'],
        'innovation': ['innovation', 'discovery', 'breakthrough']
    }
    
    for cat, keywords in categories.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_nsf():
    """从 NSF 抓取最新新闻（最近3天）"""
    print("🚀 开始抓取 NSF (National Science Foundation)...")
    print(f"📡 网址: {NSF_URL}")
    print(f"📅 只抓取最近3天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(NSF_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有新闻行
        article_items = soup.find_all('div', class_='views-row')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 查找teaser容器
                teaser = item.find('div', class_='latest-news-teaser')
                if not teaser:
                    continue
                
                # 标题和链接
                title_elem = teaser.find('span', class_='field--name-title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                
                # 链接
                link_elem = teaser.find('a', href=True)
                href = link_elem.get('href', '') if link_elem else ''
                
                # 完整链接
                if href.startswith('/'):
                    url = BASE_URL + href
                else:
                    url = href
                
                # 类型/标签
                type_elem = teaser.find('span', class_='latest-news-teaser__type')
                content_type = type_elem.get_text().strip() if type_elem else 'NSF News'
                
                # 摘要
                summary_elem = teaser.find('div', class_='field-news-body')
                summary_en = ""
                if summary_elem:
                    summary_en = summary_elem.get_text().strip()[:400]
                
                # 日期
                date_elem = teaser.find('time', class_='datetime')
                date_str = ""
                if date_elem:
                    # 从datetime属性获取
                    date_attr = date_elem.get('datetime', '')
                    if date_attr:
                        # 解析 ISO 格式日期
                        try:
                            dt = datetime.fromisoformat(date_attr.replace('Z', '+00:00'))
                            date_str = dt.strftime('%B %d, %Y')
                        except:
                            date_str = date_elem.get_text().strip()
                    else:
                        date_str = date_elem.get_text().strip()
                
                # 检查日期是否在3天内
                if date_str and not is_within_days(date_str, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date_str}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': content_type,
                        'summary_en': summary_en,
                        'source': 'NSF',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str} | 📋 {content_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在3天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'NSF - National Science Foundation',
            'source_url': NSF_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻（最近3天）")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_nsf()
