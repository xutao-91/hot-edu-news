#!/usr/bin/env python3
"""
自动生成展示页面 - 按日期聚合所有来源
所有文章按日期倒序排列，不再按来源分组
"""
import json
import os
from datetime import datetime, timedelta

def get_latest_json(directory):
    """自动找到目录下最新的JSON文件"""
    if not os.path.exists(directory):
        return None
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not json_files:
        return None
    json_files.sort(reverse=True)
    return os.path.join(directory, json_files[0])

def parse_date(date_str):
    """解析各种日期格式"""
    formats = [
        '%B %d, %Y',      # March 25, 2026
        '%b %d, %Y',      # Mar 25, 2026
        '%Y-%m-%d',       # 2026-03-25
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def format_date_key(date_str):
    """将日期字符串转为排序键"""
    parsed = parse_date(date_str)
    if parsed:
        return parsed.strftime('%Y-%m-%d')
    return date_str

def get_display_date(date_str):
    """转为中文显示格式"""
    parsed = parse_date(date_str)
    if parsed:
        return parsed.strftime('%Y年%m月%d日')
    return date_str

def generate_html():
    # 读取所有来源的翻译后数据
    sources = {
        'brookings': {'name': '布鲁金斯学会', 'color': '#2c5aa0', 'icon': '🔥'},
        'edgov': {'name': '美国教育部', 'color': '#1a4480', 'icon': '🇺🇸'},
        'whitehouse': {'name': '白宫', 'color': '#b22234', 'icon': '🏛️'},
        'ace': {'name': 'ACE教育委员会', 'color': '#003366', 'icon': '🎓'},
        'nsf_ncses': {'name': 'NSF NCSES', 'color': '#1e4d2b', 'icon': '🔬'},
        'pewresearch': {'name': '皮尤研究中心', 'color': '#233656', 'icon': '📊'}
    }
    
    all_articles = []
    
    for source_key, source_info in sources.items():
        filepath = get_latest_json(f'data/translated/{source_key}')
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for article in data.get('news', []):
                    article['_source_key'] = source_key
                    article['_source_name'] = source_info['name']
                    article['_source_color'] = source_info['color']
                    article['_source_icon'] = source_info['icon']
                    article['_sort_date'] = format_date_key(article.get('date', ''))
                    all_articles.append(article)
            except Exception as e:
                print(f"❌ 读取 {source_key} 失败: {e}")
    
    # 按日期倒序排列
    all_articles.sort(key=lambda x: x['_sort_date'], reverse=True)
    
    # 按日期分组
    articles_by_date = {}
    for article in all_articles:
        date_key = article['_sort_date']
        if date_key not in articles_by_date:
            articles_by_date[date_key] = []
        articles_by_date[date_key].append(article)
    
    # 生成HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点教育信息 - 按日期聚合</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: "Microsoft YaHei", "SimSun", serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f8f9fa;
            line-height: 1.8;
        }
        
        /* 头部 */
        .header { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white; 
            padding: 30px 25px; 
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header h1 { 
            font-size: 28px; 
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        .header-stats {
            font-size: 14px;
            opacity: 0.9;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .header-stats span {
            background: rgba(255,255,255,0.1);
            padding: 4px 12px;
            border-radius: 20px;
        }
        
        /* 日期分组 */
        .date-section {
            margin-bottom: 35px;
        }
        .date-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #dee2e6;
        }
        .date-badge {
            background: #495057;
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 15px;
            font-weight: bold;
        }
        .date-count {
            color: #6c757d;
            font-size: 14px;
        }
        
        /* 文章卡片 */
        .article { 
            background: white;
            border-left: 4px solid #dee2e6;
            padding: 20px 25px; 
            margin: 12px 0; 
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .article:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 来源标签 */
        .source-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }
        
        /* 文章头部 */
        .article-header {
            margin-bottom: 12px;
        }
        .article-title {
            font-size: 17px;
            font-weight: bold;
            color: #212529;
            line-height: 1.5;
        }
        .article-subtitle {
            font-size: 13px;
            color: #6c757d;
            margin-top: 6px;
            font-style: italic;
        }
        
        /* 摘要 */
        .article-summary {
            color: #495057;
            font-size: 14.5px;
            line-height: 1.9;
            text-align: justify;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        /* 底部 */
        .article-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 12px;
            border-top: 1px dashed #dee2e6;
        }
        .article-link {
            color: #495057;
            text-decoration: none;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .article-link:hover {
            color: #212529;
        }
        .article-meta {
            color: #adb5bd;
            font-size: 12px;
        }
        
        /* 页脚 */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 25px;
            color: #6c757d;
            font-size: 13px;
            border-top: 1px solid #dee2e6;
        }
        
        /* 今日高亮 */
        .date-section.today .date-badge {
            background: #dc3545;
        }
        .article.is-new {
            border-left-width: 5px;
        }
        .new-indicator {
            background: #dc3545;
            color: white;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 热点教育信息聚合</h1>
        <div class="header-stats">
            <span>📊 共 ''' + str(len(all_articles)) + ''' 篇文章</span>
            <span>📅 ''' + str(len(articles_by_date)) + ''' 个日期</span>
            <span>🔢 6 个来源</span>
        </div>
    </div>
'''
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 按日期输出
    for date_key in sorted(articles_by_date.keys(), reverse=True):
        articles = articles_by_date[date_key]
        display_date = get_display_date(articles[0].get('date', date_key))
        is_today = (date_key == today_str)
        today_class = 'today' if is_today else ''
        
        html += f'''
    <div class="date-section {today_class}">
        <div class="date-header">
            <span class="date-badge">{display_date}</span>
            <span class="date-count">{len(articles)} 篇文章</span>
        </div>
'''
        
        for article in articles:
            source_color = article.get('_source_color', '#666')
            source_name = article.get('_source_name', '')
            source_icon = article.get('_source_icon', '')
            title = article.get('title', '')
            original_title = article.get('original_title', '')
            summary = article.get('summary_cn', article.get('summary_en', ''))
            url = article.get('url', '')
            category = article.get('category', 'general')
            
            # 检查是否今日最新（第一篇）
            new_badge = '<span class="new-indicator">最新</span>' if is_today and article == articles[0] else ''
            
            html += f'''
        <div class="article is-new" style="border-left-color: {source_color};">
            <div class="source-tag" style="background: {source_color};">
                {source_icon} {source_name}
            </div>
            <div class="article-header">
                <div class="article-title">{title}{new_badge}</div>
                <div class="article-subtitle">{original_title}</div>
            </div>
            <div class="article-summary">{summary}</div>
            <div class="article-footer">
                <a href="{url}" target="_blank" class="article-link">🔗 查看原文</a>
                <span class="article-meta">分类: {category}</span>
            </div>
        </div>
'''
        
        html += '    </div>\n'
    
    # 页脚
    html += '''
    <div class="footer">
        📊 本项目从真实网站抓取，每条新闻都有具体URL可验证<br>
        🔄 每日自动更新 | 📝 体制内公文编译风格 | 📅 按日期聚合展示
    </div>
</body>
</html>
'''
    
    # 保存
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 展示页面已生成！共 {len(all_articles)} 篇文章，{len(articles_by_date)} 个日期")
    print("✅ 按日期倒序排列，所有来源混排")

if __name__ == '__main__':
    generate_html()
