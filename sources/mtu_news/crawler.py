#!/usr/bin/env python3
"""
Michigan Technological University News 爬虫
从 https://www.mtu.edu/news/archives/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MTU_URL = "https://www.mtu.edu/news/archives/"
RAW_DIR = "data/raw/mtu_news"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 20, 2026
        '%b %d, %Y',      # Mar 20, 2026
        '%Y-%m-%d',       # 2026-03-20
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
        'student_life': ['student', 'husky', 'extracurricular', 'broomball'],
        'academic': ['accounting', 'coursework', 'education'],
        'sports': ['broomball', 'sports', 'season'],
        'research': ['research', 'study', 'discovery']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_mtu():
    """从 MTU News 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Michigan Technological University News...")
    print(f"📡 网址: {MTU_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MTU_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - article inside div.text-stories
        story_divs = soup.find_all('div', class_='text-stories')
        
        print(f"✅ 找到 {len(story_divs)} 个文章区块，开始过滤...")
        
        for story_div in story_divs:
            try:
                # 查找文章
                article = story_div.find('article')
                if not article:
                    continue
                
                # 日期 - 从time标签获取
                date_str = ""
                date_elem = article.find('time')
                if date_elem:
                    iso_date = date_elem.get('datetime', '')
                    if iso_date:
                        match = re.search(r'(\d{4}-\d{2}-\d{2})', iso_date)
                        if match:
                            date_str = match.group(1)
                    else:
                        date_text = date_elem.get_text(strip=True)
                        try:
                            parsed = datetime.strptime(date_text, '%B %d, %Y')
                            date_str = parsed.strftime('%Y-%m-%d')
                        except:
                            date_str = date_text
                
                # 标题和链接
                title_elem = article.find('h2')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 摘要
                summary_elem = article.find('p')
                summary_en = ""
                if summary_elem:
                    # 移除"Read More"链接
                    for a in summary_elem.find_all('a', class_='yellow'):
                        a.decompose()
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
                        'type': 'News',
                        'summary_en': summary_en,
                        'source': 'MTU News',
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
            'source': 'Michigan Technological University News',
            'source_url': MTU_URL,
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
    crawl_mtu()
