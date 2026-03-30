#!/usr/bin/env python3
"""
UW-Madison CDIS (School of Computer, Data & Information Sciences) 爬虫
从 https://cdis.wisc.edu/cdis-news/ 抓取最新新闻
筛选教育、AI、计算机科学相关文章
只抓取最近3天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

CDIS_URL = "https://cdis.wisc.edu/cdis-news/"
RAW_DIR = "data/raw/uw_cdis"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 18, 2026
        '%b %d, %Y',      # Mar 18, 2026
        '%Y-%m-%d',       # 2026-03-18
    ]
    
    # 清理翻译插件添加的内容
    date_str = re.sub(r'<font.*?</font>', '', date_str).strip()
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
        'ai_ml': ['artificial intelligence', 'AI', 'machine learning', 'deep learning'],
        'computer_science': ['computer science', 'software', 'programming', 'computing'],
        'data_science': ['data science', 'big data', 'analytics'],
        'education': ['education', 'student', 'graduate', 'alumni'],
        'research': ['research', 'study', 'discovery'],
        'career': ['career', 'job', 'industry', 'engineering']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_cdis():
    """从 UW-Madison CDIS 抓取最新新闻（最近3天）"""
    print("🚀 开始抓取 UW-Madison CDIS...")
    print(f"📡 网址: {CDIS_URL}")
    print(f"📅 只抓取最近3天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(CDIS_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章列表项
        article_items = soup.find_all('li', class_='uw-post')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h3')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                # 获取标题（移除翻译插件内容）
                title_full = link_elem.get_text(separator=' ', strip=True)
                title = re.sub(r'<font.*?</font>', '', title_full).strip()
                title = re.sub(r'[\u4e00-\u9fff]+', '', title).strip()  # 移除中文
                
                url = link_elem.get('href', '')
                
                # 摘要
                excerpt_elem = item.find('p', class_='uw-post-excerpt')
                summary_en = ""
                if excerpt_elem:
                    # 清理翻译插件内容
                    summary_full = excerpt_elem.get_text(separator=' ', strip=True)
                    summary_en = re.sub(r'<font.*?</font>', '', summary_full).strip()
                    summary_en = re.sub(r'[\u4e00-\u9fff]+', '', summary_en).strip()
                    summary_en = summary_en[:400]
                
                # 日期
                date_elem = item.find('span', class_='uw-post-date')
                date_str = ""
                if date_elem:
                    date_full = date_elem.get_text(strip=True)
                    date_str = re.sub(r'<font.*?</font>', '', date_full).strip()
                    date_str = re.sub(r'[\u4e00-\u9fff]+', '', date_str).strip()
                
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
                        'source': 'UW-Madison CDIS',
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
            'source': 'UW-Madison CDIS - School of Computer, Data & Information Sciences',
            'source_url': CDIS_URL,
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
    crawl_cdis()
