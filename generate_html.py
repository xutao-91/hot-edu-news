#!/usr/bin/env python3
"""
自动生成展示页面 - 两栏布局
所有文章按日期倒序排列，左右两栏显示
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
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # 生成HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点教育信息 - 双栏布局</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: "Microsoft YaHei", "SimSun", serif; 
            margin: 0;
            padding: 20px;
            background: #f0f2f5;
            line-height: 1.7;
        }
        
        /* 头部 */
        .header { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white; 
            padding: 25px 30px; 
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        .header h1 { 
            font-size: 26px; 
            margin-bottom: 12px;
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
        
        /* 主内容区 - 两栏布局 */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        
        @media (max-width: 1000px) {
            .main-container {
                grid-template-columns: 1fr;
            }
        }
        
        /* 日期区块 */
        .date-block {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .date-block.today {
            border: 2px solid #e74c3c;
        }
        
        .date-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .date-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .date-block.today .date-title {
            color: #e74c3c;
        }
        
        .date-count {
            background: #6c757d;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 13px;
        }
        
        /* 文章卡片 - 紧凑版 */
        .article {
            background: #f8f9fa;
            border-left: 4px solid #dee2e6;
            padding: 14px 16px;
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
            transition: all 0.2s;
        }
        
        .article:hover {
            background: #e9ecef;
            transform: translateX(3px);
        }
        
        /* 来源标签 */
        .source-tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            color: white;
            margin-bottom: 8px;
        }
        
        /* 标题区域 */
        .article-title-wrap {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
        }
        
        .article-title {
            font-size: 15px;
            font-weight: bold;
            color: #212529;
            line-height: 1.5;
            flex: 1;
        }
        
        .new-badge {
            background: #e74c3c;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 4px;
            flex-shrink: 0;
            white-space: nowrap;
        }
        
        .article-subtitle {
            font-size: 12px;
            color: #868e96;
            font-style: italic;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        /* 摘要 */
        .article-summary {
            color: #495057;
            font-size: 13px;
            line-height: 1.7;
            text-align: justify;
            margin: 8px 0;
        }
        
        /* 底部 */
        .article-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px dashed #ced4da;
        }
        
        .article-link {
            color: #495057;
            text-decoration: none;
            font-size: 12px;
        }
        
        .article-link:hover {
            color: #212529;
        }
        
        .article-meta {
            color: #adb5bd;
            font-size: 11px;
        }
        
        /* 页脚 */
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #6c757d;
            font-size: 13px;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
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
    
    <div class="main-container">
'''
    
    # 准备两栏内容
    left_column = []
    right_column = []
    
    # 将日期分配到两栏（奇数日期左栏，偶数日期右栏，或按文章数量平衡）
    sorted_dates = sorted(articles_by_date.keys(), reverse=True)
    
    for i, date_key in enumerate(sorted_dates):
        articles = articles_by_date[date_key]
        display_date = get_display_date(articles[0].get('date', date_key))
        is_today = (date_key == today_str)
        today_class = 'today' if is_today else ''
        
        date_html = f'''
        <div class="date-block {today_class}">
            <div class="date-header">
                <span class="date-title">{display_date}</span>
                <span class="date-count">{len(articles)} 篇</span>
            </div>
'''
        
        for j, article in enumerate(articles):
            source_color = article.get('_source_color', '#666')
            source_name = article.get('_source_name', '')
            source_icon = article.get('_source_icon', '')
            title = article.get('title', '')
            original_title = article.get('original_title', '')
            summary = article.get('summary_cn', article.get('summary_en', ''))
            url = article.get('url', '')
            category = article.get('category', 'general')
            
            # 今日第一篇文章标记为最新
            new_badge = '<span class="new-badge">最新</span>' if is_today and j == 0 else ''
            
            date_html += f'''
            <div class="article" style="border-left-color: {source_color};">
                <div class="source-tag" style="background: {source_color};">
                    {source_icon} {source_name}
                </div>
                <div class="article-title-wrap">
                    <span class="article-title">{title}</span>
                    {new_badge}
                </div>
                <div class="article-subtitle">{original_title}</div>
                <div class="article-summary">{summary}</div>
                <div class="article-footer">
                    <a href="{url}" target="_blank" class="article-link">🔗 查看原文</a>
                    <span class="article-meta">{category}</span>
                </div>
            </div>
'''
        
        date_html += '        </div>\n'
        
        # 分配到两栏（交替分配以平衡高度）
        if i % 2 == 0:
            left_column.append(date_html)
        else:
            right_column.append(date_html)
    
    # 输出左栏
    html += '        <div class="column left">\n'
    for content in left_column:
        html += content
    html += '        </div>\n'
    
    # 输出右栏
    html += '        <div class="column right">\n'
    for content in right_column:
        html += content
    html += '        </div>\n'
    
    # 页脚
    html += '''    </div>
    
    <div class="footer">
        📊 本项目从真实网站抓取，每条新闻都有具体URL可验证<br>
        🔄 每日自动更新 | 📝 体制内公文编译风格 | 📺 双栏布局
    </div>
</body>
</html>
'''
    
    # 保存
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 双栏布局页面已生成！共 {len(all_articles)} 篇文章")
    print(f"✅ 左栏: {len(left_column)} 个日期，右栏: {len(right_column)} 个日期")

if __name__ == '__main__':
    generate_html()
