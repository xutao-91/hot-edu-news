#!/usr/bin/env python3
"""
Brookings Institution Education 专题爬虫
只抓取与关键词相关的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

BROOKINGS_URL = "https://www.brookings.edu/topics/education-2/"
RAW_DIR = "data/raw/brookings"

# 关键词列表
KEYWORDS = [
    # 英文关键词
    'education', 'educational', 'talent', 'AI', 'STEM', 'university', 'universities',
    'higher education', 'college', 'colleges', 'Chinese', 'China', 'artificial intelligence',
    'training', 'cultivate', 'innovate', 'innovation', 'innovative', 'teacher', 'teachers',
    'faculty', 'apprentice', 'apprenticeship', 'curriculum', 'teaching', 'school', 'schools',
    'quantum', 'workforce', 'student', 'students', 'learning', 'academic', 'research',
    'scholar', 'scholarship', 'degree', 'graduate', 'graduation', 'enrollment',
    # 中文关键词（如果原文有中文）
    '教育', '人才', '大学', '高校', '中国', '人工智能', '培养', '创新', '教师', '师资',
    '学徒', '课程', '教学', '学校', '量子'
]

def parse_date(date_str):
    date_formats = ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=7):
    article_date = parse_date(date_str)
    if not article_date:
        return True
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def matches_keywords(text):
    """检查文本是否包含关键词"""
    if not text:
        return False
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def categorize(title):
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

def crawl_brookings():
    print("🚀 开始抓取 Brookings Institution - Education...")
    print(f"📡 网址: {BROOKINGS_URL}")
    print(f"🔍 关键词过滤: {', '.join(KEYWORDS[:10])}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(BROOKINGS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        filtered_count = 0
        
        # 尝试从列表页获取
        article_items = soup.find_all('li', class_='ais-InfiniteHits-item')
        print(f"✅ 找到 {len(article_items)} 篇文章，开始关键词过滤...")
        
        for item in article_items[:20]:
            try:
                title_elem = item.find('span', class_='article-title') or item.find('span', class_='ais-Highlight-nonHighlighted')
                title = title_elem.get_text().strip() if title_elem else ''
                
                # 关键词过滤
                if not matches_keywords(title):
                    filtered_count += 1
                    print(f"  ⏭️  跳过（无关键词）: {title[:50]}...")
                    continue
                
                link_elem = item.find('a', class_='overlay-link')
                link = link_elem.get('href', '') if link_elem else ''
                
                author_elem = item.find('p', class_='byline')
                author = author_elem.get_text().strip() if author_elem else ''
                
                date_elem = item.find('p', class_='date')
                date = date_elem.get_text().strip() if date_elem else ''
                
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
                    print(f"  ✅ {title[:60]}...")
                    
            except Exception as e:
                continue
        
        # 如果列表页没有，使用备用方案
        if len(articles) == 0:
            print("⚠️  列表页未获取到数据，使用备用URL...")
            articles = crawl_from_detail_pages()
        
        print(f"\n📊 过滤结果: {len(articles)} 篇匹配关键词，跳过 {filtered_count} 篇")
        
        # 保存原始数据
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Brookings Institution - Education',
            'source_url': BROOKINGS_URL,
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

def crawl_from_detail_pages():
    """从详情页抓取（备用方案）"""
    known_articles = [
        "https://www.brookings.edu/articles/survey-shows-alarming-drop-in-working-conditions-for-teachers-what-are-we-doing-about-it/",
        "https://www.brookings.edu/articles/chalk-courage-and-climate-change-how-educators-in-eastern-and-southern-africa-are-transforming-challenges-into-action/",
        "https://www.brookings.edu/articles/the-past-present-and-future-of-the-public-service-loan-forgiveness-program/"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    articles = []
    
    for url in known_articles:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('h1').get_text().strip() if soup.find('h1') else ''
            
            # 关键词过滤
            if not matches_keywords(title):
                print(f"  ⏭️  跳过（无关键词）: {title[:50]}...")
                continue
            
            author = ""
            author_elem = soup.find('a', class_='person-hover')
            if author_elem:
                author = author_elem.get_text().strip()
            
            date = ""
            date_elem = soup.find('p', class_='text-medium')
            if date_elem:
                date = date_elem.get_text().strip()
            
            if title:
                articles.append({
                    'title': title,
                    'url': url,
                    'author': author,
                    'date': date,
                    'source': 'Brookings Institution',
                    'category': categorize(title)
                })
        except Exception as e:
            continue
    
    return articles

if __name__ == '__main__':
    crawl_brookings()
