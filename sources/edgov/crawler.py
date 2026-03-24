#!/usr/bin/env python3
"""
美国教育部 (ED.gov) 新闻爬虫
从 https://www.ed.gov/about/news 抓取新闻发布
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

EDGOV_URL = "https://www.ed.gov/about/news"

def crawl_edgov():
    """从ED.gov抓取新闻"""
    print("🚀 开始抓取 U.S. Department of Education...")
    print(f"📡 网址: {EDGOV_URL}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(EDGOV_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # 查找所有新闻行
        rows = soup.find_all('div', class_='views-row')
        print(f"✅ 找到 {len(rows)} 篇新闻")
        
        for row in rows[:10]:  # 取前10篇
            try:
                # 类型 (Press Release / Blog / etc.)
                type_elem = row.find('div', class_='views-field-type')
                article_type = type_elem.get_text().strip() if type_elem else ''
                
                # 标题和链接
                title_elem = row.find('div', class_='views-field-title')
                if title_elem:
                    link_elem = title_elem.find('a')
                    title = link_elem.get_text().strip() if link_elem else ''
                    href = link_elem.get('href', '') if link_elem else ''
                    link = f"https://www.ed.gov{href}" if href.startswith('/') else href
                else:
                    title = ''
                    link = ''
                
                # 日期
                date = ""
                date_elem = row.find('time')
                if date_elem:
                    date = date_elem.get_text().strip()
                
                if title and link:
                    articles.append({
                        'title': title,
                        'url': link,
                        'date': date,
                        'type': article_type,
                        'source': 'U.S. Department of Education',
                        'category': categorize(title)
                    })
                    print(f"\n  ✅ {title[:60]}...")
                    print(f"     📅 {date} | 📋 {article_type}")
                    
            except Exception as e:
                print(f"  ⚠️  解析失败: {e}")
                continue
        
        # 保存
        os.makedirs('data/edgov', exist_ok=True)
        
        output = {
            'source': 'U.S. Department of Education',
            'source_url': EDGOV_URL,
            'crawled_at': datetime.now().isoformat(),
            'crawl_method': 'requests',
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"data/edgov/{datetime.now().strftime('%Y-%m-%d')}.json"
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
    """分类"""
    title_lower = title.lower()
    categories = {
        'civil_rights': ['civil rights', 'title ix', 'discrimination', 'disabilities'],
        'higher_ed': ['higher education', 'college', 'university', 'student loan', 'financial aid'],
        'k12': ['k-12', 'elementary', 'secondary', 'school'],
        'grants': ['grant', 'funding', 'partnership'],
        'civics': ['civics', 'history', 'education rocks']
    }
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    return 'general'

if __name__ == '__main__':
    print("="*60)
    print("🚀 ED.gov爬虫启动")
    print("="*60)
    result = crawl_edgov()
    if result:
        print("\n🎉 爬虫成功！")
    else:
        print("\n❌ 爬虫失败")
