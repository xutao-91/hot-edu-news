#!/usr/bin/env python3
"""
ACE (American Council on Education) 新闻爬虫
从 https://www.acenet.edu/News-Room/Pages/default.aspx 抓取新闻
只抓取最近7天内的文章，排除播客
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

ACE_URL = "https://www.acenet.edu/News-Room/Pages/default.aspx?k=((ACETileType:%22News%22%20OR%20ACETileType:%22Statement%22%20OR%20ACETileType:%22Press%20Release%22))"
RAW_DIR = "data/raw/ace"

def parse_date(date_str):
    """解析日期字符串为datetime对象"""
    date_formats = [
        '%B %d, %Y',      # March 23, 2026
        '%b %d, %Y',      # Mar 23, 2026
        '%Y-%m-%d',       # 2026-03-23
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=4):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        return True  # 如果解析失败，默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def crawl_ace():
    """从ACE抓取新闻（最近7天）"""
    print("🚀 开始抓取 ACE (American Council on Education)...")
    print(f"📡 网址: {ACE_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(ACE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        podcast_count = 0
        
        # 查找所有文章卡片
        post_items = soup.find_all('div', class_='rollup-result')
        
        print(f"✅ 找到 {len(post_items)} 篇文章，开始过滤...")
        
        for post in post_items[:30]:  # 检查前30篇
            try:
                # 标题
                title_elem = post.find('div', class_='rollup-title')
                title = title_elem.get_text().strip() if title_elem else ''
                
                # 链接
                link = ""
                a_elem = post.find_parent('a') or post.find('a')
                if a_elem:
                    href = a_elem.get('href', '')
                    if href:
                        link = href if href.startswith('http') else f"https://www.acenet.edu{href}"
                
                # 日期
                date = ""
                date_elem = post.find('div', class_='rollup-date')
                if date_elem:
                    date = date_elem.get_text().strip()
                
                # 类型
                article_type = ""
                type_elem = post.find('div', class_='rollup-type')
                if type_elem:
                    article_type = type_elem.get_text().strip()
                
                # 过滤掉Podcast类型
                if article_type.lower() == 'podcast':
                    podcast_count += 1
                    print(f"  ⏭️  跳过Podcast: {title[:40]}...")
                    continue
                
                # 检查日期是否在7天内
                if not is_within_days(date, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date}")
                    continue
                
                # 摘要
                summary = ""
                desc_elem = post.find('div', class_='rollup-desc')
                if desc_elem:
                    summary = desc_elem.get_text().strip()
                
                if title and link:
                    articles.append({
                        'title': title,
                        'url': link,
                        'date': date,
                        'type': article_type,
                        'summary_en': summary,
                        'source': 'ACE',
                        'category': categorize(title)
                    })
                    print(f"\n  ✅ {title[:60]}...")
                    print(f"     📅 {date} | 📋 {article_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内")
        print(f"   跳过 {skipped_count} 篇（超过3天）")
        print(f"   跳过 {podcast_count} 篇（播客）")
        
        # 保存到 raw 目录
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'ACE - American Council on Education',
            'source_url': ACE_URL,
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

def categorize(title):
    """分类"""
    title_lower = title.lower()
    categories = {
        'federal_policy': ['federal', 'congress', 'legislation', 'policy', 'dea', 'certification'],
        'diversity': ['diversity', 'equity', 'inclusion', 'dei'],
        'higher_ed': ['higher education', 'college', 'university'],
        'student_aid': ['student aid', 'financial aid', 'loan', 'debt'],
        'international': ['international', 'global', 'foreign']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

if __name__ == '__main__':
    print("="*60)
    print("🚀 ACE爬虫启动（最近7天）")
    print("="*60)
    result = crawl_ace()
    if result:
        print("\n🎉 爬虫成功！")
    else:
        print("\n❌ 爬虫失败")
