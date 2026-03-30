#!/usr/bin/env python3
"""
Mlive Education 爬虫
从 https://www.mlive.com/education/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

MLIVE_URL = "https://www.mlive.com/education/"
RAW_DIR = "data/raw/mlive_education"

def parse_relative_time(time_text):
    """解析相对时间格式如 '2h ago', '1d ago'"""
    time_text = time_text.lower().strip()
    now = datetime.now()
    
    # 匹配 "Xh ago" (小时前)
    match = re.match(r'(\d+)h ago', time_text)
    if match:
        hours = int(match.group(1))
        return now - timedelta(hours=hours)
    
    # 匹配 "Xd ago" (天前)
    match = re.match(r'(\d+)d ago', time_text)
    if match:
        days = int(match.group(1))
        return now - timedelta(days=days)
    
    # 匹配 "Xm ago" (分钟前)
    match = re.match(r'(\d+)m ago', time_text)
    if match:
        minutes = int(match.group(1))
        return now - timedelta(minutes=minutes)
    
    # 标准日期格式
    date_formats = [
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y-%m-%d',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(time_text, fmt)
        except:
            continue
    
    return None

def is_within_days(time_text, days=4):
    """检查时间是否在指定天数内"""
    article_date = parse_relative_time(time_text)
    if not article_date:
        return True  # 无法解析时默认包含
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'local': ['ann arbor', 'michigan', 'community'],
        'education': ['education', 'college', 'school', 'student'],
        'policy': ['tax', 'dda', 'policy', 'expansion'],
        'finance': ['revenue', 'tax-capture', 'financial']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_mlive():
    """从 Mlive Education 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Mlive Education...")
    print(f"📡 网址: {MLIVE_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(MLIVE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('li', class_='river-item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                title_elem = item.find('h2')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a', href=True)
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 摘要
                summary_elem = item.find('p', class_=re.compile(r'_paragraph_'))
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
                # 时间
                time_elem = item.find('time')
                time_text = time_elem.get_text(strip=True) if time_elem else ''
                
                # 作者
                author_elem = item.find('a', href=re.compile(r'/staff/'))
                author = author_elem.get_text(strip=True) if author_elem else ''
                
                # 检查日期是否在4天内
                if time_text and not is_within_days(time_text, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过4天）: {title[:40]}... | {time_text}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': time_text,
                        'type': 'News',
                        'summary_en': summary_en,
                        'author': author,
                        'source': 'Mlive Education',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {time_text}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Mlive Education',
            'source_url': MLIVE_URL,
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
    crawl_mlive()
