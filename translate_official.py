#!/usr/bin/env python3
"""
官方公文风格AI编译脚本
使用 Kimi API 按照教育部/外交部官方文风翻译和编译新闻
"""
import json
import os
import re
import sys
from datetime import datetime

RAW_DIR = "data/raw"
TRANSLATED_DIR = "data/translated"
TRANSLATIONS_DB = "translations_db.json"

def load_existing_translations():
    """加载已有的翻译数据库"""
    if os.path.exists(TRANSLATIONS_DB):
        with open(TRANSLATIONS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_translations(translations_db):
    """保存翻译数据库"""
    with open(TRANSLATIONS_DB, 'w', encoding='utf-8') as f:
        json.dump(translations_db, f, indent=2, ensure_ascii=False)

def extract_date_from_text(text, default_date=None):
    """从文本中提取日期"""
    # 尝试匹配各种日期格式
    patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})',
    ]
    
    month_map = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3:
                    if groups[0].isdigit() and len(groups[0]) == 4:
                        # 2024-03-25 或 2024年3月25日
                        year, month, day = groups[0], groups[1].zfill(2), groups[2].zfill(2)
                    else:
                        # March 25, 2024
                        month_str = groups[0] if groups[0].lower() in month_map else groups[1]
                        year = groups[2] if groups[2].isdigit() and len(groups[2]) == 4 else groups[0]
                        month = month_map.get(month_str.lower(), '01')
                        day = groups[1] if groups[1].isdigit() else groups[2]
                        day = day.zfill(2)
                    return f"{year}年{month}月{day}日"
            except:
                continue
    
    # 返回默认日期
    if default_date:
        return default_date
    return datetime.now().strftime("%Y年%m月%d日")

def get_kimi_api_key():
    """获取Kimi API key"""
    # 1. 优先从环境变量获取
    api_key = os.environ.get('KIMI_API_KEY', '')
    if api_key:
        return api_key
    
    # 2. 从 hermes 配置文件读取
    try:
        hermes_config = os.path.expanduser('~/.hermes/config.yaml')
        if os.path.exists(hermes_config):
            with open(hermes_config, 'r') as f:
                for line in f:
                    if 'api_key:' in line and 'kimi' in line.lower():
                        key = line.split('api_key:')[1].strip()
                        if key and key != 'YOUR_API_KEY_HERE':
                            return key
    except:
        pass
    
    return None

def compile_article(article, source_info):
    """
    调用Kimi API进行官方风格编译
    """
    import subprocess
    
    title_en = article.get('title', '')
    summary_en = article.get('summary_en', '')
    content = article.get('content', '')
    author = article.get('author', '')
    date = article.get('date', '')
    source_name = source_info.get('name', '')
    
    # 获取 API key
    api_key = get_kimi_api_key()
    if not api_key:
        print("    ⚠️  未找到 API key，跳过编译")
        return title_en, f"{extract_date_from_text(date)}，{title_en}。"
    
    # 准备原文内容
    full_text = f"""标题: {title_en}
作者: {author}
日期: {date}
来源: {source_name}

摘要: {summary_en}

正文:
{content[:2000] if content else summary_en}
"""
    
    prompt = f"""请按照以下要求，将以下英文教育新闻编译为中文摘要：

【原文】
{full_text}

【编译要求】

一、核心底线（绝对不可违反）
1. 完全忠实原文：仅提取原文信息，禁止任何推理、引申、编造、主观评价，不添加原文以外的观点与结论。
2. 无推演、无脑补：所有内容均来自原文，不做政策解读、不做趋势判断、不补充背景。

二、格式与结构要求
1. 标题规范：正式中文标题，概括核心事件，简洁严谨。
2. 时间规范：摘要首句必须标注具体日期（如2026年3月30日）。
3. 段落规范：正文为2-5个自然段，不采用单段到底形式。
4. 篇幅规范：400字左右摘要。

三、语言与文风要求
1. 文风：采用教育部、外交部国际事务官方文风，严谨、正式、客观、权威，符合公文与外事业务表述。
2. 术语：使用规范官方译法，专业术语统一、准确。
3. 逻辑：层次清晰，先核心事件，再细节内容，最后相关背景/表态，上下文衔接流畅。

四、内容呈现要求
1. 要素齐全：必须包含时间、主体、事件、核心内容、关键数据/观点、影响/意义。
2. 人物与机构：官方名称、职务、姓名翻译规范，关键引述准确转述。
3. 去冗余：剔除原文重复表述、社交平台分享等无关信息，保留核心公务相关内容。

【输出格式】
请严格按照以下JSON格式输出，不要添加任何其他文字：

{{
  "title_cn": "正式中文标题",
  "summary_cn": "2026年X月X日，主体（机构/人物）...\\n\\n第一段核心事件...\\n\\n第二段细节内容...\\n\\n第三段相关背景或表态..."
}}
"""
    
    try:
        # 调用火山方舟API
        curl_cmd = [
            'curl', '-s', '-X', 'POST',
            'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer {api_key}',
            '-d', json.dumps({
                "model": "ark-code-latest",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            })
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                compiled = json.loads(json_match.group())
                return compiled.get('title_cn', title_en), compiled.get('summary_cn', '')
        
        print(f"    API调用失败，使用备用方案")
        
    except Exception as e:
        print(f"    编译失败: {e}")
    
    # 失败时返回原文
    return title_en, f"{extract_date_from_text(date)}，{title_en}。"

def translate_source(source_name, source_info, translations_db):
    """编译单个来源"""
    print(f"\n🔄 正在编译 {source_name}...")
    
    raw_dir = f"{RAW_DIR}/{source_name}"
    if not os.path.exists(raw_dir):
        print(f"  ⏭️  原始数据目录不存在")
        return
    
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.json')]
    if not raw_files:
        print(f"  ⏭️  没有找到原始数据文件")
        return
    
    raw_files.sort(reverse=True)
    source_file = f"{raw_dir}/{raw_files[0]}"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化该来源的翻译库
    if source_name not in translations_db:
        translations_db[source_name] = {}
    
    compiled_count = 0
    skipped_count = 0
    compiled_news = []
    
    for article in data['news']:
        title_en = article.get('title', '')
        
        # 检查是否已编译
        if title_en in translations_db[source_name]:
            article['original_title'] = title_en
            article['title'] = translations_db[source_name][title_en]['title_cn']
            article['summary_cn'] = translations_db[source_name][title_en]['summary_cn']
            skipped_count += 1
            compiled_news.append(article)
            continue
        
        # 调用AI编译
        print(f"  🤖 编译: {title_en[:60]}...")
        title_cn, summary_cn = compile_article(article, source_info)
        
        # 保存到数据库
        translations_db[source_name][title_en] = {
            "title_cn": title_cn,
            "summary_cn": summary_cn
        }
        
        article['original_title'] = title_en
        article['title'] = title_cn
        article['summary_cn'] = summary_cn
        
        compiled_count += 1
        compiled_news.append(article)
    
    data['news'] = compiled_news
    data['compiled_count'] = compiled_count
    data['skipped_count'] = skipped_count
    
    # 保存编译后数据
    os.makedirs(f"{TRANSLATED_DIR}/{source_name}", exist_ok=True)
    output_file = f"{TRANSLATED_DIR}/{source_name}/{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 新编译: {compiled_count} 篇")
    print(f"  ⏭️  已存在: {skipped_count} 篇")
    print(f"  💾 保存至: {output_file}")
    
    return translations_db

