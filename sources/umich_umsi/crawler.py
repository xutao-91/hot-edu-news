#!/usr/bin/env python3
"""
University of Michigan School of Information (UMSI) 爬虫
从 https://www.si.umich.edu/about-umsi/news 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

UMSI_URL = "https://www.si.umich.edu/about-umsi/news"
RAW_DIR = "data/raw/umich_umsi"

def parse_date(date_str):
    """解析日期字符串"""
    # UMSI格式: 03/30/2026
    date_formats = [
        '%m/%d/%Y',       # 03/30/2026
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
        'ai': ['ai', 'artificial intelligence', 'machine learning'],
        'technology': ['technology', 'tech', 'digital'],
        'ethics': ['ethics', 'choice', 'doomed', 'human'],
        'research': ['professor', 'research', 'study']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_umsi():
    """从 UMSI 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 University of Michigan School of Information (UMSI)...")
    print(f"📡 网址: {UMSI_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        response = requests.get(UMSI_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章
        article_items = soup.find_all('div', class_='item-teaser-news')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 标题和链接
                link_elem = item.find('a', href=True)
                if not link_elem:
                    continue
                
                # 构建完整URL
                href = link_elem.get('href', '')
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.si.umich.edu{href}"
                
                # 标题
                title_elem = item.find('h2')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 日期 - 在details div中
                details = item.find('div', class_='item-teaser--details')
                date_str = ""
                if details:
                    # 查找所有文本，日期通常是第二个元素（在h2之后）
                    texts = [t.strip() for t in details.stripped_strings]
                    for t in texts:
                        if re.match(r'\d{2}/\d{2}/\d{4}', t):
                            date_str = t
                            break
                
                # 摘要
                summary_elem = item.find('p')
                summary_en = summary_elem.get_text(strip=True)[:400] if summary_elem else ''
                
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
                        'source': 'UMSI',
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
            'source': 'University of Michigan School of Information (UMSI)',
            'source_url': UMSI_URL,
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
    crawl_umsi()
