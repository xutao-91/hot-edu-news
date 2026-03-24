#!/usr/bin/env python3
"""
Brookings Institution Education 专题爬虫
从 https://www.brookings.edu/topics/education-2/ 抓取真实新闻
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

BROOKINGS_URL = "https://www.brookings.edu/topics/education-2/"

def parse_date(date_str):
    """解析日期字符串为datetime对象"""
    date_formats = [
        '%B %d, %Y',      # March 23, 2026
        '%b %d, %Y',      # Mar 23, 2026
        '%Y-%m-%d',       # 2026-03-23
        '%B %d, %Y',      # Updated: March 23, 2026
    ]
    
    # 清理字符串
    date_str = re.sub(r'Updated:\s*', '', date_str).strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=7):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        return True  # 如果解析失败，默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def crawl_brookings():
    """从 Brookings Education 抓取新闻（最近7天）"""
    print("🚀 开始抓取 Brookings Institution - Education...")
    print(f"📡 网址: {BROOKINGS_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(BROOKINGS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 使用正确的选择器
        article_items = soup.find_all('li', class_='ais-InfiniteHits-item')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items[:20]:  # 检查前20篇
            try:
                # 标题
                title_elem = item.find('span', class_='article-title') or item.find('span', class_='ais-Highlight-nonHighlighted')
                title = title_elem.get_text().strip() if title_elem else ''
                
                # 链接
                link_elem = item.find('a', class_='overlay-link')
                link = link_elem.get('href', '') if link_elem else ''
                
                # 作者
                author_elem = item.find('p', class_='byline')
                author = author_elem.get_text().strip() if author_elem else ''
                
                # 日期
                date_elem = item.find('p', class_='date')
                date = date_elem.get_text().strip() if date_elem else ''
                
                # 检查日期是否在7天内
                if not is_within_days(date, days=7):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过7天）: {title[:40]}... | {date}")
                    continue
                
                # 英文摘要
                summary_elem = item.find('span', class_='ais-Snippet-nonHighlighted')
                summary_en = summary_elem.get_text().strip()[:400] if summary_elem else ''
                
                if title and link:
                    articles.append({
                        'title': title,
                        'url': link,
                        'author': author,
                        'date': date,
                        'summary_en': summary_en,
                        'source': 'Brookings Institution',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:50]}...")
                    print(f"     👤 {author} | 📅 {date}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 如果没有从列表页获取到，尝试直接访问详情页获取
        if len(articles) == 0:
            print("⚠️  列表页未获取到数据，尝试直接访问文章...")
            articles = crawl_from_detail_pages()
        
        # 保存结果
        os.makedirs('data/brookings', exist_ok=True)
        
        output = {
            'source': 'Brookings Institution - Education',
            'source_url': BROOKINGS_URL,
            'crawled_at': datetime.now().isoformat(),
            'filter_days': 7,
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"data/brookings/{datetime.now().strftime('%Y-%m-%d')}.json"
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

def crawl_from_detail_pages():
    """从详情页抓取（备用方案）"""
    print("🔄 使用备用方案：从详情页抓取...")
    
    known_articles = [
        "https://www.brookings.edu/articles/survey-shows-alarming-drop-in-working-conditions-for-teachers-what-are-we-doing-about-it/",
        "https://www.brookings.edu/articles/chalk-courage-and-climate-change-how-educators-in-eastern-and-southern-africa-are-transforming-challenges-into-action/",
        "https://www.brookings.edu/articles/the-past-present-and-future-of-the-public-service-loan-forgiveness-program/",
        "https://www.brookings.edu/articles/tips-for-parents-raising-resilient-learners-in-an-ai-world/"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    articles = []
    
    for url in known_articles:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1').get_text().strip() if soup.find('h1') else ''
            
            author = ""
            author_elem = soup.find('a', class_='person-hover')
            if author_elem:
                author = author_elem.get_text().strip()
            
            date = ""
            date_elem = soup.find('p', class_='text-medium')
            if date_elem:
                date = date_elem.get_text().strip()
            
            # 检查日期
            if not is_within_days(date, days=7):
                print(f"  ⏭️  跳过（超过7天）: {title[:40]}...")
                continue
            
            if title:
                articles.append({
                    'title': title,
                    'url': url,
                    'author': author,
                    'date': date,
                    'source': 'Brookings Institution',
                    'category': categorize(title)
                })
                print(f"  ✅ {title[:50]}...")
                
        except Exception as e:
            print(f"  ⚠️  抓取失败: {e}")
            continue
    
    return articles

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'policy': ['policy', 'federal', 'legislation', 'government'],
        'higher_ed': ['college', 'university', 'higher education', 'student debt', 'loan'],
        'k12': ['k-12', 'school', 'teacher', 'elementary', 'secondary'],
        'teacher': ['teacher', 'educator', 'teaching'],
        'economy': ['economy', 'economic', 'workforce', 'labor'],
        'technology': ['technology', 'digital', 'online', 'ai', 'artificial intelligence'],
        'climate': ['climate', 'environment', 'sustainability']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

if __name__ == '__main__':
    crawl_brookings()
