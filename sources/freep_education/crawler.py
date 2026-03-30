#!/usr/bin/env python3
"""
Detroit Free Press Education 爬虫
从 https://www.freep.com/news/education/ 抓取最新新闻
只抓取最近4天内的文章
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re

FREEP_URL = "https://www.freep.com/news/education/"
RAW_DIR = "data/raw/freep_education"

def parse_relative_time(time_text):
    """解析相对时间格式"""
    time_text = time_text.lower().strip()
    now = datetime.now()
    
    # 匹配 "X:XX a.m. ET Month Day"
    match = re.search(r'(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)\s*et\s+(\w+)\s+(\d{1,2})', time_text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        ampm = match.group(3)
        month_str = match.group(4)
        day = int(match.group(5))
        
        # 转换月份
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        month = months.get(month_str.lower(), 1)
        
        # 转换小时
        if ampm == 'p.m.' and hour != 12:
            hour += 12
        elif ampm == 'a.m.' and hour == 12:
            hour = 0
        
        year = now.year
        try:
            return datetime(year, month, day, hour, minute)
        except:
            return None
    
    return None

def is_within_days(time_text, days=4):
    """检查时间是否在指定天数内"""
    article_date = parse_relative_time(time_text)
    if not article_date:
        return True  # 无法解析时默认包含
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return article_date >= cutoff_date

def categorize(title):
    """自动分类"""
    title_lower = title.lower()
    
    categories = {
        'sports': ['basketball', 'sports', 'athletic', 'team'],
        'high_school': ['high school', 'mhsaa', 'preps'],
        'metro': ['metro', 'detroit', 'east', 'west'],
        'students': ['students', 'players', 'boys', 'girls']
    }
    
    for cat, keywords in categories.items():
        if any(kw in title_lower for kw in keywords):
            return cat
    
    return 'general'

def crawl_freep():
    """从 Detroit Free Press 抓取最新新闻（最近4天）"""
    print("🚀 开始抓取 Detroit Free Press Education...")
    print(f"📡 网址: {FREEP_URL}")
    print(f"📅 只抓取最近4天内的文章")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(FREEP_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 网页获取成功 ({len(response.text)} bytes)")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        skipped_count = 0
        
        # 查找所有文章 - gnt_m_flm_a 类
        article_items = soup.find_all('a', class_='gnt_m_flm_a')
        
        print(f"✅ 找到 {len(article_items)} 篇文章，开始过滤...")
        
        for item in article_items:
            try:
                # 获取标题 - 直接文本内容
                title = item.get_text(strip=True)
                # 移除子元素的文本（如时间）
                for sub in item.find_all('div', class_='gnt_m_flm_sbt'):
                    sub_text = sub.get_text(strip=True)
                    title = title.replace(sub_text, '')
                title = title.strip()
                
                # 获取链接
                href = item.get('href', '')
                if not href:
                    continue
                
                if href.startswith('http'):
                    url = href
                else:
                    url = f"https://www.freep.com{href}"
                
                # 获取时间和分类
                time_elem = item.find('div', class_='gnt_m_flm_sbt')
                time_text = time_elem.get_text(strip=True) if time_elem else ''
                
                # 获取data-c-br属性作为摘要
                summary_en = item.get('data-c-br', '')[:400]
                
                # 检查日期是否在4天内
                if time_text and not is_within_days(time_text, days=4):
                    skipped_count += 1
                    print(f"  ⏭️  跳过（超过4天）: {title[:40]}... | {time_text}")
                    continue
                
                if title and url:
                    articles.append({
                        'title': title,
                        'url': url,
                        'date': time_text,
                        'type': 'News',
                        'summary_en': summary_en,
                        'source': 'Detroit Free Press',
                        'category': categorize(title)
                    })
                    print(f"  ✅ {title[:60]}...")
                    print(f"     📅 {time_text}")
                    
            except Exception as e:
                print(f"  ⚠️  解析单篇文章失败: {e}")
                continue
        
        print(f"\n📊 过滤结果: {len(articles)} 篇在4天内，跳过 {skipped_count} 篇")
        
        # 保存结果
        os.makedirs(RAW_DIR, exist_ok=True)
        
        output = {
            'source': 'Detroit Free Press Education',
            'source_url': FREEP_URL,
            'crawled_at': datetime.now().isoformat(),
            'total_news': len(articles),
            'news': articles
        }
        
        filename = f"{RAW_DIR}/{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 已保存: {filename}")
        print(f"📊 共 {len(articles)} 条新闻（最近4天）")
        
        return output
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    crawl_freep()
