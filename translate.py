#!/usr/bin/env python3
"""
翻译脚本（精简版）：仅编译标题，不抓取全文，不生成摘要
"""
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

RAW_DATA_DIR = config['paths']['raw_data_dir']
TRANSLATED_DIR = config['paths']['translated_data_dir']
TRANSLATION_DB_FILE = config['paths']['translation_db_file']
PROCESSED_ARTICLES_FILE = config['paths']['processed_articles_file']

# 加载翻译数据库（仅标题翻译）
translation_db = {}
if os.path.exists(TRANSLATION_DB_FILE):
    with open(TRANSLATION_DB_FILE, 'r', encoding='utf-8') as f:
        translation_db = json.load(f)

# 加载已处理文章列表
processed_articles = set()
if os.path.exists(PROCESSED_ARTICLES_FILE):
    with open(PROCESSED_ARTICLES_FILE, 'r', encoding='utf-8') as f:
        processed_articles = set(json.load(f))

def is_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def parse_date(date_str):
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    date_formats = [
        '%B %d, %Y', '%b %d, %Y', '%Y-%m-%d', '%m/%d/%Y',
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
        except:
            continue
    return datetime.now().strftime('%Y-%m-%d')

def translate_title(article, source):
    """仅翻译标题，使用已有的翻译数据库"""
    title = article.get('title', '').strip()
    url = article.get('url', '')
    date_str = article.get('date', '')
    sort_date = parse_date(date_str)

    if not title:
        return None

    # 检查已有翻译
    if source in translation_db and title in translation_db[source]:
        t = translation_db[source][title]
        return {
            **article,
            'title_cn': t.get('title_cn', title),
            'summary_cn': '',  # 不再生成摘要
            '_sort_date': sort_date
        }

    # 中文标题直接使用
    if is_chinese(title):
        title_cn = title
    else:
        # 英文标题暂不翻译，保留原文
        title_cn = title

    # 保存到翻译数据库
    if source not in translation_db:
        translation_db[source] = {}
    translation_db[source][title] = {
        'title_cn': title_cn,
        'summary_cn': '',
        'translated_time': datetime.now().isoformat()
    }

    return {**article, 'title_cn': title_cn, 'summary_cn': '', '_sort_date': sort_date}

def main():
    print("🔄 开始处理标题（精简模式，不编译全文）...")
    os.makedirs(TRANSLATED_DIR, exist_ok=True)

    four_days_ago = datetime.now() - timedelta(days=4)
    new_count = 0

    for source in sorted(os.listdir(RAW_DATA_DIR)):
        source_dir = os.path.join(RAW_DATA_DIR, source)
        if not os.path.isdir(source_dir):
            continue

        for filename in sorted(os.listdir(source_dir)):
            if not filename.endswith('.json'):
                continue

            # 只处理最近4天
            date_str = filename.replace('.json', '')
            try:
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if file_date < four_days_ago:
                    continue
            except:
                continue

            file_path = os.path.join(source_dir, filename)
            file_key = f"{source}/{filename}"

            if file_key in processed_articles:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    articles = data
                elif isinstance(data, dict):
                    articles = data.get('articles') or data.get('news') or []
            except Exception as e:
                print(f"⚠️  读取 {file_path} 失败: {e}")
                continue

            translated_articles = []
            for article in articles:
                t = translate_title(article, source)
                if t:
                    translated_articles.append(t)
                    new_count += 1

            if translated_articles:
                out_dir = os.path.join(TRANSLATED_DIR, source)
                os.makedirs(out_dir, exist_ok=True)
                with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
                    json.dump(translated_articles, f, ensure_ascii=False, indent=2)

            processed_articles.add(file_key)

    # 保存数据库
    with open(TRANSLATION_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(translation_db, f, ensure_ascii=False, indent=2)
    with open(PROCESSED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_articles), f, ensure_ascii=False, indent=2)

    print(f"✅ 标题处理完成，共 {new_count} 篇文章")

if __name__ == "__main__":
    main()
