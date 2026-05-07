#!/usr/bin/env python3
import os
import json
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime, timedelta

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
            ['python3', crawler_path, str(DAYS_TO_FETCH)],
            capture_output=True,
            text=True,
            timeout=config['crawler']['timeout']
        )
        
        if result.returncode != 0:
            print(f"❌ {source_name} 抓取失败: {result.stderr}")
            return source_name, []
        
        # 解析爬虫输出的JSON结果
        try:
            articles = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"❌ {source_name} 输出解析失败: {str(e)}")
            return source_name, []
        
        # 过滤已抓取过的URL
        existing_urls = load_existing_urls(source_name)
        new_articles = [a for a in articles if a.get('url') not in existing_urls and a.get('url') not in url_cache]
        
        if not new_articles:
            print(f"✅ {source_name} 没有新内容")
            return source_name, []
        
        # 保存新抓取的内容
        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = os.path.join(RAW_DATA_DIR, source_name)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{today}_{len(new_articles)}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_articles, f, ensure_ascii=False, indent=2)
        
        # 更新URL缓存
        for article in new_articles:
            if 'url' in article:
                url_cache[article['url']] = {
                    'source': source_name,
                    'fetch_time': datetime.now().isoformat(),
                    'title': article.get('title', '')
                }
        
        print(f"✅ {source_name} 抓取完成，新增 {len(new_articles)} 篇文章")
        return source_name, new_articles
    
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
