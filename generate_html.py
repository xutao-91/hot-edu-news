#!/usr/bin/env python3
"""
自动生成展示页面 - 确保链接100%来自原始数据文件
禁止手动修改链接！
"""
import json
import os
from datetime import datetime, timedelta

def get_latest_json(directory):
    """自动找到目录下最新的JSON文件"""
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not json_files:
        return None
    json_files.sort(reverse=True)  # 文件名按日期倒序
    return os.path.join(directory, json_files[0])

def is_within_days(date_str, days=7):
    """检查日期是否在指定天数内"""
    try:
        article_date = datetime.strptime(date_str, '%B %d, %Y')
        cutoff_date = datetime.now() - timedelta(days=days)
        return article_date >= cutoff_date
    except:
        return True  # 解析失败默认保留

def generate_html():
    # 自动找到最新的数据文件
    sources = {
        'brookings': get_latest_json('data/brookings'),
        'edgov': get_latest_json('data/edgov'),
        'whitehouse': get_latest_json('data/whitehouse'),
        'ace': get_latest_json('data/ace')
    }
    
    data = {}
    for name, filepath in sources.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data[name] = json.load(f)
            print(f"✅ 读取 {name}: {len(data[name]['news'])} 篇文章")
        except Exception as e:
            print(f"❌ 读取 {name} 失败: {e}")
            data[name] = {'source': name, 'news': []}
    
    # HTML头部
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点教育信息 - 多来源聚合</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: "Microsoft YaHei", "SimSun", serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.8;
        }
        .header { 
            background: #2c5aa0; 
            color: white; 
            padding: 20px; 
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .header h1 { 
            font-size: 24px; 
            border-bottom: 2px solid white;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .source-info { font-size: 14px; opacity: 0.9; }
        .article { 
            background: white;
            border: 1px solid #ddd; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .article-header {
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .article-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .article-author {
            color: #2c5aa0;
            font-size: 14px;
            font-weight: bold;
        }
        .article-author::before { content: "👤 "; }
        .article-date {
            color: #666;
            font-size: 14px;
        }
        .article-date::before { content: "📅 "; }
        .article-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c5aa0;
            margin: 10px 0 5px 0;
        }
        .article-subtitle {
            font-size: 13px;
            color: #888;
            font-style: italic;
        }
        .article-summary {
            text-align: justify;
            color: #333;
            font-size: 15px;
            margin: 15px 0;
            text-indent: 2em;
        }
        .article-footer {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px dashed #ddd;
        }
        .article-link {
            color: #2c5aa0;
            text-decoration: none;
            font-size: 14px;
        }
        .article-link:hover { text-decoration: underline; }
        .meta {
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }
        .highlight {
            background: #fff3cd;
            padding: 2px 5px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
'''
    
    # Brookings
    if data.get('brookings'):
        # 只显示7天内的文章
        brookings_news = [a for a in data['brookings']['news'] if is_within_days(a['date'], days=7)]
        html += f'''
    <div class="header">
        <h1>🔥 {data['brookings']['source']}</h1>
        <div class="source-info">
            来源: <a href="{data['brookings']['source_url']}" target="_blank" style="color: white;">Brookings Institution - Education</a> |
            今日收录: {len(brookings_news)}篇
        </div>
    </div>
'''
        for i, article in enumerate(brookings_news[:4], 1):
            highlight = '<span class="highlight">' if i == 1 else ''
            highlight_end = '</span>' if i == 1 else ''
            new_badge = ' | 🆕 今日最新' if i == 1 else ''
            html += f'''
    <div class="article">
        <div class="article-header">
            <div class="article-meta">
                <span class="article-author">{article.get('author', 'Brookings')}</span>
                <span class="article-date">{highlight}{article['date']}{highlight_end}</span>
            </div>
            <div class="article-title">{article['title']}</div>
            <div class="article-subtitle">{article.get('original_title', '')}</div>
        </div>
        <div class="article-summary">{article.get('summary', article.get('summary_en', ''))}</div>
        <div class="article-footer">
            <a href="{article['url']}" target="_blank" class="article-link">🔗 查看原文</a>
            <div class="meta">来源: {article['source']} | 分类: {article.get('category', 'general')}{new_badge}</div>
        </div>
    </div>
'''
    
    # ED.gov
    if data.get('edgov'):
        # 只显示7天内的文章
        edgov_news = [a for a in data['edgov']['news'] if is_within_days(a['date'], days=7)]
        html += f'''
    <div class="header" style="margin-top: 30px; background: #1a4480;">
        <h1>🇺🇸 美国教育部 ED.gov</h1>
        <div class="source-info">
            来源: <a href="{data['edgov']['source_url']}" target="_blank" style="color: white;">U.S. Department of Education</a> |
            今日收录: {len(edgov_news)}篇
        </div>
    </div>
'''
        for i, article in enumerate(edgov_news[:4], 1):
            highlight = '<span class="highlight">' if i == 1 else ''
            highlight_end = '</span>' if i == 1 else ''
            new_badge = ' | 🆕 今日最新' if i == 1 else ''
            html += f'''
    <div class="article">
        <div class="article-header">
            <div class="article-meta">
                <span class="article-author">{article.get('author', 'U.S. Department of Education')}</span>
                <span class="article-date">{highlight}{article['date']}{highlight_end}</span>
            </div>
            <div class="article-title">{article['title']}</div>
            <div class="article-subtitle">{article.get('original_title', '')}</div>
        </div>
        <div class="article-summary">{article.get('summary', article.get('summary_en', ''))}</div>
        <div class="article-footer">
            <a href="{article['url']}" target="_blank" class="article-link">🔗 查看原文</a>
            <div class="meta">来源: {article['source']} | 分类: {article.get('category', 'general')}{new_badge}</div>
        </div>
    </div>
'''
    
    # White House
    if data.get('whitehouse'):
        # 只显示7天内的文章
        whitehouse_news = [a for a in data['whitehouse']['news'] if is_within_days(a['date'], days=7)]
        html += f'''
    <div class="header" style="margin-top: 30px; background: #b22234;">
        <h1>🏛️ 白宫 The White House</h1>
        <div class="source-info">
            来源: <a href="{data['whitehouse']['source_url']}" target="_blank" style="color: white;">The White House</a> |
            今日收录: {len(whitehouse_news)}篇
        </div>
    </div>
'''
        for i, article in enumerate(whitehouse_news[:4], 1):
            highlight = '<span class="highlight">' if i == 1 else ''
            highlight_end = '</span>' if i == 1 else ''
            new_badge = ' | 🆕 今日最新' if i == 1 else ''
            html += f'''
    <div class="article">
        <div class="article-header">
            <div class="article-meta">
                <span class="article-author">{article.get('author', 'The White House')}</span>
                <span class="article-date">{highlight}{article['date']}{highlight_end}</span>
            </div>
            <div class="article-title">{article['title']}</div>
            <div class="article-subtitle">{article.get('original_title', '')}</div>
        </div>
        <div class="article-summary">{article.get('summary', article.get('summary_en', ''))}</div>
        <div class="article-footer">
            <a href="{article['url']}" target="_blank" class="article-link">🔗 查看原文</a>
            <div class="meta">来源: {article['source']} | 分类: {article.get('category', 'general')}{new_badge}</div>
        </div>
    </div>
'''
    
    # ACE
    if data.get('ace'):
        # 只显示7天内的文章
        ace_news = [a for a in data['ace']['news'] if is_within_days(a['date'], days=7)]
        html += f'''
    <div class="header" style="margin-top: 30px; background: #003366;">
        <h1>🎓 ACE 美国教育委员会</h1>
        <div class="source-info">
            来源: <a href="{data['ace']['source_url']}" target="_blank" style="color: white;">American Council on Education</a> |
            今日收录: {len(ace_news)}篇
        </div>
    </div>
'''
        for i, article in enumerate(ace_news[:8], 1):
            highlight = '<span class="highlight">' if i == 1 else ''
            highlight_end = '</span>' if i == 1 else ''
            new_badge = ' | 🆕 今日最新' if i == 1 else ''
            html += f'''
    <div class="article">
        <div class="article-header">
            <div class="article-meta">
                <span class="article-author">{article.get('author', 'ACE')}</span>
                <span class="article-date">{highlight}{article['date']}{highlight_end}</span>
            </div>
            <div class="article-title">{article['title']}</div>
            <div class="article-subtitle">{article.get('original_title', '')}</div>
        </div>
        <div class="article-summary">{article.get('summary', article.get('summary_en', ''))}</div>
        <div class="article-footer">
            <a href="{article['url']}" target="_blank" class="article-link">🔗 查看原文</a>
            <div class="meta">来源: {article['source']} | 分类: {article.get('category', 'general')}{new_badge}</div>
        </div>
    </div>
'''
    
    # 页脚
    html += '''
    <div class="footer">
        📊 本项目从真实网站抓取，每条新闻都有具体URL可验证<br>
        🔄 每日自动更新 | 体制内公文编译风格
    </div>
</body>
</html>
'''
    
    # 保存
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n✅ 展示页面已重新生成！")
    print("✅ 所有链接100%来自原始数据文件！")

if __name__ == '__main__':
    generate_html()
