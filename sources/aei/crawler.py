#!/usr/bin/env python3
"""
AEI (American Enterprise Institute) 爬虫
从 https://www.aei.org/feed/ 抓取教育相关文章
筛选教育类别文章
只抓取最近3天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

AEI_RSS_URL = "https://www.aei.org/feed/"
RAW_DIR = "data/raw/aei"

# 教育相关关键词
EDUCATION_KEYWORDS = [
    'education', 'educational', 'school', 'student', 'teacher', 'university', 
    'college', 'academic', 'higher education', 'k-12', 'learning', 'scholar',
    '教育', '学校', '学生', '教师', '大学'
]

def parse_date(date_str):
    """解析RSS日期格式"""
    # RSS日期格式: Fri, 27 Mar 2026 17:39:32 +0000
    try:
        # 移除时区信息
        date_str = re.sub(r'\s+[+-]\d{4}$', '', date_str.strip())
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
    except:
        pass
    
    # 尝试其他格式
    date_formats = [
        '%B %d, %Y',
        '%b %d, %Y',
        '%Y-%m-%d',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
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

def is_education_related(title, categories, description):
    """检查是否是教育相关文章"""
    text = (title + ' ' + ' '.join(categories) + ' ' + description).lower()
    for keyword in EDUCATION_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'higher_ed': ['higher education', 'college', 'university', 'academic'],
        'k12': ['k-12', 'school', 'student', 'teacher', 'education'],
        'economy': ['economy', 'economic', 'finance', 'budget'],
        'policy': ['policy', 'reform', 'legislation'],
        'technology': ['technology', 'artificial intelligence', 'AI']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_aei():
    """从 AEI RSS 抓取教育相关文章（最近3天）"""
    print("🚀 开始抓取 AEI (American Enterprise Institute)...")
    print(f"📡 RSS Feed: {AEI_RSS_URL}")
    print(f"📅 只抓取最近3天内的教育相关文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(AEI_RSS_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ RSS获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'xml')
        articles = []
        skipped_count = 0
        filtered_count = 0
        
        # 查找所有item
        items = soup.find_all('item')
        
        print(f"✅ 找到 {len(items)} 篇文章，开始筛选...")
        
        for item in items:
            try:
                # 标题
                title_elem = item.find('title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # 链接
                link_elem = item.find('link')
                url = link_elem.get_text(strip=True) if link_elem else ''
                
                # 发布日期
                pubdate_elem = item.find('pubDate')
                date_str = pubdate_elem.get_text(strip=True) if pubdate_elem else ''
                
                # 描述/摘要
                desc_elem = item.find('description')
                description = ""
                if desc_elem:
                    # 清理HTML标签
                    desc_soup = BeautifulSoup(desc_elem.get_text(), 'html.parser')
                    description = desc_soup.get_text().strip()[:500]
                
                # 分类
                categories = []
                cat_elems = item.find_all('category')
                for cat in cat_elems:
                    categories.append(cat.get_text(strip=True))
                
                # 检查是否是教育相关
                if not is_education_related(title, categories, description):
                    filtered_count += 1
                    continue
                
                # 检查日期是否在3天内
                if not is_within_days(date_str, days=4):
                    skipped_count += 1
                    display_date = parse_date(date_str)
                    if display_date:
                        print(f"  ⏭️  跳过（超过3天）: {title[:40]}... | {display_date.strftime('%Y-%m-%d')}")
                    continue
                
                # 作者
                creator_elem = item.find('dc:creator')
                author = creator_elem.get_text(strip=True) if creator_elem else ''
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': date_str,
                        'type': 'Article',
                        'author': author,
                        'categories': categories,
                        'summary_en': description,
                        'source': 'AEI',
                        'category': categorize(title)
                    })
                    display_date = parse_date(date_str)
                    date_display = display_date.strftime('%Y-%m-%d') if display_date else date_str
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {date_display} | 📋 Education")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 筛选结果: {len(articles)} 篇教育相关且在3天内")
        print(f"   跳过 {skipped_count} 篇（超过3天）")
        print(f"   过滤 {filtered_count} 篇（非教育相关）")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'AEI - American Enterprise Institute',
            'source_url': AEI_RSS_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条教育新闻（最近3天）")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_aei()
