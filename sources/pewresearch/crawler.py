#!/usr/bin/env python3
"""
Pew Research Center 爬虫
从 https://www.pewresearch.org/publications/ 抓取最新研究
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

PEW_URL = "https://www.pewresearch.org/publications/"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%B %d, %Y',      # March 25, 2026
        '%b %d, %Y',      # Mar 25, 2026
        '%Y-%m-%d',       # 2026-03-25
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def is_within_days(date_str, days=7):
    """检查日期是否在指定天数内"""
    article_date = parse_date(date_str)
    if not article_date:
        # 尝试从datetime属性解析
        try:
            article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00').replace('+00:00', ''))
            cutoff_date = datetime.now() - timedelta(days=days)
            return article_date >= cutoff_date
        except:
            return True  # 解析失败默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def extract_categories(li_class):
    """从li的class中提取分类"""
    categories = []
    if 'category-' in li_class:
        matches = re.findall(r'category-([a-z0-9-]+)', li_class)
        categories = [c.replace('-', ' ').title() for c in matches]
    return categories

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'education': ['education', 'school', 'student', 'teacher', 'learning'],
        'technology': ['technology', 'internet', 'digital', 'social media', 'ai', 'automation'],
        'science': ['science', 'research', 'stem'],
        'workforce': ['work', 'employment', 'job', 'labor', 'economy', 'wage'],
        'demographics': ['demographics', 'population', 'generation', 'age', 'gender', 'race'],
        'international': ['international', 'global', 'world', 'country', 'nation'],
        'politics': ['politics', 'policy', 'government', 'election'],
        'religion': ['religion', 'religious', 'faith'],
        'social_trends': ['social', 'trends', 'attitudes', 'opinion'],
        'marriage_family': ['marriage', 'family', 'parent', 'child']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_pewresearch():
    """从 Pew Research Center 抓取最新研究（最近7天）"""
    print("🚀 开始抓取 Pew Research Center...")
    print(f"📡 网址: {PEW_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(PEW_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章项
        article_items = soup.find_all('li', class_='wp-block-post')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 获取li的class中的分类信息
                li_class = item.get('class', [])
                li_class_str = ' '.join(li_class)
                
                # 查找article
                article_elem = item.find('article', class_='wp-block-prc-block-story-item')
                if not article_elem:
                    continue
                
                # 标题
                title_elem = article_elem.find('h2', class_='header')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a')
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                url = link_elem.get('href', '')
                
                # 日期
                date_elem = article_elem.find('time', class_='date')
                date_str = ""
                if date_elem:
                    # 优先使用datetime属性
                    date_str = date_elem.get('datetime', '')
                    if not date_str:
                        date_str = date_elem.get_text(strip=True)
                
                # 描述/摘要
                desc_elem = article_elem.find('div', class_='description')
                summary_en = ""
                if desc_elem:
                    p_elem = desc_elem.find('p')
                    if p_elem:
                        summary_en = p_elem.get_text(strip=True)
                
                # 类型标签
                type_elem = article_elem.find('span', class_='label')
                content_type = type_elem.get_text(strip=True) if type_elem else ''
                
                # 检查日期是否在7天内
                if not is_within_days(date_str, days=7):
                    skipped_count += 1
                    display_date = date_elem.get_text(strip=True) if date_elem else date_str
                    print(f"  ⏭️  跳过（超过7天）: {title[:40]}... | {display_date}")
                    continue
                
                # 提取分类
                categories = extract_categories(li_class_str)
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_elem.get_text(strip=True) if date_elem else date_str,
                        'type': content_type,
                        'categories': categories,
                        'summary_en': summary_en[:400],
                        'source': 'Pew Research Center',
                        'category': categorize(title)
                    })
                    display_date = date_elem.get_text(strip=True) if date_elem else date_str
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {display_date} | 📋 {content_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs('data/pewresearch', exist_ok=True)
        
        output = {
            'source': 'Pew Research Center',
            'source_url': PEW_URL,
            'crawled_at': datetime.now().isoformat(),
            'filter_days': 7,
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"data/pewresearch/{datetime.now().strftime('%Y-%m-%d')}.json"
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

if __name__ == '__main__':
    crawl_pewresearch()