def main():
    print("=" * 70)
    print("🤖 官方公文风格AI编译系统")
    print("=" * 70)
    print("编译标准：教育部/外交部国际事务官方文风")
    print("核心原则：完全忠实原文，无推演、无脑补")
    print("=" * 70)
    
    # 加载已有翻译
    translations_db = load_existing_translations()
    print(f"\n📚 已加载翻译数据库: {len(translations_db)} 个来源")
    
    # 定义来源信息
    sources_info = {
        'brookings': {'name': '布鲁金斯学会'},
        'edgov': {'name': '美国教育部'},
        'whitehouse': {'name': '白宫'},
        'ace': {'name': '美国教育委员会'},
        'nsf_ncses': {'name': '美国国家科学基金会'},
        'pewresearch': {'name': '皮尤研究中心'},
        'heritage': {'name': '传统基金会'},
        'rand': {'name': '兰德公司'},
        'aei': {'name': '美国企业研究所'},
        'iu_news': {'name': '印第安纳大学'},
        'kelley': {'name': 'IU凯利商学院'},
        'unl_news': {'name': '内布拉斯加大学林肯分校'},
        'purdue': {'name': '普渡大学'},
        'butler_stories': {'name': '巴特勒大学'},
        'northwestern_news': {'name': '西北大学'},
        'uchicago_news': {'name': '芝加哥大学'},
        'uiowa_now': {'name': '爱荷华大学'},
        'umn_cse': {'name': '明尼苏达大学'},
        'uw_news': {'name': '华盛顿大学'},
        'washu_source': {'name': '圣路易斯华盛顿大学'}
    }
    
    # 检查 API key
    api_key = get_kimi_api_key()
    if not api_key:
        print("⚠️  未找到 Kimi API key")
        print("请设置环境变量: export KIMI_API_KEY='your-api-key'")
        print("或在 ~/.hermes/config.yaml 中配置 api_key")
        return
    else:
        print("✅ 已找到 Kimi API key")
    
    # 编译各来源
    for source_name, source_info in sources_info.items():
        translations_db = translate_source(source_name, source_info, translations_db) or translations_db
        # 每次编译后保存，防止中断丢失数据
        save_translations(translations_db)
    
    print("\n" + "=" * 70)
    print("✅ AI编译流程完成")
    print(f"💾 翻译数据库已更新: {TRANSLATIONS_DB}")
    print("=" * 70)

if __name__ == '__main__':
    main()
