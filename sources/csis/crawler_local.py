#!/usr/bin/env python3
"""
CSIS 本地爬虫 - 简化可靠版本
使用requests + 维护URL列表
每天从多渠道获取新文章URL
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

# 多渠道获取CSIS文章URL
CSIS_URL_SOURCES = {
    # 1. 已知的教育相关文章（手动维护）
    'manual': [
        "https://www.csis.org/analysis/chinas-solar-industry-upheaval-effects-will-be-global",
        # 可以添加更多...
    ],
    
    # 2. 从CSIS主题页面获取（可能有RSS或列表）
    'topic_pages': [
        "https://www.csis.org/programs/education",
        "https://www.csis.org/research/technology-policy",
    ]
}

def fetch_article_detail(url):
    """获取单篇文章详情"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 标题
        title = soup.find('h1').get_text().strip() if soup.find('h1') else ''
        
        # 作者 - 清理去重
        authors = []
        seen = set()
        for elem in soup.find_all(['span', 'a'], class_=lambda x: x and 'contributor' in str(x).lower()):
            text = elem.get_text().strip()
            if text and text not in seen and len(text) < 50 and text not in ['and', 'by']:
                # 过滤掉职位信息
                if not any(x in text.lower() for x in ['senior', 'director', 'fellow', 'professor']):
                    authors.append(text)
                    seen.add(text)
        author = ', '.join(authors[:3])
        
        # 日期
        date = ""
        text_content = soup.get_text()
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text_content)
        if date_match:
            date = date_match.group(1)
        
        # 英文摘要
        summary = ""
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            summary = desc.get('content', '')
        
        if title:
            return {
                'title': title,
                'url': url,
                'author': author,
                'date': date,
                'summary_en': summary,
                'source': 'CSIS',
                'category': categorize(title)
            }
    except Exception as e:
        print(f"  ❌ {url}: {e}")
    
    return None

def crawl_csis():
    """主爬虫函数"""
    print("="*60)
    print("🚀 CSIS本地爬虫启动")
    print("="*60)
    
    articles = []
    urls_to_fetch = []
    
    # 1. 添加手动维护的URL
    urls_to_fetch.extend(CSIS_URL_SOURCES['manual'])
    
    # 2. 尝试从主题页面发现新URL（简化版，实际可能需要更复杂的解析）
    # 这里暂时跳过，依赖手动维护
    
    print(f"📋 待抓取URL列表: {len(urls_to_fetch)} 个")
    
    # 抓取每篇文章
    for url in urls_to_fetch:
        print(f"\n📰 抓取: {url.split('/')[-1][:50]}...")
        article = fetch_article_detail(url)
        if article:
            articles.append(article)
            print(f"  ✅ {article['title'][:50]}...")
            print(f"  👤 {article['author']}")
            print(f"  📅 {article['date']}")
    
    # 保存
    if articles:
        save_articles(articles)
    else:
        print("\n⚠️  未获取到任何文章")
    
    return articles

def save_articles(articles):
    """保存文章"""
    os.makedirs('data/csis', exist_ok=True)
    
    output = {
        'source': 'CSIS - Center for Strategic and International Studies',
        'source_url': 'https://www.csis.org',
        'crawled_at': datetime.now().isoformat(),
        'crawl_method': 'local_requests',
        'total_news': len(articles),
        'news': articles
    }
    
    filename = f"data/csis/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 已保存: {filename}")
    print(f"📊 共 {len(articles)} 条新闻")

def categorize(title):
    """分类"""
    title_lower = title.lower()
    categories = {
        'china': ['china', 'chinese', 'beijing'],
        'technology': ['technology', 'tech', 'digital', 'ai'],
        'energy': ['energy', 'solar', 'climate', 'environment'],
        'security': ['security', 'defense', 'military'],
        'economy': ['economy', 'economic', 'trade', 'market']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

if __name__ == '__main__':
    crawl_csis()
