#!/usr/bin/env python3
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class NewsDB:
    def __init__(self, db_path: str = "data/news.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 原始文章表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            publish_time TEXT,
            author TEXT,
            fetch_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 翻译结果表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translated_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_article_id INTEGER UNIQUE NOT NULL,
            title_cn TEXT NOT NULL,
            content_cn TEXT NOT NULL,
            translate_time TEXT NOT NULL,
            translate_provider TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            error_msg TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_article_id) REFERENCES raw_articles (id) ON DELETE CASCADE
        )
        ''')
        
        # URL缓存表（替代url_cache.json）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS url_cache (
            url TEXT PRIMARY KEY NOT NULL,
            source TEXT NOT NULL,
            fetch_time TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 翻译缓存表（替代translation_db.json）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_cache (
            original_hash TEXT PRIMARY KEY NOT NULL,
            translated_text TEXT NOT NULL,
            translate_time TEXT NOT NULL,
            usage_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 处理状态表（替代processed_articles.json）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_articles (
            raw_article_id INTEGER PRIMARY KEY NOT NULL,
            translated BOOLEAN DEFAULT FALSE,
            html_generated BOOLEAN DEFAULT FALSE,
            pushed_to_github BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raw_article_id) REFERENCES raw_articles (id) ON DELETE CASCADE
        )
        ''')
        
        # 系统日志表（用于监控告警）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            source TEXT NOT NULL,
            message TEXT NOT NULL,
            error_detail TEXT,
            happened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            alerted BOOLEAN DEFAULT FALSE
        )
        ''')
        
        self.conn.commit()
    
    # URL缓存相关方法
    def url_exists(self, url: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM url_cache WHERE url = ?", (url,))
        return cursor.fetchone() is not None
    
    def add_url_cache(self, url: str, source: str, title: str, fetch_time: str = None):
        if fetch_time is None:
            fetch_time = datetime.now().isoformat()
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO url_cache (url, source, title, fetch_time)
            VALUES (?, ?, ?, ?)
            ''', (url, source, title, fetch_time))
            self.conn.commit()
        except Exception as e:
            self.log_error("db", f"添加URL缓存失败: {str(e)}")
            raise
    
    # 原始文章相关方法
    def add_raw_article(self, article: Dict) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO raw_articles (url, source, title, content, publish_time, author, fetch_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['url'],
                article['source'],
                article.get('title', ''),
                article.get('content', ''),
                article.get('publish_time', ''),
                article.get('author', ''),
                article.get('fetch_time', datetime.now().isoformat())
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.log_error("db", f"添加原始文章失败: {str(e)}", str(e))
            raise
    
    def get_untranslated_articles(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ra.* FROM raw_articles ra
        LEFT JOIN processed_articles pa ON ra.id = pa.raw_article_id
        LEFT JOIN translated_articles ta ON ra.id = ta.raw_article_id
        WHERE pa.translated = 0 OR ta.id IS NULL
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    # 日志相关方法
    def log_error(self, source: str, message: str, error_detail: str = None):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO system_logs (level, source, message, error_detail)
        VALUES (?, ?, ?, ?)
        ''', ("ERROR", source, message, error_detail))
        self.conn.commit()
    
    def log_info(self, source: str, message: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO system_logs (level, source, message)
        VALUES (?, ?, ?)
        ''', ("INFO", source, message))
        self.conn.commit()
    
    def get_unalerted_errors(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM system_logs
        WHERE level = 'ERROR' AND alerted = 0
        ORDER BY happened_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_errors_alerted(self, error_ids: List[int]):
        cursor = self.conn.cursor()
        placeholders = ', '.join('?' * len(error_ids))
        cursor.execute(f'''
        UPDATE system_logs SET alerted = 1 WHERE id IN ({placeholders})
        ''', error_ids)
        self.conn.commit()
    
    # 迁移历史JSON数据到数据库
    def migrate_from_json(self, config: Dict):
        """迁移所有历史JSON数据到数据库"""
        print("🚀 开始迁移历史JSON数据到数据库...")
        
        # 1. 迁移URL缓存
        url_cache_file = config['paths']['url_cache_file']
        if os.path.exists(url_cache_file):
            print(f"正在迁移URL缓存: {url_cache_file}")
            with open(url_cache_file, 'r', encoding='utf-8') as f:
                url_cache = json.load(f)
            for url, data in url_cache.items():
                self.add_url_cache(url, data['source'], data['title'], data['fetch_time'])
            print(f"✅ 迁移URL缓存完成，共 {len(url_cache)} 条记录")
        
        # 2. 迁移原始文章
        raw_dir = config['paths']['raw_data_dir']
        total_raw = 0
        for source_dir in Path(raw_dir).iterdir():
            if not source_dir.is_dir():
                continue
            source = source_dir.name
            print(f"正在迁移来源 {source} 的原始文章...")
            for json_file in source_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        articles = json.load(f)
                    if not isinstance(articles, list):
                        print(f"⚠️  跳过非列表格式的文件: {json_file}")
                        continue
                    for article in articles:
                        if not isinstance(article, dict) or 'url' not in article:
                            print(f"⚠️  跳过无效文章: {json_file}")
                            continue
                        article['source'] = source
                        article_id = self.add_raw_article(article)
                        if article_id > 0:
                            total_raw += 1
                            # 初始化处理状态
                            cursor = self.conn.cursor()
                            cursor.execute('''
                            INSERT OR IGNORE INTO processed_articles (raw_article_id, translated, html_generated, pushed_to_github)
                            VALUES (?, 0, 0, 0)
                            ''', (article_id,))
                            self.conn.commit()
                except Exception as e:
                    print(f"⚠️  处理文件 {json_file} 失败: {str(e)}")
                    continue
        print(f"✅ 迁移原始文章完成，共 {total_raw} 条记录")
        
        # 3. 迁移翻译缓存
        trans_cache_file = config['paths']['translation_db_file']
        if os.path.exists(trans_cache_file):
            print(f"正在迁移翻译缓存: {trans_cache_file}")
            try:
                with open(trans_cache_file, 'r', encoding='utf-8') as f:
                    trans_cache = json.load(f)
                cursor = self.conn.cursor()
                # 遍历来源
                for source, content_map in trans_cache.items():
                    if not isinstance(content_map, dict):
                        continue
                    # 遍历内容映射
                    for original_hash, translated_data in content_map.items():
                        if isinstance(translated_data, dict) and 'text' in translated_data:
                            cursor.execute('''
                            INSERT OR REPLACE INTO translation_cache (original_hash, translated_text, translate_time, usage_count)
                            VALUES (?, ?, ?, ?)
                            ''', (
                                original_hash,
                                translated_data['text'],
                                translated_data.get('translate_time', datetime.now().isoformat()),
                                translated_data.get('usage_count', 1)
                            ))
                        elif isinstance(translated_data, str):
                            # 如果直接是字符串，就用这个作为翻译内容
                            cursor.execute('''
                            INSERT OR REPLACE INTO translation_cache (original_hash, translated_text, translate_time, usage_count)
                            VALUES (?, ?, ?, ?)
                            ''', (
                                original_hash,
                                translated_data,
                                datetime.now().isoformat(),
                                1
                            ))
                self.conn.commit()
                print(f"✅ 迁移翻译缓存完成")
            except Exception as e:
                print(f"⚠️ 迁移翻译缓存失败: {str(e)}，跳过")
        
        # 4. 迁移已处理文章状态
        processed_file = config['paths']['processed_articles_file']
        if os.path.exists(processed_file):
            print(f"正在迁移处理状态: {processed_file}")
            with open(processed_file, 'r', encoding='utf-8') as f:
                processed = json.load(f)
            cursor = self.conn.cursor()
            # 兼容列表和字典两种格式
            if isinstance(processed, dict):
                for url, status in processed.items():
                    # 查找对应的raw_article_id
                    cursor.execute("SELECT id FROM raw_articles WHERE url = ?", (url,))
                    row = cursor.fetchone()
                    if row:
                        raw_article_id = row[0]
                        status_value = 1 if status in ['processed', True] else 0
                        cursor.execute('''
                            INSERT OR REPLACE INTO processed_articles 
                            (raw_article_id, translated, html_generated, pushed_to_github)
                            VALUES (?, ?, 1, 1)
                        ''', (raw_article_id, status_value))
            elif isinstance(processed, list):
                for url in processed:
                    # 查找对应的raw_article_id
                    cursor.execute("SELECT id FROM raw_articles WHERE url = ?", (url,))
                    row = cursor.fetchone()
                    if row:
                        raw_article_id = row[0]
                        cursor.execute('''
                            INSERT OR REPLACE INTO processed_articles 
                            (raw_article_id, translated, html_generated, pushed_to_github)
                            VALUES (?, 1, 1, 1)
                        ''', (raw_article_id,))
                    cursor.execute('''
                    UPDATE processed_articles
                    SET translated = ?, html_generated = ?, pushed_to_github = ?
                    WHERE raw_article_id = ?
                    ''', (
                        status.get('translated', False),
                        status.get('html_generated', False),
                        status.get('pushed_to_github', False),
                        row['id']
                    ))
            self.conn.commit()
            print(f"✅ 迁移处理状态完成")
        
        print("🎉 所有历史数据迁移完成！")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    # 测试数据库创建和迁移
    import json
    with open("config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    db = NewsDB()
    db.migrate_from_json(config)
    db.close()
