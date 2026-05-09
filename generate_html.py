#!/usr/bin/env python3
"""
自动生成展示页面 + RSS订阅源
功能：
- 现代化响应式页面
- 全文搜索
- 按来源/分类/日期筛选
- 分页显示
- RSS订阅
"""
import json
import json
import os
from datetime import datetime, timedelta
from email.utils import formatdate
from pathlib import Path

def parse_date_to_str(date_str):
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

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

TRANSLATED_DIR = config['paths']['translated_data_dir']
OUTPUT_DIR = config['html']['output_dir']


def render_template(template_name, context):
    """简单的模板渲染函数，支持{{变量}}、{% for %}循环和{% if %}条件"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    import re
    # 先处理for循环 {% for item in list %} ... {% endfor %}，展开所有循环
    for_pattern = re.compile(r'{% for (.*?) in (.*?) %}(.*?){% endfor %}', re.DOTALL)
    while True:
        match = for_pattern.search(template)
        if not match:
            break
        var_name, list_name, content = match.groups()
        list_data = context.get(list_name.strip(), [])
        rendered = ''
        for item in list_data:
            item_context = context.copy()
            item_context[var_name.strip()] = item
            # 渲染循环内部的变量
            loop_content = content
            # 处理变量 {{ var }}
            var_pattern = re.compile(r'{{\s*(.*?)\s*}}')
            def replace_var(m):
                key = m.group(1).strip()
                if '.' in key:
                    # 处理属性访问 a.b
                    obj, attr = key.split('.', 1)
                    return str(item_context.get(obj, {}).get(attr, ''))
                return str(item_context.get(key, ''))
            loop_content = var_pattern.sub(replace_var, loop_content)
            rendered += loop_content
        template = template[:match.start()] + rendered + template[match.end():]
    
    # 再处理所有if条件 {% if condition %} ... {% endif %}，不管是循环内还是循环外
    if_pattern = re.compile(r'{% if (.*?) %}(.*?){% endif %}', re.DOTALL)
    while True:
        match = if_pattern.search(template)
        if not match:
            break
        # 此时循环已经展开，直接处理if条件
        # 先提取条件和内容
        condition, content = match.groups()
        condition = condition.strip()
        show = False
        try:
            # 处理属性访问，此时变量已经是渲染后的？不对，还是要从context里判断
            # 或者简单处理：如果条件里的变量存在且不为空则显示
            if '.' in condition:
                obj, attr = condition.split('.', 1)
                if obj in context:
                    val = context[obj]
                    if isinstance(val, dict) and attr in val and val[attr]:
                        show = True
            else:
                if condition in context and context[condition]:
                    show = True
        except:
            pass
        if show:
            template = template[:match.start()] + content + template[match.end():]
        else:
            template = template[:match.start()] + '' + template[match.end():]
    
    # 最后处理剩余的顶层变量
    var_pattern = re.compile(r'{{\s*(.*?)\s*}}')
    def replace_var(m):
        key = m.group(1).strip()
        return str(context.get(key, ''))
    template = var_pattern.sub(replace_var, template)
    
    return template


def get_all_translated_articles():
    """获取所有已经翻译完成的中文文章"""
    articles = []
    translated_dir = "data/translated"
    if not os.path.exists(translated_dir):
        return articles
    # 1. 读取按来源存放的数组格式翻译文件
    for source_dir in os.listdir(translated_dir):
        source_path = os.path.join(translated_dir, source_dir)
        if not os.path.isdir(source_path):
            continue
        # 遍历该来源下的所有json文件
        for file in os.listdir(source_path):
            if not file.endswith(".json"):
                continue
            file_path = os.path.join(source_path, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 数组格式
                if isinstance(data, list):
                    for article in data:
                        # 确保是中文（标题至少包含3个中文字符）
                        title = article.get("title_cn", article.get("title", ""))
                        if title:
                            cn_count = sum(1 for c in title if '\u4e00' <= c <= '\u9fff')
                            if cn_count >= 3:
                                articles.append(article)
                # 数组嵌套在news字段的格式
                elif isinstance(data, dict) and "news" in data:
                    for article in data["news"]:
                        # 确保是中文（标题至少包含3个中文字符）
                        title = article.get("title_cn", article.get("title", ""))
                        if title:
                            cn_count = sum(1 for c in title if '\u4e00' <= c <= '\u9fff')
                            if cn_count >= 3:
                                articles.append(article)
                # 单篇格式（新格式）
                elif isinstance(data, dict) and "title" in data:
                    title = data.get("title_cn", data.get("title", ""))
                    cn_count = sum(1 for c in title if '\u4e00' <= c <= '\u9fff')
                    if cn_count >= 3:
                        articles.append(data)
            except:
                continue
    # 2. 读取按日期存放的单篇格式翻译文件
    for item in os.listdir(translated_dir):
        item_path = os.path.join(translated_dir, item)
        # 判断是日期目录（格式YYYY-MM-DD）
        if os.path.isdir(item_path) and len(item) == 10 and item.count('-') == 2:
            for file in os.listdir(item_path):
                if not file.endswith(".json"):
                    continue
                file_path = os.path.join(item_path, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        article = json.load(f)
                        cn_count = sum(1 for c in article["title"] if '\u4e00' <= c <= '\u9fff')
                        if cn_count >= 3:
                            articles.append(article)
                except:
                    continue
    return articles

def parse_date(date_str):
    """解析各种日期格式"""
    # 预处理：去掉星期前缀和时间时区后缀，只保留日期部分
    import re
    # 匹配 Mon, dd Month YYYY 或者 Mon, dd Mon YYYY 格式，去掉前面的星期和后面的时间
    date_str = re.sub(r'^[A-Za-z]{3},\s*', '', date_str.strip())
    date_str = re.sub(r'\s+\d{2}:\d{2}:\d{2}\s+.*$', '', date_str)
    
    formats = [
        '%B %d, %Y',      # March 25, 2026
        '%b %d, %Y',      # Mar 25, 2026
        '%Y-%m-%d',       # 2026-03-25
        '%d %B %Y',       # 04 May 2026
        '%d %b %Y',       # 04 May 2026
        '%m/%d/%Y',       # 05/04/2026
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
        'education': '教育政策',
        'quantum': '量子科技',
        'ai': '人工智能',
        'biomanufacturing': '生物制造',
        'space': '星际航空',
        'bci': '脑机接口',
        'semiconductor': '集成电路',
        'diplomacy': '外交政策',
        'talent': '人才政策',
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
        'nsf': {'name': 'NSF', 'color': '#1a5f7a'},
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
    
    # 只加载已经翻译完成的纯中文文章，确保页面无英文内容
    all_articles = get_all_translated_articles()
    
    # 补充来源信息
    source_info_map = {v['name']: v for k, v in sources.items()}
    for article in all_articles:
        article['_source_name'] = article.get('source', '未知来源')
        article['_source_color'] = source_info_map.get(article['_source_name'], {}).get('color', '#6B7280')
        article['_sort_date'] = parse_date_to_str(article.get('date', ''))
    
    # 去重
    existing_urls = set()
    unique_articles = []
    for article in all_articles:
        url = article.get('url', '')
        if url not in existing_urls:
            existing_urls.add(url)
            unique_articles.append(article)
    all_articles = unique_articles
    
    # 按日期倒序排列
    all_articles.sort(key=lambda x: x['_sort_date'], reverse=True)
    
    # 只保留最近4天的文章
    today = datetime.now()
    cutoff = today - timedelta(days=4)
    cutoff_date = cutoff.strftime('%Y-%m-%d')
    all_articles = [a for a in all_articles if a['_sort_date'] >= cutoff_date]
    
    # 构造模板数据
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 整理来源列表
    source_set = set()
    for a in all_articles:
        source_set.add(a.get('_source_name', ''))
    sources = [{'name': s} for s in sorted(source_set) if s]
    
    # 整理分类列表
    category_set = set()
    for a in all_articles:
        category = get_category_name(a.get('category', 'general'))
        category_set.add(category)
    categories = sorted(category_set)
    
    # 整理文章列表
    articles_for_template = []
    for article in all_articles:
        date_short = get_display_date_short(article.get('date', ''))
        category = get_category_name(article.get('category', 'general'))
        summary = article.get('summary', article.get('summary_cn', ''))
        if not summary:
            summary = '暂无摘要，点击查看原文'
        
        # 处理RSS日期格式
        pub_date = formatdate()
        if article.get('_sort_date'):
            try:
                pub_date = formatdate(datetime.strptime(article['_sort_date'], '%Y-%m-%d').timestamp())
            except:
                pass
        
        articles_for_template.append({
            'title': article.get('title_cn', article.get('title', '')),
            'original_title': article.get('title', ''),
            'summary': article.get('summary_cn', article.get('summary', '')).replace('\n', '<br>'), # 换行转HTML标签，保证页面分段显示
            'url': article.get('url', ''),
            'date_short': date_short,
            'sort_date': article.get('_sort_date', ''),
            'category': category,
            'source_name': article.get('_source_name', ''),
            'source_color': article.get('_source_color', '#6B7280'),
            'pub_date': pub_date
        })
    
    # 渲染HTML页面
    context = {
        'total_articles': len(all_articles),
        'update_time': update_time,
        'sources': sources,
        'categories': categories,
        'articles': articles_for_template
    }
    html = render_template('index.html', context)
    
    # 渲染RSS订阅源（只取最近20篇）
    rss_context = {
        'build_date': formatdate(),
        'articles': articles_for_template[:20]
    }
    rss = render_template('rss.xml', rss_context)
    
    # 保存HTML文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 保存RSS文件
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss)
    with open('docs/rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss)
    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss)
    
    print(f"\n✅ 页面已生成！共 {len(all_articles)} 篇文章")
    print(f"✅ RSS订阅源已生成，最近20篇文章已同步")

if __name__ == '__main__':
    generate_html()
