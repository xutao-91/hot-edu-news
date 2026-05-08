#!/usr/bin/env python3
"""
翻译脚本：严格按原文编译，绝不编造
原则：
1. 只编译可访问原文的内容
2. 原文没有的信息，绝不脑补
3. 不添加评价性语句
4. 不为凑字数而扩写
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

RAW_DATA_DIR = config['paths']['raw_data_dir']
TRANSLATED_DIR = config['paths']['translated_data_dir']
TRANSLATION_DB_FILE = config['paths']['translation_db_file']
PROCESSED_ARTICLES_FILE = config['paths']['processed_articles_file']

# 加载翻译数据库
translation_db = {}
if os.path.exists(TRANSLATION_DB_FILE):
    with open(TRANSLATION_DB_FILE, 'r', encoding='utf-8') as f:
        translation_db = json.load(f)
else:
    # 初始化默认的翻译数据（原来硬编码的内容）
    translation_db = {
        "brookings": {},
        "edgov": {},
        "whitehouse": {},
        "ace": {},
        "nsf_ncses": {},
        "pewresearch": {}
    }

# 加载已处理文章列表
processed_articles = set()
if os.path.exists(PROCESSED_ARTICLES_FILE):
    with open(PROCESSED_ARTICLES_FILE, 'r', encoding='utf-8') as f:
        processed_articles = set(json.load(f))

def is_chinese(text):
    """判断文本是否为中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def parse_date(date_str):
    """解析多种格式的日期，返回YYYY-MM-DD格式的字符串"""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    date_formats = [
        '%B %d, %Y', # May 7, 2026
        '%b %d, %Y', # May 7, 2026
        '%Y-%m-%d', # 2026-05-07
        '%m/%d/%Y', # 05/07/2026
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
        except:
            continue
    return datetime.now().strftime('%Y-%m-%d')

def translate_article(article, source):
    """翻译单篇文章，优先使用缓存，没有的话调用翻译API"""
    title = article.get('title', '').strip()
    summary = article.get('summary', '').strip()
    url = article.get('url', '')
    date_str = article.get('date', '')
    
    # 解析生成标准日期字段
    sort_date = parse_date(date_str)
    
    if not title:
        return None
    
    # 检查是否已经翻译过
    if source in translation_db and title in translation_db[source]:
        translated = translation_db[source][title]
        return {
            **article,
            'title_cn': translated.get('title_cn', title),
            'summary_cn': translated.get('summary_cn', summary),
            'translated_time': translated.get('translated_time', datetime.now().isoformat()),
            '_sort_date': sort_date
        }
    
    # 如果已经是中文，直接返回
    if is_chinese(title):
        translated = {
            'title_cn': title,
            'summary_cn': summary if is_chinese(summary) else '',
            'translated_time': datetime.now().isoformat()
        }
        # 保存到翻译数据库
        if source not in translation_db:
            translation_db[source] = {}
        translation_db[source][title] = translated
        return {**article, **translated, '_sort_date': sort_date}
    
    # 这里调用实际的翻译API，暂时先用占位符（可根据实际情况替换成OpenAI/DeepL等API）
    # 注意：实际使用时需要配置API密钥在环境变量中
    title_cn = f"[待翻译] {title}"
    summary_cn = f"[待翻译] {summary}"
    
    # 保存翻译结果到数据库
    translated = {
        'title_cn': title_cn,
        'summary_cn': summary_cn,
        'translated_time': datetime.now().isoformat()
    }
    if source not in translation_db:
        translation_db[source] = {}
    translation_db[source][title] = translated
    
    return {**article, **translated, '_sort_date': sort_date}

def main():
    print("🔄 开始翻译新增文章...")
    os.makedirs(TRANSLATED_DIR, exist_ok=True)
    
    new_translated_count = 0
    all_translated_articles = []
    
    # 遍历所有原始数据文件
    for source in os.listdir(RAW_DATA_DIR):
        source_dir = os.path.join(RAW_DATA_DIR, source)
        if not os.path.isdir(source_dir):
            continue
        
        for filename in os.listdir(source_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(source_dir, filename)
            file_key = f"{source}/{filename}"
            
            # 跳过已处理的文件
            if file_key in processed_articles:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 兼容不同格式的文章列表
                if isinstance(data, list):
                    articles = data
                elif isinstance(data, dict):
                    if 'articles' in data and isinstance(data['articles'], list):
                        articles = data['articles']
                    elif 'news' in data and isinstance(data['news'], list):
                        articles = data['news']
                    else:
                        print(f"⚠️  文件 {file_path} 格式错误，不是文章列表")
                        continue
            except Exception as e:
                print(f"⚠️  读取文件 {file_path} 失败: {str(e)}")
                continue
            
            translated_articles = []
            for article in articles:
                translated = translate_article(article, source)
                if translated:
                    translated_articles.append(translated)
                    new_translated_count += 1
            
            # 保存翻译后的文件
            if translated_articles:
                output_dir = os.path.join(TRANSLATED_DIR, source)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, filename)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_articles, f, ensure_ascii=False, indent=2)
                
                all_translated_articles.extend(translated_articles)
            
            # 标记为已处理
            processed_articles.add(file_key)
    
    # 保存更新后的翻译数据库
    with open(TRANSLATION_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(translation_db, f, ensure_ascii=False, indent=2)
    
    # 保存已处理文件列表
    with open(PROCESSED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_articles), f, ensure_ascii=False, indent=2)
    
    print(f"✅ 翻译完成，共处理 {new_translated_count} 篇新文章")
    print(f"::set-output name=new_translated_count::{new_translated_count}")

if __name__ == "__main__":
    main()
