#!/usr/bin/env python3
"""
NSF NCSES (National Center for Science and Engineering Statistics) 爬虫
从 https://ncses.nsf.gov/rss 抓取最新报告
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

RSS_URL = "https://ncses.nsf.gov/rss"
BASE_URL = "https://ncses.nsf.gov"
RAW_DIR = "data/raw/nsf_ncses"

def parse_date(date_str):
    """解析RSS日期格式"""
    # RSS日期格式: Tue, 17 Mar 2026 09:37:34 EDT
    try:
        # 移除时区信息
        date_str = re.sub(r'\s+(EDT|EST|UTC|GMT)[\s]*$', '', date_str.strip())
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
    except:
        pass
    
    # 尝试其他格式
    formats = [
        '%B %d, %Y',      # March 17, 2026
        '%b %d, %Y',      # Mar 17, 2026
        '%Y-%m-%d',       # 2026-03-17
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=3):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        return True  # 如果解析失败，默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'funding': ['funding', 'federal support', 'obligations', 'appropriations', 'budget'],
        'research': ['research', 'development', 'r&d', 'experimental'],
        'higher_ed': ['higher education', 'universities', 'colleges', 'academic', 'institutions'],
        'workforce': ['workforce', 'employment', 'personnel', 'scientists', 'engineers', 'postdoc', 'graduate'],
        'international': ['international', 'global', 'foreign', 'collaboration'],
        'innovation': ['innovation', 'patents', 'technology', 'commercialization'],
        'demographics': ['demographics', 'gender', 'race', 'ethnicity', 'diversity'],
        'stem_education': ['education', 'students', 'degrees', 'graduates', 'phd', 'doctorate', 'stem'],
        'data_update': ['data update', 'patterns']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_ncses():
    """从 NSF NCSES RSS Feed 抓取最新报告（最近7天）"""
    print("🚀 开始抓取 NSF NCSES - National Center for Science and Engineering Statistics...")
    print(f"📡 RSS Feed: {RSS_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ RSS获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'xml')
        articles = []
        skipped_count = 0
        
        # 查找所有item
        items = soup.find_all('item')
        
        print(f"✅ 找到 {len(items)} 篇文章，开始过滤...")
        
        for item in items:
            try:
                # 标题
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # 链接
                link_elem = item.find('link')
                url = link_elem.get_text(strip=True) if link_elem else ''
                
                # 描述/摘要
                desc_elem = item.find('description')
                summary_en = desc_elem.get_text(strip=True) if desc_elem else ''
                
                # 日期
                date_elem = item.find('publishDate')
                date_str = ""
                if date_elem:
                    date_str = date_elem.get_text(strip=True)
                
                # 检查日期是否在7天内
                if date_str and not is_within_days(date_str, days=3):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date_str}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': 'Report',
                        'summary_en': summary_en[:500],  # 限制长度
                        'source': 'NSF NCSES',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 保存到 raw 目录
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'NSF NCSES - National Center for Science and Engineering Statistics',
            'source_url': RSS_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 原始数据已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_ncses()
