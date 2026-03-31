#!/usr/bin/env python3
"""
Show Me Mizzou (University of Missouri) 爬虫
从 https://showme.missouri.edu/archive/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MIZZOU_URL = "https://showme.missouri.edu/archive/"
RAW_DIR = "data/raw/showme_mizzou"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
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
        'research': ['research', 'study', 'discover', 'scientific', 'fish', 'species'],
        'science': ['science', 'genetic', 'biology', 'miracle'],
        'academic': ['academic', 'faculty', 'professor'],
        'students': ['student', 'graduate', 'undergraduate']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_mizzou():
    """从 Show Me Mizzou 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Show Me Mizzou...")
    print(f"📡 网址: {MIZZOU_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MIZZOU_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - a.miz-linked-card
        article_items = soup.find_all('a', class_='miz-linked-card')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 链接
                url = item.get('href', '')
                if not url:
                    continue
                
                # 标题
                title_elem = item.find('h2', class_='miz-card__title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 日期
                date_str = ""
                date_elem = item.find('p', class_='miz-news--date')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    try:
                        parsed = datetime.strptime(date_text, '%B %d, %Y')
                        date_str = parsed.strftime('%Y-%m-%d')
                    except:
                        date_str = date_text
                
                # 摘要
                summary_elem = item.find('p', class_='miz-card__text')
                summary_en = ""
                if summary_elem:
                    # 排除日期段落
                    if 'miz-news--date' not in summary_elem.get('class', []):
                        summary_en = summary_elem.get_text(strip=True)[:400]
                    else:
                        # 找下一个p标签
                        all_p = item.find_all('p', class_='miz-card__text')
                        for p in all_p:
                            if 'miz-news--date' not in p.get('class', []):
                                summary_en = p.get_text(strip=True)[:400]
                                break
                
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
                        'source': 'Show Me Mizzou',
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
            'source': 'Show Me Mizzou',
            'source_url': MIZZOU_URL,
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
    crawl_mizzou()
