#!/usr/bin/env python3
"""
Brookings Institution Education 专题爬虫
从 https://www.brookings.edu/topics/education-2/ 抓取真实新闻
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import time

# Brookings Education URL
BROOKINGS_URL = "https://www.brookings.edu/topics/education-2/"

def crawl_brookings():
    """从 Brookings Education 抓取新闻"""
    print("🚀 开始抓取 Brookings Institution - Education...")
    print(f"📡 网址: {BROOKINGS_URL}")
    
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(BROOKINGS_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找文章列表
        # Brookings 网站常见的文章容器
        articles = []
        
        # 尝试多种选择器
        article_selectors = [
            'article.card',
            '.article-listing article',
            '.post-item',
            '.article-item',
            '[data-testid="article-card"]'
        ]
        
        article_elements = []
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                article_elements = elements
                print(f"✅ 找到文章容器: {selector} ({len(elements)}条)")
                break
        
        if not article_elements:
            # 备用：查找所有包含链接的标题
            print("⚠️  未找到标准文章容器，尝试备用选择器...")
            article_elements = soup.find_all('article')[:10]
        
        for article in article_elements[:10]:  # 取前10条
            try:
                # 提取标题
                title_elem = article.find(['h2', 'h3', 'h4']) or article.find(class_=['title', 'heading'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                
                # 提取链接
                link_elem = title_elem.find('a') or article.find('a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = 'https://www.brookings.edu' + link
                
                # 提取日期
                date_elem = article.find('time') or article.find(class_=['date', 'published'])
                date_str = ''
                if date_elem:
                    date_str = date_elem.get_text().strip()
                
                # 提取摘要
                summary_elem = article.find(class_=['excerpt', 'summary', 'description']) or article.find('p')
                summary = ''
                if summary_elem:
                    summary = summary_elem.get_text().strip()[:300]
                
                # 检查是否最近的文章
                if not is_recent(date_str):
                    continue
                
                articles.append({
                    "title": title,
                    "url": link,
                    "published": date_str,
                    "source": "Brookings Institution",
                    "summary": summary,
                    "category": categorize(title)
                })
                
                print(f"  ✅ {title[:60]}...")
                
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        # 保存结果
        output = {
            "source": "Brookings Institution - Education",
            "source_url": BROOKINGS_URL,
            "crawled_at": datetime.now().isoformat(),
            "total_news": len(articles),
            "news": articles
        }
        
        # 确保目录存在
        os.makedirs('data/brookings', exist_ok=True)
        
        # 按日期保存
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'data/brookings/{date_str}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻")
        
        if len(articles) == 0:
            print("⚠️  警告：未抓取到任何文章，可能需要更新选择器")
        
        return output
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def is_recent(date_str, days=14):
    """检查日期是否在最近N天内"""
    if not date_str:
        return True
    
    try:
        # 尝试多种日期格式
        from dateutil import parser
        date = parser.parse(date_str)
        delta = datetime.now() - date
        return delta.days <= days
    except:
        # 如果无法解析，默认保留
        return True

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'policy': ['policy', 'federal', 'legislation', 'government'],
        'higher_ed': ['college', 'university', 'higher education', 'student debt'],
        'k12': ['k-12', 'school', 'teacher', 'elementary', 'secondary'],
        'economy': ['economy', 'economic', 'workforce', 'labor'],
        'technology': ['technology', 'digital', 'online', 'ai']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

if __name__ == '__main__':
    result = crawl_brookings()
    
    if result and result['total_news'] > 0:
        print("\n🎉 抓取成功！")
        exit(0)
    else:
        print("\n⚠️  抓取失败或未获取到数据")
        exit(1)
