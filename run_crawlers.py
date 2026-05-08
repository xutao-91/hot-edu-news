#!/usr/bin/env python3
import os
import json
import subprocess
import concurrent.futures
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 新增：多领域分类规则，匹配用户要求的收录范围
CATEGORIES = {
    "education": ["education", "school", "student", "teacher", "learning", "university", "college", "k12", "higher education"],
    "quantum": ["quantum", "quantum computing", "quantum technology", "量子"],
    "ai": ["ai", "artificial intelligence", "large language model", "llm", "generative ai", "大模型", "人工智能"],
    "biomanufacturing": ["biomanufacturing", "bioproduction", "synthetic biology", "合成生物", "生物制造"],
    "space": ["space travel", "interstellar", "aerospace", "space exploration", "星际航行", "航天", "太空探索"],
    "bci": ["bci", "brain computer interface", "brain machine interface", "脑机接口"],
    "semiconductor": ["ic", "integrated circuit", "semiconductor", "chip", "集成电路", "芯片", "半导体"],
    "diplomacy": ["diplomatic", "foreign affairs", "diplomacy", "外交", "外事"],
    "talent": ["talent", "human resource", "人才", "人力资源"]
}

def categorize_article(title, summary=""):
    """统一分类判断，匹配用户要求的收录领域"""
    content = f"{title} {summary}".lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in content for keyword in keywords):
            return category
    return "general"

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

RAW_DATA_DIR = config['paths']['raw_data_dir']
CRAWLERS_DIR = config['paths']['crawlers_dir']
URL_CACHE_FILE = config['paths']['url_cache_file']
MAX_WORKERS = config['crawler']['max_workers']
DAYS_TO_FETCH = config['crawler']['days_to_fetch']

# 加载URL缓存
url_cache = {}
if os.path.exists(URL_CACHE_FILE):
    with open(URL_CACHE_FILE, 'r', encoding='utf-8') as f:
        url_cache = json.load(f)

def load_existing_urls(source):
    """加载某个来源已抓取的所有URL"""
    existing_urls = set()
    source_dir = os.path.join(RAW_DATA_DIR, source)
    if not os.path.exists(source_dir):
        return existing_urls
    
    for filename in os.listdir(source_dir):
        if not filename.endswith('.json'):
            continue
        file_path = os.path.join(source_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for article in data:
                    if 'url' in article:
                        existing_urls.add(article['url'])
        except Exception as e:
            print(f"⚠️  读取文件 {file_path} 失败: {str(e)}")
            continue
    return existing_urls

def run_crawler(crawler_path):
    """执行单个爬虫脚本，返回抓取结果"""
    source_name = os.path.basename(os.path.dirname(crawler_path))
    print(f"🚀 开始抓取 {source_name}...")
    
    try:
        # 执行爬虫脚本，传入抓取天数参数
        result = subprocess.run(
            [sys.executable, crawler_path, str(DAYS_TO_FETCH)],
            capture_output=True,
            text=True,
            timeout=config['crawler']['timeout']
        )
        
        if result.returncode != 0:
            print(f"❌ {source_name} 抓取失败: {result.stderr}")
            return source_name, []
        
        # 直接读取爬虫保存的今日文件
        today = datetime.now().strftime('%Y-%m-%d')
        source_dir = os.path.join(RAW_DATA_DIR, source_name)
        articles = []
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                if filename.startswith(today) and filename.endswith('.json'):
                    file_path = os.path.join(source_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # 确保是列表格式
                            if isinstance(data, list):
                                articles = data
                            elif isinstance(data, dict) and 'articles' in data and isinstance(data['articles'], list):
                                articles = data['articles']
                            elif isinstance(data, dict) and 'news' in data and isinstance(data['news'], list):
                                articles = data['news']
                            else:
                                print(f"⚠️  {source_name} 文件 {filename} 格式不正确，跳过")
                    except Exception as e:
                        print(f"⚠️  读取 {source_name} 结果失败: {str(e)}")
                        return source_name, []
        
        # 过滤已抓取过的URL
        existing_urls = load_existing_urls(source_name)
        new_articles = [a for a in articles if a.get('url') not in existing_urls and a.get('url') not in url_cache]
        
        # 用户要求：暂时不设过滤限制，所有抓取到的文章全部收录
        filtered_articles = []
        for article in new_articles:
            # 保留自动分类功能，但不再过滤
            category = categorize_article(article.get("title", ""), article.get("summary_en", article.get("summary", "")))
            article["category"] = category
            filtered_articles.append(article)
        
        if not filtered_articles:
            print(f"✅ {source_name} 没有新内容")
            return source_name, []
        
        print(f"✅ {source_name} 抓取完成，新增 {len(filtered_articles)} 篇文章")
        for article in filtered_articles:
            if 'url' in article:
                url_cache[article['url']] = {
                    'source': source_name,
                    'fetch_time': datetime.now().isoformat(),
                    'title': article.get('title', ''),
                    'category': article.get('category', 'general')
                }
        
        return source_name, filtered_articles
     
    except subprocess.TimeoutExpired:
        print(f"⏰ {source_name} 抓取超时")
        return source_name, []
    except Exception as e:
        print(f"❌ {source_name} 执行异常: {str(e)}")
        return source_name, []

def main():
    # 扫描所有爬虫脚本
    crawler_paths = []
    for root, dirs, files in os.walk(CRAWLERS_DIR):
        for file in files:
            if file == 'crawler.py' and os.path.isfile(os.path.join(root, file)):
                crawler_paths.append(os.path.join(root, file))
    
    print(f"📋 发现 {len(crawler_paths)} 个爬虫脚本，开始并行执行...\n")
    
    # 并行执行所有爬虫
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_crawler = {executor.submit(run_crawler, path): path for path in crawler_paths}
        for future in concurrent.futures.as_completed(future_to_crawler):
            results.append(future.result())
    
    # 保存URL缓存
    with open(URL_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(url_cache, f, ensure_ascii=False, indent=2)
    
    # 统计结果
    total_new = sum(len(articles) for _, articles in results)
    print(f"\n🎉 所有爬虫执行完成，共新增 {total_new} 篇文章")
    
    # 输出新文章数量，供后续步骤使用
    print(f"::set-output name=new_articles_count::{total_new}")

if __name__ == "__main__":
    main()
