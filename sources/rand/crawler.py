#!/usr/bin/env python3
"""
Rand Corporation 爬虫
从 https://www.rand.org/pubs.html 抓取教育相关报告
筛选主题：Teachers and Teaching, Students, Emerging Technologies, Artificial Intelligence
只抓取最近7天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

RAND_URL = "https://www.rand.org/pubs.html?realized_taxonomy_ss=Teachers+and+Teaching&realized_taxonomy_ss=Students&realized_taxonomy_ss=Emerging+Technologies&realized_taxonomy_ss=Artificial+Intelligence&rows=12"
BASE_URL = "https://www.rand.org"
RAW_DIR = "data/raw/rand"

def parse_date(date_str):
    """解析日期字符串"""
    date_formats = [
        '%b %d, %Y',      # Mar 27, 2026
        '%B %d, %Y',      # March 27, 2026
        '%Y-%m-%d',       # 2026-03-27
    ]
    
    date_str = date_str.strip()
    
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
        return True  # 解析失败默认保留
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title, doc_type):
    """自动分类"""
    title_lower = title.lower()
    type_lower = doc_type.lower()
    
    # 基于文档类型分类
    if 'research report' in type_lower:
        return 'research_report'
    elif 'commentary' in type_lower:
        return 'commentary'
    elif 'blog post' in type_lower:
        return 'blog_post'
    
    # 基于标题关键词分类
    categories = {
        'ai_technology': ['artificial intelligence', 'AI', 'technology', 'digital'],
        'teachers': ['teacher', 'teaching', 'instructional'],
        'students': ['student', 'k-12', 'school'],
        'stem': ['science', 'math', 'engineering', 'STEM'],
        'policy': ['policy', 'reform', 'legislation']
    }
    
    for cat, keywords in categories.items():
        if any(kw.lower() in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_rand():
    """从 Rand Corporation 抓取最新报告（最近7天）"""
    print("🚀 开始抓取 Rand Corporation...")
    print(f"📡 网址: {RAND_URL}")
    print(f"📅 只抓取最近7天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(RAND_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有列表项
        article_items = soup.find_all('li', {'data-relevancy': True})
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 链接
                link_elem = item.find('a', href=True)
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    url = BASE_URL + href
                else:
                    url = href
                
                # 标题
                title_elem = item.find('h3', class_='title')
                title = title_elem.get_text().strip() if title_elem else ''
                
                # 描述/摘要
                desc_elem = item.find('p', class_='desc')
                summary_en = desc_elem.get_text().strip() if desc_elem else ''
                
                # 类型
                type_elem = item.find('p', class_='type')
                doc_type = type_elem.get_text().strip() if type_elem else 'Publication'
                
                # 日期
                date_elem = item.find('p', class_='date')
                date_str = date_elem.get_text().strip() if date_elem else ''
                
                # 检查日期是否在7天内
                if date_str and not is_within_days(date_str, days=7):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过7天）: {title[:40]}... | {date_str}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': doc_type,
                        'summary_en': summary_en[:500],
                        'source': 'Rand Corporation',
                        'category': categorize(title, doc_type)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_str} | 📋 {doc_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在7天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Rand Corporation',
            'source_url': RAND_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
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
    crawl_rand()
