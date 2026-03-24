#!/usr/bin/env python3
"""
CSIS (战略与国际研究中心) 爬虫
从 https://www.csis.org/search 抓取教育相关文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

CSIS_URL = "https://www.csis.org/search?archive=0&sort_by=relevance&f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&f%5B2%5D=regions%3A801&keyword="

def crawl_csis():
    """从 CSIS 抓取文章"""
    print("🚀 开始抓取 CSIS (战略与国际研究中心)...")
    print(f"📡 网址: {CSIS_URL}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(CSIS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # 查找所有文章行
        article_rows = soup.find_all('div', class_='views-row')
        
        print(f"✅ 找到 {len(article_rows)} 篇文章")
        
        for row in article_rows[:10]:  # 取前10篇
            try:
                # 文章内部容器
                article_inner = row.find('article', class_='report-search-listing')
                if not article_inner:
                    continue
                
                # 标题
                title_elem = article_inner.find('h3', class_='headline-sm')
                if title_elem:
                    title_span = title_elem.find('span')
                    title = title_span.get_text().strip() if title_span else ''
                else:
                    title = ''
                
                # 链接
                link_elem = article_inner.find('a', class_='hocus-headline')
                link = ''
                if link_elem:
                    href = link_elem.get('href', '')
                    if href:
                        link = 'https://www.csis.org' + href if not href.startswith('http') else href
                
                # 摘要
                summary_elem = article_inner.find('div', class_='search-listing--summary')
                summary = ''
                if summary_elem:
                    p_elem = summary_elem.find('p')
                    if p_elem:
                        summary = p_elem.get_text().strip()
                
                # 作者
                author_elems = article_inner.find_all('span', class_='contributor--item')
                authors = [a.get_text().strip() for a in author_elems]
                author = ', '.join(authors) if authors else ''
                
                # 日期
                date = ''
                contributors_div = article_inner.find('div', class_='contributors')
                if contributors_div:
                    p_elem = contributors_div.find('p')
                    if p_elem:
                        text = p_elem.get_text()
                        # 提取日期格式: March 12, 2026
                        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text)
                        if date_match:
                            date = date_match.group(1)
                
                if title and link:
                    articles.append({
                        'title': title,
                        'url': link,
                        'author': author,
                        'date': date,
                        'summary_en': summary,
                        'source': 'CSIS',
                        'category': categorize(title)
                    })
                    print(f"\n  ✅ {title[:60]}...")
                    print(f"     👤 {author}")
                    print(f"     📅 {date}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        # 保存结果
        os.makedirs('data/csis', exist_ok=True)
        
        output = {
            'source': 'CSIS - Center for Strategic and International Studies',
            'source_url': CSIS_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"data/csis/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'china': ['china', 'chinese', 'beijing'],
        'technology': ['technology', 'tech', 'digital', 'ai', 'artificial intelligence'],
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
