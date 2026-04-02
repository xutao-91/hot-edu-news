#!/usr/bin/env python3
"""
自动生成展示页面 - 表格布局
表头：日期 | 分类 | 来源 | 标题 | 摘要
标题直接链接到原文
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

def get_display_date_short(date_str):
    """转为短日期格式 03-25"""
    parsed = parse_date(date_str)
    if parsed:
        return parsed.strftime('%m-%d')
    return date_str

def get_category_name(category):
    """分类英文转中文"""
    category_map = {
        'k12': 'K-12教育',
        'higher_ed': '高等教育',
        'teacher': '教师政策',
        'civil_rights': '民权',
        'civics': '公民教育',
        'grants': '资助拨款',
        'federal_policy': '联邦政策',
        'demographics': '人口统计',
        'politics': '政治',
        'social_trends': '社会趋势',
        'religion': '宗教',
        'technology': '科技媒体',
        'international': '国际',
        'general': '综合'
    }
    return category_map.get(category, category)

def generate_html():
    # 读取所有来源的翻译后数据
    sources = {
        'brookings': {'name': '布鲁金斯', 'color': '#2c5aa0'},
        'edgov': {'name': '教育部', 'color': '#1a4480'},
        'whitehouse': {'name': '白宫', 'color': '#b22234'},
        'ace': {'name': 'ACE', 'color': '#003366'},
        'nsf_ncses': {'name': 'NSF NCSES', 'color': '#1e4d2b'},
        'pewresearch': {'name': '皮尤', 'color': '#233656'},
        'heritage': {'name': '传统基金会', 'color': '#8B0000'},
        'rand': {'name': '兰德公司', 'color': '#0066CC'},
        'aei': {'name': 'AEI', 'color': '#CC5500'},
        'uw_cdis': {'name': 'UW-Madison CDIS', 'color': '#C5050C'},
        'uw_education': {'name': 'UW-Madison教育学院', 'color': '#9B0000'},
        'uw_engineering': {'name': 'UW-Madison工程学院', 'color': '#0055A4'},
        'uw_gradschool': {'name': 'UW-Madison研究生院', 'color': '#4A90E2'},
        'uw_socwork': {'name': 'UW-Madison社会工作学院', 'color': '#8B4513'},
        'uw_news': {'name': 'UW-Madison新闻', 'color': '#C41E3A'},
        'purdue': {'name': '普渡大学', 'color': '#CEB888'},
        'purdue_engineering': {'name': '普渡工程学院', 'color': '#8E6F3E'},
        'purdue_polytechnic': {'name': '普渡理工学院', 'color': '#B8860B'},
        'purdue_education': {'name': '普渡教育学院', 'color': '#4B0082'},
        'iu_news': {'name': '印第安纳大学', 'color': '#990000'},
        'iu_education': {'name': '印第安纳大学教育学院', 'color': '#7A0019'},
        'kelley': {'name': 'IU凯利商学院', 'color': '#5D0000'},
        'oneill': {'name': "IU奥尼尔学院", 'color': '#4A6741'},
        'notre_dame': {'name': '圣母大学', 'color': '#0C2340'},
        'nd_news': {'name': '圣母大学新闻', 'color': '#C99700'},
        'mendoza': {'name': '圣母大学门多萨商学院', 'color': '#00843D'},
        'nd_science': {'name': '圣母大学理学院', 'color': '#6B8E23'},
        'msoe': {'name': '密尔沃基工程学院', 'color': '#C41E3A'},
        'mcw_cancer': {'name': 'F&MCW癌症网络', 'color': '#0057B8'},
        'bridgemi': {'name': 'Bridge Michigan', 'color': '#1E5288'},
        'education_minnesota': {'name': 'Education Minnesota', 'color': '#005596'},
        'mpr_education': {'name': 'MPR Education', 'color': '#0084A8'},
        'umn_cse': {'name': 'UMN CSE', 'color': '#7A0019'},
        'washu_source': {'name': 'WashU Source', 'color': '#A51417'},
        'studlife': {'name': 'Student Life', 'color': '#154734'},
        'washu_engineering': {'name': 'WashU Engineering', 'color': '#A51417'},
        'uchicago_news': {'name': 'UChicago News', 'color': '#800000'},
        'northwestern_news': {'name': 'Northwestern News', 'color': '#4E2A84'},
        'daily_illini': {'name': 'Daily Illini', 'color': '#13294B'},
        'uic_today': {'name': 'UIC Today', 'color': '#001E62'},
        'slu_news': {'name': 'SLU News', 'color': '#003DA5'},
        'uiowa_now': {'name': 'UIowa Now', 'color': '#FFCD00'},
        'showme_mizzou': {'name': 'Show Me Mizzou', 'color': '#F1B82D'},
        'iit_news': {'name': 'IIT News', 'color': '#CC0000'},
        'iastate_news': {'name': 'Iowa State News', 'color': '#C8102E'},
        'ku_news': {'name': 'KU News', 'color': '#0051BA'},
        'kstate_news': {'name': 'K-State News', 'color': '#512888'},
        'mtu_news': {'name': 'MTU News', 'color': '#FFCD00'},
        'unl_news': {'name': 'UNL News', 'color': '#D00000'},
        'wayne_news': {'name': 'Wayne State News', 'color': '#00594C'},
        'udmercy_news': {'name': 'Detroit Mercy News', 'color': '#A6093D'},
        'butler_stories': {'name': 'Butler Stories', 'color': '#13294B'},
        'dordt_news': {'name': 'Dordt News', 'color': '#EFAA2E'},
        'rockhurst_news': {'name': 'Rockhurst News', 'color': '#003366'},
        'augie_news': {'name': 'Augustana News', 'color': '#002F87'},
        'elmhurst_news': {'name': 'Elmhurst News', 'color': '#1E4D2B'},
        'uni_news': {'name': 'UNI News', 'color': '#4B116F'},
        'kettering_news': {'name': 'Kettering News', 'color': '#FDB813'},
        'hanover_research': {'name': 'Hanover Research', 'color': '#006747'},
        'the74_news': {'name': 'The 74 Million', 'color': '#E31937'},
        'ecampus_news': {'name': 'eCampus News', 'color': '#005A8C'},
        'uillinois_news': {'name': 'UIllinois News', 'color': '#13294B'},
        'edsurge_news': {'name': 'EdSurge', 'color': '#00A4E4'},
        'pie_news': {'name': 'The PIE News', 'color': '#F26522'},
        'edtech_hub': {'name': 'EdTech Innovation Hub', 'color': '#6B46C1'},
        'nea_news': {'name': 'NEA News', 'color': '#7B1FA2'}
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
                    article['_sort_date'] = format_date_key(article.get('date', ''))
                    all_articles.append(article)
            except Exception as e:
                print(f"❌ 读取 {source_key} 失败: {e}")
    
    # 按日期倒序排列
    all_articles.sort(key=lambda x: x['_sort_date'], reverse=True)
    
    # 只保留最近4天的文章
    today = datetime.now()
    cutoff = today - timedelta(days=4)
    cutoff_date = cutoff.strftime('%Y-%m-%d')
    all_articles = [a for a in all_articles if a['_sort_date'] >= cutoff_date]
    
    # 生成HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热点教育信息 - 表格视图</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: "Microsoft YaHei", "SimSun", serif; 
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }
        
        /* 头部 */
        .header { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white; 
            padding: 20px 25px; 
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { 
            font-size: 22px; 
            margin-bottom: 8px;
        }
        .header-stats {
            font-size: 13px;
            opacity: 0.9;
        }
        
        /* 表格容器 */
        .table-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            overflow-x: auto;
        }
        
        /* 表格样式 */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        /* 表头 */
        thead {
            background: #343a40;
            color: white;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        th {
            padding: 12px 10px;
            text-align: left;
            font-weight: bold;
            font-size: 13px;
            border-bottom: 2px solid #495057;
        }
        
        /* 表体 */
        tbody tr {
            border-bottom: 1px solid #e9ecef;
            transition: background 0.2s;
        }
        
        tbody tr:hover {
            background: #f8f9fa;
        }
        
        tbody tr:last-child {
            border-bottom: none;
        }
        
        td {
            padding: 12px 10px;
            vertical-align: top;
        }
        
        /* 各列样式 */
        .col-index {
            width: 50px;
            text-align: center;
            font-weight: bold;
            color: #495057;
        }
        
        .col-date {
            width: 70px;
            white-space: nowrap;
            font-weight: bold;
            color: #495057;
        }
        
        .col-category {
            width: 100px;
        }
        
        .col-source {
            width: 100px;
        }
        
        .col-title {
            min-width: 250px;
        }
        
        .col-summary {
            min-width: 300px;
        }
        
        /* 分类标签 */
        .category-tag {
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
        }
        
        /* 来源标签 */
        .source-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
            white-space: nowrap;
        }
        
        /* 标题链接 */
        .title-link {
            color: #212529;
            text-decoration: none;
            font-weight: bold;
            line-height: 1.5;
        }
        
        .title-link:hover {
            color: #0056b3;
            text-decoration: underline;
        }
        
        .original-title {
            font-size: 11px;
            color: #868e96;
            margin-top: 4px;
            font-style: italic;
        }
        
        /* 摘要 */
        .summary {
            color: #495057;
            line-height: 1.6;
            text-align: justify;
        }
        
        /* 页脚 */
        .footer {
            text-align: center;
            margin-top: 25px;
            padding: 15px;
            color: #6c757d;
            font-size: 12px;
        }
        
        /* 响应式 */
        @media (max-width: 900px) {
            .col-summary {
                display: none;
            }
        }
        
        @media (max-width: 600px) {
            .col-index {
                display: none;
            }
            .col-category {
                display: none;
            }
            body {
                padding: 10px;
            }
            th, td {
                padding: 10px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 热点教育信息</h1>
        <div class="header-stats">共 ''' + str(len(all_articles)) + ''' 篇文章 | 6 个来源 | 表格视图</div>
    </div>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th class="col-index">序号</th>
                    <th class="col-date">日期</th>
                    <th class="col-category">分类</th>
                    <th class="col-source">来源</th>
                    <th class="col-title">标题</th>
                    <th class="col-summary">摘要</th>
                </tr>
            </thead>
            <tbody>
'''
    
    # 生成表格行
    for index, article in enumerate(all_articles, 1):
        date_short = get_display_date_short(article.get('date', ''))
        category = get_category_name(article.get('category', 'general'))
        source_name = article.get('_source_name', '')
        source_color = article.get('_source_color', '#666')
        title = article.get('title_cn', article.get('title', ''))
        original_title = article.get('original_title', article.get('title', ''))
        summary = article.get('summary_cn', article.get('summary_en', ''))
        url = article.get('url', '')
        
        html += f'''
                <tr>
                    <td class="col-index">{index}</td>
                    <td class="col-date">{date_short}</td>
                    <td class="col-category"><span class="category-tag">{category}</span></td>
                    <td class="col-source"><span class="source-tag" style="background: {source_color};">{source_name}</span></td>
                    <td class="col-title">
                        <a href="{url}" target="_blank" class="title-link">{title}</a>
                        <div class="original-title">{original_title}</div>
                    </td>
                    <td class="col-summary"><div class="summary">{summary}</div></td>
                </tr>
'''
    
    # 页脚
    html += '''            </tbody>
        </table>
    </div>
    
    <div class="footer">
        📊 本项目从真实网站抓取 | 🔄 每日自动更新 | 📝 体制内公文编译风格
    </div>
</body>
</html>
'''
    
    # 保存
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 表格布局页面已生成！共 {len(all_articles)} 篇文章")

if __name__ == '__main__':
    generate_html()
