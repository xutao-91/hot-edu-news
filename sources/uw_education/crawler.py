#!/usr/bin/env python3
"""
UW-Madison School of Education 爬虫
从 https://education.wisc.edu/category/school-news/ 抓取最新新闻
只抓取最近3天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

UW_EDU_URL = "https://education.wisc.edu/category/school-news/"
RAW_DIR = "data/raw/uw_education"

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

def is_within_days(date_str, days=3):
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
        'theatre_drama': ['theatre', 'drama', 'performance'],
        'teacher_education': ['teacher', 'teaching', 'education'],
        'awards': ['award', 'honor', 'recognition'],
        'research': ['research', 'study'],
        'student': ['student', 'graduate'],
        'faculty': ['faculty', 'professor']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_uw_education():
    """从 UW-Madison School of Education 抓取最新新闻（最近3天）"""
    print("🚀 开始抓取 UW-Madison School of Education...")
    print(f"📡 网址: {UW_EDU_URL}")
    print(f"📅 只抓取最近3天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(UW_EDU_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('article', class_='news')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h2', class_='entry-title')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 日期 - 在entry-content的第一个p标签中
                date_elem = item.find('div', class_='entry-content')
                date_str = ""
                if date_elem:
                    first_p = date_elem.find('p')
                    if first_p:
                        date_text = first_p.get_text(strip=True)
                        # 匹配日期格式
                        date_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', date_text)
                        if date_match:
                            date_str = date_match.group(1)
                
                # 摘要
                excerpt_elem = item.find('div', class_='entry-content')
                summary_en = ""
                if excerpt_elem:
                    # 获取所有p标签文本
                    p_tags = excerpt_elem.find_all('p')
                    if len(p_tags) > 1:
                        summary_en = p_tags[1].get_text(strip=True)[:400]
                
                # 检查日期是否在3天内
                if date_str and not is_within_days(date_str, days=3):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {date_str}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': 'News',
                        'summary_en': summary_en,
                        'source': 'UW-Madison School of Education',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在3天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'UW-Madison School of Education',
            'source_url': UW_EDU_URL,
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
    crawl_uw_education()
