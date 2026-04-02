#!/usr/bin/env python3
"""
Brookings Institution Education 专题爬虫
抓取原始英文数据，保存到 data/raw/brookings/
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

BROOKINGS_URL = "https://www.brookings.edu/topics/education-2/"
RAW_DIR = "data/raw/brookings"

def parse_date(date_str):
    date_formats = ['%B %d, %Y', '%b %d, %Y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=4):
    article_date = parse_date(date_str)
    if not article_date:
        return True
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    title_lower = title.lower()
    categories = {
        'policy': ['policy', 'federal', 'legislation', 'government', 'state policies'],
        'higher_ed': ['college', 'university', 'higher education', 'student debt', 'loan', 'bachelor', 'community college', "master's degree"],
        'k12': ['k-12', 'school', 'teacher', 'elementary', 'secondary', 'young children', 'early childhood'],
        'teacher': ['teacher', 'educator', 'teaching'],
        'economy': ['economy', 'economic', 'workforce', 'labor', 'earn', 'income', 'graduate', 'employment'],
        'technology': ['technology', 'digital', 'online', 'ai', 'artificial intelligence', 'generation ai'],
        'immigration': ['immigrant', 'migration', 'refugee'],
        'climate': ['climate', 'environment', 'sustainability']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

def crawl_brookings():
    print("🚀 开始抓取 Brookings Institution - Education...")
    print(f"📡 网址: {BROOKINGS_URL}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(BROOKINGS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # 方法1: 查找 article 标签
        article_items = soup.find_all('article', class_='article')
        print(f"✅ 找到 {len(article_items)} 个 article 标签")
        
        # 方法2: 查找所有包含 /articles/ 的链接
        if len(article_items) == 0:
            all_links = soup.find_all('a', href=lambda x: x and '/articles/' in x)
            print(f"✅ 找到 {len(all_links)} 个文章链接")
            
            # 去重
            seen_urls = set()
            for link in all_links[:20]:
                try:
                    url = link.get('href', '')
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # 获取标题
                    title = link.get_text().strip()
                    if not title:
                        # 尝试从父元素获取标题
                        parent = link.find_parent('article') or link.find_parent('div', class_='article')
                        if parent:
                            title_elem = parent.find('h2') or parent.find('h3') or parent.find('span', class_='article-title')
                            if title_elem:
                                title = title_elem.get_text().strip()
                    
                    if title and len(title) > 10:
                        print(f"  📰 {title[:60]}...")
                        
                        articles.append({
                            'title': title,
                            'url': url if url.startswith('http') else f"https://www.brookings.edu{url}",
                            'author': '',
                            'date': '',
                            'summary_en': '',
                            'source': 'Brookings Institution',
                            'category': categorize(title)
                        })
                        print(f"     ✅ 已添加")
                except Exception as e:
                    continue
        else:
            # 使用 article 标签解析
            for article in article_items[:20]:
                try:
                    # 获取链接
                    link_elem = article.find('a', href=lambda x: x and '/articles/' in x)
                    link = link_elem['href'] if link_elem else ''
                    
                    # 获取标题
                    title_elem = article.find('span', class_='ais-Highlight-nonHighlighted') or \
                                article.find('span', class_='article-title') or \
                                article.find('h2') or \
                                article.find('h3')
                    title = title_elem.get_text().strip() if title_elem else ''
                    
                    # 获取作者
                    author_elem = article.find('p', class_='byline')
                    author = author_elem.get_text().strip() if author_elem else ''
                    
                    # 获取日期
                    date_elem = article.find('p', class_='date')
                    date = date_elem.get_text().strip() if date_elem else ''
                    
                    # 获取摘要
                    summary_elem = article.find('span', class_='ais-Snippet-nonHighlighted')
                    summary_en = summary_elem.get_text().strip()[:500] if summary_elem else ''
                    
                    if title and link:
                        print(f"  📰 {title[:60]}...")
                        print(f"     📅 {date}")
                        
                        # 检查日期
                        if date and not is_within_days(date, days=4):
                            print(f"     ⏭️  跳过（超过4天）")
                            continue
                        
                        articles.append({
                            'title': title,
                            'url': link if link.startswith('http') else f"https://www.brookings.edu{link}",
                            'author': author,
                            'date': date,
                            'summary_en': summary_en,
                            'source': 'Brookings Institution',
                            'category': categorize(title)
                        })
                        print(f"     ✅ 已添加")
                except Exception as e:
                    continue
        
        # 如果还没有数据，尝试从已知文章列表获取
        if len(articles) == 0:
            print("⚠️  尝试备用方案...")
            articles = crawl_from_detail_pages()
        
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
    """从已知文章列表抓取（备用方案）"""
    known_articles = [
        {
            'url': "https://www.brookings.edu/articles/what-are-community-college-bachelors-degrees-and-how-much-do-their-graduates-earn/",
            'title': "What are community college bachelor's degrees and how much do their graduates earn?",
            'date': "March 31, 2026"
        },
        {
            'url': "https://www.brookings.edu/articles/generation-ai-starts-early-a-guide-to-technologies-already-shaping-young-childrens-lives/",
            'title': "Generation AI starts early: A guide to technologies already shaping young children's lives",
            'date': "March 30, 2026"
        },
        {
            'url': "https://www.brookings.edu/articles/federal-and-state-policies-targeting-immigrant-children-at-school-erode-decades-of-progress-in-education-access/",
            'title': "Federal and state policies targeting immigrant children at school erode decades of progress in education access",
            'date': "March 27, 2026"
        }
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    articles = []
    
    for item in known_articles:
        try:
            url = item['url']
            title = item['title']
            date = item['date']
            
            # 检查日期是否在4天内
            if date and not is_within_days(date, days=4):
                print(f"  ⏭️  跳过（超过4天）: {title[:50]}...")
                continue
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取作者
            author = ""
            author_elem = soup.find('a', class_='person-hover')
            if author_elem:
                author = author_elem.get_text().strip()
            
            # 获取摘要（从meta description）
            summary_en = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                summary_en = meta_desc.get('content', '')[:500]
            
            articles.append({
                'title': title,
                'url': url,
                'author': author,
                'date': date,
                'summary_en': summary_en,
                'source': 'Brookings Institution',
                'category': categorize(title)
            })
            print(f"  ✅ {title[:60]}...")
        except Exception as e:
            print(f"  ⚠️  错误: {e}")
            continue
    
    return articles

if __name__ == '__main__':
    crawl_brookings()
