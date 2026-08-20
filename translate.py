#!/usr/bin/env python3
"""标题整理脚本。

不调用 Kimi 或任何其他外部模型供应商。已有中文译名继续复用；没有
既有译名的英文标题保留原文，之后可由 Codex 工作流另行审核处理。
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
    print("🔄 开始整理标题（无外部模型供应商）...")
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

            out_dir = os.path.join(TRANSLATED_DIR, source)
            out_path = os.path.join(out_dir, filename)
            existing_translated = []
            if os.path.exists(out_path):
                try:
                    with open(out_path, 'r', encoding='utf-8') as f:
                        existing_translated = json.load(f)
                    if not isinstance(existing_translated, list):
                        existing_translated = []
                except Exception:
                    existing_translated = []

            existing_urls = {a.get('url') for a in existing_translated if a.get('url')}
            translated_articles = []
            for article in articles:
                article_key = article.get('url') or f"{source}|{article.get('title', '')}|{article.get('date', '')}"
                if article_key in processed_articles or article.get('url') in existing_urls:
                    continue
                t = translate_title(article, source)
                if t:
                    translated_articles.append(t)
                    processed_articles.add(article_key)
                    new_count += 1

            if translated_articles:
                os.makedirs(out_dir, exist_ok=True)
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_translated + translated_articles, f, ensure_ascii=False, indent=2)

    # 保存数据库
    with open(TRANSLATION_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(translation_db, f, ensure_ascii=False, indent=2)
    with open(PROCESSED_ARTICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(processed_articles), f, ensure_ascii=False, indent=2)

    summary_path = os.path.join(os.path.dirname(PROCESSED_ARTICLES_FILE), 'last_process.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'finished_at': datetime.now().isoformat(),
            'new_articles_processed': new_count,
            'provider': 'none',
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ 标题处理完成，共 {new_count} 篇文章")

if __name__ == "__main__":
    main()
